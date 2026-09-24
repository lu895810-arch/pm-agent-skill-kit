# -*- coding: utf-8 -*-
"""派生文档对齐校验：把本稿与内容基准比一遍，八项全绿才算对齐完成。

用法：
  python check_alignment.py --out <本稿.md> --base <基准md> --pages 48
  python check_alignment.py --out 稿.md --base 基准.md --forbid 轮岗,轮换,岗位固定 --report r.txt

退出码 0 = 全绿；1 = 有 FAIL。Windows 控制台请先设 PYTHONIOENCODING=utf-8。
"""
import argparse, difflib, io, os, re, sys

# 注意：不含 \u2190-\u21FF（→ 是标点，按约定要保留）
EMOJI = re.compile("[\u20e3\ufe0f\U0001F300-\U0001FAFF\u2600-\u27BF]")
RE_FOOT_NEW = re.compile(r"^> \*\*([0-9A]+\.[0-9]+)\*\*\u3000｜\u3000第 (\d+) 页 / 共 (\d+) 页\s*$", re.M)
RE_FOOT_OLD = re.compile(r'^<p align="right">([0-9A]+\.[0-9]+) ｜ 第 (\d+) 页</p>\s*$', re.M)
RE_HEAD = re.compile(r"^#{2,3}\s*([0-9A]+\.[0-9]+)", re.M)
RE_REF = re.compile(r"(?<![\w.\-/])([0-9A]+\.[0-9])(?![\w])")
RE_CODE = re.compile(r"```[a-z]*\n(.*?)```", re.S)


def read(p):
    return open(p, "rb").read().decode("utf-8-sig").replace("\r\n", "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--base")
    ap.add_argument("--pages", type=int)
    ap.add_argument("--forbid", default="")
    ap.add_argument("--report")
    a = ap.parse_args()

    out = read(a.out)
    base = read(a.base) if a.base and os.path.exists(a.base) else None
    L, fails = [], []

    def chk(name, ok, detail=""):
        L.append("  %-4s %s%s" % ("PASS" if ok else "FAIL", name, ("  —— " + detail) if detail else ""))
        if not ok:
            fails.append(name)

    # 1) 标题编号：按章分组，每组 1..N 连续（允许 0 开头）
    heads = RE_HEAD.findall(out)
    groups, order = {}, []
    for h in heads:
        c = h.split(".")[0]
        if c not in groups:
            groups[c], _ = [], order.append(c)
        groups[c].append(int(h.split(".")[1]))
    seqok, seqmsg = True, []
    for c in order:
        v = sorted(groups[c])
        if v != list(range(v[0], v[0] + len(v))):
            seqok = False
            seqmsg.append("%s 章不连续 %s" % (c, v))
    tot = len(heads)
    chk("标题编号连续", seqok, "; ".join(seqmsg))
    if a.pages:
        chk("页数 = 标题数 = %d" % a.pages, tot == a.pages, "实测 %d" % tot)

    # 2) 页脚
    fn = RE_FOOT_NEW.findall(out)
    fo = RE_FOOT_OLD.findall(out)
    if fn:
        chk("页脚数 = 页数", not a.pages or len(fn) == a.pages, "新格式 %d 处" % len(fn))
        nums = [int(x[1]) for x in fn]
        chk("页码严格单调 1..N", nums == list(range(1, len(nums) + 1)),
            "" if nums == list(range(1, len(nums) + 1)) else "断在 %s" % nums[:5])
        chk("页脚「共 N 页」唯一且 = 页数",
            len(set(x[2] for x in fn)) == 1 and (not a.pages or int(fn[0][2]) == a.pages),
            "取值 %s" % sorted(set(x[2] for x in fn)))
    else:
        chk("页脚已转成基准格式", False, "仍是旧格式 %d 处" % len(fo))

    # 3) 残留旧编号：正文里出现不属于本稿编号集的 X.Y
    valid = set(heads)
    stray = sorted(set(RE_REF.findall(out)) - valid)
    chk("正文无越界页码引用", not stray, "越界 %s" % stray[:12])

    # 4) 禁项术语 / 图标
    for w in [w for w in re.split(r"[,，\s]+", a.forbid) if w]:
        n = out.count(w)
        chk("禁用词「%s」= 0" % w, n == 0, "实测 %d" % n)
    em = EMOJI.findall(out)
    chk("禁项图标 = 0", not em, "实测 %d %s" % (len(em), sorted(set(em))[:8]))

    # 5) 锁定块逐字比对基准
    if base is not None:
        co, cb = RE_CODE.findall(out), RE_CODE.findall(base)
        chk("锁定块数量一致", len(co) == len(cb), "本稿 %d / 基准 %d" % (len(co), len(cb)))
        for i in range(min(len(co), len(cb))):
            x, y = re.sub(r"\s+", "", co[i]), re.sub(r"\s+", "", cb[i])
            if x == y:
                L.append("      块#%d 逐字一致 (%d)" % (i + 1, len(x)))
                continue
            fails.append("块#%d 不一致" % (i + 1))
            L.append("  FAIL 块#%d 不一致  本稿 %d / 基准 %d" % (i + 1, len(x), len(y)))
            sm = difflib.SequenceMatcher(None, y, x)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag != "equal":
                    L.append("       %s 基准[%s] -> 本稿[%s]  …%s…"
                             % (tag, y[i1:i2], x[j1:j2], y[max(0, i1 - 18):i2 + 18]))

    # 6) 头部页数声明（只看开头十几行；先剔掉"学案共 N 页"这类配套件页数）
    if a.pages:
        probe = "\n".join(out.split("\n")[:14])
        probe = re.sub(r"配套[^｜|\n]*学案[^｜|\n]*共\s*\d+\s*页", "", probe)
        probe = re.sub(r"《[^》]*学案》", "", probe)
        got = [int(x or y) for x, y in re.findall(r"共\s*(\d+)\s*页|对应课件\s*(\d+)\s*页", probe)]
        chk("头部页数声明 = %d" % a.pages, all(g == a.pages for g in got) if got else True,
            "声明 %s" % got)

    rep = "对齐校验 ｜ 本稿 %s\n" % os.path.basename(a.out) + "\n".join(L) + \
          "\n\n结果：%s（FAIL %d）\n" % ("全绿" if not fails else "有未通过项", len(fails))
    sys.stdout.write(rep)
    if a.report:
        open(a.report, "wb").write(rep.encode("utf-8"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
