"""
Telegram Bot 通知模块
用于量化交易系统的实时通知功能
"""

import requests
import json
import logging
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
import aiohttp
from enum import Enum

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """消息类型枚举"""
    INFO = "ℹ️"
    SUCCESS = "✅"
    WARNING = "⚠️"
    ERROR = "❌"
    TRADE = "💰"
    SIGNAL = "📊"
    PROFIT = "📈"
    LOSS = "📉"
    ALERT = "🚨"

@dataclass
class TelegramMessage:
    """Telegram消息数据类"""
    chat_id: str
    text: str
    message_type: MessageType = MessageType.INFO
    parse_mode: str = "Markdown"
    disable_notification: bool = False

class TelegramBot:
    """Telegram Bot 通知类"""
    
    def __init__(self, bot_token: str, default_chat_id: str = None):
        """
        初始化Telegram Bot
        
        Args:
            bot_token: Bot的API Token
            default_chat_id: 默认聊天ID
        """
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.session = None
        self.message_queue = []
        self.is_running = False
        self.rate_limit_delay = 1  # 发送消息间隔（秒）
        
        # 验证Bot Token
        if self.bot_token and self.bot_token != "your_bot_token_here":
            self.verify_bot()
    
    def verify_bot(self) -> bool:
        """验证Bot Token是否有效"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    logger.info(f"Telegram Bot验证成功: {bot_info['result']['username']}")
                    return True
            
            logger.error("Telegram Bot Token验证失败")
            return False
            
        except Exception as e:
            logger.error(f"验证Telegram Bot时出错: {e}")
            return False
    
    def send_message(self, text: str, chat_id: str = None, 
                    message_type: MessageType = MessageType.INFO,
                    parse_mode: str = "Markdown",
                    disable_notification: bool = False) -> bool:
        """
        发送消息到Telegram
        
        Args:
            text: 消息内容
            chat_id: 聊天ID，如果为None则使用默认ID
            message_type: 消息类型
            parse_mode: 解析模式 (Markdown/HTML)
            disable_notification: 是否禁用通知声音
            
        Returns:
            bool: 发送是否成功
        """
        if not self.bot_token or self.bot_token == "your_bot_token_here":
            logger.warning("Telegram Bot Token未配置，跳过消息发送")
            return False
        
        target_chat_id = chat_id or self.default_chat_id
        if not target_chat_id:
            logger.error("未指定聊天ID")
            return False
        
        # 格式化消息
        formatted_text = f"{message_type.value} {text}"
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': target_chat_id,
                'text': formatted_text,
                'parse_mode': parse_mode,
                'disable_notification': disable_notification
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.debug(f"Telegram消息发送成功: {text[:50]}...")
                    return True
                else:
                    logger.error(f"Telegram API错误: {result.get('description')}")
            else:
                logger.error(f"HTTP错误: {response.status_code}")
                
        except Exception as e:
            logger.error(f"发送Telegram消息时出错: {e}")
        
        return False
    
    def send_trade_notification(self, trade_data: Dict[str, Any]) -> bool:
        """发送交易通知"""
        side_emoji = "🟢" if trade_data['side'] == 'BUY' else "🔴"
        
        message = f"""
{side_emoji} *交易执行通知*

📊 *交易对*: `{trade_data['symbol']}`
🔄 *方向*: `{trade_data['side']}`
💎 *数量*: `{trade_data['quantity']:.6f}`
💰 *价格*: `${trade_data['price']:.2f}`
💵 *金额*: `${trade_data['value']:.2f}`
💸 *手续费*: `${trade_data.get('commission', 0):.2f}`
🕐 *时间*: `{trade_data['timestamp']}`

📈 *策略*: `{trade_data.get('strategy', 'N/A')}`
🎯 *信心度*: `{trade_data.get('signal_confidence', 0)*100:.1f}%`
        """
        
        return self.send_message(message, message_type=MessageType.TRADE)
    
    def send_signal_notification(self, signal_data: Dict[str, Any]) -> bool:
        """发送交易信号通知"""
        signal_emoji = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HOLD': '🟡'
        }.get(signal_data['signal'], '⚪')
        
        message = f"""
{signal_emoji} *交易信号*

📊 *交易对*: `{signal_data['symbol']}`
🎯 *信号*: `{signal_data['signal']}`
💪 *信心度*: `{signal_data['confidence']*100:.1f}%`
💰 *当前价格*: `${signal_data['price']:.2f}`
🕐 *时间*: `{signal_data['timestamp']}`

