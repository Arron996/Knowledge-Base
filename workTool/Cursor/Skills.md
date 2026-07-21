# Cursor / Claude Skills

> **原文镜像**：`skills/workspace/`（IdeaProjects）、`skills/user/`（`~/.claude/skills`）。  
> **运行时仍以本机源目录为准**；改 skill 先改源，再 rsync 回本目录。  
> Cursor 官方 Skills / Superpowers **仍只做索引**（产品自带，不镜像）。  
> MCP 仅索引，见 [[MCP]]。

Skills = 可触发的 playbook（`SKILL.md`），比 Rule 更长、更可执行。

## 原文目录

| 镜像路径 | 源 |
|----------|-----|
| `workTool/Cursor/skills/workspace/<name>/` | `~/IdeaProjects/.cursor/skills/<name>/` |
| `workTool/Cursor/skills/user/<name>/` | `~/.claude/skills/<name>/`（与 `~/.cursor/skills/` 对齐） |

## A. 工作区 Skills（原文已镜像）

| Skill | 何时用 | 原文 |
|-------|--------|------|
| `gds-rail-triage` | 国际铁路订单/票台/VC 线上排障 | [[skills/workspace/gds-rail-triage/SKILL\|SKILL.md]] |
| `auto-test-log-triage` | 联调失败 / 打包未生效 | [[skills/workspace/auto-test-log-triage/SKILL\|SKILL.md]] |
| `bat-clog-trace` | CLOG → BAT trace | [[skills/workspace/bat-clog-trace/SKILL\|SKILL.md]] |
| `fat-create-order` | FAT 生单出票 | [[skills/workspace/fat-create-order/SKILL\|SKILL.md]] |
| `fat-order-lookup` | FAT 捞单 + Admin 日志 | [[skills/workspace/fat-order-lookup/SKILL\|SKILL.md]] |
| `fat-qmq-send` | FAT/FWS 合法抛 Q | [[skills/workspace/fat-qmq-send/SKILL\|SKILL.md]] |
| `captain-release` | Captain 发布 | [[skills/workspace/captain-release/SKILL\|SKILL.md]] |
| `gds-prod-release-observe` | 生产发布观察 | [[skills/workspace/gds-prod-release-observe/SKILL\|SKILL.md]] |
| `exception-config-assistant` | Mapping Error Config | [[skills/workspace/exception-config-assistant/SKILL\|SKILL.md]] |
| `gds-api-deploy` | Maven Deploy `gds-ticketing-api` | [[skills/workspace/gds-api-deploy/SKILL\|SKILL.md]] |
| `fat-test-route` | （目录在；`SKILL.md` 可能待补） | `skills/workspace/fat-test-route/` |

## B. 用户级业务 Skills（原文已镜像）

| Skill | 何时用 | 原文 |
|-------|--------|------|
| `auto-place-order` | FAT/FWS 自动生单 | [[skills/user/auto-place-order/SKILL\|SKILL.md]] |
| `order-detail-query` | 供应商订单多表详情 | [[skills/user/order-detail-query/SKILL\|SKILL.md]] |
| `supplier-error-impact` | 供应报错影响面 | [[skills/user/supplier-error-impact/SKILL\|SKILL.md]] |
| `supplier-lookup` | 供应商负责人 | [[skills/user/supplier-lookup/SKILL\|SKILL.md]] |
| `ticket-desk-issue-analysis` | iDev 票台需求解读 | [[skills/user/ticket-desk-issue-analysis/SKILL\|SKILL.md]] |
| `ticket-desk-log-query` | 票台日志摘要 | [[skills/user/ticket-desk-log-query/SKILL\|SKILL.md]] |
| `ticket-desk-log-detail` | 按 msgTrace 查明细 | [[skills/user/ticket-desk-log-detail/SKILL\|SKILL.md]] |

## C. Cursor 官方 Skills（仅索引，不镜像）

路径：`~/.cursor/skills-cursor/`

| Skill | 作用摘要 |
|-------|----------|
| `automate` | 创建 Cursor Automations |
| `create-rule` / `create-skill` / `create-hook` / `create-subagent` | 造规则/技能/钩子/子代理 |
| `canvas` | Canvas 呈现 |
| `babysit` | PR 合入就绪循环 |
| `loop` | `/loop` |
| `sdk` | Cursor SDK |
| `split-to-prs` | 大改动拆 PR |
| `review` / `review-bugbot` / `review-security` | 评审子代理 |
| `update-cursor-settings` / `update-cli-config` / `statusline` | 设置与 CLI |
| `onboard` / `shell` / `migrate-to-skills` | 入门、/shell、迁移 |

## D. Superpowers 插件 Skills（仅索引，不镜像）

路径：`~/.cursor/plugins/cache/cursor-public/superpowers/.../skills/`

`using-superpowers`、`brainstorming`、`writing-plans`、`executing-plans`、`systematic-debugging`、`test-driven-development`、`verification-before-completion`、`requesting-code-review`、`receiving-code-review`、`using-git-worktrees`、`finishing-a-development-branch`、`dispatching-parallel-agents`、`writing-skills`、`subagent-driven-development` 等。

## E. Codex Skill（仅索引）

| 路径 | 说明 |
|------|------|
| `~/.codex/skills/gds-api-deploy` | 与 Cursor `gds-api-deploy` 对齐 |

## 同步命令

```bash
WT="/Users/aaron/Documents/知识库/workTool/Cursor/skills"
rsync -a --delete --exclude node_modules --exclude .git \
  ~/IdeaProjects/.cursor/skills/ "$WT/workspace/"
rsync -a --delete --exclude node_modules --exclude .git \
  ~/.claude/skills/ "$WT/user/"
```

### 近期变更

| 日期 | 变更 |
|------|------|
| 2026-07-20 | 业务 Skills **改为原文镜像**（workspace + user）；官方/插件仍索引 |
| 2026-07-14 | 新增 `gds-prod-release-observe` |
