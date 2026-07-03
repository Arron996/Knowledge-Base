#!/usr/bin/env bash
# Evening daily: collect + SDK agent + git push.
set -euo pipefail

VAULT="/Users/aaron/Documents/知识库"
SCRIPT_DIR="$VAULT/.scripts"
LOG="${HOME}/Library/Logs/kb-evening.log"
DATE="${1:-$(date +%Y-%m-%d)}"

exec >>"$LOG" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') evening-daily DATE=$DATE ==="

notify_fail() {
  bash "$SCRIPT_DIR/kb-notify.sh" "知识库晚间日报" "$1"
}

trap 'notify_fail "evening-daily 异常退出"' ERR

cd "$VAULT"

python3 "$SCRIPT_DIR/collect-evening.py" --date "$DATE"

if [[ -z "${CURSOR_API_KEY:-}" ]]; then
  notify_fail "CURSOR_API_KEY 未设置，仅完成采集"
  echo "CURSOR_API_KEY missing; skip agent"
  exit 4
fi

node "$SCRIPT_DIR/kb-evening-agent.mjs" --date "$DATE"

git pull --ff-only origin main
git add Daily/
if git diff --staged --quiet; then
  echo "nothing to commit"
else
  git commit -m "daily: $DATE"
fi
git push origin main

echo "evening-daily OK"
