#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""课堂课件 HTML 一键静态体检（cyx-course-html 第 6 步）
用法：
    python check_course.py <课件.html> [--core 120] [--full 180]

两种编排都支持：
  · 时长轨制（双轨）：页头带 .pace 徽章 → 传 --core / --full 校验时长算术闭合
  · 章节制（不锁时长）：页头只有页码 + 标题 → 自动跳过时长项，只查结构一致性

检查项：
  1. 标签配平 + 嵌套栈（找多余的 </div> —— 分块哨兵替换模式最常见的伤）
  2. 页数、章节/环节横幅数、<main> 配对
  3. 时长算术闭合（仅轨制版：pace 合计 + rest-banner 与目标比对）
  4. topnav 锚点是否全部命中 id
  5. 哨兵残留 @@NEXT@@ / 占位 display:none / <script>
  6. 指令编号 ①②③… 是否齐
  7. 课时语汇残留扫描（课时制→章节制改写时用得上）
退出码：0 = 全绿；1 = 有 FAIL

说明：计数一律在「剥掉 HTML 注释」后的文本上做（注释里写 </main>、<div> 这类字样很常见，
直接数会把说明文字算成标签，模板实测就误报过 main 3:4）；唯一例外是哨兵 @@NEXT@@，
它本身就写在注释里，那一项查原文件。占位符【】多于 20 处时判定为骨架/模板，
自动跳过「每章一段 main」与「时长算术闭合」——这两项要填满才成立。
"""
import re
import sys
import argparse
from html.parser import HTMLParser

VOID = {"br", "hr", "img", "meta", "link", "input", "source", "area", "base",
        "col", "embed", "param", "track", "wbr"}
ANCHOR = r'(?:part\d+|ch\d+|chapter\d+|appendix)'


class Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"line {self.getpos()[0]}: </{tag}> 无对应开标签")
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for t, pos in self.stack[i + 1:]:
                    self.errors.append(f"line {pos}: <{t}> 未闭合（被 line {self.getpos()[0]} 的 </{tag}> 抢断）")
                del self.stack[i:]
                return
        self.errors.append(f"line {self.getpos()[0]}: </{tag}> 无对应开标签")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    # 本机 Windows 控制台默认 GBK / 被宿主按 GBK 回读，中文逐项输出会变乱码；
    # 设 PYTHONIOENCODING 也会被 PowerShell 工具吞掉。加 --out 写 UTF-8 文件最稳，
    # 拿不到回显时用 Read 读该文件即可。
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--core", type=int, default=None, help="快线/core 目标分钟（章节制可省）")
    ap.add_argument("--full", type=int, default=None, help="全时长版目标分钟（章节制可省）")
    ap.add_argument("--out", default=None, help="把报告另存为 UTF-8 文件（控制台乱码时用）")
    a = ap.parse_args()

    html = open(a.path, encoding="utf-8").read()
    # 剥离 HTML 注释后再计数：注释里出现的标签字样（说明文字里的 </main>、<div>）不该参与配平。
    # 注意哨兵 @@NEXT@@ 本身写在注释里，那一项必须查原 html。
    scan = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    # 骨架/模板识别：占位符多说明这份文件是「照抄起步用」的模板，
    # 「每章一段 main」「时长算术闭合」这类需要填满才成立的项要跳过，否则每次起步都先看到一片红。
    is_skeleton = html.count("【") >= 20
    out, fails = [], []

    def w(s=""):
        out.append(s)

    def check(name, ok, detail=""):
        w(f"[{'PASS' if ok else 'FAIL'}] {name}{('  ' + detail) if detail else ''}")
        if not ok:
            fails.append(name)

    # 1 标签配平 / 嵌套栈
    b = Balance()
    b.feed(html)
    check("标签嵌套栈", not b.errors and not b.stack,
          f"stray={len(b.errors)} unclosed={len(b.stack)}")
    for e in b.errors[:12]:
        w("        " + e)
    for t, ln in b.stack[:12]:
        w(f"        <{t}> 开于 line {ln} 未闭合")
    for t in ["div", "section", "main", "table", "span"]:
        o = len(re.findall(rf"<{t}(?=[\s>])", scan)) - len(re.findall(rf"<{t}[^>]*/>", scan))
        c = len(re.findall(rf"</{t}>", scan))
        check(f"<{t}> 配平", o == c, f"{o} : {c}")

    # 2 结构规模
    pages = re.findall(r'<section class="page" id="(p\d+)">', scan)
    banners = re.findall(r'<div class="part-banner" id="(' + ANCHOR + r')">', scan)
    w(f"\n页数 = {len(pages)}   横幅 = {len(banners)}   锚点 = {len(set(banners))}")
    w("  " + " ".join(banners))
    check("<main> 配对", scan.count("<main>") == scan.count("</main>"),
          f"{scan.count('<main>')} : {scan.count('</main>')}")
    if is_skeleton:
        w("[--] 骨架/模板（占位符多）：跳过「每章一段 <main>」——模板只示范一两个 PART，照抄增补后才成立")
    else:
        check("每章一段 <main>", scan.count("<main>") == len(banners),
              f"main {scan.count('<main>')} vs 横幅 {len(banners)}")

    # 3 时长（仅轨制版）
    paced = re.findall(r'<span class="pace (\w+)">([^<]*)</span>', scan)
    w(f"\n编排模式：{'时长轨制（pace 徽章 %d 个）' % len(paced) if paced else '章节制（无 pace 徽章）'}")
    if paced and is_skeleton:
        w(f"  [--] 骨架/模板：{len(paced)} 个 pace 徽章只是写法示范，跳过时长算术校验")
    elif paced:
        tot = {}
        for kind, label in paced:
            m = re.search(r"(\d+)'", label)
            tot[kind] = tot.get(kind, 0) + (int(m.group(1)) if m else 0)
        w("  " + "  ".join(f"{k}={v}'" for k, v in sorted(tot.items())))
        if a.core is not None:
            check("核心页合计 = 快线时长", tot.get("core", 0) == a.core,
                  f"{tot.get('core', 0)}' vs {a.core}'")
        if a.full is not None:
            rest = sum(int(x) for x in re.findall(r'class="rest-banner">[^<]*?(\d+)\s*分钟', html)) \
                   or sum(int(x) for x in re.findall(r'休息\s*(\d+)\s*分钟', html))
            w(f"  休息 {rest}'")
            s_all = sum(tot.values()) + rest
            check("核心+选做+休息 = 全时长", s_all == a.full, f"{s_all}' vs {a.full}'")
    else:
        if a.core or a.full:
            w("  （传了 --core/--full 但页面无 pace 徽章，时长项已跳过）")
        w("  每页头部：页码 + 标题；章节归属由 part-banner 承担")

    # 4 锚点命中
    head = scan[:scan.find("</nav>")]
    navs = re.findall(r'<a href="#(\w+)">', head)
    ids = set(re.findall(r'id="(\w+)"', scan))
    broken = [n for n in navs if n not in ids]
    check("topnav 锚点全部命中", not broken, f"{len(navs)} 个" + (f" 断链={broken}" if broken else ""))

    # 5 残留
    check("无哨兵残留", "@@NEXT@@" not in html, "（哨兵写在注释里，查原文件）")
    check("无 <script>", "<script" not in scan, "（模板应为纯静态）")
    check("无占位 display:none", 'style="display:none"' not in scan)

    # 6 指令编号
    marks = re.findall(r"指令([①②③④⑤⑥⑦⑧⑨⑩])", scan)
    order = "①②③④⑤⑥⑦⑧⑨⑩"
    uniq = sorted(set(marks), key=order.index)
    check("指令编号连续", uniq == list(order[:len(uniq)]), " ".join(uniq))

    # 7 语汇残留（章节制下不该再有课时轨制词）
    # 「本课」两条都禁：轨制版是课时绑定，章节制版是单课绑定——项目制课程跨多节课，都不合适。
    # 「产物」同属职场语汇（→ 成果／作品），一并纳入扫描。
    if not paced:
        leftover = []
        for kw in ["分钟版", "快线", "双轨", "PART ·", "本课", "这节课", "一节课", "产物", "复盘", "交付", "交期", "结营", "交接", "立项", "干到", "下班"]:
            n = scan.count(kw)
            if n:
                leftover.append(f"{kw}×{n}")
        check("无课时轨制语汇残留", not leftover, "、".join(leftover) if leftover else "")

    w("\n" + ("=" * 40))
    w("结论：" + ("全部通过" if not fails else "存在 FAIL -> " + "、".join(fails)))
    report = "\n".join(out)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(report)
    print(report)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
