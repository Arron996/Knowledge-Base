# 晚间日报 Instructions（19:00 本机 SDK Local Agent）

工作目录：`/Users/aaron/Documents/知识库`  
规范：必须先读 `Templates/daily-style-guide.md`（含 §5 iDev 三路、§6 合并规则）与 `Templates/topic-registry.yaml`。

**禁止**用 Cloud Automation 采 iDev2 / 飞书 / GitLab（内网 MCP 不可用）。晚间固定 **本机 SDK Local Agent**（`kb-evening-agent.mjs` + `@cursor/sdk`）。

早间滚待办 / 周五 Weekly 见 [`automation-morning-instructions.md`](automation-morning-instructions.md)（**不在此流程写 Weekly**）。

## 调度

| 时间 | 脚本 | 产出 |
|------|------|------|
| 工作日 19:00 | `evening-daily.sh` | `Daily/{今天}.md` + git push |

## 自动化入口

```bash
bash .scripts/evening-daily.sh              # 今天
bash .scripts/evening-daily.sh 2026-07-02   # 补跑指定日
```

Shell 顺序：本地采集 → SDK Agent → git push。需 `CURSOR_API_KEY`（`~/.zshrc.local` 或 launchd 经 `kb-run-with-env.sh` 加载）。

## Agent 流程

1. 运行 `python3 .scripts/collect-evening.py --date 今天`（Cursor 会话 / Plan / Git）
2. **iDev2 三路 MCP**（见下方）→ 存临时 JSON → `collect-idev2.py` 写 `_staging/日期.idev2.json`
3. **飞书双查 MCP** → `collect-feishu.py` 写 `_staging/日期.feishu.json`
4. **GitLab MR** → `list_user_merge_requests(author,merged)` → `collect-gitlab.py` 写 `_staging/日期.gitlab.json`
5. 再跑 `python3 .scripts/collect-evening.py --date 日期` 合并 sidecar 到 raw
6. 写或更新 `Daily/YYYY-MM-DD.md`（见下方合并规则）
7. **不要** git commit/push（shell 脚本负责）

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
| ① 我创建 | `creator=TR043507` + 当日 `createdTimeStart/End` | 客户端：`executive=我` → `createdToday`；`creator=我且executive≠我` → `delegatedToday`（**不计入**日报/周报） |
| ② 今日指派给我 | `parentIssueId=8395325`（GDS-9247 子项）+ 客户端：`executiveObj.id=TR043507` 且 `creator≠TR043507` 且 `lastUpdatedTime` 当日 | `assignedTodayOnly` |
| ③ 指派给我且今日有更新 | 同 scan 源 + 客户端：`executiveObj.id=TR043507` 且 `lastUpdatedTime` 当日，排除 ①② | `updatedTodayOnly` |

**勿只依赖** `related=TR043507` top100（会漏 GDS-9534 等）；**必须**含 Story 子项查询。

`creator` 必须用 **工号 TR043507**，不要用 `zhaorun`。

## GitLab MR 采集（必做）

```bash
python3 .scripts/collect-gitlab.py --date YYYY-MM-DD --print-queries
```

MCP `list_user_merge_requests`（`username=zhaorun`, `role=author`, `state=merged`）→ `/tmp/gitlab-merged.json` →

```bash
python3 .scripts/collect-gitlab.py --date YYYY-MM-DD --merged-json /tmp/gitlab-merged.json
```

按 `merged_at` 筛当日合入；`releaseStage=production`（target 为 main/master）→ 正文 **✅ 已发生产**；测分分支 → 🧪 测试中。

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
- 工程明细仅在 `<details>` 参考区；iDev 参考区须含 **新建 / 今日新指派 / 今日更新** 三类；`delegatedToday` 单独标注「不计入我的 iDev」

## SDK 与环境

```bash
bash .scripts/setup.sh   # pip chinese-calendar + npm @cursor/sdk
export CURSOR_API_KEY="cursor_..."   # ~/.zshrc.local
bash .scripts/install-launchd.sh     # 19:00 + 09:00
```

日志：`~/Library/Logs/kb-evening.log`。失败时 macOS 通知。

## 手动 Agent prompt（其他 Cursor 会话）

```
工作目录：/Users/aaron/Documents/知识库
按 Templates/automation-evening-instructions.md 和 daily-style-guide.md
为今天 YYYY-MM-DD 生成/更新 Daily（§6 合并，不写 Weekly）
```
