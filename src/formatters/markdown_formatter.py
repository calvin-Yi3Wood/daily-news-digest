"""
Markdown格式化模块 - 将收集的内容格式化为Markdown
"""

import os
import yaml
import random
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MarkdownFormatter:
    """Markdown格式化器"""

    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        初始化Markdown格式化器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.kobe_quotes = self._load_kobe_quotes()

        logger.info("Markdown格式化器初始化成功")

    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"配置文件加载失败: {str(e)}")
            return {}

    def _load_kobe_quotes(self) -> List[Dict]:
        """加载科比名言库"""
        try:
            kobe_config = self.config.get('features', {}).get('kobe_quote', {})
            if not kobe_config.get('enabled', False):
                logger.info("科比名言功能未启用")
                return []

            quotes_file = kobe_config.get('quotes_file', 'config/kobe_quotes.yaml')
            with open(quotes_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                quotes = data.get('quotes', [])
                logger.info(f"科比名言加载成功: {len(quotes)}条")
                return quotes
        except Exception as e:
            logger.error(f"科比名言加载失败: {str(e)}")
            return []

    def get_random_kobe_quote(self) -> Optional[Dict]:
        """随机选择一条科比名言"""
        if not self.kobe_quotes:
            return None

        quote = random.choice(self.kobe_quotes)
        kobe_config = self.config.get('features', {}).get('kobe_quote', {})

        return {
            'en': quote.get('en', ''),
            'zh': quote.get('zh', ''),
            'category': quote.get('category', ''),
            'format': kobe_config.get('format', 'bilingual'),
            'show_category': kobe_config.get('show_category', False)
        }

    def format_digest(
        self,
        glm_results: List[Dict],
        github_projects: List[Dict],
        date: Optional[str] = None
    ) -> str:
        """
        格式化每日资讯汇总

        Args:
            glm_results: GLM搜索结果列表
            github_projects: GitHub趋势项目列表
            date: 日期（可选，默认今天）

        Returns:
            格式化的Markdown文本
        """
        if date is None:
            date = datetime.now().strftime('%Y年%m月%d日')

        # 构建Markdown内容
        md_lines = []

        # 标题
        md_lines.append(f"# 📰 每日资讯汇总 | {date}\n")

        # GLM搜索结果
        if glm_results:
            md_lines.append("## 🔍 热点资讯\n")
            for i, result in enumerate(glm_results, 1):
                if result.get('success'):
                    query = result.get('query', '未知查询')
                    content = result.get('content', '无内容')

                    md_lines.append(f"### {i}. {query}\n")
                    md_lines.append(f"{content}\n")

        # GitHub趋势项目
        if github_projects:
            md_lines.append("## ⭐ GitHub热门项目\n")
            for i, project in enumerate(github_projects, 1):
                name = project.get('full_name', '未知项目')
                desc = project.get('description', '无描述')
                url = project.get('url', '#')
                stars = project.get('stars', 0)
                language = project.get('language', '未知')

                md_lines.append(f"{i}. **[{name}]({url})**")
                md_lines.append(f"   - ⭐ {stars:,} stars | 📝 {language}")
                md_lines.append(f"   - {desc}\n")

        # 科比名言
        kobe_quote = self.get_random_kobe_quote()
        if kobe_quote:
            md_lines.append("---\n")
            md_lines.append("## 🏀 今日名言 - Kobe Bryant\n")

            if kobe_quote['show_category']:
                md_lines.append(f"*{kobe_quote['category']}*\n")

            format_type = kobe_quote['format']
            if format_type == 'bilingual':
                md_lines.append(f"> **{kobe_quote['en']}**\n")
                md_lines.append(f"> **{kobe_quote['zh']}**\n")
            elif format_type == 'en_only':
                md_lines.append(f"> {kobe_quote['en']}\n")
            elif format_type == 'zh_only':
                md_lines.append(f"> {kobe_quote['zh']}\n")

        # 结尾
        md_lines.append("---")
        md_lines.append(f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        return '\n'.join(md_lines)

    def split_content(self, content: str, max_size: int = 1300) -> List[str]:
        """
        分割内容（防止超过微信限制）

        ⚠️ 重要: 微信Webhook的markdown.content字段限制为4096**字节**（不是字符）
        中文字符在UTF-8编码中占3字节，因此约1365个中文字符

        Args:
            content: 待分割的内容
            max_size: 最大字符数（默认1300，约3900字节，为4096留缓冲）

        Returns:
            分割后的内容列表
        """
        # 如果内容不超长，直接返回
        if len(content) <= max_size:
            return [content]

        logger.info(f"内容超长，开始分割（当前字符数: {len(content)}，字节数: {len(content.encode('utf-8'))}）")

        # 按段落分割
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)  # ✅ 改为字符数，而非字节数

            if current_size + para_size + 2 <= max_size:  # +2是因为\n\n
                current_chunk.append(para)
                current_size += para_size + 2
            else:
                # 保存当前chunk
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    logger.info(f"生成分块（字符数: {len(chunk_text)}, 字节数: {len(chunk_text.encode('utf-8'))}）")
                    chunks.append(chunk_text)

                # 开始新chunk
                current_chunk = [para]
                current_size = para_size

        # 添加最后一个chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            logger.info(f"生成最后分块（字符数: {len(chunk_text)}, 字节数: {len(chunk_text.encode('utf-8'))}）")
            chunks.append(chunk_text)

        logger.info(f"内容分割完成，共{len(chunks)}个部分")
        return chunks


# 测试代码
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试Markdown格式化
    formatter = MarkdownFormatter()

    # 测试数据
    glm_results = [
        {
            'query': 'OpenAI最新动态',
            'success': True,
            'content': '这是OpenAI的最新动态内容...'
        },
        {
            'query': 'Claude AI更新',
            'success': True,
            'content': '这是Claude AI的更新内容...'
        }
    ]

    github_projects = [
        {
            'full_name': 'user/awesome-project',
            'description': '一个很棒的开源项目',
            'url': 'https://github.com/user/awesome-project',
            'stars': 12345,
            'language': 'Python'
        }
    ]

    # 格式化
    markdown = formatter.format_digest(glm_results, github_projects)
    print("\n=== 格式化的Markdown ===\n")
    print(markdown)

    # 测试分割
    long_content = "测试" * 10000
    chunks = formatter.split_content(long_content, max_size=1000)
    print(f"\n=== 内容分割测试 ===")
    print(f"分割后部分数: {len(chunks)}")
