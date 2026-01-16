#!/usr/bin/env python
# coding: utf-8
"""
爬取脚本
"""

import os
import sys
import subprocess
import json
import pandas as pd
from datetime import datetime

def main():
    print("数据爬取脚本")
    print("=" * 50)
    
    # 基础配置
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
    PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
    
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"原始数据目录: {RAW_DATA_DIR}")
    print(f"处理数据目录: {PROCESSED_DATA_DIR}")
    
    # 确保目录存在
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    # 1. 提取Git提交历史
    print("\n[1/3] 提取Git提交历史...")
    repo_path = os.path.join(RAW_DATA_DIR, "flask_main")
    
    if os.path.exists(repo_path):
        # 提取最近100条提交
        cmd = ["git", "log", "--pretty=format:%H|%an|%ae|%ad|%s", 
               "--date=format:%Y-%m-%d %H:%M:%S", "--max-count=100"]
        
        try:
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, encoding='utf-8')
            
            commits = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|", 4)
                    if len(parts) == 5:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "email": parts[2],
                            "date": parts[3],
                            "message": parts[4]
                        })
            
            if commits:
                df = pd.DataFrame(commits)
                df['date'] = pd.to_datetime(df['date'])
                
                # 保存
                output_dir = os.path.join(RAW_DATA_DIR, "git_logs_raw")
                os.makedirs(output_dir, exist_ok=True)
                df.to_csv(os.path.join(output_dir, "commits_sample.csv"), index=False, encoding='utf-8')
                
                # 基本统计
                stats = {
                    "total_commits": len(df),
                    "unique_authors": df["author"].nunique(),
                    "date_range": f"{df['date'].min()} 到 {df['date'].max()}",
                    "most_active_author": df["author"].value_counts().idxmax() if len(df) > 0 else "无"
                }
                
                print(f" 提取到 {len(df)} 条提交记录")
                print(f"  作者数量: {stats['unique_authors']}")
                print(f"  最活跃作者: {stats['most_active_author']}")
                
                # 保存统计
                with open(os.path.join(PROCESSED_DATA_DIR, "git_stats.json"), "w", encoding='utf-8') as f:
                    json.dump(stats, f, indent=2, ensure_ascii=False)
            else:
                print(" 未提取到提交记录")
                
        except Exception as e:
            print(f" Git提交历史提取失败: {e}")
    else:
        print(" Flask仓库不存在，跳过Git历史提取")
    
    # 2. 生成版本信息
    print("\n[2/3] 生成版本信息...")
    versions_info = []
    
    for version in ["2.0.0", "2.1.0", "2.2.0", "2.3.0", "3.0.0"]:
        version_dir = os.path.join(RAW_DATA_DIR, "flask_repos", f"flask_{version}")
        
        if os.path.exists(version_dir):
            # 统计Python文件
            py_files = []
            for root, dirs, files in os.walk(version_dir):
                py_files.extend([f for f in files if f.endswith(".py")])
            
            versions_info.append({
                "version": version,
                "python_files": len(py_files),
                "downloaded": True,
                "path": version_dir
            })
            print(f" 版本 {version}: {len(py_files)} 个Python文件")
        else:
            versions_info.append({
                "version": version,
                "python_files": 0,
                "downloaded": False,
                "path": "未下载"
            })
            print(f" 版本 {version}: 未下载")
    
    # 保存版本信息
    with open(os.path.join(PROCESSED_DATA_DIR, "versions_info.json"), "w", encoding='utf-8') as f:
        json.dump(versions_info, f, indent=2, ensure_ascii=False)
    
    # 3. 生成项目报告
    print("\n[3/3] 生成项目报告...")
    report = {
        "project": "Flask开源软件分析",
        "timestamp": datetime.now().isoformat(),
        "data_collection": {
            "git_history": "extracted" if commits else "not_extracted",
            "flask_versions": [v["version"] for v in versions_info if v["downloaded"]],
            "total_python_files": sum(v["python_files"] for v in versions_info)
        },
        "next_steps": ["静态分析", "动态分析", "可视化"]
    }
    
    with open(os.path.join(PROCESSED_DATA_DIR, "project_report.json"), "w", encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f" 项目报告已生成")
    
    print("\n" + "=" * 50)
    print("数据爬取完成！")
    print("=" * 50)
    
    # 显示结果摘要
    print("\n结果摘要:")
    print(f"1. Git提交记录: {len(commits) if 'commits' in locals() else 0} 条")
    print(f"2. Flask版本: {len([v for v in versions_info if v['downloaded']])} 个")
    print(f"3. 总Python文件: {sum(v['python_files'] for v in versions_info)} 个")
    print(f"\n数据位置: {PROCESSED_DATA_DIR}")
    
    return True

if __name__ == "__main__":
    main()