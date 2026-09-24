# -*- coding: utf-8 -*-
"""
fp_lecture.py — 由课件 data.json + 配置，生成「教师讲课稿」（第 5 件）。

核心思路：课件每页已经内嵌了讲课需要的一切 ——
  · details.tnote 各段（🗣 口播 / 🎬 操作 / ⚠️ 提醒）→ 讲课稿的「引导语 / 怎么带 / 要盯住」
    **三段齐备时是六块；源课件只有「口播」时自动降为四块**（怎么带 / 要盯住 整块不出现，
    不留空标题、不写「（待补）」）。
  · .todo 任务条                                          → 「学生动手」
  · .prompt 指令框                                        → 「AI 指令引文」
  · .cl 短句                                              → 「投影内容」
所以讲课稿 = 把课件里折叠的说课「展开成六块」，不手抄、不错位。

章级框架（本章主线 / 过关标准 / 卡点 / 各章交付 / 红线 / AI 使用点）属作者层内容，
放在 config.lecture 里；没有就标【待补】。

用法：
  python fp_lecture.py data.json out.md [--config cfg.json]
"""
import sys, io, re, json, argparse

# ---------- 文本工具 ----------
def strip_tags(t):
    t = re.sub(r"<[^>]+>", "", t or "")
    t = t.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return re.sub(r"\s+", " ", t).strip()

def clean_ws(t):
    return re.sub(r"\s+", " ", t or "").strip()

def as_list(v):
    """把 config 里该是 list 的字段统一成 list。

    ⚠️ 血泪坑：`pitfalls` 若写成字符串（如「学生一上来就说「我不会画」，要当场接住」），
    直接用 `for x in v` 会**逐字迭代**，输出成「1. 学 2. 生 3. 一」。
    这里统一兜住：字符串按 `；;。` 拆句，单句也返回单元素 list；None → []。
    """
    if v is None or v == "":
        return []
    if isinstance(v, (list, tuple)):
        return [x for x in v if x not in (None, "")]
    if isinstance(v, str):
        parts = [p.strip() for p in re.split(r"[；;。]", v) if p.strip()]
        return parts or [v.strip()]
    return [v]

def page_ord(p):
    """全课页序（1 起）。优先取 data.json 的 ord（由 id="pNN" 算出），退回从 id 抠数字。

    **不要**从 p["num"] 取：课件页头可能写页码（P 01）也可能写章段号（2.1），
    后者取第一个数字段会把 2.1 误当第 2 页，导致「第 N 页 / 共 M 页」全错。
    """
    if p.get("ord"):
        return int(p["ord"])
    return int(re.sub(r"\D", "", p.get("id", "")) or 0)

# ---------- 章显示名 ----------
def chapter_label(b):
    """把横幅 pnum 翻成讲课稿里的章名。序章 / 第 0N 章 / 附录。"""
    pnum = (b.get("pnum") or b.get("title") or "").strip()
    if not pnum:
        return b.get("title", "")
    if pnum.startswith("序章"):
        return pnum
    if "CHAPTER" in pnum.upper():
        parts = [p.strip() for p in pnum.split("·")]
        num = parts[1] if len(parts) > 1 else ""
        name = parts[2] if len(parts) > 2 else (parts[1] if len(parts) > 1 else pnum)
        return "第 %s 章 · %s" % (num, name)
    if "APPENDIX" in pnum.upper() or pnum.startswith("附录"):
        return "附录"
    return pnum

# ---------- 指令头解析 ----------
def parse_prompt_head(head):
    """🤖 豆包 · 角色候选 · 指令①  →  指令① · 角色候选（指令号无论阿拉伯/带圈数字都认）"""
    head = strip_tags(head)
    parts = [p.strip() for p in re.split(r"[·]", head) if p.strip()]
    parts = [p for p in parts if not p.startswith("🤖") and p != "豆包"]
    num_tok, rest = None, []
    for p in parts:
        if re.match(r"指令\s*[0-9①-⑨]", p):
            num_tok = p
        else:
            rest.append(p)
    if num_tok and rest:
        return "%s · %s" % (num_tok, " · ".join(rest))
    return " · ".join(parts) if parts else (head or "指令")

