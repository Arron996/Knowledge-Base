# MCP 清单

## 两套配置

| 文件 | 角色 |
|------|------|
| `~/.cursor/mcp.json` | **用户级，最全**（Cursor 实际连接多以此为准） |
| `~/IdeaProjects/.mcp.json` | 工作区子集；`AGENTS.md` 列为事实源之一 |

差异：用户级额外包含 `qmq-mcp`、`captain-mcp`、`arex-mcp`、`gds_soa`、`codegraph`。

> 安全：下方只记 URL 主机与用途。token / Private-Token / query `token=` **严禁**写入本库。

## 服务一览

| Server（Cursor 侧常显示为 `user-…`） | 类型 | 用途 |
|--------------------------------------|------|------|
| `bat-mcp-function` | HTTP | CLOG / Trace / 指标 / 告警等 BAT |
| `DOT` | HTTP | SQL / Mongo 查询 |
| `gitlab-mcp` | HTTP | GitLab MR / Issue / Pipeline |
| `feishu-doc-mcp` | HTTP | 飞书文档 CRUD |
| `lark_open_doc_search` | HTTP | 飞书文档搜索 |
| `qconfig-mcp-fws` | HTTP | QConfig 测试环境 |
| `qconfig-mcp-prod` | HTTP | QConfig 生产 |
| `qmq-mcp` | HTTP | QMQ 消息/消费组查询 |
| `feishu2md` | HTTP | 飞书↔Markdown、合约、多维表等 |
| `iDev2` | HTTP | iDev2 建卡/查卡/流转 |
| `gds-order-admin-mcp` | HTTP | 生产订单 Admin（日志/退款等） |
| `gds-order-admin-mcp-fat` | HTTP | FAT 订单 Admin |
| `captain-mcp` | HTTP | Captain 镜像/分组/发布/Pod |
| `arex-mcp` | HTTP | AREX 自动化用例 |
| `gds_soa` | HTTP | GDS 搜方案 / 创单 SOA |
| `codegraph` | stdio `codegraph serve --mcp` | 本地代码知识图谱 |
| `cursor-app-control` | 内置 | `rename_chat`、迁 workspace 等 |

## 按场景选 MCP

| 场景 | 优先 |
|------|------|
| 线上/FAT 订单日志 | `gds-order-admin-mcp` / `-fat`（先定 stage，见 Rule） |
| CLOG / Trace 链接 | `bat-mcp-function` |
| 建 MR / 看 Pipeline | `gitlab-mcp` |
| 建技改卡 | `iDev2` |
| 写飞书方案 | `feishu-doc-mcp`（挂载位置见 `feishu-doc-mount` Rule） |
| 搜飞书 | `lark_open_doc_search` |
| 异常配置 | Admin 相关 + Skill `exception-config-assistant` |
| 发 Q | Skill `fat-qmq-send`；查询可用 `qmq-mcp` |
| UAT/PRO 发布 | `captain-mcp` + Skill `captain-release` |
| AREX 用例 | `arex-mcp`（需 accessToken） |
| 读代码结构 | `codegraph`（有 `.codegraph/` 时优先） |
| FAT 生单 | `gds_soa` + Skill `fat-create-order` |

## 认证备注（不落库）

- 多数内网 HTTP MCP：header `x-bbzai-mcp-token`
- `gitlab-mcp`：另有 `Private-Token`
- `gds_soa`：另有 `Authorization`
- `qconfig-*`：URL query 带 token（勿复制进文档）
- AREX：业务工具需会话 `accessToken`
- 日报 launchd：`CURSOR_API_KEY` 经 `kb-load-secrets.sh` / `~/.zshrc.local` 注入

改 MCP 后：重启 MCP / 重载 Cursor，并视情况同步更新 `IdeaProjects/.mcp.json` 与 `AGENTS.md` 列表。
