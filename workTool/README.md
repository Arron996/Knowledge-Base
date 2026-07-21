# workTool · 工作工具盘点

> 个人积累的 Cursor / Obsidian / Codex / 定时任务工具总览。  
> 盘点日期：2026-07-14；**Rules/Skills 原文镜像：2026-07-20**。  
> 由 Agent 从本机配置扫描生成，**不含任何 token/密钥**。

## 存放原则

| 类型 | 本目录怎么放 |
|------|----------------|
| **Rules** | **原文镜像** → `Cursor/rules/*.mdc` + 索引 [[Cursor/Rules]] |
| **Skills**（业务） | **原文镜像** → `Cursor/skills/workspace/`、`skills/user/` + 索引 [[Cursor/Skills]] |
| **User Rules** | **原文镜像** → [[Cursor/UserRules]] |
| **MCP** | **仅索引/引用** → [[Cursor/MCP]]（不落配置正文，防泄密） |
| 官方 Skills / Superpowers | 仅索引（产品自带，不镜像） |
| 脚本 / launchd | 说明书 + 路径引用 |

运行时仍以本机源路径为准；本目录是备份与可读副本。改工具先改源，再按同步命令回写镜像。

## 快速入口

| 主题 | 文档 |
|------|------|
| 东西都在哪 | [[配置地图]] |
| Cursor Rules（索引 + 原文目录） | [[Cursor/Rules]] |
| Cursor Skills（索引 + 原文目录） | [[Cursor/Skills]] |
| MCP（仅引用） | [[Cursor/MCP]] |
| 插件 / Hooks / 扩展 | [[Cursor/插件Hooks扩展]] |
| User Rules（原文） | [[Cursor/UserRules]] |
| 日报 / 周报 / launchd | [[自动化/日报周报定时任务]] |
| IdeaProjects 辅助脚本 | [[辅助脚本]] |
| Codex 对齐 | [[Codex对齐]] |

## 一句话架构

```text
~/.cursor/mcp.json          ← 用户级 MCP（最全）—— workTool 只记名单
IdeaProjects/.mcp.json      ← 工作区 MCP 子集
IdeaProjects/.cursor/rules  ← 业务 Rules 源  → 镜像 workTool/Cursor/rules/
IdeaProjects/.cursor/skills ← 业务 Skills 源 → 镜像 workTool/Cursor/skills/workspace/
~/.claude/skills            ← 用户级 Skills 源 → 镜像 workTool/Cursor/skills/user/
~/.cursor/skills-cursor     ← Cursor 官方技能（不镜像）
知识库/.scripts + launchd   ← 早 9 / 晚 19 日报周报
~/bin/sync-my-mrs*          ← 工作日每 5 分钟同步 MR + 自动合入
```

## 维护约定

1. **密钥不进库**：MCP token、Private-Token、CURSOR_API_KEY 只写在本机 secret 文件；MCP 页只记「有哪些 header / 从哪加载」。
2. **Rules / Skills 改完要同步镜像**：用 [[Cursor/Rules]]、[[Cursor/Skills]] 文末同步命令。
3. **业务笔记仍放原处**：技改领域知识 → `领域/`；排障套路 → `工程/`；每日待办 → `Daily/`。
