# -*- coding: utf-8 -*-
"""check_caption_len.py —— 页底大字（.cl）「最长语义段 ≤14 字」审计。

精确口径：一条 .cl 内若含分隔符（·/→/；/——），按「最长分段」计长度，而非整串字符数。

用法：
    python check_caption_len.py <课件.html> [报告.txt]
退出码：0 = 全部合规；1 = 有超限条。
"""
import io, re, sys

if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
    sys.stderr.write(__doc__)
    sys.exit(2)

T = sys.argv[1]
RPT = sys.argv[2] if len(sys.argv) > 2 else ""

with io.open(T, "r", encoding="utf-8") as f:
    s = f.read()

def segs(txt):
    # 去掉空白与连接号、破折号、冒号等纯连接符
    t = re.sub(r'<[^>]+>', '', txt)
    t = re.sub(r'\s+', '', t)
    # 按 ——— → · ； 拆成语义段
    parts = re.split(r'[·→]+|——+|;|；', t)
    parts = [p.strip('，,。.') for p in parts if p.strip('，,。.')]
    return parts

rows = []
worst = 0
for m in re.finditer(r'<div class="cl">(.*?)</div>', s, re.S):
    raw = m.group(1)
    t = re.sub(r'<[^>]+>', '', raw)
    t = re.sub(r'\s+', '', t)
    ps = segs(raw)
    longest = max((len(p) for p in ps), default=len(t))
    # 单段（无分隔符）时用整串长度
    if len(ps) <= 1:
        longest = len(t)
    if longest > 14:
        rows.append("%s  [最长段 %d]" % (t, longest))
        worst = max(worst, longest)

out = []
out.append("=== 按「最长语义段」口径审计（<=14 字）===")
out.append("页数/超限条数: %d" % len(rows))
for r in rows:
    out.append("  · " + r)
out.append("")
out.append("最长段字符数上限: %d" % worst)
out.append("结论: " + ("全部合规" if not rows else "仍有 %d 条超限" % len(rows)))

if RPT:
    with io.open(RPT, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
print("OVER=%d" % len(rows))
sys.exit(0 if not rows else 1)
