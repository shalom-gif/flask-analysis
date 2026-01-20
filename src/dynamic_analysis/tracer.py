import pysnooper
from flask import Flask
import os
import datetime

# === 1. 路径逻辑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(BASE_DIR, '../../data/processed/dynamic_trace.log')
LOG_PATH = os.path.normpath(RAW_PATH)

# === 2. 确保文件夹存在 ===
DIR_NAME = os.path.dirname(LOG_PATH)
if not os.path.exists(DIR_NAME):
    os.makedirs(DIR_NAME)


with open(LOG_PATH, 'a', encoding='utf-8') as f:
    f.write(f"\n[Session Restart] {datetime.datetime.now()}\n")

app = Flask(__name__)

print(f"[*] 启动动态分析...")
print(f"[*] 日志路径: {LOG_PATH}")


@app.route('/')                    # <--- 1. 先让 Flask 准备接收路由
@pysnooper.snoop(LOG_PATH, depth=2) # <--- 2. 把它交给 PySnooper 监控
def hello_world():
    print("--- 收到请求，PySnooper 正在记录... ---")
    today = datetime.date.today()
    result = []
    for i in range(3):
        result.append(i * 10)
    return f"Hello! Date: {today}, Calculation: {result}"

if __name__ == '__main__':
    app.run(port=5000, debug=False)