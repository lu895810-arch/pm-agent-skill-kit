#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文档分区归档工具（cyx-doc-separate）。

子命令:
    init         初始化三级目录 + archive_index.md 骨架
    add-ref      登记原始素材（自动去重，同一份只留一份）
    deliver      登记/更新正式交付物，自动递增「更N」序号，旧版移入归档
    add-draft    登记临时草稿（默认不长期留存）
    list-drafts  列出待清理的临时草稿（不删除）
    plan-rename  为一批历史文件生成「更N-名称-日期」改名方案（只预览，不改动）
    verify       体检：散落文件 / 未编号交付物 / 重复素材 / 草稿堆积

命名规范（关键设计）:
    交付物文件名 = 更{N}-{名称}-{YYYYMMDD}{ext}
    例：更01-AI教育厂商调研总结报告-20260914.md

    「更N」前缀放在**最前面**，作用是在文件管理器里按名称排序时
    直接看出更新先后：更01 → 更02 → 更03。序号零填充两位，
    保证「更10」不会排到「更02」前面（纯字符串排序的坑）。
    归档时序号**原样保留**，所以 deliverables/ 与 _archive/ 混在一起看，
    依然是一条能读出来的更新链。

设计原则:
    - 只创建缺失的目录与文件，已存在的索引绝不覆盖（写入一律分节锚定）。
    - 所有操作幂等：重复执行不产生重复条目、不重新编号。
    - 去重依据 = SHA-256 内容指纹（而非文件名）。
    - 不删除任何文件：旧版只移动归档；草稿与散落文件只列出待处理。
    - plan-rename / verify 为只读操作，绝不改动磁盘。
"""

import argparse
import datetime
import hashlib
import os
import re
import shutil
import sys

REFERENCE_DIR = "reference"
DELIVERABLE_DIR = "deliverables"
ARCHIVE_SUBDIR = "_archive"
DRAFT_DIR = "tmp_drafts"
ARCHIVE_INDEX = "archive_index.md"

# ---- 命名规范常量 ----
MARKER = "更"                # 前缀标识
SEQ_PAD = 2                  # 序号零填充位数
DATE_SEP = "-"               # 字段分隔符
NAME_DATE_SEP = "-"          # 名称与日期之间的分隔符

# 文档类扩展名：用于散落文件识别与 plan-rename 的默认筛选
DOC_EXTS = {".md", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
            ".pdf", ".html", ".htm", ".txt", ".csv", ".rtf", ".wps"}

# 小节标题（锚点），用于把新行插入到正确的表格末尾
SEC_REF = "## 原始素材（reference/）"
SEC_DELIVER = "## 交付物（deliverables/）"
SEC_HISTORY = "## 历史归档交付物（deliverables/_archive/）"
SEC_DRAFT = "## 临时草稿（tmp_drafts/，不入长期归档）"

INDEX_TEMPLATE = """# 总归档清单（archive_index）

> 与对话内【附件备份区 - 索引清单】保持同步。本文件**只追加，不删除**。
> 编号一旦分配即不复用、不重排；同一份原始素材只保留一份。
> 交付物文件名形如 `更01-名称-20260914.md`，「更N」即更新序号。
> 标记取值：`原始素材` / `历史归档交付物`。

## 原始素材（reference/）

| 编号 | 文件名 | 简要说明 | 标记 | 指纹 | 入库时间 |
| --- | --- | --- | --- | --- | --- |

## 交付物（deliverables/）

| 更N | 交付物 | 版本 | 文件名 | 状态 | 更新时间 |
| --- | --- | --- | --- | --- | --- |

## 历史归档交付物（deliverables/_archive/）

| 更N | 交付物 | 版本 | 文件名 | 归档时间 | 归档原因 |
| --- | --- | --- | --- | --- | --- |

## 临时草稿（tmp_drafts/，不入长期归档）

