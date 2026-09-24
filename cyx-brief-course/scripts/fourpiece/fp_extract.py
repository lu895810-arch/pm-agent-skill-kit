# -*- coding: utf-8 -*-
"""fp_extract.py —— 四件套生成·第 1 步：从课件 HTML 抽取结构化数据。

用法（Python 3.13，本机路径见 SKILL §环境）：

    python fp_extract.py <课件.html> <data.json> [--report <报告.txt>]

产出 data.json，含两段：
  banners[]  : id / pnum / title / desc / chip          （章节横幅）
  pages[]    : id / ord / num / chip / title / caps[] /
               prompt{head,body} / todo{tk,tt,tt_html,tp} /
               segs{tsay,top,twarn} / aria[] / svg_text[] / nviz

设计要点（普适任何课件，不绑定某一门课）：
  · 全部用「结构类名」定位，不匹配任何具体文案——换课程只换输入文件，脚本不用改。
  · 属性选择器一律用「类名 + 可选后缀」的宽松写法（class="page-num" / "page-num purple" 都能吃）。
  · 抓不到的字段留空/None，不抛异常——课件写法略有出入时仍能出数据，由人工核对。
  · 输出前做一次自检：横幅数、页数、有说课的页数、有指令的页数、有 todo 的页数，全部写进报告。
"""
import re
import json
import io
import os
import sys
import argparse

sys.stdout.reconfigure(encoding="utf-8")


def strip_tags(t):
    """剥标签 + 还原实体 + 压空白。"""
    t = re.sub(r"<[^>]+>", "", t or "")
    t = (t.replace("&lt;", "<").replace("&gt;", ">")
          .replace("&amp;", "&").replace("&nbsp;", " "))
    return re.sub(r"\s+", " ", t).strip()


def grab_banners(html):
    """章节横幅。pnum / h1 / pdesc / timechip 四件，timechip 可能缺失。"""
    out = []
    pat = (r'<div class="part-banner"\s+id="([^"]+)"\s*>(.*?)'
           r'(?=<div class="part-banner"|<div class="mainwrap"|<main\b|</body>)')
    for m in re.finditer(pat, html, re.S):
        bid, block = m.group(1), m.group(2)
        pnum = re.search(r'<div class="pnum[^"]*">(.*?)</div>', block, re.S)
        h1 = re.search(r"<h1>(.*?)</h1>", block, re.S)
        desc = re.search(r'<div class="pdesc">(.*?)</div>', block, re.S)
        chip = re.search(r'<span class="timechip">(.*?)</span>', block, re.S)
        out.append({
            "id": bid,
            "pnum": strip_tags(pnum.group(1)) if pnum else "",
            "title": strip_tags(h1.group(1)) if h1 else "",
            "desc": strip_tags(desc.group(1)) if desc else "",
            "chip": strip_tags(chip.group(1)) if chip else "",
        })
    return out


