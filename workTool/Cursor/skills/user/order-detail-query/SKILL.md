---
name: order-detail-query
description: "供应商订单详情查询：根据 orderId 查询供应商订单的详细数据，支持指定查询哪些表（主订单、子订单、乘客、行程段、票务、退款、X产品等）。当用户需要查看订单详情、排查订单问题、确认订单状态时使用。"
---

# order-detail-query

根据 orderId 查询供应商订单系统中的详细数据，支持按表维度灵活查询。

## 使用场景

- 用户给出一个 orderId，想查看订单详情
- 排查订单状态、支付状态、退款信息
- 查看订单的乘客信息、行程段、票务凭证
- 确认 X 产品（休息室/餐饮等）子单状态

## 接口信息

- 方法：POST
- Content-Type：application/json
- 地址：`http://global.rail.order.admin.be.fat22.qa.nt.ctripcorp.com/api/queryTicketDeskOrderInfo`
- 接口会自动判断订单所属环境（FAT/UAT/PRO），无需用户指定

### 请求体

```json
{
  "orderId": "<订单号>",
  "tableNames": ["<表名1>", "<表名2>"]
}
```

### 可查询的表

| 表名 | 用途 |
|------|------|
| `supplier_master_order` | 主订单信息（状态、支付、渠道等） |
| `supplier_master_order_refund` | 主订单退款 |
| `supplier_master_xorder_refund` | X产品主单退款 |
| `supplier_order_passenger` | 订单乘客信息 |
| `supplier_order_tag` | 订单标签 |
| `supplier_p2p_voucher` | 车票凭证 |
| `supplier_sub_order` | 车票子订单 |
| `supplier_sub_order_accommodation` | 座席/铺位 |
| `supplier_sub_order_additional_product` | 附加产品 |
| `supplier_sub_order_fare` | 运价明细 |
| `supplier_sub_order_passenger` | 子单乘客 |
| `supplier_sub_order_refund` | 子单退款 |
| `supplier_sub_order_segment` | 行程段 |
| `supplier_sub_order_segment_ticket` | 行程段票务 |
| `supplier_sub_xorder` | X产品子订单（休息室/餐饮等） |
| `supplier_sub_xorder_refund` | X产品退款 |
| `supplier_sub_xorder_ticket` | X产品票务 |
| `supplier_sub_xorder_voucher` | X产品兑换券 |

### 默认查询策略

- 用户只说"查订单详情"且未指定表：默认查询 `supplier_master_order` + `supplier_sub_order`
- 用户说"查退款"：查询 `supplier_master_order_refund` + `supplier_sub_order_refund`
- 用户说"查乘客"：查询 `supplier_order_passenger` + `supplier_sub_order_passenger`
- 用户说"查行程"：查询 `supplier_sub_order_segment` + `supplier_sub_order_segment_ticket`
- 用户说"查X产品"：查询 `supplier_sub_xorder` + `supplier_sub_xorder_ticket` + `supplier_sub_xorder_voucher`
- 用户说"查全部"：查询所有 18 张表

## 调用方式

```bash
curl --location 'http://global.rail.order.admin.be.fat22.qa.nt.ctripcorp.com/api/queryTicketDeskOrderInfo' \
--header 'Content-Type: application/json' \
--data '{
  "orderId": "{orderId}",
  "tableNames": {tableNames数组}
}'
```

## 返回结果

```json
{
  "orderId": "1653735851295430",
  "env": "FAT",
  "tableNames": ["supplier_master_order"],
  "tables": {
    "supplier_master_order": [
      "{JSON字符串，每条记录是一个JSON}"
    ]
  }
}
```

- `tables` 中每个 key 是表名，value 是 JSON 字符串数组
- 每个 JSON 字符串需要解析后展示给用户
- 如果某张表没有数据，对应 value 为空数组
- 返回中的 `env` 字段标识该订单实际所属环境

## 输出格式

查询结果解析后，按表分组、以易读的方式展示关键字段。对于常见状态码，尽量翻译为可读含义。

### 主订单常见状态码参考

- `status`: 190=已完成
- `payStatus`: 300=已支付

## 注意事项

- orderId 必须是纯数字字符串
- 一次可查询多张表，无需多次调用
- 接口自动识别订单所属环境，无需用户指定
