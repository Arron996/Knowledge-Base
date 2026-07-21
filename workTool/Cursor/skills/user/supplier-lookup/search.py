#!/usr/bin/env python3
"""供应商负责人查询脚本 - 支持按模块名、别名、开发人员、备注等模糊匹配"""

import json
import sys
import os


def load_suppliers():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, "suppliers.json")
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)


def match_supplier(supplier, keyword):
    """检查供应商是否匹配关键词（不区分大小写）"""
    kw = keyword.lower()

    # 匹配 module
    if kw in supplier.get("module", "").lower():
        return True

    # 匹配 aliases
    for alias in supplier.get("aliases", []):
        if kw in alias.lower():
            return True

    # 匹配开发人员
    if kw in supplier.get("developer", "").lower():
        return True

    # 匹配产品人员
    if kw in supplier.get("product", "").lower():
        return True

    # 匹配业务线
    if kw in supplier.get("business", "").lower():
        return True

    # 匹配备注
    if kw in supplier.get("remark", "").lower():
        return True

    # 匹配业务负责人
    if kw in supplier.get("businessOwner", "").lower():
        return True

    return False


def format_supplier(s):
    """格式化单个供应商信息"""
    lines = []
    lines.append(f"  模块: {s.get('module', '-')}")
    if s.get("aliases"):
        lines.append(f"  别名: {', '.join(s['aliases'])}")
    lines.append(f"  业务线: {s.get('business', '-')} ({s.get('businessOwner', '-')})")
    lines.append(f"  负责开发: {s.get('developer', '-')}")
    lines.append(f"  负责产品: {s.get('product', '-')}")
    if s.get("contactEmail"):
        lines.append(f"  联系邮箱: {s['contactEmail']}")
    if s.get("otherContact"):
        lines.append(f"  其他联系: {s['otherContact']}")
    if s.get("remark"):
        lines.append(f"  备注: {s['remark']}")
    if s.get("website"):
        lines.append(f"  官网: {s['website']}")
    return "\n".join(lines)


def search(keyword):
    suppliers = load_suppliers()
    results = [s for s in suppliers if match_supplier(s, keyword)]

    if not results:
        print(f"未找到与 \"{keyword}\" 相关的供应商信息。")
        return

    print(f"找到 {len(results)} 条匹配结果：\n")
    for i, s in enumerate(results, 1):
        print(f"[{i}] {s.get('module', '未知')}")
        print(format_supplier(s))
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 search.py <关键词>")
        print("示例: python3 search.py treit")
        print("      python3 search.py 杜子健")
        print("      python3 search.py 德铁")
        sys.exit(1)

    keyword = " ".join(sys.argv[1:])
    search(keyword)
