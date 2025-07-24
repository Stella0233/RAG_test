from http.client import HTTPException
from typing import Optional
import shutil
from fastapi import FastAPI,UploadFile, File, Form
from fastapi.responses import JSONResponse
import functions,filename,lg
from fastapi.middleware.cors import CORSMiddleware
from functions import delete_on_tag
# 持久化
from persistence import Persistence
from sqlManager import db,cursor
#
from dotenv import load_dotenv
import os

app = FastAPI()

# 配置 CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3000/file-manager.html"
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

# File Uploading
@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...), tag=Form(...)):
    # 1. 生成保存路径
    file_path = filename.get_next_filename()

    # 2. 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. 加载、切分、入库
    docs = functions.load_file(file_path)
    chunks = functions.chunk(docs)
    functions.save2db(chunks, tag)

    # 4. 保存元数据到 MySQL
    cursor.execute(
        "INSERT INTO uploaded_files (file_name, file_path, tag) VALUES (%s, %s, %s)",
        (file.filename, file_path, tag)
    )
    db.commit()

    return {
        "message": f"{file_path} successfully processed and saved chunks into ChromaDB in '{tag}' collection."
    }


# Query LLM
@app.get("/query", response_class=JSONResponse)
async def query(question: str, tag:Optional[str]=None, style_needed:bool=None,session_id: Optional[str] = "default"):
    # 读取memory
    if not session_id:
        session_id = "default-session"
    # 加载 memory
    memory = Persistence.load_memory(session_id)

    # 拼接用户内容
    input_state = {
        "question": question,
        "history":[],
        "memory":memory,
    }
    if tag:
        input_state["tag"] = tag
    if style_needed:
        input_state["style_needed"] = style_needed

    # 执行 workflow
    result = lg.graph.invoke(input_state)

    #更新memory
    current_round = {"question": question, "answer": result.get("answer", "")}
    memory.append(current_round)
    # 保存 memory 到 redis
    Persistence.save_memory(session_id, memory)

    #测试输出
    print("Final result state:")
    for k, v in result.items():
        print(f"{k}: {v}")

    # 直接返回最终生成的答案
    return {
        "answer": result.get("answer", "No answer generated."),
        "thoughts": result.get("history","No history generated."),
        "origin":result.get("origin","No origin generated.")
    }


# Show filelists
@app.get("/list-files")
def list_uploaded_files(tag: str = None):
    if tag:
        cursor.execute("SELECT id, file_name, upload_time,tag FROM uploaded_files WHERE tag = %s", (tag,))
    else:
        cursor.execute("SELECT id, file_name, upload_time,tag FROM uploaded_files")

    result = cursor.fetchall()
    return [{"id": r[0], "file_name": r[1], "upload_time": r[2].strftime('%Y-%m-%d %H:%M:%S'), "tag":r[3]} for r in result]


# Delete File
@app.delete("/delete-file/{tag}")
def delete_file(tag:str):
    # 2. 删除 ChromaDB 中该 tag 对应的向量数据
    try:
        delete_on_tag(tag)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting vectors: {e}")

    # 3. 删除 MySQL 中记录
    cursor.execute("DELETE FROM uploaded_files WHERE tag = %s", (tag,))
    db.commit()

    return {"message": f"Successfully deleted MySQL record and vector data for tag: {tag}"}
