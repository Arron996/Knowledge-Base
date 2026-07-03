#!/usr/bin/env bash
# Load user secrets (CURSOR_API_KEY) for launchd jobs.
set -a
if [[ -f "${HOME}/.zshrc.local" ]]; then
  # shellcheck disable=SC1091
  source "${HOME}/.zshrc.local"
fi
set +a
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
exec "$@"
