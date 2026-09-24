# -*- coding: utf-8 -*-
"""fp_design.py —— 四件套生成·第 2 步：生成《N-<课名>-简版-设计方案.md》。

用法：

    python fp_design.py <data.json> <输出.md> [--config <config.json>]

不传 --config 时也能出稿——框架段（每页解剖 / 逐页映射 / 施工校验）全部由 data.json
自动推导，只有「四项决策」「贯穿链路」「六类主视觉」「AI 使用点表」这四块需要本课专属内容，
缺省时用占位符标出，人工补齐即可。

config.json 字段（都可省）：

    {
      "course":       "四格漫画故事工厂",
      "courseware":   "1-四格漫画故事工厂-课堂版-简版.html",
      "workbook":     "2-四格漫画故事工厂-漫画社学案.html",
      "date":         "2026-09-17",
      "audience":     "小学高年级至初中（10–15 岁）",
      "style":        "赛博 × 漫画家工作台（霓虹工厂）",
      "ai_tool":      "豆包",
      "decisions":    ["**图 = 手绘 SVG 矢量图**（零插件、零外链、断网可用）", "…"],
      "change_note":  "变更记录：…",
      "rules":        ["保命句 1", "保命句 2"],           // 7 条守则句之类
      "chains":       ["**角色链**：P11 … → P43 …", "**改稿链**：…"],
      "stamp_note":   "七枚章：…",
      "visual_types": [["场景/仪式插画", [1,2,26,46]], ["卡片/徽章/印章", [3,4]], …],
      "ai_points":    [["①","第01章","P12","出 5 个原创角色候选","挑一个，改三处，定型"], …],
      "check_items":  ["① 页码连续", "② 横幅齐全", …]
    }

主视觉分类若不给，脚本按每页 SVG 内容自动粗分（有左中右多栏→左右对照；有多个圆角卡片→卡片阵；
有流程箭头→流程图；其余归结构表格）。粗分只作起点，建议人工核一遍。
"""
import json
import io
import os
import re
import sys
import argparse

sys.stdout.reconfigure(encoding="utf-8")


def page_ord(p):
    """全课页序（1 起）。优先取 data.json 的 ord（由 id="pNN" 算出）；
    旧数据没有 ord 时退回从 id 里抠数字。

    注意：**不要**从 p["num"] 取——课件页头可能写页码（P 01）也可能写章段号（2.1），
    num 在后者里只第一个数字段，取出来会把 2.1 误当第 2 页。
    """
    if p.get("ord"):
        return int(p["ord"])
    return int(re.sub(r"\D", "", p.get("id", "")) or 0)


def derive_visual_type(p):
    """按 SVG 的结构特征粗分主视觉类型（不读短句，避免「→」这类标点误判）。

    判据顺序（从最特征化到最泛）：
      1. 有「指令/界面」类 aria → 工具界面/指令示意
      2. rect 少而 circle 多 → 卡片/徽章/印章（徽章、印章多为圆形编号阵）
      3. aria 里出现对照类词 → 左右对照/反例正例
      4. rect 多（≥8）且分布均匀 → 卡片阵 / 结构表格
      5. 其余：按 rect 数分「流程/步骤图」（少 rect、多 text）与「结构表格/速查图」
    """
    aria = " ".join(p.get("aria", []))
    stat = p.get("svg_stat") or {}
    nrect = stat.get("rect", 0)
    ncircle = stat.get("circle", 0)
    ntext = stat.get("text", 0)

    if any(k in aria for k in ("指令", "界面", "粘贴", "输入框", "对话")):
        return "工具界面/指令示意"
    if any(k in aria for k in ("对照", "反面", "不一样", "这样写", "左", "右", "≠")):
        return "左右对照/反例正例"
    if any(k in aria for k in ("封面", "开营", "仪式", "展", "合影", "颁发", "海报")):
        return "场景/仪式插画"
    if ncircle >= 4 and nrect <= 6:
        return "卡片/徽章/印章"
    if nrect >= 8 and ntext >= 10:
        return "结构表格/公式条/速查图"
    if nrect >= 5 or ntext >= 8:
        return "卡片/徽章/印章"
    return "流程/步骤图"


