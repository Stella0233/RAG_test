from typing import Dict, List
import redis
import json

class Persistence:
    # 创建 Redis 客户端
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    # 定义保存 memory 的函数
    def save_memory(session_id: str, memory: List[Dict[str, str]]):
        Persistence.r.set(f"memory:{session_id}", json.dumps(memory),ex=600)

    # 定义加载 memory 的函数
    def load_memory(session_id: str) -> List[Dict[str, str]]:
        raw = Persistence.r.get(f"memory:{session_id}")
        if raw:
            return json.loads(raw)
        return []
