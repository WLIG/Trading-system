# 增强版量化交易系统配置文件
# ================================================
# 包含Telegram Bot通知功能的完整配置
# ================================================

import os
from typing import Dict, Any, List
from datetime import datetime

# =============================================================================
# API配置
# =============================================================================

# 币安API密钥
API_KEY = os.getenv('BINANCE_API_KEY', "your_api_key_here")
API_SECRET = os.getenv('BINANCE_API_SECRET', "your_api_secret_here")

# 网络配置
USE_TESTNET = True  # True使用测试网络，False使用主网
REQUEST_TIMEOUT = 30  # 请求超时时间(秒)
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 1.0  # 重试延迟(秒)

# =============================================================================
# 交易配置
# =============================================================================

# 基础交易参数
TRADING_SYMBOL = "BTCUSDT"  # 交易对
TRADING_QUANTITY = 0.001  # 每次交易数量
MAX_POSITION = 0.01  # 最大持仓
MIN_TRADE_AMOUNT = 10  # 最小交易金额 (USDT)

# 交易模式
TRADING_MODE = "backtest"  # backtest, paper, live

# 交易限制
MAX_DAILY_TRADES = 50  # 每日最大交易次数
MAX_DAILY_LOSS_PCT = 0.10  # 每日最大亏损百分比 (10%)
POSITION_SIZE_PCT = 0.05  # 每次交易占总资金的百分比 (5%)

# =============================================================================
# 策略参数
# =============================================================================

# RSI参数
RSI_PERIOD = 14  # RSI计算周期
RSI_OVERBOUGHT = 70  # RSI超买阈值
RSI_OVERSOLD = 30  # RSI超卖阈值

# 移动平均线参数
MA_SHORT = 10  # 短期移动平均线周期
MA_LONG = 20  # 长期移动平均线周期

# MACD参数
MACD_FAST = 12  # MACD快线周期
MACD_SLOW = 26  # MACD慢线周期
MACD_SIGNAL = 9  # MACD信号线周期

# 布林带参数
BB_PERIOD = 20  # 布林带周期
BB_STD_DEV = 2  # 布林带标准差倍数

# KDJ参数
KDJ_PERIOD = 14  # KDJ周期
KDJ_SMOOTH_K = 3  # K值平滑周期
KDJ_SMOOTH_D = 3  # D值平滑周期

# 信号过滤
MIN_SIGNAL_CONFIDENCE = 0.6  # 最小信号置信度
SIGNAL_COOLDOWN = 300  # 信号冷却时间(秒)

# =============================================================================
# 风险管理
# =============================================================================

# 止损止盈
STOP_LOSS_PCT = 0.02  # 止损百分比 (2%)
TAKE_PROFIT_PCT = 0.04  # 止盈百分比 (4%)

# 动态止损
TRAILING_STOP = True  # 是否启用追踪止损
TRAILING_STOP_PCT = 0.015  # 追踪止损百分比 (1.5%)

# 资金管理
MAX_DRAWDOWN_PCT = 0.20  # 最大回撤百分比 (20%)
RISK_PER_TRADE_PCT = 0.01  # 每笔交易风险百分比 (1%)

# 仓位管理
POSITION_SIZING_METHOD = "fixed"  # fixed, percentage, kelly, volatility
VOLATILITY_LOOKBACK = 20  # 波动率回看周期

# =============================================================================
# Telegram Bot 配置
# =============================================================================

# Telegram Bot 基础配置
TELEGRAM_ENABLED = True  # 是否启用Telegram通知
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', "your_bot_token_here")
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', "your_chat_id_here")

# 通知级别配置
TELEGRAM_NOTIFICATION_LEVELS = [
    'trade',        # 交易执行通知
    'signal',       # 交易信号通知
    'alert',        # 系统警报
    'performance',  # 性能报告
    'system',       # 系统状态
    'error'         # 错误通知
]

# 静默时间配置
TELEGRAM_QUIET_HOURS = {
    'enabled': False,  # 是否启用静默时间
    'start': '22:00',  # 静默开始时间
    'end': '08:00',    # 静默结束时间
    'timezone': 'Asia/Shanghai'  # 时区
}

