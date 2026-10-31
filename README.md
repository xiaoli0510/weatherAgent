# 🌤️ WeatherAgent - 智能天气助手

这是一个基于 Python、LangChain 和通义千问（Qwen）大模型开发的天气查询智能体（Agent）学习项目。

本项目记录了从“底层手写 ReAct 循环”到“使用最新 Agent 框架封装”的演进过程，旨在深入理解 LLM Agent 的思考逻辑、工具调用机制以及多轮对话的内存管理。

## 🛠️ 技术栈

*   **语言**: Python 3.11+
*   **核心框架**: LangChain (v1.x), LangGraph
*   **大模型**: 阿里云通义千问 (通过 `langchain-openai` 兼容接口调用)
*   **外部 API**: 基于 `wttr.in` 的免费天气查询接口
*   **环境管理**: `python-dotenv` (环境变量隔离)

## 📂 项目结构
    weatherAgent/
    ├── weather_one/
    │   ├── weather01.py    # 纯手工实现 ReAct 循环（深入理解 tool_calls 机制）
    │   └── weather02.py    # 使用 create_agent 构建，支持多轮对话与历史维护
    ├── .env                # 本地环境变量（存放 API Key，已被 Git 忽略）
    ├── .gitignore          # Git 忽略规则（忽略 .venv, .env, __pycache__ 等）
    └── requirements.txt    # 项目依赖清单

## 🌟 核心亮点与设计思路
1. 深入底层：手写 ReAct 循环 (weather01.py)
没有完全依赖开箱即用的框架，而是通过手动维护 messages 列表，结合 llm.bind_tools() 和 ToolMessage，实现了一个完整的 Think -> Act -> Observe 循环。

深入理解了 LLM 是如何通过 tool_calls 发起指令，以及如何将工具结果通过 tool_call_id 塞回上下文。

2. 工程封装：多轮对话与状态维护 (weather02.py)
基于 LangGraph 的 create_agent 快速搭建智能体，并通过自定义的 WeatherChat 类实现了优雅的多轮对话管理。

完美实现了 quit（退出）和 clear（清空历史记录）的终端交互逻辑。

通过系统提示词（System Prompt）规范了 Agent 的边界（只聊天气、超温给建议、不胡编乱造）。

3. 鲁棒性与异常兜底
天气 API 请求增加了 timeout 超时控制和 try-except 异常捕获。如果外部网络不通或请求超时，会自动返回本地模拟的兜底数据，保证程序不会直接崩溃，提升了用户体验。

## 🚀 如何运行
第一步：克隆并安装依赖
确保你已激活虚拟环境，然后在项目根目录执行：

bash
git clone https://github.com/xiaoli0510/weatherAgent.git
cd weatherAgent
```bash
pip install -r requirements.txt
```
第二步：配置环境变量
在项目根目录下创建一个名为 .env 的文件，填入你的阿里云百炼 API Key 和相关配置：

env
# .env 文件内容示例
DASHSCOPE_API_KEY="sk-你的真实API_KEY"   
DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"   
DASHSCOPE_MODEL="qwen-max"  
(注：本项目默认通过通义千问的 OpenAI 兼容接口进行调用)

第三步：启动交互终端
运行主程序即可体验智能对话：

```bash
python  python .\weather_one\weather02.py
```
终端操作指令：

输入常规问题（如：北京今天天气怎么样）进行对话。

输入 clear 清空当前的对话历史，重新开始。

输入 quit 或 exit 退出程序。

💡 学习记录：从手写循环到框架封装的 AI 探索之旅。