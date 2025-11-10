"""
RSS新闻收集器 - 从可靠的RSS源获取新闻
解决GLM搜索日期不可靠的问题
"""

import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


class RSSCollector:
    """RSS新闻收集器"""

    def __init__(self):
        """初始化RSS收集器"""
        # 配置可靠的中文科技新闻源
        self.feeds = {
            'AI科技': [
                'https://www.36kr.com/feed',  # 36氪
                'https://www.infoq.cn/feed',  # InfoQ中文
            ],
            '国际科技': [
                'https://techcrunch.com/feed/',  # TechCrunch
                'https://www.theverge.com/rss/index.xml',  # The Verge
            ],
            '开发者资讯': [
                'https://github.blog/feed/',  # GitHub官方博客
            ]
        }

        logger.info("RSS收集器初始化成功")

    def collect(self, hours: int = 24, max_per_feed: int = 10) -> List[Dict]:
        """
        收集最近N小时的RSS文章

        Args:
            hours: 时间范围（小时）
            max_per_feed: 每个RSS源最多取多少条

        Returns:
            文章列表，包含标题、摘要、链接、发布时间、分类
        """
        logger.info(f"开始收集RSS文章，时间范围: {hours}小时")

        cutoff_time = datetime.now() - timedelta(hours=hours)
        articles = []

        for category, urls in self.feeds.items():
            for url in urls:
                try:
                    logger.info(f"正在获取RSS: {url}")
                    feed = feedparser.parse(url)

                    if feed.bozo:
                        logger.warning(f"RSS解析警告: {url}, {feed.bozo_exception}")

                    feed_articles = 0
                    for entry in feed.entries:
                        # 解析发布时间
                        pub_date = None
                        if hasattr(entry, 'published_parsed'):
                            pub_date = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'updated_parsed'):
                            pub_date = datetime(*entry.updated_parsed[:6])
                        elif hasattr(entry, 'published'):
                            try:
                                pub_date = date_parser.parse(entry.published)
                            except Exception as e:
                                logger.debug(f"日期解析失败: {entry.get('title', '')}, {e}")

                        if not pub_date:
                            logger.debug(f"跳过无发布日期的文章: {entry.get('title', '')}")
                            continue

                        # 时间过滤：只保留指定时间范围内的文章
                        if pub_date >= cutoff_time:
                            articles.append({
                                'title': entry.get('title', '无标题'),
                                'summary': entry.get('summary', entry.get('description', ''))[:500],
                                'link': entry.get('link', ''),
                                'published': pub_date,
                                'published_str': pub_date.strftime('%Y-%m-%d %H:%M'),
                                'category': category,
                                'source': feed.feed.get('title', url)
                            })
                            feed_articles += 1

                            if feed_articles >= max_per_feed:
                                break

                    logger.info(f"从 {url} 获取了 {feed_articles} 篇文章")

                except Exception as e:
                    logger.error(f"获取RSS失败: {url}, 错误: {str(e)}")
                    continue

        # 按发布时间倒序排序
        articles.sort(key=lambda x: x['published'], reverse=True)

        logger.info(f"RSS收集完成，共{len(articles)}篇文章")
        return articles

    def format_for_glm(self, articles: List[Dict]) -> List[Dict]:
        """
        格式化为GLM处理器兼容的格式

        Args:
            articles: RSS文章列表

        Returns:
            GLM兼容格式的结果列表
        """
        # 按分类组织
        by_category = {}
        for article in articles:
            category = article['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(article)

        # 转换为GLM格式
        glm_results = []
        for category, items in by_category.items():
            content = f"\n## {category}\n\n"
            for i, article in enumerate(items, 1):
                content += f"### {i}. {article['title']} ({article['published_str']})\n"
                content += f"{article['summary']}\n"
                content += f"来源: {article['source']} | 链接: {article['link']}\n\n"

            glm_results.append({
                'success': True,
                'query': category,
                'content': content,
                'article_count': len(items)
            })

        return glm_results


# 测试代码
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    collector = RSSCollector()
    articles = collector.collect(hours=48, max_per_feed=5)

    print(f"\n收集到 {len(articles)} 篇文章\n")
    for article in articles[:5]:
        print(f"标题: {article['title']}")
        print(f"时间: {article['published_str']}")
        print(f"分类: {article['category']}")
        print(f"摘要: {article['summary'][:100]}...")
        print("-" * 80)
