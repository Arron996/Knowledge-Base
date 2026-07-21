---
name: fat-qmq-send
description: |
  FAT/FWS 测试环境向 QMQ 合法发消息（抛 Q、联调触发 MQ）。
  用户说发 Q、抛 Q、投 MQ、测 Consumer、del.sync、联调消息时使用。
  走票台 Pod internal HTTP（首选）；发前检查 topic 白名单与 100051894 producer 权限。
---

# FAT 测试环境发 Q（票台）

在 **非 PROD** 环境触发 QMQ，用于联调 Consumer / 端到端测试。**禁止**猜未部署的 FaaS 或本地乱起 jar 浪费时间。

## 何时使用

- 用户说：**发 Q / 抛 Q / 投 MQ / 测这条 MQ / 联调 Consumer**
- 测试需要**主动触发**消息（GDPR `del.sync`、内部 Worker topic 等）
- 已有订单/数据，只差「发一条 Q 验证链路」

**不用于**：查消息是否被消费 → `qmq-mcp` `findMessages`；只看日志 → [bat-clog-trace](../bat-clog-trace/SKILL.md)；发 Q 后的根因排查 → [auto-test-log-triage](../auto-test-log-triage/SKILL.md)。

## 发 Q 前检查（必须）

| # | 条件 | 说明 |
|---|------|------|
| 1 | **环境** | 仅 FAT / FWS / UAT；`InternalQmqSendService` **禁止 PROD** |
| 2 | **Topic 白名单** | 须在票台 `InternalQmqSendService` 允许列表内（见下表） |
| 3 | **Producer 权限** | QMQ 平台为 **app.id=100051894**（票台）申请该 **subject 的 producer** |
| 4 | **实例已发布** | 含 internal 接口的代码须在目标环境 Pod 上（F2B 合 base ≠ 自动发布，需 Captain 有 Release） |

### 票台 internal 白名单（代码内）

路径：`gds-ticketing-business/.../devtools/InternalQmqSendService.java`

| Topic / 模式 | 说明 |
|--------------|------|
| `trn.train.global.rail.gds.order.del.sync` | GDPR Ingress |
| `trn.train.global.rail.gds.ticketing.gdpr.sub.order.notify` | GDPR Worker |
| `trn.train.global.rail.gds.ticketing.*` | 票台前缀通配 |

**新 topic 不在上表**：先在 `ALLOWED_TOPICS` 加条目（或扩前缀）→ F2B → 发布测试环境 → 再发 Q。

### 新增 Topic 协作清单

```
- [ ] QMQ 控制台：subject 已创建；100051894 已申请 producer
- [ ] 代码：InternalQmqSendService 白名单已包含（如需）
- [ ] 测试环境 Captain Release 成功
- [ ] GET /internal/qmq/health 返回 ok
- [ ] POST /internal/qmq/send 返回 success: true
```

## 推荐发 Q 路径：票台 Pod internal HTTP

Producer 身份与线上一致（`MessageQueueImpl`，app **100051894**）。**不要**先试 `qmq-send-function` FaaS，除非已确认域名可访问。

### Step 1：拿 Pod IP

**MCP**：`user-captain-mcp`

```text
get_groups(application_id=100051894, env="fat")   # 或 fws 组
get_pods(group_id=<目标组 id>)
```

常用组：`fws-captain-100051894`（group_id **71124222**）、`fat22-captain-100051894` 等。  
取 **Ready** Pod 的 `ip`，端口默认 **8080**。

### Step 2：健康检查

```bash
curl -sS -m 5 "http://<pod-ip>:8080/internal/qmq/health"
# 期望：{"status":"ok","appId":"100051894","env":"FWS"|"FAT",...}
```

404 / 连不上 → 该环境**未部署**含 `InternalQmqSendController` 的版本，先 Captain 发布，**不要**换别的发 Q 方式硬试。

### Step 3：发 Q

```bash
curl -sS -m 15 -X POST "http://<pod-ip>:8080/internal/qmq/send" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "<subject>",
    "key": "body",
    "value": "<JSON 字符串，需转义>",
    "delaySeconds": 0
  }'
```

成功响应示例：

```json
{"success":true,"topic":"...","key":"body","env":"FWS","error":null}
```

失败常见原因：

