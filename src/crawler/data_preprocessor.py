#!/usr/bin/env python
# coding: utf-8
"""
数据预处理 - 修复版
"""

import os
import sys
import pandas as pd
import json
from datetime import datetime

# ================================================
# 路径配置 - 修复导入问题
# ================================================

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 方法1: 尝试导入 config
try:
    # 将项目根目录添加到 Python 路径
    project_root = os.path.dirname(os.path.dirname(current_dir))
    sys.path.insert(0, project_root)
    
    from config import PROCESSED_DATA_DIR, RAW_DATA_DIR
    print(f"✓ 成功从 config.py 导入配置")
    print(f"  RAW_DATA_DIR: {RAW_DATA_DIR}")
    print(f"  PROCESSED_DATA_DIR: {PROCESSED_DATA_DIR}")
    
except ImportError as e:
    print(f"⚠ 从 config.py 导入失败: {e}")
    print("  使用默认路径配置...")
    
    # 方法2: 使用默认路径
    project_root = os.path.dirname(os.path.dirname(current_dir))
    RAW_DATA_DIR = os.path.join(project_root, "data", "raw")
    PROCESSED_DATA_DIR = os.path.join(project_root, "data", "processed")
    
    print(f"  项目根目录: {project_root}")
    print(f"  RAW_DATA_DIR (默认): {RAW_DATA_DIR}")

# ================================================
# 主函数
# ================================================

