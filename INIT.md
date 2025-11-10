# 📋 项目初始化文档 (INIT.md)

> **版本**: V1.0
> **创建时间**: 2025-11-10
> **项目代号**: Daily-News-Digest
> **架构师**: CMAF战略架构师

---

## 🎯 项目概述

**项目名称**: 智能定时资讯推送系统
**核心功能**: 每天早上8点自动汇总AI资讯、科技新闻、GitHub热门项目、金融市场、时事热点，并推送到微信（支持邮箱备选）

**技术栈**:
- GLM 4.6 Search API（智谱AI搜索引擎）
- GitHub Actions（定时任务调度）
- Python 3.11+
- 微信企业Webhook（主推送）
- SMTP邮箱（备选推送）

---

## 📊 核心参数配置

### 系统配置
```yaml
摘要Token数: 5000 tokens/次（标准版）
搜索结果数: 10条/关键词
定时触发: 每天UTC 0:00（北京时间8:00）
去重策略: 标题相似度80%阈值 + URL完全匹配
```

### 搜索关键词清单
```yaml
1. AI资讯类:
   - OpenAI最新动态
   - Claude/Gemini更新
   - 国内大模型（智谱/月之暗面/百川等）

2. 科技新闻类:
   - 苹果/特斯拉/Meta等科技巨头
   - 科技政策和监管
   - 创新产品发布

3. GitHub开源项目:
   - 高星标AI工具
   - 热门开发框架
   - 趋势技术项目

4. 金融市场类:
   - 股市行情（A股/美股）
   - 加密货币动态
   - 经济政策和数据

5. 时事热点:
   - 国内外重大事件
   - 社会民生新闻
   - 科学突破
```

---

## 🏗️ 系统架构

### 三层架构设计

```
┌─────────────────────────────────────────┐
│  Layer 1: 定时触发层                     │
│  - GitHub Actions (Cron: 0 0 * * *)    │
│  - 每天8点北京时间触发                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Layer 2: 数据收集与汇总层               │
│  - GLM 4.6 Web Search API              │
│  - GitHub Trending API                 │
│  - 内容去重模块                          │
│  - Markdown格式化                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Layer 3: 推送分发层                     │
│  - 微信Webhook (主推送)                 │
│  - SMTP邮箱 (备选)                      │
│  - 失败重试机制                          │
└─────────────────────────────────────────┘
```

### 目录结构

```
daily-news-digest/
├── .github/
│   └── workflows/
│       └── daily-news-digest.yml      # GitHub Actions配置
├── src/
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── glm_search.py             # GLM搜索模块
│   │   ├── github_trending.py        # GitHub趋势爬取
│   │   └── deduplicator.py           # 去重模块
│   ├── formatters/
│   │   ├── __init__.py
│   │   └── markdown_formatter.py     # Markdown格式化
│   └── pushers/
│       ├── __init__.py
│       ├── wechat_webhook.py         # 微信推送
│       └── email_sender.py           # 邮箱推送
├── config/
│   ├── config.yaml                   # 主配置文件
│   └── keywords.yaml                 # 搜索关键词配置
├── docs/
│   ├── ARCHITECTURE.md               # 架构详细文档
│   ├── API_GUIDE.md                  # API使用指南
│   └── DEPLOYMENT.md                 # 部署指南
├── logs/                             # 日志目录（.gitignore）
├── .env.example                      # 环境变量示例
├── .gitignore                        # Git忽略文件
├── INIT.md                           # 本文档
├── README.md                         # 项目说明
├── SECURITY.md                       # 安全指南
├── requirements.txt                  # Python依赖
└── main.py                           # 主程序入口
```

---

## 🔐 安全配置指南

### ⚠️ **重要：API密钥绝对不能直接提交到Git仓库！**

### GitHub Secrets配置（推荐方案）

**位置**: GitHub仓库 → Settings → Secrets and variables → Actions → New repository secret

**需要配置的密钥**:

1. **GLM_API_KEY**
   - 名称: `GLM_API_KEY`
   - 值: 智谱AI的API密钥
   - 获取方式: https://open.bigmodel.cn/

