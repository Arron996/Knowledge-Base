#!/usr/bin/env bash
# One-time setup for knowledge-base automation.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing Python deps..."
python3 -m pip install --user -r "$SCRIPT_DIR/requirements.txt"

echo "Installing Node deps (@cursor/sdk)..."
(cd "$SCRIPT_DIR" && npm install)

if [[ -z "${CURSOR_API_KEY:-}" ]]; then
  echo ""
  echo "CURSOR_API_KEY is not set."
  echo "Create a key at https://cursor.com/dashboard/integrations"
  echo "Then add to ~/.zshrc.local:"
  echo '  export CURSOR_API_KEY="cursor_..."'
  echo ""
  echo "LaunchAgents read the same variable from plist EnvironmentVariables."
fi

echo "Done. Run: bash $SCRIPT_DIR/evening-daily.sh (requires CURSOR_API_KEY + VPN)"
