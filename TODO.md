# WebCatch 重构计划

## 🔴 P0 — 必须立即修复

### 1. 配置外置 ✅
- [x] 引入 `config/config.yaml` 主配置（邮箱、间隔、全局参数）
- [x] 引入 `config/targets.yaml` 监控目标列表
- [x] 新增 `config_loader.py` 配置加载器（默认值兜底）
- [x] 消除所有硬编码的 TODO 占位符
- [x] 改配置不用改代码，非程序员也能维护

### 2. 错误处理 + timeout ✅
- [x] `requests.get()` 加 `timeout` 参数（默认 15s，可配置）
- [x] 引入 `urllib3.Retry` + `HTTPAdapter` 自动重试（指数退避）
- [x] 网络异常后记录日志并继续运行，不中断协程
- [x] 邮件发送失败后记录错误，不影响监控继续运行
- [x] 所有模块使用标准 `logging` 替代 print

---

## 🟡 P1 — 近期应完成

### 3. 统一并发模型 ✅
- [x] 统一用 `aiohttp` 替代 `requests`（真正的异步 HTTP）
- [x] 所有 Monitor 的 `fetch()` 均为 async 方法
- [x] 邮件发送通过 `loop.run_in_executor` 异步化

### 4. 持久化快照 ✅
- [x] 统一 `data/snapshots/` 快照目录（所有 Monitor 共用）
- [x] 增加 `data/history/` 变更历史记录（JSON Lines 格式）
- [x] 增加 `data/state.json` 进程状态（上次检查时间）
- [x] `webcatch/storage.py` 统一管理所有存储操作

### 5. 依赖管理 ✅
- [x] 创建 `requirements.txt`（beautifulsoup4、requests、pyyaml）

---

## 🟢 P2 — 架构优化

### 6. 抽象 Monitor 基类 ✅
- [x] `webcatch/monitors/base.py` — 抽象基类：`fetch()` → `diff()` → `notify()` → `run()`
- [x] `webcatch/monitors/html_monitor.py` — HTML class 抓取（aiohttp + BeautifulSoup）
- [x] `webcatch/monitors/api_monitor.py` — JSON API 抓取（专用于国考）
- [x] `webcatch/main.py` 中根据配置自动构建 Monitor 实例

### 7. 通知器抽象 ✅
- [x] `webcatch/notifiers/base.py` — 抽象基类
- [x] `webcatch/notifiers/email_notifier.py` — 邮件（支持任意 SMTP）
- [x] `webcatch/notifiers/webhook_notifier.py` — 企业微信/钉钉/飞书 Webhook
- [x] `webcatch/notifiers/console_notifier.py` — 控制台（开发用）
- [ ] `webcatch/notifiers/telegram_notifier.py` — Telegram Bot（待实现）

### 8. 日志系统升级 ✅（P0 阶段顺带完成）
- [x] 改用标准 `logging` 模块，按模块分 logger（webcatch.monitor / webcatch.email / webcatch.scs）
- [x] 统一配置 handler、格式、日志轮转（RotatingFileHandler）
- [x] 支持从 config.yaml 控制日志级别、文件路径、大小、备份数

---

## ⚪ P3 — 长期维护

### 9. 测试
- [ ] 核心逻辑（内容对比、diff 生成、邮件发送）零测试
- [ ] `tests/test_html_monitor.py`
- [ ] `tests/test_diff.py`
- [ ] `tests/test_notifier.py`
- [ ] `tests/fixtures/` — 测试用 HTML 快照

### 10. 目录结构重构 ✅
- [x] 包化 `webcatch/`，按职责分目录
- [x] 旧文件已删除，仅保留新结构

---

## 🔒 待解决 — 反爬站点（HTTP 412）

以下 4 个站点返回 HTTP 412（Precondition Failed），服务器有 WAF/CDN 反爬机制，
发送 JavaScript 挑战页，普通 HTTP 请求无法获取真实内容。

| 站点 | URL | 现象 | 解决方案 |
|------|-----|------|----------|
| 湖南省税务局 | `http://hunan.chinatax.gov.cn` | 412，返回 JS 挑战页 | 接入 Playwright/Selenium 无头浏览器 |
| 学信网 | `https://www.chsi.com.cn` | 412，WAF 拦截 | 同上，或用学信网 APP 推送替代 |
| 中国学位与研究生教育信息网 | `http://www.cdgdc.edu.cn` | 412，WAF 拦截 | 同上 |
| B站视频 | `https://www.bilibili.com/video/BV19XazzwE3W` | 412，反爬拦截 | B站有 RSS/API 可替代 |

### 可选方案

1. **接入 Playwright 无头浏览器** — 新建 `webcatch/monitors/browser_monitor.py`，用真实浏览器渲染后再提取内容
2. **用 RSS/API 替代** — B站支持 RSSHub（`https://rsshub.app/bilibili/video/BV19XazzwE3W`）
3. **放弃监控** — 这些站点内容更新频率低，手动查看即可

### 国考报名专题网站（额外发现）

| 站点 | URL | 现象 | 说明 |
|------|-----|------|------|
| 国考报名专题网站 | `http://gwy.cscs.cn` | DNS 解析失败 | 域名已失效，原备考指南中的链接有误 |

### 长沙市政府网站（2026-08-19 补充）

以下站点需加 `www` 前缀才能访问，原用户提供的是裸域名：

| 站点 | 原始 URL | 正确 URL | 现象 |
|------|----------|----------|------|
| 长沙市开福区 | `kaifu.gov.cn` | `https://www.kaifu.gov.cn` | 裸域名 DNS 无解析，需加 www |
| 长沙市政府 | `changsha.gov.cn` | `https://www.changsha.gov.cn` | 同上 |
