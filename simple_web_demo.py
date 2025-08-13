#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Web界面演示
展示量化交易系统的Web功能
"""

try:
    from flask import Flask, render_template_string, jsonify
except ImportError:
    print("Flask未安装，请运行: pip install flask")
    exit(1)

import json
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>合约量化交易系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            background: #f8f9ff;
            border-radius: 8px;
        }
        
        .metric-label {
            font-weight: 600;
            color: #555;
        }
        
        .metric-value {
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .positive {
            color: #27ae60;
        }
        
        .negative {
            color: #e74c3c;
        }
        
        .neutral {
            color: #3498db;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-online {
            background: #27ae60;
            animation: pulse 2s infinite;
        }
        
        .status-offline {
            background: #e74c3c;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .trades-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .trades-table th,
        .trades-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        .trades-table th {
            background: #667eea;
            color: white;
            font-weight: 600;
        }
        
        .trades-table tr:hover {
            background: #f8f9ff;
        }
        
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.3s ease;
            margin: 5px;
        }
        
        .btn:hover {
            background: #5a67d8;
        }
        
        .btn-success {
            background: #27ae60;
        }
        
        .btn-success:hover {
            background: #219a52;
        }
        
        .btn-danger {
            background: #e74c3c;
        }
        
        .btn-danger:hover {
            background: #c0392b;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 合约量化交易系统</h1>
            <p>智能交易 · 风险控制 · 收益最大化</p>
        </div>
        
        <div class="dashboard">
            <!-- 系统状态卡片 -->
            <div class="card">
                <h3>📊 系统状态</h3>
                <div class="metric">
                    <span class="metric-label">
                        <span class="status-indicator status-online"></span>
                        交易引擎
                    </span>
                    <span class="metric-value positive">运行中</span>
                </div>
                <div class="metric">
                    <span class="metric-label">
                        <span class="status-indicator status-online"></span>
                        数据连接
                    </span>
                    <span class="metric-value positive">正常</span>
                </div>
                <div class="metric">
                    <span class="metric-label">
                        <span class="status-indicator status-offline"></span>
                        Telegram通知
                    </span>
                    <span class="metric-value negative">未配置</span>
                </div>
                <div class="metric">
                    <span class="metric-label">运行时间</span>
                    <span class="metric-value neutral" id="uptime">00:05:23</span>
                </div>
            </div>
            
            <!-- 账户信息卡片 -->
            <div class="card">
                <h3>💰 账户信息</h3>
                <div class="metric">
                    <span class="metric-label">总资产</span>
                    <span class="metric-value positive">$102,350.75</span>
                </div>
                <div class="metric">
                    <span class="metric-label">可用余额</span>
                    <span class="metric-value neutral">$98,450.25</span>
                </div>
                <div class="metric">
                    <span class="metric-label">持仓价值</span>
                    <span class="metric-value neutral">$3,900.50</span>
                </div>
                <div class="metric">
                    <span class="metric-label">今日盈亏</span>
                    <span class="metric-value positive">+$1,250.75 (+1.24%)</span>
                </div>
            </div>
            
            <!-- 交易统计卡片 -->
            <div class="card">
                <h3>📈 交易统计</h3>
                <div class="metric">
                    <span class="metric-label">总收益率</span>
                    <span class="metric-value positive">+2.35%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">胜率</span>
                    <span class="metric-value positive">68.5%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">总交易次数</span>
                    <span class="metric-value neutral">147</span>
                </div>
                <div class="metric">
                    <span class="metric-label">最大回撤</span>
                    <span class="metric-value negative">-3.2%</span>
                </div>
            </div>
            
            <!-- 当前持仓卡片 -->
            <div class="card">
                <h3>📊 当前持仓</h3>
                <div class="metric">
                    <span class="metric-label">BTC/USDT</span>
                    <span class="metric-value positive">0.0785 BTC</span>
                </div>
                <div class="metric">
                    <span class="metric-label">入场价格</span>
                    <span class="metric-value neutral">$49,650.00</span>
                </div>
                <div class="metric">
                    <span class="metric-label">当前价格</span>
                    <span class="metric-value positive">$50,125.50</span>
                </div>
                <div class="metric">
                    <span class="metric-label">浮动盈亏</span>
                    <span class="metric-value positive">+$37.31 (+0.96%)</span>
                </div>
            </div>
        </div>
        
        <!-- 最近交易记录 -->
        <div class="card">
            <h3>📋 最近交易记录</h3>
            <table class="trades-table">
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>交易对</th>
                        <th>类型</th>
                        <th>数量</th>
                        <th>价格</th>
                        <th>盈亏</th>
                        <th>状态</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>14:32:15</td>
                        <td>BTC/USDT</td>
                        <td><span class="positive">买入</span></td>
                        <td>0.0125</td>
                        <td>$50,100.00</td>
                        <td><span class="positive">+$15.25</span></td>
                        <td><span class="positive">已成交</span></td>
                    </tr>
                    <tr>
                        <td>13:45:22</td>
                        <td>ETH/USDT</td>
                        <td><span class="negative">卖出</span></td>
                        <td>0.5</td>
                        <td>$3,125.50</td>
                        <td><span class="positive">+$25.75</span></td>
                        <td><span class="positive">已成交</span></td>
                    </tr>
                    <tr>
                        <td>12:18:45</td>
                        <td>BTC/USDT</td>
                        <td><span class="negative">卖出</span></td>
                        <td>0.02</td>
                        <td>$49,850.00</td>
                        <td><span class="negative">-$12.50</span></td>
                        <td><span class="positive">已成交</span></td>
                    </tr>
                    <tr>
                        <td>11:55:33</td>
                        <td>ETH/USDT</td>
                        <td><span class="positive">买入</span></td>
                        <td>0.8</td>
                        <td>$3,098.25</td>
                        <td><span class="positive">+$42.80</span></td>
                        <td><span class="positive">已成交</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- 控制面板 -->
        <div class="card">
            <h3>🎛️ 控制面板</h3>
            <div style="text-align: center;">
                <button class="btn btn-success" onclick="startTrading()">▶️ 启动交易</button>
                <button class="btn btn-danger" onclick="stopTrading()">⏸️ 停止交易</button>
                <button class="btn" onclick="refreshData()">🔄 刷新数据</button>
                <button class="btn" onclick="exportReport()">📊 导出报告</button>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2024 合约量化交易系统 | 版本 1.0 | 最后更新: {{ current_time }}</p>
        </div>
    </div>
    
    <script>
        // 模拟实时数据更新
        function updateUptime() {
            const uptimeElement = document.getElementById('uptime');
            let seconds = 323; // 起始秒数
            
            setInterval(() => {
                seconds++;
                const hours = Math.floor(seconds / 3600);
                const minutes = Math.floor((seconds % 3600) / 60);
                const secs = seconds % 60;
                
                uptimeElement.textContent = 
                    `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            }, 1000);
        }
        
        function startTrading() {
            alert('🚀 交易系统已启动！');
        }
        
        function stopTrading() {
            alert('⏸️ 交易系统已停止！');
        }
        
        function refreshData() {
            alert('🔄 数据刷新中...');
            setTimeout(() => {
                location.reload();
            }, 1000);
        }
        
        function exportReport() {
            alert('📊 报告导出功能开发中...');
        }
        
        // 页面加载完成后启动计时器
        document.addEventListener('DOMContentLoaded', updateUptime);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """主页"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template_string(HTML_TEMPLATE, current_time=current_time)

