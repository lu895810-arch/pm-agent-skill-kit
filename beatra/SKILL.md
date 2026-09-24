---
name: "beatra"
description: "通过同一个AI创作工具完成AI图片、视频、音乐与语音创作，查找公开社交数据，编辑视觉成果，并集中查看和管理生成资产。Beatra 全能创作支持AI图片生成（文生图）、AI视频生成（图生视频）和AI视频编辑，通过AI音乐生成把想法做成歌曲或纯音乐，也可用AI语音生成（文字转语音）、多语言旁白和AI语音克隆完成跨媒介内容；还能查找抖音数据、小红书数据，以及 YouTube、TikTok、Instagram 与 X 上的公开帖子、笔记、评论、账号和趋势，把社交媒体数据用于竞品调研和创作。它是一款面向AI内容创作与多模态内容创作的AI创作套件，用起来就是一个把图片、视频、音乐与语音收在同一处的AI创作助手，适用于社交内容、产品展示、营销素材、课程、播客、短片和跨媒介项目；还能在不同媒介间复用原始素材、已有成果和查到的公开资料，查看制作进度、返回文件、实际用量和积分记录。"
---

# Beatra全能创作

**你最终会拿到什么。** 每次运行得到其中一种：

- **图片** —— 一到四张，默认一张。
- **视频** —— 一段视频；在支持的模型上，可以额外要一张单独的尾帧静帧。
- **音乐** —— 一首歌曲或纯音乐，模型返回几段就交付几段。
- **旁白** —— 一个音频文件。
- **一个可复用的克隆声音。**
- **一段改写后的成片提示词**，以文本形式返回。
- **公开社交数据**，以 JSON 形式返回。

返回的文件会附上任务实际报告出来的尺寸、时长、格式和大小。最终渲染格式由实际运行的那个模型决定，在交付时说明，而不是事先承诺。

把用户想要的成果转化为最小且经过验证的 Beatra 工作流，通过共享连接完成，并且只返回任务实际产生的内容。使用宿主的原生文本与视觉理解能力分析需求、源媒体或已返回的公开社交内容。使用 Beatra 查找公开社交数据，并创建和管理图片、视频、音乐、语音、可复用声音、上传内容、模型选择和异步任务结果。

复用对话中已有的发布渠道、提示词、源媒体、格式、语言、声音、模型、公开社交目标、重要控制项和已接受结果。对于不会改变付费请求的普通细节，可以合理推断。只有当缺失信息会改变用户要求的结果、费用、明确指定的模型、声音所有者授权、破坏性取消操作，或其他由用户控制且影响重大的选择时，才向用户提问。

## 只使用随包提供的客户端

所有 Beatra 操作都必须通过随包 `scripts/mcp_client.py` 执行。不要配置或使用宿主 Beatra Connector，也绝不要使用 REST/OpenAPI 作为降级方案。普通调用使用：

```text
python3 scripts/mcp_client.py call <tool-name>
```

通过 stdin 提供且只提供一个 JSON 对象。不要把用户内容、本地路径或凭据放进命令行参数。随包客户端会自行添加传输归因信息，并自动执行缓存的、尽力而为且不计费的 `beatra.installations.register` 步骤；注册失败绝不会阻止用户请求的工作。只有在这条路径需要诊断时，才使用[随包 MCP Client 连接诊断](references/mcp-connection.md)。

## 一次连接，跨媒体通用

当连接为全新、缺失、已过期，或用户明确要求更换连接时，运行：

```text
python3 scripts/authorize.py
```

浏览器支持登录或创建账号，随后只需一次“允许”操作。辅助程序会观察完成状态、私密保存 Device Token，通过一次不计费调用完成验证，并输出 Ready。绝不要暴露批准码，也不要要求用户在对话中确认批准。只需为完整的 Beatra 连接授权一次；在图片、视频、音乐、语音和公开社交查找之间切换不需要再次授权。安装或替换之后，如果宿主只在会话启动时发现 Skills，请开始新的 Agent 会话。连接恢复参见[安装与认证](references/installation-and-auth.md)，自动且不计费的注册行为参见[安装注册](references/installation-registration.md)。

