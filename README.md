[English](README.en.md) | [中文](README.md)

# pm-agent技能包（含第三方改造适配技能）

在线双语版（中文 / English 按钮切换）：https://pm-agent-skills.app.workbuddy.host/

这是一套面向 WorkBuddy（以及兼容 Anthropic Agent Skills 规范的工具）的自定义技能集合。它分成两大部分：

1. **作者原创技能**——`cyx-` 系列（Lulu 把实际工作里反复打磨的方法论沉淀成技能）+ 少量 Buddy 自建的工具技能。
2. **改造适配技能**——由第三方作者创作，仓库作者将其适配到 WorkBuddy 环境。

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

# 改造适配技能（第三方作者创作，仓库作者适配到 WorkBuddy）

> 以下技能均由第三方作者创作，由仓库作者（Lulu）自行适配到 WorkBuddy 的运行环境（部分做了运行时接线、依赖安装、shim 等改造，详见各技能 `SKILL.md` 内的适配说明）。

## 图表与架构图（技术图 / 可编辑图）

- **解决什么问题**：手写 SVG / 画图软件效率低、难维护；这类技能把自然语言、代码或云配置转成规范、可编辑、可导出的图，省掉从零画图。
- **适合场景**：要画架构图、流程图、时序图、状态机、ER、云拓扑、UML、白板草图，且希望产物能继续编辑和导出。

### archify 〔改造适配 · tt-a1i〕
- **做什么**：把自然语言或粘贴的 Mermaid 代码，转成可交互的独立 HTML 图（内联 SVG）。覆盖架构图、流程图、时序图、数据流图、生命周期/状态图；内置深色/浅色双主题、可选轨迹动画，可导出 PNG/JPEG/WebP/SVG/WebM。

### buddy-diagram-design 〔改造适配 · cathrynlavery（Anthropic diagram-design 上游）〕
- **做什么**：Buddy 改造版：用自包含 HTML/SVG/PNG 绘制品牌化架构图、流程图、时序图、状态机、ER/数据模型、时间线、泳道、象限、雷达、极坐标、循环/飞轮、嵌套、树、组织架构、分层、韦恩、金字塔/漏斗、矩形树图、热力图、柱状、瀑布、折线、甘特、散点、高层、流程、数据湖、数据流、数据平台集成、数据平台安全矩阵、桑基、鱼骨、沃德利、看板、用户旅程、部署、依赖图、UML 类图、故事地图、数据库 schema 等共 41 类图；支持 .drawio / .excalidraw / Mermaid 导入，并带生命周期阶段图与上手引导。默认暗色、中文标签、结构化。

### diagram-maker 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：为概念、架构、流程、流转和头脑风暴白板，生成独立的 SVG/HTML 图，或可导出的 Excalidraw 可编辑图。

### drawio-aws 〔改造适配 · sparklabx（drawio-ai-kit）〕
- **做什么**：用户要画 AWS 架构图（VPC/网络、事件驱动、落地区、多可用区、无服务器流水线，或任何用 AWS 图标画的图）时用。基于声明式布局引擎，调用 mxgraph.aws4 真实模板生成，并做模板校验。

### drawio-azure 〔改造适配 · sparklabx（drawio-ai-kit）〕
- **做什么**：用户要画 Azure 架构图（虚拟网络/网络、应用服务、AKS、落地区、多区域，或任何用 Azure 图标画的图）时用。基于声明式布局引擎，调用 Azure 真实模板生成，并做模板/颜色/嵌套校验。

### drawio-bpmn 〔改造适配 · sparklabx（drawio-ai-kit）〕
- **做什么**：用户要画 BPMN 图、泳道图、业务流程图，或带角色/泳道/阶段的流程图时用。基于声明式布局引擎，用标准 mxgraph.bpmn 模板（事件、网关、定型任务）生成，呈横向泳道（池 → 道）。

