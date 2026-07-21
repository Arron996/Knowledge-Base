---
name: exception-config-assistant
description: |
  异常配置智能助手。解析供应/运营关于 Mapping Error Config 的需求，
  通过 HTTP 调 Admin BE：decide → 草稿 → 提审。禁止 publish。
  当用户提到异常配置、置失败、errorCode、supplier creatOrder、Mapping Error Config 时使用。
---

# 异常配置助手 Skill（本地 Cursor）

编排层负责理解意图与调用顺序；**CREATE/UPDATE/SKIP/CONFLICT 必须由 decide HTTP 决定**，禁止仅靠 LLM 拍板写草稿。

设计文档（飞书技改）：
https://trip.larkenterprise.com/wiki/V5a3wW2boigPbQkNafzcY5dVnSb

原 MCP 手册（演进为 HTTP + SubAgent）：
https://trip.larkenterprise.com/wiki/FPzywXVraidBSKkpUUmctkCDn4j

## 本地怎么用（Cursor）

1. 对话里直接说需求，例如：`gosrt createOrder 100007 Reservation failed 直接失败`，或明确「查/改异常配置」。
2. 本 Skill 会被加载；按下面编排调 **Admin BE HTTP**（不要等 MCP）。
3. **正确入口：Baiji SOA `/api/<method>`（与排障/生单同构，无 CAS）**  
   基址：`http://global.rail.order.admin.be.fat22.qa.nt.ctripcorp.com`  
   - 已有先例：`POST /api/queryTicketDeskLogSummary`（无需 cookie）  
   - 异常配置待加：`/api/queryExceptionConfigList`、`/api/queryPendingExceptionConfigs`、`/api/decideExceptionConfig`、`/api/saveExceptionConfigDraft`、`/api/submitExceptionConfigReview`  
   - 原理：admin-be `SoaConfig` 把 `GdsOrderAdminSystemServiceImpl` 挂到 `/api/*`；**不是**把 `/function` 整站免登。
4. **错误入口（不要用）**  
   - `/function/config/errorConfig/*`：Admin 人机页面 API，**要 CAS** → `not login`  
   - `gds.tciket.system...`：别的 SOA 网关，没有异常配置 method  
5. 提审后去 Admin FE 人工审核发布（仍要人登录页面）：  
   - 火车 Mapping Error Config / 汽船对应页  
6. 上述 `/api/queryException*` 未合 FAT 前：可用 DOT 只读 DB 辅助排查；**禁止**猜 CREATE/UPDATE 写库。

鉴权预期：内网 + Baiji `/api`（与 TicketDesk 相同）。写操作仅草稿+提审；禁止 publish。

## 编排顺序（必须遵守）

1. **Parse**：结构化 supplier / exceptionStage / errorCode / originErrorMessage / intentProcessType / bizLine（rail|bus）
2. **decide**（必调）：`POST .../agent/decide` → CREATE | UPDATE | SKIP | CONFLICT
3. **Draft**：仅当 action 为 CREATE/UPDATE 时 `POST .../save`
4. **compare**：`POST .../compareOnline`
5. **submitReview**：`POST .../submitReview`（0→待审，不是 publish）

任一步 CONFLICT、解析失败、或 decide=SKIP → 终止，不写草稿。

## HTTP 对照表（Baiji `/api`）

| 步骤 | Method + Path | 状态 |
|------|---------------|------|
| 查已发布配置 | POST `/api/queryExceptionConfigList` | **已加** |
| 查待办草稿 | POST `/api/queryPendingExceptionConfigs` | **已加** |
| decide / save / submit | 后续迭代 | 未做 |

基址 FAT：`http://global.rail.order.admin.be.fat22.qa.nt.ctripcorp.com`

### queryExceptionConfigList 示例

```json
POST /api/queryExceptionConfigList
{
  "bizLine": "rail",
  "suppliers": ["euros"],
  "pageNo": 1,
  "pageSize": 5
}
```

### queryPendingExceptionConfigs 示例

```json
POST /api/queryPendingExceptionConfigs
{ "bizLine": "rail" }
```

可选字段：`originErrorCodes`、`originErrorMessages`、`exceptionStages`、`processTypes`、`standardErrorCodes`。`bizLine` 支持 `rail`（默认）/ `bus`。

**不要**调 `/function/config/errorConfig/*`（CAS）。排障自检：`POST /api/queryTicketDeskLogSummary`。

## 禁止

- 调用 `/approve`、`/publish`、rollback、forbid
- 直连数据库或 Redis
- 无 decide 结果（或 decide=SKIP/CONFLICT）直接 save
- 仅由 LLM 决定 CREATE/UPDATE
- 手工推算 standardErrorCode（必须 nextStandardErrorCode 或复用已有）

## 配置原则（写草稿前必须遵守）

### 1. 供应商：默认必填，空 = ALL

