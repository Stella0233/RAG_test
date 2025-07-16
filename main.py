import shutil
import uvicorn
from langchain_core.messages import AIMessage
from fastapi import FastAPI,UploadFile, File, Form
from fastapi.responses import JSONResponse
import functions,filename,lg
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
async def query(question: str, tag:str):
    result = lg.graph.invoke({
        "messages": [
            {"role": "system", "content": "Always use tools to search the knowledge base for any factual or technical question."},
            {"role": "user", "content": question + "\n tag="+tag}
        ]
    })

    #后台检查报错用
    for msg in result["messages"]:
        print(type(msg), msg)

    # 修复：使用属性访问
    last_message = next(
        (msg for msg in reversed(result["messages"]) if isinstance(msg, AIMessage)),
        None
    )

    return {"answer": last_message.content}

# if __name__ == '__main__':
#     uvicorn.run(app, port=8000)
