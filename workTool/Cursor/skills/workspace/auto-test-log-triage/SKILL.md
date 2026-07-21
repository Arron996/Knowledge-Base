---
name: auto-test-log-triage
description: >-
  测试/联调失败或「打包后未生效」时，从相关代码提取日志关键字与 appId，
  自动串联 BAT MCP（CLOG/部署）+ Admin MCP（订单日志）+ 其他已配置 MCP 做根因排查。
  在用户说查日志、为什么没生效、联调失败、打包后不对、帮我排查测试问题时使用。
---

# 测试问题自动日志排查

## 目标

在**不猜测**的前提下，用代码里的可观测信号（log / MQ topic / appId）去环境里验证：**有没有流量、有没有跑到新逻辑、卡在哪一环**。

## 触发

- 用户说：查日志、打包后没生效、测试不对、飞书/邮件没收到、功能没走到
- 刚完成 F2B / 发布后的联调验收
- 需要**主动触发 MQ** 再排查 → 先发 Q：[fat-qmq-send](../fat-qmq-send/SKILL.md)，再回本 skill 验证

## 输入收集（缺什么先问什么）

| 项 | 来源 |
|----|------|
| 功能/类名 | 当前改动文件、Processor/Consumer 名 |
| 环境 | 用户口述；未说则 **fws**（测试），生产相关用 **pro** |
| 时间窗 | 用户测试时间 ±1h；只说「刚才」→ 最近 1h |
| orderId | 有则必用 Admin MCP；无则只靠 CLOG |
| 期望现象 | 例如「应发飞书群告警」「Admin 应展示 GDPR 字段」 |

## Step 1：从代码提取排查指纹

在**本次改动涉及的类**中收集：

1. **log 文案**（`log.info/warn/error` 的英文模板，取 distinctive 片段）
2. **log title**（若有 `[[title=xxx]]`）
3. **MQ topic / consumer 名**（`QmqConstant`、Consumer 类）
4. **appId**：各仓库 `**/META-INF/app.properties` 的 `app.id`

常用 appId（macOS 工作区）：

| 系统 | appId |
|------|-------|
| 票台 gds-ticketing-system | 100051894 |
| Admin BE gds-order-admin-be | 100053253 |

跨应用链路要查**两端**（例：票台 Lark MQ → Admin BE 消费发飞书）。

## Step 2：BAT 全局参数

先调用 `bat-global-helper`，再查 CLOG。时间一律转 **UTC ISO**。

## Step 3：CLOG 查询策略（bat-clog）

按优先级依次查，**前一个有业务日志就深入，不要只查 QMQ 心跳**：

```
1. message = Processor 入口 log 片段（如 "GdprSubOrderNotifyProcessor handle start"）
2. source = *ClassName*（如 *GdprSubOrderNotifyProcessor*）
3. title = larkMqSend / 代码里 [[title=...]]
4. message = MQ topic 名（区分 MetaInfoService 心跳 vs 真实消费）
5. logLevel = 2,3 只看 WARN/ERROR
```

- `queryLargeFields=on` 当需要完整 message
- 框架噪音多时可 `eliminateFrameworkProducts=SOA,Dal,QMQ,QConfig`
- fws 无结果 → 提示用户确认环境，必要时再查 pro

## Step 4：Admin MCP（有 orderId 时）

| 工具 | 用途 |
|------|------|
| `query-logs` | 订单全链路 + 下游票台/VC BAT trace |
| `query-order-logs` / `query-ticket-logs` | 分阶段日志 |
| `get-recent-deployments` | 近 30min 是否有 Release/ConfigModify |

## Step 5：部署 vs 合码 判定

| 现象 | 结论 |
|------|------|
| CLOG 完全无业务 log，仅有 QMQ Consumer status/Heartbeat | 消费者在线但**可能没有测试流量**，或查错环境/时间 |
| 有旧 log 文案（如 sendEmail 告警）无新 log（如 larkMqSend） | **实例未发布新包**（F2B 只合 develop/base，还需 Captain 发布） |
| 有 `privacy contact not configured` | DB/供应商配置未发布或未填 GDPR 字段 |
| 票台有 `larkMqSend`，Admin BE 无 `Lark notify user` | Admin BE 未消费或未部署 |
| Admin BE `Lark notify user: send failed` | 飞书 chat_id/open_id 或权限问题 |

## Step 6：输出模板

```markdown
## 排查结论

**环境**：fws / pro  
**时间窗**：...

### 日志证据
- [有/无] 入口 Processor 日志
- [有/无] 失败/告警日志
- [有/无] 下游 Admin Lark 消费

### 根因判断
（部署未生效 / 无测试流量 / 配置缺失 / 跨应用链路断裂）

### 建议下一步
1. ...
```

## 禁止

- 未查日志就断言「代码没问题」
- 把 QMQ MetaInfoService 心跳当成业务已执行
- 只查票台不查 Admin BE（Lark/部分配置类问题）

## 扩展

- QConfig 变更：`get-recent-deployments` category=ConfigModify，或 qconfig-mcp
- 指标：`bat-tx-data` / `bat-event-data` 查 Consumer 处理量
- 前端未生效：确认 Admin FE 是否从 develop/base 构建发布，浏览器强刷
