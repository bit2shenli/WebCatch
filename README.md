# License
This project is licensed under the [Apache-2.0 license](LICENSE).

# Web Catch
### Web Catch start~ Good news is coming~
实时关注自己在意的网页，并及时提醒，避免错过重要的信息~

---

## 📁 项目结构

```
WebCatch/
├── config/
│   ├── config.yaml          # 主配置（邮箱、间隔、超时、重试、Webhook、日志）
│   └── targets.yaml         # 监控目标列表（支持 enabled 开关）
├── webcatch/
│   ├── __init__.py
│   ├── main.py              # 主入口：加载配置 → 构建组件 → 启动异步任务
│   ├── utils.py             # 日志初始化 + HTTP Session 工厂
│   ├── storage.py           # 快照 + 变更历史（JSONL）+ 进程状态
│   ├── rss_generator.py     # RSS 2.0 输出（变更记录可订阅）
│   ├── monitors/
│   │   ├── base.py          # 抽象基类：fetch → diff → notify → run
│   │   ├── html_monitor.py  # HTML class 抓取（aiohttp 异步）
│   │   ├── api_monitor.py   # JSON API 抓取（国考专用）
│   │   ├── browser_monitor.py # Playwright 无头浏览器（反爬站点）
│   │   └── rss_monitor.py   # RSS/Atom 订阅源监控
│   └── notifiers/
│       ├── base.py          # 抽象基类
│       ├── email_notifier.py    # 邮件通知
│       ├── webhook_notifier.py  # 企业微信/钉钉/飞书 Webhook
│       └── console_notifier.py  # 控制台（调试用）
├── data/                    # 运行时数据（自动生成）
│   ├── snapshots/           # 各目标最新内容快照
│   ├── history/             # 变更历史（JSONL）
│   ├── state.json           # 进程状态
│   └── feed.xml             # RSS 输出（可订阅）
├── run.py                   # 启动脚本
├── requirements.txt
├── TODO.md
├── README.md
└── LICENSE
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

如果需要监控反爬站点（WAF 保护的网站），还需安装 Playwright 浏览器：

```bash
pip install playwright
playwright install chromium
```

### 2. 修改配置

编辑 `config/config.yaml`，填写邮箱信息：

```yaml
email:
  enabled: true
  smtp_host: "smtp.163.com"
  smtp_port: 465
  sender: "your_email@163.com"       # 改成你的邮箱
  password: "your_auth_code"          # 改成你的授权码
  receiver: "your_email@163.com"     # 改成收件邮箱
```

### 3. 添加监控目标

编辑 `config/targets.yaml`：

```yaml
targets:
  - name: "国家公务员局"
    url: "http://bm.scs.gov.cn"
    class: ""               # HTML class，留空=监控整个页面
    type: "html"            # html / rss / browser
    enabled: true
```

### 4. 启动监控

```bash
python run.py
```

后台运行：

```bash
nohup python run.py > webcatch.log 2>&1 &
```

---

# FAQ

### Q: 实现方式?

A: 通过异步协程（asyncio + aiohttp），并发请求多个网页，对比每次的内容变化，有差别时通过邮件/Webhook 通知用户。支持 4 种监控模式：

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `html` | 抓取 HTML 指定 class 区域 | 普通网页 |
| `rss` | 解析 RSS/Atom 订阅源 | 论坛、博客、新闻站（自带 RSS） |
| `api` | 调用 JSON API 接口 | 有公开 API 的网站（如国考） |
| `browser` | Playwright 无头浏览器渲染 | 有 WAF 反爬保护的网站 |

### Q: 准备环境、运行配置?

A: 下载代码后，安装依赖，修改配置文件即可运行：

```bash
git clone https://github.com/learnore/WebCatch.git
cd WebCatch
pip install -r requirements.txt

# 修改邮箱配置
vim config/config.yaml

# 修改监控目标
vim config/targets.yaml