### drawio-databricks 〔改造适配 · sparklabx（drawio-ai-kit）〕
- **做什么**：用户要画 Databricks 湖仓架构图（分层架构 Bronze/Silver/Gold、Delta Lake、Unity Catalog、工作区部署、数据面/控制面，或任何用 Databricks 图标画的图）时用。基于声明式布局引擎生成。

### drawio-gcp 〔改造适配 · sparklabx（drawio-ai-kit）〕
- **做什么**：用户要画 GCP / 谷歌云架构图（VPC/网络、GKE、Cloud Run、落地区、多区域，或任何用 GCP 图标画的图）时用。基于声明式布局引擎，调用 GCP 真实模板生成，并做模板/颜色/嵌套校验。

### drawio-skill 〔改造适配 · Agents365-ai〕
- **做什么**：创建、编辑、同步、检查、测试、发布可编辑的 draw.io 图。用户明确要 draw.io/diagrams.net，或要一套精致的架构图、ER 图、UML、时序图、C4、SysML、BPMN、网络图、泳道图、机器学习图或基础设施图时用；也支持从代码/IaC/SQL/OpenAPI 反向生成。

### excalidraw-diagram 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：生成 Excalidraw 的 JSON 图文件，用草图风格把观点可视化。用户想把工作流、架构或概念画成图时用。

### fireworks-tech-graph 〔改造适配 · yizhiyanhua-ai〕
- **做什么**：生成精确的 SVG 技术图，可导出 PNG 或离线 HTML，并把支持语义的 SVG 动画转成 GIF。用于架构图、UML、智能体图、云图或工作流图；不用于照片、位图艺术或统计图表。

## 办公文档（Word / PPT / Excel / PDF）

- **解决什么问题**：办公文档格式繁琐、手写模板费时；这类技能用脚本或库直接产出、批量处理这些文件。
- **适合场景**：写报告、做演示、整理表格、抽取 / 合并 / 拆分 PDF 等任何 Office 文档的生成与处理。

### docx 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：用户要创建、读取、编辑或处理 Word 文档（.docx）或 Word 模板（.dotx）时用。凡是提到"Word 文档""文档""docx""dotx"，或要产出带格式的专业文档，都触发它。

### pdf 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：用户要对 PDF 做任何操作时用。包括从 PDF 读/抽取文字与表格、多份 PDF 合并、拆分、旋转页面、加/去水印、新建 PDF、填表、加密等。

### pptx 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：凡涉及 .pptx 或 .potx 文件（作为输入、输出或两者）时都用。包括做幻灯片、融资 deck、演示文稿；读取、解析、抽取任意 .pptx/.potx 的文字（哪怕抽取内容会另作他用）。

### xlsx 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：凡以表格文件为主要输入或输出时都用。即用户要打开、读取、编辑或修复已有的 .xlsx/.xlsm/.xltx/.csv/.tsv（如加列、算公式、排版、画图、清洗脏数据）。

## 设计与前端 / 美术

- **解决什么问题**：从空白画布到成品跨度大；这类技能提供风格系统、模板和生成流程，降低设计启动成本。
- **适合场景**：做网页 / 前端 / 视觉设计、品牌规范、算法艺术图、主题与组件，或把想法落成可预览的页面 / 海报。

### algorithmic-art 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：用 p5.js 加随机种子和交互式参数探索做算法艺术。用户要求用代码创作、生成艺术、算法艺术、流场或粒子系统时用。做原创算法艺术，而非照搬现有作品。

### brand-guidelines 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：把 WorkBuddy 官方品牌色与字体，套用到任何需要统一观感的产物上。当涉及品牌色/风格规范、视觉排版或公司设计标准时用。

### canvas-design 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：用设计理念在 .png 和 .pdf 里创作精美的视觉作品。用户要海报、画作、设计稿或其他静态视觉件时用。做原创设计，绝不照搬他人作品以免侵权。

### frontend-design 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：新建或重塑 UI 时，提供独特、有意为之的视觉设计指引。在美学方向、字体排版，以及避免"模板默认感"的选择上给帮助。