| 响应 / 现象 | 处理 |
|-------------|------|
| `topic not allowed` | 改白名单 + 发布 |
| `internal qmq send is forbidden in PROD` | 换 FAT/FWS Pod |
| `success: false` / QMQ send failed | 查 **100051894 是否缺 producer 权限** |
| connection refused | Pod IP/端口错或实例未 Ready |

### Step 4：发 Q 后验证（与发 Q 成对）

```
Task Progress:
- [ ] 等待 5～10s
- [ ] DOT：业务表最终状态（如 ticket_gdpr_notify_record.notify_status）
- [ ] bat-clog：orderId / Processor 入口 log（appId=100051894, env=fws）
- [ ] 结论以 DB + 业务 log 为准，不单靠 QMQ 心跳
```

详见 [auto-test-log-triage](../auto-test-log-triage/SKILL.md)。

## 备选：QMQ 控制台手动发

适合人工一次性验证；trace 中操作人常为 `qmq_portal-operator: <user>`。

- Subject、key（通常 `body`）、value 与线上一致
- 仍需 **producer 权限**（与 internal API 相同）

## 不推荐路径（默认跳过）

| 路径 | 原因 |
|------|------|
| `qmq-send-function.fws.faas.qa.nt.ctripcorp.com` | 常未部署（404）；见 `qmq-send-function/README.md` |
| 本地 `java -jar qmq-send-function` | 依赖重、易版本冲突 |
| 猜对外域名 `/internal/qmq` | 仅 Pod 内网 IP 可达 |

若用户明确要求 FaaS：先 `curl .../health`，**200 再用** `qmq-send-function/scripts/send-qmq.sh`。

## 常用消息体示例

### GDPR Ingress

| 项 | 值 |
|----|-----|
| topic | `trn.train.global.rail.gds.order.del.sync` |
| key | `body` |
| value | `{"orderId":1688920223383488,"delReqTimeStr":"2026-07-09 16:53:46"}` |

`delReqTimeStr` 格式：**yyyy-MM-dd HH:mm:ss**（必填）。

### GDPR Worker（单测 Worker 时用）

| 项 | 值 |
|----|-----|
| topic | `trn.train.global.rail.gds.ticketing.gdpr.sub.order.notify` |
| value | `{"orderId":...,"orderItemId":...,"retryTimes":0}` |

通常由 Ingress 自动投；手投前确认 DB 已有对应 PENDING 记录或理解幂等行为。

## 选单建议（GDPR 等按子单消费）

发 Ingress 前可在 FAT 库确认：

```sql
SELECT s.order_id, s.order_item_id, s.supplier, s.supplier_order_id, s.idc
FROM supplier_sub_order s
LEFT JOIN ticket_gdpr_notify_record g
  ON s.order_id = g.order_id AND s.order_item_id = g.order_item_id
WHERE s.supplier = 'itntv'   -- 按需改供应商
  AND s.supplier_order_id IS NOT NULL AND s.supplier_order_id != ''
  AND s.idc = 'NTG'
  AND g.order_id IS NULL
ORDER BY s.order_id DESC
LIMIT 10;
```

订单详情：`user-gds-order-admin-mcp-fat` → `query-order`（mini）。

## 用户话术 → Agent 行为

| 用户说 | Agent 做 |
|--------|----------|
| 帮我对这单抛 Q 测 GDPR | 查子单 → Captain 拿 Pod → internal send → DOT + CLOG 验证 |
| 发 del.sync | 用 Ingress topic + orderId + delReqTimeStr |
| 这个新 topic 能发吗 | 对白名单 + 提醒申请 100051894 producer |
| 发 Q 没反应 | 先 health → 再查 producer / 是否发布 / CLOG 是否 IDC 过滤跳过 |

## 相关代码与文档

| 资源 | 路径 |
|------|------|
| Internal Controller | `gds-ticketing-gateway/.../internal/InternalQmqSendController.java` |
| 白名单与发送 | `gds-ticketing-business/.../devtools/InternalQmqSendService.java` |
| FaaS 备选（可选） | `qmq-send-function/README.md` |
| QMQ 查消息 | MCP `user-qmq-mcp` → `findMessages` |
| 快捷脚本 | `.cursor/scripts/fat-qmq-send.sh <pod-ip> <topic> <value-json>` |