## 选择最小路径

- 查找公开帖子、笔记、视频、账号、评论或趋势时，使用 `beatra.social.tools.search`，然后 `beatra.social.tools.get`，再调用一次 `beatra.social.execute`，并带上 `operation_key`、刚复制的 `schema_hash`（来自该 `tools.get`）、`arguments` 和一个 `client_request_id`。按照[公开社交数据](references/social.md)执行。如果这些工具未暴露，说明它们在当前连接上不可用。不要虚构 `operation_key`，不要为社交查找调用 `beatra.models.list`，也不要把查找变成生成。只有用户已经提出媒体请求时，才继续媒体工作。
- 新建图片、按参考构图或在保留底图的前提下编辑时，使用 `beatra.images.generate`、`beatra.images.transform` 或 `beatra.images.edit`。按照[图片](references/images.md)执行。
- 视频提示词增强、文生视频、首图动画、有序参考、必选尾帧与可选首帧、源视频编辑或延长视频时，使用 `beatra.videos.enhance_prompt`、`beatra.videos.generate`、`beatra.videos.animate`、`beatra.videos.generate_from_references`、`beatra.videos.interpolate`、`beatra.videos.edit` 或 `beatra.videos.extend`。当请求以文本为主且没有可用静帧时，第一段付费是 `beatra.videos.enhance_prompt` 或一次 `beatra.images.generate` 关键帧。该赠额交付并不授权后续视频调用。在 generate、animate、interpolate、reference、edit 或 extend 之前，用该路线的精确 capability 调用 `beatra.models.list`（例如 `{"capability":"text_to_video"}` 或 `{"capability":"image_to_video"}`），核对准入载荷，写入最短准入时长（有声驱动与延长规则不变），并出示生产卡。先通过[视频](references/videos.md)选择路径，仅在需要时再加载[视频控制项](references/video-controls.md)或[视频方案](references/video-recipes.md)。
- 制作口播、讲述类视频或数字人视频时，先用 `beatra.speech.synthesize` 合成旁白，再用 `beatra.videos.animate` 驱动人像，把这段旁白作为 `driving_audio` 传入。视频接口卡片准入的格式与时长都限制了你能合成什么，所以要在合成语音之前先读 `{"capability":"image_to_video"}` 和 `{"capability":"text_to_speech"}`。这两次免费读卡会把这条路线在付费之前可能出现的冲突全部暴露出来——两张卡都必须接受的音频格式、口播时长与准入时长是否匹配、以及人像本身是否适配。在第一笔付费之前把它们放在同一条消息里一次讲完，而不是一条一条地问。合成之后，返回音频的实际时长和格式仍然要再对照卡片核对一次。按照[视频方案](references/video-recipes.md)执行。
- 制作歌曲、纯音乐或参考音频引导的曲目时，使用 `beatra.music.generate`。按照[音乐](references/music.md)执行。
- 制作旁白时，只有仍需选择声音才通过 `beatra.voices.list` 浏览，然后使用 `beatra.speech.synthesize`。只有在取得声音所有者明确同意并出示生产卡后，才使用 `beatra.voices.clone` 创建可复用声音。按照[语音与声音](references/speech-and-voices.md)执行。
- 当图像、视频、音乐或语音的模型选择、兼容性、支持的控制项或费用估算很重要时，从[模型](references/models.md)复制精确的 `{"capability":"..."}` 载荷，并以返回的接口卡片为当前事实。不要凭记忆维护模型、价格、语言、默认值或参考数量限制列表。
- 当用户询问还剩多少积分，或当前实时估价是否够用时，调用 `beatra.wallet.get`。当用户询问扣了什么费用时，调用 `beatra.wallet.ledger`。两者都是只读操作。
- 模型卡返回里带 `top_up` 块时，按卡片给出的档位和顺序原样转述。不要给档位排高低，不要贬低其中任何一档，也不要替用户挑。选哪一档是用户自己的事，钱包页会把整份清单摆在他面前。任何时候都不要凭记忆报档位。