def grab_pages(html):
    """逐页抽取。页面容器固定 <section class="page" id="pNN">。

    额外记录 `chapter`：该页在源文件里落在哪个横幅之下——做法是扫描全文，
    记住「当前最近出现的横幅 id」，遇到 section.page 时把这个 id 挂上去。
    这样章节切分是**从文件真实顺序读出来的**，不是靠页数均分猜的。
    """
    out = []
    # 先建一张「位置 → 横幅 id」的事件表
    events = []
    for m in re.finditer(r'<div class="part-banner"\s+id="([^"]+)"', html):
        events.append((m.start(), "banner", m.group(1)))
    for m in re.finditer(r'<section class="page" id="(p\d+)"\s*>', html):
        events.append((m.start(), "page", m.group(1)))
    events.sort()
    owner = {}
    cur = ""
    for pos, kind, val in events:
        if kind == "banner":
            cur = val
        else:
            owner[val] = cur

    for m in re.finditer(r'<section class="page" id="(p\d+)"\s*>(.*?)</section>', html, re.S):
        pid, body = m.group(1), m.group(2)
        # 页序（1 起）：从 id="pNN" 取，与页头写什么无关。
        # 课件页头可能写页码（P 01）也可能写章段号（2.1），全课页序始终以 id 为准。
        ordv = int(re.sub(r"\D", "", pid) or 0)

        head = re.search(r'<div class="page-head">(.*?)</div>', body, re.S)
        head_html = head.group(1) if head else body[:400]
        num = re.search(r'<span class="page-num[^"]*">(.*?)</span>', head_html, re.S)
        chip = re.search(r'<span class="stepchip[^"]*">(.*?)</span>', head_html, re.S)
        title = re.search(r'<span class="page-title">(.*?)</span>', head_html, re.S)

        # 短句：全部 <div class="cl">…</div>
        caps = [strip_tags(c) for c in re.findall(r'<div class="cl">(.*?)</div>', body, re.S)]
        caps = [c for c in caps if c]

        # 指令框。结构固定：<div class="prompt"><div class="ph">…</div><div class="pc">…</div></div>
        # 正文里含嵌套 <span>，不嵌套 div，所以「从 pc 到最近的 </div>」即是正文。
        prompt = None
        pm = re.search(r'<div class="prompt">\s*<div class="ph">(.*?)</div>\s*<div class="pc">(.*?)</div>\s*</div>',
                       body, re.S)
        if pm:
            prompt = {"head": strip_tags(pm.group(1)), "body": pm.group(2).strip()}
        else:
            # 兜底：可能没有外层闭合的 </div>，抓 ph + pc 即可
            ph = re.search(r'<div class="ph">(.*?)</div>', body, re.S)
            pc = re.search(r'<div class="pc">(.*?)</div>', body, re.S)
            if ph:
                prompt = {"head": strip_tags(ph.group(1)),
                          "body": (pc.group(1).strip() if pc else "")}

        # 待办条
        todo = None
        tm = re.search(
            r'<div class="todo">\s*<span class="tk">(.*?)</span>\s*'
            r'<span class="tt">(.*?)</span>\s*<span class="tp">(.*?)</span>',
            body, re.S)
        if tm:
            todo = {
                "tk": strip_tags(tm.group(1)),
                "tt": strip_tags(tm.group(2)),
                "tt_html": tm.group(2).strip(),
                "tp": strip_tags(tm.group(3)),
            }

        # 说课三段（tsay / top / twarn）
        # 兼容两种写法：
        #   格式 A：<div class="tseg X"><span class="tl">🗣 口播</span><p>文本</p></div>
        #   格式 B：<div class="tseg X"><b>🗣 口播</b>：文本</div>（无 <p>、无 span.tl）
        segs = {}
        for sm in re.finditer(r'<div class="tseg (\w+)"\s*>(.*?)</div>', body, re.S):
            cls, inner = sm.group(1), sm.group(2)
            lab = re.search(r'<(?:span class="tl"|b)>(.*?)</(?:span|b)>', inner)
            label = strip_tags(lab.group(1)) if lab else ""
            pm = re.search(r'<p>(.*?)</p>', inner, re.S)
            if pm:
                txt = strip_tags(pm.group(1))
            else:
                txt = re.sub(r'<(?:span class="tl"|b)>.*?</(?:span|b)>', '', inner, flags=re.S)
                txt = strip_tags(txt).lstrip('：: ').strip()
            if txt:
                segs[cls] = {"label": label, "text": txt}

        # SVG 信息：aria-label（写「画面」用）＋ SVG 内文字（兜底）＋ 结构计数（供主视觉粗分）
        aria = re.findall(r'aria-label="([^"]+)"', body)
        svg_text = []
        svg_stat = {"rect": 0, "circle": 0, "text": 0}
        hero = re.search(r'<svg class="hero".*?</svg>', body, re.S)
        if hero:
            hb = hero.group(0)
            svg_stat["rect"] = len(re.findall(r"<rect\b", hb))
            svg_stat["circle"] = len(re.findall(r"<circle\b", hb))
            svg_stat["text"] = len(re.findall(r"<text\b", hb))
            for t in re.findall(r"<text[^>]*>(.*?)</text>", hb, re.S):
                t = strip_tags(t)
                if t and t not in svg_text:
                    svg_text.append(t)

        out.append({
            "id": pid,
            "ord": ordv,
            "num": strip_tags(num.group(1)).replace(" ", "") if num else "",
            "chapter": owner.get(pid, ""),
            "chip": strip_tags(chip.group(1)) if chip else "",
            "title": strip_tags(title.group(1)) if title else "",
            "caps": caps,
            "prompt": prompt,
            "todo": todo,
            "segs": segs,
            "aria": aria,
            "svg_text": svg_text,
            "svg_stat": svg_stat,
            "nviz": len(re.findall(r'<svg class="hero"', body)),
        })
    return out


def main():
    ap = argparse.ArgumentParser(description="四件套·从课件抽取结构数据")
    ap.add_argument("courseware", help="课件 HTML 绝对路径")
    ap.add_argument("data_json", help="输出 data.json 绝对路径")
    ap.add_argument("--report", default=None, help="输出自检报告 txt（默认与 data.json 同目录 _extract.txt）")
    a = ap.parse_args()

    html = io.open(a.courseware, encoding="utf-8").read()
    banners = grab_banners(html)
    pages = grab_pages(html)

    data = {"banners": banners, "pages": pages}
    io.open(a.data_json, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1))

    rep = a.report or os.path.join(os.path.dirname(a.data_json), "_extract.txt")
    L = []
    L.append("源文件：%s" % a.courseware)
    L.append("横幅 %d 条：" % len(banners))
    for b in banners:
        L.append("   %-9s | %-22s | %-28s | %s" % (b["id"], b["pnum"], b["title"], b["chip"]))
    L.append("")
    L.append("页面 %d 页：" % len(pages))
    ncap = sum(1 for p in pages if p["caps"])
    npm = sum(1 for p in pages if p["prompt"])
    ntd = sum(1 for p in pages if p["todo"])
    nsg = sum(1 for p in pages if p["segs"])
    nviz = sum(1 for p in pages if p["nviz"])
    naria = sum(1 for p in pages if p["aria"])
    for p in pages:
        L.append("   %-4s | %-6s | %-26s | cap=%d | 指令=%s | todo=%s | 说课=%s | svg=%d | aria=%d"
                 % (p["num"], p["chip"] or "—", p["title"],
                    len(p["caps"]), "Y" if p["prompt"] else "—",
                    "Y" if p["todo"] else "—",
                    ",".join(p["segs"].keys()) or "—", p["nviz"], len(p["aria"])))
        for c in p["caps"]:
            L.append("        短句> %s" % c)
        if p["todo"]:
            L.append("        todo> %s %s [%s]" % (p["todo"]["tk"], p["todo"]["tt"], p["todo"]["tp"]))
    L.append("")
    L.append("自检：有短句 %d/%d ｜ 有指令 %d ｜ 有 todo %d ｜ 有说课 %d/页 ｜ 有主视觉 %d ｜ 有 aria %d"
             % (ncap, len(pages), npm, ntd, nsg, nviz, naria))
    io.open(rep, "w", encoding="utf-8").write("\n".join(L))

    print("ok banners=%d pages=%d prompt=%d todo=%d segs=%d"
          % (len(banners), len(pages), npm, ntd, nsg))


if __name__ == "__main__":
    main()
