"""
实现天气的多轮对话
* 基于weather01的基础上使用agent

"""
import os
import json

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import requests
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from dotenv import load_dotenv

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """
    查询指定城市的当前天气
    :param city:城市名称
    :return: 天气
    """
    try:
        url = f"https://wttr.in/{city}?format=j1&lang=zh"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "curl/7.68.0"})
        # 检查是否调用成功，有异常会被except捕获到
        resp.raise_for_status()
        data = resp.json()
        current = data["current_condition"][0]
        area = data["nearest_area"][0]

        return (
            f"【{area['areaName'][0]['value']}天气】\n"
            f"天气：{current['weatherDesc'][0]['value']}\n"
            f"温度：{current['temp_C']}℃ (体感{current['FeelsLikeC']})\n"
            f"湿度：{current['humidity']}%\n"
            f"风速：{current['windspeedKmph']}km/h"
        )

    except Exception as e:
        return (
            f"【{city}天气】 (模拟数据，网络不通时显示) \n"
            f"天气：晴， 温度：22℃， 湿度：62%， 风速：13km/h"
        )


tools = [get_weather]
tool_map = {t.name: t for t in tools}

# 初始化agent并绑定工具
llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0
)

"""
提示词：
1. 工具的使用，避免ai的幻觉
2. 用户体验
3. 不知道的就去问用户，避免ai幻觉
4. 边界的限定
"""
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
      你是天气小助手，专业友好：
         1. 问天气必须使用get_weather工具：不要编造
         2. 回答简洁自然，根据温度给穿衣建议(<10度保暖，>30度避暑)
         3. 用户没说城市时礼貌询问
         4. 非天气问题礼貌说明你主要提供天气服务
    """
)

class WeatherChat:
    """多轮对话会话，自己维护消息历史"""
    def __init__(self):
        self.messages = []

    def send(self, user_input:str) -> str:
        self.messages.append(HumanMessage(content=user_input))
        result = agent.invoke({"messages": self.messages})
        self.messages = result["messages"]
        return self.messages[-1].content

    def clear(self):
        self.messages = []


if __name__ == '__main__':
    print("*"*20)
    print("天气助手 进阶版(多轮对话版)")
    print("命令： quit 退出 | clear 清空对话")
    print("*"*20)

    chat = WeatherChat()
    # 使用while实现多轮，由user自主决定是否退出|清空
    while True:
        user_input=input("\n你：").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("再见啦")
            break
        if user_input.lower() == "clear":
            chat.clear()
            print("对话已经清空，重新开始~")
            continue

        answer = chat.send(user_input)
        print(f"助手：{answer}")