### theme-factory 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：给产物套主题样式的工具箱。产物可以是幻灯片、文档、报告、HTML 落地页等。内置 10 套带配色/字体的预设主题，可套到任意已生成的产物上，也能即时生成新主题。

### ui-ux-pro-max 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：UI/UX 设计智能。内置 67 种风格、96 套配色、57 组字体搭配、25 类图表、13 种技术栈（React、Next.js、Vue、Svelte、SwiftUI、React Native、Flutter、Tailwind、shadcn/ui）。动作涵盖规划、构建、创建、设计、实现、评审、修复、改进、优化、增强、重构、检查等。

### web-artifacts-builder 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：一套用现代前端技术（React、Tailwind CSS、shadcn/ui）制作复杂、多组件 WorkBuddy HTML 产物的工具。用于需要状态管理、路由或 shadcn/ui 组件的复杂产物——不适用于简单单文件 HTML/JSX。

## 演示文稿（Deck 模板系列）

- **解决什么问题**：每页从头排版耗时；deck 系列提供成套版式与主题，按场景直接生成风格统一的演示。
- **适合场景**：做各类 slides——产品发布、技术分享、课程模块、社媒种草，以及杂志风 / 瑞士风 / 赛博风等不同视觉风格。

### deck-blueprint 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：奶油纸 + 锈红 + 蓝图网格 mask + 黑边硬卡片 + pipeline 盒

### deck-course-module 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：暖纸背景 + Playfair，左侧学习目标常驻，含 MCQ 自测页

### deck-dir-key-nav 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：8 页单色背景，160px display + 4px accent + Mono 箭头列表

### deck-graphify-dark 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：深夜渐变 + 漂浮 orbs + SVG 力导向图谱 + JetBrains Mono

### deck-guizang-editorial 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：电子杂志 × 电子墨水；10 个版面 + 5 套调色板（墨水/靛蓝瓷/森林墨/牛皮纸/沙丘）

### deck-hermes-cyber 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：黑底 + CRT 网格扫描线 + $ 命令行标题 + 薄荷绿大字 + 三档 tag

### deck-ljg-present 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：把 outline 1:1 铸成色块大字宣言 deck，原文不动只做美化。三档主题 black / red / yellow

### deck-magazine-web 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：电子杂志 × 电子墨水风，WebGL 流体背景 + 衬线 display

### deck-obsidian 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：GitHub-dark + 紫蓝环境光 + 三色渐变标题 + GitHub 风代码

### deck-open-slide-canvas 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：锁死 1920×1080 画布，React 组件级自由组合，不绑模板

### deck-pitch 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：10 页融资 deck，白底 + 蓝紫渐变 hero，traction 柱状，$X.XM ask

### deck-presenter-mode 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：tokyo-night 默认主题，T 切换 5 主题，S 打开提词器 popup

### deck-product-launch 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：暗 hero + 亮内容，橙→桃 accent，特性卡 + 定价 + CTA

### deck-replit 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：Replit Slides 八套主题（helix/holm/vance/bevel/world/atlas/bluehouse）

### deck-safety-alert 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：红琥珀警示色 + hazard 条纹 + L1/L2/L3 tier 卡片 + 删除线标题

### deck-simple 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：通用 horizontal-swipe HTML deck，不要 magazine 调

### deck-swiss-international 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：16 列网格 + 单一饱和 accent + 22 个锁死版面（Klein Blue / Lemon / Mint / Safety Orange）

### deck-tech-sharing 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：GitHub-dark + JetBrains Mono + 终端代码块，含 agenda + Q&A

### deck-xhs-pastel 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：奶油底 + 柔光 blob + 马卡龙圆角卡片 + Playfair 斜体序号

### deck-xhs-post 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：9 页 3:4 竖版图文，暖 pastel + 虚线 sticker 卡片

### deck-xhs-white 〔改造适配 · 第三方（deck 演示模板系列）〕
- **做什么**：纯白 + 顶部彩虹 bar + 渐变文字 + 马卡龙软卡片 + 黑底 pill

## 开发 / MCP / 测试 / API

