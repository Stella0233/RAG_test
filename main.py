from typing import Optional
import shutil
from pprint import pprint
from langchain_core.messages import AIMessage
from fastapi import FastAPI,UploadFile, File, Form
from fastapi.responses import JSONResponse
import functions,filename,lg
from logger import logger
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

app = FastAPI()

# 配置 CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...),tag=Form(...)):
    #生成文件名
    file_path = filename.get_next_filename()
    # 保存文件到磁盘
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    docs = functions.load_file(file_path)
    chunks = functions.chunk(docs)
    functions.save2db(chunks,tag)
    return {"message": f"{file_path}Successfully processed and saved chunks into ChromaDB in {tag} collection."}

from fastapi.responses import PlainTextResponse


@app.get("/query", response_class=JSONResponse)
async def query(question: str, tag:Optional[str]=None):
    # 拼接用户内容
    input_state = {
        "question": question,
        "history":[]
    }
    if tag:
        input_state["tag"] = tag

    # 执行 workflow
    result = lg.graph.invoke(input_state)
    print("Final result state:")
    for k, v in result.items():
        print(f"{k}: {v}")

    # 直接返回最终生成的答案
    return {
        "answer": result.get("answer", "No answer generated."),
        "thoughts": result.get("history","No history generated.")
    }

