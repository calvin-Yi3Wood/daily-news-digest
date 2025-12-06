# 多群推送配置指南

## 📋 目录

1. [方案选择](#方案选择)
2. [方案一：相同内容推送多群（简单）](#方案一相同内容推送多群简单)
3. [方案二：不同内容推送不同群（复杂）](#方案二不同内容推送不同群复杂)
4. [获取Webhook地址](#获取webhook地址)
5. [GitHub配置](#github配置)
6. [常见问题](#常见问题)

---

## 方案选择

### 快速判断表

| 需求场景 | 推荐方案 | 复杂度 | 配置时间 |
|---------|---------|--------|---------|
| 所有群推送完全相同的内容 | **方案一** | ⭐ 简单 | 5分钟 |
| 不同群推送不同的内容 | **方案二** | ⭐⭐⭐ 复杂 | 30分钟 |
| 部分群筛选特定主题内容 | **方案二** | ⭐⭐⭐ 复杂 | 30分钟 |

### 核心区别

- **方案一**：所有群收到的内容100%相同（今日要闻、GitHub项目、科比名言都一样）
- **方案二**：可以让不同群收到不同的内容（例如：技术群只推送AI/编程新闻，金融群只推送财经新闻）

---

## 方案一：相同内容推送多群（简单）

### ✅ 优点
- 配置简单，5分钟完成
- 无需修改内容生成逻辑
- 性能影响小（每群间隔1秒）

### 📋 实施步骤

#### 步骤1：修改 `main.py`

找到 `main.py` 中的推送部分（约第380-396行），修改为：

```python
# ============================
# 🔴 修改前（单群推送）
# ============================
from src.pushers.wechat_webhook import WeChatWebhookPusher

def main():
    # ... 前面代码不变 ...

    # 6. 推送到微信
    logger.info("=== 步骤6: 推送到微信 ===")
    pusher = WeChatWebhookPusher()  # 单群推送

    success = pusher.send_in_chunks(formatted_parts)

    # ... 后面代码不变 ...


# ============================
# 🟢 修改后（多群推送）
# ============================
from src.pushers.wechat_webhook_multi_group import MultiGroupWeChatPusher

def main():
    # ... 前面代码不变 ...

    # 6. 推送到微信（多群）
    logger.info("=== 步骤6: 推送到微信（多群）===")
    pusher = MultiGroupWeChatPusher()  # 多群推送

    success = pusher.send_in_chunks(formatted_parts)

    # ... 后面代码不变 ...
```

**核心变化**：
- `WeChatWebhookPusher` → `MultiGroupWeChatPusher`
- 导入路径修改
- 其他代码完全不变

#### 步骤2：配置GitHub Secrets

访问您的GitHub仓库：
```
https://github.com/calvin-Yi3Wood/daily-news-digest/settings/secrets/actions
```

添加多个Webhook Secret：

| Secret名称 | Secret值 | 说明 |
|-----------|---------|------|
| `WECHAT_WEBHOOK_URL` | `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=XXX` | 第1个群（主群）|
| `WECHAT_WEBHOOK_URL_1` | `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YYY` | 第2个群 |
| `WECHAT_WEBHOOK_URL_2` | `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ZZZ` | 第3个群 |
| `WECHAT_WEBHOOK_URL_3` | `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=AAA` | 第4个群（可选）|

**注意**：
- 保留 `WECHAT_WEBHOOK_URL`（主群），向后兼容
- 新增群使用 `WECHAT_WEBHOOK_URL_1`, `WECHAT_WEBHOOK_URL_2`, ...
- 编号从1开始连续递增（不能跳号）

#### 步骤3：修改 `.github/workflows/daily-news-digest.yml`

在环境变量部分添加新的webhook配置：

```yaml
# ============================
# 🔴 修改前（单群配置）
# ============================
- name: Run Daily News Digest
  env:
    GLM_API_KEY: ${{ secrets.GLM_API_KEY }}
    WECHAT_WEBHOOK_URL: ${{ secrets.WECHAT_WEBHOOK_URL }}
  run: python main.py


# ============================
# 🟢 修改后（多群配置）
# ============================
- name: Run Daily News Digest
  env:
    GLM_API_KEY: ${{ secrets.GLM_API_KEY }}
    WECHAT_WEBHOOK_URL: ${{ secrets.WECHAT_WEBHOOK_URL }}
    WECHAT_WEBHOOK_URL_1: ${{ secrets.WECHAT_WEBHOOK_URL_1 }}
    WECHAT_WEBHOOK_URL_2: ${{ secrets.WECHAT_WEBHOOK_URL_2 }}
    WECHAT_WEBHOOK_URL_3: ${{ secrets.WECHAT_WEBHOOK_URL_3 }}  # 可选
  run: python main.py
```

**说明**：
- 根据实际群数添加环境变量
- 如果只有2个群，只配置到 `WECHAT_WEBHOOK_URL_1`
- 系统会自动识别可用的webhook数量

#### 步骤4：提交并推送

```bash
git add .
git commit -m "feat: 支持多群推送相同内容"
git push origin main
```

#### 步骤5：测试验证

1. 访问 GitHub Actions 页面
2. 手动触发运行（Run workflow）
3. 查看日志输出：

```
🎯 多群微信Webhook推送器初始化成功，共配置3个群
📤 开始向3个群发送Markdown消息
📨 向第1个群发送消息...
✅ 第1个群消息发送成功
📨 向第2个群发送消息...
✅ 第2个群消息发送成功
📨 向第3个群发送消息...
✅ 第3个群消息发送成功
✅ 多群推送完成：成功3/3个群
```

4. 检查所有微信群是否都收到推送

---

## 方案二：不同内容推送不同群（复杂）

### 🎯 适用场景

- **技术群**：只推送AI、编程、开源项目相关新闻
- **金融群**：只推送金融、投资、区块链相关新闻
- **综合群**：推送所有类型新闻

### 📋 实施步骤

#### 步骤1：创建群组配置文件

创建 `config/webhook_groups.yaml`：

```yaml
# 微信群组配置

groups:
  # 技术群
  - name: "技术交流群"
    webhook_env: "WECHAT_WEBHOOK_URL"
    keywords:
      - "AI"
      - "人工智能"
      - "编程"
      - "开源"
      - "GitHub"
      - "算法"
    language_filter: ["Python", "JavaScript", "Go", "Rust"]

  # 金融群
  - name: "金融投资群"
    webhook_env: "WECHAT_WEBHOOK_URL_1"
    keywords:
      - "金融"
      - "投资"
      - "区块链"
      - "股票"
      - "基金"
      - "加密货币"
    language_filter: []  # 不筛选GitHub项目语言

  # 综合群
  - name: "综合资讯群"
    webhook_env: "WECHAT_WEBHOOK_URL_2"
    keywords: []  # 空列表表示不过滤，推送所有内容
    language_filter: []
```

#### 步骤2：创建内容路由器

创建 `src/pushers/content_router.py`：

```python
"""
内容路由器 - 根据群组配置分发不同内容
"""

import os
import yaml
import logging
from typing import List, Dict
from pathlib import Path
from src.pushers.wechat_webhook import WeChatWebhookPusher

logger = logging.getLogger(__name__)


class ContentRouter:
    """内容路由器 - 向不同群推送不同内容"""

    def __init__(self, config_path: str = "config/webhook_groups.yaml"):
        """初始化内容路由器"""
        self.config_path = Path(config_path)
        self.groups = self._load_config()
        logger.info(f"✅ 内容路由器初始化成功，共配置{len(self.groups)}个群")

    def _load_config(self) -> List[Dict]:
        """加载群组配置"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"群组配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config.get('groups', [])

    def filter_content_for_group(self, content: str, keywords: List[str]) -> bool:
        """
        判断内容是否匹配群组关键词

        Args:
            content: 新闻内容
            keywords: 群组关键词列表

        Returns:
            True表示匹配，False表示不匹配
        """
        # 如果关键词列表为空，表示推送所有内容
        if not keywords:
            return True

        # 检查内容是否包含任意关键词
        content_lower = content.lower()
        for keyword in keywords:
            if keyword.lower() in content_lower:
                return True

        return False

    def filter_github_projects(self, projects: List[Dict], language_filter: List[str]) -> List[Dict]:
        """
        筛选GitHub项目

        Args:
            projects: 项目列表
            language_filter: 语言筛选列表

        Returns:
            筛选后的项目列表
        """
        if not language_filter:
            return projects

        filtered = [
            p for p in projects
            if p.get('language') in language_filter
        ]

        return filtered

    def route_and_push(self, news_content: str, github_projects: List[Dict],
                      kobe_quote: str, formatter) -> bool:
        """
        路由内容并推送到各个群

        Args:
            news_content: 原始新闻内容
            github_projects: GitHub项目列表
            kobe_quote: 科比名言
            formatter: Markdown格式化器实例

        Returns:
            True表示全部成功，False表示有失败
        """
        all_success = True

        for group in self.groups:
            group_name = group['name']
            webhook_env = group['webhook_env']
            keywords = group['keywords']
            language_filter = group['language_filter']

            logger.info(f"📨 处理群组: {group_name}")

            # 获取webhook URL
            webhook_url = os.getenv(webhook_env)
            if not webhook_url:
                logger.warning(f"⚠️ 群组 {group_name} 的webhook未配置: {webhook_env}")
                all_success = False
                continue

            # 筛选内容
            if self.filter_content_for_group(news_content, keywords):
                # 筛选GitHub项目
                filtered_projects = self.filter_github_projects(github_projects, language_filter)

                # 格式化内容
                formatted_content = formatter.format_daily_digest(
                    news_content=news_content,
                    github_projects=filtered_projects,
                    kobe_quote=kobe_quote
                )

                # 分段
                formatted_parts = formatter.split_into_chunks(formatted_content)

                # 推送
                pusher = WeChatWebhookPusher(webhook_url)
                success = pusher.send_in_chunks(formatted_parts)

                if success:
                    logger.info(f"✅ 群组 {group_name} 推送成功")
                else:
                    logger.error(f"❌ 群组 {group_name} 推送失败")
                    all_success = False
            else:
                logger.info(f"⏭️ 群组 {group_name} 无匹配内容，跳过推送")

        return all_success
```

#### 步骤3：修改 `main.py`

```python
# 在文件开头导入
from src.pushers.content_router import ContentRouter

def main():
    # ... 前面代码不变 ...

    # 5. Markdown格式化
    logger.info("=== 步骤5: Markdown格式化 ===")
    formatter = MarkdownFormatter()

    # 获取原始内容（不要立即格式化和分段）
    news_content = processed_result.get('content', '')
    github_projects = github_result.get('projects', [])
    kobe_quote = kobe_quotes.get_daily_quote()

    # 6. 内容路由和推送（替换原来的推送部分）
    logger.info("=== 步骤6: 内容路由和多群推送 ===")
    router = ContentRouter()

    success = router.route_and_push(
        news_content=news_content,
        github_projects=github_projects,
        kobe_quote=kobe_quote,
        formatter=formatter
    )

    if success:
        logger.info("✅ 所有群推送成功")
    else:
        logger.warning("⚠️ 部分群推送失败")
```

#### 步骤4：配置GitHub Secrets和Workflow

与方案一相同，配置多个webhook secret和环境变量。

#### 步骤5：提交并测试

```bash
git add .
git commit -m "feat: 支持不同群推送不同内容"
git push origin main
```

---

## 获取Webhook地址

### 步骤1：打开企业微信群聊

在电脑端或手机端打开需要推送的企业微信群。

### 步骤2：添加群机器人

1. 点击群聊右上角 **⋯** 或 **设置**
2. 选择 **群机器人**
3. 点击 **添加机器人**
4. 选择 **Webhook机器人**

### 步骤3：配置机器人

1. 输入机器人名称：`每日资讯助手`
2. 选择机器人头像（可选）
3. 点击 **完成**

### 步骤4：复制Webhook地址

创建成功后，会显示Webhook地址：

```
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**安全提醒**：
- ⚠️ 这个地址相当于密码，不要公开分享
- ⚠️ 如果泄露，请删除机器人重新创建
- ⚠️ 不要提交到GitHub代码中（使用Secrets存储）

### 步骤5：验证Webhook

在终端测试webhook是否有效：

```bash
curl -X POST "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "msgtype": "text",
    "text": {
      "content": "测试消息：机器人配置成功！"
    }
  }'
```

如果群里收到消息，说明webhook配置正确。

---

## GitHub配置

### 配置Secrets

1. 访问仓库设置页面：
   ```
   https://github.com/YOUR_USERNAME/daily-news-digest/settings/secrets/actions
   ```

2. 点击 **New repository secret**

3. 添加Secret：
   - **Name**: `WECHAT_WEBHOOK_URL_1`
   - **Value**: 粘贴webhook地址

4. 点击 **Add secret**

5. 重复步骤添加其他webhook（如有）

### 修改Workflow

编辑 `.github/workflows/daily-news-digest.yml`：

```yaml
name: Daily News Digest

on:
  schedule:
    - cron: '55 23 * * *'  # UTC 23:55 = 北京时间 07:55
  workflow_dispatch:

jobs:
  run-daily-digest:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run Daily News Digest
      env:
        GLM_API_KEY: ${{ secrets.GLM_API_KEY }}
        WECHAT_WEBHOOK_URL: ${{ secrets.WECHAT_WEBHOOK_URL }}
        WECHAT_WEBHOOK_URL_1: ${{ secrets.WECHAT_WEBHOOK_URL_1 }}  # 新增
        WECHAT_WEBHOOK_URL_2: ${{ secrets.WECHAT_WEBHOOK_URL_2 }}  # 新增
        # 根据实际群数添加更多
      run: python main.py

    - name: Upload logs
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: logs
        path: logs/
        retention-days: 7
```

---

## 常见问题

### Q1: 最多可以添加多少个群？

**A**: 理论上无限制，但建议控制在**10个以内**，原因：
- 推送时间会延长（每群间隔1秒）
- GitHub Actions有时间限制（单次运行最多6小时）
- 建议：10个群 × 3个分段 × 1秒间隔 = 约30秒，完全可接受

### Q2: 不同群可以设置不同的推送时间吗？

**A**: 不能直接实现，但有两个解决方案：

**方案A（推荐）**: 创建多个GitHub Actions workflow
- 复制 `daily-news-digest.yml` 为 `morning-digest.yml` 和 `evening-digest.yml`
- 设置不同的 cron 时间
- 配置不同的webhook环境变量

**方案B**: 在代码中添加时间判断逻辑
```python
import datetime

current_hour = datetime.datetime.now().hour

if current_hour == 8:
    # 早上8点推送到群1和群2
    webhooks = [url1, url2]
elif current_hour == 18:
    # 晚上6点推送到群3
    webhooks = [url3]
```

### Q3: 如何暂停某个群的推送？

**方法1（推荐）**: 删除对应的GitHub Secret
- 访问 Settings → Secrets
- 删除对应的 `WECHAT_WEBHOOK_URL_X`
- 系统会自动跳过未配置的群

**方法2**: 在配置文件中注释
```yaml
# 暂时不推送到技术群
# - name: "技术交流群"
#   webhook_env: "WECHAT_WEBHOOK_URL"
```

### Q4: Webhook地址过期了怎么办？

**症状**：
- 日志显示推送失败
- 错误信息：`errcode: 93000` 或 `invalid webhook url`

**解决方法**：
1. 在企业微信群删除旧机器人
2. 重新添加新机器人，获取新webhook
3. 更新GitHub Secret中的webhook地址
4. 无需修改代码

### Q5: 推送失败但日志显示成功？

**可能原因**：
- Webhook配置正确但机器人被禁用
- 群聊被解散
- 企业微信服务故障

**排查方法**：
1. 使用 curl 命令测试webhook
2. 检查企业微信群机器人状态
3. 查看企业微信管理后台

### Q6: 如何测试多群推送？

**本地测试**（推荐）：

1. 创建 `.env` 文件：
```bash
GLM_API_KEY=your_glm_api_key
WECHAT_WEBHOOK_URL=webhook_url_1
WECHAT_WEBHOOK_URL_1=webhook_url_2
WECHAT_WEBHOOK_URL_2=webhook_url_3
```

2. 运行测试：
```bash
python main.py
```

3. 检查所有群是否收到推送

**GitHub Actions测试**：
1. 访问 Actions 页面
2. 选择 workflow
3. 点击 **Run workflow**
4. 查看运行日志和群消息

---

## 🎯 推荐配置

根据您的需求，我推荐：

### 如果所有群推送相同内容 → **方案一**

**优点**：
- ✅ 配置简单，5分钟搞定
- ✅ 代码改动少，稳定性高
- ✅ 易于维护和扩展

**实施清单**：
- [ ] 修改 `main.py` 导入语句
- [ ] 配置GitHub Secrets（多个webhook）
- [ ] 修改 `daily-news-digest.yml` 环境变量
- [ ] 提交代码并测试

### 如果不同群推送不同内容 → **方案二**

**优点**：
- ✅ 高度定制化
- ✅ 内容精准推送
- ✅ 避免信息过载

**实施清单**：
- [ ] 创建 `config/webhook_groups.yaml`
- [ ] 创建 `src/pushers/content_router.py`
- [ ] 修改 `main.py` 推送逻辑
- [ ] 配置GitHub Secrets和环境变量
- [ ] 提交代码并测试

---

## 📞 需要帮助？

如果遇到问题，请提供：
1. 错误日志（GitHub Actions日志）
2. 配置文件内容（隐藏webhook地址）
3. 期望的推送行为描述

**常见错误日志位置**：
- GitHub Actions: `https://github.com/YOUR_USERNAME/daily-news-digest/actions`
- 下载日志文件：点击失败的运行 → Artifacts → logs

---

*最后更新：2025年11月10日*
