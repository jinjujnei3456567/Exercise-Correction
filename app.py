"""
哮天犬 - 运动防伤AI
DeepSeek风格浅色版
"""

import streamlit as st
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))
from xtq.rule_engine import RuleEngine, RiskLevel
from xtq.personalizer import Personalizer, InjuryHistory
from xtq.ai_advisor import AIAdvisor

st.set_page_config(
    page_title='哮天犬',
    page_icon='🐕',
    layout='wide',
    initial_sidebar_state='expanded'
)

# DeepSeek风格CSS
st.markdown('''
<style>
.stApp {
    background: #f8fafc;
    color: #1e293b;
}
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}
.stButton>button {
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-weight: 500;
}
.stButton>button:hover {
    background: #2563eb;
}
.chat-bubble {
    background: white;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin: 0.5rem 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    text-align: center;
}
.risk-safe {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 12px;
    padding: 1.5rem;
}
.risk-caution {
    background: #fffbeb;
    border: 1px solid #fcd34d;
    border-radius: 12px;
    padding: 1.5rem;
}
.risk-warning {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 12px;
    padding: 1.5rem;
}
h1, h2, h3 {
    color: #0f172a;
    font-weight: 600;
}
</style>
''', unsafe_allow_html=True)

if 'engine' not in st.session_state:
    st.session_state.engine = RuleEngine()
if 'personalizer' not in st.session_state:
    st.session_state.personalizer = Personalizer()
if 'ai_advisor' not in st.session_state:
    st.session_state.ai_advisor = AIAdvisor()
if 'history' not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.markdown('### 🐕 哮天犬')
    st.caption('运动防伤AI')
    st.divider()
    
    if st.button('➕ 开启新对话'):
        st.rerun()
    
    st.write('')
    st.caption('今天')
    st.markdown('📊 动作检测')
    st.markdown('🤖 AI顾问')
    
    st.caption('更早')
    st.markdown('📋 训练计划')
    st.markdown('📈 数据报告')
    st.markdown('👤 我的')

st.markdown('# 🤖 AI运动顾问')
st.caption('有任何运动问题，直接问哮天犬')

st.write('')

# 聊天框
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    if msg['role'] == 'user':
        st.markdown(f'<div class="chat-bubble"><b>你：</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble" style="background:#eff6ff"><b>哮天犬：</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

st.write('')

# 输入框
q = st.text_input('', placeholder='给哮天犬发送消息...', label_visibility='collapsed')

col1, col2 = st.columns([6, 1])
with col2:
    if st.button('发送', type='primary') and q:
        st.session_state.chat_history.append({'role': 'user', 'content': q})
        
        r = st.session_state.ai_advisor.chat(q)
        if r.success:
            reply = r.content
        else:
            reply = '我是哮天犬，运动防伤AI顾问。现在AI大模型还没配置，你可以先在动作检测页测试功能。'
        
        st.session_state.chat_history.append({'role': 'ai', 'content': reply})
        st.rerun()
