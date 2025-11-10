#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置查看和对齐工具
用途：快速查看项目配置，检查配置一致性
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

class ConfigViewer:
    """配置查看器"""

    def __init__(self):
        self.config_file = PROJECT_ROOT / "config" / "config.yaml"
        self.keywords_file = PROJECT_ROOT / "config" / "keywords.yaml"
        self.env_example = PROJECT_ROOT / ".env.example"
        self.env_file = PROJECT_ROOT / ".env"

    def load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """加载YAML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ 文件不存在: {file_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ YAML解析错误: {e}")
            return {}

    def check_env_vars(self) -> Dict[str, bool]:
        """检查环境变量是否配置"""
        required_vars = [
            'GLM_API_KEY',
            'WECHAT_WEBHOOK_URL'
        ]

        optional_vars = [
            'SMTP_PASSWORD',
            'GITHUB_TOKEN',
            'SMTP_SERVER',
            'SMTP_USERNAME'
        ]

        results = {}

        print("\n🔑 环境变量检查:")
        print("=" * 60)

        for var in required_vars:
            value = os.getenv(var)
            is_set = bool(value)
            results[var] = is_set

            status = "✅ 已配置" if is_set else "❌ 未配置"
            print(f"  {var}: {status}")
            if is_set:
                # 显示前4位和后4位
                masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                print(f"    值: {masked}")

        print("\n📋 可选环境变量:")
        for var in optional_vars:
            value = os.getenv(var)
            is_set = bool(value)
            results[var] = is_set

            status = "✅ 已配置" if is_set else "⚪ 未配置（可选）"
            print(f"  {var}: {status}")

        return results

    def show_config_summary(self):
        """显示配置摘要"""
        print("\n📊 系统配置摘要:")
        print("=" * 60)

        config = self.load_yaml(self.config_file)

        if not config:
            print("❌ 无法加载配置文件")
            return

        # 系统配置
        system = config.get('system', {})
        print(f"  项目名称: {system.get('name', 'N/A')}")
        print(f "  版本: {system.get('version', 'N/A')}")
        print(f"  时区: {system.get('timezone', 'N/A')}")

        # GLM配置
        glm = config.get('glm', {})
        print(f"\n🤖 GLM配置:")
        print(f"  模型: {glm.get('model', 'N/A')}")
        print(f"  最大Token: {glm.get('max_tokens', 'N/A')}")
        print(f"  搜索结果数: {glm.get('search_count', 'N/A')}")

        # 推送配置
        wechat = config.get('wechat', {})
        email = config.get('email', {})
        print(f"\n📱 推送配置:")
        print(f"  微信推送: {'✅ 启用' if wechat.get('enabled') else '❌ 禁用'}")
        print(f"  邮箱推送: {'✅ 启用' if email.get('enabled') else '❌ 禁用'}")

        # 去重配置
        dedup = config.get('deduplication', {})
        print(f"\n🔄 去重配置:")
        print(f"  相似度阈值: {dedup.get('similarity_threshold', 'N/A')}")
        print(f"  URL去重: {'✅ 启用' if dedup.get('url_dedup') else '❌ 禁用'}")
        print(f"  标题去重: {'✅ 启用' if dedup.get('title_dedup') else '❌ 禁用'}")

    def show_keywords_summary(self):
        """显示搜索关键词摘要"""
        print("\n🔍 搜索关键词配置:")
        print("=" * 60)

        keywords = self.load_yaml(self.keywords_file)

        if not keywords:
            print("❌ 无法加载关键词配置")
            return

        categories = keywords.get('categories', [])

        enabled_count = 0
        total_keywords = 0

        for category in categories:
            name = category.get('name', 'N/A')
            icon = category.get('icon', '')
            enabled = category.get('enabled', False)
            keywords_list = category.get('keywords', [])
            keyword_count = len(keywords_list)

            if enabled:
                enabled_count += 1
                total_keywords += keyword_count

            status = "✅ 启用" if enabled else "⚪ 禁用"
            print(f"\n  {icon} {name}: {status}")
            print(f"    关键词数量: {keyword_count}")

            if enabled and keywords_list:
                print(f"    关键词示例:")
                for kw in keywords_list[:2]:  # 只显示前2个
                    query = kw.get('query', 'N/A')
                    print(f"      - {query}")

        print(f"\n📈 统计:")
        print(f"  启用分类: {enabled_count}/{len(categories)}")
        print(f"  总关键词数: {total_keywords}")

    def check_files_exist(self):
        """检查关键文件是否存在"""
        print("\n📁 文件检查:")
        print("=" * 60)

        files_to_check = [
            ("INIT.md", PROJECT_ROOT / "INIT.md"),
            ("ARCHITECTURE.md", PROJECT_ROOT / "docs" / "ARCHITECTURE.md"),
            ("SECURITY.md", PROJECT_ROOT / "SECURITY.md"),
            ("config.yaml", self.config_file),
            ("keywords.yaml", self.keywords_file),
            (".env.example", self.env_example),
            (".gitignore", PROJECT_ROOT / ".gitignore"),
        ]

        all_exist = True
        for name, path in files_to_check:
            exists = path.exists()
            status = "✅ 存在" if exists else "❌ 缺失"
            print(f"  {name}: {status}")
            if not exists:
                all_exist = False

        return all_exist

    def check_env_file(self):
        """检查.env文件配置状态"""
        print("\n🔧 .env文件状态:")
        print("=" * 60)

        if self.env_file.exists():
            print("  ✅ .env文件已创建")
            print("  💡 提示: 请确保已填入真实API密钥")
        else:
            print("  ⚪ .env文件未创建")
            print("  💡 提示: 复制.env.example为.env并填入密钥")
            print(f"  命令: cp .env.example .env")

    def generate_report(self):
        """生成完整配置报告"""
        print("\n" + "=" * 60)
        print("📋 项目配置报告")
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 检查文件
        self.check_files_exist()

        # 检查环境变量
        env_results = self.check_env_vars()

        # 显示配置摘要
        self.show_config_summary()

        # 显示关键词摘要
        self.show_keywords_summary()

        # 检查.env文件
        self.check_env_file()

        # 总结
        print("\n" + "=" * 60)
        print("📊 配置状态总结:")
        print("=" * 60)

        required_configured = all([
            env_results.get('GLM_API_KEY', False),
            env_results.get('WECHAT_WEBHOOK_URL', False)
        ])

        if required_configured:
            print("  ✅ 必需环境变量已全部配置")
            print("  🚀 系统已就绪，可以开始开发！")
        else:
            print("  ❌ 必需环境变量未完全配置")
            print("  💡 请按照SECURITY.md配置API密钥")

        print("\n📖 快速链接:")
        print("  - 查看初始化文档: cat INIT.md")
        print("  - 查看架构设计: cat docs/ARCHITECTURE.md")
        print("  - 查看安全指南: cat SECURITY.md")
        print("  - 修改配置: nano config/config.yaml")
        print("  - 修改关键词: nano config/keywords.yaml")

        print("\n" + "=" * 60)


def main():
    """主函数"""
    viewer = ConfigViewer()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--summary":
            viewer.show_config_summary()
        elif command == "--keywords":
            viewer.show_keywords_summary()
        elif command == "--env":
            viewer.check_env_vars()
        elif command == "--files":
            viewer.check_files_exist()
        elif command == "--help":
            print("配置查看工具使用说明:")
            print("  python scripts/view_config.py          - 生成完整报告")
            print("  python scripts/view_config.py --summary    - 查看配置摘要")
            print("  python scripts/view_config.py --keywords   - 查看关键词配置")
            print("  python scripts/view_config.py --env        - 检查环境变量")
            print("  python scripts/view_config.py --files      - 检查文件状态")
            print("  python scripts/view_config.py --help       - 显示帮助")
        else:
            print(f"未知命令: {command}")
            print("使用 --help 查看帮助")
    else:
        # 默认生成完整报告
        viewer.generate_report()


if __name__ == "__main__":
    main()
