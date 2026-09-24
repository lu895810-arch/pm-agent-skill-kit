#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
课件左线对齐探针（cyx-course-html 附件）

查什么
------
正文最前面那几个「框」——使用说明 `.toolnote`、教师课前准备 `.prep`——必须与正文卡片
`.page` 的外框落在同一条左线上。只用 `max-width + margin:auto` 时，视口 721–1279px 之间
这些块会撑满整宽（left=0），与卡片错开整整 24px；桌面大屏看着正常，一缩窗口就裂开。
本脚本在多个视口宽度下量出真实坐标，并把结果直接画进截图顶部，肉眼可读。

用法
----
    python align_probe.py "C:\\path\\to\\课件.html"
    python align_probe.py "C:\\path\\to\\课件.html" --widths 1440,1200,820,600
    python align_probe.py "C:\\path\\to\\课件.html" --no-shot     # 只生成探针页

产出
----
    %TEMP%\\_align_probe\\probe.html          注入测量脚本的副本
    %TEMP%\\_align_probe\\align_<宽>.png      每档一张截图（顶部黑底绿字为测量值）

判读
----
截图里这几行必须成立：
    >>> toolnote 外框 vs 正文卡: dL=0.0  dR=0.0
    >>> prep     外框 vs 正文卡: dL=0.0  dR=0.0
    >>> 内层内容起点: toolnote=116.0  prep卡片=116.0  差=0.0
    overflow=0
任何一条不为 0，就按 SKILL.md 第 3 步「正文前置组件框的左线对齐」修。
"""

import argparse
import io
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import quote

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

PROBE = """
<script>
(function(){
  function run(){
    function r(s){var e=document.querySelector(s);return e?e.getBoundingClientRect():null;}
    var t=r('.toolnote'), p=r('.prep'), pg=r('.page');
    var i1=r('.prep-item'), th=r('.toolnote .th'), bn=r('.part-banner .pnum');
    var L=[];
    L.push('vw='+window.innerWidth+'   overflow='+(document.documentElement.scrollWidth-document.documentElement.clientWidth));
    function line(tag,o){ return o ? tag+'  L='+o.left.toFixed(1)+'  R='+o.right.toFixed(1)+'  W='+o.width.toFixed(1) : tag+'  (未找到)'; }
    L.push('');
    L.push(line('page(正文卡)  ', pg));
    L.push(line('toolnote(说明) ', t));
    L.push(line('prep(课前准备) ', p));
    L.push('');
    if(t&&pg) L.push('>>> toolnote 外框 vs 正文卡: dL='+(t.left-pg.left).toFixed(1)+'  dR='+(t.right-pg.right).toFixed(1));
    if(p&&pg) L.push('>>> prep     外框 vs 正文卡: dL='+(p.left-pg.left).toFixed(1)+'  dR='+(p.right-pg.right).toFixed(1));
    if(th&&i1) L.push('>>> 内层内容起点: toolnote='+th.left.toFixed(1)+'  prep卡片='+i1.left.toFixed(1)+'  差='+(i1.left-th.left).toFixed(1));
    if(t&&p) L.push('>>> 两块垂直间距: '+(p.top-t.bottom).toFixed(1)+'px');
    if(bn&&pg) L.push('>>> 章节标题文字左='+bn.left.toFixed(1)+'  vs 正文卡='+pg.left.toFixed(1)+'  差='+(bn.left-pg.left).toFixed(1));
    var pre=document.createElement('pre');
    pre.style.cssText='position:fixed;left:0;top:0;z-index:99999;margin:0;padding:12px;'
      +'background:#000;color:#0f0;font:13px/1.65 Consolas,monospace;white-space:pre;border:1px solid #0f0';
    pre.textContent=L.join('\\n');
    document.body.appendChild(pre);
  }
  if(document.readyState==='complete'){setTimeout(run,700);}
  else{window.addEventListener('load',function(){setTimeout(run,700);});}
})();
</script>
"""


def find_browser():
    for p in EDGE_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def main():
    ap = argparse.ArgumentParser(description="课件左线对齐探针")
    ap.add_argument("html", help="课件 HTML 路径")
    ap.add_argument("--widths", default="1440,1200,820,600",
                    help="要测的视口宽度，逗号分隔（默认 1440,1200,820,600；中间档最容易漏）")
    ap.add_argument("--height", type=int, default=700, help="截图高度（默认 700）")
    ap.add_argument("--outdir", default=None, help="输出目录（默认 %%TEMP%%\\_align_probe）")
    ap.add_argument("--no-shot", action="store_true", help="只生成探针页，不截图")
    a = ap.parse_args()

    src = os.path.abspath(a.html)
    if not os.path.exists(src):
        print("[FAIL] 课件不存在: " + src)
        return 2

    html = io.open(src, encoding="utf-8").read()
    if "</body>" not in html:
        print("[FAIL] 文件里找不到 </body>，不像完整课件")
        return 2

    T = tempfile.gettempdir()
    outdir = a.outdir or os.path.join(T, "_align_probe")
    os.makedirs(outdir, exist_ok=True)

    probe_html = os.path.join(outdir, "probe.html")
    io.open(probe_html, "w", encoding="utf-8", newline="").write(
        html.replace("</body>", PROBE + "\n</body>", 1))
    print("[OK] 探针页: " + probe_html)

    try:
        widths = [int(x.strip()) for x in a.widths.split(",") if x.strip()]
    except ValueError:
        print("[FAIL] --widths 只能是逗号分隔的数字")
        return 2

    if a.no_shot:
        print("[--] --no-shot：跳过截图。用浏览器打开上面那个探针页即可。")
        return 0

    browser = find_browser()
    if not browser:
        print("[FAIL] 找不到 Edge / Chrome，无法截图。")
        print("       可加 --no-shot 生成探针页，再手动打开读顶部黑底绿字。")
        return 2
    print("[OK] 浏览器: " + browser)

    url = Path(probe_html).as_uri()
    profile = os.path.join(T, "edge_align_probe")
    results = []

    for w in widths:
        png = os.path.join(outdir, "align_%d.png" % w)
        if os.path.exists(png):
            try:
                os.remove(png)
            except Exception as e:
                print("  [warn] 删旧图失败 %s: %s" % (png, e))
        cmd = [
            browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--user-data-dir=" + profile,
            "--window-size=%d,%d" % (w, a.height),
            "--virtual-time-budget=10000",
            "--screenshot=" + png,
            url,
        ]
        try:
            subprocess.run(cmd, capture_output=True, timeout=90)
        except Exception as e:
            print("  [warn] 启动浏览器异常: %s" % e)
        for _ in range(25):
            if os.path.exists(png):
                break
            time.sleep(1)
        ok = os.path.exists(png)
        results.append((w, ok, png))
        print("  %s  %4dpx  ->  %s" % ("[OK]  " if ok else "[FAIL]", w, png if ok else "未生成"))

    good = [r for r in results if r[1]]
    print("")
    print("截图 %d/%d 张。用 Read 打开每张图，看顶部黑底绿字：" % (len(good), len(results)))
    print("  dL / dR / 内层内容起点差 / overflow  必须都是 0.0")
    print("")
    print("清临时文件（PowerShell 的 Remove-Item 会被沙箱整条拒掉，别用）：")
    print('  python -c "import shutil,os;shutil.rmtree(os.path.join(os.environ.get(\'TEMP\',\'\'),\'_align_probe\'),ignore_errors=True)"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
