# -*- coding: utf-8 -*-
"""check_repeat.py —— 同页「跨层重复」检测（可复用）

课件每页有多层文字：页标题 / 图示（SVG 内文字）/ 页底大字（.cl）/ 动手条 / 指令说明。
同一件事在两层里各说一遍，读者会觉得「翻来覆去」。本脚本按页两两比较：

  判据：LCS 覆盖率 = LCS(A,B) / min(长度)  ≥ SIM（且短句 ≥ CONTAIN 字）→ 判为重复
  「LCS 覆盖率」比整串包含 / 二元组 Jaccard 都稳：插入几个字（"场景管讲得通" vs
  "场景那栏管讲得通"）不会漏判，语序大改也不会误判。

用法：
    python check_repeat.py <课件.html> [报告.txt]
退出码：0 = 同页无重复；1 = 有待处理项。
报告另附「跨页近似句」一节，仅供复核，不计入失败。
"""
import io
import re
import sys

CONTAIN = 10      # 短句长度下限
SIM = 0.78        # LCS 覆盖率下限
XM = 0.80         # 跨页近似句阈值（仅报告）

if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
    sys.stderr.write(__doc__)
    sys.exit(2)

SRC = sys.argv[1]
RPT = sys.argv[2] if len(sys.argv) > 2 else ''

PUNCT = re.compile(r'[\s，。、；：！？…—·「」『』《》〈〉（）()\[\]【】"\'‘’“”~～|｜/\\+＋=＝→←-]')


def norm(t):
    return PUNCT.sub('', re.sub(r'<[^>]+>', '', t))


def lcs(a, b):
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for ch in a:
        cur = [0]
        for j, cj in enumerate(b):
            cur.append(prev[j] + 1 if ch == cj else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]


def cover(a, b):
    """短句被长句覆盖的比例"""
    if not a or not b:
        return 0.0
    return lcs(a, b) / float(min(len(a), len(b)))


def layers(body):
    out = []
    m = re.search(r'<span class="page-title">(.*?)</span>', body, re.S)
    if m:
        out.append(('页标题', m.group(1)))
    svg = re.search(r'<svg class="hero".*?</svg>', body, re.S)
    if svg:
        for t in re.finditer(r'<text[^>]*>(.*?)</text>', svg.group(0), re.S):
            out.append(('图示', t.group(1)))
    for m in re.finditer(r'<div class="cl">(.*?)</div>', body, re.S):
        out.append(('页底大字', m.group(1)))
    for m in re.finditer(r'<span class="tt">(.*?)</span>', body, re.S):
        out.append(('动手条', m.group(1)))
    for m in re.finditer(r'<div class="exhint">(.*?)</div>', body, re.S):
        out.append(('指令说明', m.group(1)))
    return [(k, re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', v)).strip()) for k, v in out]


s = io.open(SRC, encoding='utf-8').read()

hits = []
allstr = []      # (页, 层, 原文, 归一化)
for pm in re.finditer(r'<section class="page" id="(p\d+)"\s*>(.*?)</section>', s, re.S):
    pid, body = pm.group(1), pm.group(2)
    L = [(k, v, norm(v)) for k, v in layers(body)]
    for k, v, n in L:
        allstr.append((pid, k, v, n))
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            ki, vi, ni = L[i]
            kj, vj, nj = L[j]
            if min(len(ni), len(nj)) < CONTAIN:
                continue
            c = cover(ni, nj)
            if ni in nj or nj in ni or c >= SIM:
                hits.append((pid, ki, kj, c, vi, vj))

# 跨页近似句（仅复核）
cross = []
for i in range(len(allstr)):
    for j in range(i + 1, len(allstr)):
        pi, ki, vi, ni = allstr[i]
        pj, kj, vj, nj = allstr[j]
        if pi == pj or min(len(ni), len(nj)) < 12:
            continue
        c = cover(ni, nj)
        if ni == nj or c >= XM:
            cross.append((pi, pj, ki, kj, c, vi, vj))

lines = ['=== 同页跨层重复（LCS 覆盖率 ≥%.2f，短句 ≥%d 字）===' % (SIM, CONTAIN)]
lines.append('命中 %d 处' % len(hits))
for pid, a, b, c, va, vb in hits:
    lines.append('')
    lines.append('  [%s] %s ⇄ %s   覆盖 %.2f' % (pid, a, b, c))
    lines.append('      A %s' % va[:86])
    lines.append('      B %s' % vb[:86])
lines.append('')
lines.append('=== 跨页近似句（≥%.2f，仅供复核，不计失败）===' % XM)
lines.append('命中 %d 处' % len(cross))
for pi, pj, ki, kj, c, vi, vj in cross[:40]:
    lines.append('  %s/%s ↔ %s/%s  %.2f' % (pi, ki, pj, kj, c))
    lines.append('      %s' % vi[:76])
    lines.append('      %s' % vj[:76])
lines.append('')
lines.append('结论：' + ('同页无重复' if not hits else '同页仍有 %d 处待处理' % len(hits)))
if RPT:
    io.open(RPT, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('REPEAT=%d  CROSS=%d' % (len(hits), len(cross)))
sys.exit(0 if not hits else 1)
