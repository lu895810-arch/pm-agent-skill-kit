# -*- coding: utf-8 -*-
"""cyx-brief-course 双轨体检脚本

一次性校验「课堂简版课件 ＋ A4 打印学案」两份交付：

  python check_brief_course.py <课件.html> [<学案.html>]

检查项
  1. 标签配平（div/span/svg/text/section/main/table/tr/td/th/details/summary）
  2. 页数与页码单调递增（课件 section.page ／ 学案 section.sheet）
  3. 章节横幅数 = <main> 数（课件）
  4. 覆盖锚点齐全（#ch0..#chN + #appendix）
  5. 无哨兵残留 @@NEXT@@
  6. AI 指令编号连续（①②③…）
  7. 学案页脚「第 N 页 / 共 M 页」逐页 +1 且末页 = M
  8. **双轨咬合**：课件里「学案第 N 页」①是否超出学案页数（越界）②**是否指向该章该在的那一页**
     （按学案每页自带的章段标注 `4.1–4.3`／`5.1–5.3` 建「章号 → 学案页」底账，与课件页的章号对表）
  9. 课时语汇残留（快线／双轨／分钟版／本页 N 分钟／PART ·）
 10. 渲染抽查（可选，--render）：Edge 无头，四档视口测横向溢出

退出码 0 = 全绿。需要 playwright 时才跑 --render；没有则自动跳过并提示。
"""
import sys, os, re, argparse

sys.stdout.reconfigure(encoding="utf-8")

REQUIRED_TAGS = ["div", "span", "svg", "text", "tspan", "section", "main",
                 "table", "tr", "td", "th", "details", "summary"]

BANNED_WORDS = ["快线", "双轨", "分钟版", "PART ·", "PART·",
                "本页 5 分钟", "本节课", "一节课"]

results = []


def ok(msg):
    results.append(("[PASS]", msg))
    return True


def fail(msg, detail=""):
    results.append(("[FAIL]", msg + ("  " + detail if detail else "")))
    return False


def warn(msg, detail=""):
    results.append(("[WARN]", msg + ("  " + detail if detail else "")))
    return True


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def check_balance(name, s):
    all_ok = True
    for tag in REQUIRED_TAGS:
        o = len(re.findall(rf"<{tag}\b", s))
        c = len(re.findall(rf"</{tag}>", s))
        if o != c:
            fail(f"{name} 标签配平 <{tag}>", f"{o} 开 / {c} 闭")
            all_ok = False
    if all_ok:
        ok(f"{name} 标签全部配平（{len(REQUIRED_TAGS)} 类）")
    return all_ok


def check_sentinel(name, s):
    n = s.count("@@NEXT@@")
    if n:
        return fail(f"{name} 哨兵残留", f"{n} 处 @@NEXT@@")
    return ok(f"{name} 无哨兵残留")


