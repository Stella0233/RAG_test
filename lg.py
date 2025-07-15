from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph
from langchain.agents import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
import functions
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

### TOOLS ###
# def rag_tool_query(question:str)->str:
#     matched_text = functions.query_db(question)
#     return functions.answer(question, matched_text)

rag_tool = Tool(
    name = "query_tool",
    func = lambda q: functions.query_db(*q.split(" in ", 1)),
    description = "Use this to answer questions using the user's knowledge base. Format: 'question in <tag>'",
)

tools = [rag_tool]
### TOOLS ###

### Graph ###
# 定义 state
class AgentState(BaseModel):
    messages: List[Dict]

agent_node = create_react_agent(model, tools, prompt="你是一个善于查资料的专家。")

# 定义图状态（你可以带上 memory、历史等）
builder = StateGraph(AgentState)

# 添加 agent 节点
builder.add_node("agent", agent_node)

# 定义流程（单轮）
builder.set_entry_point("agent")

# 构建 graph
graph = builder.compile()
### Graph ###