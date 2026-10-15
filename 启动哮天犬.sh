#!/bin/bash
echo "======================================"
echo "🐕 哮天犬 - 运动防伤AI引擎"
echo "======================================"
echo ""

echo "[1/3] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到Python，请先安装Python 3.8+"
    exit 1
fi
echo "✅ Python环境正常"

echo ""
echo "[2/3] 安装依赖..."
pip3 install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi
echo "✅ 依赖安装完成"

echo ""
echo "[3/3] 启动哮天犬..."
echo ""
echo "🌐 浏览器会自动打开，按 Ctrl+C 停止"
streamlit run app.py
