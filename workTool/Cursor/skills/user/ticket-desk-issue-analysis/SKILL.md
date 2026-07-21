---
name: ticket-desk-issue-analysis
description: "iDev票台需求分析：根据 iDev issue URL 或 issueKey 获取 GDS 票台组的需求详情，自动读取关联飞书文档，提取并总结票台侧的工作内容。支持批量查询票台组待办需求列表。当用户需要了解某个需求票台要做什么、查看票台组待办列表、分析需求工作量时使用。"
---

# ticket-desk-issue-analysis

根据 iDev issue 链接或 issueKey，快速获取 GDS 票台组的需求详情，自动解析关联飞书文档内容，提取票台侧的核心工作项。

## 使用场景

- 用户给出 iDev issue URL 或 issueKey，想了解票台需要做什么
- 查看票台组当前待办/进行中的需求列表
- 分析多个需求的工作内容和优先级
- 了解某个需求的背景、上线时间、影响面

## 输入识别

### 单个需求查询

用户输入以下任一形式：
- iDev URL: `https://idev2.ctripcorp.com/team/10002849/issue/1075?issueKey=GDS-9919`
- 简短 URL: `https://idev2.ctripcorp.com/?GDS-9919`
- issueKey: `GDS-9919`

从输入中提取 issueKey（格式：`GDS-数字`）。

### 批量需求查询

用户说"看看票台待办"、"票台组有哪些需求"等，查询票台组待办列表。

## 执行流程

### Step 1: 获取 issue 基本信息

使用 `iDev2-issue-get` 工具，传入 issueKey：

```
issueKey: "GDS-9919"
```

从返回中提取：
- `title` — 需求标题
- `issuePriority` — 优先级（P0-P5）
- `issueStatus` — 当前状态
- `parentLinkObj.name` — 父需求名称
- `creatorObj` — 创建人
- `executiveObj` — 指派人
- `groupObjList` — 所属组（确认是否属于 GDS-票台）
- `contenttxt` / `content` — 需求描述（通常包含飞书文档链接）
- `customizeFieldList` — 自定义字段（排期优先级、影响面、测试方式、预计提测日期等）

### Step 2: 读取关联飞书文档

从 `contenttxt` 或 `content` 中提取飞书文档链接（格式：`https://trip.larkenterprise.com/wiki/xxxxx`）。

使用 lark-cli 读取文档内容：

```bash
lark-cli docs +fetch --doc "<飞书文档URL>" --doc-format markdown --scope full
```

从返回的 JSON 中提取 `data.document.content` 字段。

### Step 3: 分析并总结票台工作

从文档内容中：
1. 定位票台相关的工作描述（通常在表格的"票台"行，或以"票台"为标题的章节）
2. 提取票台需要做的具体工作项
3. 结合 issue 元数据给出结构化总结

## 批量查询流程

查询票台组待办需求列表时，使用 `iDev2-issue-query` 工具：

```
productIds: [10002849]          # 国际火车GDS 空间
issueStatusCategorys: [1, 2]    # TODO + DOING
issueTypeIds: [4]               # Story
size: 20
includeFields: "title,issuePriority,issueStatus,executiveObj,createtime,groupObjList"
```

返回后过滤 `groupObjList` 中包含 `GDS-票台`（id: 713）的需求。

## 输出格式

### 单个需求输出

```
**GDS-XXXX「需求标题」**

## 基本信息
- 优先级：P0
- 状态：待敏捷排期
- 父需求：xxx
- 创建人：xxx
- 指派人：xxx
- 排期优先级：1
- 影响面：xxx
- 预计提测：xxx

## 票台需要做的事

（从飞书文档中提取的票台工作内容，结构化列出）

## 关键信息

（上线时间要求、依赖项、联调方等）
```

### 批量列表输出

按排期优先级排序，表格展示：

| issueKey | 标题 | 优先级 | 状态 | 指派人 | 排期优先级 |
|----------|------|--------|------|--------|-----------|

## 自定义字段映射

| 字段ID | 字段名 | 用途 |
|--------|--------|------|
| 7114 | 排期优先级 | 数字越小越优先 |
| 7112 | 影响面 | 需求影响范围描述 |
| 7273 | 测试方式 | 纯自测/QA测试 |
| 7123 | 预计提测日期 | 毫秒时间戳 |
| 6997 | 是否重点项目 | 是/否 |
| 6148 | 需求评审 | 通过/未通过 |
| 6996 | 资源投入平台 | TC共用/Trip/Ctrip |

## 注意事项

- issueKey 格式为 `GDS-数字`，空间 ID 为 10002849（国际火车GDS）
- 票台组 ID 为 713，名称为 `GDS-票台`
- 飞书文档可能无法访问（权限问题），此时只展示 issue 元数据中的信息
- 文档中票台工作通常在产品方案表格的"票台"行，或单独的章节中
- 时间戳字段需要转换为可读日期格式展示
