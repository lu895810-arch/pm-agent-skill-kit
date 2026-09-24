#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""课件「抽页截图」探针：Playwright + 本机 Edge，按元素截图。

为什么不用 Edge 无头命令行（见 SKILL.md 7.1b）：
  那条路要先把「其余页隐藏」写成一个探针副本，再 Start-Process 轮询等 png 落地，
  拍出来的还是整页（含大片留白）。Playwright 可以直接对 `#p24` 这样的元素截图，
  一条命令出图，不用造副本、不用轮询、不用等 fragment 渲染。

环境（本机实测可用，2026-09-16）：
  解释器  C:\\Users\\admin\\.workbuddy\\binaries\\python\\envs\\default\\Scripts\\python.exe
  浏览器  playwright 自带 chromium 未下载，**必须** channel="msedge" 复用系统 Edge。

用法：
  python shot_page.py <课件.html> <输出目录> [页id ...] [--width 1500] [--full] [--scale 2]

例：
  # 只拍某几页（id 不带 #）
  python shot_page.py "四格漫画故事工厂·大纲版.html" .workbuddy/gen p24 p25
  # 整页长图
  python shot_page.py "xx.html" .workbuddy/gen --full
  # 元素定位不到时，打印页面里所有 page id 供核对
  python shot_page.py "xx.html" .workbuddy/gen --list

输出：<输出目录>/<id>_check.png（整页为 full_check.png），控制台打印每张图的字节数。
"""
from __future__ import annotations

import argparse
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

# 页面入场动画会把元素停在 opacity:0 / translateY 上，截图前一律关掉
KILL_ANIM = """
.page, .page *, section, section *, main * {
  opacity: 1 !important;
  transform: none !important;
  animation: none !important;
  transition: none !important;
}
html { scroll-behavior: auto !important; }
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html", help="课件 HTML 路径")
    ap.add_argument("outdir", help="截图输出目录")
    ap.add_argument("ids", nargs="*", help="要拍的 page id（不带 #）")
    ap.add_argument("--width", type=int, default=1500, help="视口宽度，默认 1500")
    ap.add_argument("--height", type=int, default=1000, help="视口高度，默认 1000")
    ap.add_argument("--scale", type=float, default=2.0, help="devicePixelRatio，默认 2")
    ap.add_argument("--full", action="store_true", help="整页长图（忽略 ids）")
    ap.add_argument("--list", action="store_true", help="只列出页面里的所有 id，不截图")
    args = ap.parse_args()

    src = pathlib.Path(args.html).resolve()
    if not src.exists():
        print(f"[ERR] 找不到文件：{src}")
        return 2
    outdir = pathlib.Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge")
        except Exception as exc:  # noqa: BLE001
            print(f"[ERR] 起不了 Edge：{exc}")
            print("      确认装了 Microsoft Edge；或改用 SKILL.md 7.1b 的 Edge 无头路径。")
            return 3
        page = browser.new_page(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=args.scale,
        )
        page.goto(src.as_uri())
        page.add_style_tag(content=KILL_ANIM)
        page.wait_for_timeout(600)

        if args.list:
            ids = page.eval_on_selector_all(
                "section.page", "els => els.map(e => e.id)"
            )
            print("页面 id：" + ", ".join(ids))
            browser.close()
            return 0

        made: list[pathlib.Path] = []
        if args.full:
            out = outdir / "full_check.png"
            page.screenshot(path=str(out), full_page=True)
            made.append(out)
        else:
            for pid in args.ids:
                sel = f"#{pid}" if not pid.startswith("#") else pid
                loc = page.locator(sel)
                if loc.count() == 0:
                    print(f"[MISS] {sel} 不在页面里（用 --list 看全部 id）")
                    continue
                out = outdir / f"{sel.lstrip('#')}_check.png"
                loc.first.screenshot(path=str(out))
                made.append(out)

        for f in made:
            print(f"[OK] {f.name}  {f.stat().st_size} bytes")
        if not made:
            print("没有产出任何图。")
        browser.close()
    return 0 if made else 1


if __name__ == "__main__":
    sys.exit(main())
