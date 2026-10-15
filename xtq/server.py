from fastapi import FastAPI, Security, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time, hashlib, os
from dotenv import load_dotenv
from .rule_engine import RuleEngine
from .ai_advisor import AIAdvisor
from .data_store import DataStore

load_dotenv()
app = FastAPI(title='哮天犬 AI', version='1.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

API_KEY_HEADER = APIKeyHeader(name='X-XTQ-Key', auto_error=False)
ADMIN_KEY = os.getenv('XTQ_ADMIN_KEY', 'xtq-admin-123456')
KEYS = {ADMIN_KEY: {'name': 'admin', 'calls': 0}}

engine = RuleEngine()
ai = AIAdvisor()
data_store = DataStore()

class ChatReq(BaseModel):
    message: str
    user_id: str = 'default'

class SquatReq(BaseModel):
    knee_flexion_angle: float
    trunk_lean_angle: float
    knee_ankle_deviation: float
    user_id: str = 'default'

def check_key(key: str = Security(API_KEY_HEADER)):
    if not key or key not in KEYS:
        raise HTTPException(status_code=403, detail='invalid key')
    KEYS[key]['calls'] += 1
    return key

@app.get('/')
def root():
    return {'name': '哮天犬 AI', 'version': '1.1.0', 'docs': '/docs'}

@app.get('/health')
def health():
    return {'status': 'ok', 'engine': len(engine.rules), 'ai': ai.is_ready()}

@app.post('/v1/chat')
def chat(req: ChatReq, key: str = Security(check_key)):
    t = time.time()
    
    # 如果用户问的是自己的训练情况，带上数据
    if any(word in req.message for word in ['我的', '我最近', '训练情况', '数据', '趋势', '怎么样']):
        feedback = data_store.get_feedback_summary(req.user_id)
        req.message = req.message + '\n\n【用户训练数据】' + feedback
    
    r = ai.chat(req.message)
    ms = int((time.time()-t)*1000)
    if r.success:
        return {'reply': r.content, 'model': r.model, 'ms': ms}
    return {'reply': '我是哮天犬，你问的是：' + req.message, 'ms': ms}

@app.post('/v1/analyze/squat')
def squat(req: SquatReq, key: str = Security(check_key)):
    lm = {
        'left_hip': (0.5, 0.6, 0.0),
        'left_knee': (0.5+req.knee_ankle_deviation/100, 0.8, 0.0),
        'left_ankle': (0.5, 1.0, 0.0),
        'left_shoulder': (0.45-req.trunk_lean_angle/200, 0.3, 0.0),
    }
    r = engine.evaluate('squat', lm)
    
    # 记录数据
    data_store.record(req.user_id, 'squat', r.details, r.level.value)
    
    # AI反馈
    ai_r = ai.analyze_posture('squat', r, {})
    advice = ai_r.content if ai_r.success else ''
    
    return {
        'risk_level': r.level.value,
        'message': r.message,
        'indicators': r.details,
        'ai_advice': advice
    }

@app.get('/v1/data/trend')
def trend(user_id: str = 'default', days: int = 30, key: str = Security(check_key)):
    """获取训练趋势分析"""
    return data_store.analyze_trend(user_id)

@app.get('/v1/data/feedback')
def feedback(user_id: str = 'default', key: str = Security(check_key)):
    """获取AI智能反馈（基于历史数据）"""
    summary = data_store.get_feedback_summary(user_id)
    
    # 让AI基于数据生成反馈
    prompt = '请根据以下用户的训练数据，给出简洁的运动反馈和建议。\n\n' + summary
    r = ai.chat(prompt)
    
    return {
        'data_summary': summary,
        'ai_feedback': r.content if r.success else 'AI未配置'
    }

@app.post('/v1/keys')
def create_key(name: str, tier: str = 'free', admin: str = Security(API_KEY_HEADER)):
    if admin != ADMIN_KEY:
        raise HTTPException(status_code=403, detail='need admin')
    s = hashlib.md5((name + str(time.time())).encode()).hexdigest()[:16]
    k = 'xtq-' + s
    KEYS[k] = {'name': name, 'tier': tier, 'calls': 0}
    return {'api_key': k, 'name': name, 'tier': tier}

@app.get('/v1/keys')
def list_keys(admin: str = Security(API_KEY_HEADER)):
    if admin != ADMIN_KEY:
        raise HTTPException(status_code=403)
    return {'keys': list(KEYS.keys()), 'total': len(KEYS)}
