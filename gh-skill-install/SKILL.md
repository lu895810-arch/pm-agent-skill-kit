---
name: gh-skill-install
description: >-
  把 GitHub 上任意 Agent Skill 安装并适配到 WorkBuddy。覆盖安全审计、按结构拷贝技能目录、
  托管 Python/Node 运行时接线、CLI shim 与 PATH 落地、frontmatter 适配、端到端冒烟测试。
  当用户发来 GitHub 仓库链接要求"安装这个技能 / 装一下这些 skill / 检查并安装"时使用。
license: MIT
buddy-adapted: "2026-09-24"
owner: "Buddy（Lulu 的数字搭子）"
---

# 安装并适配 GitHub Agent Skill 到 WorkBuddy

用户丢来 GitHub 仓库（或一列仓库），要装成 WorkBuddy 技能并适配。按下面流程走，
别凭感觉；每一步都可独立验证。

## 0. 先确认是否已是技能、是否已在本地

- 在 `~/.workbuddy/skills/` 里按仓库名/功能搜一遍，避免重复安装。
- 区分三类来源：
  - **真技能**（有 `SKILL.md`，符合 Agent Skills 格式）→ 走安装。
  - **改造版已在本地**（如 `buddy-diagram-design` 是 Anthropic `diagram-design` 的改造版）→ 跳过，告知用户已覆盖。
  - **不是技能**（整个仓库是 Web 应用 / 平台，无 `SKILL.md`，如 DeepDiagram）→ 不能当 skill 装，直接说明原因（许可证、需要 Docker/DB 等）。
- 用 WebFetch 抓仓库 README / 目录，判断它属于哪类、产物是什么、依赖什么。

## 1. 安全审计（强制，先于任何安装）

克隆前或克隆后都可，但**装之前必须做**。逐项核查，最后给 P0 / P1 / P2 判定：

1. 查 `package.json` 是否有 `postinstall` / `preinstall` / `install` 生命周期钩子（`grep -iE '"postinstall"|"preinstall"|"install"'`）。
2. 全仓扫描运行时脚本（`.py/.js/.mjs/.ts/.sh`）有无：
   - `eval(` / `exec(` / `os.system` / `subprocess` 拼接 shell / `child_process` 注入；
   - 凭据访问：`os.environ` 读密钥、`API_KEY`、`openai` 等敏感环境变量外传；
   - 隐蔽外联：`urllib`/`requests`/`http` 主动上报（区分"按需抓公开 CDN 资源"与"静默回传数据"）；
   - 破坏性：`rm -rf` / `shutil.rmtree` 在运行时脚本里（注意 `tools/`、`scripts/` 等 dev 目录不算技能运行时，装技能只拷 `skills/<name>/`）。
3. 判定：
   - **P0** 有静默外联上报、凭据外泄、隐藏 `postinstall` 跑远程代码 → 强烈警告，要求用户显式确认才装。
   - **P1** 有 `postinstall` 或需 `sudo` / `curl|bash` / 全局副作用 → 警告并要求确认。
   - **P2** 无上述，仅有按需公开资源抓取或本地可选导出依赖 → 直接装。

> 本机无 `skills-security-check` 技能时，按上面手搓审计，结论写进回复。

## 2. 浅克隆 + 定位技能目录

```bash
mkdir -p /tmp/skill_audit && cd /tmp/skill_audit
git clone --depth 1 <repo> <short>   # 大仓也用 --depth 1
```

- 多数仓库技能在 `skills/<name>/SKILL.md` 或根 `SKILL.md`。
- 有的仓库一个 repo 含**多个**技能（如 `drawio-ai-kit` 出 5 个 `drawio-*`），逐个拷贝。
- 有的仓库技能依赖一个**引擎**目录（如 `drawio-ai-kit` 的 `src/`、`catalog/`、`rules/`、`vendor/`），引擎要单独落到稳定路径，技能靠 CLI 调它。

## 3. 拷贝到 WorkBuddy 技能目录

```bash
cp -r <clone>/skills/<name> ~/.workbuddy/skills/<name>
```

- 引擎（若需）：`mkdir -p ~/.workbuddy/<kit>-engine && (cd <clone> && tar cf - --exclude='.git' . | tar xf - -C ~/.workbuddy/<kit>-engine)`。
- 拷贝完 `rm -rf /tmp/skill_audit` 清场。

