from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader

# 设置api
# GEMINI_API_KEY = "AIzaSyCaKJz9COcvs3iKupbkZ-sDNmBJ0g7-KXQ"
# 引入LLM model和embedding
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
#文本分割器，langchain的
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)

#数据文本加载
def load_file() -> list[Document]:
    loader = TextLoader("documents\\data.txt",encoding="utf-8")
    docs = loader.load()
    return docs

#分块
def chunk(docs:str) ->list[Document]:
    chunks = []
    for doc in docs:
        chunks.extend(text_splitter.split_text(doc.page_content))
    print(f"{chunks[0]}")
    return chunks

# #embedding
# def embed(chunks:list[str])->list[float]:
#     vectors = embeddings.embed_documents(chunks)
#     return vectors

#save to db
def save2db(chunks:list[Document]) -> None:
    documents = [Document(page_content=chunk) for chunk in chunks]
    vectorstore = Chroma.from_documents(documents, embedding, persist_directory="./chroma_db")
    # vectorstore.persist()
    print(f"Saved {len(documents)} chunks to Chroma DB.")

if __name__ == "__main__":
    docs = load_file()
    chunks = chunk(docs)
    save2db(chunks)
