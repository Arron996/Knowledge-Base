#!/usr/bin/env python3
"""Generate 票台小组周报 (Weekly/{week}-票台周报.md) from personal weekly + dailies."""

from __future__ import annotations

import argparse
import re
from datetime import date, timedelta
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent

# 不进票台小组周报的正文（个人工作流 / 非交付）
SKIP_TITLE_PATTERNS = (
    "Obsidian",
    "日报",
    "周报自动化",
    "个人知识库",
    "sdk",
    "launchd",
)

# Callout 标题 → 本周工作小标题（未命中则归「其他」）
CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Admin 优化升级", ("Admin", "Ticket Log", "异常配置", "供应配置", "历史版本", "Redis 缓存")),
    ("Bug 修复", ("误清", "兜底", "重试 complete", "降级", "修复", "refundEvent")),
    ("功能增强", ("obtain 拦截", "手动置失败", "功能增强")),
    ("需求 / 方案", ("GDPR", "Voyager", "H2", "规划", "工作流")),
    ("线上排查", ("线上排查", "UKTIS", "排障", "调研")),
]

# W27 及更早已在小组周报结项、W28 起不再重复列举（按 issueKey / 关键词）
PRIOR_WEEK_DONE_KEYS = {
    "GDS-9524",
    "GDS-9525",
    "GDS-9458",
    "GDS-2971",
    "GDS-9414",
    "GDS-9399",
    "GDS-9400",
    "GDS-9398",
    "GDS-9536",
    "GDS-9537",
}


