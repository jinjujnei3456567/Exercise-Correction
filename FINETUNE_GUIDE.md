# 哮天犬自研模型微调教程

## 路线
Qwen2.5-1.5B-Instruct → LoRA微调 → 哮天犬模型 → Ollama部署

## 第一步：租GPU
去 AutoDL 租个 3090，选 PyTorch 镜像，大概5块钱够了

## 第二步：装 LLaMA-Factory
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e .

## 第三步：准备数据
把 data/train.jsonl 放到 data/ 目录

## 第四步：开始微调
llamafactory-cli webui
然后网页上选 Qwen2.5-1.5B，选数据集，点开始

## 第五步：部署
训练完导出，用 Ollama 跑起来

## 总成本
约10块钱
