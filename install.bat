@echo off
chcp 65001 >nul
echo ========================================
echo   Mutao Assistant 依赖安装脚本
echo ========================================
echo.

REM 检查Python环境
echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python。请安装Python 3.9+并确保在PATH中。
    pause
    exit /b 1
)
echo Python环境检查通过。
echo.

REM 检查Node.js环境
echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js。请安装Node.js 18+并确保在PATH中。
    pause
    exit /b 1
)
echo Node.js环境检查通过。
echo.

REM 安装前端依赖
echo ========================================
echo 安装前端依赖...
echo ========================================
echo 当前目录: %cd%
echo.
if exist "node_modules" (
    echo node_modules目录已存在，跳过前端依赖安装。
    echo 如需重新安装，请删除node_modules目录后重新运行此脚本。
) else (
    echo 正在安装前端依赖（npm install）...
    npm install
    if errorlevel 1 (
        echo 错误: 前端依赖安装失败。
        pause
        exit /b 1
    )
    echo 前端依赖安装完成。
)
echo.

REM 安装后端依赖
echo ========================================
echo 安装后端依赖...
echo ========================================
cd /d "%~dp0backend"
echo 切换到后端目录: %cd%
echo.

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo 创建Python虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 虚拟环境创建失败。
        pause
        exit /b 1
    )
    echo 虚拟环境创建完成。
) else (
    echo 虚拟环境已存在，跳过创建。
)

REM 激活虚拟环境并安装依赖
echo.
echo 激活虚拟环境并安装Python依赖...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 警告: 虚拟环境激活失败，尝试使用全局Python环境。
) else (
    echo 虚拟环境已激活。
)

echo.
echo 正在安装Python依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: Python依赖安装失败。
    pause
    exit /b 1
)
echo Python依赖安装完成。
echo.

REM 配置环境文件
echo ========================================
echo 配置环境文件...
echo ========================================
if not exist ".env" (
    echo 复制环境配置文件...
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo 已创建 .env 文件，请编辑该文件并填写您的Gemini API密钥。
    ) else (
        echo 警告: 未找到 .env.example 文件。
    )
) else (
    echo .env 文件已存在，跳过配置。
)
echo.

REM 返回项目根目录
cd /d "%~dp0"
echo 返回项目根目录: %cd%
echo.

echo ========================================
echo   依赖安装完成！
echo ========================================
echo.
echo 前端依赖:
echo   - 位置: node_modules
echo   - 如需重新安装，删除node_modules目录后运行 'npm install'
echo.
echo 后端依赖:
echo   - 虚拟环境: backend\venv
echo   - 激活命令: backend\venv\Scripts\activate.bat
echo   - 环境配置: backend\.env (请编辑并填写Gemini API密钥)
echo.
echo 下一步:
echo   1. 编辑 backend\.env 文件，填入您的Gemini API密钥
echo   2. 运行 start.bat 启动开发服务器
echo.
pause