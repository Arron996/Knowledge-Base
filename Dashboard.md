# 工作 Dashboard

## 进度符号速查

| 符号 | 含义 | 典型信号 |
| :--- | :--- | :--- |
| 📐 设计中 | 仅有 Plan / 飞书方案，未写代码 | 今日新建 plan 或飞书 wiki，无 git commit |
| ✏️ 方案校订中 | 改 Plan / 飞书 doc，仍无代码 | plan mtime 今日；飞书 doc 编辑（非仅创建） |
| 🔍 调研中 | 排查、读需求、方案对比 | Cursor 会话以排查/读 doc 为主 |
| 🔄 处理中 | 开发进行中 | iDev 开发中；可附「下周一发生产」 |
| 🧪 测试中 | 已开发，在测分或灰度 | MR/merge 进 **develop/base*** |
| ⏳ 待发生产 | 开发完，等合主分支 | 测分通过、尚未 merge main/master |
| ⏳ 问题待解决 | 阻塞 | 会话/备注中有 blocker |
| ✅ 已发布 | **已合 main/master = 已发生产** | GitLab MR 合入主分支 |
| ✅ 已下线 | 下线类技改完成 | 与用户周报「已下线」一致 |

**Callout 配色**：`[!success]-` 已发布 · `[!example]-` 测试/灰度 · `[!note]-` 处理中 · `[!abstract]-` 设计/调研 · `[!warning]-` 阻塞

**待办分栏**：`📋 今日计划` = 9:00 滚入 · `📋 明日待办` = 19:00 晚间填写 · `🗂️ 待排期` = 未排期（🔵）

排版规范见 [[Templates/daily-style-guide|daily-style-guide]]。Obsidian 外观 → CSS 片段 → 启用 `daily-report`。

## 自动化调度

| 时间 | 脚本 | 说明 |
|------|------|------|
| 工作日 **19:00** | `.scripts/evening-daily.sh` | SDK Agent 写**当天** Daily |
| 工作日 **09:00** | `.scripts/morning-todos.sh` | 滚**今日计划**；周五 + Weekly |
| 安装 launchd | `.scripts/install-launchd.sh` | 需 `CURSOR_API_KEY` in `~/.zshrc.local` |
| 首次依赖 | `.scripts/setup.sh` | `chinese-calendar` + `@cursor/sdk` |

日志：`~/Library/Logs/kb-evening.log`、`kb-morning.log`

## 近两周日报

```dataview
TABLE weekday AS 星期, status AS 状态
FROM "Daily"
SORT file.name DESC
LIMIT 14
```

## 快捷

- 今日笔记：[[Daily/{{date:YYYY-MM-DD}}|打开今日日报]]
- 采集脚本：`.scripts/collect-evening.py`、`.scripts/collect-feishu.py`
- 晚间 Automation：[[Templates/automation-evening-instructions|automation-evening-instructions]]
- 早间 Automation：[[Templates/automation-morning-instructions|automation-morning-instructions]]
- 参考区生成：`.scripts/format-daily-ref.py --date YYYY-MM-DD`
- 原始数据：`_staging/`
- 技改映射：[[Templates/topic-registry|topic-registry.yaml]]

### 手动补跑

```bash
# 晚间 Daily
bash /Users/aaron/Documents/知识库/.scripts/evening-daily.sh 2026-07-02

# 早间待办（跨周末自动取上一工作日）
bash /Users/aaron/Documents/知识库/.scripts/morning-todos.sh

# 仅滚待办
SOURCE=$(python3 /Users/aaron/Documents/知识库/.scripts/workday.py --prev 2026-07-06)
python3 /Users/aaron/Documents/知识库/.scripts/roll-morning-todos.py --from "$SOURCE" --to 2026-07-06
```
