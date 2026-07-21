---
name: fat-order-lookup
description: |
  FAT 测试环境快速定位 Aaron 的 GDS 订单号，并输出 Admin 票台日志链接。
  用户说刚下单、捞订单号、测试环境订单、admin log、ticketLog 时使用；
  无 orderId 时按邮箱/uid/createRequest 在 CLOG 反查。
---

# FAT 测试订单快速定位 → Admin Log

通过 **BAT CLOG** 反查订单号（优先邮箱/uid 锚点），**Admin MCP** 校验，拼 **Admin 票台日志 URL** 返回用户。

## 何时使用

- 用户在 **FAT/测试环境刚下单**，要 **订单号**
- 要跳转 **Admin 订单日志**（`ticketLog`、创单/出票 stage）
- 用户说：捞单、我的测试单、admin log、createRequest

**不用于**：已有 `orderId` 的排障深挖 → [gds-rail-triage](../gds-rail-triage/SKILL.md)；只要 trace → [bat-clog-trace](../bat-clog-trace/SKILL.md)。

## 默认锚点（用户未指定时）

| 字段 | 默认值 | CLOG 脱敏形态 |
|------|--------|---------------|
| 邮箱 | `zhaorun@trip.com` | `zhH6Qun@trip.com`（搜前缀 `zhH6Qun`） |
| uid | `_TRXX1cp43t01bbki` | 明文 |

用户口述其他邮箱/uid 时以用户为准。

## 执行顺序

```
Task Progress:
- [ ] 0. 是否已有 orderId？→ 跳到 Step 4
- [ ] 1. bat-global-helper（UTC 时间窗）
- [ ] 2. bat-clog 按锚点反查 orderId + _subEnv_
- [ ] 3. pre-query-order + query-order mini 校验
- [ ] 4. 拼 Admin ticketLog URL 并回复用户
```

### Step 0：已有 orderId

用户已给单号 → 跳过 CLOG，直接 Step 3–4。

### Step 1：时间窗

| 用户说法 | fromUtc / toUtc |
|----------|-----------------|
| 刚才 / 刚刚 / 最新 | now − **30min** ~ now（比 1h 更快） |
| 给了北京时间时刻 | ±5min，转 UTC |
| 未说时间 | now − 30min ~ now |

环境：**fws**（FAT/测试）。

### Step 2：CLOG 反查（无 orderId）

**MCP**：`user-bat-mcp-function` → `bat-clog`

| 参数 | 值 |
|------|-----|
| `appId` | `100045149`（订单系统） |
| `env` | `fws` |
| `message` | 见下表锚点优先级 |
| `queryLargeFields` | `on`（必须，才能读到完整 createRequest JSON） |

**锚点 → message 关键词**（按优先级试，命中即停）：

| 用户给的锚点 | bat-clog `message` | 匹配字段 |
|--------------|-------------------|----------|
| traceId | 用 `messageId` 参数查全 trace | attribute `order_id` 或 JSON `orderId` |
| 邮箱 | `createOrder req` | `contact.email` 含邮箱前缀（如 `zhH6Qun`） |
| uid | `createOrder req` | `"uid":"_TRXX..."` |
| 仅「刚下单」 | `createOrder req` | 默认邮箱前缀；**禁止**仅按时间取最近一单 |

从命中日志提取：

- `orderId`：JSON 字段或 attribute `order_id`
- `_subEnv_`：attribute（如 `FAT22`）→ Admin 域名 `fat22`
- `timeStr`、`channel`、行程摘要（`departureLocation` / `arrivalLocation`）

多条命中：取 **时间最新且邮箱/uid 匹配** 的一条；仍无法区分时列出候选并请用户确认。

### Step 3：Admin MCP 校验

**MCP**：`user-gds-order-admin-mcp-fat`

```json
{ "orderId": "<id>" }
```

→ `pre-query-order`（channel、idc）

```json
{ "orderId": "<id>", "type": "mini" }
```

→ `query-order`（状态、行程、createTime 与 CLOG 对齐）

### Step 4：拼 Admin 票台日志 URL

**Host**（由 `_subEnv_` 决定，默认 `fat22`）：

```
http://admin.order.gds.fat{subEnv小写}.qa.nt.ctripcorp.com
```

例：`_subEnv_=FAT22` → `http://admin.order.gds.fat22.qa.nt.ctripcorp.com`

**Path + 查询参数**：

```
/order/log?orderId={orderId}&type=ticketLog&stage={STAGES}
```

**`stage` 固定列表**（逗号分隔，URL encode）：

```
ticket#createOrder,ticket#createXOrder,vc#createOrder,trn.gds.ticketing.system.create.order.result,train.global.rail.gds.ticketing.create.x.order.result,train.gds.bus.ticketing.system.create.order.result,vc#completeOrder,ticket#manualTicketResult,ticket#manualXTicketResult,trn.gds.ticketing.system.complete.order.result,train.global.rail.gds.ticketing.complete.x.order.result,train.gds.bus.ticketing.system.complete.order.result,vc#createExchange,ticket#createExchangeOrder
```

**完整示例**：

```
http://admin.order.gds.fat22.qa.nt.ctripcorp.com/order/log?orderId=1134766359779535&type=ticketLog&stage=ticket%23createOrder%2Cticket%23createXOrder%2Cvc%23createOrder%2Ctrn.gds.ticketing.system.create.order.result%2Ctrain.global.rail.gds.ticketing.create.x.order.result%2Ctrain.gds.bus.ticketing.system.create.order.result%2Cvc%23completeOrder%2Cticket%23manualTicketResult%2Cticket%23manualXTicketResult%2Ctrn.gds.ticketing.system.complete.order.result%2Ctrain.global.rail.gds.ticketing.complete.x.order.result%2Ctrain.gds.bus.ticketing.system.complete.order.result%2Cvc%23createExchange%2Cticket%23createExchangeOrder
```

`_subEnv_` 未知时默认 **fat22**（与 Admin FE 测试默认一致），并在回复中注明。

可选：`cursor-app-control` → `open_resource` 用 URI 打开链接（用户要求打开时）。

## 回复模板

```markdown
**订单号：** `{orderId}`
**环境：** FAT / {_subEnv_} · {channel}
**行程：** {departure} → {arrival} · {departureTime}
**创单时间：** {createTime}

**Admin 票台日志：** {adminLogUrl}
**BAT Trace：** https://bat.fws.qa.nt.ctripcorp.com/trace/{messageId}（若有）
```

## 用户最快话术

| 话术 | Agent 行为 |
|------|------------|
| `FAT 刚下单` | 默认邮箱前缀反查 |
| `FAT 刚下单，邮箱 xxx@trip.com` | 用指定邮箱 |
| `订单号 1134...` | 直接拼 Admin URL |
| `uid _TRXX...` | CLOG 按 uid 匹配 |

## 注意

- CLOG `message` 仅匹配前 **128 字符**；完整 JSON 必须 `queryLargeFields=on`。
- 邮箱在 CLOG 中为 **CoreInfo 脱敏**形态，用 `@` 前前缀匹配。
- FAT 多人并发时，**禁止**只靠「最近一单」；必须有邮箱/uid/trace 锚点之一。
