#!/usr/bin/env python3
"""Merge Feishu MCP sidecar into staging summary."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent


def load_feishu_sidecar(target_day: date) -> dict | None:
    path = VAULT_ROOT / "_staging" / f"{target_day.isoformat()}.feishu.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def main() -> None:
    target = date.today()
    feishu = load_feishu_sidecar(target)
    out = VAULT_ROOT / "_staging" / f"{target.isoformat()}.feishu.summary.json"
    payload = {
        "date": target.isoformat(),
        "collectedAt": datetime.now().isoformat(timespec="seconds"),
        "feishu": feishu,
        "counts": {
            "createdToday": len((feishu or {}).get("createdToday", [])),
            "editedToday": len((feishu or {}).get("editedToday", [])),
        },
    }
    if feishu is None:
        payload["notes"] = {
            "feishu": f"缺少 _staging/{target.isoformat()}.feishu.json，请用飞书 MCP 双查补充",
        }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(json.dumps(payload["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
