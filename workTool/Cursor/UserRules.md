# Cursor User Rules（已迁入 Workspace）

> **2026-07-21**：原 Settings → Rules（账号绑定）条文已合并到 `~/IdeaProjects/.cursor/rules/`，**换账号也可生效**。  
> 运行时以 IdeaProjects 源文件为准；本目录 `rules/` 为镜像。  
> 历史原文见 git 历史；下方为迁移对照表。

---

## 迁移对照

| 原 User Rule | IdeaProjects `.cursor/rules/` | 策略 |
|--------------|-------------------------------|------|
| committing-changes-with-git | [[rules/git-commit-safety.mdc]] | `alwaysApply` |
| creating-pull-requests | [[rules/github-pull-request.mdc]] | 按需（GitHub PR）；GitLab 仍走 F2B |
| 前端设计 | [[rules/frontend-design.mdc]] | 按需 |
| 沟通与输出 | [[rules/communication-style.mdc]] | `alwaysApply` |
| iDev2 建卡默认约定 | [[rules/idev2-mcp.mdc]] | 已有，已补全字段 |
| 对话标题 | [[rules/chat-title.mdc]] | 已有，未重复新建 |

冲突时：**用户当轮显式指令 > Workspace Rules**。

账号侧 Settings → Rules 可清空重复项，避免双份注入。
