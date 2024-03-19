# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  IDE         : PyCharm
  File Name   : logging
  Description : 
  Summary     : 1、
                2、
                3、
  Author      : chenyushencc@gmail.com
  date        : 2024/3/19 20:17
-------------------------------------------------
"""
import logging


# 配置日志记录器
logging.basicConfig(filename='my_logging.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


# 在日志中记录 print 输出内容
class LoggerWriter:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message != '\n':
            logging.log(self.level, message)

    def flush(self):
        pass


if __name__ == "__main__":
    # 将 sys.stdout 和 sys.stderr 重定向到日志记录器
    import sys

    sys.stdout = LoggerWriter(logging.INFO)
    sys.stderr = LoggerWriter(logging.ERROR)

    # 你的 Python 代码
    print("Hello, world!")  # 这条语句的输出会写入到 example.log 文件中
