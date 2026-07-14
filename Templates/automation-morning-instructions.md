# 早间待办 Instructions（9:00 纯脚本 + 周五 Weekly）

工作目录：`/Users/aaron/Documents/知识库`

**不调用 SDK**（平日）；周五 Weekly 由 `merge-weekly.py` + `merge-weekly-team.py` 纯 Python 合并。

## 调度

| 时间 | 脚本 | 产出 |
|------|------|------|
| 工作日 09:00 | `morning-todos.sh` | `Daily/{今天}.md` → `## 📋 今日计划` |
| 周五 09:00 | 同上 + `merge-weekly.py` + `merge-weekly-team.py` | `Weekly/YYYY-Www.md` + `Weekly/YYYY-Www-票台周报.md`（Mon–Thu Daily） |

晚间 Daily 由 **19:00** `evening-daily.sh` + SDK Agent 负责，见 [`automation-evening-instructions.md`](automation-evening-instructions.md)。

## 流程

1. `SOURCE=$(python3 .scripts/workday.py --prev 今天)` — **上一工作日**（跨周末/节假日，非日历昨天）
2. `roll-morning-todos.py --from $SOURCE --to 今天`
   - 来源 `## 📋 明日待办` 未勾选项 → 目标 `## 📋 今日计划`
   - 来源 `## 🗂️ 待排期` 未勾选项 → 目标 `## 🗂️ 待排期`（去重合并）
3. **若周五**：
   - `merge-weekly.py --date 今天` — 合并本周 Mon..Thu Daily 技改进展 → 个人周报
   - `merge-weekly-team.py --date 今天` — 票台小组周报草稿（已存在则 skip）
4. `git commit` + `push origin main`

## 上一工作日规则（workday.py）

- 默认 `chinese-calendar` 判断法定假日与调休
- **周一 9:00** → 来源 = **上周五**（非周日）
- **节后首个工作日** → 来源 = 节前最后一个工作日
- **调休周末上班**：launchd 不触发，需手动 `morning-todos.sh`

## 来源 Daily 缺失

若 `Daily/{SOURCE}.md` 不存在（例如节前未跑晚间）：

- 脚本 exit 3 + macOS 通知
- 先补跑：`bash .scripts/evening-daily.sh YYYY-MM-DD`

## 手动补跑

```bash
# 模拟周一（指定今天为 2026-07-06）
TODAY=2026-07-06 SOURCE=$(python3 .scripts/workday.py --prev 2026-07-06)
python3 .scripts/roll-morning-todos.py --from "$SOURCE" --to 2026-07-06

# 周五 Weekly
python3 .scripts/merge-weekly.py --date 2026-07-03
python3 .scripts/merge-weekly-team.py --date 2026-07-03
```

## launchd

```bash
bash .scripts/install-launchd.sh
# 日志：~/Library/Logs/kb-morning.log
```
