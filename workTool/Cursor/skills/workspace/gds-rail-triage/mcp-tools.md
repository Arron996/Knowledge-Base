# MCP 工具边界参考

排障前先确认：**查的是哪一层数据、用什么键**。  
**Stage/Action 怎么定**：先读 [stage-playbook.md](stage-playbook.md)，再调 MCP。

## 从代码定参（Admin MCP 必做）

| 锚点文件 | 得到什么 |
|----------|----------|
| `gds-order-admin-be/.../TicketLogStageRegistry.java` | 内置 `stage` → actions 映射 |
| `gds-ticketing-system/.../QmqConstant.java` | MQ topic 字符串 → `actions` |
| `gds-order-system/.../MessageQueueConstants.java` | 订单侧 topic |
| Grep `@QmqConsumer(prefix` | 消费节点 action |
| Grep `sendWithLog(` | 发送节点 topic |

**调用优先级**：`actions`（精确）> `stage`（内置封装）> `filterKey`（仅缩子单号）

## 两层日志体系

| 层 | MCP 工具 | 存什么 | 用什么过滤 |
|----|----------|--------|------------|
| Mongo 操作日志 | `query-ticket-logs` / `query-order-logs` / `query-logs` | MQ 报文、VC request/response、业务节点流水 | `stage`、`filterKey`、`actions` |
| BAT CLOG | `bat-clog` | 运行时 log.warn/error、title、堆栈 | `messageId`(trace)、`title`、`source`、`tagKey/tagValue` |
| 链路拓扑 + 消费内 ERROR | `bat-trace` | CAT 调用链、Consumer 内 Processor 失败栈 | `messageId`；推荐 `queryLog=true` |

**无 orderId、按 message 查日志并要 trace 链接**：见 Skill [bat-clog-trace](../bat-clog-trace/SKILL.md)（appId + env + message → BAT URL）。

### 常见混淆（必空）

| 错误用法 | 正确用法 |
|----------|----------|
| `query-ticket-logs` + `filterKey=itemSegmentTicketEntity is error` | `bat-clog` + `title=*itemSegmentTicketEntity*` |
| `query-order-logs` + `filterKey=after.sale.change` | `query-ticket-logs` + `actions=train.global.rail.gds.order.after.sale.change` |
| `filterKey=alteration` 广撒网 | `actions=train.global.rail.gds.order.ticketing.monitor.alteration,CompleteAlterationConsumerService` |
| `query-ticket-logs` 无 stage/filterKey/actions | 必须至少一个，否则 **returns no logs** |
| `bat-clog` 默认 IDC=SHA 查海外单 | `pre-query-order` → `queryIdc=SGP-ALI` |
| `bat-clog` messageId 空就放弃 | **改 `bat-trace` + queryLog=true**（仍用同一 msgTrace） |
| 仅有 `*Consumer` Mongo 记录就当「已处理完」 | Consumer 只证明入队消费；无下游 action 必 bat-trace 钻 Processor |
| 票台 appId 查 `GdsOrderAfterSaleChangeConsumer` | 订单 appId `100045149` |

---

## user-gds-order-admin-mcp 工具选型

| 工具 | 查什么 | 何时用 |
|------|--------|--------|
| `pre-query-order` | channel、idc | **几乎总是第一步**，轻量 |
| `query-order` mini | 订单主状态、产品、P2P | 快速看状态；full 不稳定慎用 |
| `query-ticket-logs` | **仅票台** Mongo + 可选 BAT | 票台/VC/MQ 报文，**售后变更首选** |
| `query-order-logs` | **仅订单** Mongo | book/pay/refund/exchange 阶段 |
| `query-logs` | 订单 + **递归**票台/VC | 需要全链路且接受更慢 |
| `query-order-messages` | 用户通知发送记录 | 通知未达、验证订单是否推送 |
| `query-order-message-log` | 单条通知明细 | 需 `requestKey` from messages |
| `query-order-refunds` | 退票单 | 退票专项 |

### query-ticket-logs 参数

```json
{
  "orderId": "必填",
  "stage": "book_order | pay_order | apply_refund | process_refund | apply_exchange | exchange_book_order | exchange_pay_order",
  "filterKey": "Mongo 内容模糊匹配：topic名、orderItemId、refundId 等",
  "actions": "逗号分隔原始 action，设置后忽略 stage",
  "rawOnly": "true=跳过BAT，只要Mongo报文；看VC响应时建议true"
}
```

**规则**：`actions` 与 `stage` 二选一优先 actions；无 stage/actions/filterKey 不返回日志。完整 stage 表见 [stage-playbook.md](stage-playbook.md)。

---

## user-bat-mcp-function 工具选型

