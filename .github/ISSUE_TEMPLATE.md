# 依赖锁定文件说明

## ⚠️ 重要提示

`requirements-lock.txt` 必须只包含PyPI标准格式的包，不能包含：
- ❌ Conda本地路径 (`@ file:///home/conda/...`)
- ❌ 直接的wheel文件链接 (`@ https://...whl`)

## ✅ 正确格式
```
package-name==x.y.z
```

## 🔧 重新生成lock文件的方法

```bash
# 方法1：只锁定项目直接依赖（推荐）
pip list --format=freeze | grep -E "^(zhipuai|sniffio|anyio|httpx|pydantic|requests|PyYAML|feedparser|python-dateutil|beautifulsoup4|python-dotenv|typing-extensions)==" > requirements-lock.txt

# 方法2：使用虚拟环境生成干净的lock
python -m venv clean_env
source clean_env/bin/activate  # Linux/Mac
# 或 clean_env\Scripts\activate  # Windows
pip install -r requirements.txt
pip freeze > requirements-lock.txt
deactivate
```
