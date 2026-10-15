# 哮天犬 (XiaoTianQuan / XTQ)

> 🐕 你的数字关节保镖 —— 基于AI视觉的个性化运动防伤评估引擎

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Built%20With-Streamlit-red.svg)

## 项目简介

**哮天犬**是一个开源的运动防伤AI评估引擎，基于人体姿态识别 + 大语言模型，实时分析用户动作中的关节异常受力风险，提供个性化安全预警和AI智能建议。

不同于传统健身App的"计数打卡"逻辑，哮天犬首次将"关节级安全评估"作为核心功能，填补了大众健身领域"防伤预警"的市场空白。

### 核心能力

- 🛡️ **实时防伤预警** —— 基于生物力学参数，实时评估关节异常受力程度
- 👤 **个性化安全基线** —— 根据用户损伤史，动态调整安全阈值，实现"一人一策"
- 🤖 **AI运动顾问** —— 接入大语言模型，智能分析动作并给出调整建议
- 📊 **关节健康趋势报告** —— 记录训练数据，预警慢性劳损风险

## 快速开始（5分钟跑起来）

### 第一步：克隆项目

```bash
git clone https://github.com/jinjujnei3456567/Exercise-Correction.git
cd Exercise-Correction
```

### 第二步：安装依赖

```bash
pip install -r requirements.txt
```

### 第三步：配置AI Token

复制 `.env.example` 为 `.env`，填入你的API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 你的API密钥（必填）
XTQ_API_KEY=你的API密钥

# 默认用豆包，也可以换成其他
XTQ_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
XTQ_MODEL=doubao-pro-4k
```

**支持的AI模型（任选一个）：**

| 平台 | BASE_URL | 模型名 | 申请地址 |
|------|----------|--------|----------|
| 豆包 | `https://ark.cn-beijing.volces.com/api/v3` | `doubao-pro-4k` | 火山引擎控制台 |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | platform.deepseek.com |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-turbo` | 阿里云百炼 |
| OpenAI | `https://api.openai.com/v1` | `gpt-3.5-turbo` | platform.openai.com |

### 第四步：启动！

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`，就能看到哮天犬的界面了！

## 项目结构

```
├── app.py                 # Streamlit桌面应用（主入口）
├── requirements.txt       # Python依赖
├── .env.example           # 环境变量模板
├── xtq/                   # 哮天犬核心引擎
│   ├── __init__.py
│   ├── rule_engine.py     # 防伤规则引擎
│   ├── personalizer.py    # 个性化阈值系统
│   └── ai_advisor.py       # AI大模型顾问
├── rules/                 # 规则库
│   └── squat_rules.json    # 深蹲规则
├── examples/               # 示例代码
│   └── demo_squat.py      # 命令行Demo
└── core/                  # 原始姿态识别代码（来自Exercise-Correction）
```

## 功能说明

### 🛡️ 防伤规则引擎

规则库的知识来源：
- PubMed、知网等学术数据库中的生物力学与运动康复文献
- 运动康复临床指南和关节活动度国际标准
- 经运动科学专业教师和临床护理医师双重审核

### 深蹲防伤规则示例

| 监测指标 | 安全范围 | 注意范围 | 警告范围 | 关联损伤风险 |
|---------|---------|---------|---------|-------------|
| 膝关节屈曲角 | 80°-120° | 120°-135°或60°-80° | >135°或<60° | 半月板后角挤压、髌股关节压力增大 |
| 膝-踝联动偏移 | <10° | 10°-20° | >20° | 髌股关节综合征、前交叉韧带损伤 |
| 躯干前倾角 | 30°-50° | 50°-65°或20°-30° | >65°或<20° | 腰椎间盘压力增大、下背部劳损 |

### 👤 个性化阈值系统

| 用户损伤史 | 涉及动作 | 标准阈值 | 个性化阈值 | 调整依据 |
|-----------|---------|---------|-----------|----------|
| 半月板术后（<6个月） | 深蹲 | 膝关节屈曲≤130° | 膝关节屈曲≤90° | 术后康复指南：避免深度屈膝 |
| 前交叉韧带重建术后 | 深蹲 | 膝-踝偏移<10° | 膝-踝偏移<5° | 移植物保护 |
| 腰椎间盘突出 | 硬拉 | 腰椎屈曲≤58° | 腰椎屈曲≤40° | 腰椎负荷研究（L4-L5/L5-S1） |

### 🤖 AI运动顾问

接入大语言模型后，哮天犬会：
- 自动分析你的动作数据，给出通俗易懂的调整建议
- 结合你的损伤史，提醒需要注意的部位
- 随时回答你的运动健身问题

## 支持动作

| 动作 | 状态 | 监测指标数 |
|------|------|-----------|
| 深蹲 (Squat) | ✅ V1.0 | 3项 |
| 硬拉 (Deadlift) | 🚧 开发中 | 规划12项 |
| 卧推 (Bench Press) | 🚧 开发中 | 规划10项 |

## 开发路线图

- [x] 防伤规则引擎核心
- [x] 个性化阈值系统
- [x] AI大模型顾问
- [x] Streamlit桌面界面
- [ ] 摄像头实时姿态识别对接
- [ ] 硬拉/卧推规则库
- [ ] 关节健康趋势周报
- [ ] 移动端适配

## 开源说明

本项目基于 [Exercise-Correction](https://github.com/NgoQuocBao1010/Exercise-Correction)（MIT License）进行二次开发。

- **骨架识别层**：基于 MediaPipe Pose（Apache 2.0 License）
- **防伤规则引擎**：哮天犬团队原创，MIT License 开源

## 团队

- 项目：护动智眸 —— 基于AI视觉的个性化运动防伤评估系统
- 赛道：互联网+大学生创新计划 · 职教赛道创意组
- 学校：合肥幼儿师范高等专科学校

## License

[MIT](LICENSE)
