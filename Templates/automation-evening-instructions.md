# 晚间 Automation Instructions（粘贴到 Cursor Automation）

工作目录：`/Users/aaron/Documents/知识库`  
规范：必须先读 `Templates/daily-style-guide.md`（含 §6 晚间合并规则）与 `Templates/topic-registry.yaml`。

## 流程

1. 若可访问本机：运行 `python3 .scripts/collect-evening.py`；否则读取已 push 的 `_staging/今日.*.json`
2. MCP 采集 iDev2（`creator=TR043507`，createtime + lastUpdatedTime 双路）→ `_staging/日期.idev2.json`
3. MCP 飞书 `search-doc` 双查（今日创建 + EDIT_TIME 校订）→ `collect-feishu.py` 写 `_staging/日期.feishu.json`
4. 可选：GitLab `list_user_events` 记入参考区
5. 写或更新 `Daily/YYYY-MM-DD.md`（见下方合并规则）
6. 若是周五：再写或合并 `Weekly/YYYY-Www.md`
7. commit 并 push 知识库

## 合并规则（重要）

若 `Daily/今日.md` **已存在**：

- **先读取**现有全文，**禁止整篇清空重写**
- **保留**用户手写的 `## 📋 明日待办` 与 `## 🗂️ 待排期`：勾选状态、分栏不混用
- 昨日未勾选的 **待排期** 项滚动合并到今天（去重）
- 用户手写的技改进度若与采集冲突，**以用户为准**；staging 仅补充用户未写的技改与子项
- 可更新：今日主线、补充技改进展 Callout、刷新 `## 📎 参考` 折叠区
- 过滤非工作 Cursor 会话（style-guide §1.1）

若文件不存在：按 `Templates/daily-note.md` 新建。

## 正文要求

- 技改维度 + 业务进度语言；Callout 分块 + 2 列表
- 正文禁止：分支名、commit hash、MR 编号、Story Issue 堆砌
- 工程明细仅在 `<details>` 参考区

## 周五周报

合并本周 Daily 的「技改进展」，进度取最新一天；若 `Weekly/` 文件已存在，同样先读再合并，不覆盖用户手写内容。
