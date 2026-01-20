"""
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
