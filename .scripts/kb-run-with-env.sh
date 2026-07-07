#!/usr/bin/env bash
# Load secrets for launchd jobs (launchd does NOT inherit Terminal/zsh env).
set -a
# shellcheck disable=SC1091
source "$(dirname "$0")/kb-load-secrets.sh"
load_kb_secrets
set +a
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${HOME}/bin:${PATH:-}"
exec "$@"
