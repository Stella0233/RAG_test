from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph
from langchain.agents import Tool
from langchain.tools import tool
from langchain_core.runnables import RunnableLambda
from typing import TypedDict, Optional, List
import functions,models
from logger import logger
import matplotlib.pyplot as plt

from functions import answer


#在节点之间传递数据
class RAGState(TypedDict):
    question: str
    tag:Optional[str]
    context: Optional[List[str]]
    answer: Optional[str]


@tool
def query_knowledge_base(question: str, tag: str) -> List[str]:
    """
        查询向量数据库并基于上下文生成答案。输入为问题和对应的知识库标签。
        """
    return functions.query_db(question, tag)

# Decision Node
def agent_decision_node(state: RAGState) -> dict:
    logger.debug("I'm decision node")
    # tag = state["tag"]
    tag = state.get("tag")
    # 有tag时
    if(tag is not None):
        return {"next": "query_node"}  # 跳转到 query_knowledge_base
    else:
        return {"next": "answer_node"}  # 直接回答

agent_node = RunnableLambda(agent_decision_node)

# Tool Node
def query_node(state: RAGState) -> RAGState:
    logger.debug("I'm query node")
    question = state["question"]
    tag = state["tag"]
    context = query_knowledge_base.invoke({"question": question, "tag": tag})
    return {**state, "context": context, "tag":None} #查完库之后要重置tag

# Answer Node
def answer_node(state: RAGState) -> RAGState:
    logger.debug("I'm answer node")
    question = state["question"]
    context = state.get("context", [])
    print(context)
    if(context == []):
        logger.debug("I'm answer without context")
        answer = functions.answer_without_context(question)
    else:
        logger.debug("I'm answer with context")
        answer = functions.answer(question, context)
    return {**state, "answer": answer}

### Workflow ###
workflow = StateGraph(RAGState)

# 添加节点
workflow.add_node("agent_node", agent_node)
workflow.add_node("query_node", query_node)
workflow.add_node("answer_node", answer_node)

# 添加边：从 agent → decision
workflow.set_entry_point("agent_node")
workflow.add_conditional_edges(
    "agent_node",
    lambda state: agent_decision_node(state)["next"],  # 返回字符串
    {
        "query_node": "query_node",
        "answer_node": "answer_node"
    }
)

workflow.add_edge("query_node", "answer_node")

# 设置出口
workflow.set_finish_point("answer_node")

# 编译成 Graph
graph = workflow.compile()


