# 🏗️ 系统架构详细设计

> **版本**: V1.0
> **架构师**: CMAF战略架构师
> **最后更新**: 2025-11-10

---

## 📑 目录

1. [系统概述](#系统概述)
2. [架构设计](#架构设计)
3. [模块详细设计](#模块详细设计)
4. [数据流设计](#数据流设计)
5. [API集成方案](#API集成方案)
6. [安全架构](#安全架构)
7. [性能优化](#性能优化)
8. [监控与运维](#监控与运维)

---

## 系统概述

### 核心目标
- ✅ 每天早上8点自动推送最新资讯
- ✅ 覆盖AI、科技、GitHub、金融、时事5大领域
- ✅ 智能去重，避免重复内容
- ✅ 可靠推送，支持微信和邮箱双通道

### 技术特点
- 🚀 **零服务器成本**: 基于GitHub Actions，完全免费
- 🧠 **智能搜索**: 使用GLM 4.6搜索智能体，自动汇总分析
- 🔒 **安全可靠**: GitHub Secrets加密存储API密钥
- 📊 **可扩展**: 模块化设计，易于添加新功能

---

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Actions                        │
│              (定时触发器 - Cron Scheduler)               │
│                  每天UTC 0:00触发                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  main.py (主控制器)                      │
│  - 初始化配置                                            │
│  - 调度各模块                                            │
│  - 异常处理和重试                                        │
│  - 日志记录                                              │
└────────┬────────────────────────────┬───────────────────┘
         │                            │
         ▼                            ▼
┌────────────────────┐      ┌────────────────────┐
│  数据收集层          │      │  数据处理层          │
├────────────────────┤      ├────────────────────┤
│ glm_search.py      │─────▶│ deduplicator.py    │
│ - GLM API调用      │      │ - 内容去重          │
│ - 5类关键词搜索    │      │ - 相似度计算        │
│                    │      │ - URL去重           │
├────────────────────┤      ├────────────────────┤
│ github_trending.py │─────▶│ markdown_formatter │
│ - GitHub API调用   │      │ - Markdown生成     │
│ - 趋势项目获取     │      │ - 模板渲染          │
│                    │      │ - 内容分段          │
└────────────────────┘      └─────────┬──────────┘
                                      │
                                      ▼
                            ┌────────────────────┐
                            │  推送分发层          │
                            ├────────────────────┤
                            │ wechat_webhook.py  │
                            │ - 微信推送（主）    │
                            │ - 分段发送          │
                            │ - 重试机制          │
                            ├────────────────────┤
                            │ email_sender.py    │
                            │ - 邮箱推送（备）    │
                            │ - SMTP协议          │
                            └────────────────────┘
```

### 模块依赖关系

```
main.py
  ├── collectors/
  │     ├── glm_search.py (依赖: zhipuai)
  │     ├── github_trending.py (依赖: requests)
  │     └── deduplicator.py (依赖: difflib)
  ├── formatters/
  │     └── markdown_formatter.py (依赖: jinja2)
  └── pushers/
        ├── wechat_webhook.py (依赖: requests)
        └── email_sender.py (依赖: smtplib)
```

---

## 模块详细设计

### 1. GLM搜索模块 (glm_search.py)

**职责**:
- 调用GLM 4.6搜索智能体API
- 执行5类关键词搜索
- 解析和结构化搜索结果

**核心类**: `GLMSearchCollector`

**方法**:
```python
class GLMSearchCollector:
    def __init__(self, api_key: str, max_tokens: int = 5000)

    def search_topic(self, topic: str, count: int = 10) -> dict
        """搜索单个主题"""

    def search_all_topics(self, topics: List[str]) -> List[dict]
        """批量搜索所有主题"""

    def _parse_response(self, response, topic) -> dict
        """解析GLM响应"""

    def _build_search_prompt(self, topic: str, count: int) -> str
        """构建搜索提示词"""
```

**输入**:
```python
topics = [
    "AI资讯 OpenAI Claude Gemini",
    "科技新闻 苹果 特斯拉",
    "GitHub热门AI工具",
    "金融市场 股市 加密货币",
    "时事热点 重大事件"
]
```

**输出**:
```python
{
    'topic': 'AI资讯',
    'summary': '今日AI领域有3条重要动态...',
    'articles': [
        {
            'title': 'OpenAI发布GPT-5',
            'url': 'https://...',
            'snippet': '摘要内容...',
            'publish_date': '2025-11-10'
        },
        ...
    ]
}
```

---

### 2. GitHub趋势模块 (github_trending.py)

**职责**:
- 调用GitHub REST API
- 获取高星标项目
- 按语言和时间范围过滤

**核心类**: `GitHubTrendingCollector`

**方法**:
```python
class GitHubTrendingCollector:
    def __init__(self, github_token: str = None)

    def get_trending(self, language: str = None, days: int = 7, top_n: int = 10) -> List[dict]
        """获取趋势项目"""

    def get_multi_language_trending(self, languages: List[str]) -> dict
        """多语言趋势项目"""

    def _format_project(self, repo: dict) -> dict
        """格式化项目信息"""
```

**API调用**:
```python
GET https://api.github.com/search/repositories
Parameters:
  - q: "created:>2025-11-03 language:Python"
  - sort: stars
  - order: desc
  - per_page: 10
```

**输出**:
```python
[
    {
        'name': 'openai/gpt-5',
        'url': 'https://github.com/openai/gpt-5',
        'stars': 15000,
        'description': 'GPT-5 implementation',
        'language': 'Python',
        'created_at': '2025-11-05'
    },
    ...
]
```

---

### 3. 去重模块 (deduplicator.py)

**职责**:
- 检测重复内容
- 标题相似度计算
- URL去重

**核心类**: `ContentDeduplicator`

**算法**:
```python
class ContentDeduplicator:
    def __init__(self, similarity_threshold: float = 0.8)

    def is_duplicate(self, article: dict) -> bool
        """判断是否重复"""

    def deduplicate(self, articles: List[dict]) -> List[dict]
        """批量去重"""

    def _calculate_similarity(self, text1: str, text2: str) -> float
        """计算文本相似度（使用SequenceMatcher）"""
```

**去重策略**:

1. **URL完全匹配去重**:
   ```python
   if article['url'] in self.seen_urls:
       return True  # 重复
   ```

2. **标题相似度去重**（编辑距离算法）:
   ```python
   similarity = SequenceMatcher(None, title1, title2).ratio()
   if similarity > 0.8:  # 80%相似即认为重复
       return True
   ```

3. **时间窗口去重**（可选）:
   ```python
   # 24小时内同一事件只保留最新
   if same_event and time_diff < 24h:
       keep_latest()
   ```

---

### 4. Markdown格式化模块 (markdown_formatter.py)

**职责**:
- 生成Markdown格式内容
- 使用Jinja2模板渲染
- 内容分段（避免超过微信20KB限制）

**核心类**: `MarkdownFormatter`

**模板**:
```jinja2
# 📰 每日资讯汇总 | {{ date }}

> 自动生成时间：{{ generated_time }}

---

{% for category in categories %}
## {{ category.icon }} {{ category.name }}

**关键要点**：
{% for point in category.key_points %}
- {{ point }}
{% endfor %}

**详细内容**：
{% for article in category.articles %}
{{ loop.index }}. [{{ article.title }}]({{ article.url }})
   > {{ article.snippet }}
   > 📅 {{ article.publish_date }}

{% endfor %}
---

{% endfor %}

> 💡 数据来源：智谱AI、GitHub API

{% if kobe_quote and kobe_quote.enabled %}
---

## 🏀 今日名言 - Kobe Bryant

{% if kobe_quote.format == 'bilingual' %}
> **{{ kobe_quote.en }}**
>
> **{{ kobe_quote.zh }}**
{% elif kobe_quote.format == 'en_only' %}
> **{{ kobe_quote.en }}**
{% elif kobe_quote.format == 'zh_only' %}
> **{{ kobe_quote.zh }}**
{% endif %}

{% if kobe_quote.show_category %}
*— 分类：{{ kobe_quote.category }}*
{% endif %}
{% endif %}
```

**科比名言功能**:
```python
def get_random_kobe_quote(self) -> dict:
    """
    从科比名言库中随机选择一条名言

    Returns:
        {
            'id': 1,
            'category': '梦想与目标',
            'en': 'English quote',
            'zh': '中文名言',
            'enabled': True,
            'format': 'bilingual',
            'show_category': False
        }
    """
    import random
    import yaml

    # 读取配置
    config = load_yaml('config/config.yaml')
    kobe_config = config.get('features', {}).get('kobe_quote', {})

    if not kobe_config.get('enabled', False):
        return None

    # 读取名言库
    quotes = load_yaml('config/kobe_quotes.yaml')
    quote_list = quotes.get('quotes', [])

    # 随机选择
    selected = random.choice(quote_list)

    # 添加配置信息
    selected.update({
        'enabled': True,
        'format': kobe_config.get('format', 'bilingual'),
        'show_category': kobe_config.get('show_category', False)
    })

    return selected
```

**分段策略**:
```python
def split_content(self, content: str, max_size: int = 20000) -> List[str]:
    """
    按章节分段，确保每段<20KB
    """
    sections = content.split('## ')
    chunks = []
    current_chunk = ""

    for section in sections:
        if len(current_chunk) + len(section) < max_size:
            current_chunk += '## ' + section
        else:
            chunks.append(current_chunk)
            current_chunk = '## ' + section

    return chunks
```

---

### 5. 微信推送模块 (wechat_webhook.py)

**职责**:
- 调用企业微信Webhook API
- 发送Markdown格式消息
- 处理大内容分段
- 重试机制

**核心类**: `WeChatWebhookPusher`

**API调用**:
```python
POST https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx

Request Body:
{
    "msgtype": "markdown",
    "markdown": {
        "content": "# 标题\n## 内容..."
    }
}
```

**重试策略**:
```python
@retry(max_attempts=3, delay=5)
def _send_single_message(self, content: str):
    """
    发送单条消息，失败自动重试
    """
    response = requests.post(self.webhook_url, json=payload)
    if response.json()['errcode'] != 0:
        raise PushError("推送失败")
```

---

### 6. 邮箱推送模块 (email_sender.py)

**职责**:
- SMTP协议发送邮件
- 支持HTML和纯文本格式
- 备用推送通道

**核心类**: `EmailSender`

**方法**:
```python
class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int,
                 username: str, password: str)

    def send_email(self, to_email: str, subject: str,
                   content: str, content_type: str = 'html')
        """发送邮件"""
```

**SMTP配置**（常见服务商）:
```yaml
Gmail:
  server: smtp.gmail.com
  port: 587
  tls: true

QQ邮箱:
  server: smtp.qq.com
  port: 587
  tls: true

163邮箱:
  server: smtp.163.com
  port: 465
  ssl: true
```

---

## 数据流设计

### 完整数据流程

```
1. GitHub Actions触发
   └─> main.py启动

2. 读取配置
   ├─> config/config.yaml
   └─> config/keywords.yaml

3. 数据收集
   ├─> GLMSearchCollector.search_all_topics()
   │   ├─> 搜索"AI资讯" → 返回10条结果
   │   ├─> 搜索"科技新闻" → 返回10条结果
   │   ├─> 搜索"金融市场" → 返回10条结果
   │   └─> 搜索"时事热点" → 返回10条结果
   │
   └─> GitHubTrendingCollector.get_trending()
       └─> 返回10个高星项目

4. 数据处理
   ├─> ContentDeduplicator.deduplicate()
   │   ├─> URL去重：去除3条重复
   │   └─> 标题相似度去重：去除5条重复
   │
   └─> MarkdownFormatter.format()
       ├─> 使用Jinja2模板渲染
       ├─> 生成15KB Markdown内容
       └─> 检查大小：<20KB，无需分段

5. 推送分发
   ├─> WeChatWebhookPusher.push()
   │   ├─> 发送到微信群
   │   └─> 返回成功
   │
   └─> (可选) EmailSender.send_email()
       └─> 备用邮箱推送

6. 记录日志
   └─> 写入logs/2025-11-10.log
```

### 数据结构定义

**文章数据结构**:
```python
@dataclass
class Article:
    title: str
    url: str
    snippet: str
    publish_date: str
    source: str  # 'glm' or 'github'
    category: str  # 'AI', '科技', 'GitHub', '金融', '时事'
```

**汇总数据结构**:
```python
@dataclass
class DailyDigest:
    date: str
    generated_time: str
    categories: List[Category]
    total_articles: int
    duplicate_removed: int
```

---

## API集成方案

### GLM 4.6 API集成

**官方文档**: https://docs.bigmodel.cn/

**认证方式**:
```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key=os.getenv('GLM_API_KEY'))
```

**调用搜索智能体**:
```python
response = client.assistant.conversation(
    assistant_id="659e54b1b8006379b4b2abd6",  # 搜索智能体ID
    model="glm-4-assistant",
    messages=[{
        "role": "user",
        "content": [{
            "type": "text",
            "text": search_prompt
        }]
    }],
    stream=False
)
```

**Token计费**:
- 输入: ¥0.01 / 1K tokens
- 输出: ¥0.03 / 1K tokens
- 每日预估: 30K tokens ≈ ¥0.6/天

### GitHub API集成

**官方文档**: https://docs.github.com/rest

**认证方式**（可选，提高速率限制）:
```python
headers = {
    'Authorization': f'token {github_token}',
    'Accept': 'application/vnd.github.v3+json'
}
```

**速率限制**:
- 未认证: 60次/小时
- 已认证: 5000次/小时
- 本项目需求: 1次/天（远低于限制）

---

## 安全架构

### 密钥管理

**三层安全防护**:

1. **开发环境**: `.env` 文件（不提交Git）
2. **生产环境**: GitHub Secrets（加密存储）
3. **代码层**: 使用环境变量，禁止硬编码

**密钥轮换策略**:
```yaml
GLM_API_KEY:
  轮换周期: 每季度
  轮换方式: 在智谱AI平台生成新Key，更新GitHub Secret

WECHAT_WEBHOOK_URL:
  轮换周期: 按需（泄露时立即）
  轮换方式: 重新生成企业微信机器人
```

### 权限最小化

**GitHub Actions权限**:
```yaml
permissions:
  contents: read  # 只读代码
  actions: write  # 写入Action日志
```

**API权限**:
- GLM API: 只需搜索权限
- GitHub API: 只需公开仓库读权限

---

## 性能优化

### 并发优化

**并行搜索**（5个关键词同时搜索）:
```python
import asyncio

async def search_all_topics_async(topics):
    tasks = [search_topic_async(topic) for topic in topics]
    results = await asyncio.gather(*tasks)
    return results

# 耗时: 串行10秒 → 并行2秒
```

### 缓存策略

**GitHub Trending缓存**（避免重复请求）:
```python
# 缓存1小时
cache_file = f"cache/github_trending_{date}.json"
if os.path.exists(cache_file):
    return load_cache(cache_file)
```

### 错误重试

**指数退避重试**:
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def api_call_with_retry():
    # API调用
    pass
```

---

## 监控与运维

### 日志系统

**日志级别**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/{date}.log'),
        logging.StreamHandler()
    ]
)
```

**日志内容**:
- INFO: 正常流程（开始搜索、推送成功）
- WARNING: 去重数量、分段发送
- ERROR: API调用失败、推送失败

### 告警机制

**GitHub Actions失败通知**:
```yaml
- name: 发送失败通知
  if: failure()
  run: |
    curl -X POST ${{ secrets.WECHAT_WEBHOOK_URL }} \
    -d '{"msgtype":"text","text":{"content":"❌ 定时推送失败！"}}'
```

### 运行监控

**关键指标**:
- ✅ 执行成功率: 目标99%+
- ⏱️ 执行时间: 目标<3分钟
- 📊 去重率: 正常10-20%
- 💰 Token消耗: 预算30K/天

---

## 扩展性设计

### 新增数据源

**插件化设计**:
```python
# src/collectors/base_collector.py
class BaseCollector(ABC):
    @abstractmethod
    def collect(self) -> List[Article]:
        pass

# 新增Twitter数据源
class TwitterCollector(BaseCollector):
    def collect(self) -> List[Article]:
        # 实现Twitter API调用
        pass
```

### 新增推送通道

```python
# src/pushers/telegram_pusher.py
class TelegramPusher:
    def push(self, content: str):
        # 实现Telegram Bot推送
        pass
```

---

**文档版本**: V1.0
**维护者**: CMAF战略架构师
**最后更新**: 2025-11-10
