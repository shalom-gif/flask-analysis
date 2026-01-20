#!/usr/bin/env python
# coding: utf-8
"""
运行静态分析的主脚本
"""

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "src"))

def main():
    print("=" * 60)
    print("Flask静态分析工具")
    print("=" * 60)
    
    # 配置路径
    try:
        import config
        RAW_DATA_DIR = config.RAW_DATA_DIR
        PROCESSED_DATA_DIR = config.PROCESSED_DATA_DIR
    except ImportError:
        RAW_DATA_DIR = os.path.join(project_root, "data", "raw")
        PROCESSED_DATA_DIR = os.path.join(project_root, "data", "processed")
    
    repos_dir = os.path.join(RAW_DATA_DIR, "flask_repos")
    output_dir = os.path.join(PROCESSED_DATA_DIR, "static_analysis")
    
    if not os.path.exists(repos_dir):
        print(f"Flask源码目录不存在: {repos_dir}")
        print("请先运行: python scripts/download_flask_versions.py")
        return
    
    print(f"源码目录: {repos_dir}")
    print(f"输出目录: {output_dir}")
    
    # 1. 使用AST分析
    print("\n[1/3] 使用AST分析代码结构...")
    try:
        from static_analysis.ast_analyzer import analyze_flask_version
        
        version_dirs = [d for d in os.listdir(repos_dir) 
                       if os.path.isdir(os.path.join(repos_dir, d))]
        
        results = {}
        for version_dir in version_dirs:
            if version_dir.startswith("flask_"):
                full_path = os.path.join(repos_dir, version_dir)
                summary = analyze_flask_version(full_path, output_dir)
                results[version_dir] = summary
        
        print(f" 完成了 {len(results)} 个版本的AST分析")
    except Exception as e:
        print(f" AST分析失败: {e}")
    
    # 2. 使用LibCST分析（示例）
    print("\n[2/3] 使用LibCST分析代码模式...")
    try:
        from static_analysis.libcst_modifier import analyze_with_libcst
        
        # 只分析最新版本作为示例
        latest_version = sorted([d for d in os.listdir(repos_dir) 
                                if d.startswith("flask_")])[-1]
        latest_path = os.path.join(repos_dir, latest_version)
        libcst_output = os.path.join(output_dir, "libcst_analysis.json")
        
        patterns = analyze_with_libcst(latest_path, libcst_output)
        print(f" LibCST分析完成: {patterns.get('total_files', 0)} 个文件")
    except Exception as e:
        print(f" LibCST分析失败: {e}")
    
    # 3. 生成版本演化报告
    print("\n[3/3] 生成版本演化报告...")
    try:
        from static_analysis.version_diff import generate_evolution_report
        
        evolution_report = os.path.join(output_dir, "evolution_report.json")
        report = generate_evolution_report(output_dir, evolution_report)
        
        print(" 版本演化报告生成完成")
        if report.get("summary"):
            changes = report["summary"].get("changes", {})
            for key, change in changes.items():
                print(f"  {key}: {change.get('from')} → {change.get('to')} ({change.get('percent')})")
    except Exception as e:
        print(f" 演化报告生成失败: {e}")
    
    print("\n" + "=" * 60)
    print("静态分析完成！")
    print("=" * 60)
    
    # 显示结果位置
    print(f"\n分析结果保存在: {output_dir}")
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        print(f"生成的文件:")
        for file in files:
            print(f"  - {file}")
    
    return True

if __name__ == "__main__":
    main()