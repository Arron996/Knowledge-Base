# Cursor Rules

> **原文镜像**：本目录 `rules/`（2026-07-20 自 `~/IdeaProjects/.cursor/rules/` 同步）。  
> **运行时仍以 IdeaProjects 源文件为准**；改规则先改源，再 `cp` 回本目录。  
> MCP 仅索引，见 [[MCP]]。

触发方式：`alwaysApply: true` 常驻；否则 Agent 按 description / AGENTS 策略按需 `Read`。

## 原文目录

`workTool/Cursor/rules/*.mdc`

另：`kb-daily-todo.knowledge-base.mdc` = 知识库侧精简版（源：`知识库/.cursor/rules/kb-daily-todo.mdc`）；完整 always 版为 `kb-daily-todo.mdc`。

## Always Apply（常驻）

| 文件 | 作用 |
|------|------|
| [[rules/chat-title.mdc\|chat-title.mdc]] | 会话标题 `rename_chat`：简体中文；Plan 模式不豁免 |
| [[rules/git-f2b-router.mdc\|git-f2b-router.mdc]] | F2B 规则调度：Plan 读 branch-policy；执行读 workflow |
| [[rules/kb-daily-todo.mdc\|kb-daily-todo.mdc]] | 「记待办」写 Obsidian Daily，禁止误写飞书 |

## 按需 · Git / 交付

| 文件 | 触发 |
|------|------|
| [[rules/git-f2b-branch-policy.mdc\|git-f2b-branch-policy.mdc]] | Plan / 制定合 base 计划 |
| [[rules/git-f2b-workflow.mdc\|git-f2b-workflow.mdc]] | F2B、提交、推送、合 base、建 MR、CR |
| [[rules/gitlab-mr-description.mdc\|gitlab-mr-description.mdc]] | 创建/更新 MR |
| [[rules/large-file-minimal-diff.mdc\|large-file-minimal-diff.mdc]] | 改火车/汽船/admin 大 Java 存量类 |

## 按需 · 文档

| 文件 | 触发 |
|------|------|
| [[rules/feishu-doc-mount.mdc\|feishu-doc-mount.mdc]] | 写飞书技改/需求/方案文档 |
| [[rules/tech-transformation-template.mdc\|tech-transformation-template.mdc]] | 按技改模板写文档 |
| [[rules/idev2-mcp.mdc\|idev2-mcp.mdc]] | iDev2 建卡/克隆/更新 |

## 按需 · 编码约定

| 文件 | 触发 |
|------|------|
| [[rules/clean-code.mdc\|clean-code.mdc]] | Clean Code / 重构可读性 |
| [[rules/java-mapstruct-over-beanutils.mdc\|java-mapstruct-over-beanutils.mdc]] | Java 对象拷贝：优先 MapStruct |
| [[rules/no-chinese-in-logs-and-code.mdc\|no-chinese-in-logs-and-code.mdc]] | 日志与业务字符串禁用中文 |
| [[rules/ticketing-system-project-conventions.mdc\|ticketing-system-project-conventions.mdc]] | 出票系统模块与规范 |

## 按需 · 运维 / 联调（多对 Skill）

| 文件 | 对应 Skill（原文在 [[skills/]]） |
|------|------------|
| [[rules/bat-clog-trace.mdc\|bat-clog-trace.mdc]] | `skills/workspace/bat-clog-trace` |
| [[rules/captain-release.mdc\|captain-release.mdc]] | `skills/workspace/captain-release` |
| [[rules/gds-prod-release-observe.mdc\|gds-prod-release-observe.mdc]] | `skills/workspace/gds-prod-release-observe` |
| [[rules/fat-create-order.mdc\|fat-create-order.mdc]] | `skills/workspace/fat-create-order` |
| [[rules/fat-order-lookup.mdc\|fat-order-lookup.mdc]] | `skills/workspace/fat-order-lookup` |
| [[rules/fat-qmq-send.mdc\|fat-qmq-send.mdc]] | `skills/workspace/fat-qmq-send` |
| [[rules/gds-admin-log-stage.mdc\|gds-admin-log-stage.mdc]] | 常配 `gds-rail-triage` |

## 调度关系（F2B）

```text
用户说 Plan / 合 base
  → git-f2b-router（always）
  → Plan: Read branch-policy
  → 执行: Read workflow（+ 建 MR 时 Read gitlab-mr-description）
```

## 同步命令

```bash
cp ~/IdeaProjects/.cursor/rules/*.mdc \
  "/Users/aaron/Documents/知识库/workTool/Cursor/rules/"
cp "/Users/aaron/Documents/知识库/.cursor/rules/kb-daily-todo.mdc" \
  "/Users/aaron/Documents/知识库/workTool/Cursor/rules/kb-daily-todo.knowledge-base.mdc"
```

详见 [[../Codex对齐]]、[[UserRules]]。
