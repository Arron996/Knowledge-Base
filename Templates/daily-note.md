---
date: {{date:YYYY-MM-DD}}
tags: [daily]
weekday: {{date:dddd}}
status: open
cssclasses:
  - daily-report
---

# 📅 {{date:YYYY-MM-DD}} · {{date:dddd}}

> [!abstract] 今日主线
> <!-- agent:headline -->

## 📊 技改进展

<!-- 每个技改：> [!type]- 标题 + 块内 2 列表，见 Templates/daily-style-guide.md -->
<!-- 轻工作日：Plan/飞书 校订 → ✏️ 方案校订中；无 git/iDev 也须写本节 -->

> [!note]- <!-- agent:topic-1-title -->
>
> | 子项 | 进度 |
> | :--- | ---: |
> | <!-- agent:topic-1-rows --> | |

## 📋 今日计划

<!-- 9:00 从上一工作日「明日待办」滚入；🔴🟡🟢 优先级 -->

- [ ] <!-- agent:today -->

## 📋 明日待办

- [ ] <!-- agent:tomorrow -->

## 🗂️ 待排期

<!-- 未排期、有空再做；🔵 无日期压力。排查后续 / 评估类放这里，勿默认塞进明日待办 -->

- [ ] <!-- agent:backlog -->

## 📎 参考（工程明细，默认折叠）

<!-- 数据源：_staging/{{date:YYYY-MM-DD}}.raw.json + .idev2.json + .feishu.json -->
<!-- 飞书参考区须区分 createdToday / editedTodayOnly -->

<details>
<summary>📎 原始采集</summary>

<!-- collector:auto -->

</details>