@app.route('/api/status')
def api_status():
    """API状态接口"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'uptime': '00:05:23'
    })

@app.route('/api/account')
def api_account():
    """账户信息接口"""
    return jsonify({
        'total_balance': 102350.75,
        'available_balance': 98450.25,
        'position_value': 3900.50,
        'daily_pnl': 1250.75,
        'daily_pnl_pct': 1.24
    })

@app.route('/api/trades')
def api_trades():
    """交易记录接口"""
    trades = [
        {
            'time': '14:32:15',
            'symbol': 'BTC/USDT',
            'side': 'BUY',
            'quantity': 0.0125,
            'price': 50100.00,
            'pnl': 15.25,
            'status': 'FILLED'
        },
        {
            'time': '13:45:22',
            'symbol': 'ETH/USDT',
            'side': 'SELL',
            'quantity': 0.5,
            'price': 3125.50,
            'pnl': 25.75,
            'status': 'FILLED'
        }
    ]
    return jsonify(trades)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 启动合约量化交易系统Web界面")
    print("="*60)
    print(f"🕐 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔗 访问地址: http://localhost:5000")
    print("📱 支持移动端访问")
    print("🎯 功能特性:")
    print("   ✅ 实时系统状态监控")
    print("   ✅ 账户资产展示")
    print("   ✅ 交易统计分析")
    print("   ✅ 持仓信息查看")
    print("   ✅ 交易记录管理")
    print("   ✅ 响应式设计")
    print("\n⚡ 按 Ctrl+C 停止服务器")
    print("="*60)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n⏹️ Web服务器已停止")
    except Exception as e:
        print(f"\n\n❌ Web服务器启动失败: {e}")
    finally:
        print("👋 感谢使用合约量化交易系统！")