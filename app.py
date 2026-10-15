"""
哮天犬 - 运动防伤AI引擎
全新UI版本
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

# 页面配置
st.set_page_config(
    page_title='哮天犬 - 运动防伤AI',
    page_icon='🐕',
    layout='wide',
    initial_sidebar_state='expanded'
)

# 自定义CSS
st.markdown('''
<style>
.main {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f0 100%);
}
.stButton>button {
    background: linear-gradient(90deg, #ff6b35 0%, #f7931e 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 2rem;
    font-weight: bold;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255,107,53,0.4);
}
.metric-card {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    text-align: center;
}
.risk-safe {
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    padding: 1.5rem;
    border-radius: 15px;
    border-left: 5px solid #28a745;
}
.risk-caution {
    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    padding: 1.5rem;
    border-radius: 15px;
    border-left: 5px solid #ffc107;
}
.risk-warning {
    background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    padding: 1.5rem;
    border-radius: 15px;
    border-left: 5px solid #dc3545;
}
h1 {
    color: #2d3436;
    font-weight: 800;
}
</style>
''', unsafe_allow_html=True)

# 初始化
if 'engine' not in st.session_state:
    st.session_state.engine = RuleEngine()
if 'personalizer' not in st.session_state:
    st.session_state.personalizer = Personalizer()
if 'ai_advisor' not in st.session_state:
    st.session_state.ai_advisor = AIAdvisor()
if 'history' not in st.session_state:
    st.session_state.history = []

# 侧边栏
with st.sidebar:
    st.markdown('### 🐕 哮天犬')
    st.caption('运动防伤AI引擎')
    st.divider()
    
    if st.session_state.ai_advisor.is_ready():
        st.success('✅ AI已连接')
    else:
        st.warning('⚠️ AI未配置')
    
    st.divider()
    
    exercise = st.selectbox(
        '选择动作',
        ['squat', 'deadlift', 'bench_press'],
        format_func=lambda x: {'squat': '🏋️ 深蹲', 'deadlift': '🏋️ 硬拉', 'bench_press': '🏋️ 卧推'}[x]
    )

# 主标题
st.markdown('# 🐕 哮天犬')
st.caption('你的数字关节保镖 · 用AI守护每一次训练')

st.divider()

# 标签页
tab1, tab2, tab3 = st.tabs(['📊 动作检测', '🤖 AI顾问', '📈 健康报告'])

with tab1:
    st.subheader('动作风险评估')
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('#### 🎛️ 参数调节')
        knee = st.slider('膝关节屈曲角', 30, 160, 90, help='下蹲深度')
        trunk = st.slider('躯干前倾角', 10, 80, 40, help='弯腰程度')
        dev = st.slider('膝踝偏移', 0, 30, 5, help='膝盖内扣程度')
        
        if st.button('🔍 开始评估', type='primary'):
            landmarks = {
                'left_hip': (0.5, 0.6, 0.0),
                'left_knee': (0.5+dev/100, 0.8, 0.0),
                'left_ankle': (0.5, 1.0, 0.0),
                'left_shoulder': (0.45-trunk/200, 0.3, 0.0),
            }
            result = st.session_state.engine.evaluate('squat', landmarks)
            st.session_state['last_result'] = result
    
    with col2:
        st.markdown('#### 📋 评估结果')
        
        if 'last_result' in st.session_state:
            result = st.session_state['last_result']
            
            if result.level == RiskLevel.SAFE:
                st.markdown('<div class="risk-safe"><h3>🟢 动作安全</h3><p>继续保持！</p></div>', unsafe_allow_html=True)
            elif result.level == RiskLevel.CAUTION:
                st.markdown('<div class="risk-caution"><h3>🟡 注意调整</h3><p>部分指标偏离安全范围</p></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="risk-warning"><h3>🔴 高风险！</h3><p>请立即调整动作</p></div>', unsafe_allow_html=True)
            
            st.write('')
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric('膝盖角度', f'{knee}°')
            with c2:
                st.metric('躯干角度', f'{trunk}°')
            with c3:
                st.metric('膝踝偏移', f'{dev}°')
            
            if st.button('🤖 AI给我建议'):
                with st.spinner('AI分析中...'):
                    ai_result = st.session_state.ai_advisor.analyze_posture('squat', result, {})
                    if ai_result.success:
                        st.info(ai_result.content)
                    else:
                        st.warning('AI未配置，使用规则回复')
        else:
            st.info('👈 拖动左边滑块，点开始评估')

with tab2:
    st.subheader('🤖 AI运动顾问')
    st.write('有任何运动问题，直接问哮天犬！')
    
    user_q = st.text_input('你的问题：', placeholder='比如：深蹲膝盖疼怎么办？')
    
    if st.button('发送', type='primary') and user_q:
        with st.spinner('思考中...'):
            r = st.session_state.ai_advisor.chat(user_q)
            if r.success:
                st.markdown(f'**哮天犬：**')
                st.write(r.content)
            else:
                st.warning('AI未配置，请先设置XTQ_API_KEY')

with tab3:
    st.subheader('📈 关节健康趋势')
    st.info('记录每次训练，追踪你的进步')
    st.write('')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><h2>12</h2><p>总训练次数</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h2>85%</h2><p>安全率</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h2>↑</h2><p>比上周进步</p></div>', unsafe_allow_html=True)