def main():
    ap = argparse.ArgumentParser(description="四件套·生成设计方案 md")
    ap.add_argument("data_json", help="fp_extract.py 产出的 data.json")
    ap.add_argument("out_md", help="输出 md 绝对路径")
    ap.add_argument("--config", default=None, help="本课 config.json（可选）")
    a = ap.parse_args()

    D = json.load(io.open(a.data_json, encoding="utf-8"))
    pages, banners = D["pages"], D["banners"]
    cfg = {}
    if a.config and os.path.exists(a.config):
        cfg = json.load(io.open(a.config, encoding="utf-8"))

    course = cfg.get("course", "【课名】")
    cw = cfg.get("courseware", "1-【课名】-课堂版-简版.html")
    wk = cfg.get("workbook", "2-【课名】-学案.html")
    date = cfg.get("date", "【YYYY-MM-DD】")
    npage = len(pages)
    nbanner = len(banners)
    nchap = len([b for b in banners if b["id"] not in ("ch0", "appendix")])
    napp = 1 if any(b["id"] == "appendix" for b in banners) else 0
    nAI = len([p for p in pages if p["prompt"]])
    ntodo = len([p for p in pages if p["todo"]])

    L = []
    A = L.append

    # ---------- 头 ----------
    A("# %s · 课堂简版 · 设计方案与逐页映射（施工图）" % course)
    A("")
    A("> %s 现行版（%d 页）确认的四项决策：" % (date, npage))
    dec = cfg.get("decisions") or [
        "**图 = 手绘 SVG 矢量图**（零插件、零外链、断网可用、转 PPT 仍是矢量）",
        "**独立文件** `%s`；配套学案 `%s` 打印使用" % (cw, wk),
        "**极简**：每页 = 主视觉图（约六成版面）＋ ≤3 条短句（每条 ≤14 字）＋ 折叠「🎓 说课」",
        "**%d 个 AI 指令框原样注入**，逐字节校验，一字不改" % nAI,
    ]
    for i, d in enumerate(dec):
        A("> %s %s" % ("①②③④⑤⑥"[i] if i < 6 else "·", d))
    A(">")
    note = cfg.get("change_note") or (
        "变更记录：%s 定稿 %d 页。结构＝序章 ＋ %d 章 ＋ 附录（%d 条横幅）；"
        "每章以一件成果收尾，序章不交东西。" % (date, npage, nchap, nbanner))
    A("> %s" % note)
    A("")

    # ---------- 每页解剖 ----------
    A("## 每页解剖")
    A("")
    A("`页码 + 步骤片 → 标题 → 主视觉 SVG（约六成版面）→ ≤3 短句 →（有指令的页）指令框原样 → 折叠「🎓 说课」`")
    A("")
    # 说课段的实际构成随源课件变 —— 只有口播时别写成三段（见 5.18）
    _segs = set()
    for p in pages:
        for k, v in (p.get("segs") or {}).items():
            if (v or {}).get("text"):
                _segs.add(k)
    _order = [("tsay", "🗣 口播"), ("top", "🎬 操作"), ("twarn", "⚠ 提醒")]
    _desc = " / ".join(lbl for k, lbl in _order if k in _segs) or "🗣 口播"
    _n = len([1 for k, _ in _order if k in _segs])
    _tail = "课堂上学生只见内容与图" if _n >= 2 else "课堂上学生只见内容与图"
    A("- 说课默认收起，分段为 %s——%s" % (_desc, _tail))
    rules = cfg.get("rules")
    if rules:
        A("- 保命信息以短句或图内文字存活，全课 %d 条守则句在线：%s"
          % (len(rules), "".join("「%s」" % r for r in rules)))
    else:
        A("- 保命信息以短句或图内文字存活：【本课守则句清单待补，从短句中挑出必须每页可查的那几条】")
    A("- 章横幅 %d 条（%s ＋ %s ＋ 附录）；导航、返回顶部保留"
      % (nbanner,
         banners[0]["pnum"].split("·")[0].strip() if banners else "序章",
         "CHAPTER 01–%02d" % nchap))
    chips = []
    for p in pages:
        if p["chip"] and p["chip"] not in chips:
            chips.append(p["chip"])
    A("- 深色霓虹配色不变；零 JS、零外链；SVG 内强调一律 `<tspan>`（`<b>` 在 SVG 内不渲染）")
    A("- 步骤片 `.stepchip` 取值：%s" % " / ".join(chips) if chips else "- 步骤片取值：—")
    A("- 全课 %d 页；每页一条 `.todo` 任务条指向学案具体页码（本课 %d 页带 todo）" % (npage, ntodo))
    A("")

    # ---------- 贯穿链路 ----------
    A("## 贯穿链路")
    A("")
    chains = cfg.get("chains")
    if chains:
        for c in chains:
            A("- %s" % c)
    else:
        A("- 【本课成果链待补】写成一环一环：某页产出 → 某页引用 → 最终落在哪件成果上")
        A("- 判据：把示范角色的每件产物按章排成一列，逐件往下推，**从上一件能不能推出下一件**")
    sn = cfg.get("stamp_note")
    if sn:
        A("- %s" % sn)
    A("")

    # ---------- 六类主视觉 ----------
    A("## 六类主视觉")
    A("")
    A("| 类型 | 用在哪 |")
    A("|---|---|")
    vt = cfg.get("visual_types")
    if vt:
        for name, plist in vt:
            A("| %s | %s |" % (name, " ".join("P%02d" % n for n in plist)))
    else:
        bucket = {}
        for p in pages:
            n = page_ord(p)
            if not n:
                continue
            bucket.setdefault(derive_visual_type(p), []).append(n)
        order = ["场景/仪式插画", "卡片/徽章/印章", "流程/步骤图",
                 "左右对照/反例正例", "工具界面/指令示意", "结构表格/公式条/速查图"]
        A("> ⚠️ 下表由 SVG 结构（rect / circle / text 计数 ＋ aria-label）**自动粗分**，"
          "只作起点。本表是给人看的分类索引，不进图、不影响生成——"
          "要精确分类请在 config.json 里给 `visual_types`（格式见脚本头部注释）。")
        A("")
        for name in order:
            nums = bucket.get(name, [])
            A("| %s | %s |" % (name, " ".join("P%02d" % n for n in nums) or "—"))
    A("")

    # ---------- 逐页映射 ----------
    A("## 逐页映射（%d 页）" % npage)
    A("")
    A("| 页 | 步骤 | 标题 | 短句 | 指令 |")
    A("|---|---|---|---|---|")
    over = []
    for p in pages:
        caps = " ／ ".join(p["caps"])
        ncap = len(p["caps"])
        if ncap > 3:
            over.append(("P%02d" % page_ord(p), ncap))
        cmd = ""
        if p["prompt"]:
            cmd = p["prompt"]["head"].split("·")[-1].strip() or p["prompt"]["head"]
        A("| %s | %s | %s | %s | %s |" % ("P%02d" % page_ord(p), p["chip"] or "—", p["title"], caps, cmd or "—"))
    A("")
    if over:
        A("> 自动复核：以下 %d 页短句超过「≤3 条」硬规则，建议回课件核减：" % len(over))
        A("> " + "，".join("%s（%d条）" % (n, c) for n, c in over))
        A("")

    # ---------- 施工与校验 ----------
    A("## 施工与校验")
    A("")
    A("1. 分片手写：`<style>` 头部 ＋ %d 条章横幅 ＋ %d 个 `<section class=\"page\">`，"
      "每页含全部 SVG 与短句，指令页照 %d 处指令原文照抄，不改一个字" % (nbanner, npage, nAI))
    ids = [b["id"] for b in banners]
    A("2. 导航 %d 项锚点：%s，与横幅 id 一一对应"
      % (len(ids), " ＋ ".join("`#%s`" % i for i in ids)))
    ci = cfg.get("check_items") or [
        "① 页码连续；② 横幅 %d 条齐全；③ 导航锚点全命中；④ 短句每条 ≤14 字" % nbanner,
        "⑤ 无 http/script 外链；⑥ 标签配平；⑦ 每页一张主视觉 SVG；⑧ 说课齐备",
        "⑨ 守则句在场；⑩ SVG 内无 `<b>`，强调一律 `<tspan>`",
    ]
    for i, c in enumerate(ci):
        A("%d. 校验：%s" % (3 + i, c))
    A("%d. 配套：`%s` 为打印件（A4），页码引用与课件同步——"
      "凡课件 `.todo` 里写「学案第 N 页」，学案必须有那一页" % (3 + len(ci), wk))
    A("")

    # ---------- AI 使用点 ----------
    A("## 全课 %d 处 AI 使用点" % nAI)
    A("")
    aip = cfg.get("ai_points")
    if aip:
        A("| 序 | 章 | 页 | 让 AI 干什么 | 学生跟着做什么 |")
        A("|---|---|---|---|---|")
        for r in aip:
            A("| %s | %s | %s | %s | %s |" % tuple(r))
    else:
        A("| 序 | 页 | 让 AI 干什么 | 学生跟着做什么 |")
        A("|---|---|---|---|")
        idx = 0
        for p in pages:
            if not p["prompt"]:
                continue
            idx += 1
            A("| %s | %s | 【%s】 | 【学生动作待补】 |"
              % ("①②③④⑤⑥⑦⑧⑨"[(idx - 1) % 9], "P%02d" % page_ord(p), p["prompt"]["head"]))
    A("")
    A("> %d 处以外的环节一律不动 AI。判断标准：每一处都是「**它出参考、你做决定**」——"
      "让它出多个候选（不是 1 个），审稿那一步只提问、不给答案。" % nAI)
    A("")

    io.open(a.out_md, "w", encoding="utf-8").write("\n".join(L))
    print("ok lines=%d pages=%d banners=%d" % (len(L), npage, nbanner))


if __name__ == "__main__":
    main()
