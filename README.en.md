English | [中文](README.md)

# pm-agent Skills Pack (with third-party adapted skills)

Online bilingual version (中文 / English toggle buttons): https://pm-agent-skills.app.workbuddy.host/

This is a collection of custom skills for WorkBuddy (and tools compatible with the Anthropic Agent Skills spec). It comes in two parts:

1. **Original skills by the author** — the `cyx-` series (Lulu's battle-tested methodologies turned into skills) plus a few utility skills built by Buddy.
2. **Adapted third-party skills** — created by third-party authors and adapted into the WorkBuddy environment by the repo owner.

Each skill is a standalone folder containing a `SKILL.md` plus scripts, templates, or reference files. The skills are chained along product lines — the output of one feeds the next, and the README marks the upstream/downstream relationships.

Each skill entry states three things: **what it does / what problem it solves / when to use it**, and is tagged **attribution** [Original] or [Adapted · original author].

## How to install

Copy the skill folders you need into WorkBuddy's skills directory:

```
~/.workbuddy/skills/
```

Once in place, restart WorkBuddy or refresh the skills panel to load them. Using a subset is fine, but wherever an "upstream / downstream" dependency is marked, the downstream skill won't run without its upstream's output — install those together.

> Adapted skills that carry runtime dependencies (e.g. `archify` needs `npm install`, `drawio-*` needs the `drawio-ai` engine) — follow the adaptation notes in each `SKILL.md` and install the dependencies first.

---

## Original skills (built by Lulu / Buddy)

> All of the following are [Original · Lulu] — the `cyx-` series is Lulu's real-work methodologies turned into skills; `gh-skill-install` is [Original · Buddy] (skill installation/adaptation tool).

## 1. Requirements & product planning

This group solves one thing: you hold a pile of raw material — whitepapers, website screenshots, meeting notes, competitor refs, old proposals, ideas in your head — and need to converge it into a product document that can be reviewed, approved, and scheduled. The only difference is "how heavy".

- **cyx-summary-need** — Lightweight requirements doc (single-file HTML output). Use it when you have a product whitepaper, website, screenshots, or old proposals and need a presentable feature-requirements draft that opens in a browser and can be filled in later. Good for requirement briefs, feature lists, light pre-kickoff structuring.
- **cyx-ears-need** — Heavyweight PRD (EARS six-section format + dispatch-level granularity). Use it when ideas, meeting notes, competitor screenshots, and prototypes need to converge into an engineering-grade PRD (every requirement with acceptance criteria, decomposable to production dispatch granularity). Good for ten-chapter PRDs with review snapshots and review topics. It's the heavy tool — most cases should use something else.
- **cyx-priority-need** — Requirements prioritization (P0–P3 + RICE scoring). Use it when you have a batch of requirements to grade and rank for requirement review, version planning, or backlog ordering. Output is an ordered verdict of "decision + rationale + risks", not whole-product planning.
- **cyx-strcuture-need** — Product feature planning (four-layer architecture, module breakdown, priority matrix, MVP & roadmap, single-file HTML output). Use it to split a product into modules, define MVP scope and a roadmap, and take it to a kickoff review. Lighter than a PRD; no EARS engineering granularity required.
- **cyx-original-need-md / cyx-original-need-html** — Original-requirement and feature-evolution analysis (same methodology, two output formats). Reverse-engineer the original requirements behind an existing product and map the evolution chain of "why it became what it is, what tension each version resolved". The md version feeds into later PRD and multi-format pipelines; the html version produces a viewable page directly. Best used as PRD input.

## 2. Research & reports

- **cyx-research-report** — Industry / market research reports (HTML and Markdown dual-track output). It enforces hard rules: every data point must have a source, different sources must be labeled separately, numbers with different statistical calibers must not be added or compared directly, and writing is done from a briefing perspective with AI-flavor stripped out. For any report on market share, vendor comparison, or business-model surveys, use it to hold the "credible" baseline.

## 3. Courses & courseware

- **cyx-course-html** — Classroom courseware HTML. Turns course notes, lesson plans, syllabi, or existing courseware into a single-file, dependency-free, Chinese, responsive, dark-neon classroom deck, supporting full-duration and fast-track dual tracks. Use for the classroom version of any course, bootcamp, or project class.
- **cyx-brief-course** — Simplified courseware plus student worksheets. Copies the structure, calibers, and style from an already-delivered simplified deck and worksheet in the same series to quickly produce the simplified companion. Use when a course series needs a simplified version — no need to build from scratch.

## 4. The "Shuohao" series: AI short-drama production pipeline

A complete short-drama production line, from story outline through storyboard and art. Each step's output feeds the next; art style, characters, and reconciliation rules stay consistent across steps.

- **cyx-shuohao-outline** (upstream) — Story outline. Sets total episode count, per-episode duration, and genre; splits main scenes; plans character groups and hook distribution. Input can be novel text or a handwritten scene list.
- **cyx-shuohao-characters** (midstream) — Character design. Generates character cards, fixes the art style, runs consistency checks, and outputs `cast.json`.
- **cyx-shuohao-script** (midstream) — Screenplay. Produces per-episode scripts from the outline, with character-reference reconciliation and hook-claim checks, outputting `script.json`.
- **cyx-shuohao-storyboard** (downstream) — Storyboard. Splits the script into storyboard shots; requires the script to run.
- **cyx-shuohao-art** (companion) — Art and scene image generation. Generates scene images matching each character's style; prompt-level bans on character names keep compositing from cross-contaminating files.

## 5. Document processing & alignment

- **cyx-doc-align-baseline** — Align derived documents to a content baseline. Aligns teacher lecture notes, syllabi, worksheets, and old copies to the master courseware (md): touches only page-number declarations, numbering systems, terminology families, footer formats, and cross-page references — no restructuring, no rewriting. Scenarios: "align with X", "sync this up", "this one is stale, fix it".
- **cyx-doc-separate** — Document splitting and version archiving. Names deliverables with a "rev N" prefix, builds a deliverable index, and manages versions (minor changes get a minor version number; structural rewrites get a major one). Fits archiving multi-round iterative deliverables so every version is traceable and unmixed.

## 6. Content extraction

- **cyx-douyin-extract** — Douyin and dynamic-site content extraction. Uses a real browser (Edge + CDP) to capture titles, authors, duration, engagement stats, AI chapter summaries, full transcript, comments, and hashtags. A plain `WebFetch` on Douyin only gets an empty shell — body text and comments are JS-rendered and require a real browser. The same method applies to Xiaohongshu, Bilibili web, and other dynamic sites.

## 7. Skill engineering (making skills improve themselves)

- **cyx-skill-evolution** — Skill evolution mechanism. At every delivery wrap-up, triage each user correction, recurring comment, or discovered bad command / outdated info: does it hold only for this deliverable, or should all future tasks of this kind work this way? Anything that should persist gets written back into the corresponding skill. It turns skills from "passive responders" into "self-improving assets" so the same lesson isn't paid for twice.
- **cyx-search-github** — GitHub open-source ecosystem research. Produces a keyword matrix you can search with directly, a real repository list (separating "whole-site / product-level references" from "component-level reuse"), plus licensing and selection advice. Reusable for surveying the open-source ecosystem of any product category.

- **gh-skill-install** [Original · Buddy] — Standard procedure for installing and adapting an Agent Skill from GitHub. Safely pulls a skill from someone's repo, runs a security audit (install hooks / `eval` / credential access / destructive operations), wires up managed runtimes, and adds adaptation notes. Together with `cyx-git-push` it forms the two-way "install / publish" loop for skills.

## 8. Skill deployment & publishing

- **cyx-git-push** — Push local skills to GitHub. Pushes skill directories under `~/.workbuddy/skills/` (or any file tree) to a GitHub repository: when the machine has no git credential helper and `git push` hangs on auth, it embeds a temporarily provided Personal Access Token into that one command for a one-shot push — the token never touches a file and config is cleaned right after. Covers first push to an empty repo, binary handling (images and fonts go through git, not the MCP file API which corrupts them), `.git/config` token-leak protection, and remote file-count verification. Pairs with `cyx-skill-evolution` and `cyx-search-github` to complete the "research → distill → deploy" loop.

---

# Adapted third-party skills (created by third-party authors, adapted to WorkBuddy by the repo owner)

> All skills below were created by third-party authors and adapted into the WorkBuddy runtime environment by the repo owner (Lulu). Some received runtime wiring, dependency installation, shims, etc. — see each skill's `SKILL.md` for adaptation notes.

## Diagrams & architecture (technical / editable diagrams)

- **What problem it solves**: hand-writing SVG or drawing in diagram software is slow and hard to maintain; these skills turn natural language, code, or cloud config into well-formed, editable, exportable diagrams.
- **When to use**: architecture, flow, sequence, state-machine, ER, cloud topology, UML, whiteboard sketches — when you want the output to stay editable and exportable.

### archify [Adapted · tt-a1i]
- **What it does**: Create polished, validated architecture, workflow, sequence, data-flow, and lifecycle/state diagrams as explorable standalone HTML with inline SVG, dark/light themes, optional trace motion, and PNG/JPEG/WebP/SVG/WebM export. Accept plain-language requirements or pasted Mermaid fl

### buddy-diagram-design [Adapted · cathrynlavery (Anthropic diagram-design upstream)]
- **What it does**: Buddy-adapted edition: draws branded diagrams with self-contained HTML/SVG/PNG — 41 types including architecture, flow, sequence, state machine, ER/data model, timeline, swimlane, quadrant, radar, polar, loop/flywheel, nested, tree, org chart, layered, Venn, pyramid/funnel, treemap, heatmap, bars, waterfall, line, Gantt, scatter, high-level, process, data lake, data flow, data platform integration, data platform security matrix, sankey, fishbone, Wardley, kanban, user journey, deployment, dependency graph, UML class diagram, database schema, and more; supports .drawio / .excalidraw / Mermaid import, with lifecycle-stage diagrams and onboarding guides. Dark by default, Chinese labels, structured

### diagram-maker [Adapted · Anthropic (official agent-skills)]
- **What it does**: Create standalone SVG/HTML or editable Excalidraw diagrams for concepts, architecture, processes, flows, and whiteboards.

### drawio-aws [Adapted · sparklabx (drawio-ai-kit)]
- **What it does**: Use when the user asks for an AWS architecture diagram — VPC/networking, event-driven, landing zone, multi-AZ, serverless pipeline, or any diagram built with AWS service icons. Builds with the declarative layout engine using ground-truth mxgraph.aws4 stencils, validates (stencils

### drawio-azure [Adapted · sparklabx (drawio-ai-kit)]
- **What it does**: Use when the user asks for an Azure architecture diagram — VNet/networking, App Service, AKS, landing zone, multi-region, or any diagram built with Azure service icons. Builds with the declarative layout engine using ground-truth Azure stencils, validates (stencils/colors/nesting

### drawio-bpmn [Adapted · sparklabx (drawio-ai-kit)]
- **What it does**: Use when the user asks for a BPMN diagram, swimlane diagram, business process map, or workflow diagram with roles/lanes and phases. Builds with the declarative layout engine using canonical mxgraph.bpmn stencils (events, gateways, typed tasks) in horizontal swimlanes (pool → lane

### drawio-databricks [Adapted · sparklabx (drawio-ai-kit)]
- **What it does**: Use when the user asks for a Databricks lakehouse architecture diagram — medallion architecture (Bronze/Silver/Gold), Delta Lake, Unity Catalog, workspace deployment, data-plane/control-plane, or any diagram built with Databricks icons. Builds with the declarative layout engine u

### drawio-gcp [Adapted · sparklabx (drawio-ai-kit)]
- **What it does**: Use when the user asks for a GCP or Google Cloud architecture diagram — VPC/networking, GKE, Cloud Run, landing zone, multi-region, or any diagram built with GCP service icons. Builds with the declarative layout engine using ground-truth GCP stencils, validates (stencils/colors/n

### drawio-skill [Adapted · Agents365-ai]
- **What it does**: Create, edit, synchronize, inspect, test, and publish editable draw.io diagrams. Use when the user explicitly requests draw.io/diagrams.net, needs a polished architecture, ERD, UML, sequence, C4, SysML, BPMN, network, swimlane, ML, or infrastructure diagram, wants code/IaC/SQL/Op

### excalidraw-diagram [Adapted · Anthropic (official agent-skills)]
- **What it does**: Create Excalidraw diagram JSON files that make visual arguments. Use when the user wants to visualize workflows, architectures, or concepts.

### fireworks-tech-graph [Adapted · yizhiyanhua-ai]
- **What it does**: Create precise SVG technical diagrams, export PNG or offline HTML, and animate supported semantic SVGs to GIF. Use for architecture, UML, agent, cloud or workflow diagrams; not photos, raster art or statistical charts.

## Office documents (Word / PPT / Excel / PDF)

- **What problem it solves**: office file formats are fiddly and hand-made templates are slow; these skills generate and batch-process such files with scripts or libraries.
- **When to use**: writing reports, building decks, organizing spreadsheets, extracting / merging / splitting PDFs — any Office document generation or processing.

### docx [Adapted · Anthropic (official agent-skills)]
- **What it does**: Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files) or Word templates (.dotx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', '.dotx', or requests to produce professional documents with formatting

### pdf [Adapted · Anthropic (official agent-skills)]
- **What it does**: Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/

### pptx [Adapted · Anthropic (official agent-skills)]
- **What it does**: Use this skill any time a .pptx or .potx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx or .potx file (even if the extracted content will be used else

### xlsx [Adapted · Anthropic (official agent-skills)]
- **What it does**: Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing .xlsx, .xlsm, .xltx, .csv, or .tsv file (e.g., adding columns, computing formulas, formatting, charting, cleaning messy dat

## Design & frontend / art

- **What problem it solves**: the gap from blank canvas to finished product is wide; these skills provide style systems, templates, and generation flows that cut the startup cost of design.
- **When to use**: web / frontend / visual design, brand guidelines, algorithmic art, themes and components, or turning ideas into previewable pages / posters.

### algorithmic-art [Adapted · Anthropic (official agent-skills)]
- **What it does**: Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request creating art using code, generative art, algorithmic art, flow fields, or particle systems. Create original algorithmic art rather than copying existing

### brand-guidelines [Adapted · Anthropic (official agent-skills)]
- **What it does**: Applies WorkBuddy's official brand colors and typography to any sort of artifact that may benefit from having WorkBuddy's look-and-feel. Use it when brand colors or style guidelines, visual formatting, or company design standards apply.

### canvas-design [Adapted · Anthropic (official agent-skills)]
- **What it does**: Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the user asks to create a poster, piece of art, design, or other static piece. Create original visual designs, never copying existing artists' work to avoid copyright vi

### frontend-design [Adapted · Anthropic (official agent-skills)]
- **What it does**: Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults.

### theme-factory [Adapted · Anthropic (official agent-skills)]
- **What it does**: Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to any artifact that has been creating, or can generate a new theme on-the-fly.

### ui-ux-pro-max [Adapted · third party (original author declared inside the skill files)]
- **What it does**: UI/UX design intelligence. 67 styles, 96 palettes, 57 font pairings, 25 charts, 13 stacks (React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui). Actions: plan, build, create, design, implement, review, fix, improve, optimize, enhance, refactor, check

### web-artifacts-builder [Adapted · Anthropic (official agent-skills)]
- **What it does**: Suite of tools for creating elaborate, multi-component WorkBuddy HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX ar

## Presentations (Deck template series)

- **What problem it solves**: laying out every slide from scratch is slow; the deck series provides complete layout systems and themes to generate consistent presentations per scenario.
- **When to use**: all kinds of slides — product launches, tech talks, course modules, social-media posts, and magazine / Swiss / cyber visual styles.

### deck-blueprint [Adapted · third party (deck presentation template series)]
- **What it does**: Cream paper + rust red + blueprint grid mask + hard black-edged cards + pipeline boxes

### deck-course-module [Adapted · third party (deck presentation template series)]
- **What it does**: Warm paper background + Playfair, persistent learning objectives on the left, includes MCQ self-test pages

### deck-dir-key-nav [Adapted · third party (deck presentation template series)]
- **What it does**: 8 pages, monochrome background, 160px display type + 4px accent + monospace arrow lists

### deck-graphify-dark [Adapted · third party (deck presentation template series)]
- **What it does**: Late-night gradient + floating orbs + SVG force-directed graph + JetBrains Mono

### deck-guizang-editorial [Adapted · third party (deck presentation template series)]
- **What it does**: E-magazine × e-ink; 10 layouts + 5 palettes (ink / indigo porcelain / forest ink / kraft paper / dune)

### deck-hermes-cyber [Adapted · third party (deck presentation template series)]
- **What it does**: Black background + CRT grid scanlines + $ command-line titles + mint-green display type + three-tier tags

### deck-ljg-present [Adapted · third party (deck presentation template series)]
- **What it does**: Casts an outline 1:1 into a big-type manifesto deck of color blocks — text untouched, only beautified. Three themes: black / red / yellow

### deck-magazine-web [Adapted · third party (deck presentation template series)]
- **What it does**: E-magazine × e-ink style, WebGL fluid background + serif display type

### deck-obsidian [Adapted · third party (deck presentation template series)]
- **What it does**: GitHub-dark + purple-blue ambient light + three-color gradient titles + GitHub-style code blocks

### deck-open-slide-canvas [Adapted · third party (deck presentation template series)]
- **What it does**: Locked 1920×1080 canvas, free React component composition, not bound to templates

### deck-pitch [Adapted · third party (deck presentation template series)]
- **What it does**: 10-page fundraising deck, white background + blue-purple gradient hero, traction bars, $X.XM ask

### deck-presenter-mode [Adapted · third party (deck presentation template series)]
- **What it does**: tokyo-night default theme, T toggles 5 themes, S opens a teleprompter popup

### deck-product-launch [Adapted · third party (deck presentation template series)]
- **What it does**: Dark hero + light content, orange→peach accent, feature cards + pricing + CTA

### deck-replit [Adapted · third party (deck presentation template series)]
- **What it does**: Replit Slides' eight themes (helix/holm/vance/bevel/world/atlas/bluehouse)

### deck-safety-alert [Adapted · third party (deck presentation template series)]
- **What it does**: Red-amber warning colors + hazard stripes + L1/L2/L3 tier cards + strikethrough titles

### deck-simple [Adapted · third party (deck presentation template series)]
- **What it does**: Generic horizontal-swipe HTML deck, without the magazine flavor

### deck-swiss-international [Adapted · third party (deck presentation template series)]
- **What it does**: 16-column grid + single saturated accent + 22 locked layouts (Klein Blue / Lemon / Mint / Safety Orange)

### deck-tech-sharing [Adapted · third party (deck presentation template series)]
- **What it does**: GitHub-dark + JetBrains Mono + terminal code blocks, includes agenda + Q&A

### deck-xhs-pastel [Adapted · third party (deck presentation template series)]
- **What it does**: Cream base + soft-glow blobs + macaron rounded cards + Playfair italic numbering

### deck-xhs-post [Adapted · third party (deck presentation template series)]
- **What it does**: 9-page 3:4 portrait image-text layout, warm pastel + dashed sticker cards

### deck-xhs-white [Adapted · third party (deck presentation template series)]
- **What it does**: Pure white + top rainbow bar + gradient text + macaron soft cards + black pill badges

## Development / MCP / testing / API

- **What problem it solves**: these engineering-flavored jobs have scattered workflows and many pitfalls; the skills codify scaffolding, checklists, and test procedures.
- **When to use**: building MCP servers, writing / migrating skills, testing web apps, calling APIs, making Slack GIFs, and other dev-oriented tasks.

### antigravity-api-skill [Adapted · third party (original author declared inside the skill files)]
- **What it does**: 当用户需要使用 Antigravity 反代出来的 API (Gemini 3 Flash,Gemini 3 pro, banana生图, 视频分析理解) 时使用此技能。

### claude-api [Adapted · third party (original author declared inside the skill files)]
- **What it does**: Reference for the Claude API / Anthropic SDK — model ids, pricing, params, streaming, tool use, MCP, agents, caching, token counting, model migration. TRIGGER — read BEFORE opening the target file; don't skip because it "looks like a one-liner" — whenever: the prompt names Claude

### claude-skills-migrator [Adapted · third party (original author declared inside the skill files)]
- **What it does**: Batch-migrate custom Claude Code skills into WorkBuddy's skill directory. Use whenever the user hands you a folder of custom skills originally written for Claude Code (e.g., deck-*, ui-ux-pro-max, diagram tools) and asks you to "adapt them to WorkBuddy", "make them usable for you

### mcp-builder [Adapted · Anthropic (official agent-skills)]
- **What it does**: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).

### skill-creator [Adapted · Anthropic (official agent-skills)]
- **What it does**: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's desc

### skill-migrate [Adapted · third party (original author declared inside the skill files)]
- **What it does**: 将 Anthropic 官方格式的 SKILL.md 技能（Claude skills 仓库）改造并安装到 WorkBuddy 用户技能目录。当用户要把一批外部/第三方技能适配到 WorkBuddy、或要求「把这个技能改造下适配你自己」时使用，支持单技能改造与按用户指定新名重命名。自动完成：拷贝目录、重命名 Claude/Claude Code/Anthropic → WorkBuddy、补充 agent_created 与 display_name 元数据、规范换行符、保留 LICENSE、对 Anthropic 专属技能做语境化处理，并把 Playw

### slack-gif-creator [Adapted · Anthropic (official agent-skills)]
- **What it does**: Knowledge and utilities for creating animated GIFs optimized for Slack. Provides constraints, validation tools, and animation concepts. Use when users request animated GIFs for Slack like "make me a GIF of X doing Y for Slack."

### webapp-testing [Adapted · Anthropic (official agent-skills)]
- **What it does**: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.

## Content / courses / learning / product / analysis

- **What problem it solves**: content production know-how and methodologies are scattered; these skills standardize the output process for a class of content / tasks.
- **When to use**: courses (md↔html conversion), product methodology, learning guides, internal comms, idea validation, short-video editing (JianYing), stock analysis, and more.

### ai-course-md-to-html [Adapted · third party (original author declared inside the skill files)]
- **What it does**: Convert long-form Markdown (plan, spec, system design, RFC, runbook, postmortem, brainstorm, notes) into a single self-contained HTML page with Mermaid diagrams, step timelines, callouts, sidebar TOC. WorkBuddy-orange light+dark theme. Multi-language. Portable across WorkBuddy /

### ai-product-methodology [Adapted · third party (original author declared inside the skill files)]
- **What it does**: 从 0 到 1 定义一款 AI 产品的结构化方法论 skill。当用户要构思、定义或梳理一款 AI 产品（尤其基于大模型 / Agent 的产品）时触发：覆盖产品框架与方法模型（JTBD、价值主张画布、AARRR、北极星指标、Hook、Kano、SWOT、竞品分析、差异化定位、TAM/SAM/SOM）与产品战略定位，并提供七阶段定义工作流与可填充的产品定义画布作为标准交付物。This skill should be used when the user wants to define, scope, or validate a new AI produc

### beatra [Adapted · third party (original author declared inside the skill files)]
- **What it does**: 通过同一个AI创作工具完成AI图片、视频、音乐与语音创作，查找公开社交数据，编辑视觉成果，并集中查看和管理生成资产。Beatra 全能创作支持AI图片生成（文生图）、AI视频生成（图生视频）和AI视频编辑，通过AI音乐生成把想法做成歌曲或纯音乐，也可用AI语音生成（文字转语音）、多语言旁白和AI语音克隆完成跨媒介内容；还能查找抖音数据、小红书数据，以及 YouTube、TikTok、Instagram 与 X 上的公开帖子、笔记、评论、账号和趋势，把社交媒体数据用于竞品调研和创作。它是一款面向AI内容创作与多模态内容创作的AI创作套件，用起来就是一个把图

### course-html-to-md [Adapted · third party (original author declared inside the skill files)]
- **What it does**: 把单文件课件 / 卡片式长页 HTML（课堂版、讲台版、大纲版这类「图为主·字极简」的中文宣讲页）反向转成结构化 Markdown。当用户说「根据这个 HTML 生成 md」「把这堂课导成文档」「课件转文字稿」时使用。产出：单文件 .md，SVG 插图内容被还原为文字/表格，不依赖图片资源。

### discernment-nudge [Adapted · Anthropic (official agent-skills)]
- **What it does**: After you give a substantive answer or draft that the user may act on — advice or recommendations, drafted artifacts such as goals, plans, pitches, proposals, or emails, estimates or projections, analysis or interpretation of data, factual claims they may rely on, or a multi-step

### doc-coauthoring [Adapted · Anthropic (official agent-skills)]
- **What it does**: Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical specs, decision docs, or similar structured content. This workflow helps users efficiently transfer context, refine content through iteration

### idea-validator [Adapted · Anthropic (official agent-skills)]
- **What it does**: Validate startup ideas using Hexa's Opportunity Memo framework and Perceived Created Value (PCV) methodology. Assess problem-solution fit, market opportunity, and determine if an idea is worth pursuing.

### internal-comms [Adapted · Anthropic (official agent-skills)]
- **What it does**: A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. WorkBuddy should use this skill whenever asked to write some sort of internal communications (status reports, leadership updates, 3P updates, company newslett

### jianying-editor [Adapted · third party (original author declared inside the skill files)]
- **What it does**: 剪映 (JianYing) AI自动化剪辑的高级封装 API (JyWrapper)，提供开箱即用的 Python 接口，支持录屏、素材导入、字幕生成、Web 动效合成及项目导出。全面适配 MacOS (Apple Silicon/Intel) 与 Windows，支持 v5.9+ (draft_info.json) 架构、工程自修复、智能配音字幕及录屏变焦。

### learning-guide [Adapted · Anthropic (official agent-skills)]
- **What it does**: Stop and check this skill before finishing any reply to a question about how to use WorkBuddy or a WorkBuddy feature — it points to the matching docs, tutorials, and use cases from the official WorkBuddy documentation and Help. Trigger on: "how do I", "how can I", "getting starte

### stock-analysis [Adapted · third party (original author declared inside the skill files)]
- **What it does**: Analyze stocks and cryptocurrencies using Yahoo Finance data. Supports portfolio management, watchlists with alerts, dividend analysis, 8-dimension stock scoring, viral trend detection (Hot Scanner), and rumor/early signal detection. Use for stock analysis, portfolio tracking, ea

---

## Notes

- Image resources inside skills (character-sheet templates, report thumbnails, etc.) are committed along with their skill folders and are not limited by text-based transfer.
- Every skill folder's `SKILL.md` states its own trigger conditions, upstream/downstream relations, and boundaries — read the corresponding file once installed.
- This pack evolves continuously: bad commands, outdated info, or better approaches found along the way are written back through the `cyx-skill-evolution` mechanism — not just patched into the deliverable of the moment.
- Third-party skills adapted / archived into this repository remain the property of their original authors. This repo only adapts and archives them for WorkBuddy; please respect each original author's license before use.

---

## Support

If these skills helped you, you're welcome to buy the author a coffee. Scan with Alipay:

<p align="center">
  <img src="assets/alipay-qr.jpg" alt="Alipay" width="240">
</p>

Every bit of support fuels keeping these skills organized, adapted, and updated. Thank you.