| 工具 | 何时用 |
|------|--------|
| `bat-global-helper` | 不确定 UTC 时间窗、appId 规则时 **先调一次** |
| `bat-trace` | **有 msgTrace 首选**；Mongo 有 Consumer 无下游；看 Processor 内 ERROR/Redis/DB |
| `bat-clog` | bat-trace 已够用可跳过；或需按 `title`/`source` 补查 WARN/ERROR |

### bat-trace 关键参数

```json
{
  "env": "pro | fws | uat",
  "messageId": "完整 msgTrace（来自 Mongo 或 BAT URL）",
  "queryLog": "true（推荐，内嵌 CLOG ERROR）"
}
```

### bat-clog 关键参数

```json
{
  "env": "pro | fws | uat",
  "appId": "100051894(票台) | 100045149(订单)",
  "fromUtc": "YYYY-MM-DDTHH:mm:ss.sssZ",
  "toUtc": "YYYY-MM-DDTHH:mm:ss.sssZ",
  "messageId": "完整 msgTrace，最精准",
  "title": "支持 like，如 updateDataInfo*",
  "message": "仅前128字符；长正文需 queryLargeFields=on",
  "queryLargeFields": "on",
  "queryIdc": "SHA | SGP-ALI | FRA-AWS",
  "logLevel": "2=WARN,3=ERROR",
  "source": "类名，支持 like"
}
```

**优先级**：`messageId` > `title` + 时间窗 > `message` 扫订单号

---

## 场景 action 对照

来源：`TicketLogStageRegistry` + `QmqConstant` + ticket-desk-triage。完整表见 [stage-playbook.md](stage-playbook.md)。

| 场景 | actions / stage |
|------|---------------------|
| 创单/扣位失败 | `stage=book_order` 或 `vc#createOrder`, `ticket#createOrder`, `trn.gds.ticketing.system.create.order.result` |
| 出票失败 | `stage=pay_order` 或 `trn.gds.ticketing.system.complete.order.result` |
| 卡出票 | `vc#completeOrder`, `vc#queryOrder` |
| 申请改签 | `stage=apply_exchange` |
| 改签出票 | `stage=exchange_pay_order` |
| 申请退票 | `stage=apply_refund` |
| 退票失败 | `stage=process_refund` 或 `train.global.rail.gds.ticketing.sub.refund.result`, `ticket#refundEvent` |
| 取票/电子票 | `ticket#obtainTicket` |
| 售后变更监控 | `train.global.rail.gds.order.ticketing.monitor.alteration`, `CompleteAlterationConsumerService` |
| 售后变更 VC | `train.global.rail.gds.order.vc.monitor.alteration` |
| 售后变更推订单 | `train.global.rail.gds.order.after.sale.change` |
| 暂时未知 | `stage=book_order` 或 `stage=pay_order` |

多 action **一次逗号分隔传入**，不要拆成多个 MCP 调用。

---

## 并行与串行建议

### 第一轮可并行

- `pre-query-order`
- `query-ticket-logs`（按场景 stage/filterKey）
- `query-order-messages`（若涉及通知）

### 必须串行

1. 概要日志 → 提取 msgTrace
2. **有 Consumer 无下游 → bat-trace（必做）**；否则 msgTrace → bat-trace（首选）或 bat-clog
3. 确认票台 MQ payload → 再查订单消费/通知

---

## 与 Redis 版 triage 工具名对照

| Redis/Admin 工具名 | Cursor MCP 等价 |
|--------------------|-----------------|
| queryOrderInfo | `query-order` mini；票台 DB 表暂无稳定 MCP |
| queryOrderLogSummary | `query-ticket-logs` / `query-order-logs` |
| queryOrderLogDetail | `bat-clog`(messageId) 或 query-ticket-logs 默认模式(含BAT) |

---

## 订单状态码速查（概要）

| 常量 | 码 | 含义 |
|------|-----|------|
| SEAT_BOOKING | 150 | 扣位中 |
| SEAT_BOOK_SUCCESS | 200 | 扣位成功待支付 |
| WAIT_FOR_TICKETING | 400 | 待出票 |
| SUPPLIER_TICKETING | 401 | 出票中 |
| TICKET_FAILED | 403 | 出票失败 |
| SUCCESS | 600 | 出票成功 |
| REFUNDING | 420 | 退票中 |
| REFUND_SUCCESS | 422 | 退票成功 |

完整枚举见 [飞书 wiki 原文](https://trip.larkenterprise.com/wiki/UXntw6JDLi6j2wkSrOhc51TCnjT)。

---

## 调用方判断（日志 action）

| action 前缀/模式 | 含义 |
|------------------|------|
| `ticket#` | 上游订单系统 → 票台 |
| `ticket#exception` | 票台异常处理 |
| `vc#` | 票台 → 下游 VC |
| `train.global.rail.gds.ticketing.*` | 票台 → 订单 MQ 结果 |
