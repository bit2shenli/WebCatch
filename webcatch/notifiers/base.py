# -*- coding: utf-8 -*-
"""
通知器抽象基类
"""
from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    """通知器接口，所有 notifier 必须实现 send 方法"""

    @abstractmethod
    async def send(self, subject: str, body: str, **kwargs):
        """
        发送通知

        :param subject: 通知标题
        :param body: 通知正文
        """
        ...