# 启动
python run.py
```

### Q: 支持的提醒方式?

A: 
- [x] Email（支持任意 SMTP 服务器）
- [x] Webhook（企业微信/钉钉/飞书）
- [x] RSS 输出（`data/feed.xml`，可用 RSS 阅读器订阅）
- [ ] 短信
- [ ] Telegram Bot

### Q: 监控目标怎么配置?

A: 在 `config/targets.yaml` 中添加，每个目标支持以下字段：

```yaml
- name: "网站名称"           # 必填
  url: "https://..."         # 必填
  class: "css-class-name"    # HTML class（type=browser 时为 CSS 选择器）
  type: "html"               # html / rss / browser / api（默认 html）
  enabled: true              # true 启用 / false 停用
  wait_ms: 8000              # type=browser 时，页面加载后等待时间（毫秒）
```

### Q: RSS 输出怎么用?

A: 每次检测到网页变化，系统会自动将变更记录写入 `data/feed.xml`。你可以用任意 RSS 阅读器（如 Feedly、Inoreader、NetNewsWire）订阅这个文件，就能看到每次更新的具体内容。

如果需要远程访问 RSS，可以用 Python 内置 HTTP 服务器：

```bash
cd data
python -m http.server 8080
# 然后在 RSS 阅读器中订阅 http://你的IP:8080/feed.xml
```

### Q: 常用命令?

A:

```bash
# 启动监控
python run.py

# 后台运行
nohup python run.py > webcatch.log 2>&1 &

# 查看进程
ps aux | grep "run.py"

# 停止
kill -9 <PID>

# 查看日志
tail -f webcatch.log

# 查看快照
ls data/snapshots/

# 查看变更历史
cat data/history/*.jsonl
```

---

## 📋 当前监控目标

### 公务员考试相关（启用中）

| 分类 | 网站 | 类型 |
|------|------|:----:|
| 国考 | 国家公务员局 | html |
| 国考 | 国家税务总局-公务员招录 | html |
| 国考 | 中央机关公开遴选和公开选调 | html |
| 国考 | 国家公务员局-考试录用（API） | api |
| 湖南 | 湖南人事考试网 | html |
| 湖南 | 红星网-湖南省委组织部 | html |
| 湖南 | 湖南省人力资源和社会保障厅 | html |
| 湖南 | 湖南省税务局 | browser |
| 长沙 | 长沙市开福区人民政府 | html |
| 长沙 | 长沙市财政局 | html |
| 长沙 | 长沙市人力资源和社会保障局 | html |
| 长沙 | 长沙市政府门户网站 | html |
| 四川 | 四川人事考试网 | html |
| 四川 | 四川省人力资源和社会保障厅 | html |
| 论坛 | QZZN公务员考试论坛 | rss |
| 学习 | 学习强国 | html |
| 学习 | 人民日报评论 | html |
| 学习 | 半月谈 | html |

---

## 🔒 已知限制

以下站点有 WAF 反爬保护，普通 HTTP 请求返回 412：

| 站点 | 状态 | 说明 |
|------|:----:|------|
| 湖南省税务局 | ✅ 已解决 | 使用 Playwright 无头浏览器绕过 |
| 学信网 | ⚠️ 未接入 | 需要 Playwright，暂未添加 |
| 中国学位与研究生教育信息网 | ⚠️ 未接入 | 同上 |
| B站 | ⚠️ 未接入 | 可用 RSSHub 替代 |

---

## 📝 历史版本

- **v2.0** (2026-08-19): 全面重构
  - 异步架构（asyncio + aiohttp）
  - 配置外置（YAML）
  - 抽象 Monitor/Notifier 基类
  - 支持 HTML / RSS / API / Browser 四种监控模式
  - RSS 输出（`data/feed.xml`）
  - 快照持久化 + 变更历史
  - 标准日志系统（RotatingFileHandler）
  - 错误处理 + 指数退避重试
- **v1.1** (2026-08-15): 监察国考信息
- **v1.0** (2024-03-18): 项目迁移到独立仓库、实现邮件提醒

---

## 📄 License

[Apache-2.0](LICENSE)
