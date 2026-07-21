---
name: ticket-desk-log-detail
description: "票台订单日志详情查询：根据 orderId 和 msgTrace（调用链 traceId）查询票台系统某次调用的完整日志详情，包括 WARN/ERROR 级别的日志明细。通常在使用 ticket-desk-log-query 获取摘要后，需要进一步查看某次调用的内部处理细节时使用。"
---

# ticket-desk-log-detail

根据 msgTrace（traceId）和环境查询票台系统某次调用的完整日志详情，用于深入排查某个环节的内部处理过程。

## 使用场景

- 在 ticket-desk-log-query 查询到摘要日志后，需要进一步查看某次调用的内部细节
- 排查某次调用中出现的 WARN/ERROR 日志
- 分析价格差异、参数映射异常等内部处理问题
- 追踪单次调用链中各步骤的执行情况

## 前置依赖

通常需要先使用 `ticket-desk-log-query` skill 查询订单日志摘要，从返回的 `logs[].msgTrace` 字段获取 traceId，再用本 skill 查看详情。

## 调用方式

使用 BAT MCP 的 `bat-trace` 工具查询 trace 明细数据。

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `env` | string | 是 | 环境，可选：pro、fws、uat |
| `messageId` | string | 是 | trace 的 messageId/traceId，来自 ticket-desk-log-query 返回的 msgTrace 字段，格式如 `100051894-0a9ac87e-495416-49771` |

### 环境映射规则

- 生产环境 / PRO → `pro`
- 测试环境 / FAT / FWS / 子环境 → `fws`
- UAT 环境 → `uat`
- 默认使用 `pro`

### 调用示例

```
bat-trace(env="pro", messageId="100051894-0a9ac87e-495416-49771")
```

## 输出格式

查询结果展示时：

1. **按级别分组**：优先展示 ERROR 级别日志，再展示 WARN，最后 INFO
2. **错误高亮**：ERROR 和 WARN 级别日志重点标注
3. **关键信息提取**：
   - 从 title 和 source 中识别出是哪个模块/方法产生的日志
   - 从 message 中提取关键业务信息（如价格差异、参数缺失等）
4. **问题归类**：
   - 价格差异类（如 `originTicketAmountDiff`）：提取 oldAmount 和 newAmount
   - 参数缺失类（如 `supplierTicketInfoListBySupplierLegIsEmpty`）：说明缺失了什么数据
   - 映射异常类：说明映射前后的差异
5. **上下文关联**：多条相同 title 的日志合并说明，避免重复信息

## 注意事项

- msgTrace 必须是完整的 traceId 格式（如 `100051894-0a9ac87e-495416-49771`）
- 环境需要用户指定或从上下文推断（如 ticket-desk-log-query 返回的 env 字段）
- 返回的 trace 数据包含该调用链中所有 span 和日志明细
- 日志中的 message 可能包含 JSON 字符串，需要解析后展示关键内容
- 如果查询无结果，提示用户确认环境是否正确
