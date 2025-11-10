# 🔐 安全配置指南

> **重要**: API密钥是系统的核心安全资产，必须严格保护！

---

## ⚠️ 核心安全原则

### 🚫 **绝对禁止的操作**

1. **❌ 禁止在代码中硬编码API密钥**
   ```python
   # ❌ 错误示例
   api_key = "sk-xxxxxxxxxxxxxxxx"

   # ✅ 正确示例
   api_key = os.getenv('GLM_API_KEY')
   ```

2. **❌ 禁止提交 `.env` 文件到Git**
   ```bash
   # ❌ 错误操作
   git add .env
   git commit -m "add env"

   # ✅ 确保.gitignore包含
   .env
   *.env
   .env.*
   ```

3. **❌ 禁止在公开渠道分享密钥**
   - 不要在聊天软件中发送
   - 不要在截图中暴露
   - 不要在Issue/PR中粘贴

---

## 🔑 API密钥安全管理

### GitHub Secrets配置（生产环境）

**推荐方案** - 使用GitHub Secrets存储所有敏感信息

#### 步骤1: 获取API密钥

**GLM API密钥**:
1. 访问 https://open.bigmodel.cn/
2. 注册/登录账号
3. 进入"API密钥管理"
4. 点击"创建新密钥"
5. 复制密钥（**只显示一次，务必保存**）

**微信Webhook URL**:
1. 打开企业微信群聊
2. 点击群设置 → 群机器人
3. 添加机器人
4. 复制Webhook URL

#### 步骤2: 配置GitHub Secrets

**位置**:
```
GitHub仓库 → Settings → Secrets and variables → Actions → New repository secret
```

**需要添加的Secrets**:

| 名称 | 值 | 说明 |
|------|-----|------|
| `GLM_API_KEY` | `your-glm-api-key-here` | 智谱AI API密钥 |
| `WECHAT_WEBHOOK_URL` | `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx` | 微信Webhook完整URL |
| `SMTP_PASSWORD` (可选) | `your-smtp-password` | 邮箱SMTP密码或授权码 |

**添加示例截图说明**:
```
1. 点击 "New repository secret"
2. Name: GLM_API_KEY
3. Secret: 粘贴您的API密钥
4. 点击 "Add secret"
```

#### 步骤3: 在GitHub Actions中使用

**配置文件**: `.github/workflows/daily-news-digest.yml`

```yaml
jobs:
  collect-and-push:
    runs-on: ubuntu-latest

    steps:
      - name: 执行数据收集和推送
        env:
          GLM_API_KEY: ${{ secrets.GLM_API_KEY }}
          WECHAT_WEBHOOK_URL: ${{ secrets.WECHAT_WEBHOOK_URL }}
          SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
        run: |
          python main.py
```

**验证是否生效**:
```python
# 在代码中读取
import os

glm_key = os.getenv('GLM_API_KEY')
if not glm_key:
    raise ValueError("GLM_API_KEY未配置！")
```

---

### 本地开发配置

**方案**: 使用 `.env` 文件（此文件不提交Git）

#### 步骤1: 创建 `.env` 文件

```bash
# 复制模板
cp .env.example .env

# 编辑.env文件
nano .env  # 或使用任何文本编辑器
```

#### 步骤2: 填写真实密钥

**`.env` 文件内容**:
```bash
# GLM API配置
GLM_API_KEY=your-actual-glm-api-key-here

# 微信推送配置
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-key

# 邮箱推送配置（可选）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-smtp-password-or-app-password
```

#### 步骤3: 在代码中使用

**方法1: 使用 `python-dotenv` 库**（推荐）

```python
from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()

# 读取环境变量
glm_api_key = os.getenv('GLM_API_KEY')
wechat_webhook = os.getenv('WECHAT_WEBHOOK_URL')
```

**方法2: 直接读取环境变量**

```python
import os

glm_api_key = os.getenv('GLM_API_KEY')
if not glm_api_key:
    raise ValueError("请配置GLM_API_KEY环境变量")
```

---

## 🛡️ .gitignore配置

**确保以下文件/目录已加入 `.gitignore`**:

```gitignore
# 环境变量
.env
.env.*
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 日志
logs/
*.log

# 缓存
cache/
*.cache

# 临时文件
*.tmp
temp/

# 系统文件
.DS_Store
Thumbs.db
```

**验证.gitignore是否生效**:

```bash
# 检查哪些文件会被Git跟踪
git status

# 确保.env不在列表中
# 如果.env已经被跟踪，需要移除：
git rm --cached .env
git commit -m "Remove .env from tracking"
```

---

## 🔒 密钥泄露应急响应

### 如果不小心泄露了密钥：

#### 1. **立即撤销旧密钥**

**GLM API密钥**:
1. 登录 https://open.bigmodel.cn/
2. 进入"API密钥管理"
3. 找到泄露的密钥，点击"删除"
4. 创建新密钥

