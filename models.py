from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
)

embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
# embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh")