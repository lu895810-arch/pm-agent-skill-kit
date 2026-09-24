# pm-agent技能包（含第三方改造适配技能）

这是一套面向 WorkBuddy（以及兼容 Anthropic Agent Skills 规范的工具）的自定义技能集合。它分成两大部分：

1. **作者原创技能**——`cyx-` 系列（Lulu 把实际工作里反复打磨的方法论沉淀成技能）+ 少量 Buddy 自建的工具技能。
2. **改造适配技能**——由第三方作者创作，Buddy 将其适配 / 归档到 WorkBuddy 环境。

每个技能都是一个独立目录，里面是 `SKILL.md` 加脚本、模板或参考文件。技能之间按产品线串接——前一个的产出是后一个的输入，README 里会标清楚上下游。

每个技能条目的三件事：**做什么 / 解决什么问题 / 适合场景**，并标注**作者归属**〔原创〕或〔改造适配 · 原作者〕。

## 怎么装

把需要的技能目录整个复制到 WorkBuddy 的技能目录：

```
~/.workbuddy/skills/
```

放进目录后，重启 WorkBuddy 或在技能面板刷新即可识别。只用其中一部分也行，但凡是标注了「上游 / 下游」的，缺了上游产物下游就跑不起来，装的时候一并装上。

> 改造适配类技能如果带运行依赖（如 `archify` 需要 `npm install`、`drawio-*` 需要 `drawio-ai` 引擎），请按对应 `SKILL.md` 里的适配说明先把依赖装好。

---

## 作者原创技能（Lulu / Buddy 自建）

> 以下均为 〔原创 · Lulu〕——`cyx-` 系列是 Lulu 把实际工作里反复打磨的方法论沉淀成的技能；`gh-skill-install` 为 〔原创 · Buddy〕（技能安装/适配工具）。

## 一、需求与产品规划

这一类解决的是同一件事：你手里有一堆素材——白皮书、官网截图、会议记录、竞品、旧方案、脑子里的想法——要把它们收敛成一份能评审、能立项、能排期的产品文档。区别只在"重到什么程度"。

- **cyx-summary-need** —— 轻量需求文档（产出单文件 HTML）。手里有产品白皮书、官网、截图、旧方案，要快速整理成一份能直接在浏览器打开、能讲、能往后补数据的功能需求稿时用它。适合需求 brief、功能清单、立项前的轻量梳理。
- **cyx-ears-need** —— 重型 PRD（EARS 六段式 + 派工粒度）。手里有想法、会议记录、竞品截图、原型稿，要收敛成一份工程级 PRD（每条需求带验收标准、能拆到量产派工粒度）时用它。适合十章式 PRD、评审速览加审阅议题。它是"重装工具"，没点名一般走别的技能。
- **cyx-priority-need** —— 需求优先级评估（P0–P3 + RICE 打分）。手里有一批需求，要给它们分级、排优先级，用于需求评审、版本规划、需求池排序时用它。产出是"判定 + 依据 + 风险"的排序结论，不做整盘产品规划。
- **cyx-strcuture-need** —— 产品功能规划（四层架构、模块拆解、优先级矩阵、MVP 与路线图，产出单文件 HTML）。要把一款产品拆成模块、定 MVP 范围和路线图、拿去做立项评审时用它。比 PRD 轻，不要求 EARS 工程粒度。
- **cyx-original-need-md / cyx-original-need-html** —— 原始需求与功能演进分析（同一套方法论，两种产物形态）。从现有产品反推当初的原始需求、梳理"为什么做成现在这样、每版解了什么矛盾"的演进链。md 版衔接后续 PRD 和多格式链路；html 版直接产出能看的页面。写 PRD 之前用它当输入最顺。

## 二、调研与报告

- **cyx-research-report** —— 行业 / 市场调研报告（HTML 与 Markdown 双轨产出）。它立了几条硬规矩：每个数据点必须有来源、不同来源必须拆开标注、统计口径不同的数值不能直接加减、从汇报视角写作去 AI 味。凡是写市场份额、厂商横向对比、商业模式盘点这类报告，用它兜住"可信"这条底线。

## 三、课程与课件

