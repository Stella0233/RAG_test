import shutil
from fastapi import FastAPI,UploadFile, File
from fastapi.responses import PlainTextResponse
import functions,filename,tools
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
async def upload_data(file: UploadFile = File(...)):
    #生成文件名
    file_path = filename.get_next_filename()
    # 保存文件到磁盘
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    docs = functions.load_file(file_path)
    chunks = functions.chunk(docs)
    functions.save2db(chunks)
    return {"message": f"{file_path}Successfully processed and saved chunks into Chroma vector DB."}

@app.get("/query",response_class=PlainTextResponse)
async def query(question:str):
    response = tools.agent_executor.run(question)
    return response
