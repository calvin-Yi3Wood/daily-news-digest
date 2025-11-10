"""
邮箱推送模块 - SMTP邮件发送（备用推送）
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailSender:
    """邮箱发送器"""

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        email_to: Optional[str] = None
    ):
        """
        初始化邮箱发送器

        Args:
            smtp_host: SMTP服务器地址
            smtp_port: SMTP端口
            smtp_user: SMTP用户名
            smtp_password: SMTP密码
            email_to: 收件人邮箱
        """
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = smtp_user or os.getenv('SMTP_USER')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')
        self.email_to = email_to or os.getenv('EMAIL_TO')

        # 验证配置
        if not all([self.smtp_user, self.smtp_password, self.email_to]):
            logger.warning("邮箱配置不完整，部分功能可能无法使用")

        logger.info(f"邮箱发送器初始化成功: {self.smtp_host}:{self.smtp_port}")

    def send_html(self, subject: str, html_content: str) -> bool:
        """
        发送HTML邮件

        Args:
            subject: 邮件主题
            html_content: HTML内容

        Returns:
            True表示成功，False表示失败
        """
        logger.info(f"开始发送HTML邮件: {subject}")

        try:
            # 创建消息
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = self.email_to

            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # 连接SMTP服务器
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info("HTML邮件发送成功")
            return True

        except Exception as e:
            logger.error(f"HTML邮件发送失败: {str(e)}")
            return False

    def send_text(self, subject: str, text_content: str) -> bool:
        """
        发送纯文本邮件

        Args:
            subject: 邮件主题
            text_content: 文本内容

        Returns:
            True表示成功，False表示失败
        """
        logger.info(f"开始发送文本邮件: {subject}")

        try:
            # 创建消息
            msg = MIMEText(text_content, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = self.email_to

            # 连接SMTP服务器
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info("文本邮件发送成功")
            return True

        except Exception as e:
            logger.error(f"文本邮件发送失败: {str(e)}")
            return False

    def send_markdown_as_html(self, markdown_content: str, date: Optional[str] = None) -> bool:
        """
        将Markdown转换为HTML并发送

        Args:
            markdown_content: Markdown内容
            date: 日期（可选）

        Returns:
            True表示成功，False表示失败
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        # 简单的Markdown到HTML转换
        # 生产环境建议使用markdown库
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                blockquote {{
                    border-left: 4px solid #3498db;
                    padding-left: 15px;
                    color: #7f8c8d;
                    font-style: italic;
                }}
                code {{
                    background: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                }}
                hr {{
                    border: none;
                    border-top: 1px solid #eee;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <pre style="white-space: pre-wrap; word-wrap: break-word;">{markdown_content}</pre>
        </body>
        </html>
        """

        subject = f"📰 每日资讯汇总 | {date}"
        return self.send_html(subject, html_content)


# 测试代码
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 检查配置
    if not all([os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'), os.getenv('EMAIL_TO')]):
        print("\n⚠️ 邮箱配置不完整，无法测试")
        print("请在.env文件中配置以下变量:")
        print("  - SMTP_HOST")
        print("  - SMTP_PORT")
        print("  - SMTP_USER")
        print("  - SMTP_PASSWORD")
        print("  - EMAIL_TO")
    else:
        # 测试邮箱发送
        sender = EmailSender()

        # 测试Markdown邮件
        markdown_content = """# 测试邮件

## 这是测试标题

这是测试内容。

- 列表项1
- 列表项2

**粗体文本**
"""

        print("\n=== 测试Markdown邮件 ===")
        success = sender.send_markdown_as_html(markdown_content)
        print(f"发送结果: {'成功' if success else '失败'}")
