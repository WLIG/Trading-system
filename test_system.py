#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
用于测试交易系统的基本功能
"""

import sys
import os
import traceback
from datetime import datetime

def test_imports():
    """测试模块导入"""
    print("=== 测试模块导入 ===")
    
    modules_to_test = [
        'pandas',
        'numpy', 
        'requests',
        'sqlite3',
        'json',
        'logging',
        'threading',
        'asyncio'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module} - 导入成功")
        except ImportError as e:
            print(f"❌ {module} - 导入失败: {e}")
    
    # 测试本地模块
    local_modules = [
        'enhanced_config',
        'telegram_bot',
        'integrated_trading_system'
    ]
    
    for module in local_modules:
        try:
            __import__(module)
            print(f"✅ {module} - 导入成功")
        except Exception as e:
            print(f"❌ {module} - 导入失败: {e}")

def test_config():
    """测试配置文件"""
    print("\n=== 测试配置文件 ===")
    
    try:
        from enhanced_config import ENHANCED_CONFIG
        print("✅ 配置文件加载成功")
        
        # 检查关键配置项
        required_keys = ['trading', 'strategy', 'risk_management', 'telegram']
        for key in required_keys:
            if key in ENHANCED_CONFIG:
                print(f"✅ 配置项 {key} 存在")
            else:
                print(f"❌ 配置项 {key} 缺失")
                
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        traceback.print_exc()

def test_trading_system():
    """测试交易系统"""
    print("\n=== 测试交易系统 ===")
    
    try:
        from integrated_trading_system import IntegratedTradingSystem
        from enhanced_config import ENHANCED_CONFIG
        
        # 创建交易系统实例
        trading_system = IntegratedTradingSystem(ENHANCED_CONFIG)
        print("✅ 交易系统实例创建成功")
        
        # 测试基本方法
        if hasattr(trading_system, 'initialize'):
            print("✅ initialize 方法存在")
        
        if hasattr(trading_system, 'run_strategy'):
            print("✅ run_strategy 方法存在")
            
        if hasattr(trading_system, 'calculate_performance'):
            print("✅ calculate_performance 方法存在")
            
    except Exception as e:
        print(f"❌ 交易系统测试失败: {e}")
        traceback.print_exc()

def test_telegram_bot():
    """测试Telegram Bot"""
    print("\n=== 测试Telegram Bot ===")
    
    try:
        from telegram_bot import TelegramNotificationManager
        from enhanced_config import ENHANCED_CONFIG
        
        # 创建通知管理器
        notification_manager = TelegramNotificationManager(ENHANCED_CONFIG)
        print("✅ Telegram通知管理器创建成功")
        
        # 测试基本方法
        if hasattr(notification_manager, 'send_trade_notification'):
            print("✅ send_trade_notification 方法存在")
            
        if hasattr(notification_manager, 'send_alert'):
            print("✅ send_alert 方法存在")
            
    except Exception as e:
        print(f"❌ Telegram Bot测试失败: {e}")
        traceback.print_exc()

def test_web_app():
    """测试Web应用"""
    print("\n=== 测试Web应用 ===")
    
    try:
        # 检查Flask是否可用
        import flask
        print("✅ Flask 可用")
        
        # 检查Web应用文件
        if os.path.exists('enhanced_futures_web_app.py'):
            print("✅ Web应用文件存在")
        else:
            print("❌ Web应用文件不存在")
            
        # 检查模板目录
        if os.path.exists('web_app/templates'):
            print("✅ 模板目录存在")
        else:
            print("❌ 模板目录不存在")
            
        # 检查静态文件目录
        if os.path.exists('web_app/static'):
            print("✅ 静态文件目录存在")
        else:
            print("❌ 静态文件目录不存在")
            
    except Exception as e:
        print(f"❌ Web应用测试失败: {e}")
        traceback.print_exc()

def test_database():
    """测试数据库连接"""
    print("\n=== 测试数据库 ===")
    
    try:
        import sqlite3
        
        # 创建测试数据库
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # 创建测试表
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入测试数据
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
        conn.commit()
        
        # 查询测试数据
        cursor.execute("SELECT * FROM test_table")
        result = cursor.fetchone()
        
        if result:
            print("✅ SQLite数据库功能正常")
        else:
            print("❌ SQLite数据库功能异常")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        traceback.print_exc()

def main():
    """主测试函数"""
    print(f"交易系统测试开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print("=" * 50)
    
    # 运行各项测试
    test_imports()
    test_config()
    test_database()
    test_trading_system()
    test_telegram_bot()
    test_web_app()
    
    print("\n" + "=" * 50)
    print(f"测试完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n如果看到❌标记，请检查相应的模块或配置。")
    print("如果所有测试都显示✅，系统应该可以正常运行。")

if __name__ == "__main__":
    main()