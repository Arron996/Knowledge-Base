# 工作 Dashboard

## 近两周日报

```dataview
TABLE status, file.link AS 日期
FROM "Daily"
SORT file.name DESC
LIMIT 14
```

## 快捷

- 今日笔记：[[Daily/{{date:YYYY-MM-DD}}|打开今日日报]]
- 采集脚本：`.scripts/collect-evening.py`
- 原始数据：`_staging/`
