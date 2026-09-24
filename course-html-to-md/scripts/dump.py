# -*- coding: utf-8 -*-
"""课件 HTML 剥壳：产出 skel.txt / svg.txt / svg_tail.txt
用法：
  python dump.py <课件.html> <输出目录>
说明：Windows 上 PowerShell 不回显 stdout，结果一律写文件。
"""
import re, sys, os

sys.stdout.reconfigure(encoding="utf-8")


def main(src_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    raw = open(src_path, encoding="utf-8").read()
    body = raw.split("<body>", 1)[1] if "<body>" in raw else raw
    body = re.sub(r"<style[\s\S]*?</style>", "", body)
    body = re.sub(r"<script[\s\S]*?</script>", "", body)

    def svg_texts(svg):
        return [t.strip() for t in re.findall(r"<text[^>]*>([^<]*)</text>", svg) if t.strip()]

    parts = re.split(r"(<svg[\s\S]*?</svg>)", body)
    cur, skel, svg_all, svg_tail = "?", [], [], []

    for p in parts:
        if p.startswith("<svg"):
            label = re.search(r'aria-label="([^"]*)"', p)
            label = label.group(1) if label else ""
            txts = svg_texts(p)
            head = "=== SVG on %s :: %s (%d 条) ===" % (cur, label, len(txts))
            skel.append("@@SVG@@ %s || %s" % (label, " | ".join(txts[:40])))
            svg_all.append(head)
            svg_all += ["   " + t for t in txts]
            if len(txts) > 40:                       # 骨架截断的补齐，防止静默丢内容
                svg_tail.append(head.replace("(%d 条)" % len(txts), "第 41 条起"))
                svg_tail += ["   " + t for t in txts[40:]]
        else:
            # 按出现位置取最后一个锚点，避免「章节 id 盖住后面的页 id」
            marks = [(m.start(), m.group(1) or m.group(2)) for m in re.finditer(
                r'<section class="page" id="([^"]+)"|id="(part\d|ch\d|appendix|app\w*)"', p)]
            if marks:
                cur = max(marks)[1]
            for i, ln in enumerate(p.split("\n")):
                s = re.sub(r"\s+", " ", ln.strip())
                if s:
                    skel.append(s)

    def dump(name, rows):
        open(os.path.join(out_dir, name), "w", encoding="utf-8").write("\n".join(rows))

    dump("skel.txt", skel)
    dump("svg.txt", svg_all)
    dump("svg_tail.txt", svg_tail)
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print(__doc__)
