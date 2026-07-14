# 插件 · Hooks · 扩展

## Cursor Plugins

| 插件 | 路径 / 说明 |
|------|-------------|
| **superpowers** | `~/.cursor/plugins/cache/cursor-public/superpowers/` — 流程 Skills（见 [[Skills]] D 节） |

本地插件目录：`~/.cursor/plugins/local/`（可空）。

## VS Code 兼容扩展（`~/.cursor/extensions/`）

| 扩展 | 作用 |
|------|------|
| `anysphere.remote-ssh` | Remote SSH |
| `git-ai.git-ai-vscode` | git-ai 与 hooks 配合做 checkpoint |
| `ms-ceintl.vscode-language-pack-zh-hans` | 中文语言包 |

## Hooks（`~/.cursor/hooks.json`）

| 事件 | 命令 | 作用 |
|------|------|------|
| `preToolUse`（matcher: Shell） | `rtk hook cursor` | Shell 命令走 RTK 钩子 |
| `preToolUse` | `git-ai checkpoint cursor --hook-input stdin` | 工具调用前 checkpoint |
| `postToolUse` | 同上 git-ai checkpoint | 工具调用后 checkpoint |

其它事件（`sessionStart` / `sessionEnd` / `stop` / `beforeSubmitPrompt` / `afterFileEdit`）当前为空数组。

备份：`hooks.json.bak`、`hooks.json.skillclaw-disabled-*.bak`。

## 用户设置摘录

`~/Library/Application Support/Cursor/User/settings.json`：

- `git.path` → `/Users/aaron/.git-ai/bin/git`（git-ai 包装）
- `cursor.composer.usageSummaryDisplay` → `always`

## IdeaProjects 辅助 Scripts（非 Hook，但常配合）

见 [[../辅助脚本]]：`mr-auto-merge-approved.sh`、`pre-commit-format.sh`、`fat-qmq-send.sh` 等。

## Automations

- Skill：`skills-cursor/automate`（如何创建 Cloud/Local Automation）
- 知识库晚间日报：**不用** Cloud Automation 采内网 MCP；固定本机 SDK Local Agent（见 [[../自动化/日报周报定时任务]]）