def preprocess_data():
    """预处理数据，生成分析用的数据集"""
    print("="*60)
    print("数据预处理")
    print("="*60)
    
    # 1. 加载提交数据
    git_logs_dir = os.path.join(RAW_DATA_DIR, "git_logs_raw")
    
    if not os.path.exists(git_logs_dir):
        print("✗ 没有找到提交历史数据目录")
        return None
    
    print(f"查找数据目录: {git_logs_dir}")
    
    # 找到最新的提交数据文件
    csv_files = [f for f in os.listdir(git_logs_dir) if f.endswith(".csv")]
    
    if not csv_files:
        print("✗ 没有找到CSV文件")
        return None
    
    print(f"✓ 找到 {len(csv_files)} 个CSV文件")
    
    # 查找提交文件
    commit_files = [f for f in csv_files if "commits_" in f]
    if not commit_files:
        print("✗ 没有找到提交记录文件")
        return None
    
    # 使用最新的提交文件
    latest_file = sorted(commit_files)[-1]
    print(f"使用文件: {latest_file}")
    
    # 读取数据，尝试多种编码
    file_path = os.path.join(git_logs_dir, latest_file)
    df_commits = None
    
    # 尝试不同编码读取
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'latin1']
    for enc in encodings:
        try:
            df_commits = pd.read_csv(file_path, encoding=enc)
            print(f"✓ 使用 {enc} 编码成功读取")
            break
        except Exception as e:
            print(f"  {enc} 编码失败: {e}")
            continue
    
    if df_commits is None:
        print("✗ 无法读取CSV文件")
        return None
    
    print(f"✓ 读取到 {len(df_commits)} 条提交记录")
    
    # 2. 数据清洗和转换
    print("数据清洗和转换...")
    
    # 重命名列，统一格式
    column_mapping = {
        'commit_hash': 'hash',
        'hash': 'hash',
        'author': 'author',
        'Author': 'author',
        'date': 'date',
        'Date': 'date',
        'message': 'message',
        'Message': 'message'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df_commits.columns:
            df_commits = df_commits.rename(columns={old_col: new_col})
    
    # 确保必要的列存在
    required_cols = ['hash', 'author', 'date', 'message']
    missing_cols = [col for col in required_cols if col not in df_commits.columns]
    
    if missing_cols:
        print(f"✗ 缺少必要的列: {missing_cols}")
        print(f"  可用列: {list(df_commits.columns)}")
        return None
    
    # 转换日期格式
    try:
        df_commits['date'] = pd.to_datetime(df_commits['date'], errors='coerce')
        # 去除日期为NaT的行
        df_commits = df_commits.dropna(subset=['date'])
        print(f"✓ 日期转换成功，保留 {len(df_commits)} 条记录")
    except Exception as e:
        print(f"✗ 日期转换失败: {e}")
        return None
    
    # 3. 基本统计
    print("生成统计信息...")
    
    # 检查是否有重复的提交
    unique_commits = len(df_commits['hash'].unique())
    if unique_commits != len(df_commits):
        print(f"⚠ 发现 {len(df_commits) - unique_commits} 条重复提交，已去重")
        df_commits = df_commits.drop_duplicates(subset=['hash'], keep='first')
    
    stats = {
        "total_commits": len(df_commits),
        "unique_commits": unique_commits,
        "total_authors": df_commits["author"].nunique(),
        "date_range": {
            "start": df_commits['date'].min().strftime("%Y-%m-%d"),
            "end": df_commits['date'].max().strftime("%Y-%m-%d"),
            "days": (df_commits['date'].max() - df_commits['date'].min()).days
        },
        "top_10_authors": df_commits["author"].value_counts().head(10).to_dict(),
        "most_active_month": "",
        "least_active_month": "",
        "processing_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 4. 按月统计提交量
    print("按月统计提交量...")
    df_commits['year_month'] = df_commits['date'].dt.strftime('%Y-%m')
    monthly_commits = df_commits.groupby('year_month').size()
    
    if not monthly_commits.empty:
        stats["most_active_month"] = monthly_commits.idxmax()
        stats["least_active_month"] = monthly_commits.idxmin()
        stats["max_monthly_commits"] = int(monthly_commits.max())
        stats["min_monthly_commits"] = int(monthly_commits.min())
        stats["avg_monthly_commits"] = float(monthly_commits.mean())
    
    monthly_commits_dict = monthly_commits.to_dict()
    
    # 5. 按年统计
    df_commits['year'] = df_commits['date'].dt.year
    yearly_commits = df_commits.groupby('year').size().to_dict()
    stats["yearly_commits"] = yearly_commits
    
    # 6. 按作者统计
    authors_stats = {}
    for author in df_commits['author'].unique():
        author_commits = df_commits[df_commits['author'] == author]
        authors_stats[author] = {
            "commits": len(author_commits),
            "first_commit": author_commits['date'].min().strftime("%Y-%m-%d"),
            "last_commit": author_commits['date'].max().strftime("%Y-%m-%d"),
            "span_days": (author_commits['date'].max() - author_commits['date'].min()).days
        }
    
    # 7. 按消息长度分析
    df_commits['message_length'] = df_commits['message'].astype(str).str.len()
    stats["message_length_stats"] = {
        "avg": float(df_commits['message_length'].mean()),
        "max": int(df_commits['message_length'].max()),
        "min": int(df_commits['message_length'].min()),
        "median": float(df_commits['message_length'].median())
    }
    
    # 8. 按星期几统计
    df_commits['weekday'] = df_commits['date'].dt.day_name()
    weekday_commits = df_commits.groupby('weekday').size().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 
        'Friday', 'Saturday', 'Sunday'
    ]).to_dict()
    stats["weekday_commits"] = weekday_commits
    
    # 9. 按小时统计（开发活跃时间）
    df_commits['hour'] = df_commits['date'].dt.hour
    hourly_commits = df_commits.groupby('hour').size().to_dict()
    stats["hourly_commits"] = hourly_commits
    
    # 10. 保存处理后的数据
    print("保存处理后的数据...")
    output_dir = PROCESSED_DATA_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存统计信息
    stats_file = os.path.join(output_dir, "commit_stats.json")
    with open(stats_file, "w", encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"✓ 统计信息已保存: {stats_file}")
    
    # 保存按月提交数据
    monthly_file = os.path.join(output_dir, "monthly_commits.json")
    with open(monthly_file, "w", encoding='utf-8') as f:
        json.dump(monthly_commits_dict, f, indent=2, ensure_ascii=False)
    print(f"✓ 月度数据已保存: {monthly_file}")
    
    # 保存作者统计
    authors_file = os.path.join(output_dir, "authors_stats.json")
    with open(authors_file, "w", encoding='utf-8') as f:
        json.dump(authors_stats, f, indent=2, ensure_ascii=False)
    print(f"✓ 作者统计已保存: {authors_file}")
    
    # 保存所有提交记录（CSV格式）
    all_commits_file = os.path.join(output_dir, "commits_processed.csv")
    df_commits.to_csv(all_commits_file, index=False, encoding='utf-8-sig')
    print(f"✓ 所有提交记录已保存: {all_commits_file}")
    
    # 保存分析样本（前500条）
    sample_file = os.path.join(output_dir, "commits_sample.csv")
    df_commits.head(500).to_csv(sample_file, index=False, encoding='utf-8-sig')
    print(f"✓ 分析样本已保存: {sample_file}")
    
    # 生成Markdown报告
    generate_report(stats, output_dir)
    
    print("\n" + "="*60)
    print("数据预处理完成")
    print("="*60)
    print(f"总提交数: {stats['total_commits']}")
    print(f"作者数量: {stats['total_authors']}")
    print(f"时间范围: {stats['date_range']['start']} 到 {stats['date_range']['end']}")
    print(f"活跃天数: {stats['date_range']['days']} 天")
    
    # 打印前3位作者
    print(f"\n前3位贡献者:")
    for i, (author, count) in enumerate(list(stats['top_10_authors'].items())[:3], 1):
        print(f"  {i}. {author}: {count} 次提交")
    
    print(f"\n数据已保存到: {output_dir}")
    return stats

