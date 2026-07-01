#!/usr/bin/env python3
"""Collect local work signals for daily report (Cursor chats, plans, git)."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

VAULT_ROOT = Path(__file__).resolve().parent.parent
CURSOR_PROJECTS = Path.home() / ".cursor" / "projects"
CURSOR_PLANS = Path.home() / ".cursor" / "plans"
GIT_REPOS = [
    Path("/Users/aaron/IdeaProjects/gds-order-admin-fe"),
    Path("/Users/aaron/IdeaProjects/gds-order-admin-be"),
    Path("/Users/aaron/IdeaProjects/gds-ticketing-system"),
    Path("/Users/aaron/IdeaProjects/gds-bus-ticketing-system"),
]
GIT_AUTHOR = "zhaorun"
IDEV2_CONFIG = VAULT_ROOT / ".scripts" / "idev2-config.json"
TZ = ZoneInfo("Asia/Shanghai")


def day_ms_bounds(target_day: date) -> tuple[int, int]:
    """Asia/Shanghai day range in epoch milliseconds."""
    start = datetime.combine(target_day, time.min, tzinfo=TZ)
    end = datetime.combine(target_day, time.max, tzinfo=TZ)
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


def load_sidecar(target_day: date, suffix: str) -> dict | None:
    path = VAULT_ROOT / "_staging" / f"{target_day.isoformat()}.{suffix}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def today_bounds() -> tuple[datetime, datetime]:
    d = date.today()
    start = datetime.combine(d, time.min, tzinfo=TZ)
    end = datetime.combine(d, time.max, tzinfo=TZ)
    return start, end


def mtime_in_today(path: Path, start: datetime, end: datetime) -> bool:
    ts = datetime.fromtimestamp(path.stat().st_mtime, tz=TZ)
    return start <= ts <= end


def extract_user_query(text: str) -> str:
    m = re.search(r"<user_query>\s*(.*?)\s*</user_query>", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def summarize_query(text: str, limit: int = 120) -> str:
    text = extract_user_query(text)
    text = re.sub(r"\s+", " ", text)
    if len(text) > limit:
        return text[: limit - 1] + "…"
    return text


def collect_cursor_chats(start: datetime, end: datetime) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()
    if not CURSOR_PROJECTS.exists():
        return items

    for path in CURSOR_PROJECTS.glob("*/agent-transcripts/*/*.jsonl"):
        if "/subagents/" in str(path):
            continue
        if not mtime_in_today(path, start, end):
            continue
        chat_id = path.parent.name
        if chat_id in seen:
            continue
        seen.add(chat_id)

        title = ""
        try:
            with path.open(encoding="utf-8") as f:
                for line in f:
                    row = json.loads(line)
                    if row.get("role") != "user":
                        continue
                    parts = row.get("message", {}).get("content", [])
                    for part in parts:
                        if part.get("type") == "text":
                            title = summarize_query(part.get("text", ""))
                            break
                    if title:
                        break
        except (OSError, json.JSONDecodeError):
            title = "(无法解析)"

        project = path.parts[path.parts.index("projects") + 1] if "projects" in path.parts else ""
        items.append(
            {
                "chatId": chat_id,
                "project": project,
                "title": title or "(无标题)",
                "modifiedAt": datetime.fromtimestamp(path.stat().st_mtime, tz=TZ).isoformat(timespec="seconds"),
                "transcript": str(path),
            }
        )

    items.sort(key=lambda x: x["modifiedAt"], reverse=True)
    return items


def collect_plans(start: datetime, end: datetime) -> list[dict]:
    items: list[dict] = []
    if not CURSOR_PLANS.exists():
        return items

    for path in CURSOR_PLANS.glob("*.plan.md"):
        if not mtime_in_today(path, start, end):
            continue
        name = path.stem
        title = name.rsplit("_", 1)[0] if "_" in name else name
        items.append(
            {
                "file": path.name,
                "title": title,
                "modifiedAt": datetime.fromtimestamp(path.stat().st_mtime, tz=TZ).isoformat(timespec="seconds"),
            }
        )

    items.sort(key=lambda x: x["modifiedAt"], reverse=True)
    return items


def collect_git_commits(target_day: date) -> list[dict]:
    since = f"{target_day.isoformat()} 00:00:00"
    until = f"{target_day.isoformat()} 23:59:59"
    items: list[dict] = []

    for repo in GIT_REPOS:
        if not (repo / ".git").exists():
            continue
        try:
            out = subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(repo),
                    "log",
                    f"--since={since}",
                    f"--until={until}",
                    f"--author={GIT_AUTHOR}",
                    "--pretty=format:%h|%s",
                ],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            continue
        if not out:
            continue
        commits = []
        for line in out.splitlines():
            if "|" not in line:
                continue
            h, msg = line.split("|", 1)
            commits.append({"hash": h, "message": msg})
        if commits:
            items.append({"repo": repo.name, "commits": commits})

    return items


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    args = parser.parse_args()
    target_date = date.fromisoformat(args.date)
    start = datetime.combine(target_date, time.min, tzinfo=TZ)
    end = datetime.combine(target_date, time.max, tzinfo=TZ)
    target = target_date.isoformat()
    idev2 = load_sidecar(target_date, "idev2")
    feishu = load_sidecar(target_date, "feishu")
    day_start_ms, day_end_ms = day_ms_bounds(target_date)

    payload = {
        "date": target,
        "collectedAt": datetime.now(TZ).isoformat(timespec="seconds"),
        "cursorChats": collect_cursor_chats(start, end),
        "plans": collect_plans(start, end),
        "git": collect_git_commits(target_date),
        "idev2": idev2,
        "feishu": feishu,
        "queryHints": {
            "timezone": "Asia/Shanghai",
            "idev2EmployeeId": "TR043507",
            "idev2CreatedTimeStart": day_start_ms,
            "idev2CreatedTimeEnd": day_end_ms,
            "idev2EditField": "lastUpdatedTime",
            "idev2Sidecar": f"_staging/{target}.idev2.json",
            "feishuSidecar": f"_staging/{target}.feishu.json",
            "idev2SidecarHint": "creator=工号 TR043507 + createtime 与 lastUpdatedTime 双路",
            "feishuSidecarHint": "createdToday + editedTodayOnly（update_time 当日且非当日创建）",
        },
    }

    notes = {}
    if idev2 is None:
        notes["idev2"] = f"缺少 _staging/{target}.idev2.json，请用 MCP 按 lastUpdatedTime 补充"
    if feishu is None:
        notes["feishu"] = f"缺少 _staging/{target}.feishu.json，请运行 collect-feishu.py"
    if notes:
        payload["notes"] = notes

    staging_dir = VAULT_ROOT / "_staging"
    staging_dir.mkdir(parents=True, exist_ok=True)
    out = staging_dir / f"{target}.raw.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(
        json.dumps(
            {
                "counts": {
                    "cursorChats": len(payload["cursorChats"]),
                    "plans": len(payload["plans"]),
                    "gitRepos": len(payload["git"]),
                    "idev2Issues": (idev2 or {}).get("summary", {}).get("totalDistinct"),
                    "feishuCreated": (feishu or {}).get("summary", {}).get("createdCount"),
                    "feishuEditedOnly": (feishu or {}).get("summary", {}).get("editedOnlyCount"),
                }
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
