"""
哮天犬API调用完整示例

先启动服务：python start_api.py
然后运行：python examples/call_api.py
"""

import requests

BASE_URL = 'http://localhost:8000'
API_KEY = 'xtq-admin-123456'

headers = {'X-XTQ-Key': API_KEY}
user_id = 'test_user'

print('=== 1. 健康检查 ===')
r = requests.get(f'{BASE_URL}/health')
print(r.json())

print('\n=== 2. 做几次深蹲评估（会自动记录数据）===')
for i in range(3):
    r = requests.post(
        f'{BASE_URL}/v1/analyze/squat',
        headers=headers,
        json={
            'knee_flexion_angle': 90 + i*5,
            'trunk_lean_angle': 40,
            'knee_ankle_deviation': 5,
            'user_id': user_id
        }
    )
    print(f'第{i+1}次: {r.json()["risk_level"]} - {r.json()["message"]}')

print('\n=== 3. 查看训练趋势分析 ===')
r = requests.get(
    f'{BASE_URL}/v1/data/trend',
    headers=headers,
    params={'user_id': user_id, 'days': 30}
)
print('总记录数:', r.json()['total_records'])
print('安全率:', r.json()['safe_rate'], '%')

print('\n=== 4. AI智能反馈（基于历史数据）===')
r = requests.get(
    f'{BASE_URL}/v1/data/feedback',
    headers=headers,
    params={'user_id': user_id}
)
print(r.json()['ai_feedback'])

print('\n=== 5. 对话（问自己的训练情况）===')
r = requests.post(
    f'{BASE_URL}/v1/chat',
    headers=headers,
    json={'message': '我最近训练怎么样？有什么需要改进的？', 'user_id': user_id}
)
print(r.json()['reply'])

print('\n✅ 所有测试完成！')
