---
name: supplier-error-impact
description: "供应商报错影响分析：根据供应商原始报错信息，查询生产环境最近受影响的订单数量、涉及用户数、供应商、渠道、线路等维度的统计。当用户给出供应商报错关键词（如 cert type not support、ticket sold out 等），需要了解影响范围时使用。"
---

# supplier-error-impact

根据供应商原始报错信息，快速分析生产环境中受影响的订单范围和用户数。

## 使用场景

- 用户给出一段供应商报错信息，想知道影响了多少订单/用户
- 排查某类报错的影响范围和共同特征
- 快速定位报错集中在哪个供应商、渠道、线路

## 分析步骤

### Step 1：查询受影响订单

在生产环境 `trngdssuppliertransactiondatadb` 库的 `supplier_sub_order_statistics` 表中，根据用户提供的报错关键词查询最近一段时间（默认 1 天，用户可指定）的订单：

```sql
SELECT order_id, order_item_id, sub_batch_id, supplier, channel, 
       departure_location_name, arrive_location_name, 
       origin_code, origin_reason, standard_code, standard_reason,
       status, error_deal_type, idc, userdata_location,
       book_start_time, datachange_lasttime
FROM supplier_sub_order_statistics 
WHERE datachange_lasttime >= DATE_SUB(NOW(), INTERVAL {时间范围} DAY)
  AND origin_reason LIKE '%{报错关键词}%'
LIMIT 50
```

参数说明：
- `{报错关键词}`：用户提供的供应商报错信息，支持模糊匹配
- `{时间范围}`：默认 1 天，用户可指定（如"最近3天"、"最近一周"）
- 数据库：`trngdssuppliertransactiondatadb`，环境：`pro`

### Step 2：查询涉及用户数

根据 Step 1 得到的 order_id 列表，在同库的 `supplier_master_order` 表中查询 uid：

```sql
SELECT order_id, uid 
FROM supplier_master_order 
WHERE order_id IN ({order_id_list})
```

### Step 3：输出分析报告

汇总输出以下维度信息：

1. **影响订单总数**
2. **涉及用户数**（去重 uid 数量）
3. **供应商分布**（哪些 supplier 出现了该报错）
4. **渠道分布**（TripTrain / Ctrip 等）
5. **线路分布**（出发-到达 Top 线路）
6. **时间分布**（是否集中在某个时段）
7. **错误码**（origin_code / standard_code）
8. **IDC / 用户归属地**

## 注意事项

- 生产环境只允许读操作
- 查询结果超过 50 条时，先统计总数再取样展示
- 如果报错关键词过于宽泛（如 "error"），提醒用户缩小范围
- 时间范围过大时（超过 7 天），提醒用户可能查询较慢