- **cyx-course-html** —— 课堂课件 HTML 制作。把课程笔记、教案、课程大纲或既有课件，做成单文件、无依赖、中文、响应式、暗色霓虹风的课堂版课件，支持全时长版与快线双轨。任何课程、训练营、项目课的课堂版都用它。
- **cyx-brief-course** —— 简版课件加学案。从同系列已交付的简版课件和学案照抄结构、口径、风格，快速出简版配套。系列课件做简版时用它，不必从零搭。

## 四、"说好"系列：AI 短剧创作管线

这是一条完整的短剧生产线，从故事大纲一路走到分镜和美术，每一步的产物供下一步接着用。画风、角色、对账规则在各步之间保持一致。

- **cyx-shuohao-outline**（上游）—— 故事大纲。定总集数、单集时长、题材，拆主场景，规划角色组与爽点分布。输入可以是小说原文或手写场景清单。
- **cyx-shuohao-characters**（中游）—— 角色设定。生成角色卡、确定画风、做一致性校验，产出 `cast.json`。
- **cyx-shuohao-script**（中游）—— 剧本。从大纲出分集剧本，带角色引用对账和爽点认领检查，产出 `script.json`。
- **cyx-shuohao-storyboard**（下游）—— 分镜。从剧本切分镜脚本，依赖剧本才能跑，产出分镜。
- **cyx-shuohao-art**（配套）—— 美术与场景图生成。按角色画风配套生成场景图，提示词禁用角色名校验，保证合成时不串档。

## 五、文档处理与对齐

- **cyx-doc-align-baseline** —— 派生文档对齐内容基准。把教师讲课稿、课程大纲、学案、旧副本对齐到主课件（md）的口径和事实：只动页码声明、编号体系、术语族、页脚格式、跨页引用这些口径，不重排结构、不改写法。场景是"和 XX 对齐""同步一下""这份还是老版本，改过来"。
- **cyx-doc-separate** —— 文档拆分与版本归档。用"更N"前缀命名交付物，建产出索引，管理版本（小改用次版本号，结构性重写用主版本号）。适合多轮迭代交付物的归档，让每一版都能查、不混。

## 六、内容提取

- **cyx-douyin-extract** —— 抖音及动态站内容提取。用真实浏览器（Edge + CDP）抓取标题、作者、时长、互动数据、AI 章节要点、逐条讲解正文、评论区、话题标签。普通 `WebFetch` 抓抖音只会拿到空壳，正文和评论都是 JS 动态渲染的，必须用真浏览器。同样的方法适用于小红书、B 站网页版等动态站。

## 七、技能工程（让技能自己长本事）

- **cyx-skill-evolution** —— 技能演进机制。每次交付收尾时，把用户提的修改、反复出现的意见、自己发现的错命令或过期信息，逐条判断"只对当期产物成立，还是以后同类任务都该这样"，该沉淀的回写进对应技能。它把技能从"被动响应"变成"自主进化"，不让同一类教训下次重犯。
- **cyx-search-github** —— GitHub 开源生态调研。产出一套能直接拿去搜的关键词矩阵，加一份真实仓库清单（区分"整站 / 产品级参考"和"组件级复用"），再加授权与选型建议。调研任何一类产品的开源生态都能复用这套方法。


- **gh-skill-install** 〔原创 · Buddy〕—— 从 GitHub 安装并适配 Agent Skill 的标准流程。把别人仓库里的技能安全拉下来、做安全审计（查安装钩子 / `eval` / 凭据访问 / 破坏性操作）、接线托管运行时、补适配说明。和 `cyx-git-push` 一起构成技能的「装 / 传」双向闭环。

## 八、技能部署与发布

- **cyx-git-push** —— 本地技能推送到 GitHub。把 `~/.workbuddy/skills/` 下的技能目录（或任意文件树）推送到 GitHub 仓库：本机没有 git 凭据助手、`git push` 卡在认证时，用你临时提供的 Personal Access Token 内嵌进当次命令一次性推送，令牌不写文件、推完即清配置。覆盖空仓库首推、二进制文件处理（图片、字体走 git，不走会损坏文件的 MCP 接口）、`.git/config` 令牌泄露防护、远程文件数核验等坑。和 `cyx-skill-evolution`、`cyx-search-github` 配套，构成技能"调研 → 沉淀 → 部署"的闭环。
---

