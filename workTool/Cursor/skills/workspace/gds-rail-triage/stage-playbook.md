# Admin MCP 日志 Stage / Action 速查

> **用途**：任何需要 `user-gds-order-admin-mcp` 查日志的排障，**先读本页定参，再调 MCP**。  
> 完整 SOP 见 [SKILL.md](SKILL.md)；工具边界见 [mcp-tools.md](mcp-tools.md)。

## 黄金顺序（必须）

```
1. 分类场景（创单/出票/改签/退票/售后变更/凭证/通知…）
2. 从代码解析 stage 或 actions（本节下文）
3. query-ticket-logs：优先 stage 或 actions；rawOnly=true 看报文
4. 从结果提取 msgTrace
5. 【消费断链】有 *Consumer、无下游 vc#/结果 MQ → bat-trace（queryLog=true）必做，再下结论
6. 否则：msgTrace → bat-trace（首选）或 bat-clog（勿用 filterKey 冒充 CLOG title）
7. 空结果：换 actions / 换层 / 换 queryIdc，同一参数最多试 1 次；bat-clog 空 → bat-trace
```

**禁止起手**：`filterKey=topic片段` 广撒网（慢、易漏、易空）。

---

## 参数选型决策

| 情况 | MCP 参数 | 示例 |
|------|----------|------|
| 场景在内置 stage 表 | `stage` | `stage=pay_order` |
| MQ topic / RPC action 已知 | `actions`（逗号分隔） | `actions=train.global.rail.gds.order.ticketing.monitor.alteration` |
| 需缩到子单/退改单 | `actions` + `filterKey` | `filterKey=<refundId>` |
| 仅有订单号、场景未知 | `stage=book_order` 或 `stage=pay_order` 试探 1 次 | 禁止无参查询 |
| 查运行时 WARN/堆栈 | `bat-trace` + `messageId`（首选）；或 `bat-clog` + `messageId` |

`actions` 与 `stage`：**有明确 action 时用 actions**（设置后忽略 stage）。

---

## 代码里找 stage / action（3 个锚点）

### 锚点 A：内置 stage 注册表（首选）

```
gds-order-admin-be/.../biz/mcp/service/TicketLogStageRegistry.java
```

| stage | 包含的 actions（Mongo `action` 字段） |
|-------|--------------------------------------|
| `book_order` | `ticket#createOrder`, `vc#createOrder`, `trn.gds.ticketing.system.create.order.result`, … |
| `pay_order` | `vc#completeOrder`, `trn.gds.ticketing.system.complete.order.result`, … |
| `apply_refund` | `ticket#applyRefund`, `vc#applyRefund` |
| `process_refund` | `ticket#confirmRefund`, `vc#confirmRefund`, `ticket#refundEvent`, … |
| `refund_result` | `train.global.rail.gds.ticketing.sub.refund.result` |
| `apply_exchange` | `ticket#applyExchange`, `vc#applyExchange` |
| `exchange_book_order` | `ticket#createExchangeOrder`, `vc#createExchange`, `train.global.rail.gds.ticketing.create.exchange.sub.order` |
| `exchange_pay_order` | `ticket#completeExchangeOrder`, `vc#completeExchange`, `train.global.rail.gds.ticketing.complete.exchange.sub.order` |

**不在表内**的业务（售后变更、取票、X 产品等）→ 用锚点 B/C 找 topic，走 `actions`。

### 锚点 B：MQ topic 常量

```
gds-ticketing-system/.../domain/constant/QmqConstant.java
gds-order-system/.../common/constant/MessageQueueConstants.java
```

Grep：`TOPIC_` / `after.sale` / 场景关键词 → 常量值即 `actions`。

### 锚点 C：消费者 / 发送方

```
Grep: @QmqConsumer\(prefix
Grep: sendWithLog\(|messageQueue\.send\(
```

- `@QmqConsumer(prefix = X)` → 消费侧 Mongo action 多为 **X** 或 **Consumer 类名**
- `sendWithLog(TOPIC, …)` → 发送侧 Mongo action 多为 **TOPIC 字符串**