| 文件 | 创建时间 | 说明 |
| --- | --- | --- |
"""


# ================================================================ 命名规范

def make_filename(seq, name, ext, when=None):
    """按规范拼出交付物文件名：更01-名称-20260914.md"""
    when = when or datetime.date.today()
    stamp = when.strftime("%Y%m%d")
    return f"{MARKER}{seq:0{SEQ_PAD}d}{DATE_SEP}{name}{NAME_DATE_SEP}{stamp}{ext}"


def format_marker(seq):
    """只取「更N」标识本身，用于索引与展示。"""
    return f"{MARKER}{seq:0{SEQ_PAD}d}"


def parse_marked(filename):
    """解析规范命名的文件，返回 (seq, name, datestr)；不匹配返回 None。"""
    m = re.match(
        rf"^{MARKER}(\d+){re.escape(DATE_SEP)}(.+){re.escape(NAME_DATE_SEP)}(\d{{8}})(\.[^.]+)$",
        filename,
    )
    if not m:
        return None
    return int(m.group(1)), m.group(2), m.group(3)


def is_marked(filename):
    return parse_marked(filename) is not None


def legacy_pattern(name):
    """旧命名（v1.0 版本号）的匹配式，用于兼容既有文件。"""
    return re.compile(rf"^{re.escape(name)}_v\d+\.\d+")


# ================================================================ 基础工具

def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write_lines(path, lines):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


def insert_into_section(path, section, row_line):
    """把一行记录插入到指定小节的表格末尾（而非文件末尾）。

    追加式写入必须锚定到小节，否则新行会堆积在文件尾部，
    既破坏 Markdown 表格结构，也让按小节解析的逻辑读不到这些行。
    返回插入所在的行号（从 1 开始）。
    """
    lines = read_text(path).splitlines()
    if section not in lines:
        # 小节缺失（例如用户手写过的索引）：退化为在文件末尾补建小节
        lines += ["", section, "", row_line]
        write_lines(path, lines)
        return len(lines)

    start = lines.index(section)
    # 找到该小节之后、下一个 "## " 之前的最后一个非空行，即表格末行
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    last = start
    for i in range(start + 1, end):
        if lines[i].strip():
            last = i
    lines.insert(last + 1, row_line)
    write_lines(path, lines)
    return last + 2


def sha256_of(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def write_if_absent(path, content):
    if os.path.exists(path):
        return False
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    return True


def build_dirs(root):
    return {
        "root": root,
        "reference": os.path.join(root, REFERENCE_DIR),
        "deliverables": os.path.join(root, DELIVERABLE_DIR),
        "archive": os.path.join(root, DELIVERABLE_DIR, ARCHIVE_SUBDIR),
        "drafts": os.path.join(root, DRAFT_DIR),
        "index": os.path.join(root, ARCHIVE_INDEX),
    }


def ensure_dirs(dirs):
    created, existing = [], []
    for key in ("reference", "deliverables", "archive", "drafts"):
        path = dirs[key]
        if os.path.isdir(path):
            existing.append(path)
        else:
            os.makedirs(path, exist_ok=True)
            created.append(path)
    return created, existing


def list_files(folder, exts=None):
    if not os.path.isdir(folder):
        return []
    out = []
    for name in sorted(os.listdir(folder)):
        full = os.path.join(folder, name)
        if not os.path.isfile(full) or name.startswith("."):
            continue
        if exts and os.path.splitext(name)[1].lower() not in exts:
            continue
        out.append(name)
    return out


def ensure_index(dirs):
    today = datetime.date.today().isoformat()
    if not os.path.exists(dirs["index"]):
        write_if_absent(dirs["index"], INDEX_TEMPLATE.format(today=today))
    return today


# ================================================================ 索引解析

def parse_deliverables(index_path):
    """解析「交付物」小节，返回 {名称: {"seq":int, "major":int, "minor":int, "file":str}}。

    交付物主表是「当前状态表」：一个交付物一行，记录它最新的更N与版本。
    """
    out = {}
    if not os.path.exists(index_path):
        return out
    in_section = False
    for line in read_text(index_path).splitlines():
        if line.startswith("## "):
            in_section = line.startswith("## 交付物")
            continue
        if not in_section:
            continue
        m = re.match(r"^\|\s*" + MARKER + r"(\d+)\s*\|\s*([^|]+?)\s*\|\s*v(\d+)\.(\d+)\s*\|\s*([^|]*?)\s*\|", line)
        if not m:
            continue
        name = m.group(2).strip()
        if not name or name.startswith("（"):
            continue
        out[name] = {
            "seq": int(m.group(1)),
            "major": int(m.group(3)),
            "minor": int(m.group(4)),
            "file": m.group(5).strip(),
        }
    return out


def upsert_deliverable_row(index_path, seq, name, version, filename, today):
    """在「交付物」小节就地登记：同名交付物只保留一行（更新更N与版本）。"""
    row = f"| {format_marker(seq)} | {name} | {version} | {filename} | 定稿在用 | {today} |"
    lines = read_text(index_path).splitlines()
    if SEC_DELIVER not in lines:
        lines += ["", SEC_DELIVER, "", row]
        write_lines(index_path, lines)
        return
    start = lines.index(SEC_DELIVER)
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    pat = re.compile(r"^\|\s*" + MARKER + r"\d+\s*\|\s*" + re.escape(name) + r"\s*\|")
    for i in range(start + 1, end):
        if pat.match(lines[i]):
            lines[i] = row
            break
    else:
        last = start
        for i in range(start + 1, end):
            if lines[i].strip():
                last = i
        lines.insert(last + 1, row)
    write_lines(index_path, lines)


def next_ref_number(index_path):
    """从 archive_index.md 中解析出已用的最大附件编号，返回下一个可用编号。"""
    if not os.path.exists(index_path):
        return 1
    text = read_text(index_path)
    nums = [int(n) for n in re.findall(r"\|\s*附件(\d+)\s*\|", text)]
    return (max(nums) + 1) if nums else 1


def iter_fingerprints(reference_dir):
    """扫描 reference/ 建立 指纹 → 文件名 映射。"""
    seen = {}
    if not os.path.isdir(reference_dir):
        return seen
    for name in list_files(reference_dir):
        try:
            seen[sha256_of(os.path.join(reference_dir, name))] = name
        except OSError:
            continue
    return seen


# ================================================================ 子命令

def cmd_init(args):
    root = os.path.abspath(args.target)
    if not os.path.isdir(root):
        print(f"[ERROR] 目标目录不存在: {root}", file=sys.stderr)
        return 2

    dirs = build_dirs(root)
    created, existing = ensure_dirs(dirs)
    made_index = write_if_absent(dirs["index"], INDEX_TEMPLATE.format(today=datetime.date.today().isoformat()))

    print(f"文档分区初始化完成 — 项目：{args.title or os.path.basename(root)}")
    print(f"根目录：{root}")
    for path in created:
        print(f"  [新建] {path}")
    for path in existing:
        print(f"  [已有] {path}")
    print(f"  [总索引] {dirs['index']} — {'已创建' if made_index else '已存在，跳过（不覆盖）'}")
    print()
    print("目录规范：")
    print(f"  {REFERENCE_DIR}/          原始素材（仅存原件，不修改）")
    print(f"  {DELIVERABLE_DIR}/        正式交付物，命名 更NN-名称-YYYYMMDD.ext")
    print(f"  {DELIVERABLE_DIR}/{ARCHIVE_SUBDIR}/   历史版本归档（序号原样保留，不删除）")
    print(f"  {DRAFT_DIR}/              临时草稿，定期清理，不长期留存")
    print(f"  {ARCHIVE_INDEX}           总归档清单，与对话内附件索引同步")
    return 0


def cmd_add_ref(args):
    root = os.path.abspath(args.target)
    dirs = build_dirs(root)
    if not os.path.isdir(root):
        print(f"[ERROR] 目标目录不存在: {root}", file=sys.stderr)
        return 2
    ensure_dirs(dirs)

    src = os.path.abspath(args.file)
    if not os.path.isfile(src):
        print(f"[ERROR] 源文件不存在: {src}", file=sys.stderr)
        return 2

    digest = sha256_of(src)
    seen = iter_fingerprints(dirs["reference"])
    if digest in seen:
        print(f"[去重] 内容与已有素材完全相同，跳过入库：{seen[digest]}")
        print(f"       指纹 sha256:{digest[:12]} — 同一份素材只保留一份备份。")
        return 0

    base = os.path.basename(src)
    dest = os.path.join(dirs["reference"], base)
    if os.path.exists(dest):
        stem, ext = os.path.splitext(base)
        dest = os.path.join(dirs["reference"], f"{stem}__{digest[:8]}{ext}")

    shutil.copy2(src, dest)
    today = ensure_index(dirs)
    num = next_ref_number(dirs["index"])
    note = args.note or "（待补说明）"

    insert_into_section(
        dirs["index"], SEC_REF,
        f"| 附件{num} | {os.path.basename(dest)} | {note} | 原始素材 | {digest[:12]} | {today} |",
    )

    print(f"[已入库] 附件{num} ← {base}")
    print(f"         存放：{dest}")
    print(f"         指纹：sha256:{digest[:12]}")
    return 0


def cmd_deliver(args):
    root = os.path.abspath(args.target)
    dirs = build_dirs(root)
    if not os.path.isdir(root):
        print(f"[ERROR] 目标目录不存在: {root}", file=sys.stderr)
        return 2
    ensure_dirs(dirs)

    name = args.name
    src = os.path.abspath(args.file)
    if not os.path.isfile(src):
        print(f"[ERROR] 源文件不存在: {src}", file=sys.stderr)
        return 2

    today = ensure_index(dirs)
    history = parse_deliverables(dirs["index"])
    ext = os.path.splitext(src)[1]

    if name in history:
        prev = history[name]
        seq = prev["seq"] + 1
        if args.major:
            major, minor = prev["major"] + 1, 0   # 结构性重写 → 升主版本
        else:
            major, minor = prev["major"], prev["minor"] + 1  # 增量迭代 → 升次版本
        old_ver = f"v{prev['major']}.{prev['minor']}"
        new_ver = f"v{major}.{minor}"

        # 旧版归档：匹配「新规范命名」与「旧 vX.Y 命名」两种，移动而非删除
        for fname in list_files(dirs["deliverables"]):
            hit = False
            parsed = parse_marked(fname)
            if parsed and parsed[1] == name:
                hit = True
            elif legacy_pattern(name).match(fname):
                hit = True
            if not hit:
                continue
            old = os.path.join(dirs["deliverables"], fname)
            archived = os.path.join(dirs["archive"], fname)
            if not os.path.exists(archived):
                shutil.move(old, archived)
            insert_into_section(
                dirs["index"], SEC_HISTORY,
                f"| {format_marker(prev['seq'])} | {name} | {old_ver} | {fname} | {today} | 迭代更新至 {new_ver} |",
            )
            print(f"[归档] 上一版 {format_marker(prev['seq'])} / {old_ver} → {ARCHIVE_SUBDIR}/{fname}")
    else:
        seq, major, minor = 1, 1, 0
        new_ver = "v1.0"

    new_filename = make_filename(seq, name, ext)
    dest = os.path.join(dirs["deliverables"], new_filename)
    if os.path.exists(dest) and os.path.abspath(dest) != src:
        # 同日同序号重复交付：直接覆盖当前档，不再新增序号
        print(f"[提示] 同名序号已存在，覆盖：{new_filename}")

    shutil.copy2(src, dest)
    upsert_deliverable_row(dirs["index"], seq, name, new_ver, new_filename, today)

    print(f"[交付] {format_marker(seq)} {name} {new_ver}")
    print(f"       存放：{dest}")
    print(f"       索引：{dirs['index']}")
    return 0


def cmd_add_draft(args):
    root = os.path.abspath(args.target)
    dirs = build_dirs(root)
    if not os.path.isdir(root):
        print(f"[ERROR] 目标目录不存在: {root}", file=sys.stderr)
        return 2
    ensure_dirs(dirs)

    src = os.path.abspath(args.file)
    if not os.path.isfile(src):
        print(f"[ERROR] 源文件不存在: {src}", file=sys.stderr)
        return 2

    dest = os.path.join(dirs["drafts"], os.path.basename(src))
    shutil.copy2(src, dest)
    today = ensure_index(dirs)
    insert_into_section(
        dirs["index"], SEC_DRAFT,
        f"| {os.path.basename(dest)} | {today} | {args.note or '临时草稿'} |",
    )
    print(f"[草稿] {os.path.basename(dest)} → {dest}")
    print("       临时内容默认不长期留存，需要时再明确要求保留。")
    return 0


def cmd_list_drafts(args):
    dirs = build_dirs(os.path.abspath(args.target))
    files = list_files(dirs["drafts"])
    if not files:
        print("[空] tmp_drafts 已无临时文件。")
        return 0
    print(f"tmp_drafts 待清理 {len(files)} 个文件（仅列出，未删除）：")
    for f in files:
        full = os.path.join(dirs["drafts"], f)
        size = os.path.getsize(full)
        mtime = datetime.date.fromtimestamp(os.path.getmtime(full)).isoformat()
        print(f"  - {f}  ({size} B, {mtime})")
    print("\n确认后可批量清理；本工具不会自动删除任何文件。")
    return 0


def _core_name(stem):
    """从文件名里剥出「交付物核心名」，去掉修订动作后缀与日期。

    例：
        2-AI教育调研结论与分组总结-2026-09-12-前  → AI教育调研结论与分组总结
        AI教育厂商调研总结报告-20260914-版心收窄前 → AI教育厂商调研总结报告
        4-AI教育厂商实地访谈总结                  → AI教育厂商实地访谈总结
    """
    s = stem.strip()

    # ── 0. 剥掉可能已存在的「更N」前缀，保证这一步幂等 ──
    s = re.sub(r"^更\d+[-_]", "", s)

    # ── 1. 剥尾部「日期 + 可选动作后缀」的组合 ──
    #    真实文件名有三种尾巴，逐个覆盖，顺序从最具体到最宽松：
    #      a) 名称-2026-09-12-前      （长日期 + 动作）
    #      b) 名称-2026-09-12         （长日期）
    #      c) 名称-20260914-版心收窄前 （紧凑日期 + 动作）
    #      d) 名称-20260914           （紧凑日期）
    #      e) 名称-版心收窄前          （只有动作，无日期）
    #    关键在于「日期段本身含连字符」，所以不能用 [^-] 去限制动作短语。
    s = re.sub(r"[-_]\d{4}-\d{2}-\d{2}(?:-.{1,12}前)?$", "", s)   # a / b
    s = re.sub(r"[-_]\d{8}(?:-.{1,12}前)?$", "", s)                # c / d
    s = re.sub(r"-.{1,12}前$", "", s)                              # e

    # ── 2. 剥掉前导序号，如 `2-` / `04_` ──
    s = re.sub(r"^\d+[-_]", "", s)

    # ── 3. 兜底：仍留在末尾的裸动作词（如 `名称-旧`）──
    s = re.sub(r"[-_]?(前|后|旧|新|最终|final|副本|修订版)$", "", s, flags=re.I)

    return s.strip("-_ ")


def looks_like_garbage_name(s):
    """核心名是否已退化成无意义的残片（如单独一个「2」）。

    这种名字多半是解析失败的产物，而不是真的交付物名。
    宁可让工具报错、请人工介入，也不要生成 `更01-2-20260912.md` 这种文件。
    """
    if not s:
        return True
    # 纯数字 / 纯符号：解析失败留下的壳（如「2」「7-」）
    if re.fullmatch(r"[\d\-_.\s]+", s):
        return True
    # 单个字母也没有信息量，同样请人工确认
    if len(s) == 1:
        return True
    return False


def cmd_plan_rename(args):
    """为一批历史文件生成「更N-名称-日期」改名方案。只预览，不改动磁盘。

    两道安全检查（防止把不同交付物混编成一条更新链）：

    1. 归属校验：先按核心名分组。若出现多个核心名而调用方又给了 --name，
       就报错并要求用 --only 限定范围。
       把「AI教室建设与合作模式」改名成「AI教育厂商调研总结报告」是在篡改归属。
    2. 修订分组：同一次修订常存成 md/html/docx 多个文件，按 stem 分组，
       同一 stem 的多格式共用同一更N，不同 stem 才递增序号。
       这比按 mtime 聚类可靠 —— mtime 在批量另存时会差几秒到几分钟，
       任何固定阈值都会把一次修订切成两更。
    """
    folder = os.path.abspath(args.target)
    if not os.path.isdir(folder):
        print(f"[ERROR] 目录不存在: {folder}", file=sys.stderr)
        return 2

    rows = []
    for name in sorted(os.listdir(folder)):
        full = os.path.join(folder, name)
        if not os.path.isfile(full) or name.startswith(".") or name.startswith("~$"):
            continue
        ext = os.path.splitext(name)[1].lower()
        if args.glob:
            if not __import__("fnmatch").fnmatch(name, args.glob):
                continue
        elif ext not in DOC_EXTS:
            continue
        stem = os.path.splitext(name)[0]
        if is_marked(name) and not args.include_marked:
            continue
        rows.append({
            "f": name, "stem": stem, "ext": ext.lstrip("."),
            "core": _core_name(stem),
            "mtime": os.path.getmtime(full),
        })

    if not rows:
        print("[空] 没有需要改名的候选文件。")
        return 0

    # ---------- 检查 0：核心名没解析成残片 ----------
    junk = sorted({r["f"] for r in rows if looks_like_garbage_name(r["core"])})
    if junk:
        print("⚠️  这些文件名的「交付物核心名」没能解析出来，本工具拒绝为它们生成方案：",
              file=sys.stderr)
        print("", file=sys.stderr)
        for f in junk:
            print(f"    · {f}   →  核心名解析为「{_core_name(os.path.splitext(f)[0])}」", file=sys.stderr)
        print("", file=sys.stderr)
        print("    这类文件名与现有约定差别较大，猜出来的名字会篡改归属，", file=sys.stderr)
        print("    所以留给你手工确认：请在对话中告诉我它属于哪个交付物。", file=sys.stderr)
        print("", file=sys.stderr)
        return 4

    # ---------- 检查 1：归属校验 ----------
    by_core = {}
    for r in rows:
        by_core.setdefault(r["core"], []).append(r)

    if len(by_core) > 1:
        if not args.only:
            print("⚠️  这批文件里存在多个不同的交付物，不能统一改名：", file=sys.stderr)
            print("", file=sys.stderr)
            for core in sorted(by_core, key=lambda c: -len(by_core[c])):
                print(f"    [{len(by_core[core]):>2} 个] {core}", file=sys.stderr)
            print("", file=sys.stderr)
            print("    把「A 报告」改名成「B 报告」会篡改文件归属，本工具拒绝这么做。", file=sys.stderr)
            print('    请用 --only "核心名" 明确指定要处理哪一组；其余文件单独处理。', file=sys.stderr)
            print("", file=sys.stderr)
            print("    用法示例：", file=sys.stderr)
            biggest = max(by_core, key=lambda c: len(by_core[c]))
            print(f'      plan-rename "{folder}" --only "{biggest}" --name "..."', file=sys.stderr)
            return 3
        if args.only not in by_core:
            print(f"[ERROR] --only 指定的核心名不存在：{args.only}", file=sys.stderr)
            print(f"        可选：{' / '.join(sorted(by_core))}", file=sys.stderr)
            return 2
        rows = by_core[args.only]

    # ---------- 检查 2：修订分组（按 stem）----------
    by_stem = {}
    for r in rows:
        by_stem.setdefault(r["stem"], []).append(r)

    ordered = sorted(by_stem.items(), key=lambda kv: min(x["mtime"] for x in kv[1]))

    name = args.name
    base_seq = args.start_seq
    print("改名方案预览（只读，未改动任何文件）")
    print(f"  目录：{folder}")
    print(f"  交付物名称：{name}")
    if len(by_core) == 1:
        print(f"  归属校验：通过（核心名 = {ordered[0][1][0]['core']}）")
    else:
        print(f"  归属校验：仅处理 --only 指定的「{args.only}」")
    print(f"  排序依据：文件修改时间（旧→新）")
    print(f"  分组依据：同一次修订的 md/html/docx（同 stem 不同扩展名）共用同一更N")
    print()
    print(f"  {'更N':<6} {'格式':<10} {'原文件名':<50} {'新文件名'}")
    print(f"  {'-'*6} {'-'*10} {'-'*50} {'-'*50}")

    total = 0
    for i, (stem, items) in enumerate(ordered):
        seq = base_seq + i
        marker = format_marker(seq)
        when = datetime.date.fromtimestamp(min(x["mtime"] for x in items))
        for r in sorted(items, key=lambda x: x["ext"]):
            new = make_filename(seq, name, "." + r["ext"], when)
            old_show = r["f"]
            if len(old_show) > 48:
                old_show = old_show[:22] + "…" + old_show[-24:]
            print(f"  {marker:<6} {r['ext']:<10} {old_show:<50} {new}")
            total += 1
        if len(items) > 1:
            print(f"  {'':<6} {'↑ 同一次修订':<10} {', '.join(sorted(x['ext'] for x in items))}")
    print()
    print(f"  共 {len(ordered)} 更，{total} 个文件。")
    print()
    print("  ⚠️  这只是预览方案，未改动任何文件。执行前必须：")
    print("      ① 你把这份清单逐行看过、确认序号与归属都对；")
    print("      ② 先整目录备份；")
    print("      ③ 分批改名（每批 ≤10 个），每批后核对。")
    print("      确认无误后，请在对话中说明，由我按上述安全流程执行。")
    if len(ordered) > 20:
        print()
        print(f"  ⚠️  序号已达 {len(ordered)} 更，说明这个目录堆了过多修订快照。")
        print("      按「精简归档」原则，mid 版本不宜长期留存 —— 建议只保留")
        print("      ① 关键里程碑版（结构性重写前后）② 最终定稿，其余清理。")
    return 0


def cmd_verify(args):
    """体检：散落文件 / 未编号交付物 / 重复素材 / 草稿堆积。只读。"""
    root = os.path.abspath(args.target)
    if not os.path.isdir(root):
        print(f"[ERROR] 目录不存在: {root}", file=sys.stderr)
        return 2
    dirs = build_dirs(root)
    doc_exts = DOC_EXTS

    issues = 0
    print(f"文档分区体检 — {root}")
    print("=" * 62)

    # 1. 根目录散落文件（索引自身与说明文件不算散落）
    allowed_root = {ARCHIVE_INDEX.lower(), "readme.md"}
    strays = [
        f for f in list_files(root)
        if os.path.splitext(f)[1].lower() in doc_exts and f.lower() not in allowed_root
    ]
    print(f"\n[1] 根目录散落文档：{len(strays)} 个")
    for f in strays:
        print(f"      · {f}")
    issues += len(strays)

    # 2. deliverables/ 里未带「更N」前缀
    unmarked = [f for f in list_files(dirs["deliverables"]) if not is_marked(f)]
    print(f"\n[2] 交付物缺「更N」前缀：{len(unmarked)} 个")
    for f in unmarked:
        print(f"      · {f}")
    issues += len(unmarked)

    # 3. reference/ 内容重复
    fp = {}
    dup = []
    for f in list_files(dirs["reference"]):
        try:
            d = sha256_of(os.path.join(dirs["reference"], f))
        except OSError:
            continue
        if d in fp:
            dup.append((fp[d], f, d[:12]))
        else:
            fp[d] = f
    print(f"\n[3] 原始素材重复：{len(dup)} 组")
    for keep, drop, dg in dup:
        print(f"      · {drop}  与  {keep}  内容相同（sha256:{dg}）")
    issues += len(dup)

    # 4. 归档序号连续性
    seqs = sorted(p[0] for p in (parse_marked(f) for f in list_files(dirs["archive"])) if p)
    gaps = [n for n in range(1, (max(seqs) + 1) if seqs else 1) if n not in seqs]
    print(f"\n[4] 归档序号：{'、'.join(format_marker(s) for s in seqs) or '（空）'}")
    if gaps:
        print(f"      · 缺号：{'、'.join(format_marker(g) for g in gaps)}")
        issues += len(gaps)

    # 5. 草稿堆积
    drafts = list_files(dirs["drafts"])
    total = sum(os.path.getsize(os.path.join(dirs["drafts"], f)) for f in drafts)
    print(f"\n[5] 临时草稿：{len(drafts)} 个，共 {total / 1024:.1f} KB")
    if len(drafts) > 10:
        print("      · 堆积偏多，建议清理")
        issues += 1

    print("\n" + "=" * 62)
    print(f"合计待处理项：{issues}")
    if issues == 0:
        print("分区干净。")
    else:
        print("本命令只做只读体检，未改动任何文件。")
    return 0


# ================================================================ 入口

def main(argv=None):
    parser = argparse.ArgumentParser(description="文档分区归档工具（cyx-doc-separate）")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("init", help="初始化三级目录 + archive_index.md")
    p.add_argument("target", nargs="?", default=".", help="目标根目录，默认当前目录")
    p.add_argument("--title", default="", help="可选：项目名")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("add-ref", help="登记原始素材（自动去重）")
    p.add_argument("file", help="素材文件路径")
    p.add_argument("target", nargs="?", default=".", help="目标根目录")
    p.add_argument("--note", default="", help="简要说明")
    p.set_defaults(func=cmd_add_ref)

    p = sub.add_parser("deliver", help="登记交付物（自动递增更N，旧版归档）")
    p.add_argument("file", help="交付物文件路径")
    p.add_argument("--name", required=True, help="交付物名称（不含序号与日期）")
    p.add_argument("target", nargs="?", default=".", help="目标根目录")
    p.add_argument("--major", action="store_true", help="结构性重写，升主版本号")
    p.set_defaults(func=cmd_deliver)

    p = sub.add_parser("add-draft", help="登记临时草稿（默认不长期留存）")
    p.add_argument("file", help="草稿文件路径")
    p.add_argument("target", nargs="?", default=".", help="目标根目录")
    p.add_argument("--note", default="", help="说明")
    p.set_defaults(func=cmd_add_draft)

    p = sub.add_parser("list-drafts", help="列出临时草稿（不删除）")
    p.add_argument("target", nargs="?", default=".", help="目标根目录")
    p.set_defaults(func=cmd_list_drafts)

    p = sub.add_parser("plan-rename", help="生成「更N-名称-日期」改名方案（只预览）")
    p.add_argument("target", nargs="?", default=".", help="待整理目录")
    p.add_argument("--name", required=True, help="这批文件的交付物名称")
    p.add_argument("--glob", default="", help="只选匹配的文件，如 '*.md'")
    p.add_argument("--start-seq", type=int, default=1, help="起始序号，默认 1")
    p.add_argument("--newest-first", action="store_true", help="最新的排更01")
    p.add_argument("--include-marked", action="store_true", help="连已有更N前缀的也重排")
    p.add_argument("--only", default="",
                   help="目录里混有多个交付物时，用核心名指定只处理哪一组")
    p.set_defaults(func=cmd_plan_rename)

    p = sub.add_parser("verify", help="体检：散落文件 / 未编号 / 重复 / 草稿堆积（只读）")
    p.add_argument("target", nargs="?", default=".", help="根目录")
    p.set_defaults(func=cmd_verify)

    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
