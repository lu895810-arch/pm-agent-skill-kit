---
name: skill-migrate
description: 将 Anthropic 官方格式的 SKILL.md 技能（Claude skills 仓库）改造并安装到 WorkBuddy 用户技能目录。当用户要把一批外部/第三方技能适配到 WorkBuddy、或要求「把这个技能改造下适配你自己」时使用，支持单技能改造与按用户指定新名重命名。自动完成：拷贝目录、重命名 Claude/Claude Code/Anthropic → WorkBuddy、补充 agent_created 与 display_name 元数据、规范换行符、保留 LICENSE、对 Anthropic 专属技能做语境化处理，并把 Playwright MCP / shell 检查等换成本机可用能力。
license: MIT
agent_created: true
display_name: "技能迁移"
display_name_en: "Skill Migrate"
---

# 技能迁移（Claude skills → WorkBuddy）

将 Anthropic 官方 skill 仓库里的技能改造成 WorkBuddy 可用格式并安装到用户级技能目录
`~/.workbuddy/skills/`。

## 适用场景

- 用户把一批 `SKILL.md` 技能目录丢给你，要求「适配成 WorkBuddy 的技能」「改成你能用的」。
- 源技能通常来自 `skills-main/skills/*`（Anthropic 格式：SKILL.md + YAML 前置元数据 + 可选的 scripts/references/assets）。

## 流程

1. **侦察**：列出源技能目录与子文件，读取每个 `SKILL.md` 的元数据和正文开头，判断体量（是否有 scripts/schemas 等大文件）。同时读取一个现有 WorkBuddy 技能，确认目标元数据格式（`agent_created`、`display_name`、`display_name_en`）。

2. **安全扫描**：对源脚本 grep 危险模式（`eval(`/`exec(`/`os.system`/`shell=True`/管道到 sh 的 curl）。Anthropic 官方仓库一般干净，仅记录 `shell=True` 类正常用途。

3. **拷贝**：把整个技能目录复制到 `~/.workbuddy/skills/<name>/`（保留所有子目录与 LICENSE.txt）。
   - ⚠️ **本机（Windows）Bash 工具可能不可用**：Git Bash 取不到 coreutils（报 `ls: command not found` / `dirname: command not found`），`cp -r` 会直接失败；`PowerShell` 工具能执行命令但**不返回 stdout**，只能靠副作用判断成败。
   - 因此文件操作一律走内置工具：新建/拷贝用 `PowerShell` 的 `New-Item -Force` / `Copy-Item -LiteralPath ... -Force`（中文/带括号路径必须用 `-LiteralPath`），**再用 `Glob` 验证目标文件确实存在**；读改写用 `Read`/`Write`/`Edit`；搜索校验用 `Grep`。不要依赖任何 shell 回显。

4. **改造每个 SKILL.md**（见 `migrate.py`）：
   - 前置元数据追加 `agent_created: true`、`display_name`、`display_name_en`。
   - 正文重命名（顺序很重要，先长后短）：
     1. `Claude Code` → `WorkBuddy`
     2. `claude.ai` / `Claude.ai` → `WorkBuddy`
     3. `Cowork` → `WorkBuddy`
     4. `Anthropic`（大小写） → `WorkBuddy`
     5. 其余 `\bClaude\b`（大小写） → `WorkBuddy`
   - **不要改 LICENSE.txt**（含版权方名称，改了等于伪造许可）。

5. **Anthropic 专属技能语境化**（不在上面统一重命名范围内，需手动判断）：
   - **Claude API 参考类**：保留 `Anthropic`/`Claude` 正文（它文档化的是 Anthropic API，重命名会出错），只加元数据。
   - **Academy/学习类**：`academy.claude.com` 在 WorkBuddy 无对应物 → 重写为指向官方文档 `https://www.workbuddy.cn/docs/workbuddy/Overview` 的学习指南，保留「先答后荐、不杜撰」原则，并可重命名目录（如 `academy-guide` → `learning-guide`，记得同步改 `name` 字段）。
   - **品牌规范类**：`Anthropic` 品牌 → `WorkBuddy` 品牌，色板作为默认参考，加注「如需对齐官方请替换」。

6. **规范换行符**：Windows 下 `open(...,"w")` 会把 LF 写成 CRLF，统一把文本文件（`.md/.py/.js/.css/.html/.json/.txt/.sh/.xml`）的 `\r\n` 转回 `\n`，保持干净。

7. **验证**：逐技能确认 `name` / `agent_created: true` / `display_name` 存在；grep 全文确认无意外残留的 `Claude`/`Anthropic`（API 参考类除外）。

## 单技能改造（本地目录 / 用户指定新名）

用户常见说法：「把这个 skill 改造下适配你自己」「同时命名为 xxx」。与批量迁移的差别：

1. **源目录常在本地**（桌面、下载目录，路径带括号/中文很常见）→ 先 `Glob **/*` 列全文件，再 `Read` 逐个读完，确认除 assets/scripts 外没有隐藏依赖。
2. **改名要两处同步**：目标目录名 + frontmatter `name:` **必须一致**（如都叫 `cyx-course-html`），`display_name` 跟着改成中文名（如 `"cyx 课堂课件 HTML 制作"`），否则技能列表里对不上。用户名的 `cyx-` 前缀是既有约定，沿用即可。
3. **自引用同步改**：相对路径（`assets/xxx.html`）不用动，但正文里写死的旧技能名（如「本技能 course-html」）要一并替换。
4. **「适配你自己」不只是改名字**——把流程里 WorkBuddy 不存在的能力换掉：
   - Playwright MCP → 先加载 `agent-browser` 技能（细粒度交互用 `playwright-cli`）
   - shell `grep` / `sort | uniq -c` 管道 → 内置 `Grep` 工具（`output_mode: count|content`）
   - `cp -r` / shell 文件操作 → `Write`/`Edit`/`PowerShell Copy-Item`
   - 交付环节补上 → `present_files` 打开最终 HTML 预览
   - 本地起服务用托管 Python 绝对路径：`C:\Users\admin\.workbuddy\binaries\python\versions\3.13.12\python.exe -m http.server <port>`
5. 补一节**「与其它技能的分工」**，写清和同域技能（如 `ai-course-md-to-html`、`cyx-html-style`、`cyx-research-report`）的边界，避免触发时选错。
6. **装前先做安全审计**（`skills-security-check`）：纯静态 HTML/CSS + Markdown 的文档型技能通常判 P2；带脚本的逐文件扫 `eval(` / `exec(` / `curl | bash` / `npm install -g` / 读取 `~/.ssh`·`.env` 后外送。审计报告要复述给用户。
7. 装完用 `present_files` 把 SKILL.md 交给用户过目。

## 已知限制（迁移后提醒用户）

- `docx/pptx/xlsx/pdf` 等脚本类技能依赖外部工具（pandoc、libreoffice/soffice、poppler `pdftoppm`）与 Python 库（python-docx、python-pptx、openpyxl、npm `docx`），托管环境可能未装；触发时会引导安装。
- `skill-creator` 的「描述优化」步骤引用 `claude -p` CLI，WorkBuddy 无此命令，属已知限制。
- `slack-gif-creator` 面向 Slack（当前未连接），保留备用。

## 复用脚本

`migrate.py` 是通用版：接受源目录参数，自动拷贝 + 重命名 + 补元数据 + 规范换行符，并对 `claude-api`/`academy-guide`/`brand-guidelines` 按上方规则特殊处理。
