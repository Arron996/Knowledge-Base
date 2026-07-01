# 日报 / 周报生成规范

Agent 生成或更新 [`Daily/YYYY-MM-DD.md`](../Daily/) 前**必须先读本文**。

## 1. 正文原则

- 按 **技改需求名称** 组织，禁止按 git / iDev Story / 数据源堆砌
- 禁止正文出现：分支名、commit hash、feat/fix、MR 编号、「X 笔提交」
- 每个技改：名称 + 简要说明 + 飞书链接（若有）+ **业务进度符号**
- 工程明细只放 `## 📎 参考` 折叠区

## 1.1 什么**不**进日报（过滤规则）

`_staging` 里的 `cursorChats` 会**全量采集**（含日常闲聊），但写 Daily 时 Agent **必须过滤**：

| 进日报 | 不进日报 |
|--------|----------|
| 与 **GDS / 票台 / Admin / 订单 / 技改 / iDev / 飞书方案** 相关的排查、设计、开发 | 生活、兴趣、工具玩法、Obsidian/编辑器配置等**与业务无关**的小问题 |
| 线上订单 / 慢 SQL / 退票 / GDPR 等工作排查 | 「这句话怎么写」「简单语法错误」且**无法对应任何技改**的一次性问答 |
| 当日技改 Plan / 文档校订 | 纯聊天、非工作话题 |
| 日报/周报自动化本身（可归入「工作流」技改或当日主线一句） | 重复、已废弃会话 |

**操作要求**：

- **正文 `## 📊 技改进展`**：只写工作技改；**不得**为日常问答单独开 Callout
- **「其他（排查）」**：仅 **工作域** 且未立项的线上/技术排查；Personal 内容 **禁止** 出现
- **参考区 `Cursor 会话`**：只列**与工作相关**的标题；文末可写 `已忽略 N 条非工作会话`（不必列标题）
- **今日主线**：只概括工作；不写「今天还问了 XXX 生活问题」

**边界示例**：

- ✅ 纳入：`1359045587196037 线上退票金额 0 排查`、`SLA 慢 SQL 时间分片`
- ❌ 排除：`钢琴怎么练`、`报销清单`、`Cursor 自动化怎么配（纯产品咨询且与技改无关）` — 除非当日主线就是「搭建日报工作流」这一技改

用户可说：「今日 Daily 排除会话：……」强制剔除。

## 2. 进度符号

| 符号 | 含义 | 典型信号 |
|------|------|----------|
| 📐 设计中 | 新建方案，未写代码 | 今日新建飞书 wiki / Plan，无 git |
| ✏️ 方案校订中 | 改 Plan / 改已有飞书 doc | `plans` mtime 今日；`feishu.editedTodayOnly` |
| 🔍 调研中 | **工作域**排查、读需求 | 订单/慢 SQL/技改相关 Cursor 会话 |
| 👀 评审中 | 等 CR / 方案评审 | MR comment / 未合码 |
| 🔄 处理中 | 开发进行中 | iDev DOING；可附「下周一发生产」 |
| 🧪 测试中 | 已合测分 / 灰度 | git merge 测分；口述灰度 % |
| ⏳ 待发生产 | 等发布窗口 | 测分通过 |
| ⏳ 问题待解决 | 阻塞 | 会话/blocker |
| ✅ 已发布 | 已上生产 | iDev DONE + 已上线语境 |
| ✅ 已下线 | 下线完成 | 下线类技改 |
| 📝 已完成 | 规划/文档类交付 | H2 规划等 |

## 3. 轻工作日（无 coding、无 iDev 更新）

**必须正常出日报**，不得写「今日无工作」。

### 信号来源（优先级）

1. `_staging/日期.feishu.json` → `createdToday` + `editedTodayOnly`
2. `_staging/日期.raw.json` → `plans`（**mtime 今日 = 校订也算**）
3. `cursorChats` → 讨论方案、校订 doc
4. git / idev2 为空 **不影响**正文

### 进度映射

| 情况 | 进度 |
|------|------|
| 仅新建 Plan / 飞书 doc | 📐 设计中 |
| 改已有 Plan / 改已有飞书（`editedTodayOnly`） | ✏️ 方案校订中 |
| 新建 + 当日又编辑 | 以 ✏️ 为主 |
| 排查会话、未立项 | 🔍 调研中，放「其他（排查）」Callout |

### 轻工作日示例

```markdown
> [!abstract] 今日主线
> 两项技改方案校订；无代码提交。

> [!abstract]- SLA 统计并发时间分片 · [飞书](url)
>
> | 子项 | 进度 |
> | :--- | ---: |
> | 并发分片技改方案 | ✏️ 方案校订中 |
> | Cursor Plan 对齐 | ✏️ 方案校订中 |
```

### 明日待办

从校订结论推导，例如：「方案评审通过后开 iDev」「启动 admin-fe 开发」。

## 3.1 待办分栏（明日 vs 待排期）

日报里**两种待办**，禁止混在一栏：

| 区块 | 何时用 | 优先级 | 早晨怎么用 |
|------|--------|--------|------------|
| `## 📋 明日待办` | **已决定明天要做**的事 | 🔴 必做 · 🟡 重要 · 🟢 可后 | 次日打开**昨日** Daily，按此安排今天 |
| `## 🗂️ 待排期` | **想做、未排期、有空再做**；评估类、能力补齐、排查后续 | 🔵 无日期压力 | 本周有空再扫一眼，**不**当作次日必做 |

**Agent 归类规则**：

