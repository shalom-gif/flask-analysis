"""
配置文件
"""

GITHUB_TOKEN = ""  

# Flask仓库信息
FLASK_REPO = "https://github.com/pallets/flask.git"
FLASK_REPO_OWNER = "pallets"
FLASK_REPO_NAME = "flask"

# 分析的Flask版本
FLASK_VERSIONS = [
    "2.0.0", "2.1.0", "2.2.0", "2.3.0", "3.0.0"
]

# 目录路径配置
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

# 输出配置
VERBOSE = True

print(f"项目根目录: {PROJECT_ROOT}")
print(f"数据目录: {DATA_DIR}")
print(f"Flask版本: {FLASK_VERSIONS}")

if GITHUB_TOKEN:
    print("GitHub Token: 已配置")
else:
    print("GitHub Token: 未配置（API请求有限制）")