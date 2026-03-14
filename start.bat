@echo off
chcp 65001 >nul
echo ========================================
echo AI小说连载系统
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖
echo 检查依赖...
pip install -r requirements.txt --quiet

REM 检查.env文件
if not exist ".env" (
    echo 创建.env文件...
    copy .env.example .env
    echo 请编辑.env文件配置Ollama连接
    pause
    exit /b
)

REM 运行主程序
echo.
echo 启动系统...
echo.
python main.py

pause
