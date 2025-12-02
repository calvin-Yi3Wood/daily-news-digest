# 📦 依赖管理指南

## 📋 文件说明

### requirements.txt （人类可读版本）
- **用途**: 定义项目需要哪些包（宽松版本约束）
- **格式**: `zhipuai>=2.0.0` （允许版本范围）
- **使用场景**: 本地开发、添加新依赖

### requirements-lock.txt （精确锁定版本）
- **用途**: 锁定所有依赖的确切版本
- **格式**: `zhipuai==2.1.5.20250801` （精确版本）
- **使用场景**: GitHub Actions、生产部署
- **优势**: 100%可复现的环境，避免"能跑就行"问题

---

## 🔧 常见操作

### 1️⃣ 本地开发环境设置

```bash
# 克隆仓库后首次安装
pip install -r requirements.txt

# 或使用锁定版本（推荐）
pip install -r requirements-lock.txt
```

### 2️⃣ 添加新依赖

```bash
# 1. 编辑 requirements.txt，添加新包
echo "new-package>=1.0.0" >> requirements.txt

# 2. 安装新包
pip install -r requirements.txt

# 3. 测试功能是否正常
python main.py

# 4. 更新锁定文件
pip freeze > requirements-lock.txt

# 5. 提交两个文件
git add requirements.txt requirements-lock.txt
git commit -m "添加新依赖: new-package"
git push
```

### 3️⃣ 升级依赖版本

```bash
# 1. 修改 requirements.txt 中的版本约束
# 例如: zhipuai>=2.0.0 → zhipuai>=2.2.0

# 2. 重新安装
pip install --upgrade -r requirements.txt

# 3. 测试功能
python main.py

# 4. 如果测试通过，更新锁定文件
pip freeze > requirements-lock.txt

# 5. 提交
git add requirements.txt requirements-lock.txt
git commit -m "升级依赖: zhipuai 2.0 → 2.2"
git push
```

### 4️⃣ 检查依赖健康状态

```bash
# 检查依赖冲突
pip check

# 查看过期的包
pip list --outdated

# 查看依赖树
pip install pipdeptree
pipdeptree
```

### 5️⃣ 清理并重建环境

```bash
# 创建新的虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装锁定版本
pip install -r requirements-lock.txt

# 验证
python main.py
```

---

## ⚠️ 重要提示

### ❌ 不要做的事

1. **不要直接编辑 requirements-lock.txt**
   - 这个文件是自动生成的
   - 手动编辑可能导致依赖冲突

2. **不要忽略 requirements-lock.txt**
   - 即使只改了一个包，也要重新生成
   - 否则CI/CD环境会不一致

3. **不要在生产环境使用 requirements.txt**
   - GitHub Actions必须使用lock文件
   - 宽松约束会导致"今天能跑明天不行"

### ✅ 最佳实践

1. **本地开发先用 requirements.txt**
   - 方便快速迭代和测试

2. **测试通过后立即更新 lock 文件**
   - 确保CI/CD环境与本地一致

3. **两个文件一起提交**
   - requirements.txt + requirements-lock.txt
   - 一个都不能少

4. **定期检查依赖安全性**
   ```bash
   pip install safety
   safety check -r requirements-lock.txt
   ```

---

## 🔍 故障排查

### 问题1: GitHub Actions安装依赖失败

**可能原因**: requirements-lock.txt 过期

**解决方法**:
```bash
# 重新生成锁定文件
pip freeze > requirements-lock.txt
git add requirements-lock.txt
git commit -m "更新依赖锁定文件"
git push
```

### 问题2: 本地能跑，GitHub Actions失败

**可能原因**: 环境不一致

**解决方法**:
```bash
# 使用与CI相同的依赖版本
pip install -r requirements-lock.txt
python main.py  # 本地验证
```

### 问题3: pip check 报告冲突

**可能原因**: 依赖版本不兼容

**解决方法**:
```bash
# 1. 卸载所有包
pip freeze > temp.txt
pip uninstall -y -r temp.txt

# 2. 重新安装
pip install -r requirements.txt

# 3. 检查冲突
pip check

# 4. 如果无冲突，更新lock文件
pip freeze > requirements-lock.txt
```

---

## 📊 当前依赖概况

**生成时间**: 2025-12-02
**总依赖数**: 208个包
**Python版本**: 3.11+

### 核心依赖版本:
- `zhipuai==2.1.5.20250801` - GLM API客户端
- `sniffio==1.3.1` - 异步I/O嗅探器
- `anyio==4.10.0` - 异步兼容层
- `httpx==0.28.1` - HTTP客户端
- `pydantic==2.11.7` - 数据验证
- `requests==2.32.3` - HTTP请求
- `PyYAML==6.0.2` - 配置文件解析
- `feedparser==6.0.11` - RSS解析
- `python-dateutil==2.9.0.post0` - 日期解析

---

## 🎯 为什么需要两个文件？

### 类比：建筑蓝图 vs 材料清单

**requirements.txt = 建筑蓝图**
- "我需要钢筋，强度≥400MPa"（版本范围）
- 给人看的，容易理解
- 允许一定灵活性

**requirements-lock.txt = 精确材料清单**
- "使用XX牌钢筋，型号YY-400-2024，批次123456"（精确版本）
- 给机器看的，100%可复现
- 确保每次建造完全一样

### 真实案例

**没有lock文件的后果**:
```
11月25日: zhipuai 2.0.5 → ✅ 推送成功
12月2日:  zhipuai 2.1.5 → ❌ 缺少sniffio，失败
```

**有lock文件的好处**:
```
11月25日: zhipuai==2.0.5 → ✅ 推送成功
12月2日:  zhipuai==2.0.5 → ✅ 推送成功（版本锁定）
```

---

## 📚 扩展阅读

- [Python依赖管理最佳实践](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
- [pip freeze文档](https://pip.pypa.io/en/stable/cli/pip_freeze/)
- [requirements.txt格式规范](https://pip.pypa.io/en/stable/reference/requirements-file-format/)
- [GitHub Actions缓存依赖](https://docs.github.com/actions/using-workflows/caching-dependencies-to-speed-up-workflows)

---

**最后更新**: 2025-12-02
**维护者**: 项目开发团队
