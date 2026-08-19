# -*- coding: utf-8 -*-
"""
邮件通知器 — 异步发送邮件（在执行器中运行同步 SMTP）
"""
import asyncio
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from .base import BaseNotifier

logger = logging.getLogger("webcatch.notifier.email")


class EmailNotifier(BaseNotifier):
    """
    邮件通知器

    :param config: email 配置字典，包含 smtp_host/smtp_port/sender/password/receiver
    """

    def __init__(self, config):
        self.smtp_host = config.get("smtp_host", "smtp.163.com")
        self.smtp_port = config.get("smtp_port", 465)
        self.sender = config.get("sender", "")
        self.password = config.get("password", "")
        self.receiver = config.get("receiver", "")
        self.enabled = config.get("enabled", True)

    async def send(self, subject, body, file_path=None, **kwargs):
        """异步发送邮件（实际 SMTP 在线程池中执行）"""
        if not self.enabled:
            logger.info("邮件通知已禁用")
            return False

        if not all([self.sender, self.password, self.receiver]):
            logger.error("邮件配置不完整：sender/password/receiver 不能为空")
            return False

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._send_sync, subject, body, file_path)

    def _send_sync(self, subject, body, file_path):
        """同步发送邮件"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender
            msg["To"] = self.receiver
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            if file_path:
                try:
                    with open(file_path, "rb") as f:
                        part = MIMEApplication(f.read(), Name=file_path)
                        part["Content-Disposition"] = f'attachment; filename="{file_path}"'
                        msg.attach(part)
                except FileNotFoundError:
                    logger.warning(f"附件不存在: {file_path}")

            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=15) as server:
                server.login(self.sender, self.password)
                server.sendmail(self.sender, self.receiver, msg.as_string())

            logger.info(f"邮件已发送: {subject} -> {self.receiver}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("邮件认证失败：请检查邮箱地址和授权码")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP 错误: {e}")
            return False
        except Exception as e:
            logger.error(f"邮件发送异常: {e}")
            return False
