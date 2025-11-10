"""
智能内容处理器 - 使用GLM大模型进行二次处理
对搜索结果进行质量筛选、去重、排序和摘要
"""

import os
import re
import logging
from typing import List, Dict
from datetime import datetime, timedelta
from zhipuai import ZhipuAI

logger = logging.getLogger(__name__)


class ContentProcessor:
    """智能内容处理器"""

    def __init__(self):
        """初始化内容处理器"""
        api_key = os.getenv('GLM_API_KEY')
        if not api_key:
            raise ValueError("GLM_API_KEY not found in environment variables")

        self.client = ZhipuAI(api_key=api_key)
        self.model = "glm-4-plus"  # 使用更强大的模型进行内容处理

        # 时间阈值：只接受最近30天的新闻（借鉴GitHub项目策略）
        self.max_age_days = 30

        logger.info("智能内容处理器初始化成功")

    def _validate_date(self, content: str) -> bool:
        """
        验证内容中的日期是否可靠

        借鉴GitHub项目经验：
        - RSS aggregators使用2小时时间窗口
        - 我们使用30天阈值过滤旧新闻

        Args:
            content: 待验证的文本内容

        Returns:
            True表示日期可靠，False表示包含未来或过旧的日期
        """
        today = datetime.now()
        cutoff_date = today - timedelta(days=self.max_age_days)

        # 日期模式：2025年11月10日、2025-11-10、11月10日等
        date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',  # 2025年11月10日
            r'(\d{4})-(\d{1,2})-(\d{1,2})',       # 2025-11-10
            r'(\d{1,2})月(\d{1,2})日',             # 11月10日
        ]

        found_invalid = False

        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    if len(match) == 3:  # 完整年月日
                        year, month, day = int(match[0]), int(match[1]), int(match[2])
                    elif len(match) == 2:  # 只有月日，假设今年
                        year, month, day = today.year, int(match[0]), int(match[1])
                    else:
                        continue

                    news_date = datetime(year, month, day)

                    # 检查未来日期
                    if news_date > today:
                        logger.warning(f"⚠️ 发现未来日期: {news_date.strftime('%Y-%m-%d')}（今天: {today.strftime('%Y-%m-%d')}）")
                        found_invalid = True

                    # 检查过旧日期
                    if news_date < cutoff_date:
                        logger.warning(f"⚠️ 发现过旧新闻: {news_date.strftime('%Y-%m-%d')}（超过{self.max_age_days}天）")
                        found_invalid = True

                except (ValueError, IndexError) as e:
                    logger.debug(f"日期解析异常: {match}, 错误: {e}")
                    continue

        return not found_invalid

    def process_news(self, glm_results: List[Dict], github_projects: List[Dict]) -> Dict:
        """
        智能处理新闻内容

        Args:
            glm_results: GLM搜索结果列表
            github_projects: GitHub项目列表

        Returns:
            处理后的结构化内容
        """
        logger.info("=== 开始智能内容处理 ===")

        # 1. 提取所有新闻内容
        all_news = []
        for result in glm_results:
            if result.get('success'):
                all_news.append({
                    'category': result.get('query', '未知'),
                    'content': result.get('content', '')
                })

        logger.info(f"收集了{len(all_news)}个新闻源")

        # 2. 提取GitHub项目信息
        github_summary = []
        for i, project in enumerate(github_projects[:5], 1):  # 只取前5个
            github_summary.append({
                'name': project.get('full_name', ''),
                'description': project.get('description', ''),
                'stars': project.get('stars', 0),
                'language': project.get('language', ''),
                'url': project.get('url', '')
            })

        # 3. 调用GLM进行智能处理
        processed_content = self._call_glm_processor(all_news, github_summary)

        logger.info("智能内容处理完成")
        return processed_content

    def _call_glm_processor(self, news_list: List[Dict], github_list: List[Dict]) -> Dict:
        """
        调用GLM大模型进行内容处理

        Args:
            news_list: 新闻列表
            github_list: GitHub项目列表

        Returns:
            处理后的结构化内容
        """
        # 构建新闻摘要
        news_text = ""
        for i, news in enumerate(news_list, 1):
            news_text += f"\n### 来源{i}：{news['category']}\n{news['content']}\n"

        # 构建GitHub项目摘要
        github_text = ""
        for project in github_list:
            github_text += f"- {project['name']} ({project['language']}) - {project['stars']} stars\n  {project['description']}\n"

        # 获取今天的日期和时间窗口（借鉴GitHub RSS aggregator策略）
        today = datetime.now()
        today_str = today.strftime('%Y年%m月%d日')
        cutoff_date = (today - timedelta(days=self.max_age_days)).strftime('%Y年%m月%d日')

        # 构建增强版处理提示词
        prompt = f"""# 任务说明
你是一个专业的新闻编辑，负责处理每日资讯汇总。

## 🔴 严格时间要求（最高优先级）
**今天日期**: {today_str}
**时间窗口**: {cutoff_date} 至 {today_str}

**⚠️ 关键规则（必须严格遵守）**：
1. **只保留时间窗口内的新闻**（{cutoff_date}到{today_str}之间）
2. **绝对禁止未来日期**：任何日期>{today_str}的新闻必须丢弃
3. **过滤过旧新闻**：任何日期<{cutoff_date}的新闻必须丢弃
4. **验证每条新闻**：如果原始内容包含日期，必须验证其合理性
5. **无法验证的新闻**：如果日期不明确且无法确认为近期新闻，宁可丢弃

**⚠️ 常见错误示例（必须避免）**：
- ❌ "讯飞星火V4.0于2024年6月发布" → 这是7个月前的旧闻，必须丢弃
- ❌ "Kimi宣布200万字上下文（2024年3月）" → 这是8个月前的旧闻，必须丢弃
- ✅ "OpenAI今日发布GPT-5预览版" → 只有明确为"今日"、"本周"等近期表述才保留

## 原始资讯内容
{news_text}

## GitHub热门项目
{github_text}

## 处理要求

### 1. 严格时间过滤（第一优先级）
在处理任何新闻前，先执行时间过滤：
- 提取新闻中的所有日期标识
- 将模糊时间（"今日"、"本周"）转换为具体日期范围
- 丢弃所有不在时间窗口内的新闻
- 如果80%以上的新闻都被过滤，返回"当前无最新资讯"

### 2. 质量筛选（第二优先级）
- 去除低质量、标题党、重复的内容
- 去除明显错误或无价值的信息
- 只保留有实际价值的新闻
- 优先保留AI、科技、金融领域的重大进展

### 3. 内容整理（第三优先级）
- 按重要性排序（AI/科技 > 金融 > 其他）
- 合并相似话题的新闻
- 每条新闻控制在80-120字（简洁明了）
- 总输出控制在1500-2000字（避免信息过载）
- **严禁添加原始内容中不存在的日期**（如果原文有日期就保留，没有就不要添加）
- **优先使用"今日"、"本周"等模糊时间表述**，避免具体日期错误

### 4. 输出格式
使用以下Markdown格式：

---

## 🔥 今日要闻 ({today_str})

### 1. [新闻标题]
[简洁的新闻摘要，80-120字]

### 2. [新闻标题]
[简洁的新闻摘要，80-120字]

...（最多8条要闻）

**注意**：新闻标题后不要添加具体日期，所有新闻都是今日资讯

## ⭐ GitHub热门项目

1. **[项目名称]** - [语言]
   - ⭐ [星标数] | [一句话描述]

...（最多5个项目）

---

注意：请严格按照上述Markdown模板输出，不要添加任何元信息或检查清单，直接输出可读内容。
"""

        try:
            logger.info("调用GLM-4-Plus进行智能处理...")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的新闻编辑，擅长筛选和总结高质量的资讯内容。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=4000
            )

            processed_content = response.choices[0].message.content.strip()

            logger.info(f"GLM处理完成，输出字符数: {len(processed_content)}")

            # 🆕 后处理验证：检查内容中的日期是否可靠
            # 注意：现在使用RSS数据源，时间应该100%可靠
            # 如果仍然检测到问题，说明GLM在总结时又编造了日期
            if not self._validate_date(processed_content):
                logger.warning("⚠️ 日期验证检测到问题：GLM可能在总结时修改了原始日期")
                logger.warning("💡 RSS原始数据时间可靠，但GLM总结可能引入新日期")

                # 🟡 宽松策略：仅警告，不拒绝推送（RSS数据源可靠）
                warning_msg = f"\n⚠️ **提示**：部分日期可能在AI总结时被调整，请以实际发布时间为准\n\n"
                processed_content = warning_msg + processed_content

            return {
                'success': True,
                'content': processed_content,
                'char_count': len(processed_content),
                'byte_count': len(processed_content.encode('utf-8'))
            }

        except Exception as e:
            logger.error(f"GLM处理失败: {str(e)}")
            return {
                'success': False,
                'content': '',
                'error': str(e)
            }


# 测试代码
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试内容处理器
    processor = ContentProcessor()

    # 模拟数据
    test_results = [
        {
            'success': True,
            'query': 'AI最新动态',
            'content': '测试内容1...'
        }
    ]

    test_projects = [
        {
            'full_name': 'test/project',
            'description': '测试项目',
            'stars': 1000,
            'language': 'Python',
            'url': 'https://github.com/test/project'
        }
    ]

    result = processor.process_news(test_results, test_projects)
    print(f"\n处理结果: {result['success']}")
    print(f"输出长度: {result.get('char_count', 0)}字符")
