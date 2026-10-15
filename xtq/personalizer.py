"""
个性化阈值系统 - 根据用户损伤史动态调整安全阈值
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os


@dataclass
class InjuryHistory:
    """用户损伤史"""
    condition: str  # 伤病名称
    affected_joint: str  # 受累关节
    surgery_date: Optional[str] = None  # 手术日期
    stage: str = "recovery"  # recovery / chronic / past
    notes: str = ""


@dataclass
class ThresholdAdjustment:
    """阈值调整项"""
    indicator: str  # 指标名称
    original_min: float
    original_max: float
    adjusted_min: float
    adjusted_max: float
    basis: str  # 调整依据


class Personalizer:
    """
    个性化阈值系统
    
    同样一个深蹲，膝盖做过手术的人、腰椎间盘突出的人、无损伤史的人——安全范围完全不同。
    """
    
    DEFAULT_ADJUSTMENTS = {
        'meniscus_post_op': {
            'description': '半月板术后（<6个月）',
            'adjustments': {
                'squat': {
                    'knee_flexion_angle': {
                        'max': 90,
                        'basis': '术后康复指南：避免深度屈膝'
                    }
                }
            }
        },
        'acl_reconstruction': {
            'description': '前交叉韧带重建术后',
            'adjustments': {
                'squat': {
                    'knee_ankle_deviation': {
                        'max': 5,
                        'basis': '移植物保护'
                    }
                }
            }
        },
        'lumbar_disc_herniation': {
            'description': '腰椎间盘突出（L4-L5/L5-S1）',
            'adjustments': {
                'deadlift': {
                    'lumbar_flexion_angle': {
                        'max': 40,
                        'basis': '腰椎负荷研究'
                    }
                }
            }
        },
        'rotator_cuff_injury': {
            'description': '肩袖损伤/肩峰撞击',
            'adjustments': {
                'bench_press': {
                    'shoulder_abduction_angle': {
                        'max': 70,
                        'forbidden_above': 90,
                        'basis': '肩峰下间隙保护'
                    }
                }
            }
        }
    }
    
    def __init__(self):
        self.user_injuries: List[InjuryHistory] = []
        self.adjustments_cache: Dict = {}
    
    def add_injury(self, injury: InjuryHistory):
        """添加损伤史"""
        self.user_injuries.append(injury)
        self._recalculate_adjustments()
    
    def remove_injury(self, index: int):
        """移除损伤史"""
        if 0 <= index < len(self.user_injuries):
            self.user_injuries.pop(index)
            self._recalculate_adjustments()
    
    def _recalculate_adjustments(self):
        """重新计算所有个性化阈值调整"""
        self.adjustments_cache = {}
        
        for injury in self.user_injuries:
            condition_key = self._match_condition(injury.condition)
            if condition_key and condition_key in self.DEFAULT_ADJUSTMENTS:
                preset = self.DEFAULT_ADJUSTMENTS[condition_key]
                
                for exercise, indicators in preset['adjustments'].items():
                    if exercise not in self.adjustments_cache:
                        self.adjustments_cache[exercise] = {}
                    
                    for indicator, adj in indicators.items():
                        self.adjustments_cache[exercise][indicator] = adj
    
    def _match_condition(self, condition: str) -> Optional[str]:
        """匹配伤病名称到预设key"""
        condition_lower = condition.lower()
        
        mappings = {
            'meniscus_post_op': ['半月板', 'meniscus'],
            'acl_reconstruction': ['前交叉', 'acl', '十字韧带'],
            'lumbar_disc_herniation': ['腰椎', '间盘突出', 'lumbar', 'disc'],
            'rotator_cuff_injury': ['肩袖', '肩峰', 'rotator', 'shoulder impingement'],
        }
        
        for key, keywords in mappings.items():
            for kw in keywords:
                if kw in condition_lower:
                    return key
        
        return None
    
    def get_thresholds(self, exercise: str) -> Dict:
        """获取某动作的个性化阈值"""
        return self.adjustments_cache.get(exercise, {})
    
    def get_adjustment_summary(self) -> str:
        """获取调整摘要（用于UI展示）"""
        if not self.user_injuries:
            return "使用标准安全阈值"
        
        lines = [f"已应用 {len(self.user_injuries)} 项个性化调整："]
        for injury in self.user_injuries:
            lines.append(f"  - {injury.condition}")
        return "\n".join(lines)
    
    def export_user_profile(self) -> Dict:
        """导出用户画像（用于持久化）"""
        return {
            'injuries': [{
                'condition': i.condition,
                'affected_joint': i.affected_joint,
                'surgery_date': i.surgery_date,
                'stage': i.stage,
                'notes': i.notes
            } for i in self.user_injuries],
            'adjustments': self.adjustments_cache
        }
    
    def import_user_profile(self, data: Dict):
        """导入用户画像"""
        self.user_injuries = []
        for item in data.get('injuries', []):
            self.user_injuries.append(InjuryHistory(**item))
        self._recalculate_adjustments()