📋 *原因*: {signal_data['reason']}

📊 *技术指标*:
• RSI: `{signal_data.get('indicators', {}).get('rsi', 0):.1f}`
• MACD: `{signal_data.get('indicators', {}).get('macd', 0):.4f}`
• 短期均线: `${signal_data.get('indicators', {}).get('sma_20', 0):.2f}`
• 长期均线: `${signal_data.get('indicators', {}).get('sma_50', 0):.2f}`
        """
        
        return self.send_message(message, message_type=MessageType.SIGNAL)
    
    def send_performance_report(self, performance_data: Dict[str, Any]) -> bool:
        """发送性能报告"""
        total_return = performance_data.get('total_return', 0)
        return_emoji = "📈" if total_return > 0 else "📉"
        
        message = f"""
{return_emoji} *每日性能报告*

💰 *总收益率*: `{total_return:.2f}%`
📊 *夏普比率*: `{performance_data.get('sharpe_ratio', 0):.3f}`
📉 *最大回撤*: `{performance_data.get('max_drawdown', 0):.2f}%`
🎯 *胜率*: `{performance_data.get('win_rate', 0):.1f}%`

💵 *当前价值*: `${performance_data.get('final_value', 0):.2f}`
💸 *剩余现金*: `${performance_data.get('cash_remaining', 0):.2f}`
🔢 *总交易次数*: `{performance_data.get('total_trades', 0)}`
✅ *盈利交易*: `{performance_data.get('winning_trades', 0)}`

📅 *报告时间*: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
        """
        
        return self.send_message(message, message_type=MessageType.INFO)
    
    def send_alert(self, alert_type: str, message: str, severity: str = "warning") -> bool:
        """发送警报通知"""
        severity_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }.get(severity, "⚠️")
        
        alert_message = f"""
{severity_emoji} *系统警报*

