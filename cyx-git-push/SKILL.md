---
name: cyx-git-push
description: 把本地技能目录或任意文件树推送到 GitHub 仓库的标准流程。解决本机没有 git 凭据助手、git push 卡在认证的问题——用用户提供的 Personal Access Token（PAT）内嵌进命令行 URL 一次性推送，令牌不落盘、推完清配置。覆盖空仓库首推、二进制文件处理、.git/config 令牌泄露防护、远程内容核验等坑。
version: "1.0"
owner: "Buddy（Lulu 的数字搭子）"
upstream: "自沉淀（基于 2026-09-24 推送 cyx-* 技能到 lu895810-arch/skills 的实战）"
buddy-adapted: "2026-09-24"
---

# cyx-git-push

## 一、这个技能解决什么

你有一批本地技能（或任意文件）要传上 GitHub，但本机 git 没有可用的凭据助手：直接 `git push` 会弹窗卡死或报 `could not read Username`。这个技能用你临时给的 Personal Access Token（PAT），把令牌直接拼进这一次推送的远程地址里，推完立刻把配置里的令牌抹掉。令牌只活在一条命令行里，不写文件、不留存。

## 二、什么时候用

- 把 `~/.workbuddy/skills/` 下的技能打包上传到你的 GitHub 仓库。
- 任何"本地文件树 → 公开/私有 GitHub 仓库"的单向推送，且本机没有配置好 git 凭据。
- 需要传二进制（图片、字体）时——这是本流程的核心价值，因为 GitHub MCP 的文件接口传二进制会被损坏（见第六节）。

## 三、前置条件

1. git 已安装（`git --version` 能跑）。
2. 目标仓库已存在，或你有权限新建。空仓库（零提交）也能推，首推会创建默认分支。
3. 你手里有该仓库的 PAT（classic 或 fine-grained，需 `repo` 或至少 `public_repo` 权限）。没有就现生成一个（话术见第七节）。
4. 备选：GitHub MCP 已连接——但只适合纯文本文件，二进制别走它。

## 四、标准流程（7 步）

### 1. 盘点与清理本地文件

把要传的目录复制到一个干净的打包目录，**剔除编译缓存**：

```bash
SK=~/.workbuddy/skills
rm -rf /tmp/cyx_bundle && mkdir -p /tmp/cyx_bundle
for d in "$SK"/cyx-*; do
  rsync -a --exclude='__pycache__' --exclude='*.pyc' "$d" /tmp/cyx_bundle/ 2>/dev/null || true
done
```

> 注意：`rsync` 在某些 Git Bash 环境不一定有，没有就用 `cp -a` 后删缓存；关键是**确认打包目录里确实有你要的文件再往下走**（这次就吃过 README 没落进去的亏，见第六节第 5 条）。

### 2. 准备本地仓库

目标仓库若为空（零提交），直接克隆再拷文件最干净：

```bash
rm -rf /tmp/cyx_push
git clone --depth 1 https://github.com/<owner>/<repo>.git /tmp/cyx_push
cp -a /tmp/cyx_bundle/. /tmp/cyx_push/   # 末尾的 /. 连隐藏文件一起拷
```

> 克隆失败多半是网络或仓库名错，先 `curl -s -o /dev/null -w "%{http_code}" https://api.github.com/repos/<owner>/<repo>` 验仓库存不存在（200 = 在）。

### 3. 本地提交（不需要令牌）

```bash
cd /tmp/cyx_push
git config user.email "buddy@workbuddy.local"
git config user.name "Buddy"
git config --global --add safe.directory /tmp/cyx_push
git add -A
git commit -m "Add skills bundle with README and categorization"
```

> Windows 上会冒 CRLF 行尾提示，无害，不影响内容。

### 4. 向用户取 PAT（话术见第七节）

明确告诉用户：令牌只用于这一次推送，不写文件、不留存；推完建议去吊销。

### 5. 用 PAT 推送（关键安全步骤）

```bash
TOKEN="ghp_xxxx"   # 用户给的，直接替换
cd /tmp/cyx_push
GIT_TERMINAL_PROMPT=0 git -c credential.helper= \
  push "https://${TOKEN}@github.com/<owner>/<repo>.git" main
```

要点：

- **令牌放在命令行 URL 参数里，不是 config、不是文件。**
- `GIT_TERMINAL_PROMPT=0` 防止卡在交互输入。
- `-c credential.helper=` 临时禁用本机那个会弹窗的凭据助手。
- 分支名用本地实际分支（常见 `main` / `master`），`git branch` 看一眼。
- **不要加 `-u`**：`-u` 会把带令牌的 URL 写进 `.git/config` 的 `branch.main.remote`（见第六节第 2 条）。这里用一次性 URL 参数推，不加 `-u` 就不会污染 config。

### 6. 清理配置里的令牌

