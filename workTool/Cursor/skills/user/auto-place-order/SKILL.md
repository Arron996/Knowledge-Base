---
name: auto-place-order
description: "自动生单：在 FAT/FWS 测试环境中自动创建供应商订单。支持两种触发方式：1）指定供应商名称（如 euros）自动查询最近成功订单的路线信息来生单；2）指定已有订单号，基于该订单的路线信息生成新订单。完整流程包括查询路线、搜索车次、生成订单号、下单。当用户需要在测试环境快速创建订单来验证功能时使用。"
---

# auto-place-order

在 FAT/FWS 测试环境中自动创建供应商订单，用于功能验证和测试。

## 使用场景

- 用户说"帮我创建一个 euros 的订单" → 自动查最近成功订单路线，生成新订单
- 用户说"基于订单 165373585xxxx 生成一个新订单" → 基于指定订单的路线生成新订单
- 快速在测试环境中造单验证功能

## 触发方式

### 方式一：按供应商名称

用户提供供应商名称（如 `euros`、`renfe`、`sncf` 等），自动查询该供应商最近的成功订单获取路线信息。

### 方式二：按已有订单号

用户提供一个已有的 orderId，查询该订单的出发/到达站和出发时间作为新订单的路线信息。

## 完整流程（4 步）

### Step 1：查询路线信息

从 FAT 环境 `trngdssuppliertransactiondatadb` 库的 `supplier_sub_order` 表中查询出发/到达站代码和出发时间。

**方式一（按供应商）：**

```sql
SELECT order_id, departure_location_code, departure_location_name, 
       arrive_location_code, arrive_location_name, departure_time
FROM supplier_sub_order 
WHERE DataChange_LastTime > '{今天日期}' 
  AND order_status = 600 
  AND supplier = '{供应商名称}'
LIMIT 3
```

**方式二（按订单号）：**

```sql
SELECT order_id, departure_location_code, departure_location_name, 
       arrive_location_code, arrive_location_name, departure_time
FROM supplier_sub_order 
WHERE order_id = {订单号}
LIMIT 3
```

- 数据库：`trngdssuppliertransactiondatadb`
- 环境：`fat`
- 需要提取：`departure_location_code`、`arrive_location_code`、`departure_time`（取日期部分）

### Step 2：搜索可用车次

调用 GDS 搜索接口获取 solutionId 和 fareId。

- URL：`http://gds.search.fws.qa.nt.ctripcorp.com/api/gdssearchservicev2/search`
- Method：POST
- Content-Type：application/json

```json
{
    "head": {
        "clientMetaInfo": {
            "clientId": "370011384912605400461"
        },
        "channelMetaInfo": {
            "channel": "TripTrain"
        },
        "traceId": "{生成UUID}",
        "currency": "EUR",
        "uid": "_TIXX1byop2rfw5t0",
        "locale": "en_GB",
        "udl": "GB"
    },
    "condition": {
        "origin": {
            "locationCode": "{departure_location_code}"
        },
        "destination": {
            "locationCode": "{arrive_location_code}"
        },
        "outboundDateTime": {
            "departureDateTime": "{出发日期} 20:00"
        },
        "searchAgeInfoList": [
            {
                "age": 30,
                "count": 1
            }
        ],
        "fetchCount": 3,
        "searchType": 0,
        "travelTogether": false,
        "searchWholeDay": true
    },
    "solutionType": 1
}
```

从返回结果中提取：
- `outboundTravelSolutions[0].solutionId` → solutionId
- `fares[0].fareId` → fareId（即 offerId）

### Step 3：生成订单号

调用 generateOrderId 接口获取新的 orderId。

- URL：`http://global.rail.order.system.fat22.qa.nt.ctripcorp.com/api/generateOrderId`
- Method：POST
- Content-Type：application/json

```json
{
    "head": {
        "clientMetaInfo": {
            "clientId": "50862153491260518980"
        },
        "channelMetaInfo": {
            "timestamp": 1751020784,
            "channel": "TripTrain"
        },
        "traceId": "{生成UUID}",
        "currency": "GBP",
        "uid": "_TIXX1byop2rfw5t0",
        "locale": "it_IT",
        "udl": "GB"
    },
    "uid": "_TIXX1byop2rfw5t0",
    "udl": "GB"
}
```

从返回结果中提取：`orderId`

### Step 4：下单

调用 placeOrder 接口创建订单。

- URL：`http://global.rail.order.system.fws.qa.nt.ctripcorp.com/api/placeOrder`
- Method：POST
- Content-Type：application/json

```json
{
    "head": {
        "clientMetaInfo": {
            "clientId": "37001103291260568121"
        },
        "channelMetaInfo": {
            "channel": "trainpal"
        },
        "traceId": "{生成UUID}",
        "currency": "EUR",
        "uid": "_TIXX1byop2rfw5t0",
        "locale": "en_GB",
        "udl": "GB"
    },
    "orderId": {Step3生成的orderId},
    "transactionNo": "{Step3生成的orderId}",
    "selectedTicketingOption": "ETICKET",
    "outSolutionOfferPairList": [
        {
            "solutionId": "{Step2获取的solutionId}",
            "offerId": "{Step2获取的fareId}",
            "ticketingOption": "ETICKET"
        }
    ],
    "passengerInfoList": [
        {
            "firstName": "DDD",
            "lastName": "GGG",
            "birthday": "1995-04-18",
            "gender": 2,
            "certType": 4,
            "certNo": "123456789",
            "certCountryCode": "GB",
            "certExpireDate": "2028-01-01",
            "nationality": "GB"
        }
    ],
    "contactInfo": {
        "firstName": "af",
        "lastName": "al",
        "email": "zysang@trip.com",
        "phoneOfCountry": "HK",
        "phone": "123456789"
    }
}
```

从返回结果中提取：`orderId`、`subBatchId`

## 输出格式

每一步执行完毕后输出关键信息，最终汇总：

```
✅ 自动生单完成！

| 步骤 | 结果 |
|------|------|
| 路线 | {出发站} → {到达站} |
| 车次 | {车次号}, {票价} {币种} |
| 订单号 | {orderId} |
| 子批次号 | {subBatchId} |
```

## 注意事项

- 仅用于 FAT/FWS 测试环境，不可用于生产环境
- 每一步的 traceId 都使用新生成的 UUID
- 搜索时出发时间默认使用 `{日期} 20:00`，配合 `searchWholeDay: true` 搜索全天车次
- 如果 Step 1 查不到数据（如当天没有该供应商的成功订单），提示用户换一个日期范围或供应商
- 如果 Step 2 搜索无结果或车次售罄，提示用户调整日期
- 乘客信息和联系人信息使用默认测试数据，用户可自定义覆盖
- `order_status = 600` 表示已出票成功的订单