def iso_week_label(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def week_date_range(anchor: date) -> tuple[date, date, str]:
    monday = anchor - timedelta(days=anchor.weekday())
    friday = monday + timedelta(days=4)
    if anchor < friday:
        end = anchor
    else:
        end = friday
    fmt = lambda d: f"{d.month}/{d.day}"
    return monday, end, f"{fmt(monday)} – {fmt(end)}"


def team_weekly_path(week: str) -> Path:
    return VAULT_ROOT / "Weekly" / f"{week}-票台周报.md"


def personal_weekly_path(week: str) -> Path:
    return VAULT_ROOT / "Weekly" / f"{week}.md"


def daily_path(day: date) -> Path:
    return VAULT_ROOT / "Daily" / f"{day.isoformat()}.md"


def extract_section(content: str, heading: str) -> str | None:
    pattern = rf"^{re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    m = re.search(pattern, content, flags=re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else None


def extract_callouts(progress: str) -> list[tuple[str, str]]:
    pattern = r"(> \[!\w+\]-[^\n]*(?:\n(?:>.*|\n(?!\s*> \[!)))*)"
    blocks: list[tuple[str, str]] = []
    for m in re.finditer(pattern, progress, flags=re.MULTILINE):
        block = m.group(1).strip()
        title_m = re.match(r"> \[!\w+\]-\s*(.+)", block)
        title = title_m.group(1).strip() if title_m else block[:60]
        blocks.append((title, block))
    return blocks


def latest_status_from_callout(block: str) -> str | None:
    rows = re.findall(r"\|\s*(.+?)\s*\|\s*(.+?)\s*\|", block)
    for label, status in reversed(rows):
        label = label.strip()
        status = status.strip()
        if label in ("子项", ":---") or not status:
            continue
        if status.startswith("<!--"):
            continue
        return f"{label} — {status}"
    return None


def should_skip_title(title: str) -> bool:
    return any(p in title for p in SKIP_TITLE_PATTERNS)


def classify_title(title: str) -> str:
    for category, keywords in CATEGORY_RULES:
        if any(k in title for k in keywords):
            return category
    return "其他"


def format_work_line(n: int, title: str, block: str) -> str:
    status = latest_status_from_callout(block)
    if not status:
        return ""
    status_tail = status.split("—", 1)[-1].strip()
    link_m = re.search(r"\[([^\]]+)\]\((https?://[^)]+)\)", title)
    if link_m:
        return f"{n}. [{link_m.group(1)}]({link_m.group(2)}) — {status_tail}"
    return f"{n}. {title} — {status_tail}"


def is_prior_done(title: str, block: str) -> bool:
    text = title + block
    if any(k in text for k in PRIOR_WEEK_DONE_KEYS):
        if "✅" in block and "🔄" not in block and "⬜" not in block:
            return True
    return False


def render_categorized_work(callout_map: dict[str, str]) -> str:
    buckets: dict[str, list[str]] = {cat: [] for cat, _ in CATEGORY_RULES}
    buckets["其他"] = []
    order = [cat for cat, _ in CATEGORY_RULES] + ["其他"]

    for title, block in callout_map.items():
        if should_skip_title(title):
            continue
        if is_prior_done(title, block):
            continue
        category = classify_title(title)
        n = len(buckets[category]) + 1
        line = format_work_line(n, title, block)
        if line:
            buckets[category].append(line)

    sections: list[str] = []
    for category in order:
        lines = buckets[category]
        if not lines:
            continue
        sections.append(f"**{category}**\n\n" + "\n".join(lines))
    return "\n\n".join(sections) if sections else "1. （待补充）"


def todo_lines(body: str | None) -> list[str]:
    if not body:
        return []
    out: list[str] = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("- [ ]"):
            item = re.sub(r"^\-\s*\[\s\]\s*", "", s).strip()
            if item and item not in out:
                out.append(item)
    return out


def build_team_week(anchor: date, week: str | None = None) -> Path:
    week = week or iso_week_label(anchor)
    monday, end_day, date_range = week_date_range(anchor)

    # Collect callouts from Mon..anchor daily + personal weekly
    callout_map: dict[str, str] = {}
    days: list[date] = []
    d = monday
    while d <= end_day:
        days.append(d)
        d += timedelta(days=1)

    for day in days:
        path = daily_path(day)
        if not path.exists():
            continue
        progress = extract_section(path.read_text(encoding="utf-8"), "## 📊 技改进展")
        if not progress:
            continue
        for title, block in extract_callouts(progress):
            callout_map[title] = block

    pw = personal_weekly_path(week)
    if pw.exists():
        progress = extract_section(pw.read_text(encoding="utf-8"), "## 📊 技改进展")
        if progress:
            for title, block in extract_callouts(progress):
                callout_map[title] = block

    work_md = render_categorized_work(callout_map)
    work_count = len(re.findall(r"^\d+\. ", work_md, flags=re.MULTILINE))

    next_week: list[str] = []
    if pw.exists():
        for item in todo_lines(extract_section(pw.read_text(encoding="utf-8"), "## 📋 下周计划")):
            if item not in next_week:
                next_week.append(item)
    for day in reversed(days):
        path = daily_path(day)
        if not path.exists():
            continue
        for item in todo_lines(extract_section(path.read_text(encoding="utf-8"), "## 📋 明日待办")):
            if item not in next_week:
                next_week.append(item)

    next_md = "\n".join(f"{i + 1}. {x}" for i, x in enumerate(next_week[:8])) if next_week else "1. （待补充）"

    out_path = team_weekly_path(week)
    if out_path.exists():
        print(f"skip {out_path.name}: already exists (delete to regenerate draft)")
        return out_path

    content = f"""# 国际火车票票台小队工作周报

**周期：** {week}（{date_range}）

---

**重点项目进度**

（暂未确定，待组内对齐 H2 重点项目后更新）

---

**本周工作**

{work_md}

**下周计划**

{next_md}
"""
    out_path.write_text(content, encoding="utf-8")
    print(f"created {out_path.name} ({work_count} work items, {len(next_week)} next-week items)")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 票台小组周报 draft")
    parser.add_argument("--week", help="ISO week e.g. 2026-W28")
    parser.add_argument("--date", help="Anchor date YYYY-MM-DD (default: today)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing file")
    args = parser.parse_args()
    anchor = date.fromisoformat(args.date) if args.date else date.today()
    week = args.week or iso_week_label(anchor)
    out = team_weekly_path(week)
    if args.force and out.exists():
        out.unlink()
    build_team_week(anchor, week)


if __name__ == "__main__":
    main()