# 消息批处理配置
TELEGRAM_BATCH_MESSAGES = False  # 是否批量发送消息
TELEGRAM_BATCH_SIZE = 5  # 批处理大小
TELEGRAM_BATCH_INTERVAL = 60  # 批处理间隔(秒)

# 消息格式配置
TELEGRAM_MESSAGE_FORMAT = {
    'parse_mode': 'Markdown',  # Markdown 或 HTML
    'disable_web_page_preview': True,  # 禁用网页预览
    'disable_notification': False  # 禁用通知声音
}

# 特殊通知配置
TELEGRAM_TRADE_NOTIFICATIONS = {
    'enabled': True,
    'min_trade_value': 10.0,  # 最小通知交易金额
    'include_charts': False,  # 是否包含图表
    'include_indicators': True  # 是否包含技术指标
}

TELEGRAM_ALERT_NOTIFICATIONS = {
    'enabled': True,
    'severity_levels': ['warning', 'error', 'critical'],  # 通知的严重级别
    'immediate_alerts': ['system_error', 'api_error', 'risk_breach']  # 立即通知的警报类型
}

TELEGRAM_PERFORMANCE_REPORTS = {
    'enabled': True,
    'daily_report': True,  # 每日报告
    'weekly_report': True,  # 周报告
    'monthly_report': True,  # 月报告
    'report_time': '09:00',  # 报告发送时间
    'include_charts': False  # 是否包含图表
}

# =============================================================================
# 运行配置
# =============================================================================

# 时间间隔
CHECK_INTERVAL = 60  # 主循环检查间隔 (秒)
DATA_UPDATE_INTERVAL = 30  # 数据更新间隔 (秒)
STATUS_REPORT_INTERVAL = 300  # 状态报告间隔 (秒)
PERFORMANCE_REPORT_INTERVAL = 3600  # 性能报告间隔 (秒)

# 数据配置
KLINE_LIMIT = 100  # K线数据获取数量
KLINE_INTERVAL = "1h"  # K线时间间隔

# =============================================================================
# 数据库配置
# =============================================================================

# 数据库设置
USE_DATABASE = True
DATABASE_TYPE = "sqlite"  # sqlite, postgresql, mysql
DATABASE_URL = "sqlite:///trading_system.db"

# PostgreSQL配置 (如果使用)
POSTGRES_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'trading_system'),
    'username': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

# 数据保留策略
DATA_RETENTION = {
    'trades': 365,      # 交易记录保留天数
    'signals': 90,      # 信号记录保留天数
    'performance': 730, # 性能记录保留天数
    'logs': 30         # 日志保留天数
}

# =============================================================================
# 日志配置
# =============================================================================

# 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# 日志文件配置
LOG_FILE = "trading_system.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5  # 保留5个备份文件

# 日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 日志输出配置
LOG_TO_FILE = True
LOG_TO_CONSOLE = True
LOG_TO_TELEGRAM = True  # 错误日志发送到Telegram

# =============================================================================
# 邮件通知配置 (可选)
# =============================================================================

# 邮件通知
EMAIL_NOTIFICATIONS = False
EMAIL_CONFIG = {
    'smtp_server': "smtp.gmail.com",
    'smtp_port': 587,
    'username': os.getenv('EMAIL_USER', ''),
    'password': os.getenv('EMAIL_PASSWORD', ''),
    'from_email': os.getenv('EMAIL_FROM', ''),
    'to_email': os.getenv('EMAIL_TO', ''),
    'use_tls': True
}

# =============================================================================
# 微信通知配置 (可选)
# =============================================================================

# 企业微信机器人
WECHAT_NOTIFICATIONS = False
WECHAT_WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL', '')

# =============================================================================
# 回测配置
# =============================================================================

