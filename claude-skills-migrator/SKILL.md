---
name: claude-skills-migrator
description: Batch-migrate custom Claude Code skills into WorkBuddy's skill directory. Use whenever the user hands you a folder of custom skills originally written for Claude Code (e.g., deck-*, ui-ux-pro-max, diagram tools) and asks you to "adapt them to WorkBuddy", "make them usable for you", "convert these skills", or similar. Handles frontmatter normalization (agent_created + display_name + display_name_en), brand renaming (Claude/Anthropic/.claude/skills -> WorkBuddy/.workbuddy/skills), the deck-obsidian-claude -> deck-obsidian rename, and LF line-ending cleanup.
agent_created: true
display_name: "Claude 技能迁移器"
display_name_en: "Claude Skills Migrator"
---

# Claude Skills Migrator

批量将用户自定义的 Claude Code 技能目录改造成 WorkBuddy 可用格式，并安装到 `~/.workbuddy/skills/`。

## When to use

触发场景（任一即可）：
- 用户给出一批 `~/.claude/skills/` 下的自定义 skill 目录，要求“适配到 WorkBuddy”。
- 用户说“把这些技能改成你能用的”“转成 WorkBuddy 技能”“迁移这些 Claude 技能”。
- 用户分享了一个技能压缩包或目录，其中包含大量 `SKILL.md` 文件，且原本为 Claude Code 设计。

## How to use

1. 确定源目录（通常为 `~/.claude/skills`）和目标目录（通常为 `~/.workbuddy/skills`）。
2. 运行本技能附带的迁移脚本：

```bash
python scripts/migrate.py <源技能根目录> [--dst <目标目录>]
```

3. 脚本会逐个处理源目录下的子目录：
   - 整目录拷贝到目标目录。
   - 补全 `SKILL.md` frontmatter：`agent_created: true`、`display_name`、`display_name_en`。
   - `deck-obsidian-claude` 自动重命名为 `deck-obsidian`。
   - 将 `SKILL.md` 中的 `Claude Code`、`claude.ai`、`Anthropic`、整词 `Claude` 以及 `.claude/skills` 安装路径替换为 `WorkBuddy` / `.workbuddy/skills`。
   - 对 `README.md` 做最小化重命名（保留真实 URL）。
   - 跳过 `LICENSE*` / `NOTICE*` 等版权文件，避免破坏许可信息。
   - 将所有文本文件换行符统一为 LF。

4. 运行完毕后，校验目标目录中的技能数量，确认没有残留的 `Claude`/`Anthropic` 字样出现在 `SKILL.md` 中。

## Important notes

- 示例文件（`example.html`、`example.md`、`template.html` 等）中的 `Claude` 字样不会被替换，因为它们通常是演示内容而非指令，机械替换会破坏示例（例如模型名 `claude-opus-4-6`、产品对比文案）。
- 如果源技能里包含 Anthropic 官方 API 参考类或 Academy 教程类技能，请改用 `skill-migrate`，而不是本脚本。
- 迁移完成后，WorkBuddy 无需重启即可在可用技能列表中看到新技能。
