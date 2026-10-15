"""
哮天犬 - 运动防伤AI引擎
深色科技风UI
"""

import streamlit as st
import sys
import os
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

# 深色主题CSS
st.markdown('''
<style>
.stApp {
    background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
    color: #e4e7eb;
}
section[data-testid="stSidebar"] {
    background: #1a1f2e;
    border-right: 1px solid #2d3748;
}
.stButton>button {
    background: linear-gradient(90deg, #00d4aa 0%, #00b4d8 100%);
    color: #0f1419;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 2rem;
    font-weight: 700;
}
.stButton>button:hover {
    box-shadow: 0 0 20px rgba(0, 212, 170, 0.4);
}
h1, h2, h3 {
    color: #ffffff;
}
.metric-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    backdrop-filter: blur(10px);
}
.risk-safe {
    background: rgba(0, 212, 170, 0.1);
    border: 1px solid #00d4aa;
    border-radius: 16px;
    padding: 1.5rem;
}
.risk-caution {
    background: rgba(255, 193, 7, 0.1);
    border: 1px solid #ffc107;
    border-radius: 16px;
    padding: 1.5rem;
}
.risk-warning {
    background: rgba(255, 82, 82, 0.1);
    border: 1px solid #ff5252;
    border-radius: 16px;
    padding: 1.5rem;
}
.pose-demo {
    background: rgba(255,255,255,0.03);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    font-size: 4rem;
}
</style>
''', unsafe_allow_html=True)

if 'engine' not in st.session_state:
    st.session_state.engine = RuleEngine()
if 'personalizer' not in st.session_state:
    st.session_state.personalizer = Personalizer()
if 'ai_advisor' not in st.session_state:
    st.session_state.ai_advisor = AIAdvisor()

with st.sidebar:
    st.markdown('## 🐕 哮天犬')
    st.caption('运动防伤AI引擎')
    st.divider()
    
    if st.session_state.ai_advisor.is_ready():
        st.success('● AI在线')
    else:
        st.warning('● AI未配置')
    
    st.divider()
    st.markdown('### 功能菜单')
    page = st.radio('', ['📊 动作检测', '🤖 AI顾问', '📋 训练计划', '📈 数据报告'])

if page == '📊 动作检测':
    st.markdown('# 🏋️ 动作风险评估')
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown('#### 调节参数')
        knee = st.slider('膝关节屈曲角', 30, 160, 90, help='下蹲深度')
        trunk = st.slider('躯干前倾角', 10, 80, 40, help='身体前倾程度')
        dev = st.slider('膝内扣偏移', 0, 30, 5, help='膝盖向内偏移')
        
        if st.button('🔍 开始评估', type='primary'):
            lm = {
                'left_hip': (0.5, 0.6, 0.0),
                'left_knee': (0.5+dev/100, 0.8, 0.0),
                'left_ankle': (0.5, 1.0, 0.0),
                'left_shoulder': (0.45-trunk/200, 0.3, 0.0),
            }
            st.session_state['result'] = st.session_state.engine.evaluate('squat', lm)
    
    with col2:
        st.markdown('#### 实时结果')
        
        if 'result' in st.session_state:
            r = st.session_state['result']
            
            if r.level == RiskLevel.SAFE:
                st.markdown('<div class="risk-safe"><h2>🟢 安全</h2><p>动作标准，继续保持</p></div>', unsafe_allow_html=True)
            elif r.level == RiskLevel.CAUTION:
                st.markdown('<div class="risk-caution"><h2>🟡 注意</h2><p>部分指标偏离安全范围</p></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="risk-warning"><h2>🔴 警告</h2><p>高风险！请立即调整</p></div>', unsafe_allow_html=True)
            
            st.write('')
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric('膝盖', f'{knee}°')
            with c2:
                st.metric('躯干', f'{trunk}°')
            with c3:
                st.metric('偏移', f'{dev}°')
            
            if st.button('🤖 AI智能分析'):
                with st.spinner('分析中...'):
                    ai_r = st.session_state.ai_advisor.analyze_posture('squat', r, {})
                    if ai_r.success:
                        st.info(ai_r.content)
        else:
            st.markdown('<div class="pose-demo">🧍‍♂️<br>🏋️</div>', unsafe_allow_html=True)
            st.caption('← 拖动左边滑块开始评估')

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
                st.warning('AI未配置')

elif page == '📋 训练计划':
    st.markdown('# 📋 本周训练计划')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-box"><h3>周一</h3><p>🏋️ 下肢力量</p><p>深蹲 4组×8</p><p>硬拉 3组×6</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-box"><h3>周三</h3><p>🤸 核心稳定</p><p>平板支撑 3组</p><p>臀桥 4组×15</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-box"><h3>周五</h3><p>🏋️ 上肢推</p><p>卧推 4组×8</p><p>肩推 3组×10</p></div>', unsafe_allow_html=True)
    
    st.write('')
    st.info('💡 提示：每次训练前先做5分钟动态热身')

elif page == '📈 数据报告':
    st.markdown('# 📈 健康数据报告')
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-box"><h2>23</h2><p>总训练</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-box"><h2>87%</h2><p>安全率</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-box"><h2>3.2</h2><p>周平均</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-box"><h2>↑12%</h2><p>进步幅度</p></div>', unsafe_allow_html=True)
    
    st.write('')
    st.line_chart({'安全率': [60, 65, 70, 75, 80, 85, 87]})
