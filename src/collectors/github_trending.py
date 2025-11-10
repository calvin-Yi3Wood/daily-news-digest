"""
GitHub Trending模块 - 获取GitHub热门趋势项目
"""

import os
import time
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GitHubTrendingCollector:
    """GitHub趋势项目收集器"""

    def __init__(self, api_token: Optional[str] = None):
        """
        初始化GitHub趋势收集器

        Args:
            api_token: GitHub API Token，如果不提供则从环境变量读取（可选）
        """
        self.api_token = api_token or os.getenv('GITHUB_API_TOKEN')

        # 设置请求头
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if self.api_token:
            self.headers['Authorization'] = f'token {self.api_token}'

        self.base_url = 'https://api.github.com'
        self.max_retries = 3
        self.retry_delay = 5

        logger.info("GitHub趋势收集器初始化成功")

    def get_trending(
        self,
        language: Optional[str] = None,
        days: int = 7,
        top_n: int = 10,
        min_stars: int = 50  # 最低stars门槛，确保项目质量
    ) -> List[Dict]:
        """
        获取GitHub趋势项目（基于最近活跃度和受欢迎程度）

        Args:
            language: 编程语言过滤（如 'Python', 'JavaScript'），None表示所有语言
            days: 趋势时间范围（天）- 项目在此期间有过更新活动
            top_n: 返回前N个项目
            min_stars: 最低stars要求（默认50，确保项目质量）

        Returns:
            趋势项目列表
        """
        logger.info(f"获取GitHub趋势项目: language={language}, days={days}, top_n={top_n}, min_stars={min_stars}")

        # 计算日期范围
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        # 构建搜索查询
        # 使用pushed（最近更新）而非created（新创建），获取活跃的成熟项目
        query = f"pushed:>{since_date} stars:>={min_stars}"
        if language:
            query += f" language:{language}"

        for attempt in range(self.max_retries):
            try:
                # GitHub搜索API
                url = f"{self.base_url}/search/repositories"
                params = {
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': top_n
                }

                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                projects = []

                for item in data.get('items', []):
                    project = {
                        'name': item['name'],
                        'full_name': item['full_name'],
                        'description': item.get('description', '无描述'),
                        'url': item['html_url'],
                        'stars': item['stargazers_count'],
                        'language': item.get('language', '未知'),
                        'created_at': item['created_at'],
                        'topics': item.get('topics', [])
                    }
                    projects.append(project)

                logger.info(f"成功获取{len(projects)}个趋势项目")
                return projects

            except Exception as e:
                logger.error(f"获取趋势项目失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("获取趋势项目失败，已达最大重试次数")
                    return []

        return []

    def get_trending_by_languages(
        self,
        languages: List[str],
        days: int = 7,
        top_n_per_language: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        按多种语言获取趋势项目

        Args:
            languages: 编程语言列表
            days: 趋势时间范围（天）
            top_n_per_language: 每种语言返回的项目数

        Returns:
            按语言分组的趋势项目字典
        """
        logger.info(f"按多种语言获取趋势项目: {languages}")
        results = {}

        for i, language in enumerate(languages, 1):
            logger.info(f"进度: {i}/{len(languages)} - {language}")
            projects = self.get_trending(language, days, top_n_per_language)
            results[language] = projects

            # 避免请求过快（GitHub API有速率限制）
            if i < len(languages):
                time.sleep(2)

        logger.info(f"多语言趋势项目获取完成")
        return results

    def get_top_topics(self, topic: str, days: int = 7, top_n: int = 10) -> List[Dict]:
        """
        按主题获取趋势项目

        Args:
            topic: GitHub主题（如 'machine-learning', 'web-development'）
            days: 趋势时间范围（天）
            top_n: 返回前N个项目

        Returns:
            趋势项目列表
        """
        logger.info(f"按主题获取趋势项目: {topic}")

        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        query = f"topic:{topic} created:>{since_date}"

        for attempt in range(self.max_retries):
            try:
                url = f"{self.base_url}/search/repositories"
                params = {
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': top_n
                }

                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                projects = []

                for item in data.get('items', []):
                    project = {
                        'name': item['name'],
                        'full_name': item['full_name'],
                        'description': item.get('description', '无描述'),
                        'url': item['html_url'],
                        'stars': item['stargazers_count'],
                        'language': item.get('language', '未知'),
                        'topics': item.get('topics', [])
                    }
                    projects.append(project)

                logger.info(f"成功获取{len(projects)}个主题项目")
                return projects

            except Exception as e:
                logger.error(f"获取主题项目失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        return []


# 测试代码
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试GitHub趋势收集
    collector = GitHubTrendingCollector()

    # 测试单语言
    print("\n=== Python趋势项目 ===")
    python_projects = collector.get_trending('Python', days=7, top_n=5)
    for p in python_projects:
        print(f"  ⭐ {p['stars']:,} - {p['full_name']}: {p['description'][:50]}...")

    # 测试多语言
    print("\n=== 多语言趋势项目 ===")
    multi_lang_projects = collector.get_trending_by_languages(
        ['Python', 'JavaScript'],
        days=7,
        top_n_per_language=3
    )
    for lang, projects in multi_lang_projects.items():
        print(f"\n{lang}:")
        for p in projects:
            print(f"  ⭐ {p['stars']:,} - {p['full_name']}")

    # 测试主题
    print("\n=== AI主题项目 ===")
    ai_projects = collector.get_top_topics('artificial-intelligence', days=7, top_n=5)
    for p in ai_projects:
        print(f"  ⭐ {p['stars']:,} - {p['full_name']}: {p['description'][:50]}...")
