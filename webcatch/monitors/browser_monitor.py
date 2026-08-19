# -*- coding: utf-8 -*-
"""
浏览器监控器 — 使用 Playwright 无头浏览器抓取有反爬保护的网站
通过隐藏自动化标识绕过 WAF 检测
"""
import os
import logging

from .base import BaseMonitor

logger = logging.getLogger("webcatch.monitor.browser")

# Chrome 路径（自动检测）
_CHROME_DIR = os.path.expanduser("~/.local/chrome-files")
_CHROME_BIN = os.path.join(_CHROME_DIR, "chrome")


class BrowserMonitor(BaseMonitor):
    """
    无头浏览器监控器 — 用于有 WAF 反爬保护的网站

    :param name: 监控名称
    :param url: 网页地址
    :param css_selector: 可选，提取指定元素的文本（CSS 选择器）
    :param storage: Storage 实例
    :param notifier: 通知器实例
    :param interval: 检查间隔（秒）
    :param wait_ms: 页面加载后等待时间（毫秒），等待 JS 执行完成
    :param max_retries: 最大重试次数
    """

    def __init__(self, name, url, css_selector=None, storage=None, notifier=None,
                 interval=60, wait_ms=8000, max_retries=2):
        super().__init__(name, storage, notifier, interval)
        self.url = url
        self.css_selector = css_selector
        self.wait_ms = wait_ms
        self.max_retries = max_retries

    async def fetch(self):
        """使用 Playwright 无头浏览器抓取页面"""
        # Playwright 是同步 API，在线程池中运行
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_sync)

    def _fetch_sync(self):
        """同步抓取（在线程池中执行）"""
        from playwright.sync_api import sync_playwright

        for attempt in range(1, self.max_retries + 1):
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(
                        headless=True,
                        executable_path=_CHROME_BIN,
                        args=[
                            "--no-sandbox",
                            "--disable-gpu",
                            "--disable-dev-shm-usage",
                            "--disable-blink-features=AutomationControlled",
                        ],
                    )

                    context = browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                        viewport={"width": 1920, "height": 1080},
                        locale="zh-CN",
                    )

                    page = context.new_page()

                    # 隐藏 webdriver 标识
                    page.add_init_script(
                        'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
                        'delete navigator.__proto__.webdriver;'
                    )

                    page.goto(self.url, timeout=20000)
                    page.wait_for_timeout(self.wait_ms)

                    # 提取内容
                    if self.css_selector:
                        try:
                            element = page.query_selector(self.css_selector)
                            if element:
                                text = element.inner_text()
                            else:
                                logger.warning(f"[{self.name}] 选择器 '{self.css_selector}' 未找到，使用全文")
                                text = page.inner_text("body")
                        except Exception:
                            text = page.inner_text("body")
                    else:
                        text = page.inner_text("body")

                    title = page.title()
                    browser.close()

                    if text and text.strip():
                        logger.debug(f"[{self.name}] 抓取成功: {title} ({len(text)} 字符)")
                        return text.strip()
                    else:
                        logger.warning(f"[{self.name}] 页面内容为空 (尝试 {attempt}/{self.max_retries})")

            except Exception as e:
                logger.warning(f"[{self.name}] 浏览器异常 (尝试 {attempt}/{self.max_retries}): {e}")

        return None

    def diff(self, old, new):
        """行级文本对比"""
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