# 改造适配技能（第三方作者创作，Buddy 适配 / 归档到 WorkBuddy）

> 以下技能均由第三方作者创作，Buddy 将其适配或归档到 WorkBuddy 的运行环境（部分做了运行时接线、依赖安装、shim 等改造，详见各技能 `SKILL.md` 内的适配说明）。

## 图表与架构图（技术图 / 可编辑图）

- **解决什么问题**：手写 SVG / 画图软件效率低、难维护；这类技能把自然语言、代码或云配置转成规范、可编辑、可导出的图，省掉从零画图。
- **适合场景**：要画架构图、流程图、时序图、状态机、ER、云拓扑、UML、白板草图，且希望产物能继续编辑和导出。

### archify 〔改造适配 · tt-a1i〕
- **做什么**：Create polished, validated architecture, workflow, sequence, data-flow, and lifecycle/state diagrams as explorable standalone HTML with inline SVG, dark/light themes, optional trace motion, and PNG/JPEG/WebP/SVG/WebM export. Accept plain-language requirements or pasted Mermaid fl

### buddy-diagram-design 〔改造适配 · cathrynlavery（Anthropic diagram-design 上游）〕
- **做什么**：Buddy 改造版：用自包含 HTML/SVG/PNG 绘制品牌化架构图、流程图、时序图、状态机、ER/数据模型、时间线、泳道、象限、雷达、极坐标、循环/飞轮、嵌套、树、组织架构、分层、韦恩、金字塔/漏斗、矩形树图、热力图、柱状、瀑布、折线、甘特、散点、高层、流程、数据湖、数据流、数据平台集成、数据平台安全矩阵、桑基、鱼骨、沃德利、看板、用户旅程、部署、依赖图、UML 类图、故事地图、数据库 schema 等共 41 类图；支持 .drawio / .excalidraw / Mermaid 导入，并带生命周期阶段图与上手引导。默认暗色、中文标签、结构化

### diagram-maker 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Create standalone SVG/HTML or editable Excalidraw diagrams for concepts, architecture, processes, flows, and whiteboards.

