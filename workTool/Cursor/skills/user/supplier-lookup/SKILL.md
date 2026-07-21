---
name: supplier-lookup
description: "供应商负责人查询：根据供应商模块名称（如 treit、renfe、sncf 等）查询对应的负责开发、负责产品、联系邮箱等信息。数据来源于飞书文档「001 供应商系统 - 欧铁产研明细」，已离线保存到本地 JSON 文件，无需每次调用飞书接口。当用户询问某个供应商/模块由谁负责、找谁对接、联系方式是什么时使用。"
---

# supplier-lookup

根据供应商模块名称查询负责开发人员、产品负责人及联系方式。

## 使用场景

- 用户问"treit 谁负责"、"renfe 的开发是谁"、"sncf 找谁"
- 用户问某个供应商的联系邮箱、官网
- 用户想知道某个人负责了哪些供应商

## 数据来源

飞书文档：[001 供应商系统](https://trip.larkenterprise.com/wiki/HzALwZFrRihC4Hk0zWRclddOnje)

数据已离线保存在 `suppliers.json`，包含字段：
- `module`: 供应商模块名称（主要查询键）
- `aliases`: 模块别名
- `business`: 所属业务线（欧铁/亚铁）
- `businessOwner`: 业务负责人
- `developer`: 负责开发
- `product`: 负责产品
- `contactEmail`: 供应商联系邮箱
- `otherContact`: 其他联系方式
- `remark`: 备注
- `website`: 官网

## 查询方式

运行查询脚本，支持模糊匹配。注意必须使用绝对路径（脚本位于用户 home 目录下，不在项目目录内）：

```bash
python3 ~/.kiro/skills/supplier-lookup/search.py <关键词>
```

示例：
```bash
python3 ~/.kiro/skills/supplier-lookup/search.py treit
python3 ~/.kiro/skills/supplier-lookup/search.py 德铁
python3 ~/.kiro/skills/supplier-lookup/search.py 杜子健    # 按开发人员查
```

## 数据更新

如需更新数据，重新从飞书文档读取并覆盖 `suppliers.json` 即可。
