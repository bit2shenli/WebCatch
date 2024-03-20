# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  IDE         : PyCharm
  File Name   : main
  Description : 启动程序
  Author      : chenyushencc@gmail.com
  date        : 2024/3/13 10:31
-------------------------------------------------
"""
import asyncio
import logging

from my_logging import LoggerWriter
from web_catch import get_website_content, check_update, test_email


# TODO 链接和 class 配置
link_class = []


async def main():
    tasks = []
    # 创建一个定时发送官方邮件的 test 邮件
    task = asyncio.create_task(test_email())
    tasks.append(task)

    # 创建任务并启动多个协程
    for key, value in enumerate(link_class):
        # print(key, value, value["name"], value["url"], value["class"])
        name, url, catch_class = value["name"], value["url"], value["class"]
        content = get_website_content(url, catch_class)
        if content:
            task = asyncio.create_task(check_update(name, url, catch_class, content))
            tasks.append(task)

        else:
            print(name + " 无法获取网站内容")

    for task in tasks:
        await task


if __name__ == "__main__":
    # 将 sys.stdout 和 sys.stderr 重定向到日志记录器
    """ 将 print 打印成日志，需要本地打印时，注释掉 """
    import sys
    sys.stdout = LoggerWriter(logging.INFO)
    sys.stderr = LoggerWriter(logging.ERROR)
    """ 将 print 打印成日志，需要本地打印时，注释掉 """

    # 运行主协程
    asyncio.run(main())