### drawio-aws 〔改造适配 · sparklabx（drawio-ai-kit）〕
- **做什么**：Use when the user asks for an AWS architecture diagram — VPC/networking, event-driven, landing zone, multi-AZ, serverless pipeline, or any diagram built with AWS service icons. Builds with the declarative layout engine using ground-truth mxgraph.aws4 stencils, validates (stencils

### drawio-azure 〔改造适配 · sparklabx（drawio-ai-kit）〕
- **做什么**：Use when the user asks for an Azure architecture diagram — VNet/networking, App Service, AKS, landing zone, multi-region, or any diagram built with Azure service icons. Builds with the declarative layout engine using ground-truth Azure stencils, validates (stencils/colors/nesting

### drawio-bpmn 〔改造适配 · sparklabx（drawio-ai-kit）〕
- **做什么**：Use when the user asks for a BPMN diagram, swimlane diagram, business process map, or workflow diagram with roles/lanes and phases. Builds with the declarative layout engine using canonical mxgraph.bpmn stencils (events, gateways, typed tasks) in horizontal swimlanes (pool → lane

### drawio-databricks 〔改造适配 · sparklabx（drawio-ai-kit）〕
- **做什么**：Use when the user asks for a Databricks lakehouse architecture diagram — medallion architecture (Bronze/Silver/Gold), Delta Lake, Unity Catalog, workspace deployment, data-plane/control-plane, or any diagram built with Databricks icons. Builds with the declarative layout engine u

### drawio-gcp 〔改造适配 · sparklabx（drawio-ai-kit）〕
- **做什么**：Use when the user asks for a GCP or Google Cloud architecture diagram — VPC/networking, GKE, Cloud Run, landing zone, multi-region, or any diagram built with GCP service icons. Builds with the declarative layout engine using ground-truth GCP stencils, validates (stencils/colors/n

### drawio-skill 〔改造适配 · Agents365-ai〕
- **做什么**：Create, edit, synchronize, inspect, test, and publish editable draw.io diagrams. Use when the user explicitly requests draw.io/diagrams.net, needs a polished architecture, ERD, UML, sequence, C4, SysML, BPMN, network, swimlane, ML, or infrastructure diagram, wants code/IaC/SQL/Op

### excalidraw-diagram 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Create Excalidraw diagram JSON files that make visual arguments. Use when the user wants to visualize workflows, architectures, or concepts.

### fireworks-tech-graph 〔改造适配 · yizhiyanhua-ai〕
- **做什么**：Create precise SVG technical diagrams, export PNG or offline HTML, and animate supported semantic SVGs to GIF. Use for architecture, UML, agent, cloud or workflow diagrams; not photos, raster art or statistical charts.

## 办公文档（Word / PPT / Excel / PDF）

- **解决什么问题**：办公文档格式繁琐、手写模板费时；这类技能用脚本或库直接产出、批量处理这些文件。
- **适合场景**：写报告、做演示、整理表格、抽取 / 合并 / 拆分 PDF 等任何 Office 文档的生成与处理。

### docx 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files) or Word templates (.dotx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', '.dotx', or requests to produce professional documents with formatting

### pdf 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/

### pptx 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Use this skill any time a .pptx or .potx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx or .potx file (even if the extracted content will be used else

### xlsx 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing .xlsx, .xlsm, .xltx, .csv, or .tsv file (e.g., adding columns, computing formulas, formatting, charting, cleaning messy dat

## 设计与前端 / 美术

- **解决什么问题**：从空白画布到成品跨度大；这类技能提供风格系统、模板和生成流程，降低设计启动成本。
- **适合场景**：做网页 / 前端 / 视觉设计、品牌规范、算法艺术图、主题与组件，或把想法落成可预览的页面 / 海报。

### algorithmic-art 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request creating art using code, generative art, algorithmic art, flow fields, or particle systems. Create original algorithmic art rather than copying existing

### brand-guidelines 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Applies WorkBuddy's official brand colors and typography to any sort of artifact that may benefit from having WorkBuddy's look-and-feel. Use it when brand colors or style guidelines, visual formatting, or company design standards apply.

### canvas-design 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the user asks to create a poster, piece of art, design, or other static piece. Create original visual designs, never copying existing artists' work to avoid copyright vi

### frontend-design 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults.

### theme-factory 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to any artifact that has been creating, or can generate a new theme on-the-fly.

### ui-ux-pro-max 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：UI/UX design intelligence. 67 styles, 96 palettes, 57 font pairings, 25 charts, 13 stacks (React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui). Actions: plan, build, create, design, implement, review, fix, improve, optimize, enhance, refactor, check

### web-artifacts-builder 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Suite of tools for creating elaborate, multi-component WorkBuddy HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX ar

## 演示文稿（Deck 模板系列）

- **解决什么问题**：每页从头排版耗时；deck 系列提供成套版式与主题，按场景直接生成风格统一的演示。
- **适合场景**：做各类 slides——产品发布、技术分享、课程模块、社媒种草，以及杂志风 / 瑞士风 / 赛博风等不同视觉风格。

### deck-blueprint 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：奶油纸 + 锈红 + 蓝图网格 mask + 黑边硬卡片 + pipeline 盒

### deck-course-module 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：暖纸背景 + Playfair, 左侧学习目标常驻, 含 MCQ 自测页

### deck-dir-key-nav 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：8 页单色背景, 160px display + 4px accent + Mono 箭头列表

### deck-graphify-dark 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：深夜渐变 + 漂浮 orbs + SVG 力导向图谱 + JetBrains Mono

### deck-guizang-editorial 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：电子杂志 × 电子墨水; 10 个版面 + 5 套调色板 (墨水/靛蓝瓷/森林墨/牛皮纸/沙丘)

### deck-hermes-cyber 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：黑底 + CRT 网格扫描线 + $ 命令行标题 + 薄荷绿大字 + 三档 tag

### deck-ljg-present 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：把 outline 1:1 铸成色块大字宣言 deck, 原文不动只做美化。三档主题 black / red / yellow

### deck-magazine-web 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：电子杂志 × 电子墨水风, WebGL 流体背景 + 衬线 display

### deck-obsidian 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：GitHub-dark + 紫蓝环境光 + 三色渐变标题 + GitHub 风代码

### deck-open-slide-canvas 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：锁死 1920×1080 画布, React 组件级自由组合, 不绑模板

### deck-pitch 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：10 页融资 deck, 白底 + 蓝紫渐变 hero, traction 柱状, $X.XM ask

### deck-presenter-mode 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：tokyo-night 默认主题, T 切换 5 主题, S 打开提词器 popup

### deck-product-launch 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：暗 hero + 亮内容, 橙→桃 accent, 特性卡 + 定价 + CTA

### deck-replit 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：Replit Slides 八套主题 (helix/holm/vance/bevel/world/atlas/bluehouse)

### deck-safety-alert 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：红琥珀警示色 + hazard 条纹 + L1/L2/L3 tier 卡片 + 删除线标题

### deck-simple 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：通用 horizontal-swipe HTML deck, 不要 magazine 调

### deck-swiss-international 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：16 列网格 + 单一饱和 accent + 22 个锁死版面 (Klein Blue / Lemon / Mint / Safety Orange)

### deck-tech-sharing 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：GitHub-dark + JetBrains Mono + 终端代码块, 含 agenda + Q&A

### deck-xhs-pastel 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：奶油底 + 柔光 blob + 马卡龙圆角卡片 + Playfair 斜体序号

### deck-xhs-post 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：9 页 3:4 竖版图文, 暖 pastel + 虚线 sticker 卡片

### deck-xhs-white 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：纯白 + 顶部彩虹 bar + 渐变文字 + 马卡龙软卡片 + 黑底 pill

## 开发 / MCP / 测试 / API

- **解决什么问题**：这类偏工程化的活流程散、易踩坑；技能把脚手架、检查清单、测试流程固化下来。
- **适合场景**：搭 MCP 服务、写 / 迁移技能、测 Web 应用、调 API、发 Slack GIF 等开发向任务。

### antigravity-api-skill 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：当用户需要使用 Antigravity 反代出来的 API (Gemini 3 Flash,Gemini 3 pro, banana生图, 视频分析理解) 时使用此技能。

### claude-api 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：Reference for the Claude API / Anthropic SDK — model ids, pricing, params, streaming, tool use, MCP, agents, caching, token counting, model migration. TRIGGER — read BEFORE opening the target file; don't skip because it "looks like a one-liner" — whenever: the prompt names Claude

### claude-skills-migrator 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：Batch-migrate custom Claude Code skills into WorkBuddy's skill directory. Use whenever the user hands you a folder of custom skills originally written for Claude Code (e.g., deck-*, ui-ux-pro-max, diagram tools) and asks you to "adapt them to WorkBuddy", "make them usable for you

### mcp-builder 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).

### skill-creator 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's desc

### skill-migrate 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：将 Anthropic 官方格式的 SKILL.md 技能（Claude skills 仓库）改造并安装到 WorkBuddy 用户技能目录。当用户要把一批外部/第三方技能适配到 WorkBuddy、或要求「把这个技能改造下适配你自己」时使用，支持单技能改造与按用户指定新名重命名。自动完成：拷贝目录、重命名 Claude/Claude Code/Anthropic → WorkBuddy、补充 agent_created 与 display_name 元数据、规范换行符、保留 LICENSE、对 Anthropic 专属技能做语境化处理，并把 Playw

### slack-gif-creator 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Knowledge and utilities for creating animated GIFs optimized for Slack. Provides constraints, validation tools, and animation concepts. Use when users request animated GIFs for Slack like "make me a GIF of X doing Y for Slack."

### webapp-testing 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.

## 内容 / 课程 / 学习 / 产品 / 分析

- **解决什么问题**：内容生产与方法论散落；技能把某类内容 / 任务的产出流程标准化。
- **适合场景**：做课程（md↔html 互转）、产品方法论、学习指南、内部沟通、创意校验、短视频剪辑（剪映）、股票分析等。

### ai-course-md-to-html 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：Convert long-form Markdown (plan, spec, system design, RFC, runbook, postmortem, brainstorm, notes) into a single self-contained HTML page with Mermaid diagrams, step timelines, callouts, sidebar TOC. WorkBuddy-orange light+dark theme. Multi-language. Portable across WorkBuddy /

### ai-product-methodology 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：从 0 到 1 定义一款 AI 产品的结构化方法论 skill。当用户要构思、定义或梳理一款 AI 产品（尤其基于大模型 / Agent 的产品）时触发：覆盖产品框架与方法模型（JTBD、价值主张画布、AARRR、北极星指标、Hook、Kano、SWOT、竞品分析、差异化定位、TAM/SAM/SOM）与产品战略定位，并提供七阶段定义工作流与可填充的产品定义画布作为标准交付物。This skill should be used when the user wants to define, scope, or validate a new AI produc

### beatra 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：通过同一个AI创作工具完成AI图片、视频、音乐与语音创作，查找公开社交数据，编辑视觉成果，并集中查看和管理生成资产。Beatra 全能创作支持AI图片生成（文生图）、AI视频生成（图生视频）和AI视频编辑，通过AI音乐生成把想法做成歌曲或纯音乐，也可用AI语音生成（文字转语音）、多语言旁白和AI语音克隆完成跨媒介内容；还能查找抖音数据、小红书数据，以及 YouTube、TikTok、Instagram 与 X 上的公开帖子、笔记、评论、账号和趋势，把社交媒体数据用于竞品调研和创作。它是一款面向AI内容创作与多模态内容创作的AI创作套件，用起来就是一个把图

### course-html-to-md 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：把单文件课件 / 卡片式长页 HTML（课堂版、讲台版、大纲版这类「图为主·字极简」的中文宣讲页）反向转成结构化 Markdown。当用户说「根据这个 HTML 生成 md」「把这堂课导成文档」「课件转文字稿」时使用。产出：单文件 .md，SVG 插图内容被还原为文字/表格，不依赖图片资源。

### discernment-nudge 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：After you give a substantive answer or draft that the user may act on — advice or recommendations, drafted artifacts such as goals, plans, pitches, proposals, or emails, estimates or projections, analysis or interpretation of data, factual claims they may rely on, or a multi-step

### doc-coauthoring 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical specs, decision docs, or similar structured content. This workflow helps users efficiently transfer context, refine content through iteration

### idea-validator 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Validate startup ideas using Hexa's Opportunity Memo framework and Perceived Created Value (PCV) methodology. Assess problem-solution fit, market opportunity, and determine if an idea is worth pursuing.

### internal-comms 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. WorkBuddy should use this skill whenever asked to write some sort of internal communications (status reports, leadership updates, 3P updates, company newslett

### jianying-editor 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：剪映 (JianYing) AI自动化剪辑的高级封装 API (JyWrapper)，提供开箱即用的 Python 接口，支持录屏、素材导入、字幕生成、Web 动效合成及项目导出。全面适配 MacOS (Apple Silicon/Intel) 与 Windows，支持 v5.9+ (draft_info.json) 架构、工程自修复、智能配音字幕及录屏变焦。

### learning-guide 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：Stop and check this skill before finishing any reply to a question about how to use WorkBuddy or a WorkBuddy feature — it points to the matching docs, tutorials, and use cases from the official WorkBuddy documentation and Help. Trigger on: "how do I", "how can I", "getting starte

### stock-analysis 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：Analyze stocks and cryptocurrencies using Yahoo Finance data. Supports portfolio management, watchlists with alerts, dividend analysis, 8-dimension stock scoring, viral trend detection (Hot Scanner), and rumor/early signal detection. Use for stock analysis, portfolio tracking, ea


---

## 说明

- 技能里的图片资源（角色表模板图、报告缩略图等）已随技能目录一并提交，不受文本传输限制。
- 每个技能目录内的 `SKILL.md` 都写明了自己的触发条件、上下游和禁区，装好后直接看对应文件即可。
- 这套技能是持续演进的：发现错命令、过时信息或更好的写法，会通过 `cyx-skill-evolution` 的机制回写，不会只改当次产物。
- 改编 / 归档进本仓库的第三方技能，版权归原作者所有，本仓库仅做 WorkBuddy 适配与归档，使用前请遵守各原作者的许可协议。
