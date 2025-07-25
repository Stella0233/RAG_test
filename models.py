from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import DashScopeEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
embedding_key = os.getenv("ALI_API_KEY")

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
)

embedding = DashScopeEmbeddings(model="text-embedding-v1",dashscope_api_key=embedding_key)

# # embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
# embedding = HuggingFaceEmbeddings(
#     model_name="BAAI/bge-small-zh",  # 或者 bge-base-zh
#     # model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
#     encode_kwargs={"normalize_embeddings": True}
# )