# 回测参数
BACKTEST_START_DATE = "2023-01-01"
BACKTEST_END_DATE = "2024-01-01"
BACKTEST_INITIAL_BALANCE = 100000  # 初始资金 (USDT)
BACKTEST_COMMISSION_RATE = 0.001  # 回测佣金费率
BACKTEST_SLIPPAGE_RATE = 0.0005  # 回测滑点费率

# =============================================================================
# Web界面配置
# =============================================================================

# Flask应用配置
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
WEB_DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# 安全配置
ENABLE_AUTHENTICATION = False  # 是否启用身份验证
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# =============================================================================
# 高级配置
# =============================================================================

# 性能优化
USE_WEBSOCKET = False  # 是否使用WebSocket实时数据
CACHE_MARKET_DATA = True  # 是否缓存市场数据
CACHE_DURATION = 30  # 缓存持续时间(秒)

# 并发配置
MAX_WORKERS = 4  # 最大工作线程数
ASYNC_PROCESSING = True  # 是否启用异步处理

# 调试模式
DEBUG_MODE = False  # 调试模式
DRY_RUN = False  # 模拟交易模式(不实际下单)
VERBOSE_LOGGING = False  # 详细日志

# 监控配置
ENABLE_METRICS = True  # 启用指标收集
METRICS_PORT = 8080  # 指标端口
HEALTH_CHECK_INTERVAL = 60  # 健康检查间隔

# =============================================================================
# 系统配置类
# =============================================================================

class TradingSystemConfig:
    """交易系统配置类"""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        # 基础配置
        self.api_config = {
            'api_key': API_KEY,
            'api_secret': API_SECRET,
            'use_testnet': USE_TESTNET,
            'timeout': REQUEST_TIMEOUT,
            'max_retries': MAX_RETRIES
        }
        
        # 交易配置
        self.trading_config = {
            'symbol': TRADING_SYMBOL,
            'quantity': TRADING_QUANTITY,
            'max_position': MAX_POSITION,
            'min_trade_amount': MIN_TRADE_AMOUNT,
            'mode': TRADING_MODE,
            'max_daily_trades': MAX_DAILY_TRADES,
            'max_daily_loss_pct': MAX_DAILY_LOSS_PCT
        }
        
        # 策略配置
        self.strategy_config = {
            'rsi_period': RSI_PERIOD,
            'rsi_overbought': RSI_OVERBOUGHT,
            'rsi_oversold': RSI_OVERSOLD,
            'ma_short': MA_SHORT,
            'ma_long': MA_LONG,
            'macd_fast': MACD_FAST,
            'macd_slow': MACD_SLOW,
            'macd_signal': MACD_SIGNAL,
            'bb_period': BB_PERIOD,
            'bb_std_dev': BB_STD_DEV,
            'min_signal_confidence': MIN_SIGNAL_CONFIDENCE
        }
        
        # 风险管理配置
        self.risk_config = {
            'stop_loss_pct': STOP_LOSS_PCT,
            'take_profit_pct': TAKE_PROFIT_PCT,
            'trailing_stop': TRAILING_STOP,
            'trailing_stop_pct': TRAILING_STOP_PCT,
            'max_drawdown_pct': MAX_DRAWDOWN_PCT,
            'risk_per_trade_pct': RISK_PER_TRADE_PCT
        }
        
        # Telegram配置
        self.telegram_config = {
            'enabled': TELEGRAM_ENABLED,
            'bot_token': TELEGRAM_BOT_TOKEN,
            'chat_id': TELEGRAM_CHAT_ID,
            'notification_levels': TELEGRAM_NOTIFICATION_LEVELS,
            'quiet_hours': TELEGRAM_QUIET_HOURS,
            'batch_messages': TELEGRAM_BATCH_MESSAGES,
            'batch_size': TELEGRAM_BATCH_SIZE,
            'batch_interval': TELEGRAM_BATCH_INTERVAL,
            'message_format': TELEGRAM_MESSAGE_FORMAT,
            'trade_notifications': TELEGRAM_TRADE_NOTIFICATIONS,
            'alert_notifications': TELEGRAM_ALERT_NOTIFICATIONS,
            'performance_reports': TELEGRAM_PERFORMANCE_REPORTS
        }
        
        # 数据库配置
        self.database_config = {
            'use_database': USE_DATABASE,
            'database_type': DATABASE_TYPE,
            'database_url': DATABASE_URL,
            'postgres_config': POSTGRES_CONFIG,
            'data_retention': DATA_RETENTION
        }
        
        # 运行配置
        self.runtime_config = {
            'check_interval': CHECK_INTERVAL,
            'data_update_interval': DATA_UPDATE_INTERVAL,
            'status_report_interval': STATUS_REPORT_INTERVAL,
            'performance_report_interval': PERFORMANCE_REPORT_INTERVAL,
            'kline_limit': KLINE_LIMIT,
            'kline_interval': KLINE_INTERVAL
        }
    
    def get_full_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return {
            'api': self.api_config,
            'trading': self.trading_config,
            'strategy': self.strategy_config,
            'risk': self.risk_config,
            'telegram': self.telegram_config,
            'database': self.database_config,
            'runtime': self.runtime_config
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        errors = []
        warnings = []
        
        # 验证API配置
        if self.api_config['api_key'] == "your_api_key_here":
            errors.append("请设置有效的BINANCE_API_KEY")
        
        if self.api_config['api_secret'] == "your_api_secret_here":
            errors.append("请设置有效的BINANCE_API_SECRET")
        
        # 验证Telegram配置
        if self.telegram_config['enabled']:
            if self.telegram_config['bot_token'] == "your_bot_token_here":
                errors.append("请设置有效的TELEGRAM_BOT_TOKEN")
            
            if self.telegram_config['chat_id'] == "your_chat_id_here":
                warnings.append("请设置TELEGRAM_CHAT_ID以接收通知")
        
        # 验证交易参数
        if self.trading_config['quantity'] <= 0:
            errors.append("TRADING_QUANTITY必须大于0")
        
        if self.risk_config['stop_loss_pct'] <= 0:
            errors.append("STOP_LOSS_PCT必须大于0")
        
        # 验证策略参数
        if self.strategy_config['ma_short'] >= self.strategy_config['ma_long']:
            errors.append("MA_SHORT必须小于MA_LONG")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'is_valid': len(errors) == 0
        }

