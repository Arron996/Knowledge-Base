---
name: captain-release
description: |
  Captain 镜像审批与 UAT/PRO 发布 playbook。通过 captain-mcp 查镜像/分组/发布、部署 UAT/PRO；
  填 iDev 与镜像审批需 Captain UI；iDev 号从对话上下文或 GitLab MR 标题/description 提取，测试卡点可尝试 iDev MCP 流转。
  用户提到 Captain 发布、UAT 发布、PRO 发布、填 iDev、镜像审批、忽略发布规范时使用。
---

# Captain 发布

MCP 服务器：**user-captain-mcp**（captain-mcp）。辅助：**user-gitlab-mcp**（MR → iDev）、**user-iDev2**（issue 状态）。

## MCP 能力边界

| 操作 | MCP | 说明 |
|------|-----|------|
| 查应用 / 分组 / 镜像 / 发布记录 | ✅ `get_application_info` `get_groups` `get_images` `get_releases` | |
| 部署 UAT / PRO | ✅ `deploy` | 需镜像已通过对应环境审批 |
| 填 iDev、提交 UAT/PRO 镜像审批 | ❌ | Captain UI 手动 |
| 金丝雀阶段页内点「继续」 | ❌ | 仅当 `skip_smoking: false` 时可能需要 |

**生产发布前必须用户明确确认**（镜像 ID、Group、是否忽略发布规范）。

## 通用流程：填 iDev → UAT 审批 → UAT 发布

适用于所有应用（含 admin-fe）。

```
1. 从 MR 标题或 description 提取 iDev 号
2. （可选）iDev MCP 处理测试卡点 → 见下文「iDev 测试审批」
3. Captain UI：镜像页填 iDev → 提交 UAT 审批 → 等待通过
4. 轮询 get_images 直到 is_uat_approval: true
5. deploy 到 UAT Group（或用户已在 UI 发布则跳过）
6. get_releases(env=uat) 确认 SUCCESS
```

### 1. 获取 iDev 号

按优先级查找（**不必问用户**，除非以下均无）：

1. **对话上下文** — 用户已给出的 iDev Key、技改/需求链接、或本轮 F2B/MR 讨论里出现的 Key
2. **关联 MR 标题** — GitLab MCP `get_merge_request`：读 `title`，匹配 iDev Key（团队规范要求标题含 Key，如 `GDS-9247 feat: …`）
3. **关联 MR description** — 同上工具读 `description`，匹配 iDev Key，常见：`TRAIN-\d+`、`[A-Z]+-\d+`
4. **iDev 搜索** — `iDev2-issue-search` 按 MR 标题、分支名、功能关键词

镜像与 MR 的对应：镜像 `note` / `commit_url` 通常含 MR 号或 commit；用 `get_merge_request_commits` 或 commit SHA 反查 MR，再读 **title**（优先）或 description。

仍无法确定时再问用户提供 iDev Key。

### 2. iDev 测试审批（Captain 卡点时的辅助手段）

Captain 填 iDev 后若提示 **测试审批未通过**，可尝试用 iDev MCP 把 issue 流转到测试通过态：

1. `iDev2-issue-get`（`issueKey`）— 看当前状态
2. `iDev2-issue-transition-statuses` — 列出可流转状态
3. 若列表含「测试通过」或等价态 → `iDev2-issue-update-status`（`issueKey`, `status`）

**注意**：iDev issue 状态 ≠ Captain 镜像审批；流转成功后仍需在 Captain 重试或等同步。若 transition 列表无目标态，说明需人工在 iDev 页操作，MCP 无法代劳。

### 3. Captain UI（MCP 无法替代）

镜像页示例：`https://captain.release.ctripcorp.com/app/{application_id}/image?id={image_id}`

- 填 iDev 号 → 提交 UAT 审批
- PRO 审批同理，等 `is_prod_approval: true`

### 4. UAT 部署（MCP）

```json
{
  "group_id": "<uat_group_id>",
  "image_url": "hub.cloud.ctripcorp.com/gitlab-ci/<app_id>:<image_tag>",
  "auto_next": 1,
  "note": "<MR 标题或 commit message 摘要>"
}
```