- 排查得出「以后要评估 / 要补能力 / 待产品拍板」→ **`待排期`**，**不要**默认塞进明日待办
- 用户明确说「明天做」「下周一做」→ `明日待办`（可附日期备注）
- iDev「待敏捷排期」类技改 follow-up → 优先 `待排期`，除非用户指定明天推进
- 晚间写日报时：若昨日 `待排期` 有未完成项，**滚动到今天**（去重合并），勿丢、勿擅自改成明日待办

**示例**：

```markdown
## 📋 明日待办
- [ ] 🔴 SLA 分片 — 测分环境验证

## 🗂️ 待排期
- [ ] 🔵 改签 completeExchange — 评估是否补 Admin 人工重试入口
- [ ] 🔵 GDPR 票台 — 是否发邮件（等产品确认）
```


- 每个技改一块：`> [!type]- 标题`（`-` = 默认折叠）
- 块内 **2 列表**，进度列 `| ---: |`
- **禁止** 列表 + 空格顶进度；**禁止** 超长 3 列大表
- Callout 类型：success=已发布 / example=测试灰度 / note=处理中 / abstract=设计校订 / warning=阻塞

frontmatter 建议：`cssclasses: [daily-report]`

## 5. 数据采集文件

| 文件 | 内容 |
|------|------|
| `_staging/YYYY-MM-DD.raw.json` | Cursor / Plan / Git + queryHints |
| `_staging/YYYY-MM-DD.idev2.json` | iDev 创建 + lastUpdatedTime 扭转 |
| `_staging/YYYY-MM-DD.feishu.json` | 飞书 createdToday + editedTodayOnly |

### iDev2 查询（MCP）

- `creator=TR043507`（**不要** zhaorun）
- 时间：**Asia/Shanghai 当日**毫秒，禁止手写错误年份
- **三路合并**：
  1. `createdTimeStart/End` + `creator=TR043507` → `createdToday`
  2. `executiveObj.id=TR043507` + `createtime` 在当日 + `creator≠TR043507` → `assignedTodayOnly`（他人创建、今日指派给我）
  3. 宽查 + `lastUpdatedTime` 在当日且 `executiveObj.id=TR043507`（或 `updaterObj.id=TR043507`），排除已在 1/2 → `updatedTodayOnly`

### 飞书查询（MCP）

1. **今日创建**：`create_time=[当天, 当天]` + `owners=[open_id]`
2. **今日校订**：`sort_rule=EDIT_TIME` 拉近期，`update_time` 落在当天且 **非**当天创建 → `editedTodayOnly`

合并命令：

```bash
python3 .scripts/collect-feishu.py \
  --date YYYY-MM-DD \
  --created-json /tmp/feishu-created.json \
  --edited-json /tmp/feishu-edited.json
```

## 6. 晚间合并规则（Automation 必读）

`Daily/YYYY-MM-DD.md` **可能白天已被用户手改**。晚间生成时**禁止整篇清空重写**。

### 若当日 Daily 已存在

1. **先读取**现有 `Daily/日期.md` 全文
2. **保留**用户手写的 `## 📋 明日待办` 与 `## 🗂️ 待排期`：
   - 所有 `- [ ]` / `- [x]` **勾选状态**
   - 用户新增、改写的条目与优先级（🔴🟡🟢 / 🔵）
   - **禁止**把「待排期」擅自挪到「明日待办」，或反向挪动（除非用户原文如此）
3. **技改进度以用户为准**（当与 staging 冲突时）：
   - 用户已在 Callout 中写的进度符号 / 备注 → **不降级、不删除**
   - staging 仅用于**补充**用户未写的技改、刷新参考区、推断用户未覆盖的子项
4. **可更新 / 补充**：
   - `> [!abstract] 今日主线`（合并用户表述与采集结论，取更完整者）
   - `## 📊 技改进展`：增补 Callout 或子项行；**勿删除**用户已有技改块
   - `## 📎 参考`：用最新 sidecar 刷新折叠区（可用 `format-daily-ref.py`）
5. **禁止**：因重新采集而把用户白天记录整篇覆盖为「仅机器数据」版本

### 若当日 Daily 不存在

按模板 [`daily-note.md`](daily-note.md) **新建**全文。

### 周报（仅周五）

合并**本周已有 Daily** 的技改进展；进度取**最新一天**；`## 📋 下周计划` 仅合并各日 **明日待办** 中未完成且仍属下周的项；`待排期` **不进**周报必做列表，可选在周报末尾 `## 🗂️ 持续待排期` 列最新一天快照。

## 7. 手动补录 prompt

```
按 Templates/daily-style-guide.md 更新今日 Daily，补充：……
```

**分栏示例**：

```
按 style-guide 更新今日 Daily：
- 技改进展：completeExchange VC 重试排查 → 🔍 调研中（已结论，见会话）
- 待排期（不要放明日待办）：🔵 改签 completeExchange — 评估 Admin 人工重试入口
```

```
按 style-guide 更新今日 Daily，明日待办：🔴 历史版本对比 admin-fe 开干
```

白天在 Obsidian / Cursor 已手写的内容，补录时须遵守 §6 合并规则，不得覆盖用户待办勾选与进度。

## 8. 晚间 Agent 检查清单

- [ ] 读 raw + idev2 + feishu sidecar
- [ ] **若 Daily 已存在 → 先读全文，走 §6 合并规则**
- [ ] **过滤** cursorChats：非工作/日常小问题不进正文与参考列表
- [ ] git/iDev 空 → 走轻工作日规则
- [ ] 聚合成技改 Callout（非数据源段落）
- [ ] 参考区折叠；飞书区分「新建 / 校订」
- [ ] **保留**用户「明日待办」「待排期」勾选与分栏；昨日待排期滚动合并
