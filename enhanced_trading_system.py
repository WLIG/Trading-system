"""
增强版量化交易系统
集成Telegram Bot通知功能的完整交易系统
"""

import sys
import os
import time
import threading
import signal
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入模块
from enhanced_config import TradingSystemConfig, validate_config
from telegram_bot import TelegramNotificationManager
from integrated_trading_system import (
    IntegratedTradingSystem, AdvancedStrategy, DatabaseManager,
    TradingSignal, TradingMode, MessageType
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_trading_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedTradingSystem(IntegratedTradingSystem):
    """增强版交易系统，集成Telegram通知功能"""
    
    def __init__(self, config_obj: TradingSystemConfig = None):
        """
        初始化增强版交易系统
        
        Args:
            config_obj: 配置对象
        """
        if config_obj is None:
            config_obj = TradingSystemConfig()
        
        self.config_obj = config_obj
        self.full_config = config_obj.get_full_config()
        
        # 初始化父类
        super().__init__(self.full_config)
        
        # 初始化Telegram通知管理器
        self.telegram_manager = TelegramNotificationManager(self.full_config)
        
        # 系统状态
        self.is_running = False
        self.start_time = None
        self.last_health_check = None
        self.error_count = 0
        self.max_errors = 10
        
        # 性能统计
        self.daily_stats = {
            'trades': 0,
            'profit': 0.0,
            'loss': 0.0,
            'start_value': 0.0
        }
        
        # 定时任务
        self.report_timer = None
        self.health_check_timer = None
        
        logger.info("增强版交易系统初始化完成")
    
    def start_system(self):
        """启动交易系统"""
        try:
            logger.info("正在启动增强版交易系统...")
            
            # 验证配置
            validation_result = self.config_obj.validate_config()
            if not validation_result['is_valid']:
                error_msg = "配置验证失败: " + "; ".join(validation_result['errors'])
                logger.error(error_msg)
                self.telegram_manager.send_alert("配置错误", error_msg, "error")
                return False
            
            # 显示警告
            if validation_result['warnings']:
                warning_msg = "; ".join(validation_result['warnings'])
                logger.warning(f"配置警告: {warning_msg}")
                self.telegram_manager.send_alert("配置警告", warning_msg, "warning")
            
            # 设置系统状态
            self.is_running = True
            self.start_time = datetime.now()
            self.daily_stats['start_value'] = self.total_value
            
            # 发送启动通知
            self.telegram_manager.send_startup_notification()
            
            # 启动定时任务
            self.start_scheduled_tasks()
            
            # 注册信号处理器
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            logger.info("增强版交易系统启动成功")
            return True
            
        except Exception as e:
            error_msg = f"系统启动失败: {e}"
            logger.error(error_msg)
            self.telegram_manager.send_alert("启动失败", error_msg, "critical")
            return False
    
    def stop_system(self):
        """停止交易系统"""
        try:
            logger.info("正在停止交易系统...")
            
            self.is_running = False
            
            # 停止定时任务
            self.stop_scheduled_tasks()
            
            # 生成最终报告
            final_report = self.generate_performance_report()
            
            # 发送关闭通知
            self.telegram_manager.send_shutdown_notification()
            
            logger.info("交易系统已停止")
            
        except Exception as e:
            logger.error(f"停止系统时出错: {e}")
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"接收到信号 {signum}，正在优雅关闭...")
        self.stop_system()
        sys.exit(0)
    
    def start_scheduled_tasks(self):
        """启动定时任务"""
        # 性能报告定时器
        report_interval = self.full_config['runtime']['performance_report_interval']
        self.report_timer = threading.Timer(report_interval, self.send_performance_report)
        self.report_timer.daemon = True
        self.report_timer.start()
        
        # 健康检查定时器
        health_interval = self.full_config['runtime']['status_report_interval']
        self.health_check_timer = threading.Timer(health_interval, self.health_check)
        self.health_check_timer.daemon = True
        self.health_check_timer.start()
        
        logger.info("定时任务已启动")
    
    def stop_scheduled_tasks(self):
        """停止定时任务"""
        if self.report_timer:
            self.report_timer.cancel()
        
        if self.health_check_timer:
            self.health_check_timer.cancel()
        
        logger.info("定时任务已停止")
    
    def execute_order(self, signal: TradingSignal, quantity: float) -> Optional[Any]:
        """执行订单并发送通知"""
        try:
            # 执行订单
            order = super().execute_order(signal, quantity)
            
            if order:
                # 更新日统计
                trade_value = order.quantity * order.avg_price
                if order.side.value == 'BUY':
                    self.daily_stats['trades'] += 1
                else:
                    # 计算盈亏（简化）
                    if signal.symbol in self.positions:
                        cost_basis = self.positions[signal.symbol].avg_price * order.quantity
                        pnl = trade_value - cost_basis
                        if pnl > 0:
                            self.daily_stats['profit'] += pnl
                        else:
                            self.daily_stats['loss'] += abs(pnl)
                    self.daily_stats['trades'] += 1
                
                # 发送交易通知
                trade_data = {
                    'symbol': order.symbol,
                    'side': order.side.value,
                    'quantity': order.quantity,
                    'price': order.avg_price,
                    'value': trade_value,
                    'commission': trade_value * self.config.get('commission_rate', 0.001),
                    'timestamp': order.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'strategy': 'enhanced_strategy',
                    'signal_confidence': signal.confidence
                }
                
                self.telegram_manager.send_trade_notification(trade_data)
                
                # 保存到数据库
                self.db_manager.save_trade(trade_data)
                
            return order
            
        except Exception as e:
            error_msg = f"执行订单时出错: {e}"
            logger.error(error_msg)
            self.telegram_manager.send_alert("交易错误", error_msg, "error")
            self.error_count += 1
            
            if self.error_count >= self.max_errors:
                self.telegram_manager.send_alert(
                    "系统错误", 
                    f"错误次数达到上限({self.max_errors})，系统将停止", 
                    "critical"
                )
                self.stop_system()
            
            return None
    
    def run_strategy(self, symbol: str, duration_hours: int = 24):
        """运行策略并发送通知"""
        logger.info(f"开始运行增强策略，交易对: {symbol}，持续时间: {duration_hours}小时")
        
        # 发送策略启动通知
        start_message = f"""
🚀 *策略启动*

📊 *交易对*: `{symbol}`
⏰ *运行时长*: `{duration_hours}小时`
💰 *初始资金*: `${self.total_value:.2f}`
⚙️ *运行模式*: `{self.mode.value}`

策略开始监控市场...
        """
        
        self.telegram_manager.bot.send_message(start_message, message_type=MessageType.SUCCESS)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        while datetime.now() < end_time and self.is_running:
            try:
                # 获取市场数据
                market_data = self.get_market_data(symbol)
                
                # 生成交易信号
                signal = self.strategy.analyze(market_data)
                
                # 保存信号
                self.db_manager.save_signal(signal)
                
                # 发送信号通知（仅高置信度信号）
                if signal.confidence >= 0.7:
                    signal_data = {
                        'symbol': signal.symbol,
                        'signal': signal.signal,
                        'confidence': signal.confidence,
                        'price': signal.price,
                        'timestamp': signal.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'reason': signal.reason,
                        'indicators': signal.indicators
                    }
                    
                    self.telegram_manager.send_signal_notification(signal_data)
                
                logger.info(f"信号: {signal.signal}, 置信度: {signal.confidence:.2f}, "
                          f"价格: {signal.price:.2f}, 原因: {signal.reason}")
                
                # 执行交易
                if signal.signal in ['BUY', 'SELL'] and signal.confidence >= self.full_config['strategy']['min_signal_confidence']:
                    # 计算交易数量
                    if signal.signal == 'BUY':
                        max_trade_value = self.cash * self.full_config['trading']['position_size_pct']
                        quantity = max_trade_value / signal.price
                    else:  # SELL
                        if symbol in self.positions:
                            quantity = self.positions[symbol].quantity * 0.5  # 卖出一半持仓
                        else:
                            quantity = 0
                    
                    if quantity > 0:
                        order = self.execute_order(signal, quantity)
                        if order:
                            logger.info(f"交易执行: {order.side.value} {order.quantity} {symbol}")
                
                # 更新投资组合价值
                self.update_portfolio_value()
                
                # 记录权益曲线
                self.equity_curve.append({
                    'timestamp': datetime.now(),
                    'total_value': self.total_value
                })
                
                # 风险检查
                self.risk_check()
                
                # 等待下一次检查
                time.sleep(self.full_config['runtime']['check_interval'])
                
            except KeyboardInterrupt:
                logger.info("用户中断，停止策略运行")
                break
            except Exception as e:
                error_msg = f"策略运行错误: {e}"
                logger.error(error_msg)
                self.telegram_manager.send_alert("策略错误", error_msg, "error")
                time.sleep(60)  # 错误后等待1分钟再继续
        
        # 生成最终报告
        final_report = self.generate_performance_report()
        self.send_performance_report()
    
    def risk_check(self):
        """风险检查"""
        try:
            # 检查最大回撤
            if self.equity_curve:
                equity_values = [point['total_value'] for point in self.equity_curve]
                peak = max(equity_values)
                current_value = equity_values[-1]
                drawdown = (peak - current_value) / peak
                
                max_drawdown_threshold = self.full_config['risk']['max_drawdown_pct']
                
                if drawdown > max_drawdown_threshold:
                    alert_msg = f"最大回撤({drawdown*100:.2f}%)超过阈值({max_drawdown_threshold*100:.2f}%)"
                    self.telegram_manager.send_alert("风险警报", alert_msg, "warning")
                    logger.warning(alert_msg)
            
            # 检查日损失
            daily_loss_pct = abs(self.daily_stats['loss']) / self.daily_stats['start_value']
            max_daily_loss = self.full_config['trading']['max_daily_loss_pct']
            
            if daily_loss_pct > max_daily_loss:
                alert_msg = f"日损失({daily_loss_pct*100:.2f}%)超过阈值({max_daily_loss*100:.2f}%)"
                self.telegram_manager.send_alert("风险警报", alert_msg, "critical")
                logger.error(alert_msg)
                
                # 停止交易
                self.stop_system()
            
        except Exception as e:
            logger.error(f"风险检查时出错: {e}")
    
    def health_check(self):
        """系统健康检查"""
        try:
            import psutil
            
            # 获取系统资源使用情况
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 检查系统资源
            if cpu_usage > 80:
                self.telegram_manager.send_alert("系统警报", f"CPU使用率过高: {cpu_usage:.1f}%", "warning")
            
            if memory.percent > 80:
                self.telegram_manager.send_alert("系统警报", f"内存使用率过高: {memory.percent:.1f}%", "warning")
            
            if disk.percent > 90:
                self.telegram_manager.send_alert("系统警报", f"磁盘使用率过高: {disk.percent:.1f}%", "warning")
            
            # 更新最后检查时间
            self.last_health_check = datetime.now()
            
            # 重新设置定时器
            if self.is_running:
                health_interval = self.full_config['runtime']['status_report_interval']
                self.health_check_timer = threading.Timer(health_interval, self.health_check)
                self.health_check_timer.daemon = True
                self.health_check_timer.start()
            
        except Exception as e:
            logger.error(f"健康检查时出错: {e}")
    
    def send_performance_report(self):
        """发送性能报告"""
        try:
            # 生成性能报告
            performance_data = self.generate_performance_report()
            
            # 发送Telegram通知
            self.telegram_manager.send_performance_report(performance_data)
            
            # 重新设置定时器
            if self.is_running:
                report_interval = self.full_config['runtime']['performance_report_interval']
                self.report_timer = threading.Timer(report_interval, self.send_performance_report)
                self.report_timer.daemon = True
                self.report_timer.start()
            
        except Exception as e:
            logger.error(f"发送性能报告时出错: {e}")
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """生成增强版性能报告"""
        # 调用父类方法
        base_report = super().generate_performance_report()
        
        # 添加增强信息
        if self.start_time:
            running_time = datetime.now() - self.start_time
            base_report['running_time_hours'] = running_time.total_seconds() / 3600
        
        base_report['daily_trades'] = self.daily_stats['trades']
        base_report['daily_profit'] = self.daily_stats['profit']
        base_report['daily_loss'] = self.daily_stats['loss']
        base_report['error_count'] = self.error_count
        
        return base_report

