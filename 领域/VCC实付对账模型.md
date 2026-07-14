---
title: VCC 实付对账模型
tags:
  - 领域
  - VCC
  - 财务
  - TripLink
sources:
  - "[[import/yuque/笔记/work/WORK]]"
  - https://conf.ctripcorp.com/pages/viewpage.action?pageId=3041517693
created: 2026-07-08
---

# VCC 实付对账模型

> 国际负利润 VCC：支付回抛 + 清算报表双通道给财务对账。2024 H1 落地。

---

## 双通道概览

| 通道 | 时效 | 适用 | 实现 |
|------|------|------|------|
| **实时授权回抛** | T+0 | Payment | TripLink callback → consumer → 抛 Q 给订单 |
| **清算报表** | T+1（退款 T+n） | Refund | job 捞退款中 + 解析报表 |

退款**没有**三方实时授权回调，只能走报表补数。

---

## 实时回抛流程

1. Controller 接收 TripLink 调用（[TripLink API](https://api.triplinkintl.com/v1.0/api.html#授权结果通知)）
2. 取 `transCurrencyAmt`、`transCurrency`（数字码 → 字符码）
3. 卡号查 `order_vcc_info` 得 `orderItemId`
4. 查 orderId（新库/老库；索引问题可改用 `createTime ± period` 窗口）
5. 抛 Q（qconfig 开关）给订单算负利润

### 排障 CLOG

```
cat_client_appid = '100051894' and msg like '%vcc end%' and msg like '%refund%'
```

### 币种转换

```java
Currency currency = Currency.getAvailableCurrencies()
    .stream().filter(c -> c.getNumericCode() == Integer.parseInt(transCurrency))
    .findAny().orElse(null);
```

---

## 退款与改签

| 场景 | 要点 |
|------|------|
| Refund job | ConfirmRefund 成功落库「退款中」→ job 查 VC 供应是否退成功 → T+n 清算后 T+1 报表 |
| Exchange | 需 `supplier_exchange_id` 传给订单；VC 加字段 |
| needVcc | 老票台部分走老库 vcc，应迁 VC 层；配置全切 VC 时非 vcOrder 可能 vcc 成功但出票失败 |

### needVcc 判断（边界）

```java
if (needVcc() || !appSettingProp.enableNeedVcc()
    && !gdsSupplierSwitchLogic.isVCOrder(holder.getSupplierOrderModel().getTicketingInfo())) {
    // 走 VCC
}
```

---

## 核心字段（实付表）

| 字段 | 含义 |
|------|------|
| `vccType` | Payable / Paid（应付 / 实付） |
| `trans_type` | Payment / Refund |
| `transCurrency` / `transCurrencyAmt` | 交易币种与金额 |
| `localCurrency` / `localCurrencyAmt` | 开卡币种与金额 |
| `serial_id` | 业务流水（改签单号 / 退款单号） |
| `trans_time` | 交易时间 |

bizContent 关键项：`authId`、`cardLogId`、`transactionId`、`occurTime`、`messageType`。

---

## 历史数据重刷

左闭右开区间，支持手动指定日期：

```json
{
  "startDate": "2024-10-01 00:00:00",
  "endDate": "2024-10-10 00:00:00"
}
```

---

## 踩坑清单

1. 跨库查 orderId 索引失效 → `createTime` 时间窗
2. 退款手续费是否影响实付准确性 → 考虑独立手续费字段
3. 重推 job 是否需要 idc 字段
4. 金额对账：对 `transCurrencyAmt` 异常敏感，先问需求背景再改

---

## 关联

- [[绩效/2024H1-半年报]]
- [[工程/票台排障路径]]
