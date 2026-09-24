# Venn / Set Overlap

**Best for:** intersection of concepts/domains, shared attributes between categories, "where A meets B", ikigai-style frames (desirable × feasible × viable).

## Layout conventions
- **Prefer 2 or 3 circles.** Avoid 4+ (unreadable — use a matrix instead).
- Circle stroke: 1px hairline, color per-set (ink, muted, soft).
- Circle fill: very low-opacity tint — `rgba(45,49,66,0.04)` for ink set, `rgba(79,93,117,0.05)` for muted. Tints compound naturally in overlap regions.
- Radii: equal when sets are comparable in size; proportional when sets are meaningfully different. Don't fake equal sizes for aesthetics.
- **Set labels** placed outside the circle, NEVER crossing the stroke. Geist 12–14px 600 for the set name, optional Geist Mono 9px sublabel.
- **Intersection labels** placed inside the overlap region, Geist 12px 600, centered. For small overlaps, use a leader line to a label in clear space.
- **Coral accent** on the ONE focal intersection — the "sweet spot". Either coral label stroke OR clipPath-bounded coral fill tint (`rgba(235,108,54,0.10)`).
- Circle centers and radii divisible by 4.

## 两圆间距（收紧规则）
两圆等半径 `r`、圆心距 `d`。交集是读者要看的「共享区」，**别把两圆推太开**——间距过大只剩一条缝，看不出「共享」的含义；想要「两边更聚拢」就收小 `d`。

- **取值**：`d ≈ 0.75–0.9 × 2r`（交集宽度约为单圆直径的 10–25%）。想让两边明显贴近取小值（约 `0.75 × 2r`）；想让交集只是一条窄缝（强调「各自为主、略有重叠」）取大值。
- **圆心对称**：两个圆心放在中垂线两侧，中点 x 取图区中线，`cx₁ = 中点 − d/2`、`cx₂ = 中点 + d/2`，`cy` 相同。这样交集弧线端点 x 恒等于中点。
- **交集弧线端点公式**（圆心连线水平时）：两圆交点在中垂线上，
  - `x = (cx₁ + cx₂) / 2`
  - `h = √(r² − (d/2)²)`
  - 上端点 `(x, cy − h)`，下端点 `(x, cy + h)`
  - 弧：`M x,(cy−h) A r,r 0 0,1 x,(cy+h)`（取右侧那段边界，sweep-flag = 1）。
- **独有区文字落位**：左圆独有项居中放在「仅左圆」区间（约 `cx₁` 与交点 x 之间），右圆同理；交集项居中放在 `x`（交点）上。移动圆心后这三处的 x 要同步重算，别让文字掉到圆外。
- 例：`r = 178`，想收紧取 `d = 160` → `h = √(178² − 80²) ≈ 159`，交点 `y = cy ± 159`，弧 `M x,(cy−159) A 178,178 0 0,1 x,(cy+159)`。

## Anti-patterns
- Unlabeled regions — reader can't tell which set is which.
- Circles that don't overlap when overlap is the point.
- Equal-sized circles when sets are obviously different (dishonest).
- Coral on multiple overlap regions (focal signal dies).
- Labels sitting on top of circle strokes (illegible).
- 4+ circles where 2–3 would do.

## Examples
- `assets/example-venn.html` — minimal light
- `assets/example-venn-dark.html` — minimal dark
- `assets/example-venn-full.html` — full editorial
