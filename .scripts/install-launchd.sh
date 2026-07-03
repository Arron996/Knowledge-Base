#!/usr/bin/env bash
# Install or reload LaunchAgents for knowledge-base automation.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LAUNCHD_SRC="$SCRIPT_DIR/launchd"
LAUNCHD_DST="${HOME}/Library/LaunchAgents"

install_one() {
  local name="$1"
  cp "$LAUNCHD_SRC/$name" "$LAUNCHD_DST/$name"
  launchctl bootout "gui/${UID}" "$LAUNCHD_DST/$name" 2>/dev/null || true
  launchctl bootstrap "gui/${UID}" "$LAUNCHD_DST/$name"
  echo "installed $name"
}

mkdir -p "$LAUNCHD_DST"
install_one com.zhaorun.kb-evening-daily.plist
install_one com.zhaorun.kb-morning-todos.plist
echo "LaunchAgents ready. Logs: ~/Library/Logs/kb-evening.log ~/Library/Logs/kb-morning.log"
