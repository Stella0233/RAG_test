import shutil
from fastapi import FastAPI,UploadFile, File, Form
from fastapi.responses import PlainTextResponse
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

@app.get("/query",response_class=PlainTextResponse)
async def query(question:str):
    try:
        response = lg.graph.invoke({"messages": [{"role": "user", "content": question}]})
        last_message = next(
            (msg for msg in reversed(response["messages"]) if msg["role"] == "assistant"),
            {"content": "No answer generated."}
        )
        return {"answer": last_message["content"]}
    except Exception as e:
        import traceback
        traceback.print_exc()  # 打印详细异常信息
        return PlainTextResponse("Internal Server Error", status_code=500)

