@echo off
chcp 65001
echo ======================================
eecho 🐕 哮天犬 - 运动防伤AI引擎
echo ======================================
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo [2/3] 安装依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ❌ 依赖安装失败，请检查pip
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

echo.
echo [3/3] 启动哮天犬...
echo.
echo 🌐 浏览器会自动打开，按 Ctrl+C 停止
streamlit run app.py
pause
