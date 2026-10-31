"""
实现一个手工的ReAct循环
1. 获取天气
2. 调用model
"""
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import requests
from langchain_core.messages import HumanMessage,AIMessage, ToolMessage
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
       url=f"https://wttr.in/{city}?format=j1&lang=zh"
       resp = requests.get(url, timeout = 10, headers={"User-Agent": "curl/7.68.0"})
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
tool_map={t.name: t for t in tools}


# 初始化agent并绑定工具
llm = ChatOpenAI(
    model = os.getenv("DASHSCOPE_MODEL"),
    base_url = os.getenv("DASHSCOPE_BASE_URL"),
    temperature = 0
)

llm_with_tools = llm.bind_tools(tools)


# React 循环(核心)
def run_agent(user_input:str, verbose: bool = True) -> str:
    messages = [HumanMessage(content=user_input)]
    for step in range(5):
        response:AIMessage = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            # 没有调用工具时，直接返回内容
            return response.content

        if verbose:
            for tc in response.tool_calls:
                print(f"{type(tc).__name__} tc:{tc}")
                print(f" [步骤{step+1}] 调用工具:{tc['name']},参数：{json.dumps(tc['args'], ensure_ascii=True)}")

        for tc in response.tool_calls:
            # 获取工具调用的结果
            tool_result = tool_map[tc["name"]].invoke(tc["args"])
            if verbose:
                print(f"{type(tool_result).__name__} tool_result:{tool_result}")
                print(f" [步骤{step+1}] 工具返回：{str(tool_result)[:60]}...")
            messages.append(ToolMessage(content = str(tool_result), tool_call_id=tc["id"]))
    return "处理次数超限，请换个问题"

if __name__ == '__main__':

   print("*"*20)
   for q in ["北京今天天气怎么样", "长沙现在热不热"]:
       res = run_agent(q)
       print(f"\n 你：{q}")
       print(f"\n 助手：{res}")
       print("*"*20)




