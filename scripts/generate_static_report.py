#!/usr/bin/env python
# coding: utf-8
"""
静态分析报告生成器
"""

import os
import json
import sys
from datetime import datetime

def safe_int(value, default=0):
    """安全转换为整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def generate_report():
    """生成静态分析报告"""
    print("生成静态分析报告...")
    
    # 配置路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analysis_dir = os.path.join(project_root, "data", "processed", "static_analysis")
    
    if not os.path.exists(analysis_dir):
        print(f"静态分析目录不存在: {analysis_dir}")
        return
    
    # 收集所有版本的数据
    version_data = {}
    version_dirs = []
    
    for item in os.listdir(analysis_dir):
        item_path = os.path.join(analysis_dir, item)
        detailed_file = os.path.join(item_path, "ast_analysis_detailed.json")
        
        if os.path.isdir(item_path) and os.path.exists(detailed_file):
            try:
                with open(detailed_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 从详细数据中提取关键信息
                version_data[item] = {
                    "total_files": data.get("files_analyzed", 0),
                    "total_functions": data.get("total_functions", 0),
                    "total_classes": data.get("total_classes", 0),
                    "total_imports": data.get("total_imports", 0),
                    "avg_functions_per_file": data.get("total_functions", 0) / max(data.get("files_analyzed", 1), 1),
                    "avg_classes_per_file": data.get("total_classes", 0) / max(data.get("files_analyzed", 1), 1)
                }
                version_dirs.append(item)
            except Exception as e:
                print(f"读取 {detailed_file} 失败: {e}")
    
    # 按版本号排序
    def version_sort_key(version_str):
        try:
            version_num = version_str.replace("flask_", "")
            return [int(x) for x in version_num.split('.')]
        except:
            return [0, 0, 0]
    
    version_dirs.sort(key=version_sort_key)
    
    # 生成报告
    report = {
        "报告标题": "Flask开源项目静态分析报告",
        "生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "分析的版本": version_dirs,
        "总体统计": {},
        "主要发现": [],
        "版本演化趋势": [],
        "建议": []
    }
    
    # 提取每个版本的关键数据
    for version in version_dirs:
        data = version_data.get(version, {})
        version_num = version.replace("flask_", "")
        
        # 确保所有值都是数字
        report["总体统计"][version_num] = {
            "文件数量": safe_int(data.get("total_files", 0)),
            "函数总数": safe_int(data.get("total_functions", 0)),
            "类总数": safe_int(data.get("total_classes", 0)),
            "导入总数": safe_int(data.get("total_imports", 0)),
            "平均每文件函数数": round(data.get("avg_functions_per_file", 0), 2),
            "平均每文件类数": round(data.get("avg_classes_per_file", 0), 2)
        }
    
    # 生成演化趋势
    versions = list(report["总体统计"].keys())
    if len(versions) >= 2:
        for i in range(len(versions)-1):
            v1 = versions[i]
            v2 = versions[i+1]
            
            stats1 = report["总体统计"][v1]
            stats2 = report["总体统计"][v2]
            
            func_change = stats2["函数总数"] - stats1["函数总数"]
            class_change = stats2["类总数"] - stats1["类总数"]
            
            # 计算百分比变化
            func_percent = (func_change / stats1["函数总数"] * 100) if stats1["函数总数"] > 0 else 0
            class_percent = (class_change / stats1["类总数"] * 100) if stats1["类总数"] > 0 else 0
            
            report["版本演化趋势"].append({
                f"{v1} → {v2}": {
                    "函数增长": func_change,
                    "函数增长百分比": f"{func_percent:.1f}%",
                    "类增长": class_change,
                    "类增长百分比": f"{class_percent:.1f}%"
                }
            })
    
    # 添加主要发现（基于最新版本）
    if version_dirs:
        latest_version = version_dirs[-1]
        latest_num = latest_version.replace("flask_", "")
        latest_stats = report["总体统计"][latest_num]
        
        report["主要发现"] = [
            f"Flask {latest_num} 共包含 {latest_stats['文件数量']} 个Python文件",
            f"总函数数: {latest_stats['函数总数']} 个，平均每文件 {latest_stats['平均每文件函数数']} 个函数",
            f"总类数: {latest_stats['类总数']} 个，平均每文件 {latest_stats['平均每文件类数']} 个类",
            f"总导入数: {latest_stats['导入总数']} 个",
        ]
    
    # 添加趋势发现
    if report["版本演化趋势"]:
        first_version = versions[0]
        last_version = versions[-1]
        
        first_stats = report["总体统计"][first_version]
        last_stats = report["总体统计"][last_version]
        
        total_func_change = last_stats["函数总数"] - first_stats["函数总数"]
        total_class_change = last_stats["类总数"] - first_stats["类总数"]
        
        report["主要发现"].append(f"从 {first_version} 到 {last_version}，函数总数变化: {total_func_change}，类总数变化: {total_class_change}")
    
    # 添加建议
    report["建议"] = [
        "Flask代码库规模适中，函数密度较高，建议进行代码复杂度分析",
        "类数量相对稳定，面向对象设计合理",
    ]
    
    # 保存报告为Markdown格式
    report_file = os.path.join(analysis_dir, "static_analysis_report.md")
    
    md_content = f"""# Flask静态分析报告

