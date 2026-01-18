import matplotlib.pyplot as plt
import pandas as pd
import os

# === 1. 设置文件路径 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 这里指向你刚才脚本生成的 csv 文件
CSV_PATH = os.path.join(BASE_DIR, '../../data/processed/commits_history.csv')
SAVE_PATH = os.path.join(BASE_DIR, '../../data/processed/commit_activity.png')

def plot_real_data():
    print(f"[*] 正在读取数据: {CSV_PATH}")
    
    # 检查文件是否存在
    if not os.path.exists(CSV_PATH):
        print("[-] 错误：找不到 commits_history.csv！")
        print("    请先运行 python src/crawler/full_history_extractor.py 来生成数据。")
        return

    try:
        # === 2. 读取 CSV ===
        # encoding='utf-8' 对应 extractor 脚本里的保存格式
        df = pd.read_csv(CSV_PATH, encoding='utf-8')
        
        print(f"[*] 读取成功！共加载 {len(df)} 条提交记录。")
        print("[*] 数据预览:")
        print(df.head(3)) # 打印前3行看看

        # === 3. 数据清洗 ===
        # 确保有 date 列
        if 'date' not in df.columns:
            print("[-] CSV中找不到 'date' 列，请检查提取脚本。")
            return

        # 将字符串格式的日期转换为 datetime 对象
        # errors='coerce' 表示如果遇到乱码日期变成 NaT (空值)，防止报错
        df['date'] = pd.to_datetime(df['date'], utc=True, errors='coerce')
        
        # 去除日期转换失败的坏数据
        df = df.dropna(subset=['date'])

        # === 4. 统计分析 ===
        # 按月统计提交数 ('ME' = Month End)
        monthly_counts = df.resample('ME', on='date').size()

        # === 5. 绘制图表 ===
        plt.figure(figsize=(12, 6))
        
        # 画折线图
        plt.plot(monthly_counts.index, monthly_counts.values, 
                 marker='.', linestyle='-', linewidth=1, color='#007acc', label='Commit Frequency')
        
        # 设置标题和标签
        plt.title(f'Flask Commit History ({len(df)} commits)', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Number of Commits', fontsize=12)
        
        # 添加网格
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        
        # === 6. 保存 ===
        plt.savefig(SAVE_PATH, dpi=150) # dpi=150 让图片更清晰
        print(f"\n[+] 完美！图表已保存到: {SAVE_PATH}")
        print("[+] 任务圆满完成！")

    except Exception as e:
        print(f"[-] 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    plot_real_data()