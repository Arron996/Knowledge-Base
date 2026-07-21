---
name: ticket-desk-log-query
description: "票台订单日志查询：根据 orderId 和可选的 action（关键事件）查询票台系统的操作日志摘要，支持按关键字过滤和限制条数。当用户需要排查订单流转过程、查看某个环节的请求响应、追踪订单生命周期事件时使用。"
---

# ticket-desk-log-query

根据 orderId 查询票台系统的操作日志摘要，可按关键事件（action）和关键字（filterKey）过滤，用于排查订单流转问题。

## 使用场景

- 用户给出一个 orderId，想查看订单在票台各环节的日志
- 排查创单、支付、出票、退票、改签等环节的请求响应
- 根据子订单号（orderItemId）过滤相关日志
- 追踪供应商调用链路和耗时

## 接口信息

- 方法：POST
- Content-Type：application/json
- 地址：`http://global.rail.order.admin.be.fat22.qa.nt.ctripcorp.com/api/queryTicketDeskLogSummary`
- 接口会自动判断订单所属环境（FAT/UAT/PRO），无需用户指定

### 请求体

```json
{
  "orderId": "<订单号，必填>",
  "actions": "<关键事件枚举，选填，多个用逗号分隔>",
  "filterKey": "<日志正文必须包含的字符串，选填>",
  "limit": 7
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `orderId` | string | 是 | 订单号，纯数字字符串 |
| `actions` | string | 否 | 关键事件枚举值，多个用逗号分隔。不传则查询该订单所有事件日志 |
| `filterKey` | string | 否 | 日志中必须包含的字符串（如子订单号），用于精确过滤 |
| `limit` | int | 否 | 返回条数限制，默认 7 条，最多 10 条 |

### actions 枚举值

| 枚举值 | 解释 |
|--------|------|
| `ticket#createOrder` | 上游调用票台创建火车票订单（只有普通订单） |
| `ticket#createXOrder` | 上游调用票台创建 X 产品订单 |
| `SplitOrderConsumer` | 火车票票台内部拆票（只有普通订单） |
| `gdsNewSearch#searchDetail` | 票台调用搜索接口用于拆单和准备供应商创单数据 |
| `vc#createOrder` | 票台调用下游供应商创单（包含普通订单、改签单和 X 产品订单） |
| `trn.gds.ticketing.system.create.order.result` | 火车票票台返回创单结果给上游（包含普通订单和改签单） |
| `train.global.rail.gds.ticketing.create.x.order.result` | X 产品票台返回给上游创单结果 |
| `ticket#completeOrder` | 上游调用票台支付订单（包含普通订单和改签订单） |
| `vc#completeOrder` | 票台调用下游供应商支付订单 |
| `vc#queryOrder` | 票台调用下游供应商查询订单状态（判断是否有出票结果） |
| `trn.gds.ticketing.system.complete.order.result` | 票台异步返回订单出票结果给上游 |
| `ticket#applyExchange` | 上游调用票台判断订单是否可以改签 |
| `vc#applyExchange` | 票台调用下游供应商判断是否可以改签 |
| `ticket#createExchangeOrder` | 上游调用票台创建改签订单 |
| `SplitExchangeOrderConsumer` | 火车票票台内部拆票（只有改签订单） |
| `ticket#applyRefund` | 上游调用票台判断订单是否可以退票 |
| `vc#applyRefund` | 票台调用供应商判断是否可以退票 |
| `ticket#confirmRefund` | 上游调用票台确认退票 |
| `SubConfirmRefundConsumer` | 票台内部异步处理退票 |
| `vc#confirmRefund` | 票台调用下游供应商确认退票 |
| `ticket#refundEvent` | 上游调用票台更新退票信息 |
| `train.global.rail.gds.ticketing.sub.refund.result` | 票台返回退票结果给上游 |
| `ticket#obtainTicket` | 上游订单调用票台取票（只有 obbat 有这个逻辑） |

