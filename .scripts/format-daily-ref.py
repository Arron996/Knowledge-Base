#!/usr/bin/env python3
"""Generate Daily reference section markdown from _staging sidecars."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

VAULT_ROOT = Path("/Users/aaron/Documents/知识库")

COMMIT_PREFIX = {
    "feat:": "✨",
    "fix:": "🐛",
    "refactor:": "♻️",
    "Merge": "🔀",
}

IDEV_STATUS = {
    "DONE": "✅",
    "DOING": "🔄",
    "开发中": "🔄",
    "TODO": "⬜",
    "待敏捷排期": "📅",
}


def commit_icon(message: str) -> str:
    for prefix, icon in COMMIT_PREFIX.items():
        if message.startswith(prefix) or prefix.lower() in message.lower():
            return icon
    return "·"


def idev_icon(status: str) -> str:
    return IDEV_STATUS.get(status, "·")


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def format_git(git_items: list[dict]) -> str:
    if not git_items:
        return "（今日无 commit）\n"
    lines = []
    for repo in git_items:
        lines.append(f"**{repo['repo']}**")
        for c in repo.get("commits", []):
            icon = commit_icon(c.get("message", ""))
            lines.append(f"- {icon} `{c['hash']}` {c['message']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def format_gitlab(gitlab: dict | None) -> str:
    if not gitlab:
        return "（缺少 gitlab sidecar）\n"
    merged = gitlab.get("mergedToday", [])
    if not merged:
        return "（今日无 MR 合入记录；本地 merge 仅见 Git commit）\n"
    lines = []
    for mr in merged:
        title = mr.get("title", "")
        project = mr.get("project", "")
        url = mr.get("webUrl", "")
        target = mr.get("targetBranch", "")
        hint = mr.get("progressHint")
        stage = mr.get("releaseStage", "")
        suffix = ""
        if hint:
            suffix = f" · {hint}"
        elif stage == "production":
            suffix = " · 已发生产"
        elif stage == "testing":
            suffix = " · 测试中"
        iid = mr.get("iid", "")
        if url:
            lines.append(f"- 🔀 [{project} !{iid}]({url}) → `{target}` · {title}{suffix}")
        else:
            lines.append(f"- 🔀 {project} !{iid} → `{target}` · {title}{suffix}")
    return "\n".join(lines) + "\n"


def format_idev(idev: dict | None) -> str:
    if not idev:
        return "（缺少 idev2 sidecar）\n"
    rows = []
    for item in idev.get("createdToday", []):
        key = item.get("key", "")
        title = item.get("title", "")
        status = item.get("status", "")
        rows.append(f"| {idev_icon(status)} | [{key}](https://idev2.ctripcorp.com/issueDetail/{key}) | {title} |")
    for item in idev.get("assignedTodayOnly", []):
        key = item.get("key", "")
        title = item.get("title", "")
        status = item.get("status", "")
        note = item.get("note", "今日新指派")
        rows.append(
            f"| {idev_icon(status)} | [{key}](https://idev2.ctripcorp.com/issueDetail/{key}) | {title}（{note}） |"
        )
    for item in idev.get("updatedTodayOnly", []):
        key = item.get("key", "")
        title = item.get("title", "")
        status = item.get("status", "")
        note = item.get("note", "今日扭转")
        rows.append(f"| {idev_icon(status)} | [{key}](https://idev2.ctripcorp.com/issueDetail/{key}) | {title}（{note}） |")
    delegated = idev.get("delegatedToday", [])
    if delegated:
        rows.append("")
        rows.append("**我创建但指派他人（不计入我的 iDev）**")
        for item in delegated:
            key = item.get("key", "")
            title = item.get("title", "")
            status = item.get("status", "")
            rows.append(
                f"| {idev_icon(status)} | [{key}](https://idev2.ctripcorp.com/issueDetail/{key}) | {title} |"
            )
    if not rows:
        return "（今日无 iDev 记录）\n"
    header = "| 状态 | Issue | 标题 |\n| --- | --- | --- |\n"
    return header + "\n".join(rows) + "\n"


def format_feishu(feishu: dict | None) -> str:
    if not feishu:
        return "（缺少 feishu sidecar）\n"
    lines = []
    created = feishu.get("createdToday", [])
    edited = feishu.get("editedTodayOnly", [])
    if created:
        lines.append("**今日新建**")
        for d in created:
            lines.append(f"- [{d['title']}]({d['url']})")
        lines.append("")
    if edited:
        lines.append("**今日校订**")
        for d in edited:
            lines.append(f"- [{d['title']}]({d['url']})")
        lines.append("")
    if not lines:
        return "（今日无飞书文档变更）\n"
    return "\n".join(lines).strip() + "\n"


def format_plans(plans: list[dict]) -> str:
    if not plans:
        return "（今日无 Plan 变更）\n"
    return "\n".join(f"- {p['title']}" for p in plans) + "\n"


def format_chats(chats: list[dict], limit: int = 12) -> str:
    if not chats:
        return "（今日无 Cursor 会话）\n"
    lines = [f"- {c['title']}" for c in chats[:limit]]
    if len(chats) > limit:
        lines.append(f"- …共 {len(chats)} 条")
    return "\n".join(lines) + "\n"


def build_reference(target_day: date) -> str:
    d = target_day.isoformat()
    staging = VAULT_ROOT / "_staging"
    raw = load_json(staging / f"{d}.raw.json") or {}
    idev = load_json(staging / f"{d}.idev2.json")
    feishu = load_json(staging / f"{d}.feishu.json")
    gitlab = load_json(staging / f"{d}.gitlab.json")
    if isinstance(raw, dict) and idev is None:
        idev = raw.get("idev2")
    if isinstance(raw, dict) and feishu is None:
        feishu = raw.get("feishu")
    if isinstance(raw, dict) and gitlab is None:
        gitlab = raw.get("gitlab")

    chats = raw.get("cursorChats", []) if isinstance(raw, dict) else []
    plans = raw.get("plans", []) if isinstance(raw, dict) else []
    git = raw.get("git", []) if isinstance(raw, dict) else []

    parts = [
        "<details>",
        f"<summary>💬 Cursor 会话（{len(chats)}）</summary>",
        "",
        format_chats(chats),
        "</details>",
        "",
        "<details>",
        f"<summary>📋 Plan（{len(plans)}）</summary>",
        "",
        format_plans(plans),
        "</details>",
        "",
        "<details>",
        "<summary>🔀 Git commit</summary>",
        "",
        format_git(git),
        "</details>",
        "",
        "<details>",
        "<summary>🔀 GitLab MR 合入</summary>",
        "",
        format_gitlab(gitlab if isinstance(gitlab, dict) else None),
        "</details>",
        "",
        "<details>",
        "<summary>📝 飞书文档</summary>",
        "",
        format_feishu(feishu if isinstance(feishu, dict) else None),
        "</details>",
        "",
        "<details>",
        "<summary>📋 iDev2</summary>",
        "",
        format_idev(idev if isinstance(idev, dict) else None),
        "",
        f"详见 `_staging/{d}.idev2.json`、`_staging/{d}.feishu.json`、`_staging/{d}.gitlab.json`",
        "</details>",
    ]
    return "\n".join(parts)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()
    print(build_reference(date.fromisoformat(args.date)))


if __name__ == "__main__":
    main()
