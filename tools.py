from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
import functions
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

def rag_tool_query(question:str)->str:
    matched_text = functions.query_db(question)
    return functions.answer(question, matched_text)

rag_tool = Tool(
    name = "query tool",
    func = rag_tool_query,
    description = "query tool",
)

agent_executor = initialize_agent(
    tools = [rag_tool],
    llm = model,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # 或 conversational agent
    verbose=True
)