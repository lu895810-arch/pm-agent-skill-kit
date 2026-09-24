# -*- coding: utf-8 -*-
"""四格漫画版最终体检（口径对齐《AI小记者课堂版-简版-设计方案.md》）。"""
import io, re, sys

T = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\admin\WorkBuddy\2026-09-17-15-58-14\build\out4.html"
RPT = sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\admin\WorkBuddy\2026-09-17-15-58-14\build\final.txt"

with io.open(T, "r", encoding="utf-8") as f:
    s = f.read()

R, fail = [], []
def chk(c, ok, bad):
    if c: R.append("PASS  " + ok)
    else:
        R.append("FAIL  " + bad); fail.append(bad)
def cnt(p): return len(re.findall(p, s))

pages = re.findall(r'<section class="page" id="(p\d+)">', s)
R.append("页面数: %d (%s..%s)" % (len(pages), pages[0], pages[-1]))
R.append("")

# V1 解剖顺序
bad = []
for m in re.finditer(r'<section class="page" id="(p\d+)">(.*?)</section>', s, re.S):
    pid, b = m.group(1), m.group(2)
    i_h, i_c, i_n = b.find('class="page-head"'), b.find('class="cap"'), b.find('class="tnote"')
    if not (0 <= i_h < i_c < i_n): bad.append(pid)
chk(not bad, "V1 解剖顺序 head<cap<tnote 正确（%d 页）" % len(pages), "V1 顺序异常: %s" % bad)

# V2 每页 cap / tnote 各一；hero >= 页数（P02/P03 有补充视觉）
n_cap, n_note, n_hero = cnt(r'<div class="cap">'), cnt(r'<details class="tnote">'), cnt(r'<svg class="hero"')
chk(n_cap == len(pages) + 2,
    "V2a cap=%d == 页数+2（P02/P03 各有主视觉＋补充视觉，故各多 1 条 cap）" % n_cap,
    "V2a cap %d != 页数+2（%d）" % (n_cap, len(pages)+2))
chk(n_note == len(pages), "V2b 每页一个 tnote（%d/%d）" % (n_note, len(pages)), "V2b tnote %d != %d" % (n_note, len(pages)))
R.append("      注：hero=%d（P02/P03 各含 1 个补充视觉条）" % n_hero)

# V3 页码连续
nums = [int(x) for x in re.findall(r'page-num[^"]*">\s*P\s*(\d+)\s*<', s)]
chk(nums == list(range(1, len(nums)+1)), "V3 页码连续 P1..P%d，无跳号无重号" % len(nums), "V3 页码异常: %s" % nums)

# V4 无外链
chk(cnt(r'https?://') == 0, "V4 无 http/https 外链（断网可用）", "V4 存在外链")
chk(cnt(r'<script') == 0, "V4b 无 <script>（零 JS）", "V4b 存在 script")

# V5 SVG 内无 <b>
sb = sum(b.count("<b>") for b in re.findall(r'<svg.*?</svg>', s, re.S))
chk(sb == 0, "V5 SVG 内无 <b>（强调用 tspan）", "V5 SVG 内 %d 处 <b>" % sb)

# V6 标签配平
def bal(t): return len(re.findall(r'<%s[\s>]' % t, s)), len(re.findall(r'</%s>' % t, s))
sec, det, div = bal("section"), bal("details"), bal("div")
chk(sec[0]==sec[1], "V6a <section> 配平 %d/%d" % sec, "V6a section %s" % (sec,))
chk(det[0]==det[1], "V6b <details> 配平 %d/%d" % det, "V6b details %s" % (det,))
chk(div[0]==div[1], "V6c <div> 配平 %d/%d" % div, "V6c div %s" % (div,))

# V7 横幅
banners = re.findall(r'<div class="part-banner" id="([^"]+)">', s)
chk(len(banners)==9, "V7 横幅 9 个（序章＋七章＋附录）", "V7 横幅 %d" % len(banners))

# V8 导航
navs = re.findall(r'<a href="#([^"]+)">', s)
miss = [n for n in navs if n not in banners]
chk(not miss, "V8 导航 %d 项锚点全部命中横幅" % len(navs), "V8 缺失锚点 %s" % miss)

# V9 说课三段
n1,n2,n3 = cnt(r'class="tseg tsay"'), cnt(r'class="tseg top"'), cnt(r'class="tseg twarn"')
chk(n1==len(pages) and n3==len(pages),
    "V9 说课齐备 tsay=%d top=%d twarn=%d" % (n1,n2,n3),
    "V9 说课缺失 tsay=%d twarn=%d pages=%d" % (n1,n3,len(pages)))

# V10 保命句
keys = ["不许让豆包替你把故事写完", "不许把 AI 原话直接抄进角色卡",
        "不许涂改或丢掉 V1 失败稿", "AI生成·示意图", "不许照搬 AI 成品",
        "不许直接跳到 V2", "不靠偷、抢、骗、占便宜解决问题"]
missk = [k for k in keys if k not in s]
chk(not missk, "V10 全部 %d 条保命句在场" % len(keys), "V10 缺失: %s" % missk)

# 附加：短句按最长语义段 <=14
def segs(txt):
    t = re.sub(r'<[^>]+>', '', txt); t = re.sub(r'\s+', '', t)
    ps = re.split(r'[·→]+|——+|;|；', t)
    ps = [p.strip('，,。.') for p in ps if p.strip('，,。.')]
    return ps if len(ps) > 1 else [t]
over = []
for m in re.finditer(r'<div class="cl">(.*?)</div>', s, re.S):
    ps = segs(m.group(1)); lg = max(len(p) for p in ps)
    if lg > 14:
        over.append("%s(%d)" % (re.sub(r'\s','',re.sub(r'<[^>]+>','',m.group(1))), lg))
R.append("")
chk(not over, "附加 短句最长语义段全部 <=14 字", "附加 超长 %d 条: %s" % (len(over), over))

R.append("")
R.append("元素统计: todo=%d  prompt=%d  stepchip=%d  timechip=%d  tnote=%d  hero=%d" % (
    cnt(r'<div class="todo">'), cnt(r'<div class="prompt">'), cnt(r'class="stepchip"'),
    cnt(r'class="timechip"'), cnt(r'<details class="tnote">'), cnt(r'<svg class="hero"')))
R.append("结构: mainwrap=%d  残留<main>=%d" % (cnt(r'<div class="mainwrap">'), cnt(r'<main>')))

R.append("")
R.append("========== 结论 ==========")
R.append("全绿" if not fail else "未通过 %d 项：" % len(fail))
for x in fail: R.append("  - " + x)

with io.open(RPT, "w", encoding="utf-8") as f:
    f.write("\n".join(R))
print("FAILS=%d" % len(fail))
