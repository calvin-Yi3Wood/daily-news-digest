"""
内容去重模块 - 基于标题相似度和URL的智能去重
"""

import logging
from typing import List, Dict, Set
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class ContentDeduplicator:
    """内容去重器"""

    def __init__(self, similarity_threshold: float = 0.8):
        """
        初始化去重器

        Args:
            similarity_threshold: 标题相似度阈值（0-1），默认0.8表示80%相似即判定为重复
        """
        self.similarity_threshold = similarity_threshold
        self.seen_urls: Set[str] = set()
        self.seen_titles: List[str] = []

        logger.info(f"内容去重器初始化成功，相似度阈值: {similarity_threshold}")

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            相似度分数（0-1）
        """
        # 统一转小写并去除空格
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()

        # 使用SequenceMatcher计算相似度
        return SequenceMatcher(None, text1, text2).ratio()

    def is_duplicate_title(self, title: str) -> bool:
        """
        检查标题是否重复

        Args:
            title: 待检查的标题

        Returns:
            True表示重复，False表示不重复
        """
        title = title.strip()

        # 与已知标题逐一比较
        for seen_title in self.seen_titles:
            similarity = self.calculate_similarity(title, seen_title)
            if similarity >= self.similarity_threshold:
                logger.debug(f"发现重复标题（相似度{similarity:.2f}）: {title} ≈ {seen_title}")
                return True

        return False

    def is_duplicate_url(self, url: str) -> bool:
        """
        检查URL是否重复

        Args:
            url: 待检查的URL

        Returns:
            True表示重复，False表示不重复
        """
        if url in self.seen_urls:
            logger.debug(f"发现重复URL: {url}")
            return True
        return False

    def add_content(self, title: str, url: str):
        """
        添加内容到去重记录

        Args:
            title: 标题
            url: URL
        """
        self.seen_titles.append(title.strip())
        self.seen_urls.add(url)

    def deduplicate(
        self,
        items: List[Dict],
        title_key: str = 'title',
        url_key: str = 'url'
    ) -> List[Dict]:
        """
        对项目列表进行去重

        Args:
            items: 待去重的项目列表
            title_key: 标题字段名
            url_key: URL字段名

        Returns:
            去重后的项目列表
        """
        logger.info(f"开始去重，原始项目数: {len(items)}")

        deduplicated = []

        for item in items:
            title = item.get(title_key, '')
            url = item.get(url_key, '')

            # 检查URL去重
            if self.is_duplicate_url(url):
                continue

            # 检查标题去重
            if self.is_duplicate_title(title):
                continue

            # 不重复，添加到结果
            deduplicated.append(item)
            self.add_content(title, url)

        logger.info(f"去重完成，剩余项目数: {len(deduplicated)}（去除{len(items) - len(deduplicated)}个重复）")
        return deduplicated

    def reset(self):
        """重置去重器"""
        self.seen_urls.clear()
        self.seen_titles.clear()
        logger.info("去重器已重置")


# 测试代码
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试去重功能
    dedup = ContentDeduplicator(similarity_threshold=0.8)

    # 测试数据
    items = [
        {'title': 'OpenAI发布GPT-4最新版本', 'url': 'https://example.com/1'},
        {'title': 'OpenAI发布GPT-4最新版本更新', 'url': 'https://example.com/2'},  # 标题相似
        {'title': 'Claude AI获得重大更新', 'url': 'https://example.com/3'},
        {'title': 'OpenAI发布GPT-4最新版本', 'url': 'https://example.com/1'},  # URL重复
        {'title': '特斯拉推出新款电动汽车', 'url': 'https://example.com/4'},
        {'title': '特斯拉发布新款电动汽车', 'url': 'https://example.com/5'},  # 标题相似
        {'title': 'GitHub推出新功能', 'url': 'https://example.com/6'},
    ]

    print(f"\n原始项目数: {len(items)}\n")

    # 执行去重
    unique_items = dedup.deduplicate(items)

    print(f"\n去重后项目数: {len(unique_items)}\n")
    print("去重后的项目:")
    for item in unique_items:
        print(f"  - {item['title']}")
