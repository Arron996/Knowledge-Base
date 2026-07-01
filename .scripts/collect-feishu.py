#!/usr/bin/env python3
"""Build _staging/YYYY-MM-DD.feishu.json from Feishu MCP search-doc responses."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

VAULT_ROOT = Path("/Users/aaron/Documents/知识库")
CONFIG_PATH = VAULT_ROOT / ".scripts" / "feishu-config.json"
TZ = ZoneInfo("Asia/Shanghai")


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def parse_feishu_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M%z").astimezone(TZ)
    except ValueError:
        return None


def normalize_doc(item: dict) -> dict:
    title = (item.get("title") or "(无标题)").replace("&amp;", "&")
    return {
        "id": item.get("id"),
        "title": title,
        "url": item.get("url"),
        "docType": item.get("doc_type"),
        "createTime": item.get("create_time"),
        "updateTime": item.get("update_time"),
    }


def load_mcp_payload(path: Path) -> list[dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        if "data" in raw and "items" in raw.get("data", {}):
            return raw["data"]["items"]
        if "items" in raw:
            return raw["items"]
    if isinstance(raw, list):
        return raw
    raise ValueError(f"无法解析 MCP JSON: {path}")


def build_sidecar(
    target_day: date,
    created_items: list[dict],
    edited_search_items: list[dict],
) -> dict:
    day_str = target_day.isoformat()
    created_today = [normalize_doc(x) for x in created_items]
    created_ids = {x["id"] for x in created_today if x.get("id")}

    edited_today_only: list[dict] = []
    touched_today: list[dict] = []

    for item in edited_search_items:
        doc = normalize_doc(item)
        upd = parse_feishu_datetime(doc.get("updateTime") or "")
        crt = parse_feishu_datetime(doc.get("createTime") or "")
        if not upd or upd.date().isoformat() != day_str:
            continue
        touched_today.append(doc)
        if doc.get("id") in created_ids:
            continue
        if crt and crt.date().isoformat() == day_str:
            continue
        doc["note"] = "非今日创建，今日编辑/校订"
        edited_today_only.append(doc)

    return {
        "date": day_str,
        "collectedAt": datetime.now(TZ).isoformat(timespec="seconds"),
        "ownerOpenId": load_config().get("openId"),
        "createdToday": created_today,
        "editedTodayOnly": edited_today_only,
        "touchedToday": touched_today,
        "summary": {
            "createdCount": len(created_today),
            "editedOnlyCount": len(edited_today_only),
            "touchedCount": len(touched_today),
        },
        "queryNotes": {
            "createdFilter": f"create_time=[{day_str}, {day_str}]",
            "editedFilter": f"sort_rule=EDIT_TIME + update_time 落在 {day_str}",
        },
    }


def write_sidecar(payload: dict) -> Path:
    staging = VAULT_ROOT / "_staging"
    staging.mkdir(parents=True, exist_ok=True)
    out = staging / f"{payload['date']}.feishu.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge Feishu MCP search-doc JSON into feishu sidecar")
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--created-json", type=Path, help="MCP search-doc 今日创建结果 JSON")
    parser.add_argument("--edited-json", type=Path, help="MCP search-doc EDIT_TIME 结果 JSON")
    args = parser.parse_args()

    target = date.fromisoformat(args.date)
    created_items: list[dict] = []
    edited_items: list[dict] = []

    if args.created_json:
        created_items = load_mcp_payload(args.created_json)
    if args.edited_json:
        edited_items = load_mcp_payload(args.edited_json)

    if not args.created_json and not args.edited_json:
        parser.error("至少提供 --created-json 或 --edited-json")

    payload = build_sidecar(target, created_items, edited_items)
    out = write_sidecar(payload)
    print(f"Wrote {out}")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
