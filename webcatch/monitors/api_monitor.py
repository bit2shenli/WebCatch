# -*- coding: utf-8 -*-
"""
API 监控器 — 通过 JSON API 抓取数据，检测内容变化
专用于国家公务员局等提供 API 接口的网站
"""
import datetime
import difflib
import logging

import aiohttp

from .base import BaseMonitor

logger = logging.getLogger("webcatch.monitor.api")


class ApiMonitor(BaseMonitor):
    """
    API 监控器

    :param name: 监控名称
    :param api_endpoints: dict，包含 article/others 两个 API URL 模板
    :param hb01_id: API 参数 ID
    :param storage: Storage 实例
    :param notifier: 通知器实例
    :param interval: 检查间隔（秒）
    :param timeout: HTTP 请求超时（秒）
    :param max_retries: 最大重试次数
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Mobile-Client": "0",
    }

    def __init__(self, name, api_endpoints, hb01_id, storage, notifier=None,
                 interval=300, timeout=15, max_retries=3):
        super().__init__(name, storage, notifier, interval)
        self.api_article = api_endpoints.get("article", "")
        self.api_others = api_endpoints.get("others", "")
        self.hb01_id = hb01_id
        self.timeout = timeout
        self.max_retries = max_retries

    async def fetch(self):
        """异步抓取 API 数据"""
        parts = []
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            # 抓取公告列表
            try:
                parts.append(await self._fetch_articles(session))
            except Exception as e:
                logger.error(f"[{self.name}] 获取公告失败: {e}")
                parts.append(f"[ERROR] 获取公告失败: {e}")

            # 抓取下载资源
            try:
                parts.append(await self._fetch_downloads(session))
            except Exception as e:
                logger.error(f"[{self.name}] 获取下载资源失败: {e}")
                parts.append(f"[ERROR] 获取下载资源失败: {e}")

        return "\n".join(parts)

    async def _fetch_articles(self, session):
        """获取公告列表"""
        url = self.api_article.format(hb01_id=self.hb01_id)
        for attempt in range(1, self.max_retries + 1):
            try:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"[{self.name}] 公告 API HTTP {resp.status}")
                        continue
                    data = await resp.json()
                    return self._format_articles(data)
            except aiohttp.ClientError as e:
                logger.warning(f"[{self.name}] 公告请求失败 ({attempt}/{self.max_retries}): {e}")
        return "[ERROR] 公告获取失败（重试耗尽）"

    async def _fetch_downloads(self, session):
        """获取下载资源列表"""
        url = self.api_others.format(hb01_id=self.hb01_id)
        for attempt in range(1, self.max_retries + 1):
            try:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"[{self.name}] 下载 API HTTP {resp.status}")
                        continue
                    data = await resp.json()
                    return self._format_downloads(data)
            except aiohttp.ClientError as e:
                logger.warning(f"[{self.name}] 下载请求失败 ({attempt}/{self.max_retries}): {e}")
        return "[ERROR] 下载资源获取失败（重试耗尽）"

    @staticmethod
    def _format_articles(data):
        lines = []
        for group in data.get("articleGroupList", []):
            title = group.get("title", "未知栏目")
            lines.append("=" * 50)
            lines.append(f"[栏目] {title}")
            lines.append("-" * 50)
            for art in group.get("articleList", []):
                ts = art.get("pstrtime", "")
                if ts and isinstance(ts, (int, float)) and ts > 1_000_000_000:
                    date = datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                else:
                    date = str(ts)[:10] if ts else ""
                lines.append(f"[{date}] {art.get('articleTitle', '')}")
        return "\n".join(lines)

    @staticmethod
    def _format_downloads(data):
        lines = []
        res_list = data.get("resList", [])
        if res_list:
            lines.append("=" * 50)
            lines.append(f"[下载资源] {len(res_list)} 个")
            lines.append("-" * 50)
            for res in res_list:
                lines.append(res.get("resourceName", ""))
        return "\n".join(lines)

    def diff(self, old, new):
        """使用 difflib 做行级 diff"""
        diff = list(difflib.unified_diff(
            old.splitlines(), new.splitlines(),
            fromfile="旧内容", tofile="新内容",
            lineterm="", n=1,
        ))
        if not diff:
            return None

        added = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]
        removed = [l[1:] for l in diff if l.startswith("-") and not l.startswith("---")]

        parts = []
        if added:
            parts.append(f"[新增内容] {len(added)} 行:\n" + "\n".join(added[:20]))
            if len(added) > 20:
                parts.append(f"... 还有 {len(added) - 20} 行")
        if removed:
            parts.append(f"[移除内容] {len(removed)} 行:\n" + "\n".join(removed[:10]))

        return "\n\n".join(parts) if parts else "内容有变化但无法解析差异"
