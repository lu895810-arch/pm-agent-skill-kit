# -*- coding: utf-8 -*-
"""fp_run.py —— 五件套生成·一键跑完四步（从第 1 件课件派生后四件）。

用法：

    python fp_run.py <课件.html> <输出目录> [--config <config.json>]

它会依次调用同目录下的四个脚本：
    fp_extract.py  →  <输出目录>/_build/data.json ＋ _extract.txt
    fp_design.py   →  <输出目录>/3-<课名>-简版-设计方案.md
    fp_prompts.py  →  <输出目录>/4-<课名>-简版（全页Prompt合集）.md
    fp_lecture.py  →  <输出目录>/5-<课名>-教师讲课稿.md

第 1、2 件（课件 HTML ／ 学案 HTML）本脚本不动——它们是手写/换装产物，
五件套里的后三件是从第 1 件**派生**的，所以只生成后三件。

命名规则（与参考五件套一致，编号前缀便于排序）：
    <输出目录>/3-<course>-简版-设计方案.md
    <输出目录>/4-<course>-简版（全页Prompt合集）.md
    <输出目录>/5-<course>-教师讲课稿.md
course 取 config 的 course 字段；没给就从课件 <title> 里猜。

讲课稿的「六块」全部自动派生自课件：
  · details.tnote 三段（🗣口播/🎬操作/⚠️提醒）→ 引导语/怎么带/要盯住
  · .todo 任务条                                      → 学生动手（含分钟）
  · .prompt 指令框                                    → AI 指令（复制给豆包）
  · .cl 短句                                          → 投影内容
章级框架（本章主线/过关标准/卡点/各章交付/红线/AI使用点）来自 config.lecture，
没给的章节标【待补】。

跑完会打印各件的字节数与行数，并提示还需人工补齐哪些【待补】项。
"""
import io
import json
import os
import re
import subprocess
import sys
import argparse

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))


def guess_course(courseware):
    """从课件 <title> 猜课名：取第一个分隔符之前的片段。"""
    try:
        s = io.open(courseware, encoding="utf-8").read(4000)
    except Exception:
        return "【课名】"
    m = re.search(r"<title>(.*?)</title>", s, re.S)
    if not m:
        return "【课名】"
    t = re.sub(r"\s+", " ", m.group(1)).strip()
    for sep in ("·", "—", "-", "｜", "|"):
        if sep in t:
            t = t.split(sep)[0].strip()
            break
    return t or "【课名】"


def run(script, *args):
    cmd = [sys.executable, os.path.join(HERE, script)] + [str(x) for x in args]
    r = subprocess.run(cmd, capture_output=True)
    out = r.stdout.decode("utf-8", "replace").strip()
    err = r.stderr.decode("utf-8", "replace").strip()
    if r.returncode != 0:
        print("[FAIL] %s\n  %s" % (script, err or out))
        sys.exit(1)
    return out


def main():
    ap = argparse.ArgumentParser(description="四件套·一键生成后两件（设计方案 md ＋ Prompt 合集 md）")
    ap.add_argument("courseware", help="课件 HTML 绝对路径（第 1 件）")
    ap.add_argument("outdir", help="输出目录（四件套落这里）")
    ap.add_argument("--config", default=None, help="本课 config.json（可选）")
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    build = os.path.join(a.outdir, "_build")
    os.makedirs(build, exist_ok=True)

    cfg = {}
    if a.config and os.path.exists(a.config):
        cfg = json.load(io.open(a.config, encoding="utf-8"))
    course = cfg.get("course") or guess_course(a.courseware)

    data = os.path.join(build, "data.json")
    rep = os.path.join(build, "_extract.txt")

    print("[1/3] 抽取结构 …")
    print("   " + run("fp_extract.py", a.courseware, data, "--report", rep))

    design = os.path.join(a.outdir, "3-%s-简版-设计方案.md" % course)
    prompts = os.path.join(a.outdir, "4-%s-简版（全页Prompt合集）.md" % course)

    print("[2/3] 生成设计方案 md …")
    args = [data, design]
    if a.config:
        args += ["--config", a.config]
    print("   " + run("fp_design.py", *args))

    print("[3/3] 生成 Prompt 合集 md …")
    args = [data, prompts]
    if a.config:
        args += ["--config", a.config]
    print("   " + run("fp_prompts.py", *args))

    lecture = os.path.join(a.outdir, "5-%s-教师讲课稿.md" % course)
    print()
    print("[4/4] 生成 教师讲课稿 md …")
    args = [data, lecture]
    if a.config:
        args += ["--config", a.config]
    print("   " + run("fp_lecture.py", *args))

    print()
    for p in (design, prompts, lecture):
        n = len(io.open(p, encoding="utf-8").read().split("\n"))
        print("   %8d 字节 / %4d 行  %s" % (os.path.getsize(p), n, os.path.basename(p)))

    # 待补提示（同时识别 config 占位【待补】与源课件缺信息（待补））
    todo = set()
    for p in (design, prompts, lecture):
        s = io.open(p, encoding="utf-8").read()
        for m in re.findall(r"【[^】]*待补[^】]*】|（待补）", s):
            todo.add(m)
    if todo:
        print()
        print("   待人工补齐（未给 config 或源课件缺 tnote 信息）：")
        for t in sorted(todo):
            print("     · %s" % t)
    else:
        print()
        print("   无【待补】项——内容齐全。")

    print()
    print("   提示：第 1、2 件（课件 HTML ／ 学案 HTML）需另行产出；")
    print("        本脚本只从第 1 件派生出第 3、4、5 件。")


if __name__ == "__main__":
    main()
