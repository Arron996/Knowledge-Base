#!/usr/bin/env bash
# Shared secret loader for launchd wrappers (do not exec).
load_kb_secrets() {
  if [[ -n "${CURSOR_API_KEY:-}" ]]; then
    return 0
  fi
  local keyfile="${HOME}/.config/kb-automation/cursor_api_key"
  if [[ -f "$keyfile" ]]; then
    CURSOR_API_KEY="$(tr -d '[:space:]' < "$keyfile")"
    export CURSOR_API_KEY
    return 0
  fi
  if [[ -f "${HOME}/.zshrc.local" ]]; then
    # shellcheck disable=SC1091
    source "${HOME}/.zshrc.local"
  fi
}
