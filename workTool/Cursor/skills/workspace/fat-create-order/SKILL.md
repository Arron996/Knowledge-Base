---
name: fat-create-order
description: |
  FAT 测试环境快速生单并成功出票的 playbook。用户要测试生单、造单、全流程出票、FAT 联调下单、动态搜方案生单时使用；
  从 FAT 近期成功单抄线路与渠道，走 search→searchDetail→createOrder，避免写死过期方案 ID。
---

# FAT 快速生单出票（成功优先）

目标：**尽量一次走通 createOrder → 子单 200 →（可选）completeOrder 出票**，而不是碰运气写死方案。

## 何时使用

- FAT/测试环境 **造单、生单、出票全流程**
- 验证字段入库（如 `certDocument=null`）且希望 **子单也成功**
- 需要 **动态方案**（不写死 `solutionId`/`offerId`）

**不用于**：线上 PRO 造单；已有 orderId 排障 → [gds-rail-triage](../gds-rail-triage/SKILL.md)；捞刚下的单 → [fat-order-lookup](../fat-order-lookup/SKILL.md)。

## 核心原则

1. **先抄活线路**：从 FAT 最近 **子单 status=200** 的订单抄 `supplier + 起终点 + channel`，方案 ID 每次现搜。
2. **channel 决定 MQ**：要 FAT 环境自动拆单/子单，用 **真实渠道**（如 `TripTrain`）；`local` 只写 Redis，需 IDEA 手动驱动 Processor。
3. **ticketingOption 跟 searchDetail**：以 `deliveryOptions` 为准，不要凭感觉写 ETICKET/PAH。
4. **单段优先**：首测选 **不拆票** 线路；Treit+Itntv 拆票留到专项用例。
5. **测入库 ≠ 测出票**：主单 createOrder 后 `supplier_order_passenger` 已落库；子单 200 才是供应商扣位成功。

## 执行顺序

```
Task Progress:
- [ ] 0. DOT 捞 FAT 近期成功子单 → 定 supplier / 线路 / channel
- [ ] 1. gds-search 动态搜方案（日期 = today+7，带 channel）
- [ ] 2. searchDetail → offerId + deliveryOptions
- [ ] 3. 生成 orderId / subBatchId / gdsPassengerId，组装 createOrder
- [ ] 4. 生单 + 等子单（或 IDEA local 手动驱动）
- [ ] 5. DOT / CLOG 验收；可选 completeOrder
- [ ] 6. 失败 → 见「常见失败」；换 supplier 或克隆成功单参数
```

---

## Step 0：捞 FAT 近期成功单（必做）

**MCP**：`user-DOT` → `sql_execute`

```sql
SELECT order_id, order_item_id, supplier, order_status, channel, create_time
FROM supplier_sub_order
WHERE order_status = 200
  AND create_time >= DATE_SUB(NOW(), INTERVAL 2 HOUR)
ORDER BY create_time DESC
LIMIT 15;
```

从结果选 **与目标一致** 的一行，再查行程：

```sql
SELECT order_id, departure_location_code, departure_location_name,
       arrive_location_code, arrive_location_name, ticketing_option
FROM supplier_sub_order
WHERE order_id = <参考 orderId>
LIMIT 5;
```

**只抄**：`supplier`、起终点 `locationCode`、出发时段习惯、`channel`、`ticketing_option`。  
**不要抄**：`solutionId`、`offerId`（会过期）。

CLOG 里该单的 createOrder/createSubOrder 请求可作 **乘客、contact、extPreference** 模板（`appId=100051894`，message=orderId）。

---

## Step 1：动态 search

调用 **gds-search** `search`（或项目内 `GdsSearchServiceProxy` / 供应商 `*AdapterServiceTest#testSearch`）。

| 字段 | 建议 |
|------|------|
| `origin.locationCode` / `destination.locationCode` | Step 0 抄到的站码 |
| `outboundDateTime.departureDateTime` | `LocalDate.now().plusDays(7)` + 参考单相近时刻，如 `2026-07-20 06:00` |
| `searchAgeInfoList` | `[{"age":30,"count":1}]` |
| `head.channelMetaInfo.channel` | 与 Step 0 **一致**（如 `TripTrain`） |
| `optionalParameter.requireSearchRouteSuppliers` | 可选，锁定目标 supplier |

从 `outboundTravelSolutions` 取 **目标 supplier 的第一条可售方案** 的 `travelSolutionId`/`solutionId`。

---

## Step 2：searchDetail

用 Step 1 的 `solutionId` 调 `searchDetail`，记录：

- `offerId`（通常与 fare 包内 `fareId` 对应）
- `deliveryOptions`（如 `["PAH"]` 或 ETICKET）
- 票价档（优先选 **参考成功单同档或更低档**，避免 BASE 贵档首测失败）

---

## Step 3：组装 createOrder

### ID 规则（与票台测试一致）

```
orderId        = System.currentTimeMillis()          // 1783930911337
subBatchId     = Long.parseLong(orderId + "01")      // 178393091133701
gdsPassengerId = subBatchId * 100                    // 17839309113370100
```

### 请求要点

| 字段 | 建议 |
|------|------|
| `channelMeta.channel` | Step 0 的 channel（全流程用 `TripTrain`） |
| `outSolutionOfferPairs` | `[{ solutionId, offerId, ticketingOptionSelected }]` |
| `ticketingOptionSelected` | **searchDetail.deliveryOptions 之一** |
| `passengers` | 参考成功单；测 null 证件则 **不传 `certDocument`** |
| `contact.email` | 带 `#` 后缀的测试邮箱，如 `xxx@trip.com#` |
| `extPreference` | `{ "acceptObtainTicket": true, "randomAssigned": true }` |
| `currency` | 与方案一致，欧洲线常用 `EUR` |

