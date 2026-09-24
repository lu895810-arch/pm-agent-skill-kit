#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cyx-original-need-md 交付自检

用法:
    python check_original_need_md.py <产出文件>.md

退出码:
    0 = 全过（允许 WARN）
    1 = 有 FAIL，按输出逐条修

Windows 提示:
    先设 PYTHONIOENCODING=utf-8 再跑，否则 PowerShell 捕获中文/箭头输出可能抛
    UnicodeEncodeError，表现为「输出为空」，容易被误判成脚本挂了。
"""

import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- 基础工具

class Group(object):
    def __init__(self, no, name):
        self.no = no
        self.name = name
        self.fails = []
        self.warns = []
        self.notes = []

    def fail(self, msg):
        self.fails.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def note(self, msg):
        self.notes.append(msg)

    @property
    def level(self):
        if self.fails:
            return "FAIL"
        if self.warns:
            return "WARN"
        return "PASS"


def split_sections(lines):
    """返回 [(标题, 起始行, 结束行), ...]，按 '## ' 切。"""
    idxs = [i for i, l in enumerate(lines) if re.match(r"^##\s+\S", l)]
    secs = []
    for k, i in enumerate(idxs):
        end = idxs[k + 1] if k + 1 < len(idxs) else len(lines)
        title = re.sub(r"^##\s+", "", lines[i]).strip()
        secs.append((title, i, end))
    return secs


def find_section(secs, *keywords):
    for title, s, e in secs:
        for kw in keywords:
            if kw in title:
                return (title, s, e)
    return None


def table_rows(lines, start, end):
    """取起始位置之后的第一张表的原始行 (行号, 文本)。"""
    rows = []
    for i in range(start, end):
        text = lines[i].strip()
        if text.startswith("|"):
            rows.append((i, text))
        elif rows:
            break
    return rows


def cells(row_text):
    return [c.strip() for c in row_text.strip().strip("|").split("|")]


def is_sep(row_text):
    return bool(re.match(r"^\|[\s:\-|]+\|?$", row_text)) and "-" in row_text


def data_rows(rows):
    out = []
    for i, text in rows[1:]:
        if is_sep(text):
            continue
        out.append((i, text))
    return out


def body_lines(lines, start, end):
    """排除围栏代码块与表格行后的正文行。"""
    out = []
    fenced = False
    for i in range(start, end):
        l = lines[i]
        if l.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        out.append((i, l))
    return out


# ---------------------------------------------------------------- 各检查组

REQUIRED_SECTIONS = [
    ("总览", ("总览",)),
    ("分阶段拆解", ("分阶段拆解", "分阶段")),
    ("入口架构", ("入口架构",)),
    ("需求主线", ("需求主线", "主线")),
    ("现存需求缺口", ("需求缺口", "缺口")),
    ("用户旅程", ("用户旅程", "旅程")),
]

POINT_WORDS = ("催生", "驱动", "推动", "引出", "迭代到", "打通")

LIMIT_WORDS = ("局限", "短板", "天花板", "不足", "痛点")

REQUEST_WORDS = ("背景", "原始需求", "用户诉求", "用户需求", "核心痛点", "用户痛点", "痛点")

EMOJI = (
    "\u2705\u26a0\u274c\u2714\u2716\u2b50\u2605\u25c6\u25b2\u203b"
    "\u2460\u2461\u2462\u2463\u2464\u2465\u2466\u2467\u2468"
    "\U0001f4cc\U0001f3af\U0001f680\U0001f4a1\U0001f4e6\U0001f9e0"
    "\U0001f517\U0001f6ab\U0001f4c4\U0001f4ca\U0001f9e9\U0001f44d"
    "\U0001f525\U0001f3ac\u2b06\u2b07"
)

BANNED_WORDS = ("赋能", "抓手", "闭环", "颗粒度", "组合拳", "打透", "生态化")

META_PHRASES = ("综上所述", "值得注意的是", "不难看出", "本节将从", "本文将从", "本节将", "本文将")


def check_1_skeleton(lines, secs, g):
    order = []
    for label, kws in REQUIRED_SECTIONS:
        sec = find_section(secs, *kws)
        if not sec:
            g.fail("缺章节：%s（应有一个含「%s」的二级标题）" % (label, kws[0]))
        else:
            order.append((label, sec[1]))
    if order:
        starts = [s for _, s in order]
        if starts != sorted(starts):
            g.fail("章节顺序不对：实际顺序 %s" % " → ".join(label for label, _ in order))
    g.note("必需章节 %d 段，命中 %d 段" % (len(REQUIRED_SECTIONS), len(order)))


def check_2_overview_table(lines, secs, g):
    sec = find_section(secs, "总览")
    if not sec:
        g.fail("缺「演进阶段总览」章节，无法检查总览表")
        return []
    rows = table_rows(lines, sec[1], sec[2])
    if len(rows) < 3:
        g.fail("总览表不存在或没有数据行")
        return []
    header = cells(rows[0][1])
    if len(header) != 8:
        g.fail("总览表应为 8 列，实际 %d 列：%s" % (len(header), " / ".join(header)))
    for kw in ("目标用户", "遗留"):
        if not any(kw in h for h in header):
            g.fail("总览表缺「%s」列" % kw)
    try:
        ci = [i for i, h in enumerate(header) if "遗留" in h][0]
    except IndexError:
        ci = -1
    drs = data_rows(rows)
    last_i = drs[-1][0] if drs else -1
    if ci >= 0:
        for i, text in drs:
            cs = cells(text)
            if len(cs) <= ci:
                g.fail("第 %d 行单元格数少于表头，行数据不完整" % (i + 1))
                continue
            if not cs[ci].strip():
                g.fail("第 %d 行的「遗留问题」列为空（它是链式闭环的账本，不能空）" % (i + 1))
            elif i != last_i and not any(w in cs[ci] for w in POINT_WORDS) and len(cs[ci]) < 200:
                g.warn("第 %d 行的「遗留问题」列未点明催生哪个阶段：%s" % (i + 1, cs[ci][:30]))
    g.note("总览表 %d 列 / %d 个阶段行" % (len(header), len(drs)))
    return drs


def phase_numbers_in_table(drs):
    nums = []
    for _, text in drs:
        cs = cells(text)
        if not cs:
            continue
        m = re.match(r"阶段\s*(\d+)", cs[0])
        if m:
            nums.append(int(m.group(1)))
    return nums


def check_3_phase_count(lines, secs, drs, g):
    table_nums = phase_numbers_in_table(drs)
    head_nums = []
    for i, l in enumerate(lines):
        m = re.match(r"^###\s+阶段\s*(\d+)", l.strip())
        if m:
            head_nums.append(int(m.group(1)))
    if not head_nums:
        g.fail("正文没有 `### 阶段N：…` 形式的小节")
        return []
    if table_nums != head_nums:
        g.fail("阶段数不闭合：总览表 %s / 正文小节 %s" % (table_nums, head_nums))
    if table_nums and table_nums != list(range(1, len(table_nums) + 1)):
        g.fail("阶段编号不连续：%s" % table_nums)
    if head_nums and head_nums != list(range(1, len(head_nums) + 1)):
        g.fail("正文阶段编号不连续：%s" % head_nums)
    g.note("阶段 %d 个，编号 %s" % (len(head_nums), head_nums))
    return head_nums


def check_4_chain(lines, secs, head_nums, g):
    sec = find_section(secs, "分阶段拆解", "分阶段")
    if not sec or not head_nums:
        g.fail("无法检查链式闭环（缺分阶段拆解段落或阶段小节）")
        return
    bounds = []
    for i, l in enumerate(lines):
        m = re.match(r"^###\s+阶段\s*(\d+)", l.strip())
        if m:
            bounds.append((int(m.group(1)), i))
    bounds.sort()
    total = len(bounds)
    used = set()  # 收集各阶段「用户需求」块的实际叫法，用于一致性检查
    for k, (num, start) in enumerate(bounds):
        end = bounds[k + 1][1] if k + 1 < total else sec[2]
        text = "\n".join(lines[start:end])
        if num < bounds[-1][0]:
            if not any(w in text for w in LIMIT_WORDS):
                g.fail("阶段 %d 缺「产品局限」块（天花板写在哪？）" % num)
            elif not any(w in text for w in POINT_WORDS):
                g.fail("阶段 %d 的局限块没点名催生哪个阶段" % num)
        if num > bounds[0][0]:
            if not any(w in text for w in REQUEST_WORDS):
                g.warn("阶段 %d 看不出「背景与原始需求」块，链子可能接不上" % num)
            elif not any(w in text for w in POINT_WORDS + ("接住", "天花板", "遗留")):
                g.warn("阶段 %d 的背景段看不出承接上一阶段（建议首句点回上一阶段的遗留问题）" % num)
        if not any(w in text for w in ("用户需求", "用户诉求")):
            g.warn("阶段 %d 缺「用户需求」条目" % num)
        else:
            used.add("用户需求" if "用户需求" in text else "用户诉求")
    if len(used) > 1:
        g.warn("「用户需求」块名不统一：各阶段分别写作 %s——块名全篇要一致，否则读者会以为是两件事"
               % " / ".join(sorted(used)))
    g.note("链式闭环抽查 %d 个阶段" % total)


def check_5_sources(lines, secs, head_nums, g):
    text = "\n".join(lines)
    pats = {
        "材料口径": r"(口径|白皮书|业务介绍|官网|教程|知识库|官方模板|披露)",
        "界面观察": r"(界面观察|据.{0,6}截图|据.{0,6}观察)",
        "用户反馈": r"(用户反馈|用户原话|据.{0,4}口述)",
    }
    counts = {}
    for k, p in pats.items():
        counts[k] = len(re.findall(p, text))
    need = max(1, len(head_nums))
    if counts["材料口径"] < need:
        g.warn("来源标签偏少：材料口径类 %d 处，建议每阶段至少一处" % counts["材料口径"])
    if counts["界面观察"] == 0:
        g.warn("全篇没有「界面观察」类来源标签；若确实没有界面材料，请在阶段内写明「待补观察」")
    if counts["用户反馈"] == 0:
        g.warn("全篇没有用户反馈 / 口述类来源；没材料就别编，写了就要能指向出处")
    g.note("来源标签：%s" % "，".join("%s %d 处" % (k, v) for k, v in counts.items()))


def check_6_gaps(lines, secs, g):
    sec = find_section(secs, "需求缺口", "缺口")
    if not sec:
        g.fail("缺「现存需求缺口」章节")
        return
    block = lines[sec[1]:sec[2]]
    text = "\n".join(block)
    rows = data_rows(table_rows(lines, sec[1], sec[2]))
    listed = [l for l in block if re.match(r"^\s*(?:\d+[.)、]|[-*]\s+\S|\|\s*G-)", l)]
    entries = rows if rows else listed
    if not entries:
        g.fail("缺口池没有任何条目")
    elif len(entries) < 3:
        g.warn("缺口只有 %d 条，确认是否真就这几条（确实没有也要显式写明）" % len(entries))

    nums = [int(n) for n in re.findall(r"G-(\d+)", text)]
    if nums:
        uniq = sorted(set(nums))
        if uniq != list(range(1, len(uniq) + 1)):
            g.fail("缺口编号不连续：%s" % uniq)
    else:
        g.warn("缺口池未用 `G-n` 连续编号（下游迭代池要沿用这份编号，且需与模块式 G1 区分）")
    if re.search(r"(?<![-A-Za-z])G\d+(?![-0-9])", text):
        g.warn("缺口池里出现不带连字符的模块式编号（G1 形式），与 `G-n` 混用会歧义")

    if rows:
        for i, t in rows:
            cs = cells(t)
            if len(cs) < 4:
                g.fail("第 %d 行缺口表列数不足 4（编号｜缺口｜现状证据｜影响）" % (i + 1))
            elif not cs[2].strip():
                g.fail("第 %d 行缺口缺「现状证据」（指不回去的是判断，不是缺口）" % (i + 1))
    else:
        g.warn("缺口池不是四列表（编号｜缺口｜现状证据｜影响），现状证据是否都能指回材料？")
    g.note("缺口 %d 条" % len(entries))


def check_7_language(lines, g):
    text = "\n".join(lines)
    hits = []
    for ch in set(EMOJI):
        if ch in text:
            hits.append(repr(ch).strip("'"))
    if hits:
        g.fail("出现 emoji / 图标字符：%s（标签改用加粗文字，如 `**满足需求**`）" % " ".join(sorted(hits)))
    for w in BANNED_WORDS:
        if w in text:
            g.fail("出现空话词「%s」" % w)
    for w in META_PHRASES:
        if w in text:
            g.fail("出现元语言 / 过渡填充「%s」" % w)
    if "首先" in text and "其次" in text:
        g.warn("疑似「首先 / 其次 / 最后」三段套，确认是否必要")
    # 正文里的第一人称与调研视角（引述块除外）
    bad_lines = []
    for i, l in enumerate(lines):
        if l.strip().startswith(">"):
            continue
        for w in ("我方", "本次调研"):
            if w in l:
                bad_lines.append((i + 1, w))
        if "我们" in l and not l.strip().startswith("|"):
            bad_lines.append((i + 1, "我们"))
    for ln, w in bad_lines:
        if w == "我们":
            g.warn("第 %d 行出现「我们」，本稿叙述主体是产品 / 界面 / 用户：%s" % (ln, lines[ln - 1].strip()[:40]))
        else:
            g.fail("第 %d 行出现「%s」，本稿不以此自称" % (ln, w))
    # 标题空标签
    for i, l in enumerate(lines):
        if re.match(r"^#{1,6}\s", l) and re.search(r"(一句话|核心要点|机制推演|小结与展望)", l):
            g.fail("第 %d 行标题是空标签：%s" % (i + 1, l.strip()))


def check_8_placeholders(lines, g):
    text = "\n".join(lines)
    for w in ("TODO", "待填", "XXXX", "xxxx", "？？？"):
        if w in text:
            g.fail("占位符残留：%s" % w)
    found = re.findall(r"\{[^{}\n]{1,24}\}", text)
    if found:
        g.warn("疑似模板占位符残留 %d 处：%s" % (len(found), "、".join(sorted(set(found))[:6])))


def check_9_references(lines, head_nums, g):
    if not head_nums:
        return
    top = max(head_nums)
    refs = set(int(n) for n in re.findall(r"阶段\s*(\d+)", "\n".join(lines)))
    over = sorted(n for n in refs if n > top)
    if over:
        g.fail("引用了不存在的阶段：%s（全篇只有阶段 1–%d）" % (over, top))


def check_10_tables_and_lead(lines, secs, g):
    sec = find_section(secs, "入口架构")
    if not sec:
        g.fail("缺「N 层入口架构」章节")
    else:
        rows = table_rows(lines, sec[1], sec[2])
        if len(rows) < 2:
            g.fail("入口架构章节没有表格")
        else:
            header = cells(rows[0][1])
            if len(header) != 4:
                g.fail("入口架构表应为 4 列（层级｜能力｜当前入口位置｜备注），实际 %d 列" % len(header))
            if not any("备注" in h for h in header):
                g.warn("入口架构表缺「备注」列")
    first_h2 = None
    for i, l in enumerate(lines):
        if re.match(r"^##\s+\S", l):
            first_h2 = i
            break
    lead = [l for l in lines[:(first_h2 if first_h2 is not None else len(lines))] if l.strip().startswith(">")]
    if len(lead) < 3:
        g.warn("导语不足三块（现有 %d 行）：应有能力底座与演进路径 / 核心矛盾 / 编号口径声明" % len(lead))


# ---------------------------------------------------------------- 主流程

def main():
    if len(sys.argv) < 2:
        print("用法: python check_original_need_md.py <产出文件>.md")
        return 2
    path = sys.argv[1]
    if not os.path.isfile(path):
        print("找不到文件: %s" % path)
        return 2
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()

    secs = split_sections(lines)

    groups = [
        Group(1, "骨架齐全与顺序"),
        Group(2, "演进阶段总览表"),
        Group(3, "阶段数闭合"),
        Group(4, "链式闭环"),
        Group(5, "来源标签"),
        Group(6, "需求缺口池"),
        Group(7, "去 AI 味与视角"),
        Group(8, "占位符残留"),
        Group(9, "编号引用"),
        Group(10, "入口架构表与导语"),
    ]
    g1, g2, g3, g4, g5, g6, g7, g8, g9, g10 = groups

    check_1_skeleton(lines, secs, g1)
    drs = check_2_overview_table(lines, secs, g2)
    heads = check_3_phase_count(lines, secs, drs, g3)
    check_4_chain(lines, secs, heads, g4)
    check_5_sources(lines, secs, heads, g5)
    check_6_gaps(lines, secs, g6)
    check_7_language(lines, g7)
    check_8_placeholders(lines, g8)
    check_9_references(lines, heads, g9)
    check_10_tables_and_lead(lines, secs, g10)

    print("=== cyx-original-need-md 自检：%s ===" % os.path.basename(path))
    total_fail = total_warn = 0
    for g in groups:
        print("[%s] 组%-2d %s" % (g.level, g.no, g.name))
        for m in g.fails:
            print("        FAIL  %s" % m)
        for m in g.warns:
            print("        WARN  %s" % m)
        if g.level == "PASS" and g.notes:
            print("              %s" % "；".join(g.notes))
        total_fail += len(g.fails)
        total_warn += len(g.warns)

    print("\n--- 汇总：FAIL %d 条 / WARN %d 条 ---" % (total_fail, total_warn))
    print("退出码 %d（0 = 可交付）" % (1 if total_fail else 0))
    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())