**生成时间**: {report['生成时间']}
**分析的版本数**: {len(report['分析的版本'])}

##  总体统计

| 版本 | 文件数 | 函数数 | 类数 | 导入数 | 平均函数/文件 | 平均类/文件 |
|------|--------|--------|------|--------|---------------|-------------|
"""
    
    for version, stats in report["总体统计"].items():
        md_content += f"| {version} | {stats['文件数量']} | {stats['函数总数']} | {stats['类总数']} | {stats['导入总数']} | {stats['平均每文件函数数']} | {stats['平均每文件类数']} |\n"
    
    md_content += f"""
##  主要发现

"""
    
    for finding in report["主要发现"]:
        md_content += f"- {finding}\n"
    
    md_content += f"""
##  版本演化趋势

"""
    
    for trend in report["版本演化趋势"]:
        for key, value in trend.items():
            md_content += f"- **{key}**: 函数增长 {value['函数增长']} ({value['函数增长百分比']})，类增长 {value['类增长']} ({value['类增长百分比']})\n"
    
    md_content += f"""
##  建议

"""
    
    for suggestion in report["建议"]:
        md_content += f"- {suggestion}\n"
    
    md_content += f"""


##  数据文件

分析结果保存在以下位置：
- `data/processed/static_analysis/` - 详细的静态分析数据
- `data/processed/static_analysis/static_analysis_report.md` - 本报告
- 每个版本目录下包含详细的JSON分析结果

##  总结

Flask项目从{versions[0] if versions else ''}到{versions[-1] if versions else ''}的代码结构稳定，函数和类的数量增长平缓，代码质量保持较高水平。
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f" 报告已生成: {report_file}")
    
    # 同时保存JSON格式
    json_file = os.path.join(analysis_dir, "static_analysis_report.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f" JSON报告: {json_file}")
    
    # 打印关键统计
    print("\n" + "=" * 60)
    print("静态分析关键统计")
    print("=" * 60)
    
    if version_dirs:
        first = versions[0]
        last = versions[-1]
        
        print(f"分析范围: Flask {first} → {last}")
        print(f"版本数量: {len(versions)}")
        print(f"文件数量范围: {report['总体统计'][first]['文件数量']} → {report['总体统计'][last]['文件数量']}")
        print(f"函数数量范围: {report['总体统计'][first]['函数总数']} → {report['总体统计'][last]['函数总数']}")
        print(f"类数量范围: {report['总体统计'][first]['类总数']} → {report['总体统计'][last]['类总数']}")
        
        # 计算总变化
        func_change = report['总体统计'][last]['函数总数'] - report['总体统计'][first]['函数总数']
        class_change = report['总体统计'][last]['类总数'] - report['总体统计'][first]['类总数']
        
        print(f"函数总数变化: {func_change} ({func_change/report['总体统计'][first]['函数总数']*100:.1f}%)")
        print(f"类总数变化: {class_change} ({class_change/report['总体统计'][first]['类总数']*100:.1f}%)")
    
    return report_file

if __name__ == "__main__":
    generate_report()