def check_courseware(path):
    """课件专项检查。返回 (页数, 章数)"""
    s = read(path)
    name = os.path.basename(path)

    check_balance(name, s)
    check_sentinel(name, s)

    pages = re.findall(r'class="page" id="p(\d+)"', s)
    nums = [int(x) for x in pages]
    if not nums:
        fail(f"{name} 未找到 section.page")
    else:
        ok(f"{name} section.page = {len(nums)} 页")
        if nums == sorted(nums) and len(set(nums)) == len(nums):
            ok(f"{name} 页码单调递增且无重号（p{min(nums)}…p{max(nums)}）")
        else:
            bad = [f"p{nums[i]}→p{nums[i+1]}" for i in range(len(nums) - 1) if nums[i + 1] <= nums[i]]
            fail(f"{name} 页码顺序异常", ", ".join(bad[:6]))

    # 页头标识：三种写法都合法 ——
    #   ① 页码式    <span class="page-num">P 01</span>
    #   ② 章段点式  <span class="page-num">1.0</span>
    #   ③ 章段杠式  <span class="page-num">1-1</span>（推荐：与「第 1-1 页」口语一致）
    # 只要求数量与 section.page 相等；章段号另查单调递增。
    shown_p = re.findall(r'class="page-num[^"]*">\s*P\s*(\d+)', s)
    shown_dot = re.findall(r'class="page-num[^"]*">\s*(\d+)\.(\d+)\s*<', s)
    shown_dash = re.findall(r'class="page-num[^"]*">\s*(\d+)-(\d+)\s*<', s)
    shown_ch = shown_dot or shown_dash
    shown = shown_p or shown_ch
    if len(shown) != len(nums):
        fail(f"{name} page-num 数量与 section.page 不等", f"{len(shown)} vs {len(nums)}")
    elif shown_ch:
        sep = "." if shown_dot else "-"
        # 章段号按 (章, 节) 字典序必须单调递增
        order = [(int(a), int(b)) for a, b in shown_ch]
        if order == sorted(order) and len(set(order)) == len(order):
            ok(f"{name} 章段标识单调递增且无重号（{order[0][0]}{sep}{order[0][1]}…"
               f"{order[-1][0]}{sep}{order[-1][1]}，{len(order)} 个）")
        else:
            bad = [f"{order[i][0]}{sep}{order[i][1]}→{order[i+1][0]}{sep}{order[i+1][1]}"
                   for i in range(len(order) - 1) if order[i + 1] <= order[i]]
            fail(f"{name} 章段标识顺序异常", ", ".join(bad[:6]))
    else:
        ok(f"{name} page-num 与 section.page 数量一致（{len(shown)} 个）")

    # 页头三件齐备：每页都必须有 page-num ＋ stepchip ＋ page-title
    # （2026-09-18 实测：封面页最容易只写 page-num ＋ page-title，漏掉 stepchip，
    #   于是全篇只有它一个页头比别人少一个元素，视觉上突兀）
    hdr_missing = []
    for _m in re.finditer(r'<section class="page" id="(p\d+)">\s*<div class="page-head">(.*?)</div>',
                          s, re.S):
        _pid, _h = _m.group(1), _m.group(2)
        _lack = [k for k, pat in (("page-num", r'<span class="page-num'),
                                  ("stepchip", r'<span class="stepchip"'),
                                  ("page-title", r'<span class="page-title"'))
                 if not re.search(pat, _h)]
        if _lack:
            hdr_missing.append(f"{_pid}:缺{'/'.join(_lack)}")
    if hdr_missing:
        fail(f"{name} 页头三件不齐（page-num＋stepchip＋page-title）",
             ", ".join(hdr_missing[:8]))
    else:
        ok(f"{name} 每页页头三件齐备（page-num ＋ stepchip ＋ page-title）")

    nbanner = len(re.findall(r'class="part-banner"', s))
    nmain = len(re.findall(r"<main\b[^>]*>", s))
    if nbanner == nmain and nbanner > 0:
        ok(f"{name} 章节横幅 {nbanner} 条 = <main> {nmain} 段")
    else:
        fail(f"{name} 章节横幅与 <main> 不匹配", f"banner={nbanner} main={nmain}")

    ids = set(re.findall(r'id="((?:ch|part)\d+|appendix)"', s))
    hrefs = set(re.findall(r'href="#((?:ch|part)\d+|appendix)"', s))
    missing = hrefs - ids
    if missing:
        fail(f"{name} 导航锚点落空", ", ".join(sorted(missing)))
    elif hrefs:
        ok(f"{name} 导航锚点全部命中（{len(hrefs)} 个）")

    # 指令编号
    instr = re.findall(r"指令([①②③④⑤⑥⑦⑧⑨])", s)
    uniq = []
    for x in instr:
        if x not in uniq:
            uniq.append(x)
    expect = "①②③④⑤⑥⑦⑧⑨"[: len(uniq)]
    if "".join(uniq) == expect:
        ok(f"{name} AI 指令编号连续（{len(uniq)} 处）")
    else:
        fail(f"{name} AI 指令编号跳号/重号", "".join(uniq))

    # 课时语汇
    for w in BANNED_WORDS:
        if w in s:
            fail(f"{name} 课时语汇残留：{w}")
    if not any(w in s for w in BANNED_WORDS):
        ok(f"{name} 无课时语汇残留")

    return len(nums), nbanner, s


