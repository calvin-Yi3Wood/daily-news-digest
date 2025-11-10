"""
GLM Web Search模块 - 使用智谱AI Web Search功能
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from zhipuai import ZhipuAI

logger = logging.getLogger(__name__)


class GLMSearchCollector:
    """GLM搜索收集器 - 使用智谱AI的Web Search"""

    def __init__(self, api_key: Optional[str] = None, time_range: str = "24h"):
        """
        初始化GLM搜索收集器

        Args:
            api_key: GLM API密钥，如果不提供则从环境变量读取
            time_range: 搜索时间范围 (24h=最近24小时, 3d=最近3天, 7d=最近7天)
        """
        self.api_key = api_key or os.getenv('GLM_API_KEY')
        if not self.api_key:
            raise ValueError("GLM API Key not found. Please set GLM_API_KEY environment variable.")

        # 初始化智谱AI客户端
        self.client = ZhipuAI(api_key=self.api_key)

        # 配置参数
        self.model = "glm-4-plus"  # 使用GLM-4-Plus模型，支持网络搜索
        self.max_tokens = 5000  # 最大token数
        self.temperature = 0.6   # 温度参数
        self.max_retries = 3     # 最大重试次数
        self.retry_delay = 5     # 重试延迟（秒）
        self.time_range = time_range  # 时间范围

        logger.info(f"GLM搜索收集器初始化成功，时间范围: {time_range}")

    def _get_time_range_text(self) -> str:
        """
        将时间范围代码转换为自然语言描述

        Returns:
            时间范围的自然语言描述
        """
        time_map = {
            "24h": "最近24小时内（今日）",
            "3d": "最近3天内",
            "7d": "最近7天内"
        }
        return time_map.get(self.time_range, "最近24小时内")

    def _get_time_filter_date(self) -> str:
        """
        获取时间过滤的具体日期

        Returns:
            时间过滤日期字符串（YYYY-MM-DD）
        """
        now = datetime.now()
        if self.time_range == "24h":
            filter_date = now
        elif self.time_range == "3d":
            filter_date = now - timedelta(days=3)
        elif self.time_range == "7d":
            filter_date = now - timedelta(days=7)
        else:
            filter_date = now

        return filter_date.strftime('%Y年%m月%d日')

    def search(self, query: str, max_results: int = 10) -> Dict:
        """
        执行GLM搜索

        Args:
            query: 搜索查询
            max_results: 返回的最大结果数（此参数用于提示词）

        Returns:
            包含搜索结果的字典
        """
        logger.info(f"开始搜索: {query} (时间范围: {self.time_range})")

        # 获取时间范围描述和过滤日期
        time_range_text = self._get_time_range_text()
        filter_date = self._get_time_filter_date()

        # 构建搜索提示 - 强调时间限制
        prompt = f"""请搜索并总结以下主题的最新信息（最多{max_results}条重要内容）:

{query}

⚠️ 时间要求（非常重要）:
- 只搜索{time_range_text}的资讯
- 必须是{filter_date}之后发布的内容
- 忽略所有过时的、旧的新闻
- 如果没有找到最新资讯，明确说明

内容要求:
1. 提供最新、最重要的信息
2. 每条信息包含标题、时间和简要说明
3. 按发布时间倒序排列（最新的在前）
4. 格式清晰、易读"""

        for attempt in range(self.max_retries):
            try:
                # 调用GLM API - 使用web_search工具
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    tools=[{
                        "type": "web_search",
                        "web_search": {
                            "enable": True,  # 启用网络搜索
                            "search_result": True  # 返回搜索结果
                        }
                    }]
                )

                # 提取回复内容
                if response and response.choices:
                    content = response.choices[0].message.content

                    logger.info(f"搜索成功: {query}")
                    return {
                        'query': query,
                        'success': True,
                        'content': content,
                        'timestamp': time.time()
                    }
                else:
                    logger.error(f"搜索返回空结果: {query}")
                    return {
                        'query': query,
                        'success': False,
                        'error': 'Empty response',
                        'timestamp': time.time()
                    }

            except Exception as e:
                logger.error(f"搜索失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    return {
                        'query': query,
                        'success': False,
                        'error': str(e),
                        'timestamp': time.time()
                    }

        return {
            'query': query,
            'success': False,
            'error': 'Max retries exceeded',
            'timestamp': time.time()
        }

    def batch_search(self, queries: List[str], max_results: int = 10) -> List[Dict]:
        """
        批量搜索

        Args:
            queries: 搜索查询列表
            max_results: 每个查询返回的最大结果数

        Returns:
            搜索结果列表
        """
        logger.info(f"开始批量搜索，共{len(queries)}个查询")
        results = []

        for i, query in enumerate(queries, 1):
            logger.info(f"进度: {i}/{len(queries)}")
            result = self.search(query, max_results)
            results.append(result)

            # 避免请求过快
            if i < len(queries):
                time.sleep(2)

        logger.info(f"批量搜索完成，成功{sum(1 for r in results if r['success'])}个")
        return results


# 测试代码
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试GLM搜索
    collector = GLMSearchCollector()

    # 单次搜索测试
    result = collector.search("OpenAI最新动态", max_results=5)
    print(f"\n搜索结果:\n{result}\n")
