# Cursor User Rules（对话级约定）

这些规则写在 Cursor **Settings → Rules**（对话注入），不是 `.cursor/rules/*.mdc`。  
以下为 2026-07-14 盘点时的能力摘要，改 UI 后请回写本节。

## 沟通与输出

- 默认用**简体中文**回复
- 对话标题：简体中文，准确概括任务（与 `chat-title.mdc` 一致）
- 简洁直接；少用大段加粗；长文先一句结论

## Git 安全

- **只有用户明确要求才 commit / push**
- 禁止改 git config；禁止 force push / hard reset（除非用户明示）
- 禁止 `--no-verify` 等跳过 hooks（除非明示）
- amend 条件极严：仅用户要求或 hook 改文件需补进，且未 push、且是本会话创建的 commit
- commit 前并行：`status` / `diff` / `log`；message 用 HEREDOC
- GitHub PR：用 `gh`；GitLab MR 走工作区 F2B + `gitlab-mcp` 规范（见 Rules）

## iDev2 建卡默认

- 技改 → 挂**当月**「票台 {N} 月技改」父 issue（如 7 月 GDS-9247）
- GDS Story 首次创建必带：`pdRoleIds: [713]`、`fields.customfield_7112`（影响面）、HTML `content`
- 默认不要在 GDS 顶层乱建卡

## 前端设计（若做 UI）

一套硬约束：单构图、品牌优先、避免紫渐变/奶油风等 AI 默认审美等（完整条文在 User Rules 原文）。

## 与 Workspace Rules 的关系

| 层级 | 例子 |
|------|------|
| User Rules | Git 安全、中文、iDev 建卡默认、文风 |
| Always Apply mdc | chat-title、F2B router、kb-daily-todo |
| 按需 mdc + Skills | F2B 手册、排障、FAT、Captain |

冲突时：**用户当轮显式指令 > User Rules > Workspace Rules**（与 AGENTS 一致）。
