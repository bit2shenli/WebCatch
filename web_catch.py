# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  IDE         : PyCharm
  File Name   : web_catch
  Description : 根据网页的 class 捕捉网页信息
  Summary     : 1、
                2、
                3、
  Author      : chenyushencc@gmail.com
  date        : 2024/3/13 10:04
-------------------------------------------------
"""
import requests
import datetime
import asyncio

from bs4 import BeautifulSoup
from send_email import set_email


def get_website_content(url, catch_class):
    """
    获取网站内容
    :param url: 检测网址
    :param catch_class: 检测网址的 class
    :return:
    """
    # 发送HTTP请求获取网页内容
    response = requests.get(url)

    if response.status_code == 200:
        # 使用BeautifulSoup解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 这里假设网站内容是放在<div class="content">标签内的
        content_tag = soup.find('div', class_=catch_class)

        if content_tag:
            return content_tag.get_text()

    return None


async def check_update(name, url, catch_class, last_content):
    """
    检查网址的class内容是否更新，更新了就提醒用户
    :param name: 网页名称（自定义）
    :param url: 网址
    :param catch_class: 网址 class
    :param last_content: 检测内容
    :return:
    """
    # 每隔一段时间检查一次网站更新
    while True:
        now = datetime.datetime.now().strftime("%H:%M:%S")      # 记录当前时间

        new_content = get_website_content(url, catch_class)
        if new_content and new_content != last_content:
            print(f"{now} {name} 网站有更新！\n {new_content}")
            # 存入文本 并发送邮件提醒
            with open("dedails.txt", "w", encoding='utf-8') as file:
                file.write(url + new_content)
            set_email(subject=name)

            last_content = new_content
        else:
            # print(f"point {name} \n {new_content}")
            print(f"{now} 网站暂无更新 {name}")

        await asyncio.sleep(60)  # TODO 间隔60秒再次检查


async def test_email():
    """ 每隔一段时间，发送 test 邮件，观测程序在运行 """
    while True:
        set_email(file_path=None)       # 定时测试邮件不用发送附件
        print("Web Catch start~\nGood news is coming~")

        await asyncio.sleep(8*60*60)  # TODO 间隔8小时秒再次检查


if __name__ == "__main__":
    name = "监测网站名称"
    url = "https://news.cctv.com/"  # 替换成你要检查的网站地址
    catch_class = "content"
    last_content = get_website_content(url, catch_class)
    if last_content:
        check_update(url, catch_class, last_content)
    else:
        print(name + " 无法获取网站内容")

