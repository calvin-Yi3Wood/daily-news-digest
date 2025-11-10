"""
每日资讯推送系统 - 主程序
Daily News Digest System

功能:
- 每天早上8点（北京时间）自动运行
- 使用GLM 4.6搜索最新资讯
- 获取GitHub热门项目
- 智能去重
- 推送到微信（主）或邮箱（备）
"""

import os
import sys
import yaml
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from collectors import GLMSearchCollector, GitHubTrendingCollector, ContentDeduplicator, RSSCollector
from formatters import MarkdownFormatter
from pushers import WeChatWebhookPusher, EmailSender
from processors import ContentProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daily_news_digest.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_config(config_path: str = 'config/config.yaml') -> Dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_keywords(keywords_path: str = 'config/keywords.yaml') -> List[Dict]:
    """
    加载搜索关键词（支持每个关键词不同的结果数）

    Returns:
        List[Dict]: 包含query和max_results的字典列表
        例如: [{'query': 'xxx', 'max_results': 10}, ...]
    """
    with open(keywords_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    keywords = []
    for category in data.get('categories', []):
        if category.get('enabled', True):
            # 获取该分类的search_params
            search_params = category.get('search_params', {})
            count = search_params.get('count', 10)  # 默认10

            for keyword_item in category.get('keywords', []):
                if isinstance(keyword_item, dict):
                    query = keyword_item.get('query', '')
                else:
                    query = keyword_item
                if query:
                    keywords.append({
                        'query': query,
                        'max_results': count,
                        'category': category.get('name', '未分类')
                    })

    logger.info(f"加载了{len(keywords)}个搜索关键词")
    return keywords


def collect_news(config: Dict) -> tuple:
    """
    收集新闻资讯

    Returns:
        (rss_results, github_projects) 元组
    """
    logger.info("=== 开始收集资讯 ===")

    # 1. RSS新闻收集（替代GLM搜索，时间100%可靠）
    logger.info("步骤1: RSS新闻收集")
    rss_collector = RSSCollector()

    # 收集最近24小时的RSS文章
    articles = rss_collector.collect(hours=24, max_per_feed=10)

    # 格式化为GLM处理器兼容的格式
    rss_results = rss_collector.format_for_glm(articles)

    logger.info(f"RSS收集完成: {len(articles)}篇文章, {len(rss_results)}个分类")

    # 2. GitHub趋势
    logger.info("步骤2: GitHub趋势项目")
    github_collector = GitHubTrendingCollector()
    github_config = config.get('github', {})

    languages = github_config.get('languages', ['Python', 'JavaScript', 'TypeScript'])
    days = github_config.get('trending_days', 7)
    top_n = github_config.get('top_n', 10)

    # 获取所有语言的项目并合并
    all_projects = []
    for language in languages:
        projects = github_collector.get_trending(language, days, top_n // len(languages))
        all_projects.extend(projects)

    # 按星标排序
    all_projects.sort(key=lambda x: x.get('stars', 0), reverse=True)

    # 只保留前top_n个
    github_projects = all_projects[:top_n]

    logger.info(f"收集完成: RSS文章{len(articles)}篇, GitHub项目{len(github_projects)}个")
    return rss_results, github_projects


def deduplicate_content(glm_results: List[Dict], github_projects: List[Dict], config: Dict):
    """
    去重处理

    Returns:
        去重后的结果
    """
    logger.info("=== 开始去重处理 ===")

    dedup_config = config.get('deduplication', {})
    threshold = dedup_config.get('similarity_threshold', 0.8)

    deduplicator = ContentDeduplicator(similarity_threshold=threshold)

    # GitHub项目去重（基于URL）
    github_items = []
    for project in github_projects:
        github_items.append({
            'title': project.get('full_name', ''),
            'url': project.get('url', ''),
            'data': project
        })

    unique_github_items = deduplicator.deduplicate(github_items)
    unique_github_projects = [item['data'] for item in unique_github_items]

    logger.info(f"去重完成: GitHub项目 {len(github_projects)} -> {len(unique_github_projects)}")
    return glm_results, unique_github_projects


def intelligent_process(glm_results: List[Dict], github_projects: List[Dict]) -> Dict:
    """
    智能处理内容（使用GLM大模型进行二次处理）

    Args:
        glm_results: GLM搜索结果
        github_projects: GitHub项目列表

    Returns:
        处理后的内容字典
    """
    logger.info("=== 开始智能内容处理 ===")

    try:
        processor = ContentProcessor()
        processed = processor.process_news(glm_results, github_projects)

        if processed.get('success'):
            logger.info(f"✅ 智能处理成功！输出{processed.get('char_count', 0)}字符")
            return processed
        else:
            logger.error(f"❌ 智能处理失败: {processed.get('error', '未知错误')}")
            return processed

    except Exception as e:
        logger.error(f"智能处理异常: {str(e)}", exc_info=True)
        return {
            'success': False,
            'content': '',
            'error': str(e)
        }


def format_and_push_processed(processed_content: Dict, config: Dict) -> bool:
    """
    推送智能处理后的内容

    Args:
        processed_content: 智能处理后的内容字典
        config: 系统配置

    Returns:
        True表示成功，False表示失败
    """
    logger.info("=== 开始推送处理后的内容 ===")

    if not processed_content.get('success'):
        logger.error("内容处理失败，无法推送")
        return False

    markdown = processed_content.get('content', '')
    if not markdown:
        logger.error("处理后的内容为空")
        return False

    # 添加科比名言（在分割前）
    formatter = MarkdownFormatter()
    kobe_quote = formatter.get_random_kobe_quote()
    if kobe_quote:
        # 添加科比名言到内容末尾
        kobe_lines = ["\n\n---\n"]
        kobe_lines.append("## 🏀 今日名言 - Kobe Bryant\n")

        if kobe_quote.get('show_category'):
            kobe_lines.append(f"*{kobe_quote['category']}*\n")

        format_type = kobe_quote.get('format', 'bilingual')
        if format_type == 'bilingual':
            kobe_lines.append(f"> **{kobe_quote['en']}**\n")
            kobe_lines.append(f"> **{kobe_quote['zh']}**\n")
        elif format_type == 'en_only':
            kobe_lines.append(f"> {kobe_quote['en']}\n")
        elif format_type == 'zh_only':
            kobe_lines.append(f"> {kobe_quote['zh']}\n")

        markdown += ''.join(kobe_lines)
        logger.info("✅ 已添加科比名言")

    # 检查是否需要分割
    max_size = config.get('formatter', {}).get('max_chunk_size', 1300)
    chunks = formatter.split_content(markdown, max_size)

    logger.info(f"内容分割完成，共{len(chunks)}个部分")

    # 推送
    push_config = config.get('push_strategy', {})
    primary = push_config.get('primary', 'wechat')
    enable_fallback = push_config.get('enable_fallback', True)

    success = False

    # 主推送方式
    if primary == 'wechat':
        logger.info("使用微信Webhook推送")
        try:
            pusher = WeChatWebhookPusher()
            success = pusher.send_in_chunks(chunks) if len(chunks) > 1 else pusher.send_markdown(chunks[0])
        except Exception as e:
            logger.error(f"微信推送失败: {str(e)}")
            success = False

    elif primary == 'email':
        logger.info("使用邮箱推送")
        try:
            sender = EmailSender()
            success = sender.send_markdown_as_html(markdown)
        except Exception as e:
            logger.error(f"邮箱推送失败: {str(e)}")
            success = False

    # 备用推送
    if not success and enable_fallback:
        fallback = push_config.get('fallback', 'email')
        logger.warning(f"主推送失败，尝试备用推送: {fallback}")

        if fallback == 'email':
            try:
                sender = EmailSender()
                success = sender.send_markdown_as_html(markdown)
            except Exception as e:
                logger.error(f"备用邮箱推送失败: {str(e)}")
                success = False

    return success


def format_and_push(glm_results: List[Dict], github_projects: List[Dict], config: Dict) -> bool:
    """
    格式化并推送（保留旧版本作为备用）

    Returns:
        True表示成功，False表示失败
    """
    logger.info("=== 开始格式化和推送 ===")

    # 1. 格式化
    formatter = MarkdownFormatter()
    markdown = formatter.format_digest(glm_results, github_projects)

    # 2. 检查是否需要分割
    max_size = config.get('formatter', {}).get('max_chunk_size', 1300)
    chunks = formatter.split_content(markdown, max_size)

    logger.info(f"内容格式化完成，共{len(chunks)}个部分")

    # 3. 推送
    push_config = config.get('push_strategy', {})
    primary = push_config.get('primary', 'wechat')
    enable_fallback = push_config.get('enable_fallback', True)

    success = False

    # 主推送方式
    if primary == 'wechat':
        logger.info("使用微信Webhook推送（主推送）")
        try:
            pusher = WeChatWebhookPusher()
            success = pusher.send_in_chunks(chunks) if len(chunks) > 1 else pusher.send_markdown(chunks[0])
        except Exception as e:
            logger.error(f"微信推送失败: {str(e)}")
            success = False

    elif primary == 'email':
        logger.info("使用邮箱推送（主推送）")
        try:
            sender = EmailSender()
            success = sender.send_markdown_as_html(markdown)
        except Exception as e:
            logger.error(f"邮箱推送失败: {str(e)}")
            success = False

    # 备用推送
    if not success and enable_fallback:
        fallback = push_config.get('fallback', 'email')
        logger.warning(f"主推送失败，尝试备用推送: {fallback}")

        if fallback == 'email':
            try:
                sender = EmailSender()
                success = sender.send_markdown_as_html(markdown)
            except Exception as e:
                logger.error(f"备用邮箱推送失败: {str(e)}")
                success = False

    return success


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("每日资讯推送系统启动")
    logger.info(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    try:
        # 加载配置
        config = load_config()

        # 收集资讯
        glm_results, github_projects = collect_news(config)

        # 去重处理
        glm_results, github_projects = deduplicate_content(glm_results, github_projects, config)

        # 🆕 智能内容处理（使用GLM大模型进行二次处理）
        processed_content = intelligent_process(glm_results, github_projects)

        # 推送处理后的内容
        success = format_and_push_processed(processed_content, config)

        if success:
            logger.info("✅ 资讯推送成功！")
            return 0
        else:
            logger.error("❌ 资讯推送失败！")
            return 1

    except Exception as e:
        logger.error(f"❌ 程序执行失败: {str(e)}", exc_info=True)
        return 1

    finally:
        logger.info("=" * 60)
        logger.info("程序运行结束")
        logger.info("=" * 60)


if __name__ == '__main__':
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)

    # 运行主程序
    exit_code = main()
    sys.exit(exit_code)
