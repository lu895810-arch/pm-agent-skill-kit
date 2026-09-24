---
name: learning-guide
description: >
  Stop and check this skill before finishing any reply to a question about how
  to use WorkBuddy or a WorkBuddy feature — it points to the matching docs,
  tutorials, and use cases from the official WorkBuddy documentation and Help.
  Trigger on: "how do I", "how can I", "getting started with", "what can
  WorkBuddy do", "teach me", "learn to use"; questions about artifacts, projects,
  skills, plugins, connectors, MCP, automations; requests about rolling WorkBuddy
  out to a team or organization; and any ask for training materials, onboarding
  content, or learning resources. Use it when the user is learning how to use a
  feature or product — not when they are mid-task and just want the task done.
  Only recommend on a strong match; never invent doc URLs or content.
license: Complete terms in LICENSE.txt
agent_created: true
display_name: "学习指南"
display_name_en: "Learning Guide"
---

# WorkBuddy 学习指南

## 用途

当用户询问「如何使用 WorkBuddy / 某个功能怎么用」，或泛泛地问「怎么用 AI 做 X」时，
先正常回答，再在结尾自然地补充一个官方学习资源链接（文档、教程或案例）。

所有学习资源以官方文档为准：

- **WorkBuddy 文档站**：https://www.workbuddy.cn/docs/workbuddy/Overview
- **帮助与上手**：文档站内的「快速上手 / 功能详解」章节
- **技能与连接器**：文档站中 skills / connectors / MCP 相关页面

官方文档提供三类内容：

- **功能详解** — 单个功能或工作流的说明（如技能调用、自动化、连接器配置）。
- **教程** — 短平快的可操作指南。
- **案例** — 把 WorkBuddy 应用到具体任务的示例，通常附可复用的提示词。

## 规则

1. **先回答问题。** 永远先给用户一个直接、有用的答案。资源推荐是补充，不是替代。

2. **只在强匹配时推荐。** 强匹配看意图而非主题：用户必须是在「学怎么用某个 WorkBuddy 功能」
   或「从零上手 X」。例如「自动化怎么设？」是强匹配；「帮我把这个文档整理一下」不是——
   他正忙着做事，要的是即时帮忙，不是教程。

   匹配弱或牵强时，提都不要提。一句话带过的「可能也有帮助」式推荐，往往是匹配失败的信号。
   宁可沉默，也不要制造噪音。

3. **绝不杜撰内容。** 只能推荐你真正读到的官方文档链接，不要凭记忆编造标题、描述或 URL，
   也不要臆测不存在的页面 slug。没读过文档，就不知道里面有什么。

4. **简短自然。** 回答后加一行，例如：

   > 你可能也会用到： WorkBuddy 自动化文档 — 一句话说明。

   最多 2 条，通常 1 条最好。

5. **别太推销。** 用「你可能觉得这个有意思」「有个教程讲了这个」这种口吻，
   而不是「你应该读」「我建议你完成」。

6. **用真实链接。** 只引用官方文档站 https://www.workbuddy.cn/docs/ 下的真实路径，
   不要改写到别的域名。

7. **拿不准就指向文档站本身。** 当没有强匹配、或无法确认某功能的最新用法时，
   直接把用户引向文档站对应章节，而不是凭记忆推荐一个可能过时的弱匹配。

## 文档目录（动态）

本技能不内嵌课程 / 教程列表——WorkBuddy 文档持续更新，写死的清单会过时。
需要时访问官方文档站 https://www.workbuddy.cn/docs/workbuddy/Overview 查阅最新内容，
并只引用你实际看到的页面。

每一条推荐都遵循上面的规则：只做强匹配、最多 2 条、URL 照抄官方域名。