class TelegramBotSetupHelper:
    """Telegram Bot设置助手"""
    
    @staticmethod
    def create_bot_instructions():
        """创建Bot设置说明"""
        instructions = """
# Telegram Bot 设置指南

## 1. 创建Telegram Bot

### 步骤1: 联系BotFather
1. 在Telegram中搜索 `@BotFather`
2. 发送 `/start` 开始对话
3. 发送 `/newbot` 创建新的Bot

### 步骤2: 设置Bot信息
1. 输入Bot的显示名称，例如: `我的交易机器人`
2. 输入Bot的用户名，必须以`bot`结尾，例如: `my_trading_bot`
3. BotFather会返回Bot Token，格式类似: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### 步骤3: 配置Bot权限
发送以下命令给BotFather:
- `/setprivacy` - 设置隐私模式为Disabled
- `/setjoingroups` - 允许Bot加入群组
- `/setcommands` - 设置Bot命令

## 2. 获取Chat ID

### 方法1: 直接获取
1. 向你的Bot发送任意消息
2. 访问: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. 在返回的JSON中找到 `chat.id` 字段

### 方法2: 使用代码获取
```python
from telegram_bot import TelegramBot

bot = TelegramBot("YOUR_BOT_TOKEN")
chat_id = bot.get_chat_id()
print(f"Chat ID: {chat_id}")
```

## 3. 配置环境变量

创建 `.env` 文件:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

## 4. 测试Bot功能

运行测试脚本:
```bash
python telegram_bot.py
```

## 5. Bot命令设置

向BotFather发送 `/setcommands`，然后输入:
```
start - 启动Bot
status - 查看系统状态
report - 获取性能报告
stop - 停止通知
help - 帮助信息
```
        """
        return instructions
    
    @staticmethod
    def test_bot_connection(bot_token: str, chat_id: str = None):
        """测试Bot连接"""
        from telegram_bot import TelegramBot
        
        print("正在测试Telegram Bot连接...")
        
        # 创建Bot实例
        bot = TelegramBot(bot_token, chat_id)
        
        # 验证Bot
        if bot.verify_bot():
            print("✅ Bot Token验证成功")
        else:
            print("❌ Bot Token验证失败")
            return False
        
        # 获取Chat ID（如果未提供）
        if not chat_id:
            print("正在获取Chat ID...")
            chat_id = bot.get_chat_id()
            if chat_id:
                print(f"✅ 检测到Chat ID: {chat_id}")
            else:
                print("❌ 未找到Chat ID，请先向Bot发送消息")
                return False
        
        # 发送测试消息
        test_message = "🧪 这是一条测试消息，如果您收到此消息，说明Telegram Bot配置成功！"
        if bot.send_message(test_message, chat_id):
            print("✅ 测试消息发送成功")
            return True
        else:
            print("❌ 测试消息发送失败")
            return False

def main():
    """主函数"""
    print("增强版量化交易系统")
    print("=" * 50)
    
    # 验证配置
    validation_result = validate_config()
    if not validation_result['is_valid']:
        print("配置验证失败:")
        for error in validation_result['errors']:
            print(f"  ❌ {error}")
        
        print("\n请检查配置文件并重新运行。")
        return
    
    if validation_result['warnings']:
        print("配置警告:")
        for warning in validation_result['warnings']:
            print(f"  ⚠️ {warning}")
    
    # 创建配置对象
    config = TradingSystemConfig()
    
    # 创建交易系统
    system = EnhancedTradingSystem(config)
    
    # 启动系统
    if system.start_system():
        try:
            # 运行策略
            symbol = config.trading_config['symbol']
            system.run_strategy(symbol, duration_hours=24)
        except KeyboardInterrupt:
            print("\n用户中断，正在停止系统...")
        finally:
            system.stop_system()
    else:
        print("系统启动失败")

if __name__ == "__main__":
    main()

