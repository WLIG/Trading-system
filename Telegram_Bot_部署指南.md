# Telegram Bot 完整部署指南

## 📋 概述

本指南将详细介绍如何为量化交易系统配置和部署Telegram Bot，实现实时交易通知功能。

## 🤖 第一步：创建Telegram Bot

### 1.1 联系BotFather

1. 打开Telegram应用
2. 搜索 `@BotFather` 并开始对话
3. 发送 `/start` 命令

### 1.2 创建新Bot

1. 发送 `/newbot` 命令
2. 输入Bot的显示名称（例如：`我的量化交易助手`）
3. 输入Bot的用户名（必须以`bot`结尾，例如：`my_quant_trading_bot`）

### 1.3 获取Bot Token

BotFather会返回类似以下格式的Token：
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
```

**⚠️ 重要：请妥善保管此Token，不要泄露给他人！**

### 1.4 配置Bot设置

向BotFather发送以下命令来配置Bot：

```
/setdescription
```
输入描述：`量化交易系统通知机器人，提供实时交易信号和性能报告`

```
/setabouttext
```
输入简介：`专业的量化交易通知助手`

```
/setuserpic
```
上传Bot头像（可选）

```
/setcommands
```
设置Bot命令：
```
start - 启动Bot并获取帮助
status - 查看系统运行状态
report - 获取最新性能报告
settings - 查看通知设置
stop - 停止接收通知
help - 获取帮助信息
```

## 🆔 第二步：获取Chat ID

### 2.1 方法一：通过API获取

1. 向你的Bot发送任意消息（例如：`/start`）
2. 在浏览器中访问：
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   将 `<YOUR_BOT_TOKEN>` 替换为你的实际Token

3. 在返回的JSON中找到 `"chat":{"id":123456789}` 字段
4. 记录这个数字，这就是你的Chat ID

### 2.2 方法二：使用Python脚本

创建文件 `get_chat_id.py`：

```python
import requests
import json

