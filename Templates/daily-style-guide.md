# 日报风格指南

## 1. 正文结构

1. **Callout（今日主线）**：1–2 句概括当日最重要产出或决策。
2. **技改进度**：按 `topic-registry.yaml` 分组表格，列：技改 | 子项 | 进度。
3. **明日待办**：用户可手写维护；Agent 晚间仅合并、不覆盖勾选状态。
4. **参考区**：工程明细（Cursor / Plan / Git / 飞书 / iDev2 / MR），默认折叠或置底。

### 1.1 非工作会话过滤

写入参考区前过滤以下 Cursor 会话（标题或首条 user_query 命中即剔除）：

- 知识库 / Obsidian / 日报 / 周报 **自动化本身**的 meta 会话（如「每日工作流自动化」「rename_chat」「commit push 知识库」）
- 纯闲聊、插件配置、与本 registry 无关的个人笔记
- 重复会话：同一 `chatId` 或标题高度相似（编辑距离 < 3）只保留最新一条

技改进度表**仅**收录 registry 内主题或当日 iDev2 / 飞书 / Git 可映射项；临时排查挂在「其他（排查，未立项）」。

## 2. 进度符号

| 符号 | 含义 |
|:-----|:-----|
| ✅ | 已发布 / 已完成 |
| 🧪 | 测试中 |
| 🔄 | 处理中 |
| 📐 | 设计中 |
| 🔍 | 调研中 |
| 📅 | 待排期 |
| ⬜ | 未开始 |
| 📝 | 文档已完成 |

## 3. 参考区格式

- Cursor：`💬 Cursor 会话（N）` + 标题列表，>10 条用「…共 N 条」
- Plan：`📋 Plan（N）`
- Git：按 repo 分组，commit 带 emoji 前缀（✨🐛♻️🔀）
- 飞书：`📝 飞书文档（今日创建 N）`
- iDev2：表格 + 链接，注明双路查询（createtime + lastUpdatedTime）
- GitLab MR：`🔀 GitLab MR`

## 4. Frontmatter

```yaml
---
date: YYYY-MM-DD
tags: [daily]
weekday: 周X
status: open
---
```

## 5. 周报（仅周五）

- 路径：`Weekly/YYYY-Www.md`（ISO 周）
- 合并当周 `Daily/*.md` 的 Callout + 技改进度变化 + 未完成待办
- 已存在则先读后合并，禁止整篇覆盖

## 6. 合并规则（晚间 Agent）

当 `Daily/今日.md` 或 `Daily/YYYY-MM-DD.md` **已存在**时：

1. **必须先读取**现有全文，禁止整篇清空重写。
2. **明日待办**：保留用户勾选状态（`- [x]` / `- [ ]`）及用户新增项；Agent 可追加建议项但不得删除用户项。
3. **技改进度**：若用户手写进度**新于**采集数据（含 status 符号、备注），**以用户为准**；Agent 仅**补充**新 issue / 新子项 / 状态前进（如 🔄→🧪），不得回退用户已更新状态。
4. **参考区**：每次晚间**全量刷新**（Cursor / Plan / Git / 飞书 / iDev2 / MR）。
5. **Callout**：可更新；若用户已写 Callout 且更具体，保留用户表述并微调措辞。
6. 归档：`Daily/今日.md` 与 `Daily/YYYY-MM-DD.md` 内容应对齐；若仅存在 dated 文件则直接更新 dated 文件。

## 7. 采集侧车

| 文件 | 来源 |
|:-----|:-----|
| `_staging/YYYY-MM-DD.raw.json` | `collect-evening.py` |
| `_staging/YYYY-MM-DD.idev2.json` | iDev2 MCP 双路（TR043507） |
| `_staging/YYYY-MM-DD.feishu.json` | 飞书 MCP 双查 + `collect-feishu.py` |