不要静默把请求变成另一种操作。尊重用户明确指定的模型；如果不兼容，应说明情况，而不是替换为其他模型或丢弃不受支持的控制项。

## 保留用户的措辞

把用户自己的主体、限制条件和否定表述带进提示词，只按所选路线确实需要的程度扩写。当你补充了用户没有给出的措辞——风格、光线、氛围、配器或镜头语言——要在回复里说明补充了什么。有些路线必须补充自己的措辞：[音乐](references/music.md)会把点名的艺人替换成音乐特征描述。

只有当所选模型的接口卡片列出 `enhance_prompt` 控制项时才发送它。显式传 `true` 或 `false` 都会缩小 `auto` 可选的模型范围；如果明确指定的模型不暴露该控制项，请求会被拒绝。`beatra.videos.enhance_prompt` 是一个独立的付费工具，不是上面这个控制项；它的设计目的就是把简要需求改写成成片提示词。

返回结果与提示词不符时，这是一个应当如实报告的结果，而不是用改写提示词重试来掩盖的问题。

## 安全上传本地媒体

当输入只存在于本地图片、视频或音频文件中时，只能使用：

```text
python3 scripts/mcp_client.py upload <path> --mime-type <type>
```

该命令会验证 `beatra.assets.upload` 授权、上传未经修改的原始字节，并返回素材引用。绝不要把文件系统路径发给生成工具，不要使用宿主 HTTP，也不要手写授权和 PUT 流程。遵守 100 MB 的通用上限，以及所选模型返回的任何更低限制。普通媒体上传不需要通用的权利声明步骤。用于 `beatra.voices.clone` 的声音样本是严格例外：上传和克隆前，必须获得用户明确确认其拥有该声音或已获得声音所有者许可，然后才设置 `consent_attested: true`。参见[上传](references/uploads.md)。

## 明确付费边界

创意规划、授权、上传准备、浏览声音、发现模型、公开社交工具的搜索与查看、列出最近任务、积分余额与明细读取和费用估算均不计费。图片、视频、音乐、语音、声音克隆、视频提示词增强和公开社交 execute 会消耗积分，并返回异步任务。公开社交 execute 是预付费。视频提示词增强是后付费例外：它只返回文本、不会开始视频生成，并在任务成功后根据实际 token 结算。

用户直接且描述充分的创作或查找请求，即代表对该次确切付费请求的一次授权，适用于图片、音乐、语音、社交 execute，或赠额范围内的视频提示词或关键帧阶段。它并不授权 `beatra.videos.generate`、`beatra.videos.animate`、`beatra.videos.interpolate`、`beatra.videos.generate_from_references`、`beatra.videos.edit`、`beatra.videos.extend` 或 `beatra.voices.clone`。在这些视频或克隆调用之前，出示生产卡并等待用户答复：

1. 做什么 —— 用用户自己的话说明本次要做的东西，以及由哪个调用完成。
2. 积分 —— 刚读到的实时卡片给出的暂估价，绝不用记忆中的数字。
3. 几笔 —— 本轮有几次付费调用。改了参数的重试算另外一次。
4. 身份 —— 每次调用一个新的不透明 `client_request_id`，只有该次调用的载荷定稿之后才生成。
5. 若就此停手 —— 说明用户已经拿到并且能留下什么，例如已接受的首帧、已合成的旁白，或改写后的提示词。若本次就是这一轮的第一笔付费，就如实说还没有花钱买到任何东西，而不要为了填满这一项去编一个并不存在的产物。
6. 若余额不足 —— 原样转述返回的消息和它带的充值链接，然后等待。