# 创建全局配置实例
config = TradingSystemConfig()

# =============================================================================
# 配置验证
# =============================================================================

def validate_config() -> Dict[str, Any]:
    """验证配置函数"""
    return config.validate_config()

def get_config_summary() -> Dict[str, Any]:
    """获取配置摘要"""
    return config.get_full_config()

# 在导入时进行配置验证
if __name__ != "__main__":
    validation_result = validate_config()
    if not validation_result['is_valid']:
        print("配置验证失败:")
        for error in validation_result['errors']:
            print(f"  错误: {error}")
    
    if validation_result['warnings']:
        print("配置警告:")
        for warning in validation_result['warnings']:
            print(f"  警告: {warning}")

# =============================================================================
# 环境变量模板
# =============================================================================

ENV_TEMPLATE = """
# 币安API配置
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here

# Telegram Bot配置
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# 数据库配置 (可选)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_system
DB_USER=postgres
DB_PASSWORD=your_db_password

# 邮件配置 (可选)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@gmail.com

# Web应用配置
SECRET_KEY=your_secret_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_admin_password

# 微信配置 (可选)
WECHAT_WEBHOOK_URL=your_wechat_webhook_url
"""

if __name__ == "__main__":
    print("增强版配置文件")
    print("=" * 50)
    
    # 显示配置验证结果
    validation_result = validate_config()
    print(f"配置验证: {'通过' if validation_result['is_valid'] else '失败'}")
    
    if validation_result['errors']:
        print("\n错误:")
        for error in validation_result['errors']:
            print(f"  - {error}")
    
    if validation_result['warnings']:
        print("\n警告:")
        for warning in validation_result['warnings']:
            print(f"  - {warning}")
    
    # 显示环境变量模板
    print("\n环境变量模板 (.env 文件):")
    print(ENV_TEMPLATE)

