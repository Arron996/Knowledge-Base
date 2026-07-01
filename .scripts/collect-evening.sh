#!/bin/zsh
# 晚间采集：Cursor 会话 + Plan + Git → _staging/YYYY-MM-DD.raw.json
python3 "$(dirname "$0")/collect-evening.py" "$@"