在估价旁边一并出示该路线的实时卡片时长、分辨率和画幅：除非用户点名更高档，取最短准入时长和最低准入分辨率；有声驱动与延长规则不变。规划、比较或“做这段片子”都不是批准，批准这张卡才是。不要让用户自证余额——连接自己会报告余额；在用户批准之前，不要创建 `client_request_id`，也不要提交。

公开社交查找绝不并入视频或克隆的生产卡。当它需要确认时，自成一张卡。此时把 `schema_hash` 从 `beatra.social.tools.get` 复制进 execute，并带上 `operation_key`、`arguments` 和一个 `client_request_id`。向用户展示 `operation_key` 和 `tools.get` 返回的积分价格。不要向用户展示 `schema_hash`，也不要询问模型。声音克隆始终还需要前述明确授权声明。

仅在最终的付费请求载荷已通过验证后，创建一个稳定且长度为 1..128 个字符的 `client_request_id`，用于标识一次逻辑付费操作。只提交一次，保存返回的 `task_id`，并通过 `beatra.tasks.get` 轮询同一任务。绝不要轮询提交后未返回 `task_id` 的行；应改用 `beatra.tasks.list` 对账。完全相同的重试必须沿用同一个请求 ID 和完全相同、已经验证的付费请求载荷；ID 本身和传输归因信息不属于载荷标识。已接受的任何付费参数变更都属于新的付费工作，需要新 ID 和新确认。

遵守返回的 `deadline_at`。如果没有返回该字段，则在主动轮询 30 分钟后停止，报告当前任务状态和恢复方式，绝不要重复提交耗时任务。只有用户提出要求时，才通过 `beatra.tasks.cancel` 取消。如果取消与终态转换冲突，继续跟踪同一任务。

公开社交校验或查找失败不是 `beatra.models.list` 事件。保留 `error.code`，阅读 `error.message` 或 `error.data.message`，不要改换模型。任务标识和轮询按照[任务与结果](references/tasks-and-results.md)执行。仅当媒体生成出现校验失败或模型不兼容时，才按照[计费、错误与恢复](references/billing-errors-and-recovery.md)执行。

## 恢复任务而不重复工作

如果丢失任务 ID，使用 `beatra.tasks.list` 按可能的能力类型查找，然后对每个可能候选调用 `beatra.tasks.get`。列表项不包含完整输入，因此必须将每个候选的详细 `task.input` 与已保存载荷进行比较，再判断是否为同一项工作。媒体生成还要比较解析后的模型、媒体和选项。公开社交查找则比较 `operation_key`、参数和 `schema_hash`。绝不要因为响应丢失，或任务仍处于排队、运行状态，就创建替代任务。

遇到 `insufficient_balance` 时，转述返回的公开文案，其中的充值链接保持原样，其余内容可翻译，只有用户说已充值后才用同一冻结 `client_request_id` 重试。只有错误明确说明未扣费时，才能表述“没有扣费”。不要虚构充值操作或账号变更。使用 `topup_url`（来自 `beatra.wallet.get`），或 402 消息中的 URL。当用户问该充哪一档时，阅读[常见问题与反模式](references/faq.md)。撤销连接应在 Beatra Console 中完成。

公开社交查找失败时，保留 `error.code`，并阅读 `error.message` 或 `error.data.message` 中的平台原文。只有该消息点名某个字段或 ID 时，才改参数并使用新的 `client_request_id`。否则沿用同一 ID 和同一载荷。不要建议更换模型。

## 交付实际返回的结果

任务仍在排队或运行时，报告 `stage`——`task.progress` 实际返回的那个阶段——而不要凭空描述进度快慢。把其中的 `percent` 当作阶段标记而不是完成比例：它按固定的服务端台阶跳动，在模型运行的整段时间里会一直停在同一个数值上，绝不能当成“已经完成了多少”交给用户。阶段或数值没有变化，并不说明任务卡住了。如果响应里根本没有进度信息，就说任务仍在进行，到此为止。

