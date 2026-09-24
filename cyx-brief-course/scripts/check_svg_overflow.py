# -*- coding: utf-8 -*-
"""check_svg_overflow.py —— 真机量 SVG 文字有没有越界（会被裁掉 / 压到卡片外）。

为什么必须用真机：靠字符数 × 字号估算不准 —— 类名继承的 `font-size`
（如 `<g font-size="14">` 下的 `.td`）、全角/半角混排、`text-anchor` 都影响占宽。
本脚本把一段 JS 探针注入 HTML，用 Edge 无头跑一遍，读每个 `<text>` 的
`getBBox()`，再与「SVG 画布」和「它所属的卡片 rect」比。

判据：
  ① 越过 SVG 画布  → **必错**（`svg.hero` 默认 `overflow:hidden`，文字被裁掉）
  ② 越过所属卡片    → **必错**（压到卡片外面，视觉上像错位）
  ③ HTML 横向溢出   → 报告（`svg` 元素本身跳过，它的 scrollWidth 不可靠）

用法：
    python check_svg_overflow.py <课件.html> [报告.txt] [--min-card 120]
退出码：0 = 无越界；1 = 有待修项；2 = 参数/环境错。

坑（都踩过）：
  · **宿主卡片判定**：一个文字可能落在多个 rect 的 y 范围内。取「rect.x <= 文字起点
    且 x 最大」的那个（= 从左边最近的那张卡）；若按「宽度最小」取，会把左侧窄卡
    错认成宿主，p02/p05 这种双栏页会一次报出上百条假阳性。
  · **装饰性小 rect 要排除**：徽标/序号小方块（宽 < --min-card，默认 120）不参与
    判定，否则「例」这类角标会被当成卡片。排除后 p02 的居中说明行不再误报。
  · Edge 的 `--user-data-dir` 每次要换新的（复用会命中缓存拿到旧结果）。
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "msedge",
]

PROBE = r"""
<script>
(function(){
  var res = {canvas:[], card:[], html:[]};
  document.querySelectorAll('section.page').forEach(function(pg){
    var svg = pg.querySelector('svg.hero');
    if (!svg) return;
    var vb = (svg.getAttribute('viewBox')||'').split(/[\s,]+/).map(Number);
    var vbW = vb[2]||0;
    var MINC = __MINCARD__;
    var rects = [].slice.call(svg.querySelectorAll('rect')).map(function(r){
      return {x:+r.getAttribute('x'), y:+r.getAttribute('y'),
              w:+r.getAttribute('width'), h:+r.getAttribute('height')};
    }).filter(function(r){ return r.w >= MINC && r.h > 0; });

    [].slice.call(svg.querySelectorAll('text')).forEach(function(t){
      var txt = (t.textContent||'').trim();
      if (!txt) return;
      var b; try { b = t.getBBox(); } catch(e){ return; }
      if (b.x + b.width > vbW + 1){
        res.canvas.push({pg:pg.id, txt:txt,
          x0:+b.x.toFixed(1), x1:+(b.x+b.width).toFixed(1), vbW:vbW});
      }
      var host = null, bestx = -1e9;
      rects.forEach(function(r){
        if (r.x <= b.x + 2 && r.y - 8 <= b.y + 2 && b.y + b.height <= r.y + r.h + 10){
          if (r.x > bestx){ bestx = r.x; host = r; }
        }
      });
      if (host && b.x + b.width > host.x + host.w + 2){
        res.card.push({pg:pg.id, txt:txt, x1:+(b.x+b.width).toFixed(1),
          cardX:host.x, cardW:host.w, right:+(host.x+host.w).toFixed(1),
          over:+((b.x+b.width)-(host.x+host.w)).toFixed(1)});
      }
    });
  });
  document.querySelectorAll('section.page *').forEach(function(el){
    if (el.tagName.toLowerCase() === 'svg') return;
    if (el.scrollWidth > el.clientWidth + 3 && el.clientWidth > 0){
      res.html.push({tag:el.tagName,
        cls:String((el.getAttribute&&el.getAttribute('class'))||'').slice(0,50),
        sw:el.scrollWidth, cw:el.clientWidth,
        txt:(el.textContent||'').replace(/\s+/g,' ').slice(0,70)});
    }
  });
  var pre = document.createElement('pre');
  pre.id = '__OVERFLOW__';
  pre.textContent = JSON.stringify(res);
  document.body.appendChild(pre);
})();
</script>
"""


def find_edge():
    for p in EDGE_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    minc = 120
    for a in sys.argv[1:]:
        if a.startswith("--min-card"):
            minc = int(a.split("=")[1]) if "=" in a else 120
    if not args:
        sys.stderr.write(__doc__)
        return 2

    src = args[0]
    rpt = args[1] if len(args) > 1 else ""
    edge = find_edge()
    if not edge:
        sys.stderr.write("找不到 Edge/Chromium，无法做真机测量。\n")
        return 2

    html = io.open(src, encoding="utf-8").read()
    work = tempfile.mkdtemp(prefix="ovf_")
    probe = PROBE.replace("__MINCARD__", str(minc))
    page = os.path.join(work, "m.html")
    io.open(page, "w", encoding="utf-8", newline="").write(
        html.replace("</body>", probe + "\n</body>"))
    r = subprocess.run(
        [edge, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--window-size=1280,900", "--virtual-time-budget=6000",
         "--user-data-dir=" + os.path.join(work, "_ud"),
         "--dump-dom", "file:///" + page.replace("\\", "/").replace(" ", "%20")],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    m = re.search(r'<pre id="__OVERFLOW__">(.*?)</pre>', r.stdout or "", re.S)
    if not m:
        sys.stderr.write("探针未回传结果（DOM 长度 %d）——换 --user-data-dir 或用非无头模式重试。\n"
                         % len(r.stdout or ""))
        return 2
    d = json.loads(m.group(1))

    lines = []
    lines.append(u"=== ① 越过 SVG 画布（会被裁）=== %d 处" % len(d["canvas"]))
    for x in d["canvas"]:
        lines.append(u"  %s  x %.0f→%.0f  超出 %.0f  「%s」"
                     % (x["pg"], x["x0"], x["x1"], x["x1"] - x["vbW"], x["txt"]))
    lines.append(u"")
    lines.append(u"=== ② 越过所在卡片（压到卡外）=== %d 处" % len(d["card"]))
    for x in d["card"]:
        lines.append(u"  %s  卡片 x=%s w=%s（右 %.0f）文字右端 %.0f  超出 %.0f  「%s」"
                     % (x["pg"], x["cardX"], x["cardW"], x["right"], x["x1"], x["over"], x["txt"]))
    lines.append(u"")
    lines.append(u"=== ③ HTML 横向溢出 === %d 处" % len(d["html"]))
    for x in d["html"][:40]:
        lines.append(u'  <%s class="%s">  %d > %d  「%s」'
                     % (x["tag"], x["cls"], x["sw"], x["cw"], x["txt"]))
    text = u"\n".join(lines)
    if rpt:
        io.open(rpt, "w", encoding="utf-8").write(text)
    # ③ 里 SVG <text> 的 scrollWidth 不可靠，不计失败
    n_bad = len(d["canvas"]) + len(d["card"])
    print("CANVAS_OVER=%d  CARD_OVER=%d  HTML_OVER=%d"
          % (len(d["canvas"]), len(d["card"]), len(d["html"])))
    if not rpt:
        sys.stdout.write(text + "\n")
    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
