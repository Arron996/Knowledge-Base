#!/usr/bin/env bash
# macOS notification helper for automation failures.
set -euo pipefail

TITLE="${1:-知识库自动化}"
MSG="${2:-未知错误}"

/usr/bin/osascript -e "display notification \"${MSG}\" with title \"${TITLE}\"" 2>/dev/null || true
