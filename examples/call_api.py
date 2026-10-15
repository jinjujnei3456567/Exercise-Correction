"""
哮天犬API调用示例

先启动服务：python start_api.py
然后运行本示例：python examples/call_api.py
"""

import requests

BASE_URL = 'http://localhost:8000'
API_KEY = 'xtq-admin-123456'  # 默认管理员Key

headers = {
    'X-XTQ-Key': API_KEY
}

print('=== 1. 健康检查 ===')
r = requests.get(f'{BASE_URL}/health')
print(r.json())

print('\n=== 2. AI对话 ===')
r = requests.post(
    f'{BASE_URL}/v1/chat',
    headers=headers,
    json={'message': '深蹲膝盖疼怎么办？'}
)
print(r.json()['reply'])

print('\n=== 3. 深蹲风险评估 ===')
r = requests.post(
    f'{BASE_URL}/v1/analyze/squat',
    headers=headers,
    params={'knee': 90, 'trunk': 40, 'dev': 5}
)
print(r.json())

print('\n=== 4. 创建新的API Key ===')
r = requests.post(
    f'{BASE_URL}/v1/keys',
    headers=headers,
    params={'name': '测试用户', 'tier': 'free'}
)
new_key = r.json()['api_key']
print(f'新Key: {new_key}')

print('\n=== 5. 用新Key调用 ===')
headers2 = {'X-XTQ-Key': new_key}
r = requests.post(
    f'{BASE_URL}/v1/chat',
    headers=headers2,
    json={'message': '你好哮天犬'}
)
print(r.json()['reply'])

print('\n✅ 所有测试通过！')
