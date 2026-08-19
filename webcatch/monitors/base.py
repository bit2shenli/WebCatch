# -*- coding: utf-8 -*-
"""
监控器抽象基类
所有 monitor 必须实现 fetch / diff，可选覆盖 notify
"""
import asyncio
import datetime
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("webcatch.monitor")


class BaseMonitor(ABC):
    """
    抽象监控器

    子类需实现：
        fetch()  — 抓取当前内容，返回字符串
        diff(old, new) — 对比新旧内容，返回摘要字符串或 None
    """

    def __init__(self, name, storage, notifier=None, interval=60):
        self.name = name
        self.storage = storage
        self.notifier = notifier
        self.interval = interval

    @abstractmethod
    async def fetch(self) -> str | None:
        """抓取当前网页/API 内容，失败返回 None"""
        ...

    @abstractmethod
    def diff(self, old: str, new: str) -> str | None:
        """对比新旧内容，返回变化摘要；无变化返回 None"""
        ...

    async def notify(self, diff_summary: str):
        """发送通知（默认调用 notifier，子类可覆盖）"""
        if self.notifier:
            try:
                await self.notifier.send(
                    subject=f"网页更新: {self.name}",
                    body=f"监控目标: {self.name}\n\n{diff_summary}",
                )
                logger.info(f"[{self.name}] 通知已发送")
            except Exception as e:
                logger.error(f"[{self.name}] 通知发送失败: {e}")
        else:
            logger.warning(f"[{self.name}] 未配置通知器，跳过通知")

    async def run(self):
        """主监控循环"""
        logger.info(f"[{self.name}] 启动监控 (间隔 {self.interval}s)")

        # 加载基线
        last_content = self.storage.load_snapshot(self.name)
        if last_content:
            logger.info(f"[{self.name}] 已加载历史快照 ({len(last_content)} 字符)")
        else:
            logger.info(f"[{self.name}] 首次监控，获取基线...")

        while True:
            now = datetime.datetime.now().strftime("%H:%M:%S")

            new_content = await self.fetch()

            if new_content is None:
                logger.warning(f"[{now}] [{self.name}] 获取失败，{self.interval}s 后重试")
                await asyncio.sleep(self.interval)
                continue

            if last_content is None:
                self.storage.save_snapshot(self.name, new_content)
                last_content = new_content
                logger.info(f"[{now}] [{self.name}] 基线已保存 ({len(new_content)} 字符)")
            elif new_content != last_content:
                logger.info(f"[{now}] [{self.name}] 检测到更新！")

                diff_summary = self.diff(last_content, new_content)
                self.storage.save_history(self.name, last_content, new_content)
                self.storage.save_snapshot(self.name, new_content)
                self.storage.update_check_time(self.name)

                await self.notify(diff_summary or "内容有变化")
                last_content = new_content
            else:
                logger.debug(f"[{now}] [{self.name}] 无变化")
                self.storage.update_check_time(self.name)

            await asyncio.sleep(self.interval)
