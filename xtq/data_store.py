"""
哮天犬数据存储和分析模块

记录每次训练数据，做趋势分析，给AI反馈提供数据支撑
"""

import time
import json
import os
from typing import Dict, List, Optional
from collections import defaultdict


class DataStore:
    """运动数据存储和分析"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.data_dir = os.path.abspath(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.cache = defaultdict(list)  # user_id -> [records]
    
    def record(self, user_id: str, exercise: str, data: Dict, risk_level: str):
        """记录一次训练评估"""
        record = {
            'timestamp': time.time(),
            'exercise': exercise,
            'risk_level': risk_level,
            'data': data
        }
        self.cache[user_id].append(record)
        self._save(user_id)
        return record
    
    def get_history(self, user_id: str, days: int = 30) -> List[Dict]:
        """获取最近N天的记录"""
        cutoff = time.time() - days * 86400
        records = [r for r in self.cache.get(user_id, []) if r['timestamp'] > cutoff]
        return sorted(records, key=lambda x: x['timestamp'])
    
    def analyze_trend(self, user_id: str, exercise: str = None) -> Dict:
        """分析趋势"""
        records = self.get_history(user_id, days=30)
        if exercise:
            records = [r for r in records if r['exercise'] == exercise]
        
        if not records:
            return {'total': 0, 'message': '暂无数据'}
        
        total = len(records)
        safe_count = sum(1 for r in records if r['risk_level'] == 'safe')
        caution_count = sum(1 for r in records if r['risk_level'] == 'caution')
        warning_count = sum(1 for r in records if r['risk_level'] == 'warning')
        
        # 计算各指标平均值
        all_data = [r['data'] for r in records]
        avg_data = {}
        if all_data:
            keys = all_data[0].keys()
            for k in keys:
                vals = [d.get(k, 0) for d in all_data if k in d]
                if vals:
                    avg_data[k] = round(sum(vals) / len(vals), 1)
        
        # 最近5次 vs 前5次，看趋势
        recent = records[-5:] if len(records) >= 5 else records
        prev = records[-10:-5] if len(records) >= 10 else []
        
        trend = {}
        if prev and recent:
            for k in avg_data.keys():
                recent_avg = sum(r['data'].get(k, 0) for r in recent) / len(recent)
                prev_avg = sum(r['data'].get(k, 0) for r in prev) / len(prev)
                diff = recent_avg - prev_avg
                trend[k] = {
                    'recent': round(recent_avg, 1),
                    'previous': round(prev_avg, 1),
                    'change': round(diff, 1)
                }
        
        return {
            'total_records': total,
            'safe_count': safe_count,
            'caution_count': caution_count,
            'warning_count': warning_count,
            'safe_rate': round(safe_count / total * 100, 1) if total > 0 else 0,
            'average_data': avg_data,
            'trend': trend,
            'last_record': records[-1] if records else None
        }
    
    def get_feedback_summary(self, user_id: str) -> str:
        """生成数据反馈摘要（给AI用）"""
        analysis = self.analyze_trend(user_id)
        
        if analysis['total_records'] == 0:
            return '用户还没有训练记录。'
        
        summary = f'用户最近30天共训练{analysis["total_records"]}次。'
        summary += f'安全{analysis["safe_count"]}次，注意{analysis["caution_count"]}次，警告{analysis["warning_count"]}次。'
        summary += f'安全率{analysis["safe_rate"]}%。'
        
        if analysis['trend']:
            summary += '\n趋势变化：'
            for k, v in analysis['trend'].items():
                direction = '变好' if abs(v['recent']) < abs(v['previous']) else '变差'
                summary += f'\n- {k}: 从{v["previous"]}变为{v["recent"]}（{direction}）'
        
        return summary
    
    def _save(self, user_id: str):
        """保存到文件（简化版，实际应该用数据库）"""
        filepath = os.path.join(self.data_dir, f'{user_id}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.cache[user_id], f, ensure_ascii=False, indent=2)
    
    def _load(self, user_id: str):
        """从文件加载"""
        filepath = os.path.join(self.data_dir, f'{user_id}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.cache[user_id] = json.load(f)
