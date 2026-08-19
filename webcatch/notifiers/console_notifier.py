# -*- coding: utf-8 -*-
"""
控制台通知器 — 直接打印到日志，开发/调试用
"""
import logging

from .base import BaseNotifier

logger = logging.getLogger("webcatch.notifier.console")


class ConsoleNotifier(BaseNotifier):
    """控制台通知器，用于开发调试"""

    async def send(self, subject, body, **kwargs):
        logger.info(f"[通知] {subject}\n{body}")
        return True
