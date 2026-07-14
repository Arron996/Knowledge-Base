# Codex 与 Cursor 对齐

权威说明：`~/IdeaProjects/AGENTS.md`

## 原则

- **Cursor 为本**：MCP、Rules、Skills 以 Cursor/工作区配置为事实源
- Codex 对齐现有约定，不另起并行体系
- 有 `.codegraph/` 时先用 CodeGraph，再 `rg`/读文件

## 对齐清单

| 维度 | Cursor 位置 | Codex 应做的事 |
|------|-------------|----------------|
| MCP | `.mcp.json` / `~/.cursor/mcp.json` | 同名服务、同工作流 |
| Rules | `.cursor/rules/*.mdc` | 命中触发条件先读对应文件 |
| Skills | `.cursor/skills/*/SKILL.md` | 同 playbook |
| RTK | — | 读 `~/.codex/RTK.md` |
| 待办 | `kb-daily-todo.mdc` | 写 Obsidian Daily，不写飞书 |
| 标题 | `chat-title.mdc` | 简体中文短标题 |

## AGENTS 中已映射的工作流

- F2B / MR / 大文件最小 diff
- 飞书挂载 / 技改模板
- Clean Code / MapStruct / 无中文日志
- Admin stage、BAT、FAT 生单/捞单/发 Q、Captain、异常配置、AREX 排查、API Deploy
- 生产发布观察（`gds-prod-release-observe`）：生单/出票高影响 → 先问用户再按集群拉单校验

新增工具时：改 Cursor 配置 → 更新 `AGENTS.md` → 更新本库 [[README]] 与对应子页。
