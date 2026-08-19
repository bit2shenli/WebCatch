# -*- coding: utf-8 -*-
"""
HTML 监控器 — 通过 CSS class 抓取网页指定区域，检测内容变化
"""
import logging

import aiohttp
from bs4 import BeautifulSoup

from .base import BaseMonitor

logger = logging.getLogger("webcatch.monitor.html")


class HtmlMonitor(BaseMonitor):
    """
    HTML class 监控器

    :param name: 监控名称
    :param url: 网页地址
    :param css_class: 要监控的 HTML class 名（空字符串 = 整个页面）
    :param storage: Storage 实例
    :param notifier: 通知器实例
    :param interval: 检查间隔（秒）
    :param timeout: HTTP 请求超时（秒）
    :param max_retries: 最大重试次数
    """

    def __init__(self, name, url, css_class, storage, notifier=None,
                 interval=60, timeout=15, max_retries=3):
        super().__init__(name, storage, notifier, interval)
        self.url = url
        self.css_class = css_class
        self.timeout = timeout
        self.max_retries = max_retries

    async def fetch(self):
        """异步抓取网页内容"""
        for attempt in range(1, self.max_retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.url,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                        headers={"User-Agent": "Mozilla/5.0 WebCatch/2.0"},
                    ) as resp:
                        if resp.status != 200:
                            logger.warning(
                                f"[{self.name}] HTTP {resp.status} (尝试 {attempt}/{self.max_retries})"
                            )
                            continue

                        html = await resp.text()
                        return self._parse(html)

            except aiohttp.ClientError as e:
                logger.warning(
                    f"[{self.name}] 请求失败 (尝试 {attempt}/{self.max_retries}): {e}"
                )
            except Exception as e:
                logger.error(f"[{self.name}] 异常: {e}")
                return None

        return None

    def _parse(self, html):
        """从 HTML 中提取指定 class 的文本"""
        soup = BeautifulSoup(html, "html.parser")

        if self.css_class:
            tag = soup.find("div", class_=self.css_class)
            if tag:
                return tag.get_text(separator="\n", strip=True)
            # class 未找到，返回整个页面文本作为降级
            logger.debug(f"[{self.name}] 未找到 class='{self.css_class}'，使用全文")

        return soup.get_text(separator="\n", strip=True)

    def diff(self, old, new):
        """简单文本对比（行级）"""
        old_lines = set(old.splitlines())
        new_lines = set(new.splitlines())
        added = new_lines - old_lines
        removed = old_lines - new_lines

        if not added and not removed:
            return None

        parts = []
        if added:
            preview = "\n".join(list(added)[:20])
            parts.append(f"[新增] {len(added)} 行:\n{preview}")
        if removed:
            preview = "\n".join(list(removed)[:10])
            parts.append(f"[移除] {len(removed)} 行:\n{preview}")

        return "\n\n".join(parts)
