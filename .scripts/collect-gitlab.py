#!/usr/bin/env python3
"""Build _staging/YYYY-MM-DD.gitlab.json from GitLab MCP merge request responses."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import urlparse

VAULT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = VAULT_ROOT / ".scripts" / "gitlab-config.json"
TZ = ZoneInfo("Asia/Shanghai")


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_mcp_payload(path: Path) -> list[dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        if "data" in raw and isinstance(raw["data"], list):
            return raw["data"]
    raise ValueError(f"无法解析 GitLab MCP JSON: {path}")


def parse_gitlab_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(TZ)
    except ValueError:
        return None


def project_name(mr: dict, slug_map: dict) -> str:
    project_id = str(mr.get("project_id", ""))
    if project_id in slug_map:
        return slug_map[project_id]
    web_url = mr.get("web_url") or ""
    if "/-/merge_requests/" in web_url:
        return web_url.split("/-/merge_requests/")[0].rstrip("/").split("/")[-1]
    parts = [p for p in urlparse(web_url).path.split("/") if p and p != "-"]
    if parts:
        return parts[-1]
    references = mr.get("references") or {}
    full = references.get("full") or ""
    if full.startswith("global-rail-gds/"):
        return full.split("/", 1)[1]
    return project_id or "unknown"


def infer_topic(title: str) -> str:
    m = re.search(r"GDS-\d+", title)
    return m.group(0) if m else ""


def infer_release_stage(target_branch: str | None, config: dict) -> str:
    branch = (target_branch or "").strip()
    if not branch:
        return "unknown"
    production = {b.lower() for b in config.get("productionBranches", ["main", "master"])}
    if branch.lower() in production:
        return "production"
    for pattern in config.get("testingBranchPatterns", []):
        if branch.startswith(pattern):
            return "testing"
    return "unknown"


def slim_merged(mr: dict, slug_map: dict, config: dict) -> dict:
    target_branch = mr.get("target_branch")
    stage = infer_release_stage(target_branch, config)
    item = {
        "iid": mr.get("iid"),
        "title": mr.get("title", ""),
        "project": project_name(mr, slug_map),
        "sourceBranch": mr.get("source_branch"),
        "targetBranch": target_branch,
        "webUrl": mr.get("web_url"),
        "mergedAt": mr.get("merged_at"),
        "topicKey": infer_topic(mr.get("title", "")),
        "releaseStage": stage,
    }
    if stage == "production":
        item["progressHint"] = "已发生产"
    elif stage == "testing":
        item["progressHint"] = "测试中"
    return item


def build_sidecar(target_day: date, merged_items: list[dict]) -> dict:
    day_str = target_day.isoformat()
    config = load_config()
    slug_map = config.get("projectSlugMap", {})
    merged_today: list[dict] = []

    for mr in merged_items:
        merged_at = parse_gitlab_time(mr.get("merged_at"))
        if not merged_at or merged_at.date().isoformat() != day_str:
            continue
        if mr.get("state") != "merged":
            continue
        merged_today.append(slim_merged(mr, slug_map, config))

    merged_today.sort(key=lambda x: x.get("mergedAt") or "", reverse=True)

    return {
        "date": day_str,
        "collectedAt": datetime.now(TZ).isoformat(timespec="seconds"),
        "username": load_config().get("username"),
        "mergedToday": merged_today,
        "summary": {
            "mergedCount": len(merged_today),
        },
        "queryNotes": {
            "source": "list_user_merge_requests(role=author,state=merged)",
            "filter": f"merged_at 落在 {day_str}（Asia/Shanghai）",
        },
    }


def write_sidecar(payload: dict) -> Path:
    staging = VAULT_ROOT / "_staging"
    staging.mkdir(parents=True, exist_ok=True)
    out = staging / f"{payload['date']}.gitlab.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def mcp_query_hints(target_day: date, config: dict) -> dict:
    nxt = (target_day + timedelta(days=1)).isoformat()
    return {
        "mergedAuthored": {
            "tool": "list_user_merge_requests",
            "arguments": {
                "username": config.get("username", "zhaorun"),
                "role": "author",
                "state": "merged",
                "limit": 50,
            },
            "clientFilter": f"merged_at 落在 {target_day.isoformat()}",
        },
        "reviewOptional": {
            "tool": "list_user_events",
            "arguments": {
                "username": config.get("username", "zhaorun"),
                "action_type": "approved",
                "target_type": "merge_request",
                "after": target_day.isoformat(),
                "before": nxt,
            },
        },
        "merge": f"collect-gitlab.py --date {target_day.isoformat()} --merged-json /tmp/gitlab-merged.json",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge GitLab MCP MR JSON into gitlab sidecar")
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--merged-json", type=Path, help="MCP list_user_merge_requests 结果")
    parser.add_argument("--print-queries", action="store_true")
    args = parser.parse_args()

    config = load_config()
    target = date.fromisoformat(args.date)

    if args.print_queries:
        print(json.dumps(mcp_query_hints(target, config), ensure_ascii=False, indent=2))
        if not args.merged_json:
            return

    if not args.merged_json:
        parser.error("需提供 --merged-json（或仅 --print-queries）")

    payload = build_sidecar(target, load_mcp_payload(args.merged_json))
    out = write_sidecar(payload)
    print(f"Wrote {out}")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
