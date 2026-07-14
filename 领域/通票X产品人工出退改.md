---
title: 通票 X 产品人工出退改
tags:
  - 领域
  - 通票
  - X产品
  - Offline
sources:
  - "[[import/yuque/笔记/work/WORK]]"
created: 2026-07-08
---

# 通票 X 产品人工出退改

> PASS 等 X 产品人工运维链路。Offline 出票列表日均约 50 单（2024 H1）。

页面：[Offline 通票出票](https://offline.globalrail.train.ctripcorp.com/#/ticket-list)

---

## 订单状态机

| 对象 | 状态流转 |
|------|----------|
| order | `100 → 200 → 400 → 600` |
| subXorder | `200 → 400 → 401 → 600` |
| 退票（无 VC） | `419 → 420` 直切 |

生单落库后 order 状态 200；出票成功后 → 401/600。

---

## 核心接口

| 接口 | 作用 |
|------|------|
| CreateXOrder | 生单：单程/往返、坐席、日期、乘客、联系人、金额 |
| ManualTicketResult | 人工回填：成功/失败、supplierOrderId、ticketUrl、PDF |
| ManualTicketOrderList | 列表查询（供应、状态、operator、时间窗） |
| ConfirmXProductRefund | 主退/子退落库；`refundItemInfos` 替代旧字段 |
| ManualRefundResult | 回填退票金额与结果 |

### 出票成功

- 上传 PDF：`TicketVouchers` + uid + subOrder
- 更新 master order 状态
- operator 存 `eid-ename`

### 出票失败

- 更新主单失败 + 抛 Q
- 子单全部走 `confirmRefund`

---

## 退票数据结构

- `refundItemInfos`：按 orderItemId + ticketIds + 金额明细
- `refundFlowType`：如 `manual_refund`
- `refundExtraInfo`：原因 + operator（eid/empName）

主退表 `supplier_master_xorder_refund`、子退表 `supplier_sub_xorder_refund`（orderId / orderItemId / sub_refund_id / 金额四元组等）。

---

## 前端要点（客服体验）

- 列表：p2p / x 产品筛选、orderItemId、翻页操作栏置顶
- 出票弹窗：supplierOrderId、ticketUrl、PDF 上传；package name + productName
- 日铁：多文件 + 人程维度 ticketVoucher
- 失败 vs 取消在中台区分展示

---

## 设计方向（2024 自评）

- 策略模式：通票与火车票复用同一套人工出/退接口
- 出票层封装，供票种转换、取票等复用

---

## 关联

- [[工程/Offline前后端联调套路]]
- [[领域/订单ID层级与批次号]]
- [[绩效/2024H1-半年报]]
