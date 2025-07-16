from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph
from langchain.agents import Tool
import functions,models


### TOOLS ###
#langchain tool只能接受一个传参
def rag_query(input_text:str)->str:
    #解析tag
    if "tag=" in input_text:
        question_part, tag_part = input_text.split("tag=", 1)
        question = question_part.strip()
        tag = tag_part.strip()
    else:
        return "Error: Missing 'tag=' in the input"
    #调用functions
    contexts = functions.query_db(question,tag)
    return functions.answer(question,contexts)

rag_tool = Tool(
    name="KnowledgeBaseSearch",
    description="Use this tool to answer knowledge base questions. Input format: '<question>\\n tag=<tag>'",
    func=rag_query
)
tools = [rag_tool]
### TOOLS ###


### Graph ###
# 定义 Agent（包含工具、模型）
graph = create_react_agent(
    tools=[rag_tool],
    model=models.model,
    prompt=("You are a helpful assistant. Use tools if needed to search the knowledge base."
            "If a user's question may involve specialized, factual, or detailed knowledge, "
            "always use tools to find answers from the knowledge base."
            )
)
### Graph ###