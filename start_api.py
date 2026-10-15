"""
哮天犬API服务启动脚本

运行后：
- API地址: http://localhost:8000
- 接口文档: http://localhost:8000/docs
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("🐕 哮天犬 AI 服务启动中...")
    print("=" * 50)
    print("")
    print("📖 API 文档: http://localhost:8000/docs")
    print("🏠 首页: http://localhost:8000/")
    print("")
    print("按 Ctrl+C 停止")
    print("-" * 50)
    
    uvicorn.run(
        "xtq.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
