#!/usr/bin/env python
# coding: utf-8
"""
GitHub API数据采集
"""

import requests
import json
import os
import time
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSON = os.path.join(BASE_DIR, '../../data/processed/github_info.json')
OUTPUT_CSV = os.path.join(BASE_DIR, '../../data/processed/github_stats.csv')

GITHUB_TOKEN = ""
REPO_OWNER = "pallets"
REPO_NAME = "flask"

def create_session():
    """创建一个带重试和超时设置的session"""
    session = requests.Session()
    
    # 设置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session

def make_request(url, headers=None):
    """发送请求，跳过SSL验证（仅用于测试环境）"""
    try:
        # 使用session
        session = create_session()
        response = session.get(url, headers=headers, timeout=30, verify=False)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None

def main():
    print("开始采集GitHub数据...")
    
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    # 仓库信息
    repo_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    print(f"请求URL: {repo_url}")
    
    repo_data = make_request(repo_url, headers)
    
    if not repo_data:
        print("获取仓库信息失败，请检查网络连接或SSL设置")
        return
    
    repo_info = {
        "name": repo_data.get("name"),
        "full_name": repo_data.get("full_name"),
        "stars": repo_data.get("stargazers_count", 0),
        "forks": repo_data.get("forks_count", 0),
        "open_issues": repo_data.get("open_issues_count", 0),
        "created_at": repo_data.get("created_at"),
        "updated_at": repo_data.get("updated_at"),
        "language": repo_data.get("language"),
        "size": repo_data.get("size"),
        "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None
    }
    
    print(f"成功获取仓库信息: {repo_info['full_name']}")
    
    # Issues
    issues_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    issues_data = make_request(issues_url, headers)
    issues = []
    if issues_data:
        for issue in issues_data:
            # 跳过pull request（GitHub API中issues和pull request在同一个接口）
            if "pull_request" in issue:
                continue
            issues.append({
                "number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "created_at": issue.get("created_at"),
                "user": issue.get("user", {}).get("login"),
                "comments": issue.get("comments"),
            })
    
    # 保存数据
    all_data = {
        "repo_info": repo_info,
        "issues": issues,
        "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"数据已保存到 {OUTPUT_JSON}")
    print(f"仓库: {repo_info['full_name']}")
    print(f"星标: {repo_info['stars']}")
    print(f"Fork: {repo_info['forks']}")
    print(f"Issues: {repo_info['open_issues']}")
    print(f"获取Issues数: {len(issues)}")

if __name__ == "__main__":
    main()