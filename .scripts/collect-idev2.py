#!/usr/bin/env python3
"""Merge iDev2 MCP query responses into _staging/YYYY-MM-DD.idev2.json (三路)."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

VAULT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = VAULT_ROOT / ".scripts" / "idev2-config.json"
TZ = ZoneInfo("Asia/Shanghai")

INCLUDE_FIELDS = (
    "title,issueKey,issueStatus,createtime,lastUpdatedTime,"
    "creatorObj,executiveObj,updaterObj,parentLinkObj"
)


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def day_ms_bounds(target_day: date) -> tuple[int, int]:
    start = datetime.combine(target_day, time.min, tzinfo=TZ)
    end = datetime.combine(target_day, time.max, tzinfo=TZ)
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


def load_mcp_payload(path: Path) -> list[dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        if "records" in raw:
            return raw["records"]
        if "data" in raw and isinstance(raw["data"], dict) and "records" in raw["data"]:
            return raw["data"]["records"]
    if isinstance(raw, list):
        return raw
    raise ValueError(f"无法解析 MCP JSON: {path}")


def norm_status(issue_status: object) -> str:
    if isinstance(issue_status, dict):
        return issue_status.get("name") or issue_status.get("enName") or "?"
    return str(issue_status) if issue_status else "?"


def executive_id(record: dict) -> str | None:
    return (record.get("executiveObj") or {}).get("id")


def creator_id(record: dict) -> str | None:
    return (record.get("creatorObj") or {}).get("id")


def is_my_issue(record: dict, employee_id: str) -> bool:
    """我的 iDev = 指派人是我。"""
    return executive_id(record) == employee_id


def is_delegated_by_me(record: dict, employee_id: str) -> bool:
    """我创建但指派给他人 — 不计入我的 iDev / 本周工作。"""
    return creator_id(record) == employee_id and executive_id(record) != employee_id


def slim_issue(record: dict, note: str | None = None) -> dict:
    item = {
        "key": record.get("issueKey", ""),
        "title": record.get("title", ""),
        "status": norm_status(record.get("issueStatus")),
        "parent": (record.get("parentLinkObj") or {}).get("issueKey"),
    }
    if note:
        item["note"] = note
    return item


def in_day(ts: int | None, start: int, end: int) -> bool:
    if ts is None:
        return False
    return start <= ts <= end


def merge_records(*groups: list[dict]) -> list[dict]:
    merged: list[dict] = []
    seen: set[str] = set()
    for group in groups:
        for record in group:
            key = record.get("issueKey")
            if not key or key in seen:
                continue
            seen.add(key)
            merged.append(record)
    return merged


def build_sidecar(
    target_day: date,
    created_records: list[dict],
    scan_records: list[dict],
    *,
    employee_id: str,
) -> dict:
    start, end = day_ms_bounds(target_day)
    day_str = target_day.isoformat()

    created_today: list[dict] = []
    delegated_today: list[dict] = []
    assigned_today_only: list[dict] = []
    updated_today_only: list[dict] = []
    seen_keys: set[str] = set()

    for record in created_records:
        key = record.get("issueKey")
        if not key:
            continue
        if is_delegated_by_me(record, employee_id):
            delegated_today.append(
                slim_issue(record, note="我创建但指派他人，不计入我的 iDev")
            )
            continue
        if not is_my_issue(record, employee_id):
            continue
        seen_keys.add(key)
        created_today.append(slim_issue(record, note="今日创建，指派给我"))

    for record in scan_records:
        key = record.get("issueKey")
        if not key or key in seen_keys:
            continue

        createtime = record.get("createtime") or 0
        last_updated = record.get("lastUpdatedTime") or 0
        exec_id = executive_id(record)
        cre_id = creator_id(record)

        if not in_day(last_updated, start, end):
            continue

        if not is_my_issue(record, employee_id):
            continue

        if in_day(createtime, start, end) and cre_id == employee_id:
            continue

        if cre_id != employee_id:
            assigned_today_only.append(
                slim_issue(record, note=f"他人创建，今日指派 {employee_id}")
            )
            seen_keys.add(key)
            continue

        updated_today_only.append(
            slim_issue(record, note="非今日创建，今日有进展（指派给我）")
        )
        seen_keys.add(key)

    return {
        "date": day_str,
        "collectedAt": datetime.now(TZ).isoformat(timespec="seconds"),
        "query": {
            "employeeId": employee_id,
            "createdTimeStart": start,
            "createdTimeEnd": end,
            "strategy": (
                "myIssue=executiveObj.id=employee; "
                "createdToday(今日创建且指派给我); "
                "delegatedToday(我创建指派他人,排除); "
                "assignedTodayOnly(他人创建今日指派给我); "
                "updatedTodayOnly(指派给我且今日lastUpdatedTime)"
            ),
        },
        "createdToday": created_today,
        "delegatedToday": delegated_today,
        "assignedTodayOnly": assigned_today_only,
        "updatedTodayOnly": updated_today_only,
        "summary": {
            "createdCount": len(created_today),
            "delegatedCount": len(delegated_today),
            "assignedOnlyCount": len(assigned_today_only),
            "updatedOnlyCount": len(updated_today_only),
            "totalDistinct": len(seen_keys),
        },
    }


def write_sidecar(payload: dict) -> Path:
    staging = VAULT_ROOT / "_staging"
    staging.mkdir(parents=True, exist_ok=True)
    out = staging / f"{payload['date']}.idev2.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def mcp_query_hints(target_day: date, config: dict) -> dict:
    start, end = day_ms_bounds(target_day)
    employee_id = config["employeeId"]
    product_ids = config.get("productIds", [])
    parent_ids = config.get("parentIssueIds", [])
    include = INCLUDE_FIELDS
    hints = {
        "createdToday": {
            "tool": "iDev2-issue-query",
            "arguments": {
                "creator": employee_id,
                "createdTimeStart": start,
                "createdTimeEnd": end,
                "productIds": product_ids,
                "size": 50,
                "includeFields": include,
            },
        },
        "relatedWide": {
            "tool": "iDev2-issue-query",
            "arguments": {
                "related": employee_id,
                "productIds": product_ids,
                "size": 100,
                "orderBy": "lastUpdatedTime desc",
                "includeFields": include,
            },
            "note": "补漏：Story 子树外的指派/更新；勿单独依赖（top100 会漏）",
        },
    }
    if parent_ids:
        hints["storyChildren"] = {
            "tool": "iDev2-issue-query",
            "arguments": {
                "parentIssueId": parent_ids[0],
                "productIds": product_ids,
                "size": 50,
                "includeFields": include,
            },
            "note": f"主扫 {config.get('parentIssueKeys', parent_ids)} 子 Issue，客户端筛指派/更新",
        }
    hints["merge"] = (
        "collect-idev2.py --created-json ... "
        "--scan-json story.json [--scan-json related.json]"
    )
    return hints


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge iDev2 MCP JSON into idev2 sidecar (三路)")
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--created-json", type=Path, help="MCP iDev2-issue-query 今日创建结果")
    parser.add_argument(
        "--scan-json",
        type=Path,
        action="append",
        default=[],
        help="MCP 宽查结果（可多次：storyChildren + relatedWide，合并去重后筛指派/更新）",
    )
    parser.add_argument(
        "--related-json",
        type=Path,
        help="(兼容旧参数) 等同 --scan-json 一次",
    )
    parser.add_argument(
        "--print-queries",
        action="store_true",
        help="打印 MCP 查询参数（Agent 调 MCP 前可先看）",
    )
    args = parser.parse_args()

    config = load_config()
    target = date.fromisoformat(args.date)
    employee_id = config["employeeId"]

    if args.print_queries:
        print(json.dumps(mcp_query_hints(target, config), ensure_ascii=False, indent=2))
        if not args.created_json and not args.related_json:
            return

    if not args.created_json or (not args.scan_json and not args.related_json):
        parser.error("需 --created-json，以及至少一个 --scan-json 或 --related-json")

    scan_paths = list(args.scan_json)
    if args.related_json:
        scan_paths.append(args.related_json)

    created_records = load_mcp_payload(args.created_json)
    scan_records = merge_records(*[load_mcp_payload(p) for p in scan_paths])

    payload = build_sidecar(
        target,
        created_records,
        scan_records,
        employee_id=employee_id,
    )
    out = write_sidecar(payload)
    print(f"Wrote {out}")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
