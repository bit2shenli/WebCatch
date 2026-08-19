# -*- coding: utf-8 -*-
"""
Webhook 通知器 — 支持企业微信 / 钉钉 / 飞书 / 自定义 Webhook
"""
import json
import logging

import aiohttp

from .base import BaseNotifier

logger = logging.getLogger("webcatch.notifier.webhook")


class WebhookNotifier(BaseNotifier):
    """
    Webhook 通知器

    :param url: Webhook 地址
    :param msg_type: 消息格式 — wechat / dingtalk / feishu / raw
    :param headers: 自定义请求头
    """

    def __init__(self, url, msg_type="raw", headers=None):
        self.url = url
        self.msg_type = msg_type
        self.headers = headers or {"Content-Type": "application/json"}

    async def send(self, subject, body, **kwargs):
        payload = self._build_payload(subject, body)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        logger.info(f"Webhook 发送成功: {subject}")
                        return True
                    else:
                        text = await resp.text()
                        logger.error(f"Webhook 失败 HTTP {resp.status}: {text}")
                        return False
        except Exception as e:
            logger.error(f"Webhook 异常: {e}")
            return False

    def _build_payload(self, subject, body):
        text = f"**{subject}**\n\n{body}"

        if self.msg_type == "wechat":
            return {
                "msgtype": "markdown",
                "markdown": {"content": text},
            }
        elif self.msg_type == "dingtalk":
            return {
                "msgtype": "markdown",
                "markdown": {"title": subject, "text": text},
            }
        elif self.msg_type == "feishu":
            return {
                "msg_type": "text",
                "content": {"text": f"{subject}\n\n{body}"},
            }
        else:
            return {"subject": subject, "body": body}