🏷️ *类型*: `{alert_type}`
📝 *详情*: {message}
🕐 *时间*: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`

请及时检查系统状态！
        """
        
        message_type = MessageType.ALERT if severity in ["error", "critical"] else MessageType.WARNING
        return self.send_message(alert_message, message_type=message_type)
    
    def send_system_status(self, status_data: Dict[str, Any]) -> bool:
        """发送系统状态"""
        status_emoji = "🟢" if status_data.get('status') == 'healthy' else "🔴"
        
        message = f"""
{status_emoji} *系统状态报告*

🖥️ *CPU使用率*: `{status_data.get('cpu_usage', 0):.1f}%`
💾 *内存使用率*: `{status_data.get('memory_usage', 0):.1f}%`
💿 *磁盘使用率*: `{status_data.get('disk_usage', 0):.1f}%`
🌐 *网络延迟*: `{status_data.get('network_latency', 0):.0f}ms`

⏱️ *运行时间*: `{status_data.get('uptime', 'N/A')}`
🔄 *最后更新*: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
        """
        
        return self.send_message(message, message_type=MessageType.INFO)
    
    def get_chat_id(self) -> Optional[str]:
        """获取聊天ID（用于初始设置）"""
        try:
            url = f"{self.base_url}/getUpdates"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and data.get('result'):
                    updates = data['result']
                    if updates:
                        # 返回最新消息的聊天ID
                        latest_update = updates[-1]
                        chat_id = latest_update['message']['chat']['id']
                        logger.info(f"检测到聊天ID: {chat_id}")
                        return str(chat_id)
            
            logger.warning("未找到聊天记录，请先向Bot发送消息")
            return None
            
        except Exception as e:
            logger.error(f"获取聊天ID时出错: {e}")
            return None

class TelegramNotificationManager:
    """Telegram通知管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化通知管理器
        
        Args:
            config: 配置字典，包含Telegram相关设置
        """
        self.config = config
        telegram_config = config.get('telegram', {})
        
        self.bot = TelegramBot(
            bot_token=telegram_config.get('bot_token'),
            default_chat_id=telegram_config.get('chat_id')
        )
        
        self.enabled = telegram_config.get('enabled', False)
        self.notification_levels = telegram_config.get('notification_levels', ['trade', 'alert', 'performance'])
        self.quiet_hours = telegram_config.get('quiet_hours', {})
        
        # 消息队列和批处理
        self.message_queue = []
        self.batch_size = telegram_config.get('batch_size', 5)
        self.batch_interval = telegram_config.get('batch_interval', 60)  # 秒
        
        logger.info(f"Telegram通知管理器初始化完成，启用状态: {self.enabled}")
    
    def is_quiet_time(self) -> bool:
        """检查是否在静默时间"""
        if not self.quiet_hours.get('enabled', False):
            return False
        
        current_time = datetime.now().time()
        start_time = datetime.strptime(self.quiet_hours.get('start', '22:00'), '%H:%M').time()
        end_time = datetime.strptime(self.quiet_hours.get('end', '08:00'), '%H:%M').time()
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:  # 跨天的情况
            return current_time >= start_time or current_time <= end_time
    
    def should_send_notification(self, notification_type: str) -> bool:
        """判断是否应该发送通知"""
        if not self.enabled:
            return False
        
        if notification_type not in self.notification_levels:
            return False
        
        if self.is_quiet_time() and notification_type not in ['alert', 'error']:
            return False
        
        return True
    
    def send_trade_notification(self, trade_data: Dict[str, Any]) -> bool:
        """发送交易通知"""
        if not self.should_send_notification('trade'):
            return False
        
        return self.bot.send_trade_notification(trade_data)
    
    def send_signal_notification(self, signal_data: Dict[str, Any]) -> bool:
        """发送信号通知"""
        if not self.should_send_notification('signal'):
            return False
        
        return self.bot.send_signal_notification(signal_data)
    
    def send_performance_report(self, performance_data: Dict[str, Any]) -> bool:
        """发送性能报告"""
        if not self.should_send_notification('performance'):
            return False
        
        return self.bot.send_performance_report(performance_data)
    
    def send_alert(self, alert_type: str, message: str, severity: str = "warning") -> bool:
        """发送警报"""
        if not self.should_send_notification('alert'):
            return False
        
        return self.bot.send_alert(alert_type, message, severity)
    
    def send_system_status(self, status_data: Dict[str, Any]) -> bool:
        """发送系统状态"""
        if not self.should_send_notification('system'):
            return False
        
        return self.bot.send_system_status(status_data)
    
    def send_startup_notification(self) -> bool:
        """发送启动通知"""
        message = f"""
🚀 *交易系统启动*

系统已成功启动并开始运行。

🕐 *启动时间*: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
⚙️ *运行模式*: `{self.config.get('mode', 'unknown')}`
📊 *监控交易对*: `{self.config.get('strategy', {}).get('symbol', 'N/A')}`

系统将开始监控市场并发送相关通知。
        """
        
        return self.bot.send_message(message, message_type=MessageType.SUCCESS)
    
    def send_shutdown_notification(self) -> bool:
        """发送关闭通知"""
        message = f"""
🛑 *交易系统关闭*

系统已停止运行。

🕐 *关闭时间*: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`

如需重新启动，请检查系统状态。
        """
        
        return self.bot.send_message(message, message_type=MessageType.WARNING)

# 测试函数
def test_telegram_bot():
    """测试Telegram Bot功能"""
    # 测试配置
    test_config = {
        'telegram': {
            'enabled': True,
            'bot_token': 'your_bot_token_here',  # 替换为实际的Bot Token
            'chat_id': 'your_chat_id_here',      # 替换为实际的Chat ID
            'notification_levels': ['trade', 'signal', 'alert', 'performance'],
            'quiet_hours': {
                'enabled': False,
                'start': '22:00',
                'end': '08:00'
            }
        }
    }
    
    # 创建通知管理器
    notification_manager = TelegramNotificationManager(test_config)
    
    # 测试各种通知
    print("测试Telegram Bot通知功能...")
    
    # 测试交易通知
    trade_data = {
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'quantity': 0.001,
        'price': 50000.0,
        'value': 50.0,
        'commission': 0.05,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'strategy': 'test_strategy',
        'signal_confidence': 0.85
    }
    
    notification_manager.send_trade_notification(trade_data)
    
    # 测试信号通知
    signal_data = {
        'symbol': 'BTCUSDT',
        'signal': 'BUY',
        'confidence': 0.75,
        'price': 50000.0,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'reason': '技术指标显示买入信号',
        'indicators': {
            'rsi': 35.5,
            'macd': 0.0123,
            'sma_20': 49800.0,
            'sma_50': 49500.0
        }
    }
    
    notification_manager.send_signal_notification(signal_data)
    
    # 测试警报
    notification_manager.send_alert('风险警报', '最大回撤超过阈值', 'warning')
    
    print("测试完成！请检查Telegram消息。")

if __name__ == "__main__":
    test_telegram_bot()

