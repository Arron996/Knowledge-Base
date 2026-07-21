---
name: gds-rail-triage
description: |
  国际铁路 GDS（订单/票台/VC）通用线上排障 playbook。先分类、再从代码定 stage/actions、再调 Admin MCP，少空跑。
  适用于创单/出票/改签/退票/售后变更/凭证/X 产品/通知未达等排查；
  用户提到排障、根因、日志空、msgTrace、订单不同步、Admin MCP、query-ticket-logs、MCP 返回空时使用。
  查日志前必读 stage-playbook.md。
---

# GDS 铁路排障 Playbook

> **Playbook** = 固定排查剧本（SOP），不是 MCP 参数手册。  
> 设计参考：[ticket-desk-triage Skill（Redis 原文）](https://trip.larkenterprise.com/wiki/UXntw6JDLi6j2wkSrOhc51TCnjT)  
> MCP 工具细节见 [mcp-tools.md](mcp-tools.md)  
> **Stage/Action 速查**（查 Admin MCP 前必读）：[stage-playbook.md](stage-playbook.md)

## 核心原则（必须遵守）

1. **先分类，再查** — 不确定场景时只查「概要日志」，不要广撒网
2. **先代码定 stage/actions，再 MCP** — 读 `TicketLogStageRegistry` / `QmqConstant` / `@QmqConsumer`，用 `stage` 或 `actions` 精准查；**禁止起手 filterKey 广撒网**（见 stage-playbook.md）
3. **先状态/报文，再 trace** — Mongo 操作日志 → msgTrace → **bat-trace（首选）** → bat-clog 补 WARN/ERROR
4. **分清工具边界** — Mongo `action`/`filterKey` ≠ CLOG `title`（见 mcp-tools.md）
5. **并行第一轮，串行第二轮** — 路由/MQ/通知可并行；CLOG 必须等 msgTrace
6. **空结果要换参，不要重复** — 同一错误参数最多试 1 次，换 actions 或换层
7. **用户已有证据优先用** — VC request/response、截图、时间点可跳过验证性查询
8. **代码 Grep 补日志文案** — 已知处理类时，Grep `log.warn` 文案再回 CLOG 用 `title` 查
9. **消费断链必钻消费者** — Mongo 有 `*Consumer` 消费记录、但无下游 action（如 `vc#completeOrder`）→ **根因几乎必在 Consumer 内部**；立即 `bat-trace`，禁止仅凭代码推测

## 第 0 步：收集输入（向用户确认或从上下文提取）

| 字段 | 用途 |
|------|------|
| `orderId` | 主键，几乎所有 MCP 必需 |
| 现象一句话 | 决定场景分类 |
| 大概时间 / 子单号 / refundId | 缩 CLOG 时间窗、filterKey |
| 环境 | 生产/测试（订单号通常自动识别） |
| 已有 VC/订单报文 | **有则跳过「有没有发/有没有收」验证** |
| 怀疑层级 | 票台 / 订单 / VC / 通知 |

缺 `orderId` 时停止，先索要。

## 第 1 步：问题分类

选 **一个主场景**（可附带次要）：

| 场景 | 典型现象 | 优先查什么 |
|------|----------|------------|
| 创单/扣位 | 生单失败、扣位失败 | 票台 createOrder + vc#createOrder |
| 出票 | 出票失败、卡出票 | completeOrder / queryOrder |
| 改签 | 改签失败、状态不对 | applyExchange + exchange 阶段 |
| 退票 | 退票失败、状态卡住 | applyRefund / confirmRefund / refundEvent |
| 售后变更 | 行程/凭证变更后下游未同步 | actions=monitor.alteration + CompleteAlterationConsumerService；推订单用 after.sale.change |
| 凭证/PDF | 电子票、PDF 缺失或未更新 | obtainTicket / orderDetail / voucher |
| X 产品 | X 单出退改异常 | xorder 相关 action |
| 通知 | 用户未收到短信/推送 | query-order-messages |
| 暂时未知 | 仅订单号 | 概要日志 + 主单状态 |

分类决定 **stage / filterKey / actions**，不要全表全日志扫一遍。

## 第 2 步：标准排查顺序

```
Task Progress:
- [ ] 2a 路由信息（channel / IDC / 环境）
- [ ] 2b 订单/票台概要日志（Mongo，含 VC 报文）
- [ ] 2c 提取 msgTrace + 关键时间点
- [ ] 2d BAT trace / CLOG（2c 有 msgTrace 必查；**消费断链时 2d 优先于 2f 代码推测**）
- [ ] 2e 订单侧交叉验证（通知、消费、状态）
- [ ] 2f 代码 Grep（日志文案 / 处理链路）
- [ ] 2g 输出结论（按模板）
```

### 2a 路由信息（1 次，可与 2b 并行）

```text
MCP: user-gds-order-admin-mcp → pre-query-order
参数: { "orderId": "<id>" }
得到: channel（TripTrain/trainpal）、idc（SGP/SHA/...）
```

CLOG 的 `queryIdc` 必须与 idc 一致（海外单常用 `SGP-ALI`，默认 SHA 会空）。

可选：`query-order` **mini** 看订单主状态（full 常不稳定，勿反复重试）。

### 2b 概要日志（1～2 次，按场景选参）

**查 Admin MCP 前**：Read [stage-playbook.md](stage-playbook.md)，从代码定 `stage` 或 `actions`。

**票台 + VC 报文**（首选）：

```text
MCP: user-gds-order-admin-mcp → query-ticket-logs
```

| 场景 | 推荐参数 |
|------|----------|
| 内置阶段 | `stage=book_order` / `pay_order` / `apply_refund` / `process_refund` / `apply_exchange` / `exchange_book_order` / `exchange_pay_order` |
| 售后变更 | `actions=train.global.rail.gds.order.ticketing.monitor.alteration,CompleteAlterationConsumerService`；验证推订单：`actions=train.global.rail.gds.order.after.sale.change` |
| 凭证 | `actions=ticket#obtainTicket` 或 Grep `TOPIC_OBTAIN` |
| 未知 | `stage=book_order` 或 `pay_order` 试探 1 次；**禁止**无 stage/actions/filterKey（必空） |
| 缩子单 | 在上述基础上加 `filterKey=<subBatchId/refundId>` |

**订单侧概要**（不含票台递归）：

```text
MCP: query-order-logs（仅 book/pay/refund/exchange 阶段）
```

售后变更、通知类 **不要** 用 query-order-logs 的 filterKey 硬查。

**全链路递归**（仅当需订单+票台一次拉齐，且接受更慢）：

```text
MCP: query-logs + stage 或 filterKey
```

### 2c 从概要日志提取

从 2b 结果中记录：

- `msgTrace` / traceId（CLOG 的 `messageId`）
- 异常时间点（UTC，供 bat-clog 时间窗 ±10min）
- 关键 action（`vc#*` / `ticket#*` / MQ topic）
- request/response 差异（尤其 VC 与票台 DB/MQ payload 是否一致）

### 2d BAT 明细（有 msgTrace 必查；消费断链时**强制**）

#### 首选：`bat-trace`（比 bat-clog 更可靠）

```text
MCP: user-bat-mcp-function → bat-trace
必填: env, messageId=<msgTrace>
推荐: queryLog=true（一次拿到 CAT 树 + 内嵌 CLOG ERROR/WARN）
```

BAT 链接（可直接给用户）：

- 生产：`https://bat.fx.ctripcorp.com/trace/{msgTrace}`
- 测试：`https://bat.fws.qa.nt.ctripcorp.com/trace/{msgTrace}`

在 trace 内重点搜：`ERROR`、`system error`、`BusinessException`、`CRedis`、`NeedRetryException`、Processor 类名。

#### 备选：`bat-clog`（trace 已够用则不必重复；trace 空或需按 title 补查时用）

```text
MCP: user-bat-mcp-function → bat-clog
必填: env, appId, fromUtc, toUtc
推荐: messageId=<msgTrace>, queryIdc=<2a的IDC>, queryLargeFields=on, logLevel=2,3
```

| 系统 | appId |
|------|-------|
| 票台 gds-ticketing-system | 100051894 |
| 订单 gds-order-system | 100045149 |

**bat-clog 按 messageId 返回空时**：换 `queryIdc` 仅试 1 次 → **立即改 bat-trace**，不要转代码推测。

时间不确定时先调 `bat-global-helper`。

**禁止**：在票台 appId 下用订单 Consumer 类名当 `source`；禁止无时间窗全量扫订单号；**禁止 bat-clog 空了就跳过 2d**。

### 2d+ MQ 消费断链（高频踩坑）

**触发条件**（满足任一即进入本分支）：

| Mongo 有 | Mongo 无（预期应有） | 推断 |
|----------|---------------------|------|
| `CompleteSubOrderConsumer` | `vc#completeOrder` | 出票 Consumer 内中断 |
| `CreateSubOrderConsumer` | `vc#createOrder` | 创单 Consumer 内中断 |
| 任意 `*Consumer` / topic action | 该 Consumer 应对应的下游 `vc#*` / 结果 MQ | **Consumer 内失败或提前 return** |

**动作（按序，禁止跳步）**：

1. 从 Consumer 那条 Mongo 日志取 `msgTrace`
2. **`bat-trace` + `queryLog=true`**（不要用「只有 Consumer 记录」当结论）
3. 在 trace 中定位 Processor（如 `CompleteSubOrderProcessor`）内的 ERROR 栈
4. 对照代码看失败行（Redis / DB / 限流 preCheck / 状态机 CAS 等）
5. 确认 MQ 是否被 ack（`AbstractProcessor` 吞掉非 BusinessException 会导致**消费了但不重试**）

**反例（本次工单教训）**：只看到 `CompleteSubOrderConsumer` 已消费、`vc#completeOrder` 缺失，就推测「出票池限流」—— 实际 trace 显示 Redis `setEX` 超时。

### 2e 订单侧交叉验证

```text
query-order-messages        → 通知是否发出（sendState=200）
query-order-message-log     → 需 requestKey，看发送明细
query-order mini            → 订单状态与票台是否一致
```

DOT/DB 直连：无权限时跳过，不反复尝试。

### 2f 代码 Grep（本地，零 MCP 成本）

当 CLOG/Mongo 指向某处理类但根因不明：

1. Grep 异常日志字符串（如 `is error`、`skip`、`emptyCandidate`）
2. 读对应 Service/Processor 分支条件
3. 用 Grep 到的 **title** 回 bat-clog，不要用 query-ticket-logs 的 filterKey

## 第 3 步：空结果处理决策树

```
MCP 返回空
├─ 是否无 stage/actions？ → 读 stage-playbook，从代码补 actions（仅 1 次）
├─ 是否用了 filterKey 冒充 topic？ → 改 actions=完整 topic 或 Consumer 类名
├─ 是否查 CLOG title 用了 query-ticket-logs？ → 改 bat-clog + title
├─ bat-clog 按 messageId 空？ → 改 queryIdc（1 次）→ 仍空则 bat-trace（必做，不等用户贴链接）
├─ 有 Consumer 无下游？ → 不要用代码猜；用 Consumer 的 msgTrace 做 bat-trace（§2d+）
├─ 是否 IDC 错误？ → pre-query-order 后改 queryIdc
├─ 是否时间窗不对？ → 按 MQ 时间 ±10min 缩窗
├─ 是否用错 appId？ → 票台/订单分开查
└─ 仍空 → 向用户要 BAT trace 链接 / VC 报文；Grep @QmqConsumer 补全链路；不要循环同一参数
```

## 第 4 步：输出模板（必须按此结构回复）

```markdown
## 1. 订单基础信息
- 环境（pro/fws）、orderId、channel、IDC、供应商、主/子单状态

## 2. 异常概况
- 场景分类、受影响范围（哪段子单/退改/凭证）
- 关键日志摘要（保留 msgTrace，拼 BAT 链接）
  - 生产：https://bat.fx.ctripcorp.com/trace/{msgTrace}
  - 测试：https://bat.fws.qa.nt.ctripcorp.com/trace/{msgTrace}

## 3. 根本原因
- 基于日志 + 报文 + 代码的具体根因（避免「可能」链式猜测）
- 区分：VC 未返回 / **Consumer 已消费但 Processor 内失败** / 票台未发 MQ / 订单未消费 / 通知被过滤

## 4. 责任归属
- 票台系统自身问题：是/否
- 依据：仅当明确 Java Exception（非 BusinessException）且属票台代码缺陷时为「是」；BusinessException/VC 业务拒绝一般为「否」

## 5. 解决方案与操作建议
- 修复方向（配置/代码/人工补偿）
- 后续验证步骤（如何确认已恢复）
```

## 场景速查（stage / actions）

**完整速查表**见 [stage-playbook.md](stage-playbook.md)；action 列表见 [mcp-tools.md](mcp-tools.md#场景-action-对照)。

| 场景 | query-ticket-logs 首选 |
|------|------------------------|
| 创单/扣位 | `stage=book_order` |
| 出票 | `stage=pay_order` |
| 申请改签 | `stage=apply_exchange` |
| 改签出票 | `stage=exchange_pay_order` |
| 申请退票 | `stage=apply_refund` |
| 退票结果 | `stage=process_refund` 或 `stage=refund_result` |
| 售后变更监控 | `actions=train.global.rail.gds.order.ticketing.monitor.alteration,CompleteAlterationConsumerService` |
| 售后变更推订单 | `actions=train.global.rail.gds.order.after.sale.change` |
| 取票/电子票 | `actions=ticket#obtainTicket` |
| 卡出票 | `stage=pay_order`；有 Consumer 无 `vc#` → Consumer 的 msgTrace + **bat-trace** |

## 三系统边界（排障视角）

| 项目 | 仓库 | 主分支 | 测试分支 | appId |
|------|------|--------|----------|-------|
| 票台 | gds-ticketing-system | master | develop/base_20260528_bt3 | 100051894 |
| 订单 | gds-order-system | master | - | 100045149 |
| admin-be | gds-order-admin-be | master | develop/base_20260421 | - |

日志 action 前缀：`ticket#` = 订单调票台；`vc#` = 票台调 VC；`train.global.rail.gds.*` = MQ topic。

## 反模式（禁止）

- 无分类连续盲试 10+ 次 MCP
- **未读 stage-playbook 就用 filterKey 猜 topic**（慢且易空）
- 用 CLOG title 当 query-ticket-logs 的 filterKey
- query-order full 失败反复重试
- 无 msgTrace 时用 message=订单号 扫全量 CLOG
- 无 DB 权限反复 DOT SQL
- 仅凭代码推测，不拿日志/报文佐证就下根因结论
- **有 `*Consumer` 消费记录、无下游 action，却不做 bat-trace**（Consumer 内 ERROR 是唯一可靠根因来源）
- **bat-clog 按 messageId 空就放弃 2d**，直接 Grep 代码猜限流/并发

## 关联资源

- **Stage/Action 速查（查 Admin MCP 前必读）**：[stage-playbook.md](stage-playbook.md)
- Cursor rule（Admin MCP 日志查询入口）：`.cursor/rules/gds-admin-log-stage.mdc`
- 票台 triage 原文（Redis）：[飞书 wiki](https://trip.larkenterprise.com/wiki/UXntw6JDLi6j2wkSrOhc51TCnjT)
- MCP 工具边界与参数：[mcp-tools.md](mcp-tools.md)
- 项目分支/F2B：`.cursor/rules/git-f2b-workflow.mdc`
- 票台分层与规范：`.cursor/rules/ticketing-system-project-conventions.mdc`
