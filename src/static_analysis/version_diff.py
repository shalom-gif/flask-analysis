#!/usr/bin/env python
# coding: utf-8
"""
版本差异分析工具
"""

import os
import json
from collections import defaultdict

def compare_versions(version1_stats, version2_stats, version1_name, version2_name):
    """比较两个版本的统计信息"""
    comparison = {
        "version1": version1_name,
        "version2": version2_name,
        "comparison": {}
    }
    
    # 比较基础统计
    metrics = ["total_files", "total_functions", "total_classes", "total_imports"]
    for metric in metrics:
        v1 = version1_stats.get(metric, 0)
        v2 = version2_stats.get(metric, 0)
        diff = v2 - v1
        percent = (diff / v1 * 100) if v1 > 0 else 0
        
        comparison["comparison"][metric] = {
            "v1": v1,
            "v2": v2,
            "diff": diff,
            "percent_change": f"{percent:.1f}%"
        }
    
    # 比较函数密度
    v1_density = version1_stats.get("avg_functions_per_file", 0)
    v2_density = version2_stats.get("avg_functions_per_file", 0)
    comparison["comparison"]["function_density"] = {
        "v1": f"{v1_density:.2f}",
        "v2": f"{v2_density:.2f}",
        "change": f"{v2_density - v1_density:.2f}"
    }
    
    return comparison

def analyze_version_evolution(analysis_dir):
    """分析版本演化趋势"""
    print("分析版本演化趋势...")
    
    # 查找所有版本的分析结果
    version_summaries = {}
    version_dirs = []
    
    for item in os.listdir(analysis_dir):
        item_path = os.path.join(analysis_dir, item)
        summary_file = os.path.join(item_path, "ast_analysis_summary.json")
        
        if os.path.isdir(item_path) and os.path.exists(summary_file):
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary = json.load(f)
                version_summaries[item] = summary
                version_dirs.append(item)
            except Exception as e:
                print(f"读取 {summary_file} 失败: {e}")
    
    # 按版本号排序
    version_dirs.sort(key=lambda x: [int(v) if v.isdigit() else v for v in x.split('_')[1].split('.')])
    
    # 生成演化报告
    evolution = {
        "versions": version_dirs,
        "trends": {}
    }
    
    # 收集趋势数据
    metrics = ["total_functions", "total_classes", "total_imports"]
    for metric in metrics:
        evolution["trends"][metric] = []
        for version in version_dirs:
            summary = version_summaries.get(version, {})
            # 这里需要从详细统计中获取，简化处理
            evolution["trends"][metric].append(summary.get(metric, 0))
    
    # 生成版本间比较
    comparisons = []
    for i in range(len(version_dirs) - 1):
        v1 = version_dirs[i]
        v2 = version_dirs[i + 1]
        
        # 简化比较：统计函数和类的数量变化
        v1_funcs = version_summaries.get(v1, {}).get("total_functions", 0)
        v2_funcs = version_summaries.get(v2, {}).get("total_functions", 0)
        
        v1_classes = version_summaries.get(v1, {}).get("total_classes", 0)
        v2_classes = version_summaries.get(v2, {}).get("total_classes", 0)
        
        comparisons.append({
            "from": v1,
            "to": v2,
            "function_growth": v2_funcs - v1_funcs,
            "class_growth": v2_classes - v1_classes,
            "function_growth_percent": ((v2_funcs - v1_funcs) / v1_funcs * 100) if v1_funcs > 0 else 0
        })
    
    evolution["comparisons"] = comparisons
    
    return evolution

def generate_evolution_report(analysis_dir, output_file):
    """生成版本演化报告"""
    print("生成版本演化报告...")
    
    # 读取所有版本的AST分析摘要
    version_data = {}
    
    for version_dir in os.listdir(analysis_dir):
        version_path = os.path.join(analysis_dir, version_dir)
        if os.path.isdir(version_path):
            summary_file = os.path.join(version_path, "ast_analysis_summary.json")
            if os.path.exists(summary_file):
                try:
                    with open(summary_file, 'r', encoding='utf-8') as f:
                        version_data[version_dir] = json.load(f)
                except:
                    pass
    
    # 生成报告
    report = {
        "versions_analyzed": list(version_data.keys()),
        "summary": {},
        "recommendations": []
    }
    
    # 分析趋势
    if len(version_data) >= 2:
        versions = sorted(version_data.keys())
        first_version = versions[0]
        last_version = versions[-1]
        
        first_stats = version_data[first_version]
        last_stats = version_data[last_version]
        
        # 计算变化
        changes = {}
        for key in ["total_functions", "total_classes"]:
            if key in first_stats and key in last_stats:
                change = last_stats[key] - first_stats[key]
                percent = (change / first_stats[key] * 100) if first_stats[key] > 0 else 0
                changes[key] = {
                    "from": first_stats[key],
                    "to": last_stats[key],
                    "change": change,
                    "percent": f"{percent:.1f}%"
                }
        
        report["summary"] = {
            "first_version": first_version,
            "last_version": last_version,
            "changes": changes
        }
        
        # 生成建议
        if changes.get("total_functions", {}).get("change", 0) > 50:
            report["recommendations"].append("函数数量显著增加，代码复杂度可能增加")
        if changes.get("total_classes", {}).get("change", 0) > 10:
            report["recommendations"].append("类数量增加，面向对象设计可能更加丰富")
    
    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"演化报告已生成: {output_file}")
    return report