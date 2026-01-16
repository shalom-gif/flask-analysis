#!/usr/bin/env python
# coding: utf-8
"""
Flask源码下载脚本
"""

import os
import sys
import git
import shutil

# 添加项目根目录到Python路径，这样才能导入config模块
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from config import FLASK_VERSIONS, RAW_DATA_DIR, FLASK_REPO
    print(" 成功导入配置")
except ImportError as e:
    print(f" 导入配置失败: {e}")
    print("使用默认配置...")
    
    # 默认配置
    FLASK_VERSIONS = ["2.0.0", "2.1.0", "2.2.0", "2.3.0", "3.0.0"]
    FLASK_REPO = "https://github.com/pallets/flask.git"
    
    # 设置默认数据目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    RAW_DATA_DIR = os.path.join(project_root, "data", "raw")

def download_flask_versions():
    """下载指定版本的Flask源码"""
    print("开始下载Flask源码...")
    print(f"目标版本: {FLASK_VERSIONS}")
    
    # 确保数据目录存在
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    
    # 主仓库路径
    main_repo_path = os.path.join(RAW_DATA_DIR, "flask_main")
    
    try:
        # 克隆或更新主仓库
        if os.path.exists(main_repo_path):
            print(f"更新仓库: {main_repo_path}")
            repo = git.Repo(main_repo_path)
            repo.git.pull()
        else:
            print(f"克隆仓库: {main_repo_path}")
            repo = git.Repo.clone_from(FLASK_REPO, main_repo_path)
        
        # 获取所有标签
        repo.git.fetch("--tags")
        tags = [tag.name for tag in repo.tags]
        print(f"仓库共有 {len(tags)} 个标签")
        
        # 处理每个目标版本
        for version in FLASK_VERSIONS:
            if version not in tags:
                print(f"警告: 版本 {version} 不存在，跳过")
                continue
                
            # 版本输出目录
            version_dir = os.path.join(RAW_DATA_DIR, "flask_repos", f"flask_{version}")
            
            if os.path.exists(version_dir):
                print(f"版本 {version} 已存在，跳过")
                continue
            
            print(f"处理版本: {version}")
            
            # 检出版本
            repo.git.checkout(f"tags/{version}")
            
            # 创建输出目录
            os.makedirs(version_dir, exist_ok=True)
            
            # 复制所有.py文件
            py_files = []
            for root, dirs, files in os.walk(main_repo_path):
                # 跳过.git目录
                if ".git" in root:
                    continue
                    
                for file in files:
                    if file.endswith(".py"):
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, main_repo_path)
                        dst_path = os.path.join(version_dir, rel_path)
                        
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        py_files.append(rel_path)
            
            print(f"  已复制 {len(py_files)} 个Python文件")
        
        print("下载完成！")
        return True
        
    except Exception as e:
        print(f"下载过程中出错: {e}")
        return False

if __name__ == "__main__":
    download_flask_versions()