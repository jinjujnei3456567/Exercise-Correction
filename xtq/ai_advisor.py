"""
哮天犬 AI顾问 - 接入大语言模型，提供智能运动建议

支持：OpenAI兼容接口（豆包/通义千问/OpenAI/DeepSeek等）
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class AIAdvice:
    """AI建议结果"""
    success: bool
    content: str = ""
    error: str = ""
    model: str = ""


class AIAdvisor:
    """
    AI运动顾问 - 基于大语言模型提供个性化运动建议
    
    配置方式（环境变量 .env 文件）：
        XTQ_API_KEY=your_api_key_here
        XTQ_BASE_URL=https://ark.cn-beijing.volces.com/api/v3  # 豆包
        XTQ_MODEL=doubao-pro-4k
    
    也支持直接传参初始化
    """
    
    # 支持的厂商预设
    PRESETS = {
        'doubao': {
            'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
            'model': 'doubao-pro-4k',
            'name': '豆包大模型'
        },
        'deepseek': {
            'base_url': 'https://api.deepseek.com/v1',
            'model': 'deepseek-chat',
            'name': 'DeepSeek'
        },
        'openai': {
            'base_url': 'https://api.openai.com/v1',
            'model': 'gpt-3.5-turbo',
            'name': 'OpenAI GPT'
        },
        'qwen': {
            'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'model': 'qwen-turbo',
            'name': '通义千问'
        }
    }
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        初始化AI顾问
        
        Args:
            api_key: API密钥（token）
            base_url: API地址（可选，有默认值）
            model: 模型名称（可选）
        """
        self.api_key = api_key or os.getenv('XTQ_API_KEY', '')
        self.base_url = base_url or os.getenv('XTQ_BASE_URL', '')
        self.model = model or os.getenv('XTQ_MODEL', '')
        
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """初始化OpenAI客户端"""
        if not self.api_key:
            print("[哮天犬AI] 未配置API Key，AI顾问功能不可用")
            print("[哮天犬AI] 请在 .env 文件中配置 XTQ_API_KEY")
            return
        
        if not self.base_url:
            # 默认用豆包
            self.base_url = self.PRESETS['doubao']['base_url']
            print(f"[哮天犬AI] 未配置BASE_URL，使用默认：豆包")
        
        if not self.model:
            self.model = self.PRESETS['doubao']['model']
        
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            print(f"[哮天犬AI] 连接成功，模型：{self.model}")
        except Exception as e:
            print(f"[哮天犬AI] 初始化失败：{e}")
            self.client = None
    
    def is_ready(self) -> bool:
        """检查AI是否就绪"""
        return self.client is not None
    
    def analyze_posture(self, exercise: str, risk_result, 
                        user_profile: Dict = None) -> AIAdvice:
        """
        分析动作并给出AI建议
        
        Args:
            exercise: 动作名称
            risk_result: RuleEngine的RiskResult对象
            user_profile: 用户画像（损伤史等）
        
        Returns:
            AIAdvice: AI建议
        """
        if not self.client:
            return AIAdvice(
                success=False,
                error="AI未配置，请先设置API Key"
            )
        
        # 构造提示词
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(exercise, risk_result, user_profile)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            advice = response.choices[0].message.content
            return AIAdvice(
                success=True,
                content=advice,
                model=self.model
            )
        except Exception as e:
            return AIAdvice(
                success=False,
                error=f"API调用失败：{str(e)}"
            )
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是「哮天犬」，一位专业的运动防伤AI顾问。

你的职责：
1. 根据用户的动作风险数据，给出通俗易懂的调整建议
2. 用鼓励但专业的语气，不要吓人
3. 建议要具体、可操作，不要空泛
4. 结合用户的损伤史给出个性化提醒
5. 控制在150字以内，重点突出

输出格式：
- 先一句话总结当前动作状态
- 然后列出1-3条具体调整建议
- 最后一句鼓励的话

注意：你不是医生，严重问题建议就医。"""
    
    def _build_user_prompt(self, exercise: str, risk_result, 
                           user_profile: Dict = None) -> str:
        """构建用户提示词"""
        exercise_names = {
            'squat': '深蹲',
            'deadlift': '硬拉',
            'bench_press': '卧推'
        }
        exercise_name = exercise_names.get(exercise, exercise)
        
        prompt = f"""动作类型：{exercise_name}
当前风险等级：{risk_result.level.value}
评估提示：{risk_result.message}

详细指标：
"""
        
        for key, value in risk_result.details.items():
            prompt += f"- {key}: {value}°\n"
        
        if risk_result.indicators:
            prompt += "\n异常指标：\n"
            for alert in risk_result.indicators:
                prompt += f"- {alert['indicator']}: {alert['value']}° ({alert['level']})，关联风险：{alert['injury_risk']}\n"
        
        if user_profile and user_profile.get('injuries'):
            prompt += "\n用户损伤史：\n"
            for injury in user_profile['injuries']:
                prompt += f"- {injury.get('condition', '未知')}\n"
        
        prompt += "\n请给出你的专业建议。"
        
        return prompt
    
    def chat(self, message: str) -> AIAdvice:
        """
        自由对话模式
        
        Args:
            message: 用户消息
        
        Returns:
            AIAdvice: AI回复
        """
        if not self.client:
            return AIAdvice(
                success=False,
                error="AI未配置，请先设置API Key"
            )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是哮天犬，运动防伤AI顾问，用简洁友好的语气回答用户关于运动健身和损伤预防的问题。"},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return AIAdvice(
                success=True,
                content=response.choices[0].message.content,
                model=self.model
            )
        except Exception as e:
            return AIAdvice(
                success=False,
                error=f"API调用失败：{str(e)}"
            )
