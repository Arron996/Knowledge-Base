#!/usr/bin/env bash
# Re-inject CURSOR_API_KEY into evening LaunchAgent from local secrets.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LAUNCHD_DST="${HOME}/Library/LaunchAgents"
PLIST="${LAUNCHD_DST}/com.zhaorun.kb-evening-daily.plist"

if [[ ! -f "$PLIST" ]]; then
  echo "Run install-launchd.sh first." >&2
  exit 1
fi

# shellcheck disable=SC1091
source "${SCRIPT_DIR}/kb-load-secrets.sh"
load_kb_secrets

if [[ -z "${CURSOR_API_KEY:-}" ]]; then
  echo "CURSOR_API_KEY not found. Set ~/.config/kb-automation/cursor_api_key or ~/.zshrc.local" >&2
  exit 1
fi

/usr/libexec/PlistBuddy -c "Add :EnvironmentVariables dict" "$PLIST" 2>/dev/null || true
if /usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:CURSOR_API_KEY" "$PLIST" &>/dev/null; then
  /usr/libexec/PlistBuddy -c "Set :EnvironmentVariables:CURSOR_API_KEY ${CURSOR_API_KEY}" "$PLIST"
else
  /usr/libexec/PlistBuddy -c "Add :EnvironmentVariables:CURSOR_API_KEY string ${CURSOR_API_KEY}" "$PLIST"
fi

launchctl bootout "gui/${UID}" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/${UID}" "$PLIST"
echo "Evening LaunchAgent reloaded with CURSOR_API_KEY."
