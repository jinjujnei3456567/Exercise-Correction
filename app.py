"""
哮天犬桌面应用 - Streamlit Web界面

启动方式：
    streamlit run app.py
"""

import streamlit as st
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入哮天犬模块
sys.path.insert(0, os.path.dirname(__file__))
from xtq.rule_engine import RuleEngine, RiskLevel
from xtq.personalizer import Personalizer, InjuryHistory
from xtq.ai_advisor import AIAdvisor

# 页面配置
st.set_page_config(
    page_title="哮天犬 - 运动防伤AI",
    page_icon="🐕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if 'engine' not in st.session_state:
    st.session_state.engine = RuleEngine()
if 'personalizer' not in st.session_state:
    st.session_state.personalizer = Personalizer()
if 'ai_advisor' not in st.session_state:
    st.session_state.ai_advisor = AIAdvisor()
if 'history' not in st.session_state:
    st.session_state.history = []


def main():
    st.title("🐕 哮天犬 - 运动防伤AI引擎")
    st.caption("你的数字关节保镖 · 基于AI视觉的个性化运动防伤评估")
    
    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 设置")
        
        # API配置状态
        if st.session_state.ai_advisor.is_ready():
            st.success(f"✅ AI已连接: {st.session_state.ai_advisor.model}")
        else:
            st.warning("⚠️ AI未配置")
            st.info("请在 .env 文件中配置 XTQ_API_KEY")
        
        st.divider()
        
        # 动作选择
        exercise = st.selectbox(
            "选择动作",
            ["squat", "deadlift", "bench_press"],
            format_func=lambda x: {
                'squat': '深蹲',
                'deadlift': '硬拉（开发中）',
                'bench_press': '卧推（开发中）'
            }[x]
        )
        
        st.divider()
        
        # 损伤史管理
        st.subheader("🏥 我的损伤史")
        injuries = st.session_state.personalizer.user_injuries
        
        if injuries:
            for i, inj in enumerate(injuries):
                st.write(f"• {inj.condition}")
        else:
            st.write("暂无记录")
        
        with st.expander("添加损伤史"):
            condition = st.text_input("伤病名称", placeholder="如：半月板术后")
            joint = st.text_input("受累关节", placeholder="如：左膝")
            if st.button("添加") and condition:
                st.session_state.personalizer.add_injury(InjuryHistory(
                    condition=condition,
                    affected_joint=joint
                ))
                st.rerun()
    
    # 主页面标签
    tab1, tab2, tab3, tab4 = st.tabs(["📊 动作检测", "🤖 AI顾问", "📈 健康趋势", "ℹ️ 关于"])
    
    with tab1:
        st.header("动作风险评估")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("输入参数（演示模式）")
            st.info("💡 这是演示模式，真实版本会调用摄像头实时识别")
            
            knee_angle = st.slider("膝关节屈曲角 (°)", 30, 160, 90)
            trunk_angle = st.slider("躯干前倾角 (°)", 10, 80, 40)
            deviation = st.slider("膝-踝偏移 (°)", 0, 30, 5)
            
            if st.button("开始评估", type="primary"):
                # 构造模拟数据
                landmarks = {
                    'left_hip': (0.5, 0.6, 0.0),
                    'left_knee': (0.5 + deviation/100, 0.8, 0.0),
                    'left_ankle': (0.5, 1.0, 0.0),
                    'left_shoulder': (0.45 - trunk_angle/200, 0.3, 0.0),
                }
                
                result = st.session_state.engine.evaluate(exercise, landmarks)
                
                # 记录历史
                st.session_state.history.append({
                    'exercise': exercise,
                    'knee_angle': knee_angle,
                    'trunk_angle': trunk_angle,
                    'deviation': deviation,
                    'level': result.level.value
                })
                
                st.session_state['last_result'] = result
        
        with col2:
            st.subheader("评估结果")
            
            if 'last_result' in st.session_state:
                result = st.session_state['last_result']
                
                # 风险等级展示
                if result.level == RiskLevel.SAFE:
                    st.success(f"🟢 安全：{result.message}")
                elif result.level == RiskLevel.CAUTION:
                    st.warning(f"🟡 注意：{result.message}")
                else:
                    st.error(f"🔴 警告：{result.message}")
                
                # 详细指标
                st.write("**详细指标：**")
                for k, v in result.details.items():
                    st.write(f"- {k}: {v}°")
                
                # 异常指标
                if result.indicators:
                    st.write("**异常项：**")
                    for alert in result.indicators:
                        st.error(f"• {alert['indicator']}: {alert['value']}° — {alert['injury_risk']}")
                
                # AI建议按钮
                if st.button("🤖 让哮天犬给我建议"):
                    with st.spinner("AI正在分析..."):
                        user_profile = st.session_state.personalizer.export_user_profile()
                        ai_result = st.session_state.ai_advisor.analyze_posture(
                            exercise, result, user_profile
                        )
                        
                        if ai_result.success:
                            st.info(f"**AI顾问建议：**\n\n{ai_result.content}")
                        else:
                            st.error(f"AI调用失败：{ai_result.error}")
            else:
                st.info("👈 拖动左边的滑块，然后点击「开始评估」")
    
    with tab2:
        st.header("🤖 AI运动顾问")
        st.write("有任何运动问题，直接问哮天犬！")
        
        if not st.session_state.ai_advisor.is_ready():
            st.warning("AI未配置，请先在 .env 文件中设置 XTQ_API_KEY")
        
        user_question = st.text_input("你的问题：", placeholder="比如：深蹲膝盖疼怎么办？")
        
        if st.button("发送", type="primary") and user_question:
            with st.spinner("思考中..."):
                result = st.session_state.ai_advisor.chat(user_question)
                if result.success:
                    st.write(f"**哮天犬：**\n\n{result.content}")
                else:
                    st.error(result.error)
        
        # 快捷问题
        st.write("**试试问：**")
        cols = st.columns(2)
        with cols[0]:
            if st.button("深蹲常见错误有哪些？"):
                result = st.session_state.ai_advisor.chat("深蹲常见错误有哪些？")
                if result.success:
                    st.write(result.content)
        with cols[1]:
            if st.button("膝盖不好怎么健身？"):
                result = st.session_state.ai_advisor.chat("膝盖不好怎么健身？")
                if result.success:
                    st.write(result.content)
    
    with tab3:
        st.header("📈 关节健康趋势")
        
        if st.session_state.history:
            import pandas as pd
            df = pd.DataFrame(st.session_state.history)
            
            st.write(f"已记录 {len(df)} 次评估")
            
            # 趋势图
            st.line_chart(df[['knee_angle', 'trunk_angle']])
            
            # 风险等级统计
            level_counts = df['level'].value_counts()
            st.write("**风险等级分布：**")
            st.bar_chart(level_counts)
        else:
            st.info("还没有记录，先去「动作检测」页做几次评估吧")
    
    with tab4:
        st.header("ℹ️ 关于哮天犬")
        st.write("""
        **哮天犬 (XiaoTianQuan / XTQ)** 是一个开源的运动防伤AI评估引擎。
        
        ### 核心功能
        - 🛡️ 实时动作风险评估
        - 👤 个性化安全阈值
        - 🤖 AI智能运动建议
        - 📊 长期健康趋势追踪
        
        ### 技术栈
        - 姿态识别：MediaPipe Pose
        - 规则引擎：自研防伤规则库
        - AI顾问：大语言模型API
        - 界面：Streamlit
        
        ### 开源协议
        MIT License
        """)


if __name__ == '__main__':
    main()
