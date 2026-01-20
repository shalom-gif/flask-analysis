import os
import subprocess
import csv
import pandas as pd

# === 配置路径 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 临时存放 Flask 官方仓库的位置 (下载到 data/raw/flask_official)
REPO_DIR = os.path.join(BASE_DIR, '../../data/raw/flask_official')
# 结果保存位置
OUTPUT_CSV = os.path.join(BASE_DIR, '../../data/processed/commits_history.csv')

def clone_flask_repo():
    """如果本地没有 Flask 仓库，就从 GitHub 克隆一个下来"""
    if os.path.exists(REPO_DIR):
        print(f"[*] 检测到仓库已存在: {REPO_DIR}")
        return

    print(f"[*] 正在克隆 Flask 官方仓库 (这可能需要几分钟)...")
    try:
        # 使用 git clone 下载
        subprocess.run(['git', 'clone', 'https://github.com/pallets/flask.git', REPO_DIR], check=True)
        print("[+] 克隆完成！")
    except Exception as e:
        print(f"[-] 克隆失败: {e}")
        print("请检查你的网络是否能访问 GitHub，或者是否安装了 Git。")
        exit(1)

def extract_git_log():
    """运行 git log 命令提取所有历史"""
    print("[*] 正在提取提交记录...")
    
    # 定义 git log 的格式：哈希 | 作者 | 时间 | 信息
    # %h = hash, %an = author name, %ad = date, %s = message
    cmd = ['git', 'log', '--pretty=format:%h|%an|%ad|%s', '--date=iso']
    
    try:
        # 在 REPO_DIR 目录下运行 git log
        result = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print("[-] Git 命令运行失败:", result.stderr)
            return

        # 获取输出的文本
        logs = result.stdout.strip().split('\n')
        print(f"[*] 提取成功！共获取到 {len(logs)} 条提交记录。")
        
        return logs
    except Exception as e:
        print(f"[-] 提取过程出错: {e}")
        return []

def save_to_csv(logs):
    """将提取的文本保存为 CSV"""
    print(f"[*] 正在写入 CSV 文件: {OUTPUT_CSV}")
    
    headers = ['commit_hash', 'author', 'date', 'message']
    rows = []
    
    for line in logs:
        try:
            # 按 | 分割 (我们刚才在 git log 里定义的)
            parts = line.split('|')
            if len(parts) >= 4:
                # 重新组合，防止 message 里也有 | 符号
                commit_hash = parts[0]
                author = parts[1]
                date = parts[2]
                message = "|".join(parts[3:]) 
                rows.append([commit_hash, author, date, message])
        except:
            continue
            
    # 使用 pandas 保存，方便处理编码和格式
    df = pd.DataFrame(rows, columns=headers)
    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig') # sig encoding 防止 Excel 打开乱码
    print(f"[+] 完美！文件已保存。")

if __name__ == "__main__":
    # 1. 准备仓库
    clone_flask_repo()
    
    # 2. 提取日志
    logs = extract_git_log()
    
    # 3. 保存结果
    if logs:
        save_to_csv(logs)