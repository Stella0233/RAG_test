import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 设置日志级别

# 创建一个控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 创建一个文件处理器
file_handler = logging.FileHandler('debug.log')
file_handler.setLevel(logging.DEBUG)

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 添加处理器到logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# # 使用
# logger.debug("I'm answer node")