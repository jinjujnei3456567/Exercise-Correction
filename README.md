# 哮天犬 (XiaoTianQuan / XTQ)

> 🐕 你的数字关节保镖 —— 运动防伤AI引擎

既是独立AI产品，也可以作为API服务被其他项目调用。

## 双重身份

### 1. 独立AI产品
像豆包、DeepSeek一样，有自己的界面和对话能力，直接用。

### 2. API服务提供商
你的项目可以调用哮天犬的API，传入动作数据，返回风险评估和AI建议。

## 快速开始

### 启动Web界面版
```bash
streamlit run app.py
```

### 启动API服务版
```bash
python start_api.py
```
然后访问 http://localhost:8000/docs 看API文档

## API调用方式

### 认证
所有API请求都要在Header里带上你的Key：
```
X-XTQ-Key: xtq-xxxxxx
```

### 对话接口
```python
import requests

r = requests.post(
    'http://localhost:8000/v1/chat',
    headers={'X-XTQ-Key': '你的Key'},
    json={'message': '深蹲膝盖疼怎么办？'}
)
print(r.json()['reply'])
```

### 动作评估接口
```python
r = requests.post(
    'http://localhost:8000/v1/analyze/squat',
    headers={'X-XTQ-Key': '你的Key'},
    params={'knee': 90, 'trunk': 40, 'dev': 5}
)
print(r.json())
```

### 管理接口（管理员用）
- 创建新Key: `POST /v1/keys`
- 查看所有Key: `GET /v1/keys`

## 默认管理员Key
```
xtq-admin-123456
```
（建议生产环境修改环境变量 XTQ_ADMIN_KEY）

## 项目结构
```
├── app.py              # Streamlit Web界面
├── start_api.py         # API服务启动脚本
├── xtq/
│   ├── server.py       # FastAPI后端
│   ├── rule_engine.py   # 防伤规则引擎
│   ├── personalizer.py # 个性化阈值
│   └── ai_advisor.py   # AI顾问模块
├── examples/
│   ├── demo_squat.py   # 命令行Demo
│   └── call_api.py     # API调用示例
└── rules/
    └── squat_rules.json
```

## License
MIT
