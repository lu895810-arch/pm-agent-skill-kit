#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch migrate custom Claude Code skills into WorkBuddy's skill directory.

Usage:
    python migrate.py <source-skills-root> [--dst <target-dir>]

Defaults (can be overridden with --dst):
    source = ~/.claude/skills
    dst    = ~/.workbuddy/skills
"""
import argparse
import os
import re
import shutil
import sys

DEFAULT_DST = os.path.expanduser("~/.workbuddy/skills")

# Non-deck skills without zh_name/en_name in their frontmatter
EXPLICIT_DISPLAY = {
    "ai-course-md-to-html": ("Markdown 转课程 HTML", "AI Course MD→HTML"),
    "cyx_research_report": ("数据溯源调研报告", "Research Report (CYX)"),
    "diagram-maker": ("图表生成器", "Diagram Maker"),
    "excalidraw-diagram": ("Excalidraw 手绘图表", "Excalidraw Diagram"),
    "ui-ux-pro-max": ("UI/UX 设计智能库", "UI/UX Pro Max"),
}

# Directory renames (remove Claude-branded suffixes)
DIR_RENAME = {
    "deck-obsidian-claude": "deck-obsidian",
}

# Files whose copyright/notice text must not be altered
PROTECTED_FILES = {"LICENSE", "LICENSE.txt", "NOTICE", "NOTICE.md", "COPYING"}

TEXT_EXTS = (
    ".md", ".py", ".js", ".css", ".html", ".json",
    ".txt", ".sh", ".xml", ".yaml", ".yml", ".toml", ".csv",
)


def rebrand_skill(text: str) -> str:
    """Full rebrand for SKILL.md (including install paths)."""
    text = re.sub(r'\.claude/', '.workbuddy/', text)
    text = re.sub(r'~/.claude\b', '~/.workbuddy', text)
    text = text.replace("Claude Code", "WorkBuddy")
    text = re.sub(r'[Cc]laude\.ai', "WorkBuddy", text)
    text = text.replace("Cowork", "WorkBuddy")
    text = re.sub(r'Anthropic', "WorkBuddy", text, flags=re.I)
    text = re.sub(r'\b[Cc]laude\b', "WorkBuddy", text)
    return text


def rebrand_readme(text: str) -> str:
    """Minimal rebrand for README.md: install paths + 'Claude Code' phrase only."""
    text = re.sub(r'\.claude/', '.workbuddy/', text)
    text = re.sub(r'~/.claude\b', '~/.workbuddy', text)
    text = text.replace("Claude Code", "WorkBuddy")
    return text


def split_frontmatter(content: str):
    m = re.match(r'^---\n(.*?)\n---\n', content, re.S)
    if not m:
        return None, content
    return m.group(1), content[m.end():]


def set_yaml_field(fm: str, key: str, value: str) -> str:
    if re.search(r'(?m)^\s*' + re.escape(key) + r'\s*:', fm):
        return fm
    return fm.rstrip() + f"\n{key}: {value}\n"


def strip_claude_from_name(name: str) -> str:
    name = re.sub(r'\s*Claude\b', '', name)
    name = re.sub(r'\bClaude\s*', '', name)
    return name.strip()


def extract_field(fm: str, key: str):
    pattern = r'(?m)^\s*' + re.escape(key) + r'\s*[:=]\s*"?([^"\n]+)"?\s*$'
    m = re.search(pattern, fm)
    return m.group(1).strip() if m else None


def normalize_lf(path: str):
    b = open(path, "rb").read()
    if b"\r\n" in b:
        open(path, "wb").write(b.replace(b"\r\n", b"\n"))


def main():
    parser = argparse.ArgumentParser(
        description="Migrate custom Claude Code skills to WorkBuddy"
    )
    parser.add_argument("src", help="Source skills root directory")
    parser.add_argument(
        "--dst",
        default=DEFAULT_DST,
        help=f"Target directory (default: {DEFAULT_DST})",
    )
    args = parser.parse_args()

    src = os.path.abspath(args.src)
    dst = os.path.abspath(args.dst)

    if not os.path.isdir(src):
        print(f"Source directory does not exist: {src}")
        sys.exit(1)
    os.makedirs(dst, exist_ok=True)

    count = 0
    for name in sorted(os.listdir(src)):
        sdir = os.path.join(src, name)
        if not os.path.isdir(sdir):
            continue

        tname = DIR_RENAME.get(name, name)
        ddir = os.path.join(dst, tname)
        if os.path.exists(ddir):
            shutil.rmtree(ddir)
        shutil.copytree(sdir, ddir)
        count += 1
        print(f"[copy] {name} -> {tname}")

        skill_path = os.path.join(ddir, "SKILL.md")
        if not os.path.exists(skill_path):
            print(f"   ! no SKILL.md, skipping transformation")
            continue

        c = open(skill_path, encoding="utf-8").read()
        fm, rest = split_frontmatter(c)
        if fm is None:
            print(f"   ! no frontmatter, skipping transformation")
            continue

        # Sync name field with directory name
        if tname != name:
            fm = re.sub(r'(?m)^(name:\s*).*$', r'\1' + tname, fm, count=1)

        # Rebrand frontmatter too (description may reference Claude)
        fm = rebrand_skill(fm)

        # Compute display names
        zh = extract_field(fm, "zh_name") or EXPLICIT_DISPLAY.get(tname, (tname, tname))[0]
        en = extract_field(fm, "en_name") or EXPLICIT_DISPLAY.get(tname, (tname, tname))[1]
        if tname != name:
            en = strip_claude_from_name(en)

        fm = set_yaml_field(fm, "agent_created", "true")
        fm = set_yaml_field(fm, 'display_name', f'"{zh}"')
        fm = set_yaml_field(fm, 'display_name_en', f'"{en}"')

        new_rest = rebrand_skill(rest)
        c = "---\n" + fm + "---\n" + new_rest
        open(skill_path, "w", encoding="utf-8").write(c)
        print(f"   [skill] agent_created + display_name({zh} / {en}) + rebrand")

        readme_path = os.path.join(ddir, "README.md")
        if os.path.exists(readme_path):
            rc = open(readme_path, encoding="utf-8").read()
            rc2 = rebrand_readme(rc)
            if rc2 != rc:
                open(readme_path, "w", encoding="utf-8").write(rc2)
                print(f"   [readme] install path / phrase rebrand")

    # Normalize line endings, skipping protected files
    for root, _, files in os.walk(dst):
        for fn in files:
            if fn in PROTECTED_FILES:
                continue
            if fn.lower().endswith(TEXT_EXTS):
                normalize_lf(os.path.join(root, fn))

    print(f"\nDone: {count} skill directory(s) migrated to {dst}")


if __name__ == "__main__":
    main()
