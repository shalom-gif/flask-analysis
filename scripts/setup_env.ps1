<#
Flask分析项目 - 虚拟环境设置脚本
在Windows PowerShell中右键选择"使用PowerShell运行"
#>

Write-Host "=========================================" -ForegroundColor Green
Write-Host "Flask分析项目 - 环境配置脚本" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# 检查Python是否安装
Write-Host "`n[1/6] 检查Python环境..." -ForegroundColor Cyan
$pythonVersion = python --version 2>$null
if ($pythonVersion -match "Python 3\.([7-9]|1[0-9])") {
    Write-Host "  ✓ Python版本: $pythonVersion" -ForegroundColor Green
} elseif ($pythonVersion) {
    Write-Host "  ⚠ Python版本: $pythonVersion (建议使用Python 3.7+)" -ForegroundColor Yellow
} else {
    Write-Host "  ✗ 未找到Python，请先安装Python 3.7+" -ForegroundColor Red
    Write-Host "    下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# 升级pip
Write-Host "`n[2/6] 升级pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip --no-warn-script-location

# 创建虚拟环境
Write-Host "`n[3/6] 创建虚拟环境..." -ForegroundColor Cyan
if (-not (Test-Path "venv")) {
    python -m venv venv
    if (Test-Path "venv") {
        Write-Host "  ✓ 虚拟环境创建成功: venv/" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 虚拟环境创建失败" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ℹ 虚拟环境已存在，跳过创建" -ForegroundColor Blue
}

# 激活虚拟环境
Write-Host "`n[4/6] 激活虚拟环境..." -ForegroundColor Cyan
if (Test-Path "venv\Scripts\Activate.ps1") {
    try {
        & .\venv\Scripts\Activate.ps1
        Write-Host "  ✓ 虚拟环境已激活" -ForegroundColor Green
        $pythonPath = (Get-Command python).Source
        Write-Host "  当前Python路径: $pythonPath" -ForegroundColor Cyan
        
        # 检查是否真的激活
        if ($pythonPath -like "*venv*") {
            Write-Host "  ✓ 确认在虚拟环境中" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ 警告：可能未成功激活虚拟环境" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ✗ 激活失败: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  ✗ 找不到激活脚本" -ForegroundColor Red
}

# 修复requirements.txt编码问题
Write-Host "`n[5/6] 修复文件编码..." -ForegroundColor Cyan
$requirementsPath = "requirements.txt"
if (Test-Path $requirementsPath) {
    # 读取文件内容（使用UTF-8）
    $content = Get-Content $requirementsPath -Encoding UTF8 -Raw
    # 重新保存为UTF-8 with BOM（Windows兼容）
    $content | Out-File -FilePath $requirementsPath -Encoding UTF8
    Write-Host "  ✓ 修复requirements.txt编码" -ForegroundColor Green
} else {
    Write-Host "  ⚠ requirements.txt不存在" -ForegroundColor Yellow
}

# 安装依赖的指引
Write-Host "`n[6/6] 安装项目依赖..." -ForegroundColor Cyan

# 先安装几个核心包
Write-Host "  安装核心依赖..." -ForegroundColor Blue
$corePackages = @("requests", "gitpython", "pandas", "numpy", "tqdm")
foreach ($pkg in $corePackages) {
    try {
        pip install $pkg --no-warn-script-location
        Write-Host "    ✓ $pkg" -ForegroundColor Green
    } catch {
        Write-Host "    ✗ $pkg 安装失败" -ForegroundColor Red
    }
}

Write-Host "`n核心依赖安装完成！" -ForegroundColor Green
Write-Host "如需安装完整依赖，请运行:" -ForegroundColor Yellow
Write-Host "  pip install -r requirements.txt" -ForegroundColor White -BackgroundColor DarkGray

Write-Host "`n=========================================" -ForegroundColor Green
Write-Host "环境配置完成！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

Write-Host "`n后续步骤：" -ForegroundColor Cyan
Write-Host "1. 初始化项目: python scripts\init_project.py" -ForegroundColor Yellow
Write-Host "2. 安装剩余依赖（可选）: pip install -r requirements.txt" -ForegroundColor Yellow
Write-Host "3. 下载Flask源码: python scripts\download_flask_versions.py" -ForegroundColor Yellow

# 检查当前环境
Write-Host "`n当前环境信息：" -ForegroundColor Cyan
Write-Host "  Python版本: $(python --version)" -ForegroundColor White
Write-Host "  PIP版本: $(pip --version)" -ForegroundColor White