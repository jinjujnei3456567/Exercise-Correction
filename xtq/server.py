from fastapi import FastAPI, Security, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time, hashlib, os
from dotenv import load_dotenv
from .rule_engine import RuleEngine
from .ai_advisor import AIAdvisor

load_dotenv()
app = FastAPI(title='哮天犬 AI', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

API_KEY_HEADER = APIKeyHeader(name='X-XTQ-Key', auto_error=False)
ADMIN_KEY = os.getenv('XTQ_ADMIN_KEY', 'xtq-admin-123456')
KEYS = {ADMIN_KEY: {'name': 'admin', 'calls': 0}}

engine = RuleEngine()
ai = AIAdvisor()

class ChatReq(BaseModel):
    message: str

async def check_key(key: str = Security(API_KEY_HEADER)):
    if not key or key not in KEYS:
        raise HTTPException(status_code=403, detail='invalid key')
    KEYS[key]['calls'] += 1
    return key

@app.get('/')
def root():
    return {'name': '哮天犬 AI', 'version': '1.0.0', 'docs': '/docs'}

@app.get('/health')
def health():
    return {'status': 'ok', 'engine': len(engine.rules), 'ai': ai.is_ready()}

@app.post('/v1/chat')
def chat(req: ChatReq, key: str = Security(check_key)):
    t = time.time()
    r = ai.chat(req.message)
    ms = int((time.time()-t)*1000)
    if r.success:
        return {'reply': r.content, 'model': r.model, 'ms': ms}
    return {'reply': '我是哮天犬，你问的是：' + req.message, 'ms': ms}

@app.post('/v1/analyze/squat')
def squat(knee: float, trunk: float, dev: float, key: str = Security(check_key)):
    lm = {
        'left_hip': (0.5, 0.6, 0.0),
        'left_knee': (0.5+dev/100, 0.8, 0.0),
        'left_ankle': (0.5, 1.0, 0.0),
        'left_shoulder': (0.45-trunk/200, 0.3, 0.0),
    }
    r = engine.evaluate('squat', lm)
    return {'risk': r.level.value, 'msg': r.message, 'data': r.details}

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
