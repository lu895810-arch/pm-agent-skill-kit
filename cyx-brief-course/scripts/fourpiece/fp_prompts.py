# -*- coding: utf-8 -*-
"""fp_prompts.py —— 四件套生成·第 3 步：生成《N-<课名>-简版（全页Prompt合集）.md》。

用法：

    python fp_prompts.py <data.json> <输出.md> [--config <config.json>]

产出结构与参考件一致：

    # <课名> · 课堂简版（全页 Prompt 合集）
    > 元信息引用块（📅 / 🛠 / 🎯 / 🧮 / 🛡）
    ## 🔩 风格锚定段（代码块，9 条【】）
    ## 🗺️ 整门课页面地图
    ## 📌 每页字段的用途
    ## 📌 现场课适配说明
    # 🚩 序章 · …（各章分节）
    ### ⏱ 第 N 页 · <标题>
    - **版式** / **画面** / **要显示的文字** / **🎓 说课（❌不进图）** / **给 AI 的指令引文（完整版，❌不进图）**
    ## 📋 附：全课待办与课堂动作一览

**「版式」「画面」两字段的生成策略**（普适任何课件的关键）：
  1. 若 config.json 给了 `layout_overrides`（{"P12": ["版式…","画面…"], …}）→ 用人工稿；
  2. 否则自动合成：版式按 SVG 结构模板（封面 / 卡片阵 / 对照 / 流程 / 表格）出通用描述；
     画面 = aria-label（作者写的画面概述）＋ SVG 内主文字串（画面元素清单）。
     自动稿是**可直接用的初稿**，比空着强；要精细就补 overrides。

config.json 常用字段见 fp_design.py 头部注释，本脚本额外用：
    layout_overrides : {"P01": ["中心构图封面", "暗夜墨蓝底，中央…"]}
    map_rows         : [["🚩 序章 · 开工", "第 1–9 页", "欢迎→看作品→公约→…"], …]
    ai_points        : 同 fp_design，供「指令引文」页标注
"""
import json
import io
import os
import re
import sys
import argparse

sys.stdout.reconfigure(encoding="utf-8")


def strip_tags(t):
    t = re.sub(r"<[^>]+>", "", t or "")
    t = t.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return re.sub(r"\s+", " ", t).strip()


def page_ord_raw(p):
    """页 id 里的数字（pNN → NN）。**只是排序键**，不等于真实页序。

    课件删过页时 id 会留空号（例如删掉 p07 后，剩下 p01…p31 但只有 30 页），
    所以这个值会跳号、且最大值大于总页数。要真实页序用下面的 page_ord()。
    """
    if p.get("ord"):
        return int(p["ord"])
    return int(re.sub(r"\D", "", p.get("id", "")) or 0)


# 真实页序映射：{页 id: 1..N}，由 `build_seq()` 填充。
SEQ = {}


def build_seq(pages):
    """按 id 数字排序后重编 1…N，得到**真实页序**——与课件页脚「第 N 页 / 共 N 页」一致。

    为什么不能用 id 数字：课件删过页后 id 会留空号（p01…p31 但只 30 页），
    直接拿 id 数字当页码，会导致合集里出现「第 29–31 页」「第 31 页」这种
    对不上课件页脚、且区间末尾大于总页数的页码。
    """
    global SEQ
    SEQ = {}
    for i, p in enumerate(sorted(pages, key=page_ord_raw), 1):
        SEQ[p["id"]] = i
    return SEQ


def page_ord(p):
    """全课页序（1 起）。**真实页序**：id 排序后重编，与课件页脚一致。

    **不要**从 p["num"] 取：课件页头可能写页码（P 01）也可能写章段号（2.1），
    后者取第一个数字段会把 2.1 误当第 2 页，导致排序与区间全错。
    """
    if SEQ:
        v = SEQ.get(p.get("id", ""))
        if v:
            return v
    return page_ord_raw(p)


def strip_tags_keep_lines(t):
    """剥标签但**保留换行**——指令引文要逐行保留，才能与课件逐字一致。"""
    t = re.sub(r"<[^>]+>", "", t or "")
    t = t.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in t.split("\n")]
    return "\n".join([ln for ln in lines if ln])


SEG_LABELS = [("tsay", "🗣口播"), ("top", "🎬操作"), ("twarn", "⚠️提醒")]


def seg_labels(pages):
    """按源课件**实际有哪些说课段**拼字段说明——源里没有的段不写进去。

    课件只说口播时，这里就只写「🗣口播」，不会留下「🎬操作/⚠️提醒」这种
    指向空段的字眼（生成器不许描述源里不存在的东西）。
    """
    got = []
    for key, lbl in SEG_LABELS:
        if any((p.get("segs") or {}).get(key, {}).get("text") for p in pages):
            got.append(lbl)
    return "/".join(got) or "🗣口播"


