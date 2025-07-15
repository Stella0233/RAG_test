import os
import re

UPLOAD_DIR = "documents"
BASENAME = "data"
EXT = ".txt"

def get_next_filename() -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    existing_files = os.listdir(UPLOAD_DIR)

    # 匹配形如 data_x.txt 的文件
    pattern = re.compile(rf"{BASENAME}_(\d+){EXT}")

    numbers = []
    for filename in existing_files:
        match = pattern.match(filename)
        if match:
            numbers.append(int(match.group(1)))

    next_number = max(numbers, default=0) + 1
    return os.path.join(UPLOAD_DIR, f"{BASENAME}_{next_number}{EXT}")