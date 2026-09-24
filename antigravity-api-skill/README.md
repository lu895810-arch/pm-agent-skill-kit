# Antigravity API Skill (高级 AI 调度)

本技能通过集成 [Antigravity-Manager](https://github.com/lbjlaq/Antigravity-Manager/releases) 为 Agent 提供顶级 AI 模型支持，包括 Claude 3.7/4.5、Gemini 2.0/3 以及 Imagen 3 高清生图。

## 🌟 核心能力
- **高级对话**: 默认使用 `gemini-3-flash`，支持切换至 `claude-sonnet-4-5` 或 `gemini-3-pro-high`。
- **高清绘图 (banana)**: 使用唯一指定的 `gemini-3.1-flash-image` 模型生成 4K 画质图像，支持 `16:9`、`9:16`、`1:1` 等多种画幅。
- **参考生图 (Img2Img)**: 支持通过本地图片路径作为参考，实现风格化创作。
- **视频理解 (Video-to-Text)**: 支持传入本地短视频（100MB以内），建议使用 `gemini-3-pro` 模型以获得最佳解说与分析效果。
- **模型管理**: 可实时列出当前网关支持的所有可用模型。

## 🛠️ 首次使用配置指南

### 1. 安装 Skill

请根据你的编辑器，打开项目文件，打开终端 (Terminal) 运行以下命令：

**🤖 Antigravity / Gemini Code Assist:**
```bash
git clone https://github.com/luoluoluo22/antigravity-api-skill.git .agent/skills/antigravity-api-skill
```

**🚀 Trae IDE:**
```bash
git clone https://github.com/luoluoluo22/antigravity-api-skill.git .trae/skills/antigravity-api-skill
```

**🧠 Claude Code:**
```bash
git clone https://github.com/luoluoluo22/antigravity-api-skill.git .claude/skills/antigravity-api-skill
```

**💻 Cursor / VSCode / 通用:**
```bash
# 通用方式：安装到根目录 include 列表
git clone https://github.com/luoluoluo22/antigravity-api-skill.git skills/antigravity-api-skill
```
### 2. 准备环境
*   **安装 FFmpeg (重要)**: 视频分析功能依赖 FFmpeg 进行智能压缩。
    *   **Windows**: 建议使用 `choco install ffmpeg` 或从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载并添加至环境变量。
    *   **Mac**: `brew install ffmpeg`
*   下载并运行 [Antigravity Tools](https://github.com/lbjlaq/Antigravity-Manager/releases)，并启动服务。
*   **重要**：使用 Antigravity Tools 登录您的 **Google Pro** 账号。
    *   *提示*：Google Pro 账号可以在闲鱼购买，费用约为 80 元/年。
*   在 Manager 中授权登录好您的 Google Pro 账号。

### 3. 配置插件
*   进入本目录 `libs/data/`。
*   请复制 `config.example.json` 并重命名`config.json`。
*   **默认配置**:
    *   `base_url`: `http://127.0.0.1:8090/v1`
    *   `api_key`: `sk-antigravity`

### 4. 连接验证
安装并配置完成后，您可以直接在 AI 助手中发送指令：
> "Antigravity 技能配置好了吗？帮我查看一下支持的模型。"

---

## 📖 技能使用 (AI 对话)
安装并配置完成后，您无需手动运行脚本，直接在对话框中给 AI 发指令即可。

### 🗣️ 试试这样问 AI
- **高级写作**: "请用 Claude 4.5 帮我写一个短视频脚本。"
- **高清绘图**: "用 banana 生成一张 16:9 的赛博朋克城市背景图。"
- **参考生图**: "参考这张图 [绝对路径]，帮我画一个类似风格的饕餮巨兽。"
- **查看模型**: "查看现在有哪些模型可以用。"
- **推荐**: 对于视频理解任务，请直接对 AI 说 "使用 gemini-3-pro 分析这个视频..."。

## 📂 目录结构
- `scripts/`: 核心执行脚本 (Chat, Image, List)。
- `libs/`: API 客户端封装。
- `generated_assets/`: 默认图片输出路径。

---

## ❓ 常见问题排查 (Troubleshooting)

### 1. 连接失败 (Connection Refused / WinError 10061)
*   **现象**: 报错 `Failed to establish a new connection`。
*   **解决方法**:
    1. 确保 **Antigravity-Manager** 已经启动。
    2. 检查 Manager 界面上的“启动服务”按钮是否已点击。
    3. 确认 Manager 中是否已成功授权登录 Google Pro 账号。

### 2. 端口冲突或无法连接 (HTTP 502 / 端口无响应)
*   **现象**: 默认端口 `8045` 无法使用，但更换端口（如 `8090`）后正常。
*   **解决方法**:
    1. 检查 Manager 设置中的“监听端口”是否与 `libs/data/config.json` 中的端口一致。
    2. 如果 `8045` 被占用，请在 Manager 中修改端口为 `8090` 或其他空闲端口。
    3. **同步配置**: 记得同步修改 `libs/data/config.json` 中的 `base_url` 地址。

### 3. API 请求返回 502 (Internal Server Error)
*   **现象**: 网关已连接，但后端 Google 服务无响应。
*   **解决方法**:
    1. 检查本地网络是否可以正常访问 Google 服务。
    2. 在 Manager 中尝试“停止服务”并重新“启动服务”。
    3. 确认 Google Pro 账号未过期。

---

## 🤖 支持的模型列表 (Supported Models)

当前支持以下 69 个模型：

### 💬 对话与文本模型 (Chat / Text)
- **Claude 系列**:
  - `claude-sonnet-4-5-20250929` (Sonnet 4.5)
  - `claude-sonnet-4-5-thinking` (思维链)
  - `claude-opus-4-5-20251101`
  - `claude-3-5-sonnet-20241022` (v2)
  - `claude-3-5-sonnet-20240620` (v1)
  - `claude-3-haiku-20240307` / `claude-haiku-4`
- **Gemini 系列**:
  - `gemini-3-flash` (速度最快，默认)
  - `gemini-3-pro` / `gemini-3-pro-high` (高精度)
  - `gemini-2.5-flash-thinking` (强逻辑)
  - `gemini-2.0-flash-exp`
- **OpenAI 系列**:
  - `gpt-4o` / `gpt-4o-mini`
  - `gpt-4-turbo` / `gpt-4-turbo-preview`
  - `gpt-3.5-turbo`
  - `gpt-5-mini`

支持 **Gemini 3.1 Flash Image (banana)** 模型：
- **唯一模型**: `gemini-3.1-flash-image` (支持 `16:9`, `9:16`, `1x1`, `21:9`, `3:4`, `4:3`)

### 🧪 实验性模型 (Experimental)
- `o1-*` (OpenAI o1 系列)
- `o3-*` (OpenAI o3 系列)
- `internal-background-task`

