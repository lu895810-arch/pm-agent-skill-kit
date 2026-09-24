# GitHub 开源调研关键词库

通用关键词模板，供 Step 3 挑选组合。使用时应结合目标产品补充该方向特有的词。

## 通用搜索词（对任何产品类型都适用）

| 类型 | 中文 | 英文 |
|---|---|---|
| 直接名称 | `{产品} 开源`、`{产品} 源码` | `{product} open source` |
| 找整站 | `{产品} 系统`、`{产品} 平台` | `{product} platform`、`{product} app` |
| 找仿品参考 | `{产品} clone`、`仿{产品}` | `{product} clone`、`{product} like` |
| 找小程序版 | `{产品} 小程序` | `{product} mini program`、`{product} wechat` |
| 找后台 | `{产品} 后台`、`{产品} 管理` | `{product} admin`、`{product} cms` |

## 常见模块词（按需组合"模块 + 技术栈"）

| 模块 | 中文 | 英文 |
|---|---|---|
| 播放器 | `播放器`、`竖屏播放`、`滑动播放` | `video player`、`hls player`、`m3u8 player`、`vertical video swipe` |
| 客户端 | `小程序`、`h5`、`uniapp` | `mini program`、`flutter`、`react native`、`PWA` |
| 商业化 | `付费解锁`、`订阅`、`会员`、`虚拟币`、`分销`、`CPS` | `paywall`、`subscription`、`membership`、`coin wallet`、`affiliate` |
| 点播/存储 | `点播`、`视频存储` | `VOD`、`video on demand`、`signed url`、`CDN` |
| 账号体系 | `登录`、`用户体系` | `auth`、`oauth`、`user system` |
| 搜索推荐 | `推荐`、`搜索` | `recommendation`、`search` |
| 内容生产 | `{产品} 生成`、`AI{产品}` | `{product} generator`、`ai {product}` |

## 关键技巧

1. **英文优先用行业习语**：如 `short drama` 的正规说法是 `micro drama`、`mini drama`；DramaBox 是标杆产品名，`dramabox clone` 能搜到大量白标参考。
2. **中文源码多在 Gitee**：整站/分销/小程序类中文"开源"，很多实际托管在 Gitee 而非 GitHub，搜索时两者都查。
3. **商业化类仓库要警惕授权**：`CPS`、`分销`、`白标`、`clone` 类源码，"仅学习用、商用需购买"非常常见，交付时必须标注。
4. **技术栈限定**：同一个模块，加 `flutter` / `react native` / `uniapp` 会得到完全不同的结果，按你的客户端技术栈分别搜。
5. **star 数筛选**：>1k star 通常是社区验证过的稳定组件；小项目 star 少但可能更贴你的具体场景，两者都值得看。
6. **用 GitHub 连接器按 star 排序**：`mcp__github__search_repositories` 支持 `sort: stars`，直接拿到高星候选，比网页搜索摘要更准；中文整站搜不到时再补 Gitee 一轮。
