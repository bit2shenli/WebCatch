# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  IDE         : PyCharm
  File Name   : send_email
  Description : 邮件发送
  Summary     : 1、
                2、
                3、
  Author      : chenyushencc@gmail.com
  date        : 2024/3/13 10:20
-------------------------------------------------
"""
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def set_email(subject="Web Catch Email", file_path='dedails.txt'):
    """
    设置完直接发送邮件
    :param subject: 邮件主题（可自定义）
    :param file_path: 附件路径，也决定附件的名称，如果不需要附件可以设置为 None
    :return:
    """
    # 请替换成你的邮箱地址和密码
    sender_email = 'your_email@163.com'              # TODO 邮箱，可自己给自己发邮件
    authentication = 'your_email_authentication'     # TODO 授权码
    receiver_email = 'your_email@163.com'            # TODO 邮箱，可自己给自己发邮件
    body = 'Web Catch start~\nGood news is coming~'

    send_email(sender_email, authentication, receiver_email, subject, body, file_path)


def send_email(sender_email, authentication, receiver_email, subject, body, file_path=None):
    """
    :param sender_email: 发邮箱的邮箱地址
    :param authentication: 163邮箱是使用的授权码
    :param receiver_email: 收邮箱的邮箱地址
    :param subject: 邮件主题
    :param body: 邮件内容
    :param file_path: 附件地址
    :return:
    """
    # 创建邮件消息
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # 添加正文内容
    msg.attach(MIMEText(body, 'plain'))

    # 添加附件
    if file_path:
        with open(file_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=file_path)
            part['Content-Disposition'] = 'attachment; filename="%s"' % file_path
            msg.attach(part)

    # 连接到SMTP服务器并发送邮件
    with smtplib.SMTP_SSL('smtp.163.com', 465) as server:       # TODO SMTP 也需要修改，具体见各个邮箱官网，一般百度可查
        server.login(sender_email, authentication)
        server.sendmail(sender_email, receiver_email, msg.as_string())


if __name__ == "__main__":
    # 请替换成你的邮箱地址和密码
    print("Web Catch")