2. **WECHAT_WEBHOOK_URL**
   - 名称: `WECHAT_WEBHOOK_URL`
   - 值: 企业微信群机器人Webhook URL
   - 获取方式: 企业微信群 → 添加群机器人 → 复制Webhook

3. **SMTP_PASSWORD**（可选）
   - 名称: `SMTP_PASSWORD`
   - 值: 邮箱SMTP密码或授权码
   - 用途: 备用邮箱推送

**在GitHub Actions中使用**:
```yaml
env:
  GLM_API_KEY: ${{ secrets.GLM_API_KEY }}
  WECHAT_WEBHOOK_URL: ${{ secrets.WECHAT_WEBHOOK_URL }}
```

### 本地开发配置

**使用 `.env` 文件**（此文件已加入.gitignore）:

```bash
# .env（本地开发用，不提交到Git）
GLM_API_KEY=your-glm-api-key-here
WECHAT_WEBHOOK_URL=your-wechat-webhook-url-here
SMTP_PASSWORD=your-smtp-password-here
```

**安全检查清单**:
- ✅ `.env` 已加入 `.gitignore`
- ✅ 提供了 `.env.example` 作为模板
- ✅ 使用 GitHub Secrets 存储生产环境密钥
- ✅ 代码中使用 `os.getenv()` 读取环境变量

---

## 📈 成本估算

### GLM API费用
```yaml
每日调用:
  - 5个关键词 × 10条结果 = 50条搜索
  - Token消耗: 6000 tokens/关键词
  - 总消耗: 30,000 tokens/天

月度费用:
  - GLM-4-assistant: ¥15-20/月

年度费用:
  - GLM API: ¥180-240/年
  - GitHub Actions: 免费（2000分钟/月）
  - 微信Webhook: 免费

总计: < ¥300/年
```

---

## 🚀 快速启动步骤

### 步骤1: 克隆仓库（待创建后）
```bash
git clone <your-repo-url>
cd daily-news-digest
```

### 步骤2: 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入真实的API密钥
nano .env
```

### 步骤3: 安装依赖
```bash
pip install -r requirements.txt
```

### 步骤4: 本地测试
```bash
# 测试单次运行
python main.py

# 测试GLM搜索模块
python -m src.collectors.glm_search

# 测试微信推送
python -m src.pushers.wechat_webhook
```

### 步骤5: 配置GitHub Secrets
1. 访问 GitHub仓库 → Settings → Secrets
2. 添加 `GLM_API_KEY`
3. 添加 `WECHAT_WEBHOOK_URL`
4. （可选）添加 `SMTP_PASSWORD`

### 步骤6: 启用GitHub Actions
1. 提交代码到GitHub
2. Actions会自动启用
3. 可以手动触发测试：Actions → Daily News Digest → Run workflow

---

## 📝 配置文件说明

### config/config.yaml
```yaml
# 主配置文件
system:
  max_tokens: 5000
  search_count: 10
  similarity_threshold: 0.8
  timezone: "Asia/Shanghai"

schedule:
  cron: "0 0 * * *"  # UTC 0:00 = 北京8:00

glm:
  model: "glm-4-assistant"
  assistant_id: "659e54b1b8006379b4b2abd6"
  temperature: 0.6
```

### config/keywords.yaml
```yaml
# 搜索关键词配置（可随时修改）
categories:
  - name: "AI资讯"
    keywords:
      - "OpenAI最新动态"
      - "Claude Gemini更新"
      - "国内大模型 智谱 月之暗面"

  - name: "科技新闻"
    keywords:
      - "苹果 特斯拉 Meta 最新消息"
      - "科技政策"

  - name: "GitHub热门"
    languages:
      - "Python"
      - "JavaScript"
      - "TypeScript"
    days: 7
    top_n: 10

  - name: "金融市场"
    keywords:
      - "A股 美股 行情"
      - "比特币 以太坊"

  - name: "时事热点"
    keywords:
      - "国内外重大事件"
      - "科学突破"