def get_chat_id(bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data['ok'] and data['result']:
            for update in data['result']:
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    chat_type = update['message']['chat']['type']
                    
                    if 'first_name' in update['message']['chat']:
                        name = update['message']['chat']['first_name']
                    else:
                        name = update['message']['chat']['title']
                    
                    print(f"Chat ID: {chat_id}")
                    print(f"Chat Type: {chat_type}")
                    print(f"Name: {name}")
                    print("-" * 30)
            
            return data['result'][-1]['message']['chat']['id']
        else:
            print("没有找到消息记录，请先向Bot发送消息")
            return None
            
    except Exception as e:
        print(f"获取Chat ID时出错: {e}")
        return None

if __name__ == "__main__":
    bot_token = input("请输入Bot Token: ")
    chat_id = get_chat_id(bot_token)
    
    if chat_id:
        print(f"\n✅ 你的Chat ID是: {chat_id}")
        print("请将此ID保存到配置文件中")
    else:
        print("❌ 获取Chat ID失败")
```

运行脚本：
```bash
python get_chat_id.py
```

## ⚙️ 第三步：配置系统

### 3.1 环境变量配置

创建 `.env` 文件：

```bash
# Telegram Bot配置
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
TELEGRAM_CHAT_ID=123456789

# 币安API配置
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# 其他配置...
```

### 3.2 配置文件设置

在 `enhanced_config.py` 中确认以下设置：

```python
# Telegram Bot 基础配置
TELEGRAM_ENABLED = True
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

# 静默时间配置（可选）
TELEGRAM_QUIET_HOURS = {
    'enabled': True,   # 启用静默时间
    'start': '22:00',  # 静默开始时间
    'end': '08:00',    # 静默结束时间
    'timezone': 'Asia/Shanghai'
}
```

## 🧪 第四步：测试Bot功能

### 4.1 基础连接测试

创建测试脚本 `test_telegram.py`：

```python
import os
from telegram_bot import TelegramBot, TelegramNotificationManager

def test_basic_connection():
    """测试基础连接"""
    print("🧪 测试Telegram Bot基础连接...")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or bot_token == "your_bot_token_here":
        print("❌ 请设置TELEGRAM_BOT_TOKEN环境变量")
        return False
    
    if not chat_id or chat_id == "your_chat_id_here":
        print("❌ 请设置TELEGRAM_CHAT_ID环境变量")
        return False
    
    # 创建Bot实例
    bot = TelegramBot(bot_token, chat_id)
    
    # 验证Bot
    if not bot.verify_bot():
        print("❌ Bot Token验证失败")
        return False
    
    print("✅ Bot Token验证成功")
    
    # 发送测试消息
    test_message = "🧪 **测试消息**\n\n这是一条测试消息，如果您收到此消息，说明Telegram Bot配置成功！"
    
    if bot.send_message(test_message):
        print("✅ 测试消息发送成功")
        return True
    else:
        print("❌ 测试消息发送失败")
        return False

def test_notification_features():
    """测试通知功能"""
    print("\n🧪 测试通知功能...")
    
    config = {
        'telegram': {
            'enabled': True,
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
            'notification_levels': ['trade', 'signal', 'alert', 'performance']
        }
    }
    
    manager = TelegramNotificationManager(config)
    
    # 测试交易通知
    trade_data = {
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'quantity': 0.001,
        'price': 50000.0,
        'value': 50.0,
        'commission': 0.05,
        'timestamp': '2024-01-01 12:00:00',
        'strategy': 'test_strategy',
        'signal_confidence': 0.85
    }
    
    if manager.send_trade_notification(trade_data):
        print("✅ 交易通知测试成功")
    else:
        print("❌ 交易通知测试失败")
    
    # 测试信号通知
    signal_data = {
        'symbol': 'BTCUSDT',
        'signal': 'BUY',
        'confidence': 0.75,
        'price': 50000.0,
        'timestamp': '2024-01-01 12:00:00',
        'reason': '技术指标显示买入信号',
        'indicators': {
            'rsi': 35.5,
            'macd': 0.0123,
            'sma_20': 49800.0,
            'sma_50': 49500.0
        }
    }
    
    if manager.send_signal_notification(signal_data):
        print("✅ 信号通知测试成功")
    else:
        print("❌ 信号通知测试失败")
    
    # 测试警报通知
    if manager.send_alert('测试警报', '这是一个测试警报消息', 'warning'):
        print("✅ 警报通知测试成功")
    else:
        print("❌ 警报通知测试失败")
    
    # 测试性能报告
    performance_data = {
        'total_return': 5.25,
        'sharpe_ratio': 1.45,
        'max_drawdown': 2.1,
        'win_rate': 68.5,
        'final_value': 105250.0,
        'cash_remaining': 25000.0,
        'total_trades': 45,
        'winning_trades': 31
    }
    
    if manager.send_performance_report(performance_data):
        print("✅ 性能报告测试成功")
    else:
        print("❌ 性能报告测试失败")

if __name__ == "__main__":
    print("Telegram Bot 功能测试")
    print("=" * 50)
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 基础连接测试
    if test_basic_connection():
        # 通知功能测试
        test_notification_features()
        print("\n🎉 所有测试完成！")
    else:
        print("\n❌ 基础连接测试失败，请检查配置")
```

运行测试：
```bash
python test_telegram.py
```

### 4.2 完整系统测试

```python
from enhanced_trading_system import EnhancedTradingSystem, TradingSystemConfig

def test_full_system():
    """测试完整系统"""
    print("🧪 测试完整交易系统...")
    
    # 创建配置
    config = TradingSystemConfig()
    
    # 验证配置
    validation = config.validate_config()
    if not validation['is_valid']:
        print("❌ 配置验证失败:")
        for error in validation['errors']:
            print(f"  - {error}")
        return False
    
    # 创建系统
    system = EnhancedTradingSystem(config)
    
    # 启动系统
    if system.start_system():
        print("✅ 系统启动成功")
        
        # 运行短时间测试
        try:
            system.run_strategy('BTCUSDT', duration_hours=0.1)  # 6分钟测试
        except KeyboardInterrupt:
            pass
        finally:
            system.stop_system()
        
        print("✅ 系统测试完成")
        return True
    else:
        print("❌ 系统启动失败")
        return False

if __name__ == "__main__":
    test_full_system()
```

## 🚀 第五步：生产环境部署

### 5.1 服务器环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和依赖
sudo apt install python3 python3-pip python3-venv git -y

# 创建项目目录
mkdir ~/trading_system
cd ~/trading_system

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 5.2 配置文件设置

创建生产环境配置文件 `production.env`：

```bash
# 生产环境配置
TRADING_MODE=live
USE_TESTNET=False

# Telegram配置
TELEGRAM_ENABLED=True
TELEGRAM_BOT_TOKEN=your_production_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 币安API配置
BINANCE_API_KEY=your_production_api_key
BINANCE_API_SECRET=your_production_api_secret

# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost:5432/trading_system

# 安全配置
SECRET_KEY=your_very_secure_secret_key
ADMIN_PASSWORD=your_secure_admin_password
```

### 5.3 创建系统服务

创建 `trading_system.service` 文件：

```ini
[Unit]
Description=Enhanced Trading System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/trading_system
Environment=PATH=/home/ubuntu/trading_system/venv/bin
EnvironmentFile=/home/ubuntu/trading_system/production.env
ExecStart=/home/ubuntu/trading_system/venv/bin/python enhanced_trading_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

安装和启动服务：

```bash
# 复制服务文件
sudo cp trading_system.service /etc/systemd/system/

# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable trading_system

# 启动服务
sudo systemctl start trading_system

# 查看状态
sudo systemctl status trading_system

# 查看日志
sudo journalctl -u trading_system -f
```

### 5.4 监控和维护

创建监控脚本 `monitor.py`：

```python
import subprocess
import time
import requests
import os
from datetime import datetime

def check_service_status():
    """检查服务状态"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'trading_system'], 
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except:
        return False

def send_alert(message):
    """发送警报"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token and chat_id:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': f"🚨 系统监控警报\n\n{message}\n\n时间: {datetime.now()}"
        }
        requests.post(url, json=data)

def main():
    """主监控循环"""
    while True:
        if not check_service_status():
            send_alert("交易系统服务已停止，正在尝试重启...")
            
            # 尝试重启服务
            subprocess.run(['sudo', 'systemctl', 'restart', 'trading_system'])
            time.sleep(30)
            
            if check_service_status():
                send_alert("交易系统服务重启成功")
            else:
                send_alert("交易系统服务重启失败，需要人工干预")
        
        time.sleep(300)  # 每5分钟检查一次

if __name__ == "__main__":
    main()
```

## 📱 第六步：Bot命令处理（可选）

为了让Bot更智能，可以添加命令处理功能：

```python
import telebot
from telebot import types

class TradingBotHandler:
    def __init__(self, bot_token, trading_system):
        self.bot = telebot.TeleBot(bot_token)
        self.trading_system = trading_system
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start_command(message):
            welcome_text = """
🤖 欢迎使用量化交易助手！

可用命令：
/status - 查看系统状态
/report - 获取性能报告
/settings - 通知设置
/help - 帮助信息

系统正在为您监控市场...
            """
            self.bot.reply_to(message, welcome_text)
        
        @self.bot.message_handler(commands=['status'])
        def status_command(message):
            status = self.trading_system.get_system_status()
            self.bot.reply_to(message, f"📊 系统状态：{status}")
        
        @self.bot.message_handler(commands=['report'])
        def report_command(message):
            report = self.trading_system.generate_performance_report()
            self.bot.reply_to(message, f"📈 性能报告：{report}")
    
    def start_polling(self):
        self.bot.polling(none_stop=True)
```

## 🔧 故障排除

### 常见问题及解决方案

1. **Bot Token无效**
   - 检查Token是否正确复制
   - 确认Bot是否被BotFather正确创建

2. **Chat ID获取失败**
   - 确保已向Bot发送过消息
   - 检查Bot的隐私设置

3. **消息发送失败**
   - 检查网络连接
   - 确认Bot没有被用户屏蔽
   - 验证Chat ID是否正确

4. **服务启动失败**
   - 检查配置文件语法
   - 确认所有依赖已安装
   - 查看系统日志

### 调试命令

```bash
# 查看服务状态
sudo systemctl status trading_system

# 查看实时日志
sudo journalctl -u trading_system -f

# 重启服务
sudo systemctl restart trading_system

# 手动运行（调试模式）
cd ~/trading_system
source venv/bin/activate
python enhanced_trading_system.py
```

## 📋 检查清单

部署完成后，请确认以下项目：

- [ ] Bot Token已正确配置
- [ ] Chat ID已正确获取
- [ ] 基础连接测试通过
- [ ] 通知功能测试通过
- [ ] 系统服务正常运行
- [ ] 监控脚本已部署
- [ ] 日志记录正常
- [ ] 错误处理机制有效

## 🎉 完成

恭喜！您已成功部署了带有Telegram Bot通知功能的量化交易系统。系统将自动发送以下类型的通知：

- 🔄 交易执行通知
- 📊 交易信号提醒
- ⚠️ 风险警报
- 📈 性能报告
- 🚨 系统状态警报

享受您的智能交易助手吧！

