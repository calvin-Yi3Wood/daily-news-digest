# 📰 智能定时资讯推送系统

> 每天早上8点自动汇总AI资讯、科技新闻、GitHub热门、金融市场、时事热点，推送到微信

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-enabled-green.svg)](https://github.com/features/actions)

---

## ✨ 核心特性

- 🤖 **智能搜索**: 基于GLM 4.6搜索智能体，自动汇总分析最新资讯
- ⏰ **定时推送**: GitHub Actions定时任务，每天早上8点自动执行
- 🕐 **⚡ 智能时间过滤（重要）**: 只推送最近24小时的最新资讯，避免过时内容
- 🔍 **多维度覆盖**: AI、科技、GitHub、金融、时事5大领域
- 🚫 **智能去重**: 自动检测重复内容，避免信息冗余
- 📱 **双通道推送**: 微信Webhook主推送 + 邮箱备用推送
- 🔒 **安全可靠**: GitHub Secrets加密存储API密钥
- 💰 **零服务器成本**: 完全基于GitHub Actions，免费运行

---

## 🕐 时间过滤逻辑（核心功能）

### 为什么需要时间过滤？
每日资讯推送的核心价值在于**及时性**。系统通过智能时间过滤，确保推送的都是**最新、最有价值的资讯**。

### GLM搜索时间过滤
**工作原理**：
- 默认只搜索**最近24小时**的资讯
- 在搜索提示中明确要求GLM过滤过时内容
- 搜索结果包含发布时间，便于用户判断新鲜度
- 自动忽略所有旧新闻和过时信息

**配置位置**：`config/config.yaml`
```yaml
glm:
  time_range: "24h"  # 24h=最近24小时（推荐）, 3d=3天, 7d=7天
```

### GitHub趋势时间过滤
**工作原理**：
- 默认只获取**最近1天**创建的热门项目
- 使用GitHub Search API的`created:>YYYY-MM-DD`过滤
- 按星标数排序，确保推送的都是最新最热门的项目

**配置位置**：`config/config.yaml`
```yaml
github:
  trending_days: 1  # 1=最近1天（推荐）, 3=3天, 7=7天
```

### 时间过滤效果示例
```
❌ 旧系统（无时间过滤）：
- OpenAI发布GPT-4（2023年3月）
- Python 3.10正式发布（2022年10月）
- React 18新特性介绍（2022年3月）

✅ 新系统（24h时间过滤）：
- OpenAI推出GPT-5（2025-11-11 10:00）
- 欧盟通过AI大模型监管新规（2025-11-11 08:30）
- 中国"模速空间"发布新一代AI平台（2025-11-11 07:15）
```

### 不同场景的推荐配置
| 场景 | GLM时间范围 | GitHub天数 | 说明 |
|------|------------|-----------|------|
| 每日推送（推荐） | 24h | 1 | 最新资讯，每天8点准时推送 |
| 半周报 | 3d | 3 | 每3天汇总一次 |
| 周报 | 7d | 7 | 每周汇总一次 |

---

## 📋 系统架构

```
GitHub Actions (定时触发)
       ↓
数据收集层 (GLM搜索 + GitHub API)
       ↓
数据处理层 (去重 + 格式化)
       ↓
推送分发层 (微信 + 邮箱)
```

详细架构设计请查看 [ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🚀 快速开始

### 前置要求

- Python 3.11+
- GitHub账号
- GLM API密钥（[注册地址](https://open.bigmodel.cn/)）
- 企业微信群机器人Webhook

### 安装步骤

#### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd daily-news-digest
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入真实API密钥
nano .env
```

**必填项**:
- `GLM_API_KEY`: 智谱AI API密钥
- `WECHAT_WEBHOOK_URL`: 企业微信Webhook URL

**详细配置指南**: 请查看 [SECURITY.md](SECURITY.md)

#### 4. 本地测试

```bash
# 测试单次运行
python main.py

# 查看配置状态
python scripts/view_config.py
```

#### 5. 配置GitHub Secrets（生产环境）

1. 访问 GitHub仓库 → Settings → Secrets and variables → Actions
2. 添加以下Secrets:
   - `GLM_API_KEY`
   - `WECHAT_WEBHOOK_URL`
   - `SMTP_PASSWORD`（可选）

#### 6. 启用GitHub Actions

推送代码到GitHub后，Actions会自动启用：

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

可以手动触发测试：
```
Actions → Daily News Digest → Run workflow
```

---

## 📊 配置说明

### 主配置文件: `config/config.yaml`

```yaml
# 修改系统参数
glm:
  max_tokens: 5000  # 摘要Token数
  search_count: 10  # 每个关键词返回结果数

deduplication:
  similarity_threshold: 0.8  # 去重相似度阈值

wechat:
  enabled: true  # 启用微信推送

email:
  enabled: false  # 启用邮箱推送
```

### 关键词配置: `config/keywords.yaml`

```yaml
categories:
  - name: "AI资讯"
    enabled: true  # 启用/禁用分类
    keywords:
      - query: "OpenAI最新动态 GPT ChatGPT"
        weight: 10

  # 添加自定义关键词
  - name: "新分类"
    enabled: true
    keywords:
      - query: "您的关键词"
        weight: 8
```

---

## 🔧 使用指南

### 查看配置状态

```bash
# 生成完整配置报告
python scripts/view_config.py

# 只查看配置摘要
python scripts/view_config.py --summary

# 只查看关键词配置
python scripts/view_config.py --keywords

# 检查环境变量
python scripts/view_config.py --env
```

### 修改推送时间

编辑 `.github/workflows/daily-news-digest.yml`:

```yaml
schedule:
  # 每天早上8点（北京时间）= UTC 0:00
  - cron: '0 0 * * *'

  # 改为早上9点（北京时间）= UTC 1:00
  # - cron: '0 1 * * *'
```

### 添加新的搜索关键词

1. 编辑 `config/keywords.yaml`
2. 在对应分类下添加新关键词
3. 提交代码，下次运行时自动生效

```yaml
keywords:
  - query: "新关键词"
    weight: 8
```

### 切换推送方式

**主推送改为邮箱**:

编辑 `config/config.yaml`:

```yaml
push_strategy:
  primary: "email"  # 改为email
  fallback: "wechat"
```

---

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| [INIT.md](INIT.md) | 📋 项目初始化文档，包含所有设计要点 |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | 🏗️ 详细架构设计和模块说明 |
| [SECURITY.md](SECURITY.md) | 🔐 安全配置指南和API密钥管理 |
| [API_GUIDE.md](docs/API_GUIDE.md) | 📡 GLM API使用指南（待创建） |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | 🚀 部署和运维指南（待创建） |

---

## 💡 常见问题

### Q1: 如何修改推送内容格式？

**A**: 编辑 `src/formatters/markdown_formatter.py` 中的模板

### Q2: 微信推送失败，提示"invalid webhook url"？

**A**: 这是最常见的问题，说明Webhook key已过期或无效。

**解决方法**：
1. 在企业微信群中重新创建机器人
   - 打开企业微信群 → 群设置 → 群机器人
   - 添加新的机器人
   - 复制新的Webhook URL

2. 更新`.env`文件
   ```bash
   WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=新的key
   ```

3. 重新测试
   ```bash
   python test_modules.py wechat
   ```

**常见原因**：
- Webhook key有有效期，定期会失效
- 企业微信群被删除或修改
- 机器人被管理员移除

**预防措施**：
- 定期检查webhook是否可用
- 在GitHub Secrets中及时更新新的webhook URL

### Q3: 如何添加更多数据源？

**A**:
1. 在 `src/collectors/` 创建新的Collector类
2. 继承 `BaseCollector` 抽象类
3. 实现 `collect()` 方法

### Q4: 如何控制成本？

**A**:
- 减少 `search_count` (每个关键词返回结果数)
- 减少 `max_tokens` (摘要Token数)
- 禁用部分分类（修改 `keywords.yaml`）

当前配置预估成本: **<¥300/年**

---

## 📈 性能优化

- ✅ 并发搜索（5个关键词同时搜索）
- ✅ 结果缓存（避免重复请求）
- ✅ 智能去重（减少冗余内容）
- ✅ 分段推送（避免超过微信20KB限制）

---

## 🛠️ 开发指南

### 项目结构

```
daily-news-digest/
├── src/                    # 源代码
│   ├── collectors/         # 数据收集模块
│   ├── formatters/         # 格式化模块
│   └── pushers/            # 推送模块
├── config/                 # 配置文件
├── docs/                   # 文档
├── scripts/                # 工具脚本
└── main.py                 # 主程序入口
```

### 添加新功能

1. 创建新的模块文件
2. 编写单元测试
3. 更新配置文件
4. 更新文档

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_glm_search.py
```

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本仓库
2. 创建Feature分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

---

## 📜 开源协议

本项目采用 MIT 协议，详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- [智谱AI](https://open.bigmodel.cn/) - 提供强大的GLM搜索智能体
- [GitHub Actions](https://github.com/features/actions) - 免费的定时任务服务
- [企业微信](https://work.weixin.qq.com/) - 稳定的Webhook推送

---

## 📞 联系方式

- **项目作者**: CMAF战略架构师
- **问题反馈**: [GitHub Issues](<your-repo-url>/issues)
- **功能建议**: [GitHub Discussions](<your-repo-url>/discussions)

---

## 🌟 Star History

如果这个项目对你有帮助，请给个Star ⭐️

[![Star History Chart](https://api.star-history.com/svg?repos=<your-repo>&type=Date)](https://star-history.com/#<your-repo>&Date)

---

**最后更新**: 2025-11-10
**版本**: V1.0
**状态**: ✅ 已完成初始化，待开发实施

> 💡 **提示**: 查看 [INIT.md](INIT.md) 了解完整的项目设计和参数配置