- **解决什么问题**：这类偏工程化的活流程散、易踩坑；技能把脚手架、检查清单、测试流程固化下来。
- **适合场景**：搭 MCP 服务、写 / 迁移技能、测 Web 应用、调 API、发 Slack GIF 等开发向任务。

### antigravity-api-skill 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：当用户需要使用 Antigravity 反代出来的 API（Gemini 3 Flash、Gemini 3 pro、banana 生图、视频分析理解）时使用此技能。

### claude-api 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：Claude API / Anthropic SDK 的参考手册——模型 ID、定价、参数、流式、工具调用、MCP、智能体、缓存、令牌计数、模型迁移。凡是提示里提到 Claude，都要在打开目标文件之前先读它，别因为它"看着像一行命令"就跳过。

### claude-skills-migrator 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：把为 Claude Code 写的自定义技能批量迁移进 WorkBuddy 技能目录。凡是用户交来一批原本为 Claude Code 写的技能（如 deck-*、ui-ux-pro-max、图表工具），要求"适配到 WorkBuddy""让它们能为你所用"时用。

### mcp-builder 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：创建高质量 MCP（模型上下文协议）服务器的指引，让 LLM 通过设计良好的工具对接外部服务。要搭 MCP 服务器来接入外部 API 或服务时用，无论是 Python（FastMCP）还是 Node/TypeScript（MCP SDK）。

### skill-creator 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：新建技能、修改并改进已有技能，并测算技能表现。用户要从零建技能、编辑或优化已有技能、跑评测检验技能、用方差分析给技能表现做基准，或优化技能描述时用。

### skill-migrate 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：将 Anthropic 官方格式的 SKILL.md 技能（Claude skills 仓库）改造并安装到 WorkBuddy 用户技能目录。当用户要把一批外部/第三方技能适配到 WorkBuddy、或要求「把这个技能改造下适配你自己」时使用，支持单技能改造与按用户指定新名重命名。自动完成：拷贝目录、重命名 Claude/Claude Code/Anthropic → WorkBuddy、补充 agent_created 与 display_name 元数据、规范换行符、保留 LICENSE、对 Anthropic 专属技能做语境化处理，并把 Playwright 等依赖接线到位。

### slack-gif-creator 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：制作 Slack 专用动图（GIF）的知识与工具。提供约束条件、校验工具和动画思路。用户要做 Slack 动图（"给我做个 X 在 Slack 里做 Y 的 GIF"）时用。

### webapp-testing 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：用 Playwright 与本地 Web 应用交互并测试的 toolkit。支持验证前端功能、调试 UI 行为、抓取浏览器截图、查看浏览器日志。

## 内容 / 课程 / 学习 / 产品 / 分析

- **解决什么问题**：内容生产与方法论散落；技能把某类内容 / 任务的产出流程标准化。
- **适合场景**：做课程（md↔html 互转）、产品方法论、学习指南、内部沟通、创意校验、短视频剪辑（剪映）、股票分析等。

### ai-course-md-to-html 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：把长篇 Markdown（计划、规格、系统设计、RFC、运维手册、复盘、头脑风暴、笔记）转成单个自包含 HTML 页，带 Mermaid 图、步骤时间线、提示块和侧栏目录。WorkBuddy 橙色深/浅主题，多语言，可在 WorkBuddy 间移植。

### ai-product-methodology 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：从 0 到 1 定义一款 AI 产品的结构化方法论技能。当用户要构思、定义或梳理一款 AI 产品（尤其基于大模型 / Agent 的产品）时触发：覆盖产品框架与方法模型（JTBD、价值主张画布、AARRR、北极星指标、Hook、Kano、SWOT、竞品分析、差异化定位、TAM/SAM/SOM）与产品战略定位，并提供七阶段定义工作流与可填充的产品定义画布作为标准交付物。当用户想要定义、划定范围或验证一款新 AI 产品（尤其基于大模型 / Agent 的产品）时使用。

