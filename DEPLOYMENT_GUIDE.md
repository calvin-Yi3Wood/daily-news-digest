# 🚀 完整部署指南

## 📋 部署前检查清单

### ✅ 已完成的准备工作

- [x] **项目结构完整** - 所有核心模块已就绪
- [x] **依赖项完整** - requirements.txt 包含所有依赖
- [x] **配置文件完整** - config.yaml、keywords.yaml、kobe_quotes.yaml
- [x] **GitHub Actions配置** - .github/workflows/daily-news-digest.yml
- [x] **安全配置** - .gitignore 正确配置，防止泄露密钥
- [x] **核心功能验证** - RSS收集、GitHub热门、GLM处理、科比名言
- [x] **代码质量** - 质量得分 90.7/100

---

## 🔧 部署步骤

### 步骤1：初始化Git仓库（如果还未初始化）

```bash
# 进入项目目录
cd "D:\项目库\定时任务推送（微信-邮箱）"

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 创建初始提交
git commit -m "🎉 Initial commit: 智能定时资讯推送系统

✨ 功能特性:
- 📰 RSS新闻聚合（36kr、InfoQ、TechCrunch等）
- ⭐ GitHub热门项目（自动筛选高质量项目）
- 🤖 GLM-4-Plus智能内容处理
- 🏀 科比名言每日推送
- 📱 企业微信Webhook推送
- 🔄 GitHub Actions自动化定时任务

📊 质量保证:
- 代码质量得分: 90.7/100
- 测试覆盖: 核心功能完整验证
- 安全防护: 敏感信息保护完善"
```

### 步骤2：创建GitHub仓库并推送

**方法A：通过GitHub网页创建（推荐）**

1. 访问 https://github.com/new
2. 仓库名称：`daily-news-digest`
3. 描述：智能定时资讯推送系统 - 每日自动推送科技资讯到企业微信
4. 选择"Private"（推荐）或"Public"
5. **不要**勾选"Initialize this repository with a README"
6. 点击"Create repository"

7. 在本地执行：
```bash
git remote add origin https://github.com/YOUR_USERNAME/daily-news-digest.git
git branch -M main
git push -u origin main
```

**方法B：使用GitHub CLI（如果已安装）**

```bash
gh repo create daily-news-digest --private --source=. --remote=origin
git push -u origin main
```

### 步骤3：配置GitHub Secrets

访问仓库页面：`https://github.com/YOUR_USERNAME/daily-news-digest/settings/secrets/actions`

点击"New repository secret"，逐个添加以下密钥：

#### 必需的Secrets：

1. **GLM_API_KEY**
   - Value: 你的智谱AI API密钥
   - 获取地址: https://open.bigmodel.cn/

2. **WECHAT_WEBHOOK_URL**
   - Value: 企业微信机器人Webhook地址
   - 格式: `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=XXXXXXX`
   - 获取方法: 企业微信 → 群聊 → 群机器人 → 添加机器人

#### 可选的Secrets（备用邮件推送）：

3. **GITHUB_API_TOKEN** （可选）
   - Value: GitHub Personal Access Token
   - 用途: 提高GitHub API速率限制
   - 获取地址: https://github.com/settings/tokens

4. **SMTP_HOST**、**SMTP_PORT**、**SMTP_USER**、**SMTP_PASSWORD**、**EMAIL_TO**
   - 如果需要邮件备用推送，配置这些

### 步骤4：启用GitHub Actions

1. 访问仓库的"Actions"标签页
2. 如果看到"Workflows aren't being run on this forked repository"，点击"I understand my workflows, go ahead and enable them"
3. 确认看到"Daily News Digest"工作流

### 步骤5：测试手动触发

1. 进入"Actions" → "Daily News Digest"
2. 点击"Run workflow"下拉菜单
3. 选择"main"分支
4. 点击"Run workflow"按钮
5. 等待约2-3分钟，查看运行结果
6. 检查企业微信是否收到推送

---

## ⏰ 定时任务说明

**当前配置**：每天UTC 23:55（北京时间 7:55）

GitHub Actions会自动执行以下流程：
1. 7:55 启动任务
2. 7:56 安装依赖
3. 7:57-8:02 收集新闻、处理内容
4. 8:00 推送到企业微信

**修改执行时间**：
编辑 `.github/workflows/daily-news-digest.yml` 第9行的cron表达式：
```yaml
schedule:
  - cron: '55 23 * * *'  # UTC时间，北京时间+8小时
```

常用时间对照：
- 北京时间 08:00 → UTC 00:00 → `'0 0 * * *'`
- 北京时间 09:00 → UTC 01:00 → `'0 1 * * *'`
- 北京时间 18:00 → UTC 10:00 → `'0 10 * * *'`

---

## 🔍 故障排查

### 推送失败

1. 检查GitHub Actions日志
   - Actions → 最新运行 → 查看详细日志
2. 验证Secrets配置
   - Settings → Secrets and variables → Actions
3. 测试微信Webhook
   ```bash
   curl -X POST "YOUR_WEBHOOK_URL" \
     -H "Content-Type: application/json" \
     -d '{"msgtype":"markdown","markdown":{"content":"测试"}}'
   ```

### 内容质量问题

1. RSS源失效
   - 检查 `src/collectors/rss_collector.py` 的feeds列表
   - 替换或添加新的RSS源

2. GitHub项目质量低
   - 调整 `src/collectors/github_trending.py` 的min_stars参数
   - 当前默认50，可提高到100或200

### API限制问题

1. GLM API额度不足
   - 检查智谱AI控制台额度
   - 升级API套餐

2. GitHub API速率限制
   - 配置GITHUB_API_TOKEN Secret
   - 或减少每个语言的top_n参数

---

## 📊 监控和维护

### 日志查看

GitHub Actions自动保存运行日志（保留7天）：
- Actions → 运行记录 → Artifacts → logs-XXX

### 性能监控

关键指标：
- RSS收集时间：< 5秒
- GitHub收集时间：< 15秒
- GLM处理时间：30-60秒
- 总执行时间：< 2分钟

### 定期维护

**每月**：
- 检查RSS源可用性
- 更新失效的RSS订阅源
- 检查推送内容质量

**每季度**：
- 更新依赖包版本
- 检查GitHub Actions配置
- 优化关键词列表

---

## 🎯 自定义配置

### 修改新闻源

编辑 `src/collectors/rss_collector.py`：
```python
self.feeds = {
    'AI科技': [
        'https://www.36kr.com/feed',
        'https://www.infoq.cn/feed',
        # 添加你的RSS源
    ],
    '国际科技': [
        'https://techcrunch.com/feed/',
        # 添加更多
    ]
}
```

### 修改GitHub语言

编辑 `config/config.yaml`：
```yaml
github:
  languages:
    - "Python"
    - "JavaScript"
    - "TypeScript"
    # 添加或删除语言
```

### 修改科比名言库

编辑 `config/kobe_quotes.yaml`，添加更多名言。

---

## 🆘 需要帮助？

1. 查看项目文档：`docs/ARCHITECTURE.md`
2. 检查测试脚本：运行 `python test_content_preview.py`
3. 质量检查：运行 `python quality_check.py`
4. 安全指南：查看 `SECURITY.md`

---

## ✅ 部署完成检查

- [ ] Git仓库已推送到GitHub
- [ ] GitHub Secrets已全部配置
- [ ] GitHub Actions已启用
- [ ] 手动测试运行成功
- [ ] 企业微信收到测试推送
- [ ] 定时任务时间已确认

**恭喜！🎉 部署成功！每天早上自动收到精选资讯！**
