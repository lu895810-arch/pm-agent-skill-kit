---
name: course-html-to-md
description: 把单文件课件 / 卡片式长页 HTML（课堂版、讲台版、大纲版这类「图为主·字极简」的中文宣讲页）反向转成结构化 Markdown。当用户说「根据这个 HTML 生成 md」「把这堂课导成文档」「课件转文字稿」时使用。产出：单文件 .md，SVG 插图内容被还原为文字/表格，不依赖图片资源。
agent_created: true
---

# 课件 HTML → Markdown

## 何时用

- 用户给一个课件 / 展板 / 长页 HTML，要 md 版本。
- 页面结构是「一页一 section、页头写页码标题、正文是内嵌 SVG 插图 ＋ 底部标语 ＋ 动作行」这一类手工课件。
- **不适用**：普通文章页（直接 Read 后改写即可）、需要保留原视觉的场合（该导出 PDF / 截图，不该转 md）。

## 先判断一件事：要不要图片

SVG 是手写的信息型插图（表格、卡片、清单），**不要**走渲染成图片的路：

- Windows 上 `cairosvg` / `svglib` 基本装不起来（缺 cairo 原生库），`playwright` 通常也没装。
- 调 Edge / Chrome headless 截图在沙箱里被禁止（不许起 GUI 进程）。
- 绝大多数手工课件的 SVG 里塞的全是文字 —— 提取文字重排成 md 表格，信息零损失，还顺手可搜索可编辑。

所以默认口径：**纯文字 md，SVG 内容文字化**。做完在回复里说一句「插图已文字化，需要图片版另说」，把选择权交给用户。

## 四步流程

### 1. 摸清结构，别整文件读

`Read` 整个文件经常超 token 上限（CSS 单行几千字符）。先 `Grep -c '^'` 拿行数，再用脚本剥掉 `<style>/<script>/<svg>` 后 dump 骨架。

`scripts/dump.py` 一次性产出两份东西：

- `skel.txt`：非 SVG 的正文行（含页面头、标语、动作行、说课块）＋ 每张 SVG 所在页码与文字摘要。
- `svg.txt` / `svg_tail.txt`：每张 SVG 按页码归属的完整文字列表。

**踩过的坑**：脚本里给 SVG 文字加 `[:40]` 截断会静默丢内容（本例丢了 p08 的盖章规则整块）。要么不截断，要么另跑一遍只输出被截掉的部分做对照。

### 2. 读骨架，逐页记内容

按 `skel.txt` 顺序读，页与页之间的结构是固定的。原文里的**标语、动作行、说课稿都是正文，别丢**——说课稿在 HTML 里默认折叠，在 md 里就是普通段落。

对表格类 SVG（轮换表、对照表、脚本表），**去看原始 SVG 源码确认行列关系**：文字提取虽然保序，但分不清「同一行的三列」和「上下两段」。用 `Grep -n 'id="pXX"'` 定位再 `Read` 那十几行。

### 3. 分块写 md

一次 `Write` 写不完 49 页（会顶到输出上限）。分 3 块写进 `.workbuddy/gen/md_p1..3.md`，再用 `merge.py` 拼成成品。比 Write + Edit 追加稳。

### 4. 自检

`scripts/lint.py` 检查三件事：每张表格各行列数一致、无 `</div>`/`</span>`/`<section>` 等 HTML 残留、页数是否等于 `###` 数量。跑完再报「做完了」。

## 版式映射（HTML 元素 → Markdown）

| 原页元素 | md 写法 |
|---|---|
| `part-banner`：`pnum` + `h1` + `pdesc` + `timechip` | `## 章名` → 加粗主标题行 → 一行说明 → `📦 成果：…` |
| `section.page`：`page-num` + `stepchip` + `page-title` | `### P 09　序章 · 过关检查（过关）`（页码 ＋ 全角空格 ＋ 标题，chip 放括号里；「总览」这种与标题重复的 chip 丢掉） |
| 承接句 `🔗 接第0N章…` | `> 🔗 **接第 0N 章 XX**：…` |
| SVG 顶部大字标题 | 加粗独立行 |
| SVG 里的卡片组 / 清单 / 表格 | 真 md 表格（列数不一致时改成 bullets） |
| SVG 底部小字注释 | 普通行，跟在结构后面 |
| `cap`：两三条大字标语 | 加粗行，条间用全角 `　｜　` 连 |
| `todo`：✍️/🧭 ＋ 动作 ＋ 时间片 | `> ✍️　动作原文　⏱ 3 分钟` |
| `prompt`：`ph` 标题 ＋ `pc` 正文 | 加粗标题 ＋ ` ```text ` 代码块（保留换行与标点，表情符号照抄） |
| `tnote` 说课：口播 / 操作 / 提醒 | 加粗 `**🎓 说课**` ＋ 三条 bullet，用全角空格顶开标签与正文 |
| `footer` | 文末普通行 ＋ 引用行 |

## 环境注意（Windows / 本机）

- **Bash 不可用**（缺 coreutils，退出码 127）。跑脚本走 PowerShell ＋ 托管 Python 绝对路径：
  `& "C:\Users\admin\.workbuddy\binaries\python\versions\3.13.12\python.exe" script.py`
- **PowerShell 不回显 stdout**：脚本自己写结果文件，再用 `Read` 看。
- 脚本开头 `sys.stdout.reconfigure(encoding="utf-8")`，读写文件一律显式 `encoding="utf-8"`。
- 中间脚本和分块稿放项目 `.workbuddy/gen/`，成品放项目根目录。

## 交付口径

- 文件名沿用原作名（把「·课堂精简版」这类后缀换成 md 能看懂的后缀即可），放在项目根目录。
- 结尾回复里说清三件事：多少页、说课稿有没有带上、插图是怎么处理的。
