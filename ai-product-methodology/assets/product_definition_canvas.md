# AI 产品定义画布

> 用途：从 0 到 1 定义一款 AI 产品的标准交付物。逐项填写；无法手动填写的项标注「待验证」。
> 可用 `scripts/build_canvas.py` 以 JSON 批量填充本模板中的 `{{KEY}}` 占位符；缺失字段会渲染为 `[待填写]`。

## 1. 一句话定义
- 产品名：{{PRODUCT_NAME}}
- 一句话：{{ONE_LINER}}

## 2. 机会与背景
- 为什么是现在：{{WHY_NOW}}
- 为什么是我们：{{WHY_US}}

## 3. 目标用户与问题（JTBD）
- 目标用户：{{TARGET_USER}}
- JTBD：当用户处于 {{JTBD_CONTEXT}}，想达成 {{JTBD_OUTCOME}}，以便 {{JTBD_GAIN}}。
- 当前凑合方案：{{CURRENT_WORKAROUND}}
- 问题证据：{{PROBLEM_EVIDENCE}}

## 4. 价值主张
- 一句话价值：{{VALUE_PROP}}
- 缓解的痛点：{{PAIN_RELIEF}}
- 创造的收益：{{GAIN_CREATED}}
- Kano 分层：基本 {{KANO_BASIC}} / 期望 {{KANO_EXPECTED}} / 兴奋 {{KANO_EXCITED}}

## 5. 差异化定位与竞品
- 竞品对比：{{COMPETITORS}}
- 定位声明：对于 {{POS_TARGET_USER}}，当 {{POS_CONTEXT}}，我们的产品是 {{POS_CATEGORY}} 中唯一能 {{POS_DIFF}} 的，因为 {{POS_PROOF}}。
- 护城河：{{MOAT}}

## 6. 市场机会
- TAM：{{MARKET_TAM}}
- SAM：{{MARKET_SAM}}
- SOM：{{MARKET_SOM}}
- 关键假设：{{MARKET_ASSUMPTIONS}}

## 7. 方案与 MVP 边界
- 人机协作模式：{{HUMAN_AI_MODE}}
- 技术路径：{{TECH_APPROACH}}
- MVP 范围（做）：{{MVP_IN}}
- 明确不做：{{MVP_OUT}}

## 8. 指标
- 北极星指标：{{NORTH_STAR}}
- AARRR：获取 {{AARRR_A}} / 激活 {{AARRR_B}} / 留存 {{AARRR_C}} / 营收 {{AARRR_D}} / 推荐 {{AARRR_E}}
- 激活 Aha 时刻：{{AHA}}

## 9. 评测与护栏
- 评测维度与门槛：{{EVAL}}
- 护栏策略：{{GUARDRAILS}}
- 上线标准：{{LAUNCH_CRITERIA}}

## 10. 核心风险与待验证假设
- 最大风险：{{TOP_RISK}}
- 最该先验证的假设：{{KEY_ASSUMPTION}}