**禁止**：测试类里写死的 globa2/Treit 拆票 `solutionId` 直接复用到 FAT 动态联调。

---

## Step 4：两条执行路径

### 路径 A — FAT 真实渠道（推荐，子单走 MQ）

1. `createOrder`（channel=`TripTrain` 等）
2. 等待 **30s～2min**（QMQ 可能有积压/重试）
3. DOT 查子单：

```sql
SELECT order_id, order_item_id, supplier, order_status, supplier_order_id, datachange_lasttime
FROM supplier_sub_order WHERE order_id = <orderId>;
```

| order_status | 含义 |
|--------------|------|
| 150 | 扣位中，继续等或查 CLOG |
| **200** | 生单成功 ✅ |
| 199 | 失败，查 CLOG `CREATE_ORDER_FAIL` |

4. （可选）调 `completeOrder` + 等子单 400→600

### 路径 B — IDEA 本地 `local` channel

适用：**本机连 FAT**，且避免与测试环境 MQ 抢消费。

测试类：`gds-ticketing-gateway` → `CreateOrderServiceByNewSearchTest`

1. `channelMeta.channel = "local"`
2. `createOrder` 后从 Redis 读事件并 **手动** 驱动：
   - `splitOrder:{orderId}` → `splitOrderByNewSearchProcessor`
   - `createSubOrder:{orderItemId}` → `createSubOrderByNewSearchProcessor`
   - `completeSubOrder:{orderItemId}` → `completeSubOrderProcessor`
3. VM 需 `--add-opens`（Java 17+ cdubbo）；见项目 gateway 测试配置

路径 B **不会** 验证 FAT MQ；仅适合本地调试 Processor。

---

## Step 5：验收

### 生单成功

```sql
-- 子单 200 + 有 supplier_order_id
SELECT order_status, supplier_order_id FROM supplier_sub_order WHERE order_id = ?;

-- 测字段入库（不必等子单）
SELECT cert_no, cert_no IS NULL, cert_no = '' FROM supplier_order_passenger WHERE order_id = ?;
```

### 日志

| 目的 | 工具 |
|------|------|
| 流程节点 | BAT CLOG `appId=100051894`，message=orderId |
| 子单失败 | 搜 `CREATE_ORDER_FAIL` / `SubOrderStatusChangeHelper` |
| 调用链 | BAT Trace，messageId 取 CreateSubOrderConsumer 的 cat-msg-id |

Admin 票台日志（子单成功后更有内容）：见 [fat-order-lookup](../fat-order-lookup/SKILL.md) Step 4。

---

## 常见失败与处理

| 现象 | 根因 | 处理 |
|------|------|------|
| 主单 100，无子单 | channel=`local` 未发 MQ | 改 TripTrain，或走路径 B 手动驱动 |
| 子单 150 长时间不动 | QMQ 延迟/重试 | 等 2～5min；CLOG 看 createSubOrder 是否已发 |
| 子单 199 + NPE `soonDepartureCheck` | 供应商缺 `departureSoonBlockCreate` | 补 qconfig/DB 或换 supplier |
| 子单 199 + `999999` / `100007` | 供应商拒单 | 克隆成功单 uid/票价档；换 treit/uktis；查 supplier-order CLOG |
| createOrder 报 channel invalid | search 未带 channel | head.channelMetaInfo.channel 必填 |
| 方案搜不到 | 日期太近/线路无票 | 改 +7～+14 天；换 Step 0 其他成功 supplier |

**首测失败**：换 Step 0 列表里 **另一个刚成功的 supplier**，不要死磕 cerca。

---

## 供应商速查

详细线路与选项见 [supplier-routes.md](supplier-routes.md)。

| supplier | 常见 channel | ticketingOption | 备注 |
|----------|--------------|-----------------|------|
| **treit** | TripTrain | ETICKET / PAH | 罗马→米兰 IT3909→IT3901；FAT 成功率高 |
| **uktis** | TripTrain / trainpal | 看 searchDetail | 英铁，FAT 有成功单 |
| **sncfr** | ctrainintl | 看 searchDetail | 法铁，多走 ctrainintl |
| **cerca** | TripTrain | **PAH** 为主 | 西语近程；supplier 层易 999999，不适合首测出票 |
| **jrcen** | ctrainintl | ETICKET | 日铁，channel 常不同 |

---

## 推荐首测组合（按成功率）

1. **treit** · IT3909→IT3901 · TripTrain · ETICKET · 日期 +7 天 06:00 档
2. **uktis** · 从 Step 0 成功单抄英铁起终点 · TripTrain
3. cerca · 仅当明确要测西语线或 supplier 行为时再选

---

## 用户话术

| 用户说 | Agent 行为 |
|--------|------------|
| FAT 生单 / 造单 / 测试下单 | 本 skill 全流程 |
| 要出票 / 全流程 | Step 4 路径 A + completeOrder |
| certDocument null 测入库 | createOrder 后查 `supplier_order_passenger`，不强制子单 200 |
| 参考刚才成功的单 | Step 0 SQL + CLOG 克隆参数 |

---

## 关联 Skill

- 捞单号 + Admin 链接：[fat-order-lookup](../fat-order-lookup/SKILL.md)
- trace / CLOG：[bat-clog-trace](../bat-clog-trace/SKILL.md)
- 子单失败深排：[gds-rail-triage](../gds-rail-triage/SKILL.md)
