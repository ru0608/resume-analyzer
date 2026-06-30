@echo off
echo ================================================
echo   📄 智能简历分析系统 - 启动器
echo ================================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请安装 Python 3.10+
    pause
    exit /b
)

:: 检查 Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请安装 Node 18+
    pause
    exit /b
)

echo [1/2] 启动后端服务 (http://localhost:8000)
echo         API 文档: http://localhost:8000/docs
start "Backend" cmd /c "cd /d "%~dp0backend" && uvicorn app:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 >nul

echo [2/2] 启动前端页面 (http://localhost:5173)
echo         自动打开浏览器...
start "Frontend" cmd /c "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ✅ 启动完成！
echo.
echo    后端: http://localhost:8000
echo    前端: http://localhost:5173
echo    接口文档: http://localhost:8000/docs
echo.
echo 按任意键停止服务...
pause >nul

echo 正在关闭服务...
taskkill /f /fi "WINDOWTITLE eq Backend" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Frontend" >nul 2>&1
echo 已停止。
