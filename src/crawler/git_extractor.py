#!/usr/bin/env python
# coding: utf-8
"""
Git提交历史提取
"""

import os
import subprocess
import pandas as pd
from datetime import datetime
from config import RAW_DATA_DIR

def extract_git_history():
    """提取Flask仓库的Git提交历史"""
    print("提取Git提交历史...")
    
    # Flask主仓库路径
    repo_path = os.path.join(RAW_DATA_DIR, "flask_main")
    
    if not os.path.exists(repo_path):
        print(f" 仓库不存在: {repo_path}")
        return None
    
    # 1. 提取提交日志
    print("提取提交日志...")
    cmd = ["git", "log", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=format:%Y-%m-%d %H:%M:%S"]
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
    
    # 转换为DataFrame
    df_commits = pd.DataFrame(commits)
    df_commits['date'] = pd.to_datetime(df_commits['date'])
    
    print(f"提取到 {len(df_commits)} 条提交记录")
    
    # 2. 提取文件变更统计（最近500次提交）
    print("提取文件变更统计...")
    cmd = ["git", "log", "--pretty=format:%H", "--max-count=500", "--numstat"]
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    
    changes = []
    current_commit = None
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        if len(line) == 40 and " " not in line:  # 提交哈希
            current_commit = line
        elif current_commit and "\t" in line:  # 文件变更
            parts = line.split("\t")
            if len(parts) == 3:
                changes.append({
                    "commit": current_commit,
                    "additions": int(parts[0]) if parts[0].isdigit() else 0,
                    "deletions": int(parts[1]) if parts[1].isdigit() else 0,
                    "filename": parts[2]
                })
    
    df_changes = pd.DataFrame(changes)
    print(f"提取到 {len(df_changes)} 条文件变更记录")
    
    # 3. 提取标签信息
    print("提取标签信息...")
    cmd = ["git", "tag", "-l", "--sort=v:refname"]
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    
    tags = []
    for tag in result.stdout.strip().split("\n"):
        if tag:
            cmd_date = ["git", "log", "-1", "--format=%ad", "--date=short", tag]
            result_date = subprocess.run(cmd_date, cwd=repo_path, capture_output=True, text=True)
            tags.append({
                "tag": tag,
                "date": result_date.stdout.strip()
            })
    
    df_tags = pd.DataFrame(tags)
    print(f"提取到 {len(df_tags)} 个标签")
    
    # 保存数据
    timestamp = datetime.now().strftime("%Y%m%d")
    output_dir = os.path.join(RAW_DATA_DIR, "git_logs_raw")
    os.makedirs(output_dir, exist_ok=True)
    
    df_commits.to_csv(os.path.join(output_dir, f"commits_{timestamp}.csv"), index=False, encoding='utf-8')
    df_changes.to_csv(os.path.join(output_dir, f"changes_{timestamp}.csv"), index=False, encoding='utf-8')
    df_tags.to_csv(os.path.join(output_dir, f"tags_{timestamp}.csv"), index=False, encoding='utf-8')
    
    print(f"数据已保存到: {output_dir}")
    return df_commits, df_changes, df_tags

if __name__ == "__main__":
    extract_git_history()