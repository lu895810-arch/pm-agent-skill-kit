#!/usr/bin/env python3
"""
build_canvas.py —— AI 产品定义画布生成器

从 JSON 数据批量填充 assets/product_definition_canvas.md 中的 {{KEY}} 占位符，
产出一份可直接交付的产品定义画布 Markdown。目标字段缺失时保留 [待填写] 提示。

用法：
    python build_canvas.py --data data.json --out canvas.md
    python build_canvas.py --data data.json                # 输出到 stdout

参数：
    --template   画布模板路径（默认：脚本同级的 ../assets/product_definition_canvas.md）
    --data       JSON 数据文件路径，键需与模板 {{KEY}} 对应（大写）
    --out        输出 Markdown 路径（省略则打印到 stdout）

JSON 示例：
{
  "PRODUCT_NAME": "智能周报助手",
  "ONE_LINER": "把零散工作记录自动生成结构化周报",
  "NORTH_STAR": "成功生成的周报数"
}
"""
import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def render(template: str, data: dict) -> str:
    """将模板中的 {{KEY}} 用 data 中的值替换；缺失项标记为 [待填写]。"""
    def repl(match: re.Match) -> str:
        key = match.group(1)
        value = data.get(key)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return "[待填写]"
        return str(value)

    return PLACEHOLDER_RE.sub(repl, template)


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    default_template = script_dir.parent / "assets" / "product_definition_canvas.md"

    parser = argparse.ArgumentParser(description="AI 产品定义画布生成器")
    parser.add_argument("--template", default=str(default_template),
                        help="画布模板路径（默认 assets/product_definition_canvas.md）")
    parser.add_argument("--data", required=True, help="JSON 数据文件路径")
    parser.add_argument("--out", default=None, help="输出 Markdown 路径（省略则 stdout）")
    args = parser.parse_args()

    template_path = Path(args.template)
    if not template_path.exists():
        print(f"错误：模板不存在 - {template_path}", file=sys.stderr)
        return 1

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"错误：数据文件不存在 - {data_path}", file=sys.stderr)
        return 1

    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"错误：JSON 解析失败 - {e}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print("错误：JSON 顶层必须为对象（键=占位符名，值=内容）", file=sys.stderr)
        return 1

    template = template_path.read_text(encoding="utf-8")
    output = render(template, data)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"已生成画布：{out_path}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
