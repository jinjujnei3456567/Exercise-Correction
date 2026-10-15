"""
哮天犬 Demo - 深蹲防伤检测示例

使用方法：
    python examples/demo_squat.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from xtq.rule_engine import RuleEngine, RiskLevel
from xtq.personalizer import Personalizer, InjuryHistory


def demo_basic_squat():
    """基础深蹲检测演示"""
    print("=" * 50)
    print("🐕 哮天犬 - 深蹲防伤检测 Demo")
    print("=" * 50)
    
    # 初始化规则引擎
    engine = RuleEngine()
    
    # 模拟一组骨骼关键点（正常深蹲姿势）
    good_posture = {
        'left_hip': (0.5, 0.6, 0.0),
        'left_knee': (0.5, 0.8, 0.0),
        'left_ankle': (0.5, 1.0, 0.0),
        'left_shoulder': (0.45, 0.3, 0.0),
    }
    
    print("\n【测试1：标准深蹲姿势】")
    result = engine.evaluate('squat', good_posture)
    print(f"风险等级: {result.level.value}")
    print(f"提示信息: {result.message}")
    print(f"详细数据: {result.details}")
    
    # 模拟一组骨骼关键点（膝内扣 + 弯腰过度）
    bad_posture = {
        'left_hip': (0.5, 0.6, 0.0),
        'left_knee': (0.42, 0.8, 0.0),
        'left_ankle': (0.5, 1.0, 0.0),
        'left_shoulder': (0.35, 0.35, 0.0),
    }
    
    print("\n【测试2：问题姿势 - 膝内扣 + 弯腰】")
    result2 = engine.evaluate('squat', bad_posture)
    print(f"风险等级: {result2.level.value}")
    print(f"提示信息: {result2.message}")
    print(f"异常指标数: {len(result2.indicators)}")
    for alert in result2.indicators:
        print(f"  - {alert['indicator']}: {alert['value']}° ({alert['level']})")
        print(f"    关联风险: {alert['injury_risk']}")


def demo_personalized():
    """个性化阈值演示"""
    print("\n" + "=" * 50)
    print("👤 个性化阈值系统 Demo")
    print("=" * 50)
    
    personalizer = Personalizer()
    
    print("\n初始状态：")
    print(personalizer.get_adjustment_summary())
    
    # 添加半月板术后
    personalizer.add_injury(InjuryHistory(
        condition="半月板术后",
        affected_joint="左膝",
        surgery_date="2026-06-01",
        stage="recovery",
        notes="术后3个月，避免深度屈膝"
    ))
    
    print("\n添加半月板术后记录后：")
    print(personalizer.get_adjustment_summary())
    
    squat_thresholds = personalizer.get_thresholds('squat')
    print(f"\n深蹲个性化阈值：")
    for indicator, adj in squat_thresholds.items():
        print(f"  - {indicator}: 调整依据 = {adj.get('basis', 'N/A')}")


if __name__ == '__main__':
    demo_basic_squat()
    demo_personalized()
    print("\n" + "=" * 50)
    print("✅ Demo 运行完成")
    print("=" * 50)
