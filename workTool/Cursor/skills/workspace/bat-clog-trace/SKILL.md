---
name: bat-clog-trace
description: |
  用 BAT MCP（bat-clog / bat-trace）按应用+环境+message 查 CLOG，提取 messageId 并输出 BAT trace 链接。
  用户提到 trace 链接、CLOG、按 message 查日志、FAT/UAT 排障时使用。
---

# BAT CLOG → Trace 链接

通过 **user-bat-mcp-function** MCP 查日志，从命中行取 `messageId`，拼可点击的 BAT trace URL 返回给用户。

## 何时使用

- 用户在 FAT/UAT/生产触发了某请求，要 **trace 链接**
- 按 **message 关键词** 找最近一次（或指定时间段）日志
- 需要 **`bat-trace`** 看完整 CAT 调用链

**不用于**：有 `orderId` 的订单排障主路径 → 优先 [gds-rail-triage](../gds-rail-triage/SKILL.md)（Mongo → msgTrace → CLOG）。

## 执行顺序（必须）

1. **`bat-global-helper`** — 取当前 UTC 时间、环境/appId 规则
2. **`bat-clog`** — 按 appId + env + message + 时间窗查日志
3. 从每条 `<log>` 的 **`messageId`**（或 attribute `cat-msg-id`）拼 trace 链接
4. 可选 **`bat-trace`** — 拉完整 CAT 链路
5. **直接回复用户**：trace 链接 + 命中时间 + 请求摘要（从 request 日志提取）

## MCP 参数

### bat-clog（必填）

| 参数 | 说明 |
|------|------|
| `env` | `fws`（FAT/测试）、`uat`、`pro` |
| `appId` | 纯数字；见仓库 `META-INF/app.properties` 的 `app.id` |
| `fromUtc` / `toUtc` | ISO 8601 UTC；用户说北京时间需 **减 8h** |
| `message` | 日志正文前 128 字符匹配；用接口名、Controller 方法名等短词 |
| `messageId` | 已有 traceId 时，查同 trace 全量日志 |
| `queryLargeFields` | 需要完整 request/response JSON 时设 `on` |
| `eliminateFrameworkProducts` | 只要业务日志时可剔框架；需看 SQL 时 **不要剔 Dal** |

### bat-trace

| 参数 | 说明 |
|------|------|
| `env` | 同 bat-clog |
| `messageId` | 完整 traceId，如 `100053253-0a76277c-495242-8990` |

## Trace 链接模板

| 环境 | URL |
|------|-----|
| FAT / fws / 测试 | `https://bat.fws.qa.nt.ctripcorp.com/trace/{messageId}` |
| 生产 | `https://bat.fx.ctripcorp.com/trace/{messageId}` |

**输出格式（给用户）**：

```markdown
**Trace：** https://bat.fws.qa.nt.ctripcorp.com/trace/{messageId}
- 时间：{timeStr}
- 子环境：{_subEnv_}
- 锚点日志：{message 前 80 字}
```

多条命中时：按时间倒序列出，从 request 日志提取可辨认字段（时间、关键参数）。

## appId 查找

对话里已明确 appId 时直接用；否则 Grep 目标仓库 `app.id=`（如 admin-be → `100053253`）。

## 时间窗建议

| 用户说法 | fromUtc / toUtc |
|----------|-----------------|
| 刚才 / 最新 / 最近 | now - 1h ~ now |
| 给了北京时间具体时刻 | ±3 分钟窗口，转 UTC |
| 未给时间 | 默认最近 1h；命中多条再让用户收窄 |

## 示例（通用）

查 admin-be 某 HTTP 接口最近一次请求：

```json
{
  "env": "fws",
  "appId": "100053253",
  "message": "SomeController someMethod request",
  "fromUtc": "<now-1h>",
  "toUtc": "<now>",
  "queryLargeFields": "on"
}
```

取 **request** 行（非 response）的 `messageId` 拼 trace 链接；需要看下游 SQL/RPC 时再调 `bat-trace`。

## 注意

- `bat-clog` 返回 XML，**不会自动带 trace 链接**；Agent 必须用 `messageId` 拼接 URL。
- `message` 只匹配前 **128 字符**。
- 查无数据：确认 env（FAT 用 `fws`）、时间窗、appId；提示扩大时间或切换环境。
