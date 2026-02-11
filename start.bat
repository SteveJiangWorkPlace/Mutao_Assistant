@echo off
chcp 65001 >nul
echo ========================================
echo   Mutao Assistant 开发环境启动脚本
echo ========================================
echo.

REM 检查后端依赖
echo 检查后端Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python。请安装Python 3.9+并确保在PATH中。
    pause
    exit /b 1
)

REM 检查前端依赖
echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js。请安装Node.js 18+并确保在PATH中。
    pause
    exit /b 1
)

echo 环境检查通过。
echo.

REM 检查后端环境配置文件
if not exist "%~dp0backend\.env" (
    echo 警告: 后端环境配置文件 .env 不存在。
    echo 请从 .env.example 复制并填写您的Gemini API密钥。
    echo 命令: copy "%~dp0backend\.env.example" "%~dp0backend\.env"
    echo.
)

REM 提示用户确保依赖已安装
echo 请确保已安装以下依赖：
echo 1. 后端: 在backend目录中运行 'pip install -r requirements.txt'
echo 2. 前端: 在项目根目录中运行 'npm install'
echo.
set /p continue="如果依赖已安装，按回车键继续启动服务，或按Ctrl+C取消..."
echo.

REM 启动后端服务（新窗口）
echo 启动后端开发服务器（端口8001，热重载启用）...
start "Mutao Backend" cmd /k "cd /d %~dp0backend && echo 后端运行目录: %cd% && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat && echo 虚拟环境已激活) else echo 使用全局Python环境) && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001"
timeout /t 2 /nobreak >nul

REM 启动前端服务（新窗口）
echo 启动前端开发服务器（端口5174，热重载启用）...
start "Mutao Frontend" cmd /k "cd /d %~dp0 && echo 前端运行目录: %cd% && npm run dev"

echo.
echo ========================================
echo   服务启动完成！
echo ========================================
echo 后端: http://localhost:8001
echo 前端: http://localhost:5174
echo API健康检查: http://localhost:8001/api/health
echo.
echo 请勿关闭新打开的CMD窗口。
echo 按任意键退出本启动脚本...
pause >nul