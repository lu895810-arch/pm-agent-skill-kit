---
name: antigravity-api-skill
description: 当用户需要使用 Antigravity 反代出来的 API (Gemini 3 Flash,Gemini 3 pro, banana生图, 视频分析理解) 时使用此技能。
---

# Antigravity Skill

## 目标
利用 Antigravity API 网关提供的加强版 AI 能力，包括 **Gemini 3 Flash / Pro**文本生成与 **Gemini 3 Pro Image (Imagen 3)** 的 4K 绘图能力。

## 场景
- **高级对话**: 使用 Gemini 3 进行复杂逻辑分析、脚本编写。
- **高清绘图**: 生成 16:9 4K 质量的视频素材、封面图 (优于普通绘图)。
- **视频深度理解 (Vid2Text)**: 内置 **FFmpeg 智能压缩引擎**，支持 100MB+ 甚至 500MB+ 的超大视频。自动优化分辨率（480P）以在保留准确时间轴的前提下，实现极速上传与分析。
- **批量素材处理**: 支持一次性喂入多个视频/图片素材。适用于分析全集剧情、对比视频色彩或批量生成解说词。

## 环境配置 (Setup)

### 首次使用配置指南
本技能依赖本地运行的 **Antigravity Manager** 服务。首次使用请按以下步骤配置：

1.  **准备环境**:
    *   **安装 FFmpeg (必填)**: 视频分析依赖它进行压缩。Windows 建议从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载。
    *   **下载客户端**: [Antigravity-Manager Releases](https://github.com/lbjlaq/Antigravity-Manager/releases)
    *   **重要**: 必须在客户端中登录您的 **Google Pro** 账号（可在闲鱼购买，约 80 元/年）。

2.  **配置连接**:
    *   **零配置启动**: 脚本会自动回退到 `config.example.json`，如果 Manager 使用默认设置（端口 8045），您可以直接开始使用，如果访问出错，尝试修改为8090，配置文件也需要同步修改。
    *   **自定义配置**: 如需修改，请复制 `libs/data/config.example.json` 为 `config.json`。
    *   **默认地址**: `http://127.0.0.1:845/v1`

3.  **验证连接**:
    *   运行指令 "查看所有模型" 或 "/Antigravity 技能配置好了吗" 来测试。

## 指令

### 🗣️ 试试这样问 AI
- **高级写作**: "请用 gemini-3-pro 帮我写一个短视频脚本。"
- **高清绘图**: "用 banana 生成一张 16:9 的赛博朋克城市背景图。"
- **参考生图**: "参考这张图 [绝对路径]，帮我画一个类似风格的饕餮巨兽。"
- **视频理解**: "帮帮我分析下这个视频的内容：[视频路径]"
- **查看模型**: "查看现在有哪些模型可以用。"
- **推荐模型**: `gemini-3-flash` (视频理解首选), `gemini-3-pro-high`

### 1. 对话与多模态 (Chat & Multimodal)
**指令**: "请帮我写一段脚本..." / "分析这个视频: [视频路径]"
- **执行**: `python scripts/chat.py "{Prompt}" "{ModelName}" "{FilePath1}" "{FilePath2}" ...`
- **能力**: 
  - 自动识别图片/视频。
  - **超强压缩**: 内置 FFmpeg，自动优化大视频体积，支持 100MB+ 文件的秒级分析。
  - **时间对齐**: 压缩过程不损失任何时间戳精度，完美适配“分镜拆解”与“解说打轴”任务。
  - **建议**: 对于复杂项目，请明确指定使用 `gemini-3-pro`。

### 2. 专用视频分析 (Deep Video Analysis)
**指令**: "分析视频分镜: [视频路径]" / "拆解这个视频: [视频路径]"
- **执行**: `python scripts/video_analyzer.py "{VideoPath}"`
- **优势**: 自动从 `config.json` 加载端口，默认使用最强的 `gemini-3-pro` 模型，预设专业分镜分析 Prompt，输出格式规整。

### 2. 高清绘图 (Imagen 3 / banana)
**指令**: "用 banana 画一张..." / "生成一张 16:9 的高清图..."
- **执行**: `python scripts/generate_image.py "{Prompt}" "{Size/Ratio}" "{ReferenceImagePath}"`
- **参数**:
  - `Prompt`: 描述词
  - `Size`: 支持 `16:9`, `9:16`, `1:1` 等。
  - `ReferenceImagePath`: (可选) 本地图片绝对路径。如果提供，AI 将参考该图片进行创作。

### 3. 查看可用模型 (List Models)
**指令**: "查看所有模型" / "有什么模型可以用"
- **执行**: `python scripts/list_models.py`

## 注意事项
- 绘图默认开启 HD (4K) 质量。
- 图片保存在根目录 `generated_assets/`。
