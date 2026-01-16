#!/usr/bin/env python
# coding: utf-8
"""
GitHub API数据爬取 - 简洁版
约50行代码
"""

import requests
import json
import os
import time
from config import GITHUB_TOKEN, FLASK_REPO_OWNER, FLASK_REPO_NAME, PROCESSED_DATA_DIR

def fetch_github_data():
    """从GitHub API获取数据"""
    print("从GitHub API获取数据...")
    
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    
    # 1. 获取仓库信息
    print("获取仓库信息...")
    url = f"https://api.github.com/repos/{FLASK_REPO_OWNER}/{FLASK_REPO_NAME}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        repo_data = response.json()
        repo_info = {
            "stars": repo_data["stargazers_count"],
            "forks": repo_data["forks_count"],
            "watchers": repo_data["subscribers_count"],
            "open_issues": repo_data["open_issues_count"],
            "created_at": repo_data["created_at"],
            "updated_at": repo_data["updated_at"],
            "language": repo_data["language"],
            "size": repo_data["size"]
        }
        print(f"仓库信息: {repo_info['stars']} stars, {repo_info['forks']} forks")
    else:
        print(f"获取仓库信息失败: {response.status_code}")
        repo_info = {}
    
    # 2. 获取最近的issues
    print("获取最近的issues...")
    url = f"https://api.github.com/repos/{FLASK_REPO_OWNER}/{FLASK_REPO_NAME}/issues"
    params = {"state": "all", "per_page": 50, "sort": "created", "direction": "desc"}
    response = requests.get(url, headers=headers, params=params)
    
    issues = []
    if response.status_code == 200:
        for issue in response.json():
            # 过滤掉pull requests
            if "pull_request" not in issue:
                issues.append({
                    "number": issue["number"],
                    "title": issue["title"],
                    "state": issue["state"],
                    "created_at": issue["created_at"],
                    "updated_at": issue["updated_at"],
                    "user": issue["user"]["login"],
                    "comments": issue["comments"]
                })
        print(f"获取到 {len(issues)} 个issues")
    else:
        print(f"获取issues失败: {response.status_code}")
    
    # 保存数据
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    with open(os.path.join(PROCESSED_DATA_DIR, "repo_info.json"), "w", encoding='utf-8') as f:
        json.dump(repo_info, f, indent=2, ensure_ascii=False)
    
    with open(os.path.join(PROCESSED_DATA_DIR, "issues.json"), "w", encoding='utf-8') as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)
    
    print(f"数据已保存到: {PROCESSED_DATA_DIR}")
    return repo_info, issues

if __name__ == "__main__":
    fetch_github_data()