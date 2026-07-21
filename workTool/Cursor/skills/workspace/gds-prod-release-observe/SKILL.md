---
name: gds-prod-release-observe
description: |
  票台/出票高影响改动的生产发布观察：按 Captain 发布集群（IDC/Pod）拉 createOrder/obtainTicket 真实订单并按技改断言校验。
  触发：用户说发布后观察、线上验证、灰度观察、拉发布集群订单；或改动 createOrder / obtainTicket / 乘客映射 / 状态机 / 拦截校验；
  或写涉及生单/出票主流程的 plan 时——须先问用户「要不要包含发布监控方案」，由用户决定后再写入 plan 或执行观察。
---

# GDS 生产发布观察

适用：**生单 / 出票主流程**的高影响改动上线后（或 plan 阶段规划观察）。  
目标：验证**打到本次发布实例**的真实订单，而不是全网随机单。

相关技能：[`captain-release`](../captain-release/SKILL.md)、[`bat-clog-trace`](../bat-clog-trace/SKILL.md)、[`gds-rail-triage`](../gds-rail-triage/SKILL.md)。

## 何时必须先问用户

命中下方**任一**时，**先问一句，等用户决定**，再写入 plan 或执行观察。不要默认强加整段监控流程。

**问法（原话可用）：**

> 这次改动碰了生单/出票主流程，要不要在方案里加「生产发布监控观察」步骤？（发布后按集群拉单 + 按技改断言校验）

**须提问的场景：**

1. **写 plan / CreatePlan**：改动涉及主流程生单、出票，或触及 `createOrder` / `obtainTicket` / 乘客映射 / 状态机 / 拦截校验
2. **理解或实施方案**：同上触点，且将上生产或做 PRO 灰度
3. 用户未明确说「要观察 / 不要观察」时

**用户说要 →** plan 增加「阶段：生产发布观察」并按下文 checklist；发布后按 **执行流程** 跑。  
**用户说不要 →** 不写该阶段，可仅保留 FAT/MR；不要反复追问。

## 高影响触点（触发提问）

| 触点 | 例 |
|------|-----|
| `createOrder` | 创单入口、分单、Mapping、落库 |
| `obtainTicket` | 取票 before/execute、Consumer、结果 MQ |
| 乘客映射 | `SupplierPassengerMapping`、`certNo`、证件加解密 |
| 状态机 | 子单/obtain/出票状态流转、allowObtain 等 |
| 拦截校验 | 到达时间、状态拦截、灰度开关、BusinessException 门禁 |

汽船票台等同理：用对应 `app.id`，断言按技改改。

---

## 执行流程（用户确认要观察，或主动要求发布后校验）

### Step 0 — 锁定发布面

| 项 | 来源 |
|----|------|
| `appId` | 仓库 `META-INF/app.properties`（火车票台常见 `100051894`） |
| 镜像 / commit | Captain `get_releases` / admin `get-recent-deployments` |
| 含不含本次改动 | `git merge-base --is-ancestor <feature-commit> <image-sha>` |
| IDC / group | 用户指定或本次 PRO 发布 group（如 SHARB） |
| Pod IP | Captain `get_pods` |
| 时间窗 | 发版 **SUCCESS 完成时刻** → now（北京时间转 UTC：减 8h） |

**禁止**用「供应商名 = IDC」误查；SHARB 是机房不是供应商。

### Step 1 — 健康面（BAT 指标）

MCP：`user-bat-mcp-function` → `bat-tx-data`

```json
{
  "env": "pro",
  "appId": "<appId>",
  "idc": "<发布IDC，如 SHARB>",
  "type": "URL",
  "name": "/api/gdsticketingservice/json/createOrder",
  "groupBy": "name",
  "fromUtc": "<发版完成UTC>",
  "toUtc": "<now UTC>"
}
```

obtain 另查：`.../json/obtainTicket`。记录 **count / fail / failRatio**。

