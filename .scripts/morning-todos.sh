#!/usr/bin/env bash
# Morning: roll todos from previous workday; Friday also merge Weekly.
set -euo pipefail

VAULT="/Users/aaron/Documents/知识库"
SCRIPT_DIR="$VAULT/.scripts"
LOG="${HOME}/Library/Logs/kb-morning.log"
TODAY="$(date +%Y-%m-%d)"
WEEKDAY="$(date +%u)"

exec >>"$LOG" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') morning-todos TODAY=$TODAY ==="

notify_fail() {
  bash "$SCRIPT_DIR/kb-notify.sh" "知识库早间待办" "$1"
}

SOURCE="$(python3 "$SCRIPT_DIR/workday.py" --prev "$TODAY")" || {
  notify_fail "workday.py 失败"
  exit 1
}

echo "SOURCE=$SOURCE TARGET=$TODAY"

if ! python3 "$SCRIPT_DIR/roll-morning-todos.py" --from "$SOURCE" --to "$TODAY"; then
  notify_fail "来源 Daily/$SOURCE.md 不存在或滚动失败"
  exit 3
fi

if [[ "$WEEKDAY" == "5" ]]; then
  WEEK="$(date +%G-W%V)"
  python3 "$SCRIPT_DIR/merge-weekly.py" --date "$TODAY" --week "$WEEK"
  python3 "$SCRIPT_DIR/merge-weekly-team.py" --date "$TODAY" --week "$WEEK" || true
fi

cd "$VAULT"

git_pull_ok=0
git pull --ff-only origin main || git_pull_ok=$?
if [[ "$git_pull_ok" -ne 0 ]]; then
  echo "WARN: git pull failed (rc=$git_pull_ok)"
  notify_fail "git pull 失败，继续尝试 commit/push"
fi

git add Daily/ Weekly/
MSG="morning: $TODAY todos"
[[ "$WEEKDAY" == "5" ]] && MSG="$MSG + weekly + team-weekly"
if git diff --staged --quiet; then
  echo "nothing to commit"
else
  git commit -m "$MSG"
fi

if ! git push origin main; then
  notify_fail "git push 失败，Daily 已在本地，请补 push"
  exit 6
fi

echo "morning-todos OK"