UAT 一般无需 `ignore_release_control`；默认 `skip_baking: true`。

### 5. 验证

- `get_images`：`is_uat_approval`
- `get_releases`：`env=uat`, `group_id`, 最新一条 `status=SUCCESS`

---

## admin-fe（gds-order-admin-fe）专用

| 项 | 值 |
|----|-----|
| 应用名 | GDS 订单管理后台 |
| application_id | `100059418` |
| GitLab | `global-rail-gds/gds-order-admin-fe`（project `126917`） |
| 仓库 AppID | `package.json` → `100059418` |
| UAT Group | `81010826` — `trn-gds-order-admin-fe-uat-captain-100059418` |
| PRO Group | `91060954` — `trn-gds-order-admin-fe-application-rb-captain-100059418`（SHARB） |
| 镜像 URL 前缀 | `hub.cloud.ctripcorp.com/gitlab-ci/100059418:` |

### admin-fe PRO 发布（团队约定）

**在 UAT 已发布且 PRO 镜像审批通过后**，PRO 使用以下参数（忽略发布规范 + 跳过金丝雀，减少页内手点）：

```json
{
  "group_id": 91060954,
  "image_url": "hub.cloud.ctripcorp.com/gitlab-ci/100059418:<image_tag>",
  "ignore_release_control": true,
  "skip_baking": true,
  "skip_smoking": true,
  "batch": 3,
  "batch_delay": 60,
  "auto_next": 1,
  "note": "<发布说明>"
}
```

| 参数 | admin-fe PRO 值 | 对应 UI |
|------|-----------------|---------|
| `ignore_release_control` | `true` | 临时关闭发布规范 |
| `skip_baking` | `true` | 跳过堡垒发布 |
| `skip_smoking` | `true` | **跳过金丝雀**（与上次未跳金丝雀导致需手点滚动对比） |
| `batch_delay` | `60` | API 上限 60s（UI 可选 2m，MCP 会被截断） |

PRO 前置：`is_uat_approval: true` 且 `is_prod_approval: true`（用户确认或 `get_images` 校验）。

发布链接：`https://captain.release.ctripcorp.com/app/100059418/release?id={release_id}`

---

## deploy 参数速查

| 参数 | 默认 | 说明 |
|------|------|------|
| `group_id` | 必填 | 目标 Group |
| `image_url` | 必填 | 完整镜像 URL |
| `ignore_release_control` | `false` | 临时关闭发布规范 |
| `skip_baking` | `true` | 跳过堡垒/Baking |
| `skip_smoking` | `true` | 跳过金丝雀；`false` 时可能需在页内手点继续 |
| `batch` | `2` | 批次数；admin-fe PRO 用 `3` |
| `batch_delay` | `0` | 批间秒数，**≤ 60** |
| `auto_next` | `1` | 自动进入下一步 |
| `note` | `""` | 发布说明 |

`deploy` 基于 Group 最近一次成功 release 的 version 参数，仅替换 `image_url`。

---

## 执行顺序（Agent）

1. 确认目标：**UAT 还是 PRO**、镜像 ID 或 tag
2. admin-fe → 用上表 Group / app_id；其他应用 → `get_application_info` + `get_groups`
3. 无 iDev → 先查对话上下文与关联 MR **title** / description，再 iDev search；仍无则问用户
4. 测试审批卡点 → iDev transition 流程（上文）
5. 镜像审批未过 → 指引 Captain UI，轮询 `get_images`
6. **PRO**：用户确认后 `deploy`（admin-fe 用 PRO 专用参数）
7. `get_releases` 回报 release id、status、Captain 链接

## 禁止

- 未经用户确认 deploy PRO
- 假设 MCP 已填 iDev 或已提交镜像审批
- `batch_delay` > 60（API 400）

## 扩展其他应用

在 [apps/](apps/) 下新增 `{app}.md`，复制 admin-fe 表格结构；本 SKILL 通用节不变。
