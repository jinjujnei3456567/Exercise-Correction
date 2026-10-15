"""
哮天犬 (XiaoTianQuan / XTQ) - 运动防伤AI评估引擎

核心模块：
- rule_engine: 防伤规则引擎
- personalizer: 个性化阈值系统
- angle_calculator: 关节角度计算
"""

__version__ = "1.0.0"
__author__ = "护动智眸团队"
__license__ = "MIT"

from .rule_engine import RuleEngine, RiskLevel
from .personalizer import Personalizer
