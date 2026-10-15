"""
哮天犬 - 运动防伤AI引擎
终极完善版
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

st.markdown('''
<style>
.stApp {
    background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #16213e 100%);
    color: #e4e7eb;
}
section[data-testid="stSidebar"] {
    background: rgba(26, 31, 46, 0.8);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.05);
}
.stButton>button {
    background: linear-gradient(90deg, #00d4aa 0%, #0096c7 100%);
    color: #0f1419;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 2rem;
    font-weight: 700;
    transition: all 0.3s;
}
.stButton>button:hover {
    box-shadow: 0 0 30px rgba(0, 212, 170, 0.5);
    transform: translateY(-2px);
}
.metric-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s;
}
.metric-box:hover {
    border-color: #00d4aa;
    transform: translateY(-3px);
}
.risk-safe {
    background: linear-gradient(135deg, rgba(0,212,170,0.15) 0%, rgba(0,212,170,0.05) 100%);
    border: 1px solid #00d4aa;
    border-radius: 16px;
    padding: 2rem;
}
.risk-caution {
    background: linear-gradient(135deg, rgba(255,193,7,0.15) 0%, rgba(255,193,7,0.05) 100%);
    border: 1px solid #ffc107;
    border-radius: 16px;
    padding: 2rem;
}
.risk-warning {
    background: linear-gradient(135deg, rgba(255,82,82,0.15) 0%, rgba(255,82,82,0.05) 100%);
    border: 1px solid #ff5252;
    border-radius: 16px;
    padding: 2rem;
}
.history-item {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid #00d4aa;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
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
    st.markdown('## 🐕 哮天犬')
    st.caption('运动防伤AI引擎 v1.0')
    st.divider()
    
    if st.session_state.ai_advisor.is_ready():
        st.markdown('🟢 **AI在线**')
    else:
        st.markdown('🟡 **AI未配置**')
    
    st.divider()
    st.markdown('### 导航')
    page = st.radio('', ['📊 动作检测', '🤖 AI顾问', '📋 训练计划', '📈 数据报告', '👤 我的'])

if page == '📊 动作检测':
    st.markdown('# 🏋️ 深蹲动作检测')
    
    col1, col2 = st.columns([1, 1.3])
    
    with col1:
        st.markdown('#### 🎛️ 参数调节')
        knee = st.slider('膝关节屈曲角', 30, 160, 90)
        trunk = st.slider('躯干前倾角', 10, 80, 40)
        dev = st.slider('膝内扣偏移', 0, 30, 5)
        
        if st.button('🔍 开始评估', type='primary'):
            lm = {
                'left_hip': (0.5, 0.6, 0.0),
                'left_knee': (0.5+dev/100, 0.8, 0.0),
                'left_ankle': (0.5, 1.0, 0.0),
                'left_shoulder': (0.45-trunk/200, 0.3, 0.0),
            }
            r = st.session_state.engine.evaluate('squat', lm)
            st.session_state['result'] = r
            st.session_state['history'].append({
                'time': datetime.now().strftime('%H:%M'),
                'level': r.level.value,
                'knee': knee,
                'trunk': trunk,
                'dev': dev
            })
    
    with col2:
        st.markdown('#### 📋 评估结果')
        
        if 'result' in st.session_state:
            r = st.session_state['result']
            
            if r.level == RiskLevel.SAFE:
                st.markdown('<div class="risk-safe"><h2>🟢 安全</h2><p>动作标准，继续保持！</p></div>', unsafe_allow_html=True)
            elif r.level == RiskLevel.CAUTION:
                st.markdown('<div class="risk-caution"><h2>🟡 注意</h2><p>部分指标偏离安全范围</p></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="risk-warning"><h2>🔴 警告</h2><p>高风险！请立即调整</p></div>', unsafe_allow_html=True)
            
            st.write('')
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric('膝盖角度', f'{knee}°')
            with c2:
                st.metric('躯干角度', f'{trunk}°')
            with c3:
                st.metric('膝内扣', f'{dev}°')
            
            if st.button('🤖 AI智能分析'):
                with st.spinner('分析中...'):
                    ai_r = st.session_state.ai_advisor.analyze_posture('squat', r, {})
                    if ai_r.success:
                        st.info(ai_r.content)
        else:
            st.info('👈 拖动左边滑块开始')
    
    st.divider()
    st.markdown('#### 🕐 最近记录')
    if st.session_state['history']:
        for h in reversed(st.session_state['history'][-5:]):
            icon = '🟢' if h['level'] == 'safe' else '🟡' if h['level'] == 'caution' else '🔴'
            st.markdown(f'<div class="history-item">{icon} {h["time"]} · 膝盖{h["knee"]}° · 躯干{h["trunk"]}°</div>', unsafe_allow_html=True)
    else:
        st.caption('还没有记录')

elif page == '🤖 AI顾问':
    st.markdown('# 🤖 AI运动顾问')
    st.write('有任何运动问题，直接问')
    
    q = st.text_input('', placeholder='比如：深蹲膝盖疼怎么办？')
    
    if st.button('发送', type='primary') and q:
        with st.spinner('思考中...'):
            r = st.session_state.ai_advisor.chat(q)
            if r.success:
                st.markdown('**哮天犬：**')
                st.write(r.content)
            else:
                st.warning('AI未配置，请先设置API Key')

elif page == '📋 训练计划':
    st.markdown('# 📋 本周训练计划')
    
    days = [
        ('周一', '下肢力量', '深蹲 4组×8\n硬拉 3组×6\n箭步蹲 3组×10'),
        ('周三', '核心稳定', '平板支撑 3组×60秒\n臀桥 4组×15\n死虫式 3组×12'),
        ('周五', '上肢推', '卧推 4组×8\n肩推 3组×10\n俯卧撑 3组×力竭'),
        ('周日', '有氧恢复', '快走 30分钟\n动态拉伸 10分钟'),
    ]
    
    cols = st.columns(4)
    for i, (day, title, content) in enumerate(days):
        with cols[i]:
            st.markdown(f'<div class="metric-box"><h3>{day}</h3><p><b>{title}</b></p><p>{content.replace(chr(10), "<br>")}</p></div>', unsafe_allow_html=True)
    
    st.write('')
    st.info('💡 提示：每次训练前先做5分钟动态热身')

elif page == '📈 数据报告':
    st.markdown('# 📈 健康数据报告')
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-box"><h2>23</h2><p>总训练次数</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-box"><h2>87%</h2><p>安全率</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-box"><h2>3.2</h2><p>周均训练</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-box"><h2>↑12%</h2><p>进步幅度</p></div>', unsafe_allow_html=True)
    
    st.write('')
    st.markdown('#### 最近7天安全率趋势')
    st.line_chart({'安全率(%)': [60, 65, 70, 72, 78, 85, 87]})

elif page == '👤 我的':
    st.markdown('# 👤 个人设置')
    
    st.markdown('#### 🏥 我的损伤史')
    injuries = st.session_state.personalizer.user_injuries
    
    if injuries:
        for inj in injuries:
            st.markdown(f'<div class="history-item">🦴 {inj.condition}</div>', unsafe_allow_html=True)
    else:
        st.caption('暂无损伤记录')
    
    with st.expander('➕ 添加损伤记录'):
        cond = st.text_input('伤病名称', placeholder='如：半月板术后')
        joint = st.text_input('受累关节', placeholder='如：左膝')
        if st.button('添加') and cond:
            st.session_state.personalizer.add_injury(InjuryHistory(condition=cond, affected_joint=joint))
            st.success('添加成功！')
            st.rerun()
    
    st.divider()
    st.markdown('#### ⚙️ 系统设置')
    st.checkbox('开启声音提醒')
    st.checkbox('自动保存训练记录')
    st.selectbox('主题', ['深色', '浅色'])
