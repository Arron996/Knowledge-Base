# Cursor Rules

源目录：`~/IdeaProjects/.cursor/rules/`  
知识库镜像规则：`知识库/.cursor/rules/kb-daily-todo.mdc`（与工作区同步用途）

触发方式：`alwaysApply: true` 常驻；否则 Agent 按 description / AGENTS 策略按需 `Read`。

## Always Apply（常驻）

| 文件 | 作用 |
|------|------|
| `chat-title.mdc` | 会话标题 `rename_chat`：简体中文；Plan 模式不豁免 |
| `git-f2b-router.mdc` | F2B 规则调度：Plan 读 branch-policy；执行读 workflow；核心禁止项 |
| `kb-daily-todo.mdc` | 「记待办」写 Obsidian Daily，禁止误写飞书 |

## 按需 · Git / 交付

| 文件 | 触发 |
|------|------|
| `git-f2b-branch-policy.mdc` | Plan / 制定合 base 计划 |
| `git-f2b-workflow.mdc` | F2B、提交、推送、合 base、建 MR、CR |
| `gitlab-mr-description.mdc` | 创建/更新 MR（三问、自动合入、删源分支） |
| `large-file-minimal-diff.mdc` | 改火车/汽船/admin 大 Java 存量类 |

## 按需 · 文档

| 文件 | 触发 |
|------|------|
| `feishu-doc-mount.mdc` | 写飞书技改/需求/方案文档 |
| `tech-transformation-template.mdc` | 明确要求「按技改模板」写文档 |
| `idev2-mcp.mdc` | iDev2 建卡/克隆/更新 |

## 按需 · 编码约定

| 文件 | 触发 |
|------|------|
| `clean-code.mdc` | Clean Code / 重构可读性 |
| `java-mapstruct-over-beanutils.mdc` | Java 对象拷贝：优先 MapStruct |
| `no-chinese-in-logs-and-code.mdc` | 日志与业务字符串禁用中文 |
| `ticketing-system-project-conventions.mdc` | 出票系统模块与规范 |

## 按需 · 运维 / 联调（多对 Skill）

| 文件 | 对应 Skill |
|------|------------|
| `bat-clog-trace.mdc` | `bat-clog-trace` |
| `captain-release.mdc` | `captain-release` |
| `gds-prod-release-observe.mdc` | `gds-prod-release-observe`（先问要不要监控，再执行） |
| `fat-create-order.mdc` | `fat-create-order` |
| `fat-order-lookup.mdc` | `fat-order-lookup` |
| `fat-qmq-send.mdc` | `fat-qmq-send` |
| `gds-admin-log-stage.mdc` | 查 Admin 日志前定 stage；常配 `gds-rail-triage` |

## 调度关系（F2B）

```text
用户说 Plan / 合 base
  → git-f2b-router（always）
  → Plan: Read branch-policy
  → 执行: Read workflow（+ 建 MR 时 Read gitlab-mr-description）
```

详见 [[../Codex对齐]] 中 AGENTS 加载策略镜像。
