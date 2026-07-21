---
name: gds-api-deploy
description: |
  在 GitLab Maven Deploy 页发布 gds-ticketing-api。Cursor 可拼 URL 并打开页面；最终 Deploy 点击需用户确认后手动完成，或改用 Codex Computer Use 全自动。
  用户提到 gds-api-deploy、Maven Deploy、deploy api、gds-ticketing-api 发布时使用。
---

# GDS API Deploy

在 **gds-ticketing-system** 的 GitLab Maven Deploy 页，为 **`gds-ticketing-api`** 触发 Deploy。

## 能力边界（Cursor vs Codex）

| 操作 | Cursor | Codex Computer Use |
|------|--------|-------------------|
| 拼 Maven Deploy 分支 URL | ✅ | ✅ |
| 用已登录浏览器打开页面 | ✅ `open_resource` | ✅ |
| 读页面、定位 `gds-ticketing-api` 行 | ❌ | ✅ |
| 点击 Deploy 按钮 | ❌（需用户手动） | ✅ |
| 轮询 history 确认成功 | ❌ | ✅ |

**GitLab MCP 无 Maven Deploy API**，不能绕过 UI 触发发布。

若用户要**全自动点 Deploy**，明确告知 Cursor 做不到，建议在同一台 Mac 上用 **Codex + Computer Use** 并引用 `$gds-api-deploy`（`~/.codex/skills/gds-api-deploy`）。

## URL 规则

**项目**：`global-rail-gds/gds-ticketing-system`

**分支详情页**（Deploy 按钮在此页）：

```
https://git.dev.sh.ctripcorp.com/global-rail-gds/gds-ticketing-system/maven_deployments/{branch_encoded}
```

`{branch_encoded}` = 分支名把 `/` 换成 `%2F`。示例：

| 分支 | URL 片段 |
|------|----------|
| `develop/base_20260528_bt3` | `develop%2Fbase_20260528_bt3` |
| `feature/GDS-1234_foo` | `feature%2FGDS-1234_foo` |

用户给**完整 URL** 时直接使用；只给**分支名**时按上表拼接。

## 执行顺序（Cursor）

1. 从用户消息提取完整 URL 或分支名；分支名按上节编码。
2. 复述：**分支**、**制品**（默认 `gds-ticketing-api`）、目标 URL。
3. **`open_resource`** 打开 URL（`https://...`），提示用户在已登录浏览器中确认页面分支正确。
4. **Deploy 前必须用户明确确认**（例如回复「确认 deploy」）。未确认前**不要**声称已发布。
5. 确认后：请用户在页面找到 **`gds-ticketing-api`** 行，点击 **Deploy**；若出现二次确认弹窗，先说明再点。
6. 请用户回报：history 是否出现新行、时间戳、状态（进行中 / Success / Failure）。Cursor 无法自动读页，**不得**在无用户反馈时断言成功。

## 安全规则

- 只对 **`gds-ticketing-api`** 点 Deploy，除非用户明确要求其他制品。
- 页面分支与请求不一致时暂停，说明实际看到的分支。
- 将 Deploy 视为**有副作用**操作；每次执行前需当次确认，不沿用旧会话的口头许可。
- 分支详情页与 history 页是不同状态；未在详情页实际点击前不要说「已 deploy」。

## 可靠性（全自动场景供 Codex 参考）

若在 Codex Computer Use 中执行，沿用原 skill 校验：

- 点击前记录 `gds-ticketing-api` 最新 history 时间戳（或确认尚无新行）。
- 点击后至少满足其一再报成功：新 history 行且时间更晚、Deploy 按钮变灰/进行中、状态到 Success 或 Failure。
- 仍在 spinning 时说「已提交、处理中」，不说已成功。
- 浏览器切走 tab 后重新打开**精确分支 URL**，不要依赖后退。

## 触发语

- 「用 gds-api-deploy 发布这个分支的 api」
- 「打开 Maven Deploy 链接，deploy gds-ticketing-api」
- 「帮我 deploy develop/base_xxx 的 api」

## 完成汇报

说明分支、制品、用户反馈的可见结果（history 时间戳与状态）。Cursor 半自动流程下注明 Deploy 由用户在本机浏览器完成。