```

### config/kobe_quotes.yaml
```yaml
# 科比·布莱恩特名言库（中英双语）
quotes:
  - id: 1
    category: "梦想与目标"
    en: "Everything negative - pressure, challenges - is all an opportunity for me to rise."
    zh: "所有负面的东西——压力、挑战——对我来说都是崛起的机会。"

  - id: 8
    category: "自律与专注"
    en: "Have you ever seen the scene of Los Angeles at 4 am?"
    zh: "你见过洛杉矶凌晨四点的样子吗？"

  # 共40条精选名言，涵盖12个分类
  # 每日推送结尾随机选择一条显示
```

**功能配置** (config/config.yaml):
```yaml
features:
  kobe_quote:
    enabled: true           # 启用科比名言
    format: "bilingual"     # 双语显示（中英文）
    selection: "random"     # 随机选择
    show_category: false    # 不显示分类标签
```

---

## 🔄 随时查看和对齐机制

### 机制1: 文档快速导航

**命令行快速查看**:
```bash
# 查看初始化文档
cat INIT.md

# 查看架构详情
cat docs/ARCHITECTURE.md

# 查看当前配置
cat config/config.yaml

# 查看搜索关键词
cat config/keywords.yaml
```

**IDE快速导航**:
- VSCode: `Ctrl+P` → 输入 `INIT.md`
- 侧边栏 → 点击 `INIT.md`

### 机制2: 配置同步脚本

创建 `scripts/sync_config.py` 用于检查配置一致性：
```python
# 检查本地配置和GitHub Secrets是否对齐
python scripts/sync_config.py --check

# 显示当前配置摘要
python scripts/sync_config.py --summary
```

### 机制3: 配置版本控制

**配置文件都使用Git版本控制**（除了包含密钥的 `.env`）:
```bash
# 查看配置变更历史
git log config/config.yaml

# 回滚到上一个配置版本
git checkout HEAD~1 config/config.yaml
```

### 机制4: 定期对齐检查

**每周自动检查**（可选，通过GitHub Actions）:
```yaml
# 每周一早上检查配置一致性
schedule:
  - cron: "0 1 * * 1"
```

---

## 🎯 项目里程碑

### Phase 1: 基础功能（已完成）
- ✅ 需求分析
- ✅ 架构设计
- ✅ 技术选型
- ✅ 参数确认
- ✅ 初始化文档

### Phase 2: 核心开发（进行中）
- ⏳ 项目目录创建
- ⏳ 核心模块编写
- ⏳ 单元测试
- ⏳ 集成测试

### Phase 3: 部署上线（待开始）
- ⏳ GitHub仓库创建
- ⏳ GitHub Actions配置
- ⏳ Secrets配置
- ⏳ 首次运行验证

### Phase 4: 优化增强（未来）
- ⏳ 邮箱推送备选
- ⏳ 内容质量优化
- ⏳ 监控告警
- ⏳ 个性化推荐

---

## 📞 支持与反馈

### 常见问题

**Q1: 如何修改推送时间？**
A: 编辑 `.github/workflows/daily-news-digest.yml`，修改 `cron` 表达式。

**Q2: 如何添加新的搜索关键词？**
A: 编辑 `config/keywords.yaml`，添加新的关键词即可。

**Q3: 微信推送失败怎么办？**
A: 检查 Webhook URL 是否正确，查看日志文件 `logs/latest.log`。

**Q4: 如何切换到邮箱推送？**
A: 在 `config/config.yaml` 中设置 `pusher: email`。

### 联系方式

- **架构师**: CMAF战略架构师
- **技术支持**: 查看 `docs/` 目录下的详细文档
- **问题反馈**: GitHub Issues

---

## 📄 相关文档

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - 架构详细设计
- [SECURITY.md](SECURITY.md) - 安全配置指南
- [API_GUIDE.md](docs/API_GUIDE.md) - GLM API使用指南
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - 部署和运维指南
- [README.md](README.md) - 项目README

---

**最后更新**: 2025-11-10
**文档版本**: V1.0
**维护者**: CMAF战略架构师