## 4. 运行时接线（关键，决定能不能用）

WorkBuddy 的托管运行时已在 PATH：`python3`（~/.workbuddy/binaries/python/...）和 `node`（~/.workbuddy/binaries/node/...）。
技能脚本若写 `python3` / `node`，通常直接可用。要处理两种情况：

### 4a. 技能依赖外部 CLI（如 `drawio-ai`、`archify`）
做 shim，让裸命令在 WorkBuddy Bash 会话里也能解析：

1. 在 `~/.workbuddy/bin/` 写 `drawio-ai`（无扩展，shebang `#!/bin/sh`，`exec node "<引擎或技能>/src/cli.mjs" "$@"`）和 `drawio-ai.cmd`（`node "绝对路径" %*`）。`archify` 同理。
2. shim 放两处，确保都生效：
   - `~/.workbuddy/bin/`：用 PowerShell `[Environment]::SetEnvironmentVariable("PATH", "...;C:\Users\admin\.workbuddy\bin", "User")` 加进**用户** PATH（供 WorkBuddy 重启后 / 外部终端用）。
   - **托管 node bin 目录** `~/.workbuddy/binaries/node/versions/<ver>/`：直接 `cp` shim 过去（该目录稳在 PATH，解决"当前会话 Git Bash 继承宿主环境、新增 User PATH 重启前不生效"的坑）。
3. `chmod +x` 无扩展 shim。验证：`command -v drawio-ai` 与 `command -v archify` 都能解析。

### 4b. Node 技能需要运行时依赖
在技能目录 `npm install`（用托管 node；允许 `devDependencies`，运行时常需它们，如 archify 的 ajv/parse5/saxes/simple-icons）。

### 4c. Python 技能的可选导出依赖
核心若只用标准库即可离线跑；PNG/GIF 之类可选导出需要的 `rsvg-convert` / `cairosvg` / Puppeteer 按需再装，并在适配说明里写清。

## 5. frontmatter 适配（别踩 YAML 折叠标量坑）

在 `SKILL.md` 的 frontmatter 里加元数据，**必须先看有没有折叠标量**：

- 若 frontmatter 里有 `description: >-` / `>-` / `|` 这类块标量：插入的 `buddy-adapted: ...` 等行**必须按列 0** 插在折叠块结束之后（折叠块在遇到缩进 < 2 的行时结束），否则会被吞进 description 字符串，导致元数据不是顶层键、甚至污染描述。
- 正确做法（Python 脚本）：取两个 `---` 之间的 frontmatter；删掉旧的可疑元数据行；若检测到块标量则在其结束处按列 0 插入，否则在 closing `---` 前按列 0 追加：
  ```
  buddy-adapted: "YYYY-MM-DD"
  owner: "Buddy（Lulu 的数字搭子）"
  upstream: "<repo>"
  ```
- 验证：`yaml.safe_load(frontmatter)` 且 `"buddy-adapted" in d` 且 `buddy-adapted` 不在 `d["description"]` 里。
- 在 frontmatter 之后（body 开头）加一段 `> **Buddy 适配（日期）**：…` 说明运行时、引擎/shim 路径、可选依赖，方便日后回看。

## 6. 端到端冒烟测试（装完必须验，别吹）

- `python3 scripts/<cli>.py doctor` / `version`，或 `node bin/<cli>.mjs doctor`。
- 对依赖外部 CLI 的技能：先确认 `command -v <cli>` 通过，再跑一个真实生成（如 `archify render lifecycle <example>.json out.html`、`fireworks render memory <fixture>.json out.svg`）。
- 注意技能对**类型/参数**有约束（如 fireworks 的 template type 要和 fixture 的 mode 匹配、archify 的 `<type>` 要对应 example 文件名），用错参数会报"conflict/const"——那是调用姿势问题，不是技能坏。

## 7. 交付给用户

- 列出：已覆盖（哪些其实已有）、新装了哪些、哪些不是技能已说明。
- 写明每个技能的触发方式、产物格式、以及**可选依赖**（PNG/GIF 需 rsvg-convert/Puppeteer；`.drawio` 的 PNG 渲染需 draw.io 桌面 CLI ≥ v30；Graphviz 可选）。
- 若做了 shim/PATH 改动，说明改动位置与"重启 WorkBuddy 后外部终端也能用"。