## 默认查询策略

- 用户只说"查订单日志"且未指定 action：不传 actions 参数，查询所有事件
- 用户说"查创单日志"：actions 设为 `ticket#createOrder,vc#createOrder,trn.gds.ticketing.system.create.order.result`
- 用户说"查支付/出票日志"：actions 设为 `ticket#completeOrder,vc#completeOrder,vc#queryOrder,trn.gds.ticketing.system.complete.order.result`
- 用户说"查退票日志"：actions 设为 `ticket#applyRefund,vc#applyRefund,ticket#confirmRefund,SubConfirmRefundConsumer,vc#confirmRefund,train.global.rail.gds.ticketing.sub.refund.result`
- 用户说"查改签日志"：actions 设为 `ticket#applyExchange,vc#applyExchange,ticket#createExchangeOrder,SplitExchangeOrderConsumer`
- 用户说"查 X 产品日志"：actions 设为 `ticket#createXOrder,train.global.rail.gds.ticketing.create.x.order.result`
- 用户提到子订单号（如 50136866542）：将其设为 filterKey

## 调用方式

```bash
curl --location 'http://global.rail.order.admin.be.fat22.qa.nt.ctripcorp.com/api/queryTicketDeskLogSummary' \
--header 'Content-Type: application/json' \
--data '{
  "orderId": "{orderId}",
  "actions": "{actions}",
  "filterKey": "{filterKey}",
  "limit": {limit}
}'
```

注意：actions 和 filterKey 为空时不传或传空字符串均可。

## 返回结果

```json
{
  "orderId": "1400827950653148",
  "env": "PRO",
  "action": "vc#createOrder",
  "filterKey": "50136866542",
  "logs": [
    {
      "timestamp": "2026-07-08T16:56:49",
      "title": "gds_ticket_system",
      "action": "vc#createOrder",
      "msgTrace": "100051894-0a9ac87e-495416-49771",
      "message": "{...元数据JSON，含 msgTrace/costTime/appId/idc 等}",
      "request": "{...请求JSON}",
      "response": "{...响应JSON}"
    }
  ]
}
```

### 返回字段说明

| 字段 | 说明 |
|------|------|
| `orderId` | 订单号 |
| `env` | 订单所属环境（FAT/UAT/PRO） |
| `action` | 查询的 action 过滤条件 |
| `filterKey` | 查询的关键字过滤条件 |
| `logs` | 日志列表 |
| `logs[].timestamp` | 日志时间 |
| `logs[].title` | 日志来源应用 |
| `logs[].action` | 该条日志对应的事件类型 |
| `logs[].msgTrace` | 调用链 traceId |
| `logs[].message` | 元数据（含耗时、IDC、父 trace 等） |
| `logs[].request` | 请求体 JSON |
| `logs[].response` | 响应体 JSON |

## 输出格式

查询结果展示时：

1. **按时间线展示**：日志按 timestamp 顺序排列，清晰呈现订单流转过程
2. **摘要信息**：每条日志先展示 action、时间、耗时、IDC
3. **关键字段提取**：
   - 从 message 中提取 `costTime`（耗时毫秒）、`idc`（机房）
   - 从 response 中提取 `success`/`code` 判断调用是否成功
   - 从 response 中提取 `supplierReference`（供应商订单号）、`ticketPrice` 等关键业务数据
4. **错误高亮**：如果 response 中 success=false 或 code≠200，重点标注错误信息
5. **请求响应折叠**：request 和 response 体较大时，默认只展示关键字段，用户要求时再展示完整 JSON

## 注意事项

- orderId 必须是纯数字字符串
- 单个 action 查询时直接传该值，多个用逗号分隔
- limit 默认 7，最大 10，超过 10 会被截断
- 接口自动识别订单所属环境，无需用户指定
- 日志中的 request/response 是 JSON 字符串，需要解析后再展示
- 如果返回 logs 为空，可能是 action 拼写错误或该订单没有对应环节的日志