def extract_minutes(todo):
    """✍️把指令①整段照抄进豆包…不是 1 个5 分钟  →  ('5', '把指令①整段照抄进豆包，一次要 5 个候选，不是 1 个。')"""
    txt = strip_tags(todo)
    txt = re.sub(r"^[\s\W✔✍⚡📝]+", "", txt)  # 去前缀 emoji/符号
    m = re.search(r"(\d+)\s*分钟", txt)
    mins = m.group(1) if m else ""
    if m:
        txt = (txt[: m.start()] + txt[m.end():]).strip(" ；;。")
    return mins, txt

# ---------- 主生成 ----------
def build(data, cfg):
    A = []
    def A_(s=""):
        A.append(s)

    course = cfg.get("course", "本课程")
    L0 = cfg.get("lecture", {}) or {}
    workbook = (L0.get("workbook_name") or cfg.get("workbook_name")
                or re.sub(r"^.*?-", "", cfg.get("workbook", "学案")).replace(".html", "") or "学案")
    if "学案" not in workbook:
        workbook = workbook + "学案"
    wb_pages = cfg.get("workbook_pages", "")
    wb_pages_s = (" 共 %s 页" % wb_pages) if wb_pages else ""
    # 总页数＝**页数**，不是最大页序 —— 课件删过页时 id 会留空号
    # （例：删掉 p07 后仍是 30 页，但 id 跑到 p31），用 max 会多报一页。
    total = len(data["pages"])
    banners = data["banners"]
    pages = data["pages"]
    L = cfg.get("lecture", {}) or {}

    # ============ 头部 ============
    A_("# %s · 课堂简版" % course)
    A_("")
    A_("教师讲课稿 ｜ 对应课件 %d 页 ｜ 配套《%s》A4%s" % (total, workbook, wb_pages_s))
    A_("")
    for line in as_list(L.get("stance")):
        A_("> %s" % line)
    A_("")
    A_("---")
    A_("")

    # ============ 这份稿子怎么用（通用） ============
    # 源课件若只有「口播」一段（用户可能要求把操作/提醒去掉），
    # 下面「怎么带」「要盯住」两块就整体跳过 —— 见 has_top / has_twarn
    has_top = any(((p.get("segs") or {}).get("top") or {}).get("text") for p in pages)
    has_twarn = any(((p.get("segs") or {}).get("twarn") or {}).get("text") for p in pages)
    n_blocks = 4 + (1 if has_top else 0) + (1 if has_twarn else 0)

    A_("## 这份稿子怎么用")
    A_("")
    A_("每一页都按上课的顺序排成%d块，从上往下念，就是一堂课的节奏。" % n_blocks)
    A_("")
    A_("| 块 | 拿它做什么 |")
    A_("| ------ | ----------------------------- |")
    A_("| 这页要干什么 | 看这页要让学生得到什么，备课只读这一行就能串起全章 |")
    A_("| 投影内容 | 投影给学生看的内容，含表格和页底大字 |")
    A_("| 引导语（可照读） | 可以直接照读；一句话背后该做的事，都写在这一段里了 |")
    if has_top:
        A_("| 怎么带 | 手上的动作：先点哪里、停多久、怎么提问 |")
    A_("| 学生动手 | 学生现在做什么、写进学案第几页、大约几分钟 |")
    if has_twarn:
        A_("| 要盯住 | 巡场重点，还有这一页最容易翻车的地方 |")
    A_("")
    tip_no = 1
    A_("%d. 每章开头先读「本章主线」，一眼看完该章的走法；再读各页，顺序就不会乱。" % tip_no)
    tip_no += 1
    if has_twarn:
        A_("%d. 「学生最容易卡住的三个地方」＝各页「要盯住」的汇总。" % tip_no)
        tip_no += 1
    A_("%d. 标了「例（XXX）」的都是范例，不是必填格式，别照抄。" % tip_no)
    A_("")
    A_("页码用「章.节」标，每章从 .1 起；每页右下角另标一个全文页序（第 1 到第 %d 页），打印和口头指路都用得上。" % total)
    A_("")
    A_("---")
    A_("")

    # ============ 全课地图 ============
    A_("## 全课地图")
    A_("")
    chain = L.get("chain_text")
    if chain:
        A_("### 整门课是一条单向链")
        A_("")
        A_(chain)
        A_("")
        A_("每一环都拿上一环的成果当起点。顺序比速度重要，跳过一步，后面就不算数。")
        A_("")
    A_("### 各章各交一件")
    A_("")
    A_("| 章 | 这一段要解决什么 | 交出来的那一件 | 章盖在哪 |")
    A_("| ------ | ---------- | ------------------------- | --------------- |")
    chcfg = L.get("chapters", {}) or {}
    for b in banners:
        cid = b["id"]
        c = chcfg.get(cid, {})
        label = chapter_label(b)
        solves = c.get("solves", "【待补】")
        delivers = c.get("delivers", "【待补】")
        stamp = c.get("stamp", "【待补】")
        A_("| %s | %s | %s | %s |" % (label, solves, delivers, stamp))
    A_("")
    A_("各件拼起来才叫「整套作品包」。少一件，最后一章就不算过。")
    A_("")
    # 全课 AI 使用点
    ai = as_list(cfg.get("ai_points") or L.get("ai_points"))
    if ai:
        A_("### 全课只有 %d 处用 AI" % len(ai))
        A_("")
        A_("| # | 在哪一章 | 让 AI 做什么 | 学生必须跟着做什么 |")
        A_("| - | ------ | ------------- | ---------------------- |")
        for row in ai:
            A_("| %s | %s | %s | %s |" % (row[0], row[1], row[2], row[3]))
        A_("")
        A_("这 %d 处以外的环节一律不动 AI。讲的时候要把这句话说死。" % len(ai))
        A_("")
    # 红线
    rl = as_list(L.get("red_lines"))
    if rl:
        A_("### 红线（碰一条，本章不盖章）")
        A_("")
        for i, line in enumerate(rl, 1):
            A_("%s %s" % (["①", "②", "③", "④", "⑤", "⑥"][i - 1] if i <= 6 else str(i), line))
        A_("")
    A_("---")
    A_("")

    # ============ 分章逐页 ============
    page_what = L.get("page_what", {}) or {}
    page_bottom = L.get("page_bottom", {}) or {}
    page_dot = L.get("page_dot", {}) or {}

    bid2idx = {b["id"]: i for i, b in enumerate(banners)}
    # 每个章的页，按全文页序排序
    bych = {}
    for p in pages:
        ci = bid2idx.get(p.get("chapter", ""), 0)
        bych.setdefault(ci, []).append(p)
    for ci in bych:
        bych[ci].sort(key=page_ord)

    # 真实页序：按课件出现顺序 1…N 重编（不跟 id 走）。
    # id 会因删页留空号（删了 p07 之后 id 直接从 p06 跳到 p08），
    # 直接拿 id 当页序会漏号、且总数多报 —— 见本文件顶部 total 的说明。
    seq_of = {}
    for i, p in enumerate(sorted(pages, key=page_ord), 1):
        seq_of[p["id"]] = i

    for ci, b in enumerate(banners):
        cid = b["id"]
        c = chcfg.get(cid, {})
        sub_pages = bych.get(ci, [])
        # 章头
        label = chapter_label(b)
        sub = c.get("subtitle", "")
        A_("# %s%s" % (label, ("：" + sub) if sub else ""))
        A_("")
        intro = c.get("intro")
        if intro:
            A_("这一章要做的事：%s" % intro)
        delivers = c.get("delivers")
        if delivers:
            A_("本章交什么：%s" % delivers)
        pas = c.get("pass")
        if pas:
            A_("过关标准：%s" % pas)
        ml = c.get("main_line")
        if ml:
            A_("本章主线：%s" % ml)
        pits = as_list(c.get("pitfalls"))
        if pits:
            A_("学生最容易卡住的三个地方：")
            A_("")
            for i, pt in enumerate(pits[:3], 1):
                A_("%d. %s" % (i, pt))
        A_("")

        for p in sub_pages:
            # 章段号：优先用课件页头真实写的 `num`（页头可能写「1-1」或「2.1」这类章段号）；
            # 它是「P 01」这类纯页码时不能用，退回按章内序次生成。
            raw_num = (p.get("num") or "").strip()
            if re.fullmatch(r"\d+[.\-]\d+", raw_num):
                dot = page_dot.get(p["id"]) or raw_num.replace("-", ".")
            else:
                dot = page_dot.get(p["id"]) or ("%d.%d" % (ci, sub_pages.index(p) + 1))
            gnum = seq_of.get(p["id"], page_ord(p))
            title = p["title"]
            A_("## %s ｜ %s" % (dot, title))
            A_("")
            # 这页要干什么
            what = page_what.get(p["id"]) or title
            A_("这页要干什么：%s" % what)
            A_("")
            # 投影内容
            A_("投影内容")
            A_("")
            caps = p.get("caps") or []
            if caps:
                for cap in caps:
                    A_("- %s" % cap)
            else:
                sv = p.get("svg_text") or p.get("aria") or []
                if sv:
                    # 无页底大字时的兜底：**取 SVG 文字末尾两条**，不取开头。
                    # （2026-09-19 修：开头几条常是卡片内的碎片短词，如 p05 取到
                    #   「① ／ 一格一件事 ／ 一格只干一件事」，读起来不是一句话；
                    #   收口句总在 SVG 末尾。）
                    tail = sv[-2:] if len(sv) > 2 else sv
                    A_("- %s" % (" ／ ".join(tail)))
                else:
                    A_("- （本页以讲解为主，无投影文字）")
            if p.get("prompt"):
                clean = parse_prompt_head(p["prompt"]["head"])
                A_("- 〔本页动 AI：%s〕" % clean)
            pb = page_bottom.get(p["id"])
            if pb:
                A_("")
                A_("> 页底收口：%s" % pb)
            A_("")
            # 引导语
            segs = p.get("segs") or {}
            tsay = (segs.get("tsay") or {}).get("text", "")
            top = (segs.get("top") or {}).get("text", "")
            twarn = (segs.get("twarn") or {}).get("text", "")
            A_("引导语（可照读）")
            A_("")
            A_("> %s" % (tsay or "（待补）"))
            A_("")
            # 怎么带（源课件没写这一段就整块跳过，不留空标题）
            if top:
                A_("怎么带：%s" % top)
                A_("")
            # 学生动手
            todo = p.get("todo") or ""
            if isinstance(todo, dict):
                todo_txt = strip_tags(todo.get("tt") or "")
                todo_tp = todo.get("tp") or ""
                mm = re.search(r"(\d+)", todo_tp or "")
                mins = mm.group(1) if mm else ""
            else:
                mins, todo_txt = extract_minutes(todo)
            if todo_txt:
                if mins:
                    A_("学生动手（%s 分钟）：%s" % (mins, todo_txt))
                else:
                    A_("学生动手：%s" % todo_txt)
            else:
                A_("学生动手：本页不动手，只看和听。")
            A_("")
            # 要盯住（源课件没写这一段就整块跳过）
            if twarn:
                A_("要盯住：%s" % twarn)
                A_("")
            # AI 指令
            if p.get("prompt"):
                clean = parse_prompt_head(p["prompt"]["head"])
                A_("%s（复制给豆包）" % clean)
                A_("")
                A_("```text")
                body = p["prompt"]["body"]
                body = strip_tags(body)
                for ln in body.split("\n"):
                    A_(ln.rstrip())
                A_("```")
                A_("")
            # 页脚
            A_("> **%s**　｜　第 %d 页 / 共 %d 页" % (dot, gnum, total))
            A_("")

    # ============ 全篇页脚 ============
    A_("---")
    A_("")
    A_("## 全篇页脚")
    A_("")
    foot = L.get("foot")
    if not foot:
        stance_last = (as_list(L.get("stance")) or [""])[-1]
        # ⚠️ 章数必须**从横幅现算**，不能写死「七章」——
        # 拆章／并章后（见 SKILL §5.13）写死的数字会与课件页脚口径打架。
        n_ch = len([b for b in (data.get("banners") or [])
                    if (b.get("pnum") or "").upper().startswith("CHAPTER")])
        tail = ("序章 ＋ %d 个流程章，每章以一件成果收尾" % n_ch) if n_ch \
            else "序章 ＋ 各章，每章以一件成果收尾"
        foot = [
            "%s · 课堂简版 ｜ 图为主 · 字极简 ｜ 配套《%s》A4%s ｜ %s"
            % (course, workbook, wb_pages_s, tail),
            stance_last,
        ]
    for line in foot:
        A_("> %s" % line)

    return "\n".join(A) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("out")
    ap.add_argument("--config")
    a = ap.parse_args()

    data = json.load(io.open(a.data, encoding="utf-8"))
    cfg = {}
    if a.config:
        cfg = json.load(io.open(a.config, encoding="utf-8"))

    out = build(data, cfg)
    io.open(a.out, "w", encoding="utf-8").write(out)
    print("ok lines=%d bytes=%d" % (out.count("\n") + 1, len(out.encode("utf-8"))))


if __name__ == "__main__":
    main()
