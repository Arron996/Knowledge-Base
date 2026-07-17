#!/usr/bin/env python3
"""Roll 明日待办 / 待排期 from source Daily into target Daily 今日计划 / 待排期."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
WEEKDAY_ZH = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

SECTION_TOMORROW = "## 📋 明日待办"
SECTION_TODAY = "## 📋 今日计划"
SECTION_BACKLOG = "## 🗂️ 待排期"


def daily_path(day: date) -> Path:
    return VAULT_ROOT / "Daily" / f"{day.isoformat()}.md"


def extract_section(content: str, heading: str) -> str | None:
    pattern = rf"^{re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    m = re.search(pattern, content, flags=re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else None


def checkbox_lines(body: str | None, unchecked_only: bool = True) -> list[str]:
    if not body:
        return []
    lines: list[str] = []
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("- ["):
            continue
        if unchecked_only and s.startswith("- [x]"):
            continue
        if "<!-- agent:" in s:
            continue
        lines.append(s)
    return lines


def normalize_item(line: str) -> str:
    return re.sub(r"^\-\s*\[[ xX]\]\s*", "", line).strip()


def merge_checkbox_lists(existing: list[str], incoming: list[str]) -> list[str]:
    seen = {normalize_item(x) for x in existing}
    out = list(existing)
    for line in incoming:
        key = normalize_item(line)
        if key and key not in seen:
            out.append(line)
            seen.add(key)
    return out


def upsert_section(content: str, heading: str, body_lines: list[str]) -> str:
    body = "\n".join(body_lines)
    if body:
        block = f"{heading}\n\n{body}\n\n"
    else:
        block = f"{heading}\n\n"

    pattern = rf"^{re.escape(heading)}\s*\n.*?(?=^## |\Z)"
    if re.search(pattern, content, flags=re.MULTILINE | re.DOTALL):
        return re.sub(pattern, block, content, count=1, flags=re.MULTILINE | re.DOTALL)

    # Insert before 明日待办, else before 待排期, else before 参考
    for anchor in (SECTION_TOMORROW, SECTION_BACKLOG, "## 📎 参考"):
        idx = content.find(anchor)
        if idx != -1:
            return content[:idx] + block + "\n" + content[idx:]

    return content.rstrip() + "\n\n" + block


def load_template(target: date) -> str:
    tpl = (VAULT_ROOT / "Templates" / "daily-note.md").read_text(encoding="utf-8")
    wd = WEEKDAY_ZH[target.weekday()]
    return (
        tpl.replace("{{date:YYYY-MM-DD}}", target.isoformat())
        .replace("{{date:dddd}}", wd)
    )


def ensure_daily(target: date) -> tuple[Path, str, bool]:
    path = daily_path(target)
    if path.exists():
        return path, path.read_text(encoding="utf-8"), False
    return path, load_template(target), True


def roll(source: date, target: date) -> None:
    src_path = daily_path(source)
    if not src_path.exists():
        print(f"WARNING: source Daily missing: {src_path}", file=sys.stderr)
        raise SystemExit(3)

    src = src_path.read_text(encoding="utf-8")
    todo_in = checkbox_lines(extract_section(src, SECTION_TOMORROW))
    backlog_in = checkbox_lines(extract_section(src, SECTION_BACKLOG))

    tgt_path, content, created = ensure_daily(target)

    existing_today = checkbox_lines(extract_section(content, SECTION_TODAY), unchecked_only=False)
    merged_today = merge_checkbox_lists(existing_today, todo_in)
    content = upsert_section(content, SECTION_TODAY, merged_today)

    existing_backlog = checkbox_lines(extract_section(content, SECTION_BACKLOG), unchecked_only=False)
    merged_backlog = merge_checkbox_lists(existing_backlog, backlog_in)
    content = upsert_section(content, SECTION_BACKLOG, merged_backlog)

    # New daily notes come from a template containing placeholder checkboxes.
    # Normalize untouched sections once so placeholders do not leak into later merges.
    existing_tomorrow = checkbox_lines(extract_section(content, SECTION_TOMORROW), unchecked_only=False)
    content = upsert_section(content, SECTION_TOMORROW, existing_tomorrow)

    tgt_path.parent.mkdir(parents=True, exist_ok=True)
    tgt_path.write_text(content, encoding="utf-8")
    action = "created" if created else "updated"
    print(f"{action} {tgt_path.name}: {len(merged_today)} 今日计划, {len(merged_backlog)} 待排期 (from {source.isoformat()})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", dest="source", required=True, metavar="YYYY-MM-DD")
    parser.add_argument("--to", dest="target", required=True, metavar="YYYY-MM-DD")
    args = parser.parse_args()
    roll(date.fromisoformat(args.source), date.fromisoformat(args.target))


if __name__ == "__main__":
    main()
