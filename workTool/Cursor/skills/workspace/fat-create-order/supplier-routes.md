# FAT 生单 — 供应商与线路参考

随 FAT 环境变化；**以 Step 0「近 2 小时 order_status=200」为准**，下表仅为历史稳定参考。

## treit（首选）

| 项 | 值 |
|----|-----|
| 线路 | Rome Termini `IT3909` → Milan Central `IT3901` |
| 车次示例 | FR 9508，06:00 发 |
| channel | `TripTrain` |
| ticketingOption | `ETICKET`（searchDetail 有 PAH 也可） |
| 搜方案 | `requireSearchRouteSuppliers: ["treit"]` 可选 |
| 注意 | 首测选 **低价档**（如 Speciale Eventi），不要默认最贵 BASE |

参考成功单字段：真实 `uid`、正常乘客姓名成功率高于 `test_*` + `TEST/CERTNULL`。

## uktis

| 项 | 值 |
|----|-----|
| channel | `TripTrain` 或 `trainpal` |
| 线路 | 从 Step 0 成功单抄 `departure_location_code` |
| ticketingOption | 以 searchDetail 为准 |

## sncfr / jrcen

| supplier | 常见 channel | 说明 |
|----------|--------------|------|
| sncfr | `ctrainintl` | 法铁，Step 0 成功单多 |
| jrcen | `ctrainintl` | 日铁 |

channel 与 TripTrain 不同；**必须抄成功单 channel**，不要默认 TripTrain。

## cerca（慎选首测出票）

| 项 | 值 |
|----|-----|
| 线路 | Castellón `ES001058088` → Valencia `ES001058289` |
| channel | `TripTrain` |
| ticketingOption | **PAH**（searchDetail `deliveryOptions` 通常仅 PAH） |
| 风险 | 缺 `departureSoonBlockCreate` 会 NPE；supplier 常返 999999 |

适合：西语线、证件 nullable、supplier 适配排障。  
不适合：「第一次就要子单 200」的冒烟。

## 拆票（Treit + Itntv 等）

- 仅 `CreateOrderServiceByNewSearchTest.buildCreateOrderRequest` 类场景
- `outSolutionOfferPairs` 多条、globa2 solution
- **不要**用于 FAT 动态首测；方案极易过期

## search 公共参数

```
outboundDateTime: today + 7～14 天，时刻对齐参考单
searchAgeInfoList: [{ "age": 30, "count": 1 }]
searchType: 0
solutionType: 1
head.channelMetaInfo.channel: 与目标 channel 一致
```

## createOrder 公共参数

```json
{
  "currency": "EUR",
  "locale": "en_XX",
  "extPreference": {
    "acceptObtainTicket": true,
    "randomAssigned": true
  },
  "contact": {
    "email": "test@trip.com#",
    "firstName": "...",
    "lastName": "...",
    "phoneNo": ""
  }
}
```

乘客测 null 证件：**省略 `certDocument` 字段**，不要传 `{ "certNo": null }`。
