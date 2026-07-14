# Cursor / Claude Skills

Skills = 可触发的 playbook（`SKILL.md`），比 Rule 更长、更可执行。

## A. IdeaProjects 工作区 Skills

路径：`~/IdeaProjects/.cursor/skills/`

| Skill | 何时用 |
|-------|--------|
| `gds-rail-triage` | 国际铁路订单/票台/VC 线上排障；必读 `stage-playbook.md` |
| `auto-test-log-triage` | 联调失败 / 打包未生效：BAT + Admin 串联排查 |
| `bat-clog-trace` | 按 appId+环境+message 查 CLOG → BAT trace 链接 |
| `fat-create-order` | FAT 生单出票（search→detail→createOrder） |
| `fat-order-lookup` | FAT 捞 Aaron 订单号 + Admin 日志链接 |
| `fat-qmq-send` | FAT/FWS 合法抛 Q（topic 白名单 + producer） |
| `captain-release` | Captain 镜像 / UAT / PRO 发布 |
| `gds-prod-release-observe` | 生单/出票高影响改动的**生产发布观察**（按发布集群拉单+技改断言；写 plan 时须先问用户要不要加） |
| `exception-config-assistant` | Mapping Error Config；草稿+审核，禁止 publish |
| `gds-api-deploy` | GitLab Maven Deploy `gds-ticketing-api` |
| `fat-test-route` | （目录存在，暂无 `SKILL.md`，待补） |

## B. Claude / 用户级业务 Skills

路径（内容基本一致，两处都有）：

- `~/.claude/skills/`
- `~/.cursor/skills/`（用户级镜像）

| Skill | 何时用 |
|-------|--------|
| `auto-place-order` | FAT/FWS 按供应商名或已有单自动生单 |
| `order-detail-query` | 按 orderId 查供应商订单多表详情 |
| `supplier-error-impact` | 供应报错关键词 → 影响面统计 |
| `supplier-lookup` | 供应商模块 → 负责人（离线 JSON） |
| `ticket-desk-issue-analysis` | iDev 票台需求解读 / 待办列表 |
| `ticket-desk-log-query` | 票台订单日志摘要 |
| `ticket-desk-log-detail` | 按 orderId + msgTrace 查 WARN/ERROR 明细 |

## C. Cursor 官方 Skills（`~/.cursor/skills-cursor/`）

偏编辑器/产品本身，不是业务域。

| Skill | 作用摘要 |
|-------|----------|
| `automate` | 创建 Cursor Automations |
| `create-rule` / `create-skill` / `create-hook` / `create-subagent` | 造规则/技能/钩子/子代理 |
| `canvas` | 分析结果用 Canvas 呈现 |
| `babysit` | PR 合入就绪循环 |
| `loop` | `/loop` 周期性跑 prompt/skill |
| `sdk` | Cursor SDK 集成开发 |
| `split-to-prs` | 大改动拆 PR |
| `review` / `review-bugbot` / `review-security` | Bugbot / 安全评审子代理 |
| `update-cursor-settings` / `update-cli-config` / `statusline` | 设置与 CLI |
| `onboard` / `shell` / `migrate-to-skills` | 入门、/shell、规则迁 Skills |

## D. Superpowers 插件 Skills

路径：`~/.cursor/plugins/cache/cursor-public/superpowers/.../skills/`

流程纪律类（会话开头 hooks 会注入 `using-superpowers`）：

| Skill | 作用 |
|-------|------|
| `using-superpowers` | 任务前先找 skill |
| `brainstorming` | 创意/新功能前先澄清设计 |
| `writing-plans` / `executing-plans` / `subagent-driven-development` | 计划与执行 |
| `systematic-debugging` / `test-driven-development` | 排障 / TDD |
| `verification-before-completion` | 声称完成前要证据 |
| `requesting-code-review` / `receiving-code-review` | CR 流程 |
| `using-git-worktrees` / `finishing-a-development-branch` | worktree / 收尾 |
| `dispatching-parallel-agents` / `writing-skills` | 并行子代理 / 写 skill |

## E. Codex Skill

| 路径 | 说明 |
|------|------|
| `~/.codex/skills/gds-api-deploy` | 与 Cursor `gds-api-deploy` 对齐的 Codex 版 |

## Rule ↔ Skill 配对速查

多数运维 Rule 只写「触发 + Read 哪份 SKILL」；细节在 Skill 里。详见 [[Rules]]。

### 近期变更

| 日期 | 变更 |
|------|------|
| 2026-07-14 | 新增工作区 Skill + Rule：`gds-prod-release-observe`（生产发布观察）；补充用户级路径 `~/.cursor/skills/` |