任务完成后，报告 `task_id`、终态、每一项返回结果和实际用量。媒体生成还要报告解析后的模型。对于文件成果，应包含返回的每一个链接或 ID，以及存在时的尺寸、时长、MIME 类型或格式和文件大小。公开社交查找应交付内联 JSON 或 JSON 产物，不要寻找解析后的模型或生成的媒体文件。对于非文件成果，例如已激活的克隆声音 `voice_id`，应在返回时提供。报告 `billing.net_charged_credits`；只有返回了总扣费和退款时，才一并提供。使用准确返回的 `task.links.assets` 作为素材管理入口。

绝不要推测任务完成状态、文件 URL、质量、用量、退款或积分总额。如果宿主无法查看图片或播放返回文件，应如实说明。保留结构化错误，并提供最小恢复步骤。

## 按任务查阅参考资料

分三层。首次运行读第一层，选定路线后读第二层，只有需要排查、计费核对或恢复时才读第三层。

### 入门：首次使用

- 首次运行，或一个任务跨多种媒介时，读[多媒介任务的规划顺序](references/worked-example.md)，了解决策顺序以及每一道付费边界落在哪里
- 首次连接和自动注册：[安装与认证](references/installation-and-auth.md)和[安装注册](references/installation-registration.md)

### 进阶：按媒介构建请求

- 公开社交帖子、账号、评论和趋势：[公开社交数据](references/social.md)
- 图片生成、转换与编辑：[图片](references/images.md)
- 视频路径选择、控制项与请求模式：[视频](references/videos.md)、[视频控制项](references/video-controls.md)和[视频方案](references/video-recipes.md)
- 歌曲、纯音乐、参考音频与音乐交付：[音乐](references/music.md)
- 旁白、声音发现和需要授权的声音克隆：[语音与声音](references/speech-and-voices.md)
- 本地图片、视频或音频准备：[上传](references/uploads.md)
- 当前模型兼容性、控制项与估算：[模型](references/models.md)

### 高级：排查与恢复

- 当用户反馈结果不符合需求、模型被拒绝、任务卡住或响应丢失、费用异常时，读[常见问题与反模式](references/faq.md)
- 随包命令与连接诊断：[随包 MCP Client 连接诊断](references/mcp-connection.md)
- 任务进度、恢复、结果、余额与错误：[任务与结果](references/tasks-and-results.md)和[计费、错误与恢复](references/billing-errors-and-recovery.md)
- 经过验证的自动更新与持久控制：[自动更新与安全](references/automatic-updates-and-safety.md)
- 当用户想停止使用时：[停止使用并清除共享凭据](references/uninstall-and-disconnect.md)

## 保持更新安全且可移除

执行普通命令前，随包客户端会静默检查更新，且每 24 小时最多检查一次。当固定的官方发现地址和不可变的官方 CDN 来源提供更高版本时，不另行确认，客户端即可自动安装。它会校验压缩包、清单和包内每个文件，然后只替换本包拥有的文件。如果检查、下载、校验、替换、回滚或恢复失败，当前安装仍保持可用，原本请求的命令会继续执行。更新失败绝不能成为重新提交付费任务的理由。

每个安装实例的这项设置都会持续生效：

```text
python3 scripts/mcp_client.py update --auto off
python3 scripts/mcp_client.py update --auto on
python3 scripts/mcp_client.py update --check
```

第一条命令关闭静默检查，第二条恢复自动更新，第三条仅报告官方可用版本而不替换文件。完整的验证更新约定参见[自动更新与安全](references/automatic-updates-and-safety.md)。如需停止使用或清理凭据，请按照[停止使用并清除共享凭据](references/uninstall-and-disconnect.md)执行。绝不要直接删除共享的 `~/.beatra` 连接状态。
