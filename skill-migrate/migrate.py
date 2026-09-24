#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用技能迁移脚本：将 Anthropic 官方格式的 SKILL.md 技能改造并安装到 WorkBuddy。

用法:
    python migrate.py <源技能根目录> [--dst C:/Users/admin/.workbuddy/skills]

<源技能根目录> 下每个子目录被视为一个待迁移的技能。
脚本会：拷贝整目录、重命名 Claude/Anthropic -> WorkBuddy、补元数据、规范换行符。
对 claude-api / academy-guide / brand-guidelines 按语境化规则特殊处理。
"""
import os, re, sys, shutil

DEFAULT_DST = "C:/Users/admin/.workbuddy/skills"

# 通用技能 -> (中文显示名, 英文显示名)
DISPLAY_NAMES = {
    "algorithmic-art": ("算法艺术", "Algorithmic Art"),
    "canvas-design": ("画布设计", "Canvas Design"),
    "discernment-nudge": ("审慎追问", "Discernment Nudge"),
    "doc-coauthoring": ("文档协作", "Doc Coauthoring"),
    "docx": ("Word 文档", "DOCX"),
    "frontend-design": ("前端设计", "Frontend Design"),
    "internal-comms": ("内部沟通", "Internal Comms"),
    "mcp-builder": ("MCP 构建", "MCP Builder"),
    "pdf": ("PDF 处理", "PDF"),
    "pptx": ("PPT 演示", "PPTX"),
    "skill-creator": ("技能创建", "Skill Creator"),
    "slack-gif-creator": ("Slack GIF 制作", "Slack GIF Creator"),
    "theme-factory": ("主题工厂", "Theme Factory"),
    "web-artifacts-builder": ("Web 构件", "Web Artifacts Builder"),
    "webapp-testing": ("Web 应用测试", "WebApp Testing"),
    "xlsx": ("表格处理", "XLSX"),
}

# 设计类技能：模板/资源文件里的 Anthropic 品牌也要重命名
REBRAND_ASSET_SKILLS = ["algorithmic-art", "canvas-design"]

TEXT_EXTS = (".md", ".py", ".js", ".css", ".html", ".json",
             ".txt", ".sh", ".xml", ".yaml", ".yml", ".toml")


def rebrand(text: str) -> str:
    text = text.replace("Claude Code", "WorkBuddy")
    text = re.sub(r'[Cc]laude\.ai', "WorkBuddy", text)
    text = text.replace("Cowork", "WorkBuddy")
    text = re.sub(r'Anthropic', "WorkBuddy", text, flags=re.I)
    text = re.sub(r'\b[Cc]laude\b', "WorkBuddy", text)
    return text


def add_frontmatter(content: str, dn_zh: str, dn_en: str) -> str:
    m = re.match(r'^---\n(.*?)\n---\n', content, re.S)
    if not m:
        return content
    fm, rest = m.group(1), content[m.end():]
    keys = []
    if "agent_created:" not in fm:
        keys.append("agent_created: true")
    if "display_name:" not in fm:
        keys.append(f'display_name: "{dn_zh}"')
    if "display_name_en:" not in fm:
        keys.append(f'display_name_en: "{dn_en}"')
    if keys:
        fm = fm + "\n" + "\n".join(keys) + "\n"
        return "---\n" + fm + "---\n" + rest
    return content


def normalize_lf(path: str):
    b = open(path, "rb").read()
    if b"\r\n" in b:
        open(path, "wb").write(b.replace(b"\r\n", b"\n"))


def main():
    if len(sys.argv) < 2:
        print("用法: python migrate.py <源技能根目录> [--dst <目标目录>]")
        sys.exit(1)
    src = sys.argv[1]
    dst = DEFAULT_DST
    if "--dst" in sys.argv:
        dst = sys.argv[sys.argv.index("--dst") + 1]

    for name in sorted(os.listdir(src)):
        sdir = os.path.join(src, name)
        if not os.path.isdir(sdir) or name == "LICENSE.txt":
            continue
        ddir = os.path.join(dst, name)
        shutil.copytree(sdir, ddir, dirs_exist_ok=True)
        print(f"已拷贝 {name}")

        skill = os.path.join(ddir, "SKILL.md")
        if not os.path.exists(skill):
            continue
        c = open(skill, encoding="utf-8").read()

        if name == "claude-api":
            # Anthropic API 参考：保留正文，只补元数据
            c = add_frontmatter(c, "Claude API 参考", "Claude API Reference")
            open(skill, "w", encoding="utf-8").write(c)
            print(f"  元数据已补 (正文保留 API 参考): {name}")
        elif name == "brand-guidelines":
            c = add_frontmatter(c, "品牌规范", "Brand Guidelines")
            c = c.replace("Anthropic", "WorkBuddy")
            c = c.replace("# WorkBuddy Brand Styling", "# WorkBuddy 品牌规范")
            c = c.rstrip() + ("\n\n## 注意\n本技能默认提供一套中性参考色板与字体方案，便于快速套用统一视觉风格。"
                              "若需严格对齐 WorkBuddy 官方品牌，请将上方色值、字体替换为官方设计系统中的规范资产。\n")
            open(skill, "w", encoding="utf-8").write(c)
            print(f"  已重命名为 WorkBuddy 品牌规范: {name}")
        elif name == "academy-guide":
            # 重写为 WorkBuddy 学习指南（见 SKILL.md 同目录的 learning-guide 范本）
            print(f"  跳过自动处理，请手动重写为 learning-guide（指向 workbuddy.cn/docs）: {name}")
        else:
            dn_zh, dn_en = DISPLAY_NAMES.get(name, (name, name))
            c = add_frontmatter(c, dn_zh, dn_en)
            c = rebrand(c)
            open(skill, "w", encoding="utf-8").write(c)
            print(f"  已重命名 + 补元数据: {name}")

        # 设计类技能：模板/资源文件一并重命名
        if name in REBRAND_ASSET_SKILLS:
            for dp, _, files in os.walk(ddir):
                for fn in files:
                    if fn.lower().endswith(TEXT_EXTS) and fn != "LICENSE.txt":
                        fp = os.path.join(dp, fn)
                        try:
                            t = open(fp, encoding="utf-8").read()
                        except Exception:
                            continue
                        if re.search(r'[Cc]laude|Anthropic', t):
                            t2 = rebrand(t)
                            if t2 != t:
                                open(fp, "w", encoding="utf-8").write(t2)

        # 规范换行符
        for dp, _, files in os.walk(ddir):
            for fn in files:
                if fn.lower().endswith(TEXT_EXTS):
                    normalize_lf(os.path.join(dp, fn))

    print("迁移完成。")


if __name__ == "__main__":
    main()