---

## 场景 → MCP 参数速查

| 场景 | 推荐 MCP 调用 |
|------|----------------|
| 创单/扣位 | `stage=book_order` |
| 出票 | `stage=pay_order` |
| 卡出票 | `stage=pay_order`；若仅有 Consumer 无 `vc#completeOrder` → 加 `actions=CompleteSubOrderConsumer` 取 msgTrace → **bat-trace** |
| 申请改签 | `stage=apply_exchange` |
| 改签扣位 | `stage=exchange_book_order` |
| 改签出票 | `stage=exchange_pay_order` |
| 申请退票 | `stage=apply_refund` |
| 退票处理 | `stage=process_refund` |
| 退票结果 MQ | `stage=refund_result` 或 `actions=train.global.rail.gds.ticketing.sub.refund.result` |
| **售后变更监控** | `actions=train.global.rail.gds.order.ticketing.monitor.alteration,CompleteAlterationConsumerService` |
| **售后变更 VC 侧** | `actions=train.global.rail.gds.order.vc.monitor.alteration` |
| **售后变更推订单** | `actions=train.global.rail.gds.order.after.sale.change` |
| 售后解析 | `actions=train.global.rail.gds.order.ticketing.inner.parse.after.sale.info` |
| 取票 | `actions=ticket#obtainTicket` 或 Grep `TOPIC_OBTAIN` |
| 用户通知 | `query-order-messages`（非 ticket-logs） |
| 子单/退改单缩小 | 在上述基础上加 `filterKey=<subBatchId/refundId/orderItemId>` |

### 售后变更示例（票台 Mongo）

```json
{
  "orderId": "<id>",
  "actions": "train.global.rail.gds.order.ticketing.monitor.alteration,CompleteAlterationConsumerService",
  "rawOnly": true
}
```

验证是否已通知订单：

```json
{
  "orderId": "<id>",
  "actions": "train.global.rail.gds.order.after.sale.change",
  "rawOnly": true
}
```

---

## action 命名规律

| 模式 | 含义 | 示例 |
|------|------|------|
| `ticket#*` | 订单 → 票台 RPC | `ticket#createOrder` |
| `vc#*` | 票台 → VC | `vc#completeOrder` |
| `trn.gds.ticketing.system.*` | 票台 → 订单 结果 MQ | `trn.gds.ticketing.system.complete.order.result` |
| `train.global.rail.gds.*` | 业务 MQ topic | `train.global.rail.gds.order.after.sale.change` |
| `*ConsumerService` / 类名 | 消费处理节点 | `CompleteAlterationConsumerService` |

Mongo 日志 `action` 字段 = MCP `actions` 入参（精确匹配，非模糊）。

---

## 空结果快速判断

| 现象 | 下一步 |
|------|--------|
| `after.sale.change` 空、monitor 有日志 | 监控已跑但未推送订单；查 CLOG `sendSuccessMsg2Order` |
| 全部空 | 确认 `pre-query-order` IDC；换 `stage=book_order` 验证订单是否有日志 |
| 有 monitor 无 consumer | 消费未执行或 action 名不对；Grep Consumer 类名补 actions |
| **有 Consumer 无下游**（如 `CompleteSubOrderConsumer` 有、`vc#completeOrder` 无） | **bat-trace**（Consumer 的 msgTrace）；根因在 Consumer/Processor 内，勿先猜限流 |
| bat-clog messageId 空 | 改 `queryIdc` 试 1 次 → **bat-trace** |
| 有报文无 WARN | Mongo 正常；若业务仍卡住，用 bat-trace 看运行时 ERROR（Mongo 不记堆栈） |

---

## 维护说明

新增 MCP 内置 stage 时改 `TicketLogStageRegistry.java`；**未注册进 stage 的 MQ 节点**在本 playbook「场景速查」补一行即可，无需改 MCP 代码。
