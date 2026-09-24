# -*- coding: utf-8 -*-
"""md 自检：表格列数是否自洽、有没有 HTML 残留、页数统计。
用法：python lint.py <成品.md>
退出码 0 = 全绿。
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

RESIDUE = ["</div>", "</span>", "</section>", "<section", "<details", "&nbsp;", "undefined"]


def main(md_path):
    lines = open(md_path, encoding="utf-8").read().split("\n")
    bad, block, start = [], [], 0

    def flush():
        if len(block) >= 2:
            counts = [r.count("|") for _, r in block]
            if len(set(counts)) != 1:
                bad.append((start + 1, counts, block[0][1][:90]))

    for i, l in enumerate(lines):
        if l.strip().startswith("|"):
            if not block:
                start = i
            block.append((i, l.strip()))
        else:
            flush()
            block = []
    flush()

    txt = "\n".join(lines)
    out = ["表格全部自洽" if not bad else "表格列数不一致："]
    for a, b, c in bad:
        out.append("  第 %d 行 counts=%s :: %s" % (a, b, c))
    hit = ["残留 %s × %d" % (p, txt.count(p)) for p in RESIDUE if txt.count(p)]
    out += hit or ["无 HTML 残留"]
    out.append("章 %d ／ 页 %d ／ 行 %d" % (
        sum(1 for l in lines if l.startswith("## ")),
        sum(1 for l in lines if l.startswith("### ")),
        len(lines)))
    open(os.path.join(os.path.dirname(md_path) or ".", ".lint-report.txt"),
         "w", encoding="utf-8").write("\n".join(out))
    print("\n".join(out))
    return 0 if not bad and not hit else 1


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        sys.exit(main(sys.argv[1]))
    print(__doc__)
