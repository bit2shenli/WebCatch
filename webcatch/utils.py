# -*- coding: utf-8 -*-
"""
工具模块 — 日志初始化、HTTP Session 工厂
"""
import sys
import logging
from logging.handlers import RotatingFileHandler

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def setup_logging(config=None):
    """
    初始化日志系统

    :param config: logging 配置字典
    """
    if config is None:
        config = {}

    level_str = config.get("level", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)
    log_file = config.get("file", "webcatch.log")
    max_bytes = config.get("max_bytes", 10 * 1024 * 1024)
    backup_count = config.get("backup_count", 5)

    root = logging.getLogger("webcatch")
    root.setLevel(level)
    root.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)
    sh.setFormatter(fmt)
    root.addHandler(sh)

    # 文件（带轮转）
    try:
        fh = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        fh.setLevel(level)
        fh.setFormatter(fmt)
        root.addHandler(fh)
    except Exception as e:
        root.warning(f"无法创建日志文件 {log_file}: {e}")

    return root


def create_http_session(max_retries=3, backoff_factor=1, timeout=15):
    """
    创建带自动重试的 requests Session

    :param max_retries: 最大重试次数
    :param backoff_factor: 退避因子
    :param timeout: 默认超时（秒），存于 session 对象上供调用方使用
    """
    session = requests.Session()
    retry = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.default_timeout = timeout  # 自定义属性
    return session
