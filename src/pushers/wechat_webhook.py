"""
微信Webhook推送模块 - 企业微信群机器人推送
"""

import os
import time
import logging
import requests
from typing import Optional, List

logger = logging.getLogger(__name__)


class WeChatWebhookPusher:
    """微信Webhook推送器"""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        初始化微信Webhook推送器

        Args:
            webhook_url: 微信Webhook URL，如果不提供则从环境变量读取
        """
        self.webhook_url = webhook_url or os.getenv('WECHAT_WEBHOOK_URL')
        if not self.webhook_url:
            raise ValueError("WeChat Webhook URL not found. Please set WECHAT_WEBHOOK_URL environment variable.")

        self.max_retries = 3
        self.retry_delay = 3

        logger.info("微信Webhook推送器初始化成功")

    def send_markdown(self, content: str) -> bool:
        """
        发送Markdown消息

        Args:
            content: Markdown内容

        Returns:
            True表示成功，False表示失败
        """
        logger.info("开始发送Markdown消息到微信")

        # 🔍 调试信息：记录实际发送的内容长度
        actual_char_count = len(content)
        actual_byte_count = len(content.encode('utf-8'))
        logger.info(f"📊 实际发送内容统计：字符数={actual_char_count}, 字节数={actual_byte_count}")

        if actual_char_count > 4096:
            logger.warning(f"⚠️ 内容超过微信4096字符限制！当前{actual_char_count}字符")

        # 打印内容前100字符用于调试
        logger.debug(f"📝 内容预览（前100字符）: {content[:100]}")

        # 构建请求数据
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.webhook_url,
                    json=data,
                    timeout=10
                )

                result = response.json()

                if result.get('errcode') == 0:
                    logger.info("微信消息发送成功")
                    return True
                else:
                    error_msg = result.get('errmsg', '未知错误')
                    logger.error(f"微信消息发送失败: {error_msg}")

                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                    else:
                        return False

            except Exception as e:
                logger.error(f"微信消息发送异常 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    return False

        return False

    def send_text(self, content: str) -> bool:
        """
        发送文本消息

        Args:
            content: 文本内容

        Returns:
            True表示成功，False表示失败
        """
        logger.info("开始发送文本消息到微信")

        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.webhook_url,
                    json=data,
                    timeout=10
                )

                result = response.json()

                if result.get('errcode') == 0:
                    logger.info("微信文本消息发送成功")
                    return True
                else:
                    error_msg = result.get('errmsg', '未知错误')
                    logger.error(f"微信文本消息发送失败: {error_msg}")

                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)

            except Exception as e:
                logger.error(f"微信文本消息发送异常 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        return False

    def send_in_chunks(self, contents: List[str]) -> bool:
        """
        分段发送多个消息

        Args:
            contents: 内容列表

        Returns:
            True表示全部成功，False表示有失败
        """
        logger.info(f"开始分段发送，共{len(contents)}个部分")

        all_success = True
        for i, content in enumerate(contents, 1):
            logger.info(f"发送第{i}/{len(contents)}部分")

            success = self.send_markdown(content)
            if not success:
                all_success = False
                logger.error(f"第{i}部分发送失败")

            # 避免发送过快
            if i < len(contents):
                time.sleep(1)

        if all_success:
            logger.info("所有部分发送成功")
        else:
            logger.warning("部分内容发送失败")

        return all_success


# 测试代码
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试微信推送
    pusher = WeChatWebhookPusher()

    # 测试Markdown消息
    markdown_content = """# 测试消息

## 这是标题

- 列表项1
- 列表项2

**粗体文本**
"""

    print("\n=== 测试Markdown消息 ===")
    success = pusher.send_markdown(markdown_content)
    print(f"发送结果: {'成功' if success else '失败'}")

    # 测试文本消息
    print("\n=== 测试文本消息 ===")
    success = pusher.send_text("这是一条测试文本消息")
    print(f"发送结果: {'成功' if success else '失败'}")
