#!/usr/bin/env python
# coding: utf-8
"""
数据预处理 - Flask 2.0.0到3.0.0版本区间分析
"""

import os
import sys
import pandas as pd
import json
from datetime import datetime

# ================================================
# 路径配置
# ================================================

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

try:
    # 将项目根目录添加到 Python 路径
    project_root = os.path.dirname(os.path.dirname(current_dir))
    sys.path.insert(0, project_root)
    
    from config import PROCESSED_DATA_DIR, RAW_DATA_DIR
    print(f"✓ 成功导入配置")
    
except ImportError as e:
    print(f"⚠ 导入配置失败: {e}")
    project_root = os.path.dirname(os.path.dirname(current_dir))
    RAW_DATA_DIR = os.path.join(project_root, "data", "raw")
    PROCESSED_DATA_DIR = os.path.join(project_root, "data", "processed")

# ================================================
# 主函数
# ================================================

def preprocess_data():
    """预处理数据，支持Flask 2.0.0-3.0.0版本区间分析"""
    
    print("\n" + "="*60)
    print("Flask数据预处理工具")
    print("="*60)
    
    # 询问是否分析版本区间
    print("是否分析Flask 2.0.0-3.0.0版本区间? (y/n)")
    analyze_version_range = input().strip().lower() == 'y'
    
    # 1. 首先尝试读取完整的commits_history.csv
    commits_history_path = os.path.join(PROCESSED_DATA_DIR, "commits_history.csv")
    
    if os.path.exists(commits_history_path):
        print(f"✓ 找到完整提交历史文件: {commits_history_path}")
        file_path = commits_history_path
        use_full_history = True
    else:
        # 2. 如果不存在，则读取git_logs_raw目录下的文件
        print(f"⚠ 未找到完整提交历史文件，尝试读取git_logs_raw目录")
        git_logs_dir = os.path.join(RAW_DATA_DIR, "git_logs_raw")
        
        if not os.path.exists(git_logs_dir):
            print("✗ 没有找到提交历史数据目录")
            return None
        
        # 找到提交数据文件
        csv_files = [f for f in os.listdir(git_logs_dir) if f.endswith(".csv") and "commits" in f]
        
        if not csv_files:
            print("✗ 没有找到CSV文件")
            return None
        
        # 使用最新的提交文件
        latest_file = sorted(csv_files)[-1]
        file_path = os.path.join(git_logs_dir, latest_file)
        use_full_history = False
    
    # 读取数据
    print(f"读取文件: {file_path}")
    try:
        df_commits = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"✓ 读取到 {len(df_commits)} 条提交记录")
    except:
        try:
            df_commits = pd.read_csv(file_path, encoding='utf-8')
            print(f"✓ 读取到 {len(df_commits)} 条提交记录")
        except Exception as e:
            print(f"✗ 读取CSV文件失败: {e}")
            return None
    
    # 2. 数据清洗
    print("数据清洗和转换...")
    
    # 重命名列
    column_mapping = {
        'commit_hash': 'hash',
        'hash': 'hash',
        'author': 'author',
        'date': 'date',
        'message': 'message'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df_commits.columns:
            df_commits = df_commits.rename(columns={old_col: new_col})
    
    # 转换日期格式（修复警告）
    try:
        # 添加 utc=True 参数修复警告
        df_commits['date'] = pd.to_datetime(df_commits['date'], errors='coerce', utc=True)
        
        # 如果分析版本区间，则过滤Flask 2.0.0-3.0.0的数据
        if analyze_version_range:
            # Flask 2.0.0发布时间: 2021-05-11, 3.0.0发布时间: 2023-09-30
            start_date = pd.Timestamp('2021-01-01', tz='UTC')  # 包含开发期
            end_date = pd.Timestamp('2023-12-31', tz='UTC')    # 包含发布后期
            
            original_count = len(df_commits)
            df_commits = df_commits[
                (df_commits['date'] >= start_date) & 
                (df_commits['date'] <= end_date)
            ]
            print(f"✓ 版本区间过滤：从 {original_count} 条记录中保留 {len(df_commits)} 条")
        
        # 去除无效日期
        df_commits = df_commits.dropna(subset=['date'])
        print(f"✓ 日期转换成功，最终保留 {len(df_commits)} 条有效记录")
        
    except Exception as e:
        print(f"✗ 日期转换失败: {e}")
        return None
    
    # 3. 基本统计
    print("生成统计信息...")
    
    # 去重
    df_commits = df_commits.drop_duplicates(subset=['hash'], keep='first')
    
    # 计算关键指标
    days_range = (df_commits['date'].max() - df_commits['date'].min()).days
    avg_commits_per_day = len(df_commits) / max(days_range, 1)
    
    # 如果使用完整历史但没有过滤版本区间，显示完整统计
    if use_full_history and not analyze_version_range:
        stats = {
            "data_source": "full_history",
            "total_commits": len(df_commits),
            "total_authors": df_commits["author"].nunique(),
            "date_range": {
                "start": df_commits['date'].min().strftime("%Y-%m-%d %H:%M:%S"),
                "end": df_commits['date'].max().strftime("%Y-%m-%d %H:%M:%S"),
                "days": days_range
            },
            "avg_commits_per_day": round(avg_commits_per_day, 2)
        }
    else:
        stats = {
            "data_source": "version_range" if analyze_version_range else "partial",
            "total_commits": len(df_commits),
            "total_authors": df_commits["author"].nunique(),
            "date_range": {
                "start": df_commits['date'].min().strftime("%Y-%m-%d"),
                "end": df_commits['date'].max().strftime("%Y-%m-%d"),
                "days": days_range
            },
            "avg_commits_per_day": round(avg_commits_per_day, 2)
        }
    
    # 4. 作者统计
    top_authors = df_commits["author"].value_counts().head(5)
    stats["top_5_authors"] = top_authors.to_dict()
    
    # 5. 按月统计
    df_commits['year_month'] = df_commits['date'].dt.strftime('%Y-%m')
    monthly_commits = df_commits.groupby('year_month').size()
    
    if not monthly_commits.empty:
        stats["most_active_month"] = monthly_commits.idxmax()
        stats["max_monthly_commits"] = int(monthly_commits.max())
    
    # 6. 按年统计
    df_commits['year'] = df_commits['date'].dt.year
    yearly_commits = df_commits.groupby('year').size().to_dict()
    stats["yearly_commits"] = yearly_commits
    
    # 7. 保存处理后的数据
    print("保存处理后的数据...")
    output_dir = PROCESSED_DATA_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存统计信息
    stats_file = os.path.join(output_dir, "commit_stats.json")
    with open(stats_file, "w", encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"✓ 统计信息已保存: {stats_file}")
    
    # 保存处理后的CSV
    if analyze_version_range:
        output_csv = "commits_2.0-3.0.csv"
    elif use_full_history:
        output_csv = "commits_full_history.csv"
    else:
        output_csv = "commits_processed.csv"
    
    all_commits_file = os.path.join(output_dir, output_csv)
    df_commits.to_csv(all_commits_file, index=False, encoding='utf-8-sig')
    print(f"✓ 提交记录已保存: {all_commits_file}")
    
    # 8. 打印报告
    print_report(stats, analyze_version_range, use_full_history)
    
    return stats

def print_report(stats, analyze_version_range, use_full_history):
    """打印分析报告"""
    print("\n" + "="*60)
    
    if analyze_version_range:
        print("Flask 2.0.0-3.0.0 版本区间分析结果")
    elif use_full_history:
        print("Flask 完整历史数据分析结果")
    else:
        print("Flask 提交历史分析结果")
    
    print("="*60)
    print(f"总提交数: {stats['total_commits']}")
    print(f"作者数量: {stats['total_authors']}")
    print(f"时间范围: {stats['date_range']['start']} 到 {stats['date_range']['end']}")
    print(f"活跃天数: {stats['date_range']['days']} 天")
    print(f"平均提交频率: {stats['avg_commits_per_day']} 次/天")
    
    if 'most_active_month' in stats:
        print(f"最活跃月份: {stats['most_active_month']} ({stats['max_monthly_commits']} 次提交)")
    
    print(f"\n前5位贡献者:")
    for i, (author, count) in enumerate(stats['top_5_authors'].items(), 1):
        print(f"  {i}. {author}: {count} 次提交")
    
    # 显示年份分布
    if 'yearly_commits' in stats:
        print(f"\n年份分布:")
        for year in sorted(stats['yearly_commits'].keys()):
            count = stats['yearly_commits'][year]
            print(f"  {year}: {count} 次提交")
    
    if analyze_version_range:
        print(f"\n✓ Flask 2.0.0-3.0.0版本区间分析完成!")
    elif use_full_history:
        print(f"\n✓ Flask 完整历史数据分析完成!")
    else:
        print(f"\n✓ Flask 数据分析完成!")

if __name__ == "__main__":
    try:
        result = preprocess_data()
        if result:
            print("\n✓ 数据预处理完成!")
        else:
            print("\n✗ 数据预处理失败!")
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")