### Step 2 — 拉发布集群订单（BAT 日志）

对 group 内 **每个 Pod IP**（或先 1～2 台）：

```json
{
  "env": "pro",
  "appId": "<appId>",
  "queryIdc": "SHA",
  "hostIp": "<podIp>",
  "message": "createOrder",
  "fromUtc": "<发版完成UTC>",
  "toUtc": "<now UTC>",
  "eliminateFrameworkProducts": "CRedis,SOA,Dal,Clogging,Hermes,Apollo,QMQ,QConfig"
}
```

obtain：`"message": "obtainTicket"`；ERROR：同条件加 `"logLevel": "3"`。

从日志提取 `orderId`（attributes `order_id` / message 内 JSON）。  
建议：生单 ≥10（不够则说明流量稀）；obtain 按实际流量，≥1 也要写清样本量。

**不要**只靠 `supplier_sub_order_statistics` 下结论——无 IDC 维度，不能证明打到发布实例。

### Step 3 — 按技改断言校验

对每个关键 orderId：

1. Admin：`query-ticket-logs`（`stage=book_order` 或 `actions=ticket#createOrder` / `ticket#obtainTicket`）
2. 订单详情：`queryTicketDeskOrderInfo` 或 DOT（乘客/子单时间/状态）
3. 负向：BAT 搜**旧行为关键词**（发版后窗口、同 host/idc）须为 **0**

#### 断言模板（按技改改写）

| 类型 | 示例 |
|------|------|
| 正向透传 | createOrder 请求 `certNo` == DB `cert_no`（Admin 脱敏时两侧须同值） |
| 正向放行 | 已过到达时间仍 `obtainTicket` success（须有匹配样本） |
| 负向消失 | 无 `LocalShield` / `CoreInfo` / `encryptNotEqual` / `obtain ticket time passed` |
| 健康 | URL fail=0；样例子单状态符合预期（如 600 / obtain 成功） |

样本不足（如无「已过到达」单）时：**明确标注「证据不足」**，勿谎称全面通过。

### Step 4 — 汇报用户

简明结构：

1. 发布面（镜像、IDC、时间窗、是否含 feature commit）
2. 指标（count / fail）
3. 订单表（orderId、供应商、状态、关键字段对照）
4. 断言结果（✅ / ❌ / ⚠ 样本不足）
5. 建议（继续观察 / 扩大 IDC / 回滚门槛）

---

## Plan 内嵌模板（用户同意「包含发布监控」时粘贴）

```markdown
### 阶段 N：生产发布观察验证

**触点：** createOrder / obtainTicket / 乘客映射 / 状态机 / 拦截校验（勾选用到的）

**前置**
- [ ] Captain 确认 appId、group、IDC、镜像 commit 含本次改动
- [ ] 记录发版 SUCCESS 时间与 Pod IP

**拉单（仅发布集群）**
- [ ] `bat-tx-data`：idc + createOrder / obtainTicket → count/fail
- [ ] `bat-clog`：hostIp + 接口 message → 抽 orderId（生单建议≥10）
- [ ] 排除发版完成前的流量

**技改断言**
- [ ] 正向：…
- [ ] 负向旧路径=0：…
- [ ] 健康：fail=0 + 样例状态符合预期

**门槛**
- 通过：断言全绿（或标注样本不足项经人工接受）
- 回滚：fail 上升 / 关键断言失败 / 不可用 ERROR
```

---

## 注意

- 只观察 **已发布成功** 的 group；滚动中可分 IDC 分批报。
- Admin / ticket-log **会脱敏**；比的是「请求 vs 入库是否同值」，不是明文真值。
- 发版前历史窗口出现旧错误文案，不能单独证明「本次已下线」；须看**本镜像 + 本 IDC** 发版后窗口。
- 生产观察 **不能代替** FAT；FAT 仍走 f2b / fat-* skills。