def auto_layout(p):
    """按 SVG 结构合成「版式」字段（通用模板，普适任何课件的暗色霓虹页）。"""
    stat = p.get("svg_stat") or {}
    nrect, ncircle, ntext = stat.get("rect", 0), stat.get("circle", 0), stat.get("text", 0)
    aria = " ".join(p.get("aria", []))
    if any(k in aria for k in ("封面", "开营", "海报", "仪式", "合影", "颁发")):
        return "中心构图封面/仪式页"
    if any(k in aria for k in ("对照", "反面", "不一样", "这样写", "≠")):
        return "左右对照（正例／反例）"
    if any(k in aria for k in ("指令", "界面", "粘贴", "输入框", "对话")):
        return "工具界面示意（模拟对话/输入框）"
    if ncircle >= 4 and nrect <= 6:
        return "徽章／印章阵"
    if nrect >= 8 and ntext >= 10:
        return "结构表格／速查图"
    if nrect >= 5:
        return "卡片阵（横排或网格）"
    return "流程／步骤图"


def auto_scene(p):
    """合成「画面」字段：aria-label 概括 ＋ SVG 内文字元素清单。"""
    aria = p.get("aria", [])
    txt = p.get("svg_text", [])
    parts = []
    if aria:
        parts.append("；".join(aria) + "。")
    if txt:
        # 去掉纯数字/单字符，保留有信息量的文字
        keep = [t for t in txt if len(re.sub(r"[\s\d\W]", "", t, flags=re.U)) >= 2]
        if keep:
            # 不截断：合集是「屏显文字底账」，少一条，AI 重绘就少一行。
            # （2026-09-19 修：原为 keep[:14]，把 p03 底部三行公式/收口/顺序句砍掉了）
            shown = keep if len(keep) <= 40 else keep[:40]
            line = "画面内文字： " + " ／ ".join(shown)
            if len(shown) < len(keep):
                line += " ／ …（共 %d 条，其余见课件该页）" % len(keep)
            parts.append(line + "。")
    if not parts:
        return "【画面待补——源课件该页 SVG 未写 aria-label，建议补一条】"
    return "".join(parts)


