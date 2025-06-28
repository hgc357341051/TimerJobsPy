#!/usr/bin/env python3
"""
数据库切换脚本
快速切换小胡定时任务系统的数据库类型
"""

import os
import sys


def print_banner() -> None:
    """打印横幅"""
    print("=" * 60)
    print("小胡定时任务系统 - 数据库切换工具")
    print("=" * 60)


def get_current_config() -> dict:
    """获取当前配置"""
    try:
        from app.config import Config

        return {
            "database_type": Config.DATABASE_TYPE,
            "database_url": Config.get_database_url(),
            "table_prefix": Config.DATABASE_SQLITE_TABLEPREFIX
            if Config.DATABASE_TYPE == "sqlite"
            else Config.DATABASE_MYSQL_TABLEPREFIX,
        }
    except Exception as e:
        print(f"获取配置失败: {e}")
        return {}


def switch_to_sqlite() -> None:
    """切换到SQLite"""
    print("正在切换到 SQLite...")
    os.environ["DATABASE_TYPE"] = "sqlite"
    print("✅ 已切换到 SQLite 配置")


def switch_to_mysql() -> None:
    """切换到MySQL"""
    print("正在切换到 MySQL...")
    os.environ["DATABASE_TYPE"] = "mysql"
    os.environ["DATABASE_MYSQL_HOST"] = "127.0.0.1"
    os.environ["DATABASE_MYSQL_PORT"] = "3306"
    os.environ["DATABASE_MYSQL_USERNAME"] = "root"
    os.environ["DATABASE_MYSQL_PASSWORD"] = "root123456"
    os.environ["DATABASE_MYSQL_DBNAME"] = "xiaohu_jobs"
    print("✅ 已切换到 MySQL 配置")


def print_config() -> None:
    """打印当前配置"""
    config = get_current_config()
    if config:
        print("\n当前配置:")
        print(f"  数据库类型: {config['database_type']}")
        print(f"  数据库URL: {config['database_url']}")
        print(f"  表前缀: {config['table_prefix']}")


def main() -> None:
    """主函数"""
    print_banner()
    print_config()
    print("\n请选择操作:")
    print("1. 切换到 SQLite (推荐开发/单机)")
    print("2. 切换到 MySQL (推荐生产环境)")
    print("3. 退出")

    choice = input("\n请输入选择 (1-3): ").strip()

    if choice == "1":
        switch_to_sqlite()
    elif choice == "2":
        switch_to_mysql()
    elif choice == "3":
        print("退出程序")
        sys.exit(0)
    else:
        print("❌ 无效选择")
        return

    print_config()


if __name__ == "__main__":
    main()
