from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader
# from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
#文本分割器，langchain的
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)


#数据文本加载
def load_file(file_path: str) -> list[Document]:
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    return docs

#分块
def chunk(docs:str) ->list[Document]:
    chunks = []
    for doc in docs:
        chunks.extend(text_splitter.split_text(doc.page_content))
    print(f"{chunks[0]}")
    return chunks

#save to db
def save2db(chunks:list[Document]) -> None:
    documents = [Document(page_content=chunk) for chunk in chunks]
    vectorstore = Chroma.from_documents(documents, embedding, persist_directory="./chroma_db")
    print(f"Saved {len(documents)} chunks to Chroma DB.")

#查知识库
def query_db(question:str):
    # 加载已有的向量数据库
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding)
    # Top-k 条内容
    results = vectorstore.similarity_search(question, k=5)
    # 返回内容
    matched_texts = [doc.page_content for doc in results]
    return matched_texts

#生成回答答案
def answer(question:str, matched_texts:list[str]) -> str:
    #写提示词
    prompt = ""
    prompt += "According to the context, answer the question."
    prompt += "question:\n" + question + "\ncontext:"
    for text in matched_texts:
        prompt += "\n" + text
        prompt +="____________\n"
    #生成回答
    response = model.invoke([
        {"role": "user", "content": prompt}
    ])
    return response.content