**微信Webhook**:
1. 企业微信群 → 群机器人
2. 删除旧机器人
3. 添加新机器人，获取新Webhook URL

#### 2. **更新GitHub Secrets**

1. 访问 GitHub仓库 → Settings → Secrets
2. 找到泄露的Secret，点击"Update"
3. 粘贴新密钥，保存

#### 3. **更新本地.env文件**

```bash
nano .env
# 替换为新密钥
```

#### 4. **检查Git历史**

**如果密钥曾被提交到Git历史**:

```bash
# 方案1: 使用git-filter-repo（推荐）
pip install git-filter-repo
git filter-repo --path .env --invert-paths

# 方案2: 使用BFG Repo-Cleaner
java -jar bfg.jar --delete-files .env

# 强制推送（谨慎操作）
git push origin --force --all
```

#### 5. **通知相关人员**

如果是团队项目，通知所有成员更新密钥。

---

## 🔐 密钥轮换策略

### 定期轮换（推荐）

**建议周期**:
- **GLM API密钥**: 每3个月轮换一次
- **微信Webhook**: 按需轮换（或每6个月）
- **SMTP密码**: 每6个月轮换一次

**轮换步骤**:
1. 生成新密钥（不删除旧密钥）
2. 更新GitHub Secrets和本地.env
3. 测试验证新密钥可用
4. 删除旧密钥

---

## 🛠️ 安全检查清单

### 部署前检查

- [ ] ✅ `.env` 文件已加入 `.gitignore`
- [ ] ✅ 代码中无硬编码密钥
- [ ] ✅ GitHub Secrets已正确配置
- [ ] ✅ `.env.example` 文件已创建（不含真实密钥）
- [ ] ✅ 本地.env文件权限设置为 `600`（Linux/Mac）

```bash
# 设置.env文件权限（仅所有者可读写）
chmod 600 .env
```

### 运行时检查

```python
# 在main.py中添加密钥检查
import os

def validate_environment():
    """验证环境变量配置"""
    required_vars = ['GLM_API_KEY', 'WECHAT_WEBHOOK_URL']

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        raise ValueError(f"缺少环境变量: {', '.join(missing)}")

    print("✅ 环境变量验证通过")

# 程序启动时调用
validate_environment()
```

---

## 📱 安全最佳实践

### 1. 使用专用API密钥

**为不同环境创建不同密钥**:
- 开发环境: 使用开发专用Key
- 生产环境: 使用生产专用Key

**好处**:
- 开发测试不影响生产
- 泄露时影响范围可控

### 2. 限制密钥权限

**GLM API**:
- 只启用必需的功能权限
- 设置调用频率限制

**GitHub Token**:
- 使用Fine-grained tokens（细粒度权限）
- 只授予必需的仓库和权限

### 3. 监控异常使用

**设置告警**:
- GLM API调用量突然增加
- 微信推送失败次数过多
- 异常时间点的API调用

### 4. 定期审计

**每月检查**:
- GitHub Secrets列表
- API密钥使用情况
- Git历史中是否有敏感信息

---

## 🚨 常见安全问题

### Q1: GitHub Secrets安全吗？

**A**: 非常安全！

- ✅ 加密存储（AES-256）
- ✅ 只有仓库Owner和Admin可访问
- ✅ Actions运行时自动注入环境变量
- ✅ 日志中自动屏蔽Secret内容

**GitHub官方说明**:
> Secrets are encrypted and only exposed to the runner environment during job execution.

### Q2: 本地.env文件丢失怎么办？

**A**: 从.env.example重新创建

```bash
cp .env.example .env
# 重新填写真实密钥
```

**备份建议**:
- 使用密码管理器（1Password/LastPass）保存密钥
- 不要依赖本地.env文件作为唯一备份

### Q3: 如何验证密钥是否生效？

**A**: 编写测试脚本

```python
# test_api_keys.py
import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv()

def test_glm_key():
    api_key = os.getenv('GLM_API_KEY')
    if not api_key:
        print("❌ GLM_API_KEY未配置")
        return False

    try:
        client = ZhipuAI(api_key=api_key)
        # 测试调用
        response = client.chat.completions.create(
            model="glm-4",
            messages=[{"role": "user", "content": "hello"}]
        )
        print("✅ GLM API密钥有效")
        return True
    except Exception as e:
        print(f"❌ GLM API密钥无效: {e}")
        return False

if __name__ == "__main__":
    test_glm_key()
```

---

## 📄 相关文档

- [INIT.md](INIT.md) - 项目初始化文档
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - 架构设计
- [.env.example](.env.example) - 环境变量模板

---

**文档版本**: V1.0
**最后更新**: 2025-11-10
**维护者**: CMAF战略架构师

> 🔐 **记住**: 安全无小事，保护好您的API密钥！