- 配置里 **不填 supplier** → 运行时匹配**全部供应商**（UI 常显示 ALL）。
- **原则上必须指定供应商**，缩小影响面；只有用户/运营**明确要求「全供应通用」**时才允许空 supplier。
- Agent 缺省 supplier 时：先追问；不得默认写成 ALL。
- 查询时：按供应商筛会包含该供应专属行 **以及** 空 supplier 的 ALL 行（两边都要评估是否已覆盖）。

### 2. 优先复用已有配置，少新建

写草稿前先 `getExceptionConfigList`（含 ALL 行），按下面优先：

| 已有情况 | 动作 | 举例 |
|----------|------|------|
| 同 supplier+stage+code（或 ALL 已覆盖）且 processType 已正确 | **SKIP** | 已有 gosrt + CREATE + 100007 → SUB_CREATE_FAIL，需求也是置失败 |
| 同行匹配、processType 不对 | **UPDATE** 改 processType | 已有 SUB_CREATE_RETRY，需求改为直接失败 → 改成 SUB_CREATE_FAIL，**不要**再插一行 |
| 已有宽行（无 originMessage / 空 code）且可安全收窄 | **UPDATE** 补 originErrorMessage 或收窄 code | 宽行「100007 + 空 message + RETRY」误伤其它文案 → 加上 `Reservation failed` 关键词 |
| 宽行正在服务多种文案、不能改 | **CREATE** 更精确行 | 宽 ALL/宽 message 必须保留；新问题用「指定供应 + 指定 message」精确行（匹配权重更高） |
| 标准错误文案/码已存在 | **复用** standardErrorCode | 同义「call supplier failed」用已有 100007，禁止再 nextCode |
| 已有待审草稿 / 冲突重叠 | **CONFLICT**，停写 | 同 bizId 待审、或两行会命中同一场景但 processType 不同 |

一句话：**能 UPDATE 就不要 CREATE；能 SKIP 就不要动；能复用标准码就不要新码。**

### 3. 匹配维度：宁窄勿宽

出票匹配优先级（数字越大越高）：**originErrorMessage 权重最高**，其次 errorCode / supplier / stage / tag。

- **stage**：默认必填（如 CREATE_SUB_ORDER）；空 stage 会跨阶段误伤，须用户确认。
- **errorCode**：尽量填写；空 code 等同该供应+阶段下「任意供应商错误码」都可能命中。
- **originErrorMessage**：用稳定、有辨识度的子串；多关键词用 `;` 分隔；避免过短词（如 `error`、`fail`）导致误匹配。
- **禁止擅自拓宽**：不要为图省事删掉 supplier / message / stage；拓宽须用户明确同意。
- **收窄优先于新建**：给宽行加 message，优于平行再插一条同 code 宽行。

### 4. processType 与 stage 一致

- 生单/扣位阶段用 CREATE 系（如 SUB_CREATE_FAIL / SUB_CREATE_RETRY），不要套退票/出票阶段的 processType。
- 瞬时故障（超时、5xx）倾向 **RETRY** + 合理 maxRetryTimes/retryInterval；明确业务失败（sold out、证件不支持）倾向 **FAIL**，避免无意义重试。
- 改 processType 时核对 retry 字段是否仍合理（FAIL 不必保留超大重试次数）。

### 5. 标准码与业务线

- 标准码：先查已有 `exp_error_code_config`；同义复用；仅全新语义才 `nextStandardErrorCode`。
- **rail / bus 配置库分离**：汽船问题不要改火车配置，反之亦然；`bizLine` 必须正确。

### 6. 影响面与确认

写草稿前向用户用一句话确认影响面，例如：  
`将配置为 supplier=gosrt, stage=CREATE_SUB_ORDER, code=100007, message含"Reservation failed", processType=SUB_CREATE_FAIL（非 ALL）`。  
涉及 **空 supplier / 空 stage / 空 code / 改宽行 processType** 时必须二次确认。

## Decide 规则摘要

与出票 `ExceptionOrderMapConfigLogic` 一致（服务端 DecideService 实现；本地不得另写一套）：

- 已命中且 processType 正确 → SKIP
- 已命中但 processType 不同 → UPDATE
- 宽兜底行可安全收窄 → UPDATE（加 originErrorMessage）
- 宽行不能改 → CREATE 精确行
- 无命中 → CREATE
- 重叠冲突 → CONFLICT

## 口语映射

| 口语 | 标准值 |
|------|--------|
| creatOrder / 生单 | CREATE_SUB_ORDER |
| 直接失败 / 置失败 | SUB_CREATE_FAIL（CREATE 阶段） |
| code：100007 | errorCode=100007 |
| 汽船 / bus | bizLine=bus |
| 火车 / rail（默认） | bizLine=rail |

## 示例

用户：gosrt createOrder 100007 Reservation failed 直接失败

1. Parse → supplier=gosrt, stage=CREATE_SUB_ORDER, code=100007, processType=SUB_CREATE_FAIL, bizLine=rail
2. `POST .../agent/decide` → 若已有 SUB_CREATE_RETRY → UPDATE
3. `POST .../save` → `compareOnline` → `submitReview`
4. 告知用户在 Admin Mapping Error Config 审核发布
