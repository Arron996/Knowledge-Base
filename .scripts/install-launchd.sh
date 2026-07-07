#!/usr/bin/env bash
# Install LaunchAgents; entrypoints in ~/bin (not Documents) for clearer FDA targeting.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LAUNCHD_SRC="$SCRIPT_DIR/launchd"
LAUNCHD_DST="${HOME}/Library/LaunchAgents"
BIN_DIR="${HOME}/bin"

load_cursor_api_key() {
  # shellcheck disable=SC1091
  source "${SCRIPT_DIR}/kb-load-secrets.sh"
  load_kb_secrets
}

plist_set_env() {
  local plist="$1"
  local key="$2"
  local value="$3"
  /usr/libexec/PlistBuddy -c "Add :EnvironmentVariables dict" "$plist" 2>/dev/null || true
  if /usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:${key}" "$plist" &>/dev/null; then
    /usr/libexec/PlistBuddy -c "Set :EnvironmentVariables:${key} ${value}" "$plist"
  else
    /usr/libexec/PlistBuddy -c "Add :EnvironmentVariables:${key} string ${value}" "$plist"
  fi
}

install_one() {
  local name="$1"
  local launch_script="$2"
  local inject_key="${3:-false}"
  cp "$LAUNCHD_SRC/$name" "$LAUNCHD_DST/$name"
  /usr/libexec/PlistBuddy -c "Set :ProgramArguments:1 ${launch_script}" "$LAUNCHD_DST/$name"
  /usr/libexec/PlistBuddy -c "Delete :WorkingDirectory" "$LAUNCHD_DST/$name" 2>/dev/null || true
  /usr/libexec/PlistBuddy -c "Add :WorkingDirectory string ${HOME}" "$LAUNCHD_DST/$name"
  plist_set_env "$LAUNCHD_DST/$name" PATH "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${HOME}/bin"
  if [[ "$inject_key" == "true" && -n "${CURSOR_API_KEY:-}" ]]; then
    plist_set_env "$LAUNCHD_DST/$name" CURSOR_API_KEY "$CURSOR_API_KEY"
  fi
  launchctl bootout "gui/${UID}" "$LAUNCHD_DST/$name" 2>/dev/null || true
  launchctl bootstrap "gui/${UID}" "$LAUNCHD_DST/$name"
  echo "installed $name → $launch_script"
}

mkdir -p "$LAUNCHD_DST" "$BIN_DIR"
chmod +x "$BIN_DIR/kb-morning-launch.sh" "$BIN_DIR/kb-evening-launch.sh" 2>/dev/null || true
for f in kb-morning-launch.sh kb-evening-launch.sh; do
  if [[ ! -x "$BIN_DIR/$f" ]]; then
    echo "ERROR: missing $BIN_DIR/$f — create it first." >&2
    exit 1
  fi
done

load_cursor_api_key
install_one com.zhaorun.kb-evening-daily.plist "$BIN_DIR/kb-evening-launch.sh" true
install_one com.zhaorun.kb-morning-todos.plist "$BIN_DIR/kb-morning-launch.sh" false
echo ""
echo "LaunchAgents ready."
echo "If launchd still gets Operation not permitted on Documents/知识库:"
echo "  System Settings → Privacy → Full Disk Access → + → /bin/bash (Cmd+Shift+G)"
echo "  Terminal/Cursor FDA does NOT apply to background launchd jobs."
