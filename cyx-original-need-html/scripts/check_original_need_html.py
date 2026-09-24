#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_original_need_html.py
《功能演进与需求分析》单文件 HTML 交付前机检。

用法：
    python check_original_need_html.py <产出文件>.html

退出码：
    0 = 通过（允许 WARN）；1 = 有 FAIL

Windows 编码坑：PowerShell 捕获 Python 输出默认走 GBK，本脚本会 print 箭头等字符，
不设编码会抛 UnicodeEncodeError 表现为「输出为空」。先执行：
    $env:PYTHONIOENCODING = "utf-8"
"""

import os
import re
import sys

# 八章骨架：第 i 个 h2 必须含 CH[i]
CHAPTERS = ["演进路径", "演进背景", "阶段演进", "入口架构", "需求主线", "缺口", "用户旅程", "口径"]

# 来源标签（每阶段至少命中一类）
SRC_PAT = re.compile(
    r"界面观察|待补观察|白皮书|业务介绍|官网|教程|知识库|官方模板|官方口径|用户反馈|用户口述|分析推断"
)

# 去 AI 味：硬禁词
BANNED_FAIL = ["赋能", "抓手", "闭环", "颗粒度", "干货", "硬核", "炸裂", "颠覆",
               "保姆级", "划重点", "综上所述", "值得注意的是", "不难看出",
               "一目了然", "如上图所示", "从图可见", "首先", "其次"]
# 加工痕迹 / 修订流水
BANNED_META = ["整理说明", "本稿以", "整理自", "修订记录", "最近修订", "本整理稿", "本文档由"]
# 视角越界（我们 可能出现在用户原话里，单列 WARN）
BANNED_VIEW = ["我方", "本次调研"]

EMOJI_PAT = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
ICON_TAG_PAT = re.compile(r"[✅⚠️❌📌💡🔥⭐👉✔✖]")
PLACEHOLDER_PAT = re.compile(r"\{[^{}\n]{1,24}\}")
TODO_PAT = re.compile(r"TODO|待填|TBD|XXX")

results = []  # (level, group, message)


def add(level, group, msg):
    results.append((level, group, msg))


def strip_blocks(html):
    """去掉 style / script / 注释，只留可读正文，供文字类检查使用。"""
    s = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<!--[\s\S]*?-->", " ", s)
    return s


def text_of(fragment):
    return re.sub(r"<[^>]+>", " ", fragment)


def main():
    if len(sys.argv) < 2:
        print("用法: python check_original_need_html.py <产出文件>.html")
        return 2
    path = sys.argv[1]
    if not os.path.isfile(path):
        print("找不到文件: %s" % path)
        return 2

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()
    body = strip_blocks(html)
    btext = text_of(body)

    # ── 组 1 八章骨架与顺序 ─────────────────────────────────────────
    h2s = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<h2>([\s\S]*?)</h2>", html)]
    if len(h2s) != len(CHAPTERS):
        add("FAIL", 1, "part-banner 的 h2 有 %d 个，应为 %d 个（八章）" % (len(h2s), len(CHAPTERS)))
    for i, kw in enumerate(CHAPTERS):
        if i >= len(h2s):
            add("FAIL", 1, "缺第 %d 章（标题应含「%s」）" % (i + 1, kw))
        elif kw not in h2s[i]:
            add("FAIL", 1, "第 %d 章标题是「%s」，应含「%s」——章节顺序或名称不对" % (i + 1, h2s[i][:24], kw))

    # ── 组 2 章节组件与编号 ─────────────────────────────────────────
    sections = re.findall(r"<section\b[^>]*>", html)
    banners = re.findall(r'<div class="part-banner">', html)
    if len(banners) != len(sections):
        add("FAIL", 2, "part-banner 有 %d 个、section 有 %d 个，应一一对应" % (len(banners), len(sections)))
    pnums = re.findall(r'<div class="pnum">\s*(\d+)\s*</div>', html)
    if [int(x) for x in pnums] != list(range(1, len(pnums) + 1)):
        add("FAIL", 2, "章编号块 pnum 不是 1..N 连续：%s" % ",".join(pnums))
    ids = re.findall(r'<section\b[^>]*id="([^"]+)"', html)
    if ids != ["s%d" % i for i in range(1, len(ids) + 1)]:
        add("WARN", 2, "section 的 id 不是 s1..sN 连续：%s" % ",".join(ids))

    # ── 定位第 3 章（阶段演进） ─────────────────────────────────────
    sec3 = ""
    m = re.search(r'<section\b[^>]*id="s3"[\s\S]*?</section>', html)
    if m:
        sec3 = m.group(0)
    else:
        add("FAIL", 3, "找不到 id=\"s3\" 的阶段演进章节")

    # ── 组 3 总览表列与内容 ─────────────────────────────────────────
    tbl = ""
    mt = re.search(r"<table>([\s\S]*?)</table>", sec3)
    if mt:
        tbl = mt.group(1)
    else:
        add("FAIL", 3, "第 3 章找不到总览表")
    if tbl:
        head = re.search(r"<tr>([\s\S]*?)</tr>", tbl)
        ths = re.findall(r"<th>([\s\S]*?)</th>", head.group(1)) if head else []
        if len(ths) != 6:
            add("FAIL", 3, "总览表有 %d 列，应为 6 列（阶段/产品形态/核心入口/解决痛点/目标用户/遗留问题）" % len(ths))
        for kw in ["目标用户", "遗留问题"]:
            if not any(kw in h for h in ths):
                add("FAIL", 3, "总览表缺列「%s」" % kw)

    # ── 组 4 阶段数闭合 ─────────────────────────────────────────────
    stage_ids = [int(x) for x in re.findall(r'<h3\s+id="s3-(\d+)"', html)]
    rows = 0
    if tbl:
        rows = max(0, len(re.findall(r"<tr>", tbl)) - 1)
    if stage_ids != list(range(1, len(stage_ids) + 1)):
        add("FAIL", 4, "阶段小节编号不连续：s3-%s" % ",s3-".join(str(x) for x in stage_ids))
    if stage_ids and rows and len(stage_ids) != rows:
        add("FAIL", 4, "总览表 %d 行，阶段小节 %d 个，两处不闭合" % (rows, len(stage_ids)))
    if not stage_ids:
        add("FAIL", 4, "没有找到阶段小节（<h3 id=\"s3-N\">）")
    # 头部 KPI 与阶段数
    mk = re.search(r"演进阶段</div>\s*<div class=\"v\">\s*(\d+)\s*</div>", html)
    if mk and stage_ids and int(mk.group(1)) != len(stage_ids):
        add("WARN", 4, "头部「演进阶段」写 %s，正文实际 %d 个阶段" % (mk.group(1), len(stage_ids)))

    # ── 组 5 链式闭环 ───────────────────────────────────────────────
    if stage_ids and sec3:
        for n in stage_ids:
            start = sec3.find('id="s3-%d"' % n)
            nxt = sec3.find('id="s3-%d"' % (n + 1))
            chunk = sec3[start: nxt if nxt > 0 else len(sec3)]
            if 'class="note warn"' not in chunk:
                add("FAIL", 5, "阶段 %d 缺「局限」块（.note.warn）" % n)
            elif n != stage_ids[-1] and not re.search(r"阶段\s*%d" % (n + 1), chunk):
                add("FAIL", 5, "阶段 %d 的局限块没有点名催生阶段 %d" % (n, n + 1))
    # 每阶段至少一处来源标签 + 「背景」「用户需求」块
    if stage_ids and sec3:
        for n in stage_ids:
            start = sec3.find('id="s3-%d"' % n)
            nxt = sec3.find('id="s3-%d"' % (n + 1))
            chunk = sec3[start: nxt if nxt > 0 else len(sec3)]
            if not SRC_PAT.search(chunk):
                add("FAIL", 6, "阶段 %d 全段没有来源标签（材料口径 / 界面观察 / 用户反馈）" % n)
            if "背景" not in chunk:
                add("FAIL", 5, "阶段 %d 缺「背景」块" % n)
            if "用户需求" not in chunk:
                add("FAIL", 5, "阶段 %d 缺「用户需求」块（块名是否写成了「用户诉求」？）" % n)

    # ── 组 6 全篇界面观察 ───────────────────────────────────────────
    if "界面观察" not in body and "待补观察" not in body:
        add("FAIL", 6, "全篇没有「界面观察」，也无「待补观察」声明——界面类事实缺来源")

    # ── 组 7 缺口池编号 ─────────────────────────────────────────────
    sec6 = ""
    m6 = re.search(r'<section\b[^>]*id="s6"[\s\S]*?</section>', html)
    if m6:
        sec6 = m6.group(0)
    gaps = [int(x) for x in re.findall(r"\bG(\d+)\b", sec6)]
    if not gaps:
        add("FAIL", 7, "第 6 章找不到缺口条目（G1…Gn）")
    else:
        seen, dedup = set(), []
        for g in gaps:
            if g not in seen:
                seen.add(g)
                dedup.append(g)
        if dedup != list(range(1, len(dedup) + 1)):
            add("FAIL", 7, "缺口编号不连续或有重号：%s" % ",".join("G%d" % g for g in gaps))
        if len(dedup) != len(gaps):
            add("WARN", 7, "缺口编号有重复出现：%s" % ",".join("G%d" % g for g in gaps))

    # ── 组 8 去 AI 味与视角 ─────────────────────────────────────────
    for w in BANNED_FAIL:
        if w in btext:
            add("FAIL", 8, "正文出现禁用词「%s」" % w)
    for w in BANNED_META:
        if w in btext:
            add("FAIL", 8, "正文出现加工痕迹「%s」——归交付说明，不进文档" % w)
    for w in BANNED_VIEW:
        if w in btext:
            add("FAIL", 8, "正文出现「%s」——叙述主体应是产品 / 界面 / 用户" % w)
    if "我们" in btext:
        add("WARN", 8, "正文出现「我们」（若在用户原话引述中可忽略）")
    if EMOJI_PAT.search(btext) or ICON_TAG_PAT.search(btext):
        add("FAIL", 8, "正文出现 emoji 或图标标签，改成加粗文字标签")

    # ── 组 9 占位符残留 ─────────────────────────────────────────────
    ph = PLACEHOLDER_PAT.findall(btext)
    if ph:
        add("FAIL", 9, "占位符残留 %d 处，例如 %s" % (len(ph), " ".join(ph[:5])))
    td = TODO_PAT.findall(btext)
    if td:
        add("FAIL", 9, "占位符残留：%s" % ",".join(sorted(set(td))))

    # ── 组 10 锚点可达与单文件自包含 ────────────────────────────────
    ids_all = set(re.findall(r'id="([^"]+)"', html))
    for h in re.findall(r'href="#([^"]+)"', html):
        if h not in ids_all:
            add("FAIL", 10, "目录锚点 #%s 找不到对应 id" % h)
    if re.search(r"<link[^>]+rel=[\"']?stylesheet", html, flags=re.I):
        add("FAIL", 10, "存在外链 CSS，交付物要求单文件自包含")
    if re.search(r"<script[^>]+src=", html, flags=re.I):
        add("FAIL", 10, "存在外链 JS，交付物要求单文件自包含")
    if not re.search(r'<meta\s+name="viewport"', html):
        add("WARN", 10, "缺 viewport meta，窄屏与手机端会缩放异常")
    if 'class="kick"' not in html:
        add("WARN", 10, "头部缺 .kick 一句话导语")
    if 'class="metas"' not in html:
        add("WARN", 10, "头部缺 .metas 指标区")

    # ── 输出 ────────────────────────────────────────────────────────
    fails = [r for r in results if r[0] == "FAIL"]
    warns = [r for r in results if r[0] == "WARN"]
    print("机检文件：%s" % os.path.basename(path))
    print("─" * 62)
    if not results:
        print("全部检查通过。")
    for level, grp, msg in results:
        print("[%s][组%d] %s" % (level, grp, msg))
    print("─" * 62)
    print("FAIL %d 项 · WARN %d 项" % (len(fails), len(warns)))
    if not fails:
        print("结论：可交付（WARN 项自行判断是否处理）。")
    else:
        print("结论：不可交付，按上面 FAIL 逐条修。")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