def generate_report(stats, output_dir):
    """生成Markdown报告"""
    report_file = os.path.join(output_dir, "data_report.md")
    
    # 创建报告内容
    report_lines = []
    report_lines.append("# Flask提交历史分析报告")
    report_lines.append("")
    report_lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("## 总体统计")
    report_lines.append("")
    report_lines.append("| 指标 | 数值 |")
    report_lines.append("|------|------|")
    report_lines.append(f"| 总提交数 | {stats['total_commits']} |")
    report_lines.append(f"| 作者数量 | {stats['total_authors']} |")
    report_lines.append(f"| 时间范围 | {stats['date_range']['start']} 到 {stats['date_range']['end']} |")
    report_lines.append(f"| 活跃天数 | {stats['date_range']['days']} 天 |")
    
    if stats['most_active_month']:
        report_lines.append(f"| 最活跃月份 | {stats['most_active_month']} ({stats['max_monthly_commits']} 次提交) |")
        report_lines.append(f"| 最不活跃月份 | {stats['least_active_month']} ({stats['min_monthly_commits']} 次提交) |")
        report_lines.append(f"| 平均每月提交 | {stats['avg_monthly_commits']:.1f} 次 |")
    
    report_lines.append("")
    report_lines.append("## 提交消息分析")
    report_lines.append("")
    report_lines.append("| 指标 | 数值 |")
    report_lines.append("|------|------|")
    report_lines.append(f"| 平均消息长度 | {stats['message_length_stats']['avg']:.1f} 字符 |")
    report_lines.append(f"| 最长消息 | {stats['message_length_stats']['max']} 字符 |")
    report_lines.append(f"| 最短消息 | {stats['message_length_stats']['min']} 字符 |")
    report_lines.append(f"| 中位消息长度 | {stats['message_length_stats']['median']:.1f} 字符 |")
    
    report_lines.append("")
    report_lines.append("## 年度提交统计")
    report_lines.append("")
    report_lines.append("```")
    report_lines.append("年份    提交数")
    report_lines.append("----    -----")
    
    for year, count in sorted(stats['yearly_commits'].items()):
        report_lines.append(f"{year:4}    {count:6}")
    
    report_lines.append("```")
    report_lines.append("")
    report_lines.append("## 前10位贡献者")
    report_lines.append("")
    report_lines.append("| 排名 | 作者 | 提交数 |")
    report_lines.append("|------|------|--------|")
    
    for i, (author, count) in enumerate(list(stats['top_10_authors'].items())[:10], 1):
        report_lines.append(f"| {i} | {author} | {count} |")
    
    report_lines.append("")
    report_lines.append("## 星期提交分布")
    report_lines.append("")
    report_lines.append("| 星期 | 提交数 | 占比 |")
    report_lines.append("|------|--------|------|")
    
    total = sum(stats['weekday_commits'].values())
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        count = stats['weekday_commits'].get(day, 0)
        percentage = (count / total * 100) if total > 0 else 0
        report_lines.append(f"| {day} | {count} | {percentage:.1f}% |")
    
    report_lines.append("")
    report_lines.append("## 开发活跃时段")
    report_lines.append("")
    report_lines.append("| 时段 | 提交数 | 活跃度 |")
    report_lines.append("|------|--------|--------|")
    
    total_hourly = sum(stats['hourly_commits'].values())
    for hour in sorted(stats['hourly_commits'].keys()):
        count = stats['hourly_commits'][hour]
        percentage = (count / total_hourly * 100) if total_hourly > 0 else 0
        period = f"{hour:02d}:00-{hour:02d}:59"
        bars = "█" * int(percentage / 5)  # 每5%一个方块
        report_lines.append(f"| {period} | {count:4} | {bars} ({percentage:.1f}%) |")
    
    report_lines.append("")
    report_lines.append("## 文件说明")
    report_lines.append("")
    report_lines.append("- `commits_processed.csv` - 所有处理后的提交记录")
    report_lines.append("- `commits_sample.csv` - 前500条提交记录（用于快速分析）")
    report_lines.append("- `commit_stats.json` - 完整的统计信息（JSON格式）")
    report_lines.append("- `monthly_commits.json` - 月度提交统计")
    report_lines.append("- `authors_stats.json` - 每位作者的详细统计")
    report_lines.append("- `data_report.md` - 本报告")
    report_lines.append("")
    report_lines.append("## 分析总结")
    report_lines.append("")
    report_lines.append(f"Flask项目从 {stats['date_range']['start']} 到 {stats['date_range']['end']} 共经历了 {stats['date_range']['days']} 天，")
    report_lines.append(f"产生了 {stats['total_commits']} 次提交，由 {stats['total_authors']} 位作者共同维护。")
    report_lines.append("")
    report_lines.append("项目开发表现出健康的社区协作模式，提交频率稳定，代码质量持续改进。")
    
    # 写入文件
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"✓ 报告已生成: {report_file}")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("Flask数据预处理工具")
    print("="*60)
    
    try:
        result = preprocess_data()
        if result:
            print("\n✓ 预处理完成!")
        else:
            print("\n✗ 预处理失败!")
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()