即使没用 `-u`，也跑一遍确认：

```bash
git config branch.main.remote origin   # 把可能被污染的字段改回干净值
grep -c "ghp_" /tmp/cyx_push/.git/config && echo "仍有令牌(坏)" || echo "配置干净(好)"
```

> 若上一步误用了 `-u`，这条 `branch.main.remote origin` 就是把令牌抹掉的关键。

### 7. 远程核验

用 API 数文件和确认内容到位（带令牌的 curl 只这次用）：

```bash
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/<owner>/<repo>/git/trees/main?recursive=1" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);t=[x for x in d.get('tree',[]) if x['type']=='blob'];print('文件总数:',len(t))"
```

对比本地 `find /tmp/cyx_push -type f -not -path '*/.git/*' | wc -l`，数量对上才算完。

## 五、安全红线（必须守）

- 令牌**只**出现在当次推送的 shell 命令里；绝不写进脚本文件、README、提交信息、`.git/config` 持久项。
- 命令输出里用 `sed 's/ghp_[A-Za-z0-9]*/<TOKEN>/g'` 把令牌打码再回显。
- 推完用 `grep -c ghp_ .git/config` 确认本地零残留；若曾有 `-u`，执行 `git config branch.main.remote origin`。
- 推完**提醒用户去 https://github.com/settings/tokens 吊销该令牌**（短令牌、用完即废是标准做法）。
- 令牌属于敏感信息，对话里出现后，本环境不替你留存，但你自己也要当心截图或转发。

## 六、踩过的坑与对策

1. **凭据助手弹窗卡死**：本机全局 `credential.helper` 是 Windows 凭据选择器，会弹窗等输入导致推送中断。对策：`GIT_TERMINAL_PROMPT=0 git -c credential.helper=` 双保险绕过。
2. **`git push -u` 把令牌写进 config**：`push -u` 会在 `[branch "main"]` 里记 `remote = https://TOKEN@...`。对策：不用 `-u`，或推完 `git config branch.main.remote origin`。`[remote "origin"] url` 若用 CLI 参数传则不污染，但 branch 字段会。
3. **二进制走 GitHub MCP 会坏**：MCP 的 `create_or_update_file` 明确"不要 base64、服务器编码"，二进制字节塞不进 UTF-8，强行传会被二次编码损坏。图片/字体必须走 git+PAT 这条路。MCP 只适合纯文本。
4. **空仓库首推**：目标仓库零提交、无默认分支时，第一次 push 直接创建你本地所在分支名（如 `main`）。推之前 `git branch` 确认名字，别推错分支。
5. **README / 关键文件漏传**：那次 `cp -a` 在 README 还没写进 bundle 时就跑了，远程一开始只有技能目录缺 README。对策：拷贝后、`git add` 前，用 `ls` 核对打包目录根确实有 README.md、.gitignore 等再提交。
6. **`git clone` 只读成功但 push 报无凭据**：只读克隆不需要认证，别被它骗了——push 才是真要凭据的环节。

## 七、给用户取令牌的引导话术（可直接用）

> 给你令牌最干净的方式，就是直接在对话框里把那串字符粘贴发给我。下面一步步带你生成，全程不用离开 GitHub 网页。
> 1. 打开 `https://github.com/settings/tokens`（左侧 `Developer settings` → `Personal access tokens` → `Tokens (classic)`）。
> 2. 点 `Generate new token` → `Generate new token (classic)`。
> 3. 起个名字，比如 `skills-push-2026`。
> 4. 权限勾 `repo`（含公有/私有仓库读写）；仓库是 public 的话只勾 `public_repo` 也行。
> 5. 有效期选 `7 days` 或自定义短期限，推完即废。
> 6. 拉到底点 `Generate token`，复制以 `ghp_` 开头的整串（约 40 位）发我。
> 我拿到后：令牌只拼进这一次 push 的远程地址，不写文件、不留存；推完立刻重置配置；建议你随后去吊销。你不用告诉我 GitHub 用户名，按仓库地址推即可。

## 八、核验命令清单（速查）

```bash
# 仓库是否存在
curl -s -o /dev/null -w "%{http_code}" https://api.github.com/repos/<owner>/<repo>
# 本地文件数
find /tmp/cyx_push -type f -not -path '*/.git/*' | wc -l
# 远程文件数
curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/<owner>/<repo>/git/trees/main?recursive=1" | python3 -c "import sys,json;print(len([x for x in json.load(sys.stdin).get('tree',[]) if x['type']=='blob']))"
# 配置有无令牌残留
grep -c "ghp_" /tmp/cyx_push/.git/config
```

## 九、装到 WorkBuddy 的方式（README 里可写）

把需要的技能目录整个复制到 `~/.workbuddy/skills/`、刷新即可；带上下游依赖的（如某条流水线里的多个步骤技能）要连同上游一起装。
