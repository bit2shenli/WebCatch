# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name   : web_catch_scs.py
  Description : 监控国家公务员局网站变化（纯 API 方式，无需 Selenium）
  Usage       : python web_catch_scs.py
-------------------------------------------------
"""
import os
import json
import time
import difflib
import datetime
import hashlib

import requests

# 复用你仓库的邮件模块
from send_email import send_email

# ==================== 配置区 ====================

# 国家公务员局 API（从网页 JS 中提取）
API_ARTICLE = "http://dl.scs.gov.cn/api/gkhome/article/{hb01_id}"
API_OTHERS = "http://dl.scs.gov.cn/api/gkhome/others/{hb01_id}"
HB01_ID = "8a81f6d9980207bb0198ab5683670008"  # 2026年度国考

# 检查间隔（秒）
CHECK_INTERVAL = 300  # 5分钟

# 快照存储目录
SNAPSHOT_DIR = "snapshots"

# 邮件配置（和你 send_email.py 保持一致）
SENDER_EMAIL = "your_email@163.com"           # TODO 改成你的
AUTHENTICATION = "your_email_authentication"  # TODO 改成你的授权码
RECEIVER_EMAIL = "your_email@163.com"         # TODO 改成你的

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Mobile-Client": "0",
}

# ==================== 核心逻辑 ====================

def fetch_articles():
    """通过 API 获取公告列表，返回格式化文本"""
    url = API_ARTICLE.format(hb01_id=HB01_ID)
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()

    lines = []
    for group in data.get("articleGroupList", []):
        title = group.get("title", "未知栏目")
        lines.append("=" * 50)
        lines.append("[栏目] " + title)
        lines.append("-" * 50)
        for art in group.get("articleList", []):
            ts = art.get("pstrtime", "")
            if ts and isinstance(ts, (int, float)) and ts > 1000000000:
                date = datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
            else:
                date = str(ts)[:10] if ts else ""
            lines.append("[" + date + "] " + art.get("articleTitle", ""))
    return "\n".join(lines)


def fetch_downloads():
    """通过 API 获取下载资源列表，返回格式化文本"""
    url = API_OTHERS.format(hb01_id=HB01_ID)
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()

    lines = []
    res_list = data.get("resList", [])
    if res_list:
        lines.append("=" * 50)
        lines.append("[下载资源] " + str(len(res_list)) + " 个")
        lines.append("-" * 50)
        for res in res_list:
            lines.append(res.get("resourceName", ""))
    return "\n".join(lines)


def fetch_all():
    """获取所有内容，合并为一个文本"""
    parts = []
    try:
        parts.append(fetch_articles())
    except Exception as e:
        parts.append("[ERROR] 获取公告失败: " + str(e))
    try:
        parts.append(fetch_downloads())
    except Exception as e:
        parts.append("[ERROR] 获取下载资源失败: " + str(e))
    return "\n".join(parts)


def get_snapshot_path(name):
    """获取快照文件路径"""
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    url_hash = hashlib.md5(name.encode()).hexdigest()[:12]
    return os.path.join(SNAPSHOT_DIR, url_hash + ".txt")


def load_snapshot(name):
    """加载上次的快照"""
    path = get_snapshot_path(name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def save_snapshot(name, content):
    """保存快照"""
    path = get_snapshot_path(name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def diff_content(old_text, new_text):
    """对比新旧内容，返回变化摘要"""
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    diff = list(difflib.unified_diff(
        old_lines, new_lines,
        fromfile="旧内容", tofile="新内容",
        lineterm="", n=1
    ))

    if not diff:
        return None

    # 提取新增的行
    added = [line[1:] for line in diff if line.startswith("+") and not line.startswith("+++")]
    # 提取删除的行
    removed = [line[1:] for line in diff if line.startswith("-") and not line.startswith("---")]

    summary_parts = []
    if added:
        summary_parts.append("[新增内容] " + str(len(added)) + " 行:\n" + "\n".join(added[:20]))
        if len(added) > 20:
            summary_parts.append("... 还有 " + str(len(added) - 20) + " 行")
    if removed:
        summary_parts.append("[移除内容] " + str(len(removed)) + " 行:\n" + "\n".join(removed[:10]))

    return "\n\n".join(summary_parts) if summary_parts else "内容有变化但无法解析差异"


def send_change_email(subject, diff_summary):
    """发送变化通知邮件"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = (
        "检测时间: " + now + "\n"
        "监控页面: 国家公务员局 - 考试录用专题\n"
        "页面地址: http://bm.scs.gov.cn/pp/gkweb/core/web/ui/business/home/gkhome.html\n"
        + "=" * 50 + "\n\n"
        + diff_summary + "\n\n"
        + "=" * 50 + "\n"
        "~ FROM shenyuchen の WebCatch ~"
    )
    send_email(
        sender_email=SENDER_EMAIL,
        authentication=AUTHENTICATION,
        receiver_email=RECEIVER_EMAIL,
        subject=subject,
        body=body,
        file_path=None
    )


def run_monitor():
    """主监控循环"""
    print("[START] WebCatch 国家公务员局监控 - " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("[INFO] 检查间隔: " + str(CHECK_INTERVAL) + " 秒")
    print("[INFO] API 方式: 直接 HTTP 请求，无需浏览器")
    print()

    monitor_name = "国家公务员局-考试录用"

    # 首次获取基线
    last = load_snapshot(monitor_name)
    if not last:
        print("[INIT] 首次运行，获取基线快照...")
        content = fetch_all()
        save_snapshot(monitor_name, content)
        print("[INIT] 基线已保存 (" + str(len(content)) + " 字符)")
    else:
        print("[INIT] 已有历史快照 (" + str(len(last)) + " 字符)")

    print()
    print("[RUN] 开始循环监控...")
    print()

    while True:
        now = datetime.datetime.now().strftime("%H:%M:%S")

        try:
            new_content = fetch_all()
        except Exception as e:
            print("[" + now + "] 获取失败: " + str(e))
            time.sleep(CHECK_INTERVAL)
            continue

        old_content = load_snapshot(monitor_name)

        if old_content is None:
            save_snapshot(monitor_name, new_content)
            print("[" + now + "] 初始化基线")
        elif new_content == old_content:
            print("[" + now + "] 无变化")
        else:
            diff_summary = diff_content(old_content, new_content)
            print("[" + now + "] 检测到变化！")
            print(diff_summary[:500])

            try:
                send_change_email("网页更新: 国家公务员局", diff_summary)
                print("[MAIL] 邮件已发送")
            except Exception as e:
                print("[ERROR] 邮件发送失败: " + str(e))

            save_snapshot(monitor_name, new_content)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run_monitor()
