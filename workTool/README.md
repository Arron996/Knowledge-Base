# workTool · 工作工具盘点

> 个人积累的 Cursor / Obsidian / Codex / 定时任务工具总览。  
> 盘点日期：2026-07-14；**Skills 同步：2026-07-14 傍晚**（新增 `gds-prod-release-observe`）。  
> 由 Agent 从本机配置扫描生成，**不含任何 token/密钥**。

本目录只做**索引与说明书**，真正的规则/脚本仍在原路径；改工具请改源文件，再按需回来更新本章。

## 快速入口

| 主题 | 文档 |
|------|------|
| 东西都在哪 | [[配置地图]] |
| Cursor Rules | [[Cursor/Rules]] |
| Cursor Skills | [[Cursor/Skills]] |
| MCP | [[Cursor/MCP]] |
| 插件 / Hooks / 扩展 | [[Cursor/插件Hooks扩展]] |
| User Rules（对话级约定） | [[Cursor/UserRules]] |
| 日报 / 周报 / launchd | [[自动化/日报周报定时任务]] |
| IdeaProjects 辅助脚本 | [[辅助脚本]] |
| Codex 对齐 | [[Codex对齐]] |

## 一句话架构

```text
~/.cursor/mcp.json          ← 用户级 MCP（最全）
IdeaProjects/.mcp.json      ← 工作区 MCP 子集（AGENTS.md 事实源之一）
IdeaProjects/.cursor/rules  ← 业务 Rules（always + 按需）
IdeaProjects/.cursor/skills ← 业务 Skills（playbook）
~/.cursor/skills-cursor     ← Cursor 官方技能
~/.claude/skills            ← Claude 侧业务技能（部分 Cursor 也可见）
知识库/.scripts + launchd   ← 早 9 / 晚 19 日报周报
~/bin/sync-my-mrs*          ← 工作日每 5 分钟同步 MR + 自动合入
```

## 维护约定

1. **密钥不进库**：MCP token、Private-Token、CURSOR_API_KEY 只写在本机 secret 文件，本目录只记「有哪些 header / 从哪加载」。
2. **改了工具就改索引**：新增 Rule/Skill/MCP/定时任务时，至少更新对应子页 + 本 README 日期。
3. **业务笔记仍放原处**：技改领域知识 → `领域/`；排障套路 → `工程/`；每日待办 → `Daily/`。`workTool` 只登记「工具本身」。
