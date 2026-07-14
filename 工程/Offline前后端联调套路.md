---
title: Offline 前后端联调套路
tags:
  - 工程
  - Offline
  - 前端
sources:
  - "[[import/yuque/笔记/work/WORK]]"
created: 2026-07-08
---

# Offline 前后端联调套路

> 2024 通票 / 日铁人工出票页面沉淀。文件上传 + JSON 混合参数的典型解法。

---

## 文件上传接口设计

**问题**：`@RequestBody` 不能传文件；`@RequestParam` 必须传全部参数。

**解法**：`@RequestParam` + `FormData`，集合字段 JSON 序列化后后端反序列化。

### 前端

```javascript
const formData = new FormData();
fileList.forEach((item) => formData.append('files', item));
formData.append('orderId', row.orderId);
formData.append('orderItemId', row.orderItemId);
formData.append('resultType', 'TICKET_SUCCESS');
formData.append('ticketVoucherList', JSON.stringify(ticketVoucherList));
formData.append('segmentTicketList', JSON.stringify(segmentTicketList));
formData.append('fileTicketMap', JSON.stringify(Object.fromEntries(fileTicketMap)));
```

### 后端

```java
List<TicketVoucherDTO> list = JsonUtil.fromJsonToList(ticketVoucherListJson, TicketVoucherDTO.class);
List<SegmentTicket> segments = JsonUtil.fromJsonToList(segmentTicketListJson, SegmentTicket.class);
Map<String, String> fileMap = new ObjectMapper().readValue(fileTicketMapJson,
    new TypeReference<Map<String, String>>() {});
```

日铁场景：`Dragger` 多文件 + `customRequest` + `fileTicketMap` 映射乘客与文件。

---

## 请求封装

```javascript
// 普通 JSON
export function sendShortMessage(data) {
  return axios({ url: '/api/event/message/send', method: 'post', data });
}

// 人工出票（可走 originAxios 避免全局拦截）
export function manualTicket(data) {
  return originAxios({ url: '/api/newTicket/manual/result', method: 'post', data });
}
```

---

## 本地代理

`package.json` 或 devServer proxy 示例：

```json
"proxy_bak": "http://localhost:8080/",
"proxy": "http://web.globalrail.offline.train.fat20.qa.nt.ctripcorp.com/"
```

`localProxy` 可配多环境；**改完需重启** dev server。

---

## 关联

- [[领域/通票X产品人工出退改]]
- [[工程/票台排障路径]]
