# 晚间日报 Instructions（本机 Local Agent）

工作目录：`/Users/aaron/Documents/知识库`  
规范：必须先读 `Templates/daily-style-guide.md`（含 §5 iDev 三路、§6 合并规则）与 `Templates/topic-registry.yaml`。

**禁止**用 Cloud Automation 采 iDev2 / 飞书 / GitLab（内网 MCP 不可用）。晚间固定 **本机 Desktop Local Agent**。

## 流程

1. 运行 `python3 .scripts/collect-evening.py`（Cursor 会话 / Plan / Git）
2. **iDev2 三路 MCP**（见下方）→ 存临时 JSON → `collect-idev2.py` 写 `_staging/日期.idev2.json`
3. **飞书双查 MCP** → `collect-feishu.py` 写 `_staging/日期.feishu.json`
4. 再跑 `python3 .scripts/collect-evening.py --date 日期` 合并 sidecar 到 raw
5. 写或更新 `Daily/YYYY-MM-DD.md`（见下方合并规则）
6. 若是周五：再写或合并 `Weekly/YYYY-Www.md`
7. commit 并 push 知识库

## iDev2 三路 MCP（必做）

先看参数：

```bash
python3 .scripts/collect-idev2.py --date YYYY-MM-DD --print-queries
```

Agent 调 **三次** `iDev2-issue-query`，结果存 `/tmp/idev-created.json`、`/tmp/idev-story.json`（必选）、可选 `/tmp/idev-related.json`，再：

```bash
python3 .scripts/collect-idev2.py \
  --date YYYY-MM-DD \
  --created-json /tmp/idev-created.json \
  --scan-json /tmp/idev-story.json \
  --scan-json /tmp/idev-related.json
```

| 路 | MCP 参数 | sidecar 字段 |
|----|----------|--------------|
| ① 我创建 | `creator=TR043507` + 当日 `createdTimeStart/End` | `createdToday` |
| ② 今日指派给我 | `parentIssueId=8395325`（GDS-9247 子项）+ 客户端：`executiveObj.id=TR043507` 且 `creator≠TR043507` 且 `lastUpdatedTime` 当日 | `assignedTodayOnly` |
| ③ 指派给我且今日有更新 | 同 scan 源 + 客户端：`lastUpdatedTime` 当日且 `executiveObj.id=TR043507`（或 `updaterObj=TR043507`），排除 ①② | `updatedTodayOnly` |

**勿只依赖** `related=TR043507` top100（会漏 GDS-9534 等）；**必须**含 Story 子项查询。

`creator` 必须用 **工号 TR043507**，不要用 `zhaorun`。

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
- 工程明细仅在 `<details>` 参考区；iDev 参考区须含 **新建 / 今日新指派 / 今日更新** 三类

## 周五周报

合并本周 Daily 的「技改进展」，进度取最新一天；若 `Weekly/` 文件已存在，同样先读再合并，不覆盖用户手写内容。
