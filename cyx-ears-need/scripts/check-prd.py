#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cyx-ears-need / check-prd.py

对一份 PRD（.html 或 .md）做结构、台账、闭合与文风机检。

用法:
    python check-prd.py <prd.html|prd.md>

退出码: 0 = 无 FAIL；1 = 存在 FAIL。
输出: 分组打印 [OK] / [FAIL] / [WARN]，末尾给汇总。
"""

import io
import os
import re
import sys

# Windows 控制台默认 GBK，输出含箭头/特殊符号会抛 UnicodeEncodeError
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FAILS = []
WARNS = []
OKS = []


def ok(group, msg):
    OKS.append((group, msg))
    print("  [OK]   %s" % msg)


def fail(group, msg):
    FAILS.append((group, msg))
    print("  [FAIL] %s" % msg)


def warn(group, msg):
    WARNS.append((group, msg))
    print("  [WARN] %s" % msg)


def head(n, title):
    print("\n" + "=" * 66)
    print("组 %d / %s" % (n, title))
    print("=" * 66)


# ---------------------------------------------------------------- 读取与抽取

def strip_tags(s):
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    s = s.replace("&quot;", '"').replace("&#39;", "'")
    return re.sub(r"[ \t]+", " ", s)


def load(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def get_headings(raw, is_html, level):
    """返回 [(文本, 位置)]，level 取 2 / 3 / 4。"""
    out = []
    if is_html:
        pat = r"<h%d\b[^>]*>([\s\S]*?)</h%d>" % (level, level)
        for m in re.finditer(pat, raw, flags=re.I):
            out.append((strip_tags(m.group(1)).strip(), m.start()))
    else:
        prefix = "#" * level
        for m in re.finditer(r"^%s\s+(.*)$" % prefix, raw, flags=re.M):
            out.append((m.group(1).strip(), m.start()))
    return out


def get_h4_blocks(raw, is_html, level=4):
    """返回 [(标题, 块正文文本)]，块 = 本标题到下一个同级或更高级标题之间。"""
    if not is_html:
        hs = get_headings(raw, False, level)
        if not hs:
            return []
        bounds = [p for _, p in get_headings(raw, False, 2)] + \
                 [p for _, p in get_headings(raw, False, 3)] + [p for _, p in hs]
        blocks = []
        for i, (txt, pos) in enumerate(hs):
            nxt = None
            for b in sorted(bounds):
                if b > pos:
                    nxt = b
                    break
            seg = raw[pos: nxt or len(raw)]
            blocks.append((txt, strip_tags(seg)))
        return blocks

    pat = r"<h%d\b[^>]*>([\s\S]*?)</h%d>" % (level, level)
    ms = list(re.finditer(pat, raw, flags=re.I))
    if not ms:
        return []
    stops = [m.start() for m in re.finditer(r"<h[23]\b[^>]*>", raw, flags=re.I)]
    blocks = []
    for m in ms:
        end = len(raw)
        for s in stops:
            if s > m.start():
                end = s
                break
        blocks.append((strip_tags(m.group(1)).strip(), strip_tags(raw[m.start():end])))
    return blocks


def get_tables(raw, is_html):
    """返回 [{'header':[...], 'rows':[[...]]}]。"""
    tables = []
    if is_html:
        for tm in re.finditer(r"<table\b[^>]*>([\s\S]*?)</table>", raw, flags=re.I):
            body = tm.group(1)
            rows = []
            for rm in re.finditer(r"<tr\b[^>]*>([\s\S]*?)</tr>", body, flags=re.I):
                cells = [strip_tags(c).strip() for c in
                         re.findall(r"<t[hd]\b[^>]*>([\s\S]*?)</t[hd]>", rm.group(1), flags=re.I)]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append({"header": rows[0], "rows": rows[1:]})
        return tables

    cur = None
    for line in raw.splitlines():
        if re.match(r"^\s*\|.*\|\s*$", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue
            if cur is None:
                cur = {"header": cells, "rows": []}
            else:
                cur["rows"].append(cells)
        else:
            if cur:
                tables.append(cur)
                cur = None
    if cur:
        tables.append(cur)
    return tables


def find_table(tables, *header_kw):
    for t in tables:
        h = " ".join(t["header"])
        if all(k in h for k in header_kw):
            return t
    return None


def section_text(raw, is_html, start_kw, max_len=6000):
    """取某个二级章节的正文文本（从标题到下一个二级标题）。"""
    hs = get_headings(raw, is_html, 2)
    for i, (txt, pos) in enumerate(hs):
        if start_kw in txt:
            end = hs[i + 1][1] if i + 1 < len(hs) else len(raw)
            return raw[pos:end]
    return ""


# ---------------------------------------------------------------- 检查项

CHAPTERS = [
    ("背景", ["背景"]),
    ("产品定位与目标", ["产品定位与目标", "产品定位"]),
    ("需求描述（EARS）", ["用户故事与需求描述", "需求描述", "EARS"]),
    ("功能清单与优先级", ["功能清单与优先级", "功能清单"]),
    ("业务流程说明", ["业务流程"]),
    ("交互与页面说明", ["交互与页面", "交互与界面"]),
    ("数据指标与埋点", ["数据指标与埋点", "指标体系", "埋点"]),
    ("非功能需求", ["非功能需求"]),
    ("依赖与风险", ["依赖与风险", "依赖", "风险清单"]),
    ("里程碑与验收", ["里程碑与验收", "里程碑"]),
]


def check_structure(h2, text):
    head(1, "十章骨架齐全 + 顺序")
    idx = []
    for name, kws in CHAPTERS:
        pos = -1
        for i, (t, _) in enumerate(h2):
            if any(k in t for k in kws):
                pos = i
                break
        if pos < 0:
            fail(1, "缺章节：%s" % name)
        else:
            idx.append((name, pos))
    if idx:
        seq = [p for _, p in idx]
        if seq == sorted(seq):
            ok(1, "十章齐全且顺序正确（命中 %d/10）" % len(idx))
        else:
            ordered = " > ".join(n for n, _ in sorted(idx, key=lambda x: x[1]))
            fail(1, "章节顺序错乱：%s" % ordered)


def check_review_layer(text, is_html):
    head(2, "审阅层四件套")
    need = [("评审速览", ["评审速览", "速览"]),
            ("文档信息", ["文档信息"]),
            ("审阅议题", ["审阅要点", "审阅议题", "评审议题"]),
            ("目录", ["目录"])]
    for name, kws in need:
        if any(k in text for k in kws):
            ok(2, "%s 在位" % name)
        else:
            fail(2, "缺 %s" % name)
    if "北极星" in text:
        ok(2, "Hero/速览含北极星指标")
    else:
        warn(2, "未见北极星指标")
    if re.search(r"P0\s*需求", text):
        ok(2, "含 P0 需求体量 KPI")
    else:
        warn(2, "未见「P0 需求」KPI 元数据")


def check_requirement_blocks(h4blocks):
    head(3, "需求编号连续性 + 六段式齐备")
    codes = []
    for title, _ in h4blocks:
        m = re.match(r"^([A-Z])(\d+)([a-z]?)\b", title)
        if m:
            codes.append((m.group(1), int(m.group(2)), m.group(3) or "", title))
    if not codes:
        warn(3, "未识别到需求条目（h4 形如「A1 需求名（P0）」）")
    else:
        ok(3, "识别到 %d 条需求条目" % len(codes))
    # 同字母序号连续性
    from collections import defaultdict
    grp = defaultdict(list)
    for l, n, s, _ in codes:
        grp[l].append(n)
    gaps = []
    for l, ns in sorted(grp.items()):
        uniq = sorted(set(ns))
        for i in range(1, len(uniq)):
            if uniq[i] != uniq[i - 1] + 1:
                gaps.append("%s%d→%s%d" % (l, uniq[i - 1], l, uniq[i]))
    if gaps:
        warn(3, "序号不连续：%s（若为有意的空号可忽略）" % ", ".join(gaps))
    else:
        ok(3, "各能力域序号连续无空号")

    # 六段式（仅 P0）
    segs = ["用户故事", "EARS", "验收标准", "关联页面"]
    bad = []
    n_p0 = 0
    no_unwanted = []
    for title, block in h4blocks:
        if not re.match(r"^[A-Z]\d+[a-z]?\b", title):
            continue
        if "P0" not in title:
            continue
        n_p0 += 1
        miss = [s for s in segs if s not in block]
        if miss:
            bad.append("%s 缺 %s" % (title.split("（")[0].strip(), "/".join(miss)))
        if "如果" not in block:
            no_unwanted.append(title.split("（")[0].strip())
    if n_p0 == 0:
        warn(3, "未找到 P0 需求条目，无法检查六段式")
    elif bad:
        fail(3, "P0 需求六段不全：%s" % "；".join(bad[:8]))
    else:
        ok(3, "%d 条 P0 需求六段齐全" % n_p0)
    if no_unwanted:
        warn(3, "缺 Unwanted（异常）句式：%s" % ", ".join(no_unwanted[:8]))


def check_ledgers(tables):
    head(4, "台账完整性")
    d = find_table(tables, "决策项")
    if d is None:
        fail(4, "未见「决策记录」表")
    else:
        h = " ".join(d["header"])
        if "影响" in h:
            ok(4, "决策记录含「影响」列（%d 条）" % len(d["rows"]))
        else:
            fail(4, "决策记录缺「影响」列")
    b = find_table(tables, "责任方", "状态")
    if b is None:
        b = find_table(tables, "建议责任方")
    if b is None:
        fail(4, "未见「待确认问题清单」表（表头需含 责任方 / 状态）")
    else:
        ok(4, "待确认清单含责任方与状态（%d 条）" % len(b["rows"]))
    r = find_table(tables, "风险", "等级")
    if r is None:
        warn(4, "未见「风险清单」表（表头需含 风险 / 等级 / 对策）")
    else:
        h = " ".join(r["header"])
        if "对策" in h:
            ok(4, "风险清单含「对策」列（%d 条）" % len(r["rows"]))
        else:
            fail(4, "风险清单缺「对策」列")
    m = find_table(tables, "阶段", "准出")
    if m is None:
        warn(4, "未见「里程碑」表（表头需含 阶段 / 准出条件）")
    else:
        ok(4, "里程碑表含准出条件（%d 个阶段）" % len(m["rows"]))
    g = find_table(tables, "版本", "依据")
    if g is None:
        warn(4, "未见「需求变更记录」表（表头需含 版本 / 变更 / 依据）")
    else:
        ok(4, "变更记录含「依据」列（%d 条）" % len(g["rows"]))


def check_numbers(text, tables, h4blocks):
    head(5, "数字闭合（头部 KPI ↔ 清单 ↔ 正文）")

    # --- P0 需求数 ---
    rows = None
    for t in tables:
        h = " ".join(t["header"])
        if "编号" in h and "需求" in h and "优先级" in h:
            rows = t["rows"]
            break
    # 清单里优先级列以 P0 开头的行（含「P0（约束）」）
    n_list_p0 = 0
    if rows:
        for r in rows:
            if len(r) >= 3 and r[2].strip().upper().startswith("P0"):
                n_list_p0 += 1
    # 正文里标题带 P0 的条目
    n_body_p0 = sum(1 for title, _ in h4blocks
                    if re.match(r"^[A-Z]\d+[a-z]?\b", title) and "P0" in title)
    # 头部 "P0 需求 25 + 1"
    m = re.search(r"P0\s*需求[^\d]{0,12}?(\d+)\s*(?:\+\s*(\d+))?", text)
    n_base = int(m.group(1)) if m else None
    n_plus = int(m.group(2)) if (m and m.group(2)) else 0
    n_head = (n_base + n_plus) if n_base is not None else None

    print("      清单 P0 行=%d  正文带 P0 标注条目=%d  头部 KPI=%s" %
          (n_list_p0, n_body_p0, ("%d + %d" % (n_base, n_plus)) if n_base is not None else "未标注"))

    if n_head is not None and n_list_p0 and n_list_p0 != n_head:
        warn(5, "清单 P0 行数(%d) 与头部 KPI(%d) 不一致" % (n_list_p0, n_head))
    elif n_list_p0:
        ok(5, "清单 P0 行数与头部 KPI 一致（%d）" % n_list_p0)

    if n_base is not None and n_body_p0 and n_body_p0 != n_base:
        warn(5, "正文带 P0 标注的条目数(%d) 与头部基准数(%d) 不一致"
             "（若「+%d」为架构约束类条目，属正常）" % (n_body_p0, n_base, n_plus))
    elif n_base is not None:
        ok(5, "正文 P0 条目数与头部基准数一致（%d）" % n_base)

    # --- 待确认项数 ---
    m = re.search(r"待确认[^\d]{0,8}(\d+)\s*项", text)
    if m:
        n_decl = int(m.group(1))
        bt = find_table(tables, "建议责任方") or find_table(tables, "责任方", "状态")
        if bt:
            open_rows = [r for r in bt["rows"]
                         if not any("已确认" in c or "已关闭" in c for c in r)]
            n_total, n_open = len(bt["rows"]), len(open_rows)
            print("      附录 B 总行数=%d  其中未关闭=%d  头部声明=%d" % (n_total, n_open, n_decl))
            if n_decl in (n_total, n_open):
                ok(5, "待确认项数与附录 B 对得上（声明 %d，总 %d / 未关闭 %d）"
                   % (n_decl, n_total, n_open))
            else:
                warn(5, "头部「待确认 %d 项」与附录 B（总 %d / 未关闭 %d）均不一致"
                     % (n_decl, n_total, n_open))


def check_refs(raw, is_html, h2, h3, text):
    head(6, "跨章引用可命中")
    sec_nums = set()
    for t, _ in h2 + h3:
        m = re.match(r"^(\d+(?:\.\d+)?)", t)
        if m:
            sec_nums.add(m.group(1))
    # 章节引用统一写成「X.Y 节」，不用 §
    refs = set(re.findall(r"(?:见|详见|参见|回指|指向)\s*(\d+(?:\.\d+)?)\s*节", text))
    refs |= set(re.findall(r"(\d+\.\d+)\s*节", text))
    if refs:
        tops = {s.split(".")[0] for s in sec_nums}
        bad = sorted(r for r in refs if r not in sec_nums and r.split(".")[0] not in tops)
        if bad:
            warn(6, "疑似悬空章节引用：%s 节" % "、".join(bad))
        else:
            ok(6, "%d 个「X.Y 节」引用均可命中" % len(refs))
    else:
        warn(6, "未见「X.Y 节」形式章节引用")

    alltext = strip_tags(raw) if is_html else raw
    for label, pat in (("B-", r"B-(\d+)"), ("D-", r"D-(\d+)")):
        used = set(re.findall(pat, alltext))
        if used:
            nums = sorted(int(x) for x in used)
            ok(6, "%s 编号引用 %d 个（%d–%d）" % (label, len(used), nums[0], nums[-1]))


def check_placeholders(raw, text):
    head(7, "占位符残留")
    n = raw.count("{{")
    if n:
        fail(7, "残留模板占位符 {{ }} 共 %d 处" % n)
        for m in list(re.finditer(r"\{\{([^}]{0,40})", raw))[:8]:
            print("         · {{%s" % m.group(1))
    else:
        ok(7, "无 {{ }} 模板占位符")
    nested = re.findall(r"\{\{[^{}]*\{\{", raw)
    if nested:
        warn(7, "疑似嵌套占位符 %d 处——替换后外层花括号会残留在正文里" % len(nested))
    words = ["待填", "占位", "TODO", "FIXME", "TBD", "待补充", "此处填写", "示例文本"]
    hit = [w for w in words if w in text]
    if hit:
        warn(7, "疑似占位词：%s" % ", ".join(hit))
    else:
        ok(7, "无占位词")


def check_style(raw, text, heads):
    head(8, "去 AI 味硬规则")
    emoji = ["⚡", "📌", "💡", "🔥", "⭐", "👉", "👀", "🎯", "🚀",
             "⚠", "✅", "❌", "🔴", "🟡", "📄", "📊", "✨"]
    hit = [e for e in emoji if e in text]
    if hit:
        fail(8, "装饰性 emoji：%s（改用文字或 CSS 色块）" % " ".join(hit))
    else:
        ok(8, "无装饰性 emoji")

    hard = ["一句话结论", "一句话解读", "核心要点", "核心观点", "核心结论",
            "综上所述", "本节将", "本部分将", "划重点", "三步走", "四个维度", "五个关键"]
    hit = [w for w in hard if w in text]
    if hit:
        warn(8, "空标签 / 元语言：%s" % ", ".join(hit))
    else:
        ok(8, "无空标签与元语言")

    # 读者导引类元语言：只在句首（段首 / 句号后）才算元语言
    soft = r"(?:^|[。；\n])\s*(值得注意的是|如上图所示|从图可见|一目了然|不难看出|众所周知)"
    m = re.findall(soft, text)
    if m:
        warn(8, "句首读者导引类元语言 %d 处：%s" % (len(m), "、".join(sorted(set(m)))))
    else:
        ok(8, "无句首读者导引类元语言")

    jargon = ["赋能", "抓手", "打透", "颗粒度", "组合拳", "生态位"]
    hit = [w for w in jargon if w in text]
    if hit:
        warn(8, "空话词：%s" % ", ".join(hit))
    else:
        ok(8, "无空话词")

    vague = re.findall(r"(?:系统应(?:支持|优化|提升|完善))|(?:^|\n)\s*(?:支持|优化|提升|完善)(?:[^，。；\n]{0,8})(?=[，。；\n])",
                       text)
    if len(vague) > 8:
        warn(8, "疑似空需求动词（支持/优化/提升/完善）出现 %d 次，建议逐条改为「系统应 {具体动作}」" % len(vague))
    else:
        ok(8, "空需求动词数量正常（%d 次）" % len(vague))

    # 标题命名：实体名词，不带括注式自我描述与「一句话 X」元语言
    BAN_HEAD = ["一句话", "一页纸", "（必读", "（重要", "（详细", "（完整", "（小结",
                "（补充", "（附", "划重点", "小贴士", "核心要点", "核心观点", "核心结论",
                "本版明确不做", "（速览"]
    bad_head = [h for h in heads if any(b in h for b in BAN_HEAD)]
    if bad_head:
        warn(8, "标题含括注式自我描述 / 元语言，应改为实体名词：%s" % "；".join(bad_head[:6]))
    else:
        ok(8, "标题均为实体名词（无「一句话 X」「（一页纸）」类括注）")


def check_badges(raw, is_html):
    head(9, "徽章规范")
    if not is_html:
        warn(9, "Markdown 文件，跳过徽章检查")
        return
    body = re.sub(r"<!--[\s\S]*?-->", " ", raw)
    body = re.sub(r"<script[\s\S]*?</script>", " ", body, flags=re.I)
    body = re.sub(r"<style[\s\S]*?</style>", " ", body, flags=re.I)
    hand = len(re.findall(r'<span class="pb\b', body))
    if hand:
        warn(9, "发现 %d 处手写徽章 HTML；正文应只写纯文本 P0 / 高 / M1，由脚本自动转徽章" % hand)
    else:
        ok(9, "正文未手写徽章 HTML（纯文本形式，由脚本自动转换）")
    plain = strip_tags(body)
    for token in ["P0", "P1"]:
        if token in plain:
            ok(9, "正文含纯文本优先级 %s" % token)
            break
    if 'id="toc"' in raw:
        ok(9, "含 TOC 容器（脚本自动生成导航）")
    else:
        warn(9, "未见 id=\"toc\" 容器")


def check_symbols(raw, text, is_html):
    """排版符号黑名单。原则：符号要么人人认得（→ ≤ ✓），要么别用。
    § ※ ◆ ★ ▲ 这类是排版机器标记，中文读者读不出来，一律不写。"""
    head(10, "符号规范（不写排版标记）")
    BAN = {
        "§": "章节引用号，改写「X.Y 节」",
        "※": "注释号，改写文字",
        "◆": "菱形装饰，改用 CSS 色块",
        "◇": "菱形装饰",
        "★": "星号装饰", "☆": "星号装饰",
        "▲": "三角装饰，改用 CSS 图形", "▼": "三角装饰",
        "●": "圆点装饰", "○": "空心圆装饰",
        "■": "方块装饰", "□": "空方块装饰",
        "①": "圈号，改写 1）", "②": "圈号，改写 2）", "③": "圈号，改写 3）",
        "④": "圈号", "⑤": "圈号", "⑥": "圈号",
    }
    hit = [(c, d) for c, d in BAN.items() if c in text]
    if hit:
        fail(10, "排版符号残留 %d 类：%s"
             % (len(hit), "；".join("%s（%s）" % (c, d.split("，")[0]) for c, d in hit[:6])))
        shown = 0
        for c, _ in hit:
            for m in re.finditer(re.escape(c), text):
                if shown >= 4:
                    break
                ctx = text[max(0, m.start() - 20):m.start() + 20].replace("\n", " ")
                print("         · …%s…" % ctx.strip())
                shown += 1
            if shown >= 4:
                break
        print("         共 %d 处；替换口径见 SKILL.md 第 3 章第 6 条" % sum(text.count(c) for c, _ in hit))
    else:
        ok(10, "无排版符号（§ ※ ◆ ★ ▲ ①②③ 等）")

    if is_html:
        css = " ".join(re.findall(r"<style[\s\S]*?</style>", raw, flags=re.I))
        deco = re.findall(r'content:\s*"([^"]{1,2})"', css)
        if deco:
            warn(10, "CSS 里拿字符当装饰图形：%s（改用 width/height + background 画）" % " ".join(deco))
        else:
            ok(10, "CSS 装饰图形未使用字符（均为 CSS 画块）")

    rng = re.findall(r"[0-9A-Za-z]+\s*[–~]\s*[0-9A-Za-z]+", text)
    if rng:
        warn(10, "半角连接号当范围号用 %d 处：%s（中文范围号用「～」）"
             % (len(rng), "、".join(sorted(set(rng))[:6])))
    else:
        ok(10, "区间未误用半角连接号（中文范围号统一用 ～）")


# ---------------------------------------------------------------- main

def main():
    if len(sys.argv) < 2:
        print("用法: python check-prd.py <prd.html|prd.md>")
        return 2
    path = sys.argv[1]
    if not os.path.exists(path):
        print("文件不存在: %s" % path)
        return 2

    raw = load(path)
    is_html = path.lower().endswith((".html", ".htm"))
    text = strip_tags(raw) if is_html else raw
    print("检查对象: %s" % path)
    print("类型: %s  字符数: %d" % ("HTML" if is_html else "Markdown", len(raw)))

    h2 = get_headings(raw, is_html, 2)
    h3 = get_headings(raw, is_html, 3)
    h4blocks = get_h4_blocks(raw, is_html, 4)
    tables = get_tables(raw, is_html)
    print("h2=%d  h3=%d  h4=%d  table=%d" % (len(h2), len(h3), len(h4blocks), len(tables)))

    check_structure(h2, text)
    check_review_layer(text, is_html)
    check_requirement_blocks(h4blocks)
    check_ledgers(tables)
    check_numbers(text, tables, h4blocks)
    check_refs(raw, is_html, h2, h3, text)
    check_placeholders(raw, text)
    check_style(raw, text, [t for t, _ in h2] + [t for t, _ in h3] + [t for t, _ in h4blocks])
    check_badges(raw, is_html)
    check_symbols(raw, text, is_html)

    print("\n" + "=" * 66)
    print("汇总: OK %d  |  WARN %d  |  FAIL %d" % (len(OKS), len(WARNS), len(FAILS)))
    print("=" * 66)
    if FAILS:
        print("\n必须修复（FAIL）:")
        for g, m in FAILS:
            print("  [组%d] %s" % (g, m))
    if WARNS:
        print("\n建议复核（WARN）:")
        for g, m in WARNS:
            print("  [组%d] %s" % (g, m))
    if not FAILS:
        print("\n结构检查通过。")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
