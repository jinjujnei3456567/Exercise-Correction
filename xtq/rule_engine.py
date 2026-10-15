"""
防伤规则引擎 - 哮天犬核心模块

接收骨骼关键点坐标，计算关节角度，调用规则库进行风险评估
"""

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math


class RiskLevel(Enum):
    """风险等级"""
    SAFE = "safe"        # 安全（绿色）
    CAUTION = "caution"  # 注意（黄色）
    WARNING = "warning"   # 警告（红色）


@dataclass
class JointAngle:
    """关节角度数据"""
    name: str
    value: float  # 角度值（度）
    side: str = ""  # left / right


@dataclass
class RiskResult:
    """风险评估结果"""
    level: RiskLevel
    message: str
    details: Dict[str, any] = field(default_factory=dict)
    indicators: List[Dict] = field(default_factory=list)


class RuleEngine:
    """
    防伤规则引擎
    
    工作流程：
    1. 接收骨骼关键点实时坐标
    2. 计算关键关节角度
    3. 调用自研规则库，将计算角度与安全阈值比对
    4. 综合多项指标，输出风险评估结果
    """
    
    def __init__(self, rules_dir: str = None):
        """
        初始化规则引擎
        
        Args:
            rules_dir: 规则库目录路径
        """
        if rules_dir is None:
            rules_dir = os.path.join(os.path.dirname(__file__), '..', 'rules')
        self.rules_dir = os.path.abspath(rules_dir)
        self.rules: Dict[str, Dict] = {}
        self._load_rules()
    
    def _load_rules(self):
        """加载所有规则库"""
        if not os.path.exists(self.rules_dir):
            print(f"[哮天犬] 规则库目录不存在: {self.rules_dir}")
            return
        
        for filename in os.listdir(self.rules_dir):
            if filename.endswith('.json'):
                exercise = filename.replace('_rules.json', '')
                filepath = os.path.join(self.rules_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.rules[exercise] = json.load(f)
                print(f"[哮天犬] 已加载 {exercise} 规则库，{len(self.rules[exercise].get('indicators', []))} 项指标")
    
    def calculate_angle(self, p1: Tuple[float, float, float], 
                        p2: Tuple[float, float, float], 
                        p3: Tuple[float, float, float]) -> float:
        """
        计算三点之间的关节角度
        
        Args:
            p1: 第一个点 (x, y, z)
            p2: 关节点 (x, y, z)
            p3: 第三个点 (x, y, z)
        
        Returns:
            角度值（度）
        """
        v1 = (p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2])
        v2 = (p3[0] - p2[0], p3[1] - p2[1], p3[2] - p2[2])
        
        dot = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        cos_angle = dot / (mag1 * mag2)
        cos_angle = max(-1.0, min(1.0, cos_angle))  # 防止浮点误差
        angle = math.degrees(math.acos(cos_angle))
        
        return round(angle, 1)
    
    def analyze_squat(self, landmarks: Dict) -> RiskResult:
        """
        分析深蹲动作
        
        Args:
            landmarks: MediaPipe Pose 33个关键点坐标
        
        Returns:
            RiskResult: 风险评估结果
        """
        exercise = 'squat'
        if exercise not in self.rules:
            return RiskResult(
                level=RiskLevel.SAFE,
                message="规则库未加载"
            )
        
        rules = self.rules[exercise]
        indicators = rules.get('indicators', [])
        
        # 计算各项指标
        calculated = {}
        alerts = []
        
        for indicator in indicators:
            name = indicator['name']
            calc_func = getattr(self, f"_calc_{name}", None)
            
            if calc_func:
                value = calc_func(landmarks)
                calculated[name] = value
                
                # 与阈值比对
                safe_range = indicator.get('safe_range', [])
                caution_range = indicator.get('caution_range', [])
                warning_range = indicator.get('warning_range', [])
                injury_risk = indicator.get('injury_risk', '')
                
                level = self._check_threshold(value, safe_range, caution_range, warning_range)
                
                if level != RiskLevel.SAFE:
                    alerts.append({
                        'indicator': name,
                        'value': value,
                        'level': level.value,
                        'injury_risk': injury_risk
                    })
        
        # 综合判断
        if any(a['level'] == 'warning' for a in alerts):
            overall_level = RiskLevel.WARNING
            message = "警告！检测到高风险动作，请立即调整"
        elif any(a['level'] == 'caution' for a in alerts):
            overall_level = RiskLevel.CAUTION
            message = "注意：部分动作指标偏离安全范围，建议调整"
        else:
            overall_level = RiskLevel.SAFE
            message = "动作安全，继续保持"
        
        return RiskResult(
            level=overall_level,
            message=message,
            details=calculated,
            indicators=alerts
        )
    
    def _check_threshold(self, value: float, safe: list, caution: list, warning: list) -> RiskLevel:
        """检查阈值范围"""
        if self._in_range(value, warning):
            return RiskLevel.WARNING
        elif self._in_range(value, caution):
            return RiskLevel.CAUTION
        elif self._in_range(value, safe):
            return RiskLevel.SAFE
        else:
            return RiskLevel.CAUTION
    
    def _in_range(self, value: float, range_list: list) -> bool:
        """判断值是否在范围内（支持多段区间）"""
        if not range_list:
            return False
        
        for r in range_list:
            if len(r) == 2 and r[0] <= value <= r[1]:
                return True
        return False
    
    # === 具体指标计算方法 ===
    
    def _calc_knee_flexion_angle(self, landmarks: Dict) -> float:
        """计算膝关节屈曲角"""
        hip = landmarks.get('left_hip', (0, 0, 0))
        knee = landmarks.get('left_knee', (0, 0, 0))
        ankle = landmarks.get('left_ankle', (0, 0, 0))
        return self.calculate_angle(hip, knee, ankle)
    
    def _calc_trunk_lean_angle(self, landmarks: Dict) -> float:
        """计算躯干前倾角"""
        shoulder = landmarks.get('left_shoulder', (0, 0, 0))
        hip = landmarks.get('left_hip', (0, 0, 0))
        knee = landmarks.get('left_knee', (0, 0, 0))
        return self.calculate_angle(shoulder, hip, knee)
    
    def _calc_knee_ankle_deviation(self, landmarks: Dict) -> float:
        """计算膝-踝联动偏移（简化版）"""
        knee_x = landmarks.get('left_knee', (0, 0, 0))[0]
        ankle_x = landmarks.get('left_ankle', (0, 0, 0))[0]
        hip_y = landmarks.get('left_hip', (0, 0, 0))[1]
        ankle_y = landmarks.get('left_ankle', (0, 0, 0))[1]
        
        if ankle_y == hip_y:
            return 0.0
        
        offset_ratio = abs(knee_x - ankle_x) / max(abs(hip_y - ankle_y), 0.001)
        return round(math.degrees(math.atan(offset_ratio)), 1)
    
    def evaluate(self, exercise: str, landmarks: Dict, 
                 personalized_thresholds: Optional[Dict] = None) -> RiskResult:
        """
        通用评估接口
        
        Args:
            exercise: 动作名称 (squat/deadlift/bench_press)
            landmarks: 骨骼关键点坐标
            personalized_thresholds: 个性化阈值（可选）
        
        Returns:
            RiskResult: 风险评估结果
        """
        if exercise == 'squat':
            result = self.analyze_squat(landmarks)
        else:
            result = RiskResult(
                level=RiskLevel.SAFE,
                message=f"{exercise} 动作支持开发中"
            )
        
        if personalized_thresholds and result.indicators:
            # TODO: 根据个性化阈值重新评估
            pass
        
        return result