def check_workbook(path, courseware_s=None, courseware_pages=0):
    """学案专项检查。返回页数"""
    s = read(path)
    name = os.path.basename(path)

    check_balance(name, s)
    check_sentinel(name, s)

    sheets = re.findall(r'class="sheet"', s)
    n = len(sheets)
    if n:
        ok(f"{name} section.sheet = {n} 页")
    else:
        fail(f"{name} 未找到 section.sheet")

    # 页脚逐页 +1
    foots = re.findall(r"第\s*(\d+)\s*页\s*/\s*共\s*(\d+)\s*页", s)
    if foots:
        pg = [int(a) for a, _ in foots]
        tot = {int(b) for _, b in foots}
        if pg == list(range(1, len(pg) + 1)):
            ok(f"{name} 页脚页码逐页 +1（1…{len(pg)}）")
        else:
            fail(f"{name} 页脚页码不连续", str(pg))
        if len(tot) == 1 and tot.pop() == n:
            ok(f"{name} 页脚总数 = 实际页数 {n}")
        else:
            fail(f"{name} 页脚总数与实际页数不符", f"n={n}")
    elif "【N】" in s and "页 / 共" in s:
        # 未落地的模板：页脚里还留着占位符。给 WARN 不算 FAIL，但要提醒替换。
        warn(f"{name} 页脚仍是占位符【N】——落地时必须换成实际页码（此检查项本轮跳过）")
    else:
        fail(f"{name} 未找到页脚「第 N 页 / 共 M 页」")

    # 双轨咬合：课件里「学案第 N 页」
    if courseware_s is not None:
        refs = re.findall(r"学案第\s*(\d+)\s*页", courseware_s)
        over = sorted({int(r) for r in refs if int(r) > n})
        if over:
            fail("双轨咬合：课件引用了学案不存在的页", f"学案只有 {n} 页，却引用第 {over} 页")
        elif refs:
            ok(f"双轨咬合正常：课件 {len(refs)} 处引用均在 1…{n} 页内")

        # 指向正确（2026-09-19 补）：光查「没越界」不够——页码指错页照样过。
        # 底账从学案自身取：每页小节标注「4.1–4.3」「5.1–5.3」，据此建「章号 -> 学案页」；
        # 课件页按自己的页码前缀（如 5.1）认领章号，两下一对就知道该指第几页。
        sheets = re.findall(r'<section[^>]*class="sheet"[^>]*>(.*?)</section>', s, re.S)
        ch2pg = {}
        for i, sh in enumerate(sheets, 1):
            for a, b in re.findall(r"(\d+)\.\d+\s*[\u2013\u2014\u301c~\-]\s*(\d+)\.\d+", sh):
                ch2pg.setdefault(int(a), i)
                ch2pg.setdefault(int(b), i)
        bad = []
        for i, sec in enumerate(re.findall(r'<section class="page"[^>]*>(.*?)</section>',
                                           courseware_s, re.S), 1):
            m = re.search(r'<span class="page-num[^"]*">\s*(\d+)\.\d+\s*</span>', sec)
            if not m:
                continue
            exp = ch2pg.get(int(m.group(1)))
            if exp is None:          # 序章 / 认识 / 附录等无章段标注的页，不参与此检查
                continue
            for mt in re.finditer(r"学案第\s*(\d+)\s*页", sec):
                win = sec[max(0, mt.start() - 30):mt.end() + 20]
                if "章格" in win or "盖章" in win:   # 章格统一在学案第 1 页，属正常
                    continue
                if int(mt.group(1)) != exp:
                    bad.append(f"课件 p{i}（{m.group(1)}.x）引学案第 {mt.group(1)} 页，应为第 {exp} 页")
        if bad:
            fail("双轨咬合：课件页码指向与学案的章段不符", "；".join(bad))
        elif ch2pg:
            ok("双轨咬合：按章段指向学案页全部命中（底账 %s）"
               % "/".join("%d->p%d" % (k, v) for k, v in sorted(ch2pg.items())))
    return n


def check_render(htmls):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        results.append(("[SKIP]", "--render 需要 playwright，本机未安装，已跳过渲染抽查"))
        return
    vps = [(1440, 900), (1200, 900), (820, 900), (600, 900)]
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="msedge")
        except Exception as e:
            results.append(("[SKIP]", f"未找到 Edge，已跳过渲染抽查：{e}"))
            return
        for h in htmls:
            if not h or not os.path.exists(h):
                continue
            nm = os.path.basename(h)
            for w, hh in vps:
                pg = b.new_page(viewport={"width": w, "height": hh})
                pg.goto("file:///" + h.replace("\\", "/"))
                pg.wait_for_timeout(400)
                r = pg.evaluate("""() => {
                  const W = document.documentElement.clientWidth;
                  const over = [];
                  document.querySelectorAll('.page,.hero,.prompt,.todo,.tnote,.sheet,.wake,.grid2,.grid5,.stampbar,.fourgrid,.mast').forEach(el=>{
                    const b = el.getBoundingClientRect();
                    if (Math.round(b.right + window.scrollX - W) > 1) over.push(el.className.slice(0,30));
                  });
                  return {sw: document.documentElement.scrollWidth, vw: W, over};
                }""")
                if r["over"]:
                    fail(f"{nm}@{w} 横向溢出", str(r["over"][:5]))
                else:
                    ok(f"{nm}@{w} 无横向溢出（scrollW={r['sw']}）")
                pg.close()
        b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("courseware", help="课堂简版课件 HTML 路径")
    ap.add_argument("workbook", nargs="?", help="A4 打印学案 HTML 路径（可选）")
    ap.add_argument("--render", action="store_true", help="额外跑 Edge 无头渲染抽查")
    a = ap.parse_args()

    cp, _, cs = check_courseware(a.courseware)
    if a.workbook:
        check_workbook(a.workbook, cs, cp)

    print(f"课件 {os.path.basename(a.courseware)}：{cp} 页")
    if a.workbook:
        print(f"学案 {os.path.basename(a.workbook)}")

    if a.render:
        check_render([a.courseware, a.workbook])

    for tag, msg in results:
        print(f"{tag} {msg}")

    nf = sum(1 for t, _ in results if t == "[FAIL]")
    nw = sum(1 for t, _ in results if t == "[WARN]")
    print(f"\nFAIL = {nf}   WARN = {nw}   SKIP = {sum(1 for t, _ in results if t == '[SKIP]')}")
    sys.exit(1 if nf else 0)


if __name__ == "__main__":
    main()
