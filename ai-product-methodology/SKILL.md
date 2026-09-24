---
name: ai-product-methodology
description: 从 0 到 1 定义一款 AI 产品的结构化方法论 skill。当用户要构思、定义或梳理一款 AI 产品（尤其基于大模型 / Agent 的产品）时触发：覆盖产品框架与方法模型（JTBD、价值主张画布、AARRR、北极星指标、Hook、Kano、SWOT、竞品分析、差异化定位、TAM/SAM/SOM）与产品战略定位，并提供七阶段定义工作流与可填充的产品定义画布作为标准交付物。This skill should be used when the user wants to define, scope, or validate a new AI product from scratch, choose the right product framework, or produce a product definition canvas / one-pager.
agent_created: true
---

# AI 产品方法论（AI Product Methodology）

## Overview

帮助从 0 到 1 定义一款 AI 产品：把模糊的想法，经由一套产品框架与战略定位方法，收敛为一份结构清晰、可直接评审的「产品定义画布」。聚焦 AI 产品特有挑战——能力边界、人机协作、评测与护栏，而非泛化的软件产品流程。

## When to Use

触发场景（满足任一即可）：

- 用户想「定义 / 构思 / 梳理一款（新的）AI 产品、AI 功能、Agent、AI 工作流」。
- 用户需要为 AI 产品选择或应用某个产品框架（JTBD、价值主张画布、北极星指标、AARRR、Hook、Kano、SWOT、竞品分析、差异化定位、TAM/SAM/SOM）。
- 用户要求产出「产品定义画布 / 产品 One-Pager / 产品立项文档」。
- 用户要评估 AI 产品的可行性、差异化、MVP 范围或评测方案。

不覆盖（本 skill 范围外，除非用户另行要求）：PRD/需求文档撰写、用户研究与原型设计、增长投放执行、具体代码实现。

## How to Use

按以下流程执行。资源按需加载，避免在上下文一次塞入全部内容。

### 1. 判定阶段，加载对应方法论
先与用户确认其处于哪个阶段（机会筛选 / 用户问题 / 价值主张 / 定位竞品 / 市场评估 / 方案 MVP / 指标 / 评测）。用 Grep 在 `references/frameworks.md` 定位所需框架，只加载相关片段。

### 2. 走七阶段工作流
以 `references/ai_playbook.md` 为流程主线，逐阶段推进：每个阶段给出目标、关键动作、应使用的方法论、产出物与完成检查点。阶段可迭代，但每阶段需有明确产出再进入下一阶段。

七阶段速览：
- 阶段 0 机会识别与筛选 → 阶段 1 用户与问题(JTBD) → 阶段 2 价值主张 → 阶段 3 差异化定位与竞品 → 阶段 4 市场机会(TAM/SAM/SOM) → 阶段 5 方案与 MVP 边界 → 阶段 6 北极星与漏斗 → 阶段 7 评测与护栏。

### 3. 生成标准交付物
将各阶段产出填入 `assets/product_definition_canvas.md`（模板含 `{{KEY}}` 占位符）。两种填充方式：
- **对话内直接填写**：在回复中输出填写好的画布 Markdown，供用户复制或保存。
- **程序化生成**：若用户给出结构化字段，运行 `scripts/build_canvas.py`：
  ```bash
  python scripts/build_canvas.py --data data.json --out canvas.md
  ```
  `data.json` 为 `{ "PRODUCT_NAME": "...", "NORTH_STAR": "..." }` 形式的对象，键与模板占位符一一对应；缺失项自动标为 `[待填写]`。

### 4. 应用 AI 产品专属约束
全程遵循 `references/frameworks.md` 第 11 节的 AI 专属方法论：
- 先问题后技术，避免「技术可行性先于需求」。
- 明确人机协作档位（Copilot / Agent / 全自动），错误成本越高越靠人。
- 技术路径默认「提示工程 + RAG」起步，按需微调。
- 必须有评测集（golden set）与护栏策略，否则不建议上线。
- 差异化来自数据/场景/工作流/评测，而非「也用了大模型」。

### 5. 提示常见陷阱
在交付时，对照 `references/ai_playbook.md` 的「常见陷阱」清单，主动指出本次方案可能踩坑之处（如用 Demo 替代验证、过度承诺能力边界、忽视成本与延迟）。

## Resources

### references/
- `frameworks.md` —— 产品框架与方法模型目录（含 AI 专属方法论）。执行中按阶段 Grep 加载对应框架。
- `ai_playbook.md` —— 从 0 到 1 定义 AI 产品的七阶段工作流与检查清单、常见陷阱。

### assets/
- `product_definition_canvas.md` —— 可填充的产品定义画布模板（标准交付物骨架，`{{KEY}}` 占位符）。

### scripts/
- `build_canvas.py` —— 从 JSON 批量填充画布模板，生成可交付 Markdown。
