@echo off
chcp 65001 >nul
echo ========================================
echo AI小说连载系统 - 环境配置
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 创建虚拟环境...
if not exist "venv\" (
    python -m venv venv
    echo 虚拟环境创建完成
) else (
    echo 虚拟环境已存在
)

echo.
echo [2/4] 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo [3/4] 安装Python依赖...
pip install -r requirements.txt

echo.
echo [4/4] 检查Ollama连接...
python -c "from utils import get_client; client = get_client(); print('Ollama连接成功' if client.check_connection() else 'Ollama连接失败，请确保Ollama已启动')"

echo.
echo ========================================
echo 配置完成！
echo ========================================
echo.
echo 下一步：
echo 1. 确保Ollama已安装并运行
echo 2. 下载模型: ollama pull qwen3:30b
echo 3. 编辑 .env 文件（如果不存在会自动创建）
echo 4. 运行 start.bat 启动系统
echo.
pause
