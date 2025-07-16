from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from typing import List
import models

### Ingestion ###
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
def save2db(chunks:list[Document],tag:str) -> None:
    documents = [Document(page_content=chunk) for chunk in chunks]
    vectorstore = Chroma.from_documents(
        documents,
        models.embedding,
        persist_directory="./chroma_db",
        collection_name= tag,
    )
    print(f"Saved {len(documents)} chunks in ChromaDB.")

### Retrieval ###
#查知识库
def query_db(question: str, tag:str) -> List[str]:
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=models.embedding,collection_name=tag)
    results: List[Document] = vectorstore.similarity_search(question, k=5)
    return [doc.page_content for doc in results]

#生成回答
def answer(question: str, contexts: List[str]) -> str:
    prompt = "You are an assistant that answers questions based on the provided context.\n\n"
    prompt += f"Question: {question}\n\nContext:\n"
    for text in contexts:
        prompt += text + "\n---\n"

    response = models.model.invoke([{"role": "user", "content": prompt}])
    return response["content"] if isinstance(response, dict) else response.content

#直接询问模型
def answer_without_context(question: str) -> str:
    prompt = "You are a knowledgable professor,please answer the question:\n\n"
    prompt += f"Question: {question}\n"
    response = models.model.invoke([{"role": "user", "content": prompt}])
    return response["content"] if isinstance(response, dict) else response.content
