#!/usr/bin/env python
# coding: utf-8
"""
数据预处理 - 简洁版
约40行代码
"""

import os
import pandas as pd
import json
from datetime import datetime
from config import PROCESSED_DATA_DIR, RAW_DATA_DIR

def preprocess_data():
    """预处理数据，生成分析用的数据集"""
    print("预处理数据...")
    
    # 1. 加载提交数据
    git_logs_dir = os.path.join(RAW_DATA_DIR, "git_logs_raw")
    if not os.path.exists(git_logs_dir):
        print("✗ 没有找到提交历史数据")
        return
    
    # 找到最新的提交数据文件
    csv_files = [f for f in os.listdir(git_logs_dir) if f.endswith(".csv")]
    if not csv_files:
        print("✗ 没有找到CSV文件")
        return
    
    latest_date = max([f.split("_")[1].split(".")[0] for f in csv_files if "commits_" in f])
    
    # 读取数据
    df_commits = pd.read_csv(os.path.join(git_logs_dir, f"commits_{latest_date}.csv"))
    df_changes = pd.read_csv(os.path.join(git_logs_dir, f"changes_{latest_date}.csv"))
    
    # 2. 基本统计
    stats = {
        "total_commits": len(df_commits),
        "total_authors": df_commits["author"].nunique(),
        "date_range": f"{df_commits['date'].min()} 到 {df_commits['date'].max()}",
        "top_authors": df_commits["author"].value_counts().head(10).to_dict(),
        "total_file_changes": len(df_changes),
        "avg_additions": df_changes["additions"].mean(),
        "avg_deletions": df_changes["deletions"].mean()
    }
    
    # 3. 按月统计提交量
    df_commits['date'] = pd.to_datetime(df_commits['date'])
    df_commits['year_month'] = df_commits['date'].dt.strftime('%Y-%m')
    monthly_commits = df_commits.groupby('year_month').size().to_dict()
    
    # 4. 保存处理后的数据
    output_dir = PROCESSED_DATA_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存统计信息
    with open(os.path.join(output_dir, "commit_stats.json"), "w", encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # 保存按月提交数据
    with open(os.path.join(output_dir, "monthly_commits.json"), "w", encoding='utf-8') as f:
        json.dump(monthly_commits, f, indent=2, ensure_ascii=False)
    
    # 保存前1000条提交记录（用于分析）
    df_commits.head(1000).to_csv(os.path.join(output_dir, "commits_sample.csv"), index=False, encoding='utf-8')
    
    print(f"数据预处理完成，结果保存在: {output_dir}")
    print(f"统计信息: {stats}")
    return stats

if __name__ == "__main__":
    preprocess_data()