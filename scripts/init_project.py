#!/usr/bin/env python
# coding: utf-8
"""
项目初始化脚本
"""
import os
import sys
import json

def main():
    print("=" * 60)
    print("Flask分析项目初始化")
    print("=" * 60)
    
    # 检查环境
    print("检查Python环境...")
    print(f"Python版本: {sys.version}")
    # 检查关键包
    required_packages = ['requests', 'pandas', 'numpy']
    print("\n检查依赖包...")
    missing = []
    for pkg in required_packages:
        try:
            __import__(pkg)
            print(f"  {pkg}")
        except ImportError:
            print(f"  {pkg}")
            missing.append(pkg)
    
    if missing:
        print(f"\n缺少包: {', '.join(missing)}")
        print("请运行: pip install " + " ".join(missing))
        return
    
    # 创建目录结构
    print("\n创建目录结构...")
    directories = [
        "data/raw/flask_repos",
        "data/processed",
        "docs",
        "notebooks",
        "src/crawler",
        "src/static_analysis",
        "logs"
    ]
    
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  [+] {dir_path}")
        
        # 为src目录创建__init__.py
        if dir_path.startswith("src/"):
            init_file = os.path.join(dir_path, "__init__.py")
            with open(init_file, "w", encoding="utf-8") as f:
                f.write("# Package initializer\n")
    
    # 创建配置文件
    print("\n创建配置文件...")
    config_content = '''"""
Flask分析项目 - 配置文件
"""

# Flask版本列表
FLASK_VERSIONS = ["2.0.0", "2.1.0", "2.2.0", "2.3.0", "3.0.0"]

# Flask仓库URL
FLASK_REPO = "https://github.com/pallets/flask.git"

# 目录配置
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
SRC_DIR = os.path.join(BASE_DIR, "src")

print(f"项目根目录: {BASE_DIR}")
print(f"数据目录: {DATA_DIR}")
print(f"Flask版本: {FLASK_VERSIONS}")
'''
    
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    print("  [+] config.py")
    
    # 创建.gitignore
    gitignore_content = '''# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
.env
.venv
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Data files
data/raw/
logs/

# Jupyter Notebook
.ipynb_checkpoints/

# OS
.DS_Store
Thumbs.db
'''
    
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    print("  [+] .gitignore")
    
    print("\n" + "=" * 60)
    print("项目初始化完成！")
    print("=" * 60)
    print("\n下一步：测试配置")
    print("运行: python -c \"import config; print('配置加载成功')\"")

if __name__ == "__main__":
    main()