def main():
    ap = argparse.ArgumentParser(description="四件套·生成全页 Prompt 合集 md")
    ap.add_argument("data_json", help="fp_extract.py 产出的 data.json")
    ap.add_argument("out_md", help="输出 md 绝对路径")
    ap.add_argument("--config", default=None, help="本课 config.json（可选）")
    a = ap.parse_args()

    D = json.load(io.open(a.data_json, encoding="utf-8"))
    pages, banners = D["pages"], D["banners"]
    build_seq(pages)          # 先建真实页序（id 有空号时不能直接拿 id 数字当页码）
    cfg = {}
    if a.config and os.path.exists(a.config):
        cfg = json.load(io.open(a.config, encoding="utf-8"))

    course = cfg.get("course", "【课名】")
    date = cfg.get("date", "【YYYY-MM-DD】")
    cw = cfg.get("courseware", "1-【课名】-课堂版-简版.html")
    wk = cfg.get("workbook", "2-【课名】-学案.html")
    audience = cfg.get("audience", "【受众待补】")
    style = cfg.get("style", "赛博 × 霓虹工厂")
    tool = cfg.get("ai_tool", "【AI 工具名】")
    npage = len(pages)
    nAI = len([p for p in pages if p["prompt"]])
    ov = cfg.get("layout_overrides") or {}

    L = []
    A = L.append

    # ---------- 头 ----------
    A("# %s · 课堂简版（全页 Prompt 合集）" % course)
    A("")
    A("> 📅 %s ｜ 配套：`%s`（投影原稿）· `%s`（A4 打印）" % (date, cw, wk))
    A("> 🛠 用法：把「风格锚定段」+「该页内容」合并，粘进 **%s** 逐页生成整页幻灯片图。"
      "项目课：按章推进，动笔的活都在纸上。" % tool)
    A("> 🎯 受众：%s ｜ 风格：%s ｜ 共 **%d 页** ｜ 节奏弹性：按章节推进、可拆多次课" % (audience, style, npage))
    A("> 🧮 **教师备课 · 工具与物料**：全课只用 **%s**，共 %d 处 AI 使用点；学案每组一份；"
      "其余物料按本课清单准备。" % (tool, nAI))
    A("> 🛡 **应急预案**：上不了网 → 教师统一投屏演示，学生只做思考、筛选、记录；"
      "关键工具不可用 → 该步骤整章跳过或改手作；成果无法实体展示 → 换线上展示，结构照旧只换载体。")
    A("")
    A("---")
    A("")

    # ---------- 风格锚定段 ----------
    A("## 🔩 风格锚定段（每页 prompt 开头都带这一段，保证全套统一）")
    A("")
    anchors = cfg.get("style_anchors")
    if anchors:
        A("```")
        for s in anchors:
            A(s)
        A("```")
    else:
        A("```")
        A("【风格锚定 · 全套通用】")
        A("标准 16:9 宽屏(1920×1080)。%s 风格。" % style)
        A("【主色调】暗夜墨蓝(#0A0E27 / #0F1638 / #141B3F)底；赛博青绿(#00F5D4)、品红霓虹(#FF2E97)、")
        A("电光黄(#FFE74C)高光与发光描边；紫(#BB86FC)、蓝(#4FC3F7)、绿(#5CE082)、橙(#FF6B35)做信息分区。")
        A("【元素】发光手绘线稿、霓虹字条、卡片与编号圆、页码片、光粒子与电路纹理。")
        A("【人物】需要人时只用剪影或背影，绝不露正脸。")
        A("【版式】标题醒目居上；主视觉大图占画面约 60–70%；每页除标题外最多 3 条短句(每条 ≤14 字)，")
        A("以霓虹字条排在图下或图侧；全套一致。")
        A("【内容密度】图为主、字极少：信息靠画面传达，避免成段文字。")
        A("【气质】酷、有现场感。")
        A("【避免】① 成段说明文字堆叠；② 真实人物露正脸；③ 与课程主题无关的元素乱入；")
        A("④ 中文文字渲染乱码。")
        A("```")
    A("")
    A("---")
    A("")

    # ---------- 页面地图 ----------
    # 篇名统一由 chapter_label() 取：config.map_rows[i][0] 优先（人工润色），
    # 否则用横幅 pnum（源文件里的「序章 · ／ CHAPTER 01 · ／ APPENDIX ·」结构名）。
    map_rows = cfg.get("map_rows") or []

    def chapter_label(i):
        if 0 <= i < len(map_rows):
            return map_rows[i][0]
        b = banners[i] if i < len(banners) else None
        if b:
            return ("🚩 " if i == 0 else "📘 ") + (b["pnum"] or b["title"])
        return "第 %d 章" % (i + 1)

    A("## 🗺️ 整门课页面地图")
    A("")
    A("| 篇 | 页码 | 内容 |")
    A("|---|---|---|")
    bid2idx = {b["id"]: i for i, b in enumerate(banners)}
    bych = {}
    for p in pages:
        n = page_ord(p)
        if not n:
            continue
        ci = bid2idx.get(p.get("chapter", ""), 0) if p.get("chapter") else 0
        bych.setdefault(ci, []).append((n, p["title"]))
    got = False
    for i, b in enumerate(banners):
        if i not in bych:
            continue
        items = sorted(bych[i])
        lo, hi = items[0][0], items[-1][0]
        names = "→".join(t for _, t in items[:6]) + ("…" if len(items) > 6 else "")
        A("| %s | 第 %d–%d 页 | %s |" % (chapter_label(i), lo, hi, names))
        got = True
    if not got:
        A("| — | — | 【页面地图待补——源文件未读到章归属，请给 config.json 的 map_rows】 |")
    A("")
    A("---")
    A("")

    # ---------- 字段用途 ----------
    A("## 📌 每页字段的用途（哪些进图，哪些不进 —— 先看这条）")
    A("")
    A("| 字段 | 给谁用 | 是否渲染进图 |")
    A("|---|---|---|")
    A("| 版式＋画面 | 喂给 %s（控构图与画面） | 转成视觉，不是文字 |" % tool)
    A("| **要显示的文字** | 喂给 %s 渲染 | ✅ **进图**（标题＋短句） |" % tool)
    A("| 🎓 说课（%s） | 给老师（课堂动作，与 HTML 说课逐字一致） | ❌ 不进图 |" % seg_labels(pages))
    A("| **给 AI 的指令引文（完整版）** | **给学生**（复制到 %s 操作） | ❌ **不进图** |" % tool)
    A("")
    A("> 💡 **关于指令**：PPT 上不打整段指令（违背多图少字）。学生上课要**整段复制**指令 → "
      "老师课前把本文档发到班级群或共享文档，或讲到指令页时切 HTML 简版让学生照屏抄录。"
      "铁律：**指令一字不改**，尤其「负面要求」那一行，删了 AI 就会越界。")
    A("")
    A("---")
    A("")

    # ---------- 现场课适配 ----------
    A("## 📌 现场课适配说明")
    A("")
    A("- **使用场景**：分组动手。老师投影讲叙事线与规则，动笔、改稿、表决全部由学生在纸上完成；"
      "AI 只在指定的 %d 页出场，其余环节一律不动。" % nAI)
    A("- **每章节奏**：讲规则页 → 打开指令页、操作员整段粘贴 → 学案上落笔 / 组内互查 → "
      "过关检查页当众盖章 → 岗位轮换（或按下一条规则）。")
    A("- **学案贯穿全课**：所有要交的东西都落在学案上——序章发放，全程别丢。")
    A("- **节奏弹性**：不设固定时长，按章节推进、可拆多次课。")
    A("- **弹性标记**：⏱ 核心 / ⚡ 学生操作·动手 / ⏭ 可压缩")
    A("")
    A("---")
    A("")

    # ---------- 分章逐页 ----------
    # 章归属优先用抽取时读到的真实章（p["chapter"]，从源文件顺序读出，不猜）；
    # 缺 chapter 字段（老 data.json）时退回按横幅数均分。
    nums = [page_ord(p) for p in pages]
    valid = [n for n in nums if n]
    nB = max(1, len(banners))
    has_real_ch = any(p.get("chapter") for p in pages)

    bid2idx = {b["id"]: i for i, b in enumerate(banners)}

    if has_real_ch:
        def chapter_of(n):
            for p in pages:
                if page_ord(p) == n:
                    return bid2idx.get(p.get("chapter", ""), 0)
            return 0
    else:
        cuts = cfg.get("chapter_cuts")
        if isinstance(cuts, dict):
            cuts = [int(v) for _, v in sorted(cuts.items())]
        if not cuts:
            lo, hi = min(valid), max(valid)
            span = hi - lo + 1
            cuts = [lo + round(i * span / nB) for i in range(nB)]
        norm = []
        for c in cuts:
            if not norm or c > norm[-1]:
                norm.append(c)
        while len(norm) < nB:
            norm.append(norm[-1] + 1 if norm else min(valid))
        cuts = norm
        A("> ⚠️ 章节页码区间为**按横幅数均分**的近似（源数据里没有章归属）。"
          "要精确请重新跑 fp_extract.py（新版会记录每页真实所属章），或在 config.json 给 `chapter_cuts`。")
        A("")

        def chapter_of(n):
            idx = 0
            for i, c in enumerate(cuts):
                if n >= c:
                    idx = i
            return min(idx, nB - 1)

    cur_ch = None
    for p in pages:
        n = page_ord(p)
        if not n:
            continue
        ci = chapter_of(n)
        if ci != cur_ch:
            cur_ch = ci
            b = banners[ci] if ci < len(banners) else None
            if b:
                in_ch = [x for x in valid if chapter_of(x) == ci]
                if in_ch:
                    A("# %s（第 %d–%d 页）"
                      % (chapter_label(ci), min(in_ch), max(in_ch)))
                else:
                    A("# %s" % chapter_label(ci))
            else:
                A("# 第 %d 页起" % n)
            A("")

        A("### ⏱ 第 %d 页 · %s" % (n, p["title"]))
        A("")
        pkey = "P%02d" % n
        if pkey in ov:
            lay, vis = ov[pkey][0], ov[pkey][1]
        elif p["id"].upper() in ov:
            lay, vis = ov[p["id"].upper()][0], ov[p["id"].upper()][1]
        else:
            lay, vis = auto_layout(p), auto_scene(p)
        A("- **版式**：%s" % lay)
        A("- **画面**：%s" % vis)
        want = "＋".join(['标题「%s」' % p["title"]] + ["短句「%s」" % c for c in p["caps"]])
        A("- **要显示的文字**：%s" % (want or "【待补】"))
        seg = p["segs"]
        segtxt = "　".join("%s %s" % ({"tsay": "🗣", "top": "🎬", "twarn": "⚠️"}.get(k, "·"), v["text"])
                          for k, v in seg.items() if v.get("text"))
        A("- **🎓 说课（❌不进图）**：%s" % (segtxt or "【无】"))
        if p["prompt"]:
            A("- **给 AI 的指令引文（完整版，❌不进图）**：")
            A("  > **%s**" % p["prompt"]["head"])
            A("  >")
            # 保留原文内的换行（源指令里每行一个要求，逐行引用才与课件逐字一致）
            for ln in strip_tags_keep_lines(p["prompt"]["body"]).split("\n"):
                ln = ln.strip()
                if ln:
                    A("  > %s" % ln)
        else:
            A("- **给 AI 的指令引文**：—")
        A("")

    # ---------- 待办表 ----------
    A("---")
    A("")
    A("## 📋 附：全课待办与课堂动作一览")
    A("")
    A("| 页 | 课堂动作 | 时长 |")
    A("|---|---|---|")
    for p in pages:
        if not p["todo"]:
            continue
        A("| P%02d | %s %s | %s |"
          % (page_ord(p), p["todo"]["tk"], p["todo"]["tt"], p["todo"]["tp"]))
    A("")

    io.open(a.out_md, "w", encoding="utf-8").write("\n".join(L))
    print("ok lines=%d pages=%d prompt=%d" % (len(L), npage, nAI))


if __name__ == "__main__":
    main()
