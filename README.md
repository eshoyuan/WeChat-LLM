# WeChat-LLM: Build LLM to Mimic Your WeChat Style / 根据微信聊天记录定制私人聊天机器人

## 项目简介
WeChat-LLM 是一个基于RAG的聊天机器人, 可以根据微信聊天记录定制模仿你的聊天风格的私人聊天机器人. 尝试使用LoRA对7b/13b的模型进行微调, 发现效果很差, 基于RAG的模型效果更好.

## 使用

### 准备

使用前, 请使用[WeChatMsg](https://github.com/LC044/WeChatMsg)提取微信聊天记录. 导出与特定联系人的聊天记录把数据放在data/raw_data文件夹下. 使用前请配置好OPENAI API.

```
export OPENAI_API_KEY="YOUR_API_KEY"
```

### 安装依赖

```
pip install -r requirements.txt
```

### 清洗数据

```
python scripts/clean_data.py
```

### 开始对话
```
python chat.py
```
