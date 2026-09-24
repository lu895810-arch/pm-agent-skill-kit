# -*- coding: utf-8 -*-
"""把分块写好的 md 片段拼成成品，顺手出个体检报告。
用法：python merge.py <成品.md> <片段1.md> <片段2.md> ...
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")


def main(out_path, part_paths):
    parts = [open(p, encoding="utf-8").read().strip("\n") for p in part_paths]
    text = "\n\n".join(parts) + "\n"
    while "\n\n\n\n" in text:
        text = text.replace("\n\n\n\n", "\n\n\n")
    open(out_path, "w", encoding="utf-8").write(text)

    lines = text.split("\n")
    report = [
        "chars=%d" % len(text),
        "lines=%d" % len(lines),
        "chapters=%d" % sum(1 for l in lines if l.startswith("## ")),
        "pages=%d" % sum(1 for l in lines if l.startswith("### ")),
    ]
    rep = os.path.join(os.path.dirname(out_path) or ".", ".merge-report.txt")
    open(rep, "w", encoding="utf-8").write("\n".join(report))
    print("\n".join(report))


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        main(sys.argv[1], sys.argv[2:])
    else:
        print(__doc__)
