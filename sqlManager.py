import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
db_password = os.getenv("DB_PASSWORD")

# 建立数据库连接（建议提取到单独模块中做连接池）
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=db_password,
    database="agentic_rag"
)
cursor = db.cursor()