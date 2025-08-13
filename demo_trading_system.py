#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合约量化交易系统演示
展示系统的核心功能和完整工作流程
"""

import sys
import os
import time
import logging
from datetime import datetime
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('trading_demo.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def demo_system_initialization():
    """演示系统初始化"""
    print("\n" + "="*60)
    print("🚀 合约量化交易系统演示启动")
    print("="*60)
    
    try:
        from enhanced_config import ENHANCED_CONFIG
        print("✅ 配置文件加载成功")
        
        # 显示关键配置
        trading_config = ENHANCED_CONFIG.get('trading', {})
        print(f"📊 交易模式: {trading_config.get('mode', 'backtest')}")
        print(f"💰 交易对: {trading_config.get('symbol', 'BTCUSDT')}")
        print(f"💵 初始资金: {ENHANCED_CONFIG.get('backtest', {}).get('initial_balance', 100000):,.2f} USDT")
        
        return ENHANCED_CONFIG
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return None

def demo_trading_system(config):
    """演示交易系统核心功能"""
    print("\n📈 初始化交易系统...")
    
    try:
        from integrated_trading_system import IntegratedTradingSystem
        
        # 创建交易系统
        trading_system = IntegratedTradingSystem(config)
        print("✅ 交易系统创建成功")
        
        # 获取市场数据
        symbol = config.get('trading', {}).get('symbol', 'BTCUSDT')
        print(f"\n📊 获取 {symbol} 市场数据...")
        
        price_data = trading_system.get_market_data(symbol, 50)
        current_price = price_data[-1]
        print(f"💰 当前价格: ${current_price:,.2f}")
        
        # 生成交易信号
        print("\n🎯 生成交易信号...")
        signal = trading_system.strategy.generate_signal(symbol, price_data)
        
        print(f"📊 信号类型: {signal.signal}")
        print(f"💪 信心度: {signal.confidence:.1%}")
        print(f"📋 原因: {signal.reason}")
        print(f"📈 RSI: {signal.indicators.get('rsi', 0):.1f}")
        print(f"📊 MACD: {signal.indicators.get('macd', 0):.4f}")
        
        # 模拟交易执行
        if signal.signal in ['BUY', 'SELL'] and signal.confidence > 0.6:
            print(f"\n💼 执行交易: {signal.signal}")
            
            quantity = 0.001 if symbol == 'BTCUSDT' else 0.1
            order = trading_system.execute_trade(symbol, signal.signal, quantity, current_price)
            
            if order:
                print(f"✅ 交易成功: {signal.signal} {quantity} {symbol} @ ${current_price:,.2f}")
                
                # 保存交易记录
                trade_data = {
                    'timestamp': order.timestamp.isoformat(),
                    'symbol': symbol,
                    'side': signal.signal,
                    'quantity': quantity,
                    'price': current_price,
                    'value': quantity * current_price,
                    'strategy': 'demo_strategy',
                    'signal_confidence': signal.confidence
                }
                trading_system.db_manager.save_trade(trade_data)
                trading_system.db_manager.save_signal(signal, symbol)
                
            else:
                print("❌ 交易执行失败")
        else:
            print(f"\n⏸️ 信号强度不足或为HOLD，跳过交易")
        
        # 生成性能报告
        print("\n📊 生成性能报告...")
        performance = trading_system.generate_performance_report()
        
        print(f"💰 当前总价值: ${performance['final_balance']:,.2f}")
        print(f"📈 总收益率: {performance['total_return_pct']:.2f}%")
        print(f"🎯 总交易次数: {performance['total_trades']}")
        print(f"✅ 胜率: {performance['win_rate_pct']:.1f}%")
        print(f"📉 最大回撤: {performance['max_drawdown_pct']:.2f}%")
        print(f"📊 夏普比率: {performance['sharpe_ratio']:.3f}")
        
        return trading_system, performance
        
    except Exception as e:
        print(f"❌ 交易系统演示失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def demo_telegram_notifications(config, performance_data):
    """演示Telegram通知功能"""
    print("\n📱 测试Telegram通知功能...")
    
    try:
        from telegram_bot import TelegramNotificationManager
        
        # 创建通知管理器
        notification_manager = TelegramNotificationManager(config)
        print("✅ Telegram通知管理器创建成功")
        
        # 检查配置
        telegram_config = config.get('telegram', {})
        if not telegram_config.get('enabled', False):
            print("ℹ️ Telegram通知已禁用，跳过通知测试")
            return
        
        if not telegram_config.get('bot_token') or telegram_config.get('bot_token') == 'your_bot_token_here':
            print("⚠️ Telegram Bot Token未配置，跳过通知测试")
            return
        
        # 发送测试通知
        print("📤 发送测试通知...")
        
        # 系统启动通知
        notification_manager.send_startup_notification()
        
        # 交易通知
        test_trade_data = {
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'quantity': 0.001,
            'price': 50000.0,
            'value': 50.0,
            'commission': 0.05,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'strategy': 'demo_strategy',
            'signal_confidence': 0.85
        }
        notification_manager.send_trade_notification(test_trade_data)
        
        # 性能报告通知
        if performance_data:
            notification_manager.send_performance_report(performance_data)
        
        # 警报通知
        notification_manager.send_alert('系统测试', '这是一个测试警报消息', 'info')
        
        print("✅ Telegram通知发送完成")
        
    except Exception as e:
        print(f"❌ Telegram通知测试失败: {e}")
        import traceback
        traceback.print_exc()

def demo_web_interface():
    """演示Web界面功能"""
    print("\n🌐 检查Web界面组件...")
    
    try:
        # 检查Flask可用性
        import flask
        print("✅ Flask框架可用")
        
        # 检查Web应用文件
        web_files = [
            'enhanced_futures_web_app.py',
            'web_app/templates',
            'web_app/static'
        ]
        
        for file_path in web_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path} 存在")
            else:
                print(f"⚠️ {file_path} 不存在")
        
        print("ℹ️ Web界面可通过运行 enhanced_futures_web_app.py 启动")
        print("ℹ️ 默认访问地址: http://localhost:5000")
        
    except ImportError:
        print("❌ Flask框架不可用，请安装: pip install flask")
    except Exception as e:
        print(f"❌ Web界面检查失败: {e}")

def demo_database_operations():
    """演示数据库操作"""
    print("\n🗄️ 测试数据库功能...")
    
    try:
        from integrated_trading_system import DatabaseManager
        
        # 创建数据库管理器
        db_manager = DatabaseManager("demo_trading.db")
        print("✅ 数据库初始化成功")
        
        # 测试数据保存
        test_trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'quantity': 0.001,
            'price': 50000.0,
            'value': 50.0,
            'commission': 0.05,
            'strategy': 'demo_strategy',
            'signal_confidence': 0.85
        }
        
        db_manager.save_trade(test_trade)
        print("✅ 交易记录保存成功")
        
        # 测试性能数据保存
        test_performance = {
            'timestamp': datetime.now().isoformat(),
            'total_value': 100050.0,
            'cash': 99950.0,
            'positions_value': 100.0,
            'daily_return': 0.05,
            'cumulative_return': 0.05
        }
        
        db_manager.save_performance(test_performance)
        print("✅ 性能记录保存成功")
        
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        import traceback
        traceback.print_exc()

def demo_risk_management(config):
    """演示风险管理功能"""
    print("\n⚠️ 风险管理功能演示...")
    
    risk_config = config.get('risk_management', {})
    
    print(f"📊 最大单笔损失: {risk_config.get('max_single_loss_pct', 2)}%")
    print(f"📉 最大日损失: {risk_config.get('max_daily_loss_pct', 5)}%")
    print(f"📈 最大回撤: {risk_config.get('max_drawdown_pct', 10)}%")
    print(f"💰 最大持仓比例: {risk_config.get('max_position_size_pct', 20)}%")
    
    # 模拟风险检查
    current_drawdown = 3.5  # 模拟当前回撤
    max_drawdown = risk_config.get('max_drawdown_pct', 10)
    
    if current_drawdown > max_drawdown:
        print(f"🚨 风险警报: 当前回撤 {current_drawdown}% 超过最大允许回撤 {max_drawdown}%")
    else:
        print(f"✅ 风险控制正常: 当前回撤 {current_drawdown}% 在允许范围内")

def main():
    """主演示函数"""
    start_time = datetime.now()
    
    print(f"\n🕐 演示开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python版本: {sys.version.split()[0]}")
    print(f"📁 工作目录: {os.getcwd()}")
    
    # 1. 系统初始化
    config = demo_system_initialization()
    if not config:
        print("❌ 系统初始化失败，演示终止")
        return
    
    # 2. 交易系统演示
    trading_system, performance = demo_trading_system(config)
    
    # 3. 数据库操作演示
    demo_database_operations()
    
    # 4. 风险管理演示
    demo_risk_management(config)
    
    # 5. Telegram通知演示
    demo_telegram_notifications(config, performance)
    
    # 6. Web界面检查
    demo_web_interface()
    
    # 演示总结
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("📊 演示完成总结")
    print("="*60)
    print(f"⏱️ 演示用时: {duration:.2f} 秒")
    print(f"🕐 结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if trading_system and performance:
        print(f"💰 模拟交易结果: {performance['total_return_pct']:.2f}% 收益")
        print(f"📊 交易次数: {performance['total_trades']}")
    
    print("\n✅ 合约量化交易系统演示完成！")
    print("\n📋 下一步操作建议:")
    print("   1. 配置Telegram Bot Token以启用通知功能")
    print("   2. 运行 python enhanced_futures_web_app.py 启动Web界面")
    print("   3. 根据实际需求调整策略参数")
    print("   4. 在纸上交易模式下测试策略")
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 演示被用户中断")
    except Exception as e:
        print(f"\n\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 感谢使用合约量化交易系统！")