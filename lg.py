from fontTools.merge.base import mergeObjects
from langgraph.graph import StateGraph
from langchain.tools import tool
from langchain_core.runnables import RunnableLambda
from typing import TypedDict, Optional, List, Dict
from functions import query_db,answer_with_context,answer_without_context,judge_answer,trace,call_query_rewriter,stylize
from logger import logger


#在节点之间传递数据
class RAGState(TypedDict):
    #basic
    question: str
    tag:Optional[str]
    context: Optional[List[str]]
    answer: Optional[str]
    #pro
    style_needed:bool
    # style_answer: Optional[str] #风格化回答
    reflection_count: int #判断回答是否合格
    reflecting:bool
    history: List[str] #思考过程
    origin: str #原文溯源
    memory: List[Dict[str, str]]


@tool
def query_knowledge_base(question: str, tag: str) -> List[str]:
    """
        查询向量数据库并基于上下文生成答案。输入为问题和对应的知识库标签。
        """
    return query_db(question, tag)

# Rewrite Query Node
def rewrite_question_node(state: RAGState) -> RAGState:
    logger.debug("I'm questio rewriting node")
    #
    memory = state.get("memory", [])
    question = state["question"]
    #
    rewritten = call_query_rewriter(question)
    state["history"].append(f"Rewrited question:{rewritten}")
    return {**state, "question": rewritten}

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
    return {**state, "context": context, "tag":None} #查完库之后要重置tag\

# Answer Node
def answer_node(state: RAGState) -> RAGState:
    logger.debug("I'm answer node")
    state["history"].append("Answering...")
    #
    question = state["question"]
    context = state.get("context", [])
    memory = state.get("memory", [])
    print(context)
    #
    if(context == []):
        logger.debug("I'm answer without context")
        answer = answer_without_context(question,memory)
    else:
        logger.debug("I'm answer with context")
        answer = answer_with_context(question, context,memory)
    return {**state, "answer": answer}

# Origin Node
def origin_node(state: RAGState) -> RAGState:
    logger.debug("I'm origin node")
    #
    answer = state["answer"]
    context = state["context"]
    # 没有context不需要溯源
    if (context == []):
        return state
    #溯源
    state["history"].append("Originating...")
    origin_sentences = trace(answer, context)
    logger.debug(origin_sentences)
    return {**state, "origin": origin_sentences}

# Reflection Node
def reflection_node(state: RAGState) -> str:
    logger.debug("I'm reflection node")
    state["history"].append("Reflecting...")
    count = state.get("reflection_count", 0)
    #
    style_needed = state.get("style_needed", False)
    answer = state["answer"]
    question = state["question"]
    #
    response = judge_answer(question, answer)
    logger.debug(f"Reflection Response: {response}, Count: {count}")

    if(response == "no" and count < 2):
        # 重新回答
        state["reflection_count"] = count + 1
        state["reflecting"] = True  # 你可以用这个标记告诉 answer node 这是反思过程中的回答
        return {"next": "answer_node"}
    elif(style_needed):
        # 公文输出流程
        state["reflecting"] = False
        return {"next": "style_node"}
    else:
        # 结束流程
        state["reflecting"] = False
        return {"next": "end_node"}

# Style Node
def style_node(state: RAGState) -> RAGState:
    logger.debug("I'm style node")
    state["history"].append("Stylizng...")
    answer = state["answer"]
    style_answer = stylize(answer)
    return {**state, "answer": style_answer}

# end node（即使是空的）
def end_node(state: RAGState) -> RAGState:
    logger.debug("Reached end node")
    return state


### Workflow ###
workflow = StateGraph(RAGState)

# 添加节点
workflow.add_node("rewrite_question_node", rewrite_question_node)
workflow.add_node("agent_node", agent_node)
workflow.add_node("query_node", query_node)
workflow.add_node("answer_node", answer_node)
workflow.add_node("reflection_node", reflection_node)
workflow.add_node("origin_node",origin_node)
workflow.add_node("style_node",style_node)
workflow.add_node("end_node", end_node)

# 添加边
# entry
workflow.set_entry_point("rewrite_question_node")
# rewrite_question_node -> agent node
workflow.add_edge("rewrite_question_node", "agent_node")
# agent_node -> query_node | answer_node
workflow.add_conditional_edges(
    "agent_node",
    lambda state: agent_decision_node(state)["next"],  # 返回字符串
    {
        "query_node": "query_node",
        "answer_node": "answer_node"
    }
)
# query_node -> answer_node
workflow.add_edge("query_node", "answer_node")
# answer_node -> origin_node
workflow.add_edge("answer_node", "origin_node")
# oringin_node -> reflection_node
workflow.add_edge("origin_node", "reflection_node")
# reflection_node -> answer_node | style_node | end_node
workflow.add_conditional_edges(
    "reflection_node",
    lambda state: reflection_node(state)["next"],
    {
        "answer_node": "answer_node",
        "style_node": "style_node",
        "end_node": "end_node"
    }
)
#style_node -> end_node
workflow.add_edge("style_node", "end_node")
# exit
workflow.set_finish_point("end_node")

# 编译成 Graph
graph = workflow.compile()


