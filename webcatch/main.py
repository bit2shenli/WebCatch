# -*- coding: utf-8 -*-
"""
WebCatch 主入口 — 从配置加载目标，构建 Monitor + Notifier，启动异步监控
"""
import asyncio
import datetime
import logging

import yaml

from .utils import setup_logging
from .storage import Storage
from .monitors.html_monitor import HtmlMonitor
from .monitors.api_monitor import ApiMonitor
from .monitors.browser_monitor import BrowserMonitor
from .notifiers.email_notifier import EmailNotifier
from .notifiers.console_notifier import ConsoleNotifier

logger = logging.getLogger("webcatch.main")


def _load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def build_notifiers(config):
    """根据配置构建通知器列表"""
    notifiers = []
    email_cfg = config.get("email", {})
    if email_cfg.get("enabled", True) and email_cfg.get("sender"):
        notifiers.append(EmailNotifier(email_cfg))

    webhook_cfg = config.get("webhook", {})
    if webhook_cfg.get("url"):
        from .notifiers.webhook_notifier import WebhookNotifier
        notifiers.append(WebhookNotifier(
            url=webhook_cfg["url"],
            msg_type=webhook_cfg.get("msg_type", "raw"),
        ))

    # 兜底：至少有个控制台通知器
    if not notifiers:
        notifiers.append(ConsoleNotifier())

    return notifiers


def build_monitors(config, targets_cfg, storage, notifiers):
    """根据配置构建监控器列表"""
    monitors = []
    mon_cfg = config.get("monitor", {})
    timeout = mon_cfg.get("request_timeout", 15)
    max_retries = mon_cfg.get("max_retries", 3)
    interval = mon_cfg.get("check_interval", 60)
    notifier = notifiers[0] if notifiers else None

    for t in targets_cfg.get("targets", []):
        if t.get("enabled", True) is False:
            continue
        name = t.get("name", "未命名")
        url = t.get("url", "")
        css_class = t.get("class", "")
        target_type = t.get("type", "html")

        if not url:
            continue

        if target_type == "browser":
            monitors.append(BrowserMonitor(
                name=name,
                url=url,
                css_selector=css_class or None,
                storage=storage,
                notifier=notifier,
                interval=interval,
                wait_ms=t.get("wait_ms", 8000),
                max_retries=max_retries,
            ))
        else:
            monitors.append(HtmlMonitor(
                name=name,
                url=url,
                css_class=css_class,
                storage=storage,
                notifier=notifier,
                interval=interval,
                timeout=timeout,
                max_retries=max_retries,
            ))

    return monitors


def build_scs_monitor(config, storage, notifiers):
    """构建国考 API 监控器"""
    scs_cfg = config.get("scs_monitor", {})
    if not scs_cfg.get("enabled", True):
        return None

    mon_cfg = config.get("monitor", {})
    notifier = notifiers[0] if notifiers else None

    return ApiMonitor(
        name="国家公务员局-考试录用",
        api_endpoints={
            "article": scs_cfg.get("api_article", ""),
            "others": scs_cfg.get("api_others", ""),
        },
        hb01_id=scs_cfg.get("hb01_id", ""),
        storage=storage,
        notifier=notifier,
        interval=scs_cfg.get("check_interval", 300),
        timeout=mon_cfg.get("request_timeout", 15),
        max_retries=mon_cfg.get("max_retries", 3),
    )


async def _test_email_loop(notifier, interval):
    """定期发送测试邮件"""
    while True:
        try:
            await notifier.send(
                subject="WebCatch 运行状态: 正常",
                body=f"WebCatch 正在运行中~\n时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            )
        except Exception as e:
            logger.error(f"测试邮件失败: {e}")
        await asyncio.sleep(interval)


def run(config_path="config/config.yaml", targets_path="config/targets.yaml"):
    """
    主运行函数

    :param config_path: 主配置文件路径
    :param targets_path: 监控目标文件路径
    """
    # 加载配置
    config = _load_yaml(config_path)
    targets_cfg = _load_yaml(targets_path)

    # 初始化日志
    setup_logging(config.get("logging", {}))

    logger.info("=" * 50)
    logger.info("WebCatch v2.0 启动")
    logger.info("=" * 50)

    # 初始化存储
    storage = Storage(config.get("storage", {}))

    # 构建通知器
    notifiers = build_notifiers(config)
    logger.info(f"通知器: {[type(n).__name__ for n in notifiers]}")

    # 构建 HTML 监控器
    html_monitors = build_monitors(config, targets_cfg, storage, notifiers)
    logger.info(f"HTML 监控目标: {len(html_monitors)} 个")

    # 构建国考 API 监控器
    scs_monitor = build_scs_monitor(config, storage, notifiers)
    if scs_monitor:
        logger.info("国考 API 监控: 已启用")

    # 组装所有异步任务
    all_monitors = html_monitors + ([scs_monitor] if scs_monitor else [])
    tasks = [m.run() for m in all_monitors]

    # 测试邮件任务
    test_interval = config.get("monitor", {}).get("test_email_interval", 8 * 60 * 60)
    if notifiers and test_interval > 0:
        tasks.append(_test_email_loop(notifiers[0], test_interval))

    logger.info(f"共启动 {len(tasks)} 个异步任务")

    # 运行
    async def _run_all():
        await asyncio.gather(*tasks)

    try:
        asyncio.run(_run_all())
    except KeyboardInterrupt:
        logger.info("WebCatch 已停止")


if __name__ == "__main__":
    run()
