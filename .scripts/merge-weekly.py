#!/usr/bin/env python3
"""Merge Daily notes into Weekly (Friday morning, Mon..Thu). Pure Python, no SDK."""

from __future__ import annotations

import argparse
import re
from datetime import date, timedelta
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent


def iso_week_label(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def daily_path(day: date) -> Path:
    return VAULT_ROOT / "Daily" / f"{day.isoformat()}.md"


def weekly_path(week: str) -> Path:
    return VAULT_ROOT / "Weekly" / f"{week}.md"


def extract_section(content: str, heading: str) -> str | None:
    pattern = rf"^{re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    m = re.search(pattern, content, flags=re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else None


def extract_headline(content: str) -> str | None:
    m = re.search(r"> \[!abstract\] 今日主线\s*\n>\s*(.+)", content)
    return m.group(1).strip() if m else None


def extract_progress_block(content: str) -> str | None:
    return extract_section(content, "## 📊 技改进展")


def extract_callouts(progress: str) -> list[tuple[str, str]]:
    """Return list of (title, full_callout_block)."""
    pattern = r"(> \[!\w+\]-[^\n]*(?:\n(?:>.*|\n(?!\s*> \[!)))*)"
    blocks: list[tuple[str, str]] = []
    for m in re.finditer(pattern, progress, flags=re.MULTILINE):
        block = m.group(1).strip()
        title_m = re.match(r"> \[!\w+\]-\s*(.+)", block)
        title = title_m.group(1).strip() if title_m else block[:60]
        blocks.append((title, block))
    return blocks


def todo_lines(body: str | None) -> list[str]:
    if not body:
        return []
    out: list[str] = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("- [ ]"):
            out.append(re.sub(r"^\-\s*\[\s\]\s*", "", s).strip())
    return out


def merge_week(anchor: date, week: str | None = None) -> Path:
    week = week or iso_week_label(anchor)
    # Friday 9:00: Mon..Thu (exclude today Friday)
    end = anchor - timedelta(days=1)
    monday = anchor - timedelta(days=anchor.weekday())
    days: list[date] = []
    d = monday
    while d <= end:
        days.append(d)
        d += timedelta(days=1)

    headlines: list[str] = []
    callout_map: dict[str, str] = {}
    next_week: list[str] = []
    backlog_latest: list[str] = []

    for day in days:
        path = daily_path(day)
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        hl = extract_headline(content)
        if hl:
            headlines.append(hl)
        progress = extract_progress_block(content)
        if progress:
            for title, block in extract_callouts(progress):
                callout_map[title] = block
        for item in todo_lines(extract_section(content, "## 📋 明日待办")):
            if item not in next_week:
                next_week.append(item)
        bl = todo_lines(extract_section(content, "## 🗂️ 待排期"))
        if bl:
            backlog_latest = bl

    headline = headlines[-1] if headlines else f"本周 {week}（待补充）"
    progress_md = "\n\n".join(callout_map.values()) if callout_map else "<!-- 本周尚无 Daily 技改进展 -->"
    next_md = "\n".join(f"- [ ] {x}" for x in next_week) if next_week else "- <!-- 待补充 -->"
    backlog_md = "\n".join(f"- [ ] {x}" for x in backlog_latest) if backlog_latest else ""

    out_path = weekly_path(week)
    existing = out_path.read_text(encoding="utf-8") if out_path.exists() else None

    if existing:
        # Preserve user edits in 下周计划 if they added content beyond auto list
        body = existing
        if "## 📊 技改进展" in body and callout_map:
            body = re.sub(
                r"^## 📊 技改进展\s*\n.*?(?=^## |\Z)",
                f"## 📊 技改进展\n\n{progress_md}\n",
                body,
                count=1,
                flags=re.MULTILINE | re.DOTALL,
            )
        out_path.write_text(body, encoding="utf-8")
        print(f"merged progress into existing {out_path.name} ({len(callout_map)} topics)")
        return out_path

    tpl = (VAULT_ROOT / "Templates" / "weekly-note.md").read_text(encoding="utf-8")
    content = (
        tpl.replace("{{date:YYYY-MM-DD}}", anchor.isoformat())
        .replace("{{date:YYYY-[W]ww}}", week)
        .replace("<!-- agent:weekly-headline -->", headline)
        .replace("<!-- 每个技改：> [!type]- 标题 + 块内 2 列表；合并本周 Daily，进度取最新 -->", "")
        .replace("> [!example]- <!-- agent:topic-1-title -->\n>\n> | 子项 | 进度 |\n> | :--- | ---: |\n> | <!-- agent:topic-1-rows --> | |", progress_md)
        .replace("- <!-- agent:next-week -->", next_md.strip())
    )
    if backlog_md:
        content = content.replace(
            "<!-- 可选：取本周最新 Daily 的「待排期」快照，非下周必做 -->",
            backlog_md,
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"created {out_path.name} from {len(days)} days, {len(callout_map)} topics")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", help="ISO week e.g. 2026-W27 (default: current)")
    parser.add_argument("--date", help="Anchor date YYYY-MM-DD (default: today)")
    args = parser.parse_args()
    anchor = date.fromisoformat(args.date) if args.date else date.today()
    merge_week(anchor, args.week)


if __name__ == "__main__":
    main()
