from langgraph.graph import StateGraph
from langchain.tools import tool
from langchain_core.runnables import RunnableLambda
from typing import TypedDict, Optional, List
from functions import query_db,answer_with_context,answer_without_context,judge_answer
from logger import logger
from models import model

#在节点之间传递数据
class RAGState(TypedDict):
    question: str
    tag:Optional[str]
    context: Optional[List[str]]
    answer: Optional[str]
    reflection_count: int #判断是否合格
    reflecting:bool
    history: List[str]


@tool
def query_knowledge_base(question: str, tag: str) -> List[str]:
    """
        查询向量数据库并基于上下文生成答案。输入为问题和对应的知识库标签。
        """
    return query_db(question, tag)

# Decision Node
def agent_decision_node(state: RAGState) -> dict:
    logger.debug("I'm decision node")
    state["history"].append("Decision being made...")
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
    state["history"].append("Querying...")
    question = state["question"]
    tag = state["tag"]
    context = query_knowledge_base.invoke({"question": question, "tag": tag})
    return {**state, "context": context, "tag":None} #查完库之后要重置tag

# Answer Node
def answer_node(state: RAGState) -> RAGState:
    logger.debug("I'm answer node")
    state["history"].append("Answering...")
    question = state["question"]
    context = state.get("context", [])
    print(context)
    if(context == []):
        logger.debug("I'm answer without context")
        answer = answer_without_context(question)
    else:
        logger.debug("I'm answer with context")
        answer = answer_with_context(question, context)
    return {**state, "answer": answer}

# Reflection Node
def reflection_node(state: RAGState) -> str:
    logger.debug("I'm reflection node")
    state["history"].append("Reflecting...")
    count = state.get("reflection_count", 0)
    answer = state["answer"]
    question = state["question"]
    response = judge_answer(question, answer)
    logger.debug(f"Reflection Response: {response}, Count: {count}")

    if(response == "no" and count < 2):
        # 重新回答
        state["reflection_count"] = count + 1
        state["reflecting"] = True  # 你可以用这个标记告诉 answer node 这是反思过程中的回答
        return {"next": "answer_node"}
    else:
        # 结束流程
        state["reflecting"] = False
        return {"next": "end_node"}

# end node（即使是空的）
def end_node(state: RAGState) -> RAGState:
    logger.debug("Reached end node")
    return state


### Workflow ###
workflow = StateGraph(RAGState)

# 添加节点
workflow.add_node("agent_node", agent_node)
workflow.add_node("query_node", query_node)
workflow.add_node("answer_node", answer_node)
workflow.add_node("reflection_node", reflection_node)
workflow.add_node("end_node", end_node)

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
workflow.add_edge("answer_node", "reflection_node")
##
workflow.add_conditional_edges(
    "reflection_node",
    lambda state: reflection_node(state)["next"],
    {
        "answer_node": "answer_node",
        "end_node": "end_node",
    }
)
# 设置出口
workflow.set_finish_point("end_node")

# 编译成 Graph
graph = workflow.compile()


