#!/usr/bin/env python
# coding: utf-8
"""
Flask分析项目 - 环境配置脚本 
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, description):
    """运行命令"""
    print(f"[{description}]")
    print(f"  执行: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ 成功")
            return True
        else:
            print(f"  ✗ 失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ 异常: {e}")
        return False

def main():
    print("=" * 60)
    print("Flask分析项目 - 环境配置")
    print("=" * 60)
    
    # 检查Python
    print(f"\n[1/6] 检查Python环境...")
    print(f"  版本: {sys.version}")
    
    # 升级pip
    run_command("python -m pip install --upgrade pip", "升级pip")
    
    # 创建虚拟环境
    print(f"\n[3/6] 创建虚拟环境...")
    if not os.path.exists("venv"):
        if run_command("python -m venv venv", "创建venv"):
            print("  ✓ 虚拟环境创建成功")
        else:
            print("  ✗ 虚拟环境创建失败")
            return
    else:
        print("  ⚠ 虚拟环境已存在")
    
    # 激活指引
    print(f"\n[4/6] 激活虚拟环境指引...")
    print("  请运行:  “.\\venv\Scripts\Activate.ps1”")

    
    # 创建requirements.txt
    print(f"\n[5/6] 创建依赖文件...")
    requirements = [
        "requests==2.31.0",
        "gitpython==3.1.40", 
        "pandas==2.2.0",
        "numpy==1.26.4",
        "tqdm==4.66.2",
        "libcst==1.1.0"
    ]
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(requirements))
    print("  ✓ 已创建requirements.txt")
    
    # 安装依赖指引
    print(f"\n[6/6] 安装依赖指引...")
    print("  激活虚拟环境后运行: pip install -r requirements.txt")
    
    print(f"\n" + "=" * 60)
    print("环境配置完成！")
    print("=" * 60)
    
    print(f"\n后续步骤:")
    print("1. 激活虚拟环境")
    print("2. 安装依赖: pip install -r requirements.txt")
    print("3. 初始化: python scripts/init_project.py")
    print("4. 下载源码: python scripts/download_flask_versions.py")

if __name__ == "__main__":
    main()