### beatra 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：通过同一个 AI 创作工具完成 AI 图片、视频、音乐与语音创作，查找公开社交数据，编辑视觉成果，并集中查看和管理生成资产。Beatra 全能创作支持 AI 图片生成（文生图）、AI 视频生成（图生视频）和 AI 视频编辑，通过 AI 音乐生成把想法做成歌曲或纯音乐，也可用 AI 语音生成（文字转语音）、多语言旁白和 AI 语音克隆完成跨媒介内容；还能查找抖音数据、小红书数据，以及 YouTube、TikTok、Instagram 与 X 上的公开帖子、笔记、评论、账号和趋势，把社交媒体数据用于竞品调研和创作。它是一款面向 AI 内容创作与多模态内容创作的 AI 创作套件。

### course-html-to-md 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：把单文件课件 / 卡片式长页 HTML（课堂版、讲台版、大纲版这类「图为主·字极简」的中文宣讲页）反向转成结构化 Markdown。当用户说「根据这个 HTML 生成 md」「把这堂课导成文档」「课件转文字稿」时使用。产出：单文件 .md，SVG 插图内容被还原为文字/表格，不依赖图片资源。

### discernment-nudge 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：在你给出用户可能据此行动的答案或草稿后——建议或推荐、目标/计划/提案/邮件等草稿、估算或预测、数据分析或解读、用户可能采信的事实判断，或多步任务——给出提示，让用户再审视一下再行动。

### doc-coauthoring 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：引导用户走一套结构化的协作写文档流程。用户要写文档、提案、技术规格、决策文档或类似结构化内容时用。该流程帮用户高效传递上下文、通过迭代打磨内容。

### idea-validator 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：用 Hexa 的机会备忘录框架和感知创造价值（PCV）方法论验证创业点子。评估问题-方案匹配度、市场机会，判断一个点子是否值得做。

### internal-comms 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：一套帮用户写各类内部沟通件的资源，采用公司惯用的格式。凡被要求写内部沟通（状态报告、管理层更新、3P 更新、公司简报）时用。

### jianying-editor 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：剪映（JianYing）AI 自动化剪辑的高级封装 API（JyWrapper），提供开箱即用的 Python 接口，支持录屏、素材导入、字幕生成、Web 动效合成及项目导出。全面适配 MacOS（Apple Silicon/Intel）与 Windows，支持 v5.9+（draft_info.json）架构、工程自修复、智能配音字幕及录屏变焦。

### learning-guide 〔改造适配 · Anthropic（官方 agent-skills）〕
- **做什么**：在回答任何"怎么用 WorkBuddy 或某个功能"的问题、给出最终回复前，先停一下查这个技能——它指向官方文档与帮助里的对应文档、教程和用例。触发词："怎么用""如何开始"等。

### stock-analysis 〔改造适配 · 第三方（原作者见技能文件内声明）〕
- **做什么**：用雅虎财经数据做股票和加密货币分析。支持投资组合管理、带提醒的观察清单、分红分析、八维股票打分、病毒式趋势探测（热门扫描器）和传闻/早期信号探测。用于股票分析、组合跟踪等。


---

## 说明

- 技能里的图片资源（角色表模板图、报告缩略图等）已随技能目录一并提交，不受文本传输限制。
- 每个技能目录内的 `SKILL.md` 都写明了自己的触发条件、上下游和禁区，装好后直接看对应文件即可。
- 这套技能是持续演进的：发现错命令、过时信息或更好的写法，会通过 `cyx-skill-evolution` 的机制回写，不会只改当次产物。
- 改编 / 归档进本仓库的第三方技能，版权归原作者所有，本仓库仅做 WorkBuddy 适配与归档，使用前请遵守各原作者的许可协议。

---

## 感谢支持

如果这套技能帮到了你，欢迎请作者喝杯咖啡。打开支付宝扫一扫：

<p align="center">
  <img src="assets/alipay-qr.jpg" alt="支付宝收款码" width="240">
</p>

每一份支持都是持续整理、适配和更新这些技能的动力，谢谢。
