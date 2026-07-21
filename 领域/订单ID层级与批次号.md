---
title: 订单 ID 层级与批次号
tags:
  - 领域
  - 票台
  - 创单
  - 改签
sources:
  - "[[import/yuque/笔记/work/WORK]]"
  - "[[import/yuque/笔记/work/业务]]"
created: 2026-07-08
---

# 订单 ID 层级与批次号

> 理解创单、拆单、退票、改签的根模型。摘自 2024 入职笔记提炼。

---

## ID 层级

```
orderId（主单）
  └── solutionId（单程解决方案；一个 order 可有 1–2 个 solution）
        └── orderItemId（拆票子单）
              └── fareId / ticketId / segmentId
```

| 概念 | 说明 |
|------|------|
| `splitPlanId` | 通常等于 `solutionId` |
| 主单 / 子单 | 用户下的换乘单 vs 按拆票请求供应的子单 |
| 乘客 | 订单层 `gdsPassengers`（含婴儿）vs 供应层 `SupplierPassengers`（仅出票乘客） |

---

## 创单流程（新老对比）

### 老票台

```
SupplierCreateOrderProcessor
  → getSupplierCode → getBookingService
  → AbstractSupplierBookingService.createOrder
      → 调 VC
      → 供应商 impl.doCreateOrder
      → 存缓存 / 重试
  → 更新票据 result
```

### 新票台

```
CreateOrderProcessor
  → sendSplitOrderMessage
  → SplitOrderConsumer → SplitOrderProcessor
      → searchDetail → splitOrderLogic.doSplit
      → sendCreateSubOrderMessage（每个 subOrder）
  → CreateSubOrderConsumer → CreateSubOrderProcessor
      → p2p booking → 老票台
      → supplierOrder → VC
  → 全部子单结束 → 查子单 → build result → 发 event
  → 超时：sendWaitingCreateOrderResult → CreateOrderTimeoutConsumer（SEAT_BOOKING 未支付 → fail）
```

### seatMap（老票台）

按 `solutionId` 的 `@gds supplier` + config 概率切 VC（`GdsSupplierOrderService`）或老票台 `SupplierBookingService`。

---

## 完整下单链路（用户视角）

```
place order (gds order)
  → split order（uktis）
  → x create order
  → book seat / create order per subOrder（supplier create order）
  → search solution → get price → pay
  → complete per subOrder → gds ticket → 更新 order
```

---

## 改签批次号

每次改签对操作对象生成新批次号：

```
01 01 01  →  02 01 02
```

- **主单号不变**
- **子单号改变**，生成新批次
- 记录改签原单：`orderItemId` → `actualOrderItemId`

---

## 关联

- [[领域/退票可退维度问题集]]
- [[领域/通票X产品人工出退改]]
- [[绩效/2024H2-半年报]]
