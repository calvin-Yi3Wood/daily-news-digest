# 📋 部署检查清单

## ✅ 已完成项

### 1. 核心开发
- [x] GLM搜索模块（带24小时时间过滤）
- [x] GitHub趋势模块（支持1天时间范围）
- [x] 智能去重模块
- [x] Markdown格式化模块（含科比名言）
- [x] 微信Webhook推送模块
- [x] 邮件SMTP备用推送模块
- [x] 主程序集成

### 2. 测试验证
- [x] GLM搜索测试通过（带时间戳验证）
- [x] GitHub趋势测试通过
- [x] 微信推送测试通过（新Webhook URL已配置）
- [x] 模块测试脚本创建
- [x] 完整集成测试运行中

### 3. 配置文件
- [x] `.env` 文件已配置（GLM API Key、GitHub Token、微信Webhook）
- [x] `config/config.yaml` 已优化（24h时间范围、1天趋势）
- [x] `config/keywords.yaml` 已配置（21个搜索关键词）
- [x] `config/kobe_quotes.yaml` 已创建（40条名言）

### 4. 文档完善
- [x] README.md（含时间过滤详细说明）
- [x] 微信webhook问题解决方案
- [x] 时间过滤效果对比示例
- [x] 不同场景配置推荐

### 5. 自动化
- [x] GitHub Actions workflow配置
- [x] 定时任务设置（每天UTC 0:00 = 北京8:00）
- [x] Secrets配置说明
- [x] 手动触发支持

---

## 📝 待完成项

### 1. GitHub部署
- [ ] 推送代码到GitHub仓库
- [ ] 配置GitHub Secrets（5个必需密钥）
- [ ] 启用GitHub Actions
- [ ] 手动触发测试一次

### 2. 邮件推送配置（可选）
- [ ] 配置SMTP服务器信息
- [ ] 测试邮件推送功能
- [ ] 验证备用推送机制

### 3. 监控和优化
- [ ] 首次自动运行验证
- [ ] 检查推送内容质量
- [ ] 根据需要调整关键词
- [ ] 性能优化（如需要）

---

## 🚀 GitHub部署步骤

### 步骤1: 创建GitHub仓库
```bash
# 初始化Git（如果还没有）
git init

# 添加所有文件（.env已被.gitignore排除）
git add .

# 提交
git commit -m "Initial commit: 智能定时资讯推送系统 V1.0"

# 关联远程仓库
git remote add origin https://github.com/your-username/daily-news-digest.git

# 推送到GitHub
git push -u origin main
```

### 步骤2: 配置GitHub Secrets
访问：https://github.com/your-username/daily-news-digest/settings/secrets/actions

添加以下Secrets：

| Secret名称 | 值来源 | 是否必需 |
|-----------|-------|---------|
| `GLM_API_KEY` | 智谱AI API密钥 | ✅ 必需 |
| `GITHUB_API_TOKEN` | GitHub Personal Access Token | ✅ 必需 |
| `WECHAT_WEBHOOK_URL` | 企业微信Webhook URL | ✅ 必需 |
| `SMTP_HOST` | SMTP服务器地址 | ⏸️ 可选 |
| `SMTP_PORT` | SMTP端口 | ⏸️ 可选 |
| `SMTP_USER` | SMTP用户名 | ⏸️ 可选 |
| `SMTP_PASSWORD` | SMTP密码 | ⏸️ 可选 |
| `EMAIL_TO` | 收件人邮箱 | ⏸️ 可选 |

**当前配置值**：
```
GLM_API_KEY: c761cd05b2274e449cf44a2c9b10efee.4zN8sanS5ms6vUYH
GITHUB_API_TOKEN: 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
WECHAT_WEBHOOK_URL: https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=2e3c9294-0859-4468-8070-d97802de8f6c
```

### 步骤3: 启用GitHub Actions
1. 推送代码后，访问仓库的 `Actions` 标签页
2. 点击 `I understand my workflows, go ahead and enable them`
3. 找到 `Daily News Digest` workflow
4. 点击 `Enable workflow`

### 步骤4: 手动触发测试
1. 进入 `Actions` → `Daily News Digest`
2. 点击 `Run workflow` 按钮
3. 选择分支 `main`
4. 点击 `Run workflow` 确认
5. 等待运行完成（约10-15分钟）
6. 检查微信群是否收到推送消息
7. 查看运行日志排查问题（如有）

### 步骤5: 验证自动定时任务
- 第二天早上8点检查微信群
- 确认收到最新资讯推送
- 验证内容时间戳都是最新的

---

## ⚠️ 常见问题快速参考

### Q1: 微信推送失败
**症状**: `invalid webhook url`

**解决**:
1. 企业微信群 → 群设置 → 群机器人 → 添加
2. 复制新的Webhook URL
3. 更新GitHub Secrets中的`WECHAT_WEBHOOK_URL`
4. 重新运行workflow

### Q2: GLM API调用失败
**症状**: `API key not found` 或 `401 Unauthorized`

**解决**:
1. 检查智谱AI控制台API额度
2. 确认API key正确无误
3. 更新GitHub Secrets中的`GLM_API_KEY`

### Q3: 推送的资讯还是旧的
**症状**: 资讯时间戳不是最近24小时

**解决**:
1. 检查`config/config.yaml`中的`glm.time_range`是否为`"24h"`
2. 检查`github.trending_days`是否为`1`
3. 查看推送内容，确认时间标注

### Q4: GitHub Actions没有自动运行
**症状**: 第二天没有收到推送

**解决**:
1. 检查workflow是否启用
2. 查看Actions标签页是否有报错
3. 确认cron表达式正确：`'0 0 * * *'`

---

## 📊 时间配置快速参考

### 每日推送（推荐）
```yaml
glm:
  time_range: "24h"
github:
  trending_days: 1
```

### 半周报
```yaml
glm:
  time_range: "3d"
github:
  trending_days: 3
```

### 周报
```yaml
glm:
  time_range: "7d"
github:
  trending_days: 7
```

---

## 🎯 成功标准

系统部署成功的标志：

1. ✅ GitHub Actions每天自动运行（无报错）
2. ✅ 微信群每天早上8点收到推送
3. ✅ 推送内容包含最新资讯（24小时内）
4. ✅ GitHub趋势都是最新项目（1天内）
5. ✅ 无重复内容
6. ✅ Markdown格式正确显示

---

## 📞 技术支持

- 查看日志：`logs/daily_news_digest.log`
- 模块测试：`python test_modules.py all`
- 完整运行：`python main.py`
- 问题反馈：GitHub Issues

---

**最后更新**: 2025-11-10
**版本**: V1.0
**状态**: ✅ 本地测试通过，待GitHub部署
