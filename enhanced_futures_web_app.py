"""
增强版合约量化交易Web应用

集成了合约交易策略、Telegram通知、实时监控等功能
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import threading
import time
import logging
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# 导入我们的策略模块
import sys
sys.path.append('/home/ubuntu')
sys.path.append('/home/ubuntu/contracts/strategies')
from futures_strategies import (
    StrategyManager, GridTradingStrategy, MomentumStrategy, 
    DualMAStrategy, RSIMeanReversionStrategy, generate_sample_futures_data
)
from simplified_strategy_analysis import ContractStrategyAnalyzer

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量
strategy_manager = StrategyManager()
current_data = None
strategy_results = {}
is_running = False

def initialize_strategies():
    """初始化策略"""
    global strategy_manager
    
    # 清空现有策略
    strategy_manager = StrategyManager()
    
    # 添加各种合约策略
    strategy_manager.add_strategy("网格交易", GridTradingStrategy("BTCUSDT", leverage=2, grid_spacing=0.015))
    strategy_manager.add_strategy("动量策略", MomentumStrategy("BTCUSDT", leverage=3, threshold=0.015))
    strategy_manager.add_strategy("双均线", DualMAStrategy("BTCUSDT", leverage=2, fast_period=8, slow_period=21))
    strategy_manager.add_strategy("RSI均值回归", RSIMeanReversionStrategy("BTCUSDT", leverage=2, oversold=25, overbought=75))

def generate_market_data():
    """生成市场数据"""
    global current_data
    current_data = generate_sample_futures_data(days=400, initial_price=50000)
    return current_data

@app.route('/')
def index():
    """主页"""
    return render_template('futures_index.html')

@app.route('/api/strategies')
def get_strategies():
    """获取策略列表"""
    strategies = list(strategy_manager.strategies.keys())
    return jsonify({'strategies': strategies})

@app.route('/api/run_backtest', methods=['POST'])
def run_backtest():
    """运行回测"""
    global strategy_results, current_data
    
    try:
        # 获取参数
        data = request.get_json()
        selected_strategies = data.get('strategies', [])
        
        if not current_data is None:
            current_data = generate_market_data()
        
        # 运行选定的策略
        if selected_strategies:
            # 创建临时策略管理器
            temp_manager = StrategyManager()
            for strategy_name in selected_strategies:
                if strategy_name in strategy_manager.strategies:
                    # 创建策略的新实例
                    original_strategy = strategy_manager.strategies[strategy_name]
                    if strategy_name == "网格交易":
                        new_strategy = GridTradingStrategy("BTCUSDT", leverage=2, grid_spacing=0.015)
                    elif strategy_name == "动量策略":
                        new_strategy = MomentumStrategy("BTCUSDT", leverage=3, threshold=0.015)
                    elif strategy_name == "双均线":
                        new_strategy = DualMAStrategy("BTCUSDT", leverage=2, fast_period=8, slow_period=21)
                    elif strategy_name == "RSI均值回归":
                        new_strategy = RSIMeanReversionStrategy("BTCUSDT", leverage=2, oversold=25, overbought=75)
                    
                    temp_manager.add_strategy(strategy_name, new_strategy)
            
            strategy_results = temp_manager.run_all_strategies(current_data)
        else:
            strategy_results = strategy_manager.run_all_strategies(current_data)
        
        # 生成比较表
        comparison_df = strategy_manager.compare_strategies(strategy_results)
        
        return jsonify({
            'success': True,
            'results': strategy_results,
            'comparison': comparison_df.to_dict('records'),
            'data_points': len(current_data)
        })
        
    except Exception as e:
        logger.error(f"回测运行失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/market_data')
def get_market_data():
    """获取市场数据"""
    global current_data
    
    if current_data is None:
        current_data = generate_market_data()
    
    # 转换为前端需要的格式
    data_dict = {
        'dates': current_data.index.strftime('%Y-%m-%d').tolist(),
        'prices': current_data['close'].tolist(),
        'volumes': current_data['volume'].tolist(),
        'highs': current_data['high'].tolist(),
        'lows': current_data['low'].tolist()
    }
    
    return jsonify(data_dict)

@app.route('/api/strategy_details/<strategy_name>')
def get_strategy_details(strategy_name):
    """获取策略详细信息"""
    if strategy_name not in strategy_results:
        return jsonify({'error': 'Strategy not found'})
    
    result = strategy_results[strategy_name]
    
    # 获取策略实例以获取更多信息
    strategy = strategy_manager.strategies.get(strategy_name)
    if strategy:
        equity_curve = strategy.equity_curve
        trades = [
            {
                'timestamp': trade.timestamp.isoformat(),
                'side': trade.side,
                'quantity': trade.quantity,
                'price': trade.price,
                'commission': trade.commission,
                'realized_pnl': trade.realized_pnl
            }
            for trade in strategy.trades
        ]
        
        positions = [
            {
                'symbol': pos.symbol,
                'side': pos.side,
                'size': pos.size,
                'entry_price': pos.entry_price,
                'unrealized_pnl': pos.unrealized_pnl,
                'realized_pnl': pos.realized_pnl
            }
            for pos in strategy.positions.values()
        ]
    else:
        equity_curve = []
        trades = []
        positions = []
    
    return jsonify({
        'metrics': result,
        'equity_curve': equity_curve,
        'trades': trades,
        'positions': positions
    })

@app.route('/api/generate_chart/<chart_type>')
def generate_chart(chart_type):
    """生成图表"""
    try:
        plt.style.use('seaborn-v0_8')
        fig, ax = plt.subplots(figsize=(12, 8))
        
        if chart_type == 'equity_curves':
            # 权益曲线对比
            for name, strategy in strategy_manager.strategies.items():
                if hasattr(strategy, 'equity_curve') and strategy.equity_curve:
                    ax.plot(strategy.equity_curve, label=name, linewidth=2)
            
            ax.set_title('策略权益曲线对比', fontsize=16, fontweight='bold')
            ax.set_xlabel('时间')
            ax.set_ylabel('权益价值')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
        elif chart_type == 'returns_distribution':
            # 收益分布
            for name, strategy in strategy_manager.strategies.items():
                if hasattr(strategy, 'equity_curve') and len(strategy.equity_curve) > 1:
                    equity_series = pd.Series(strategy.equity_curve)
                    returns = equity_series.pct_change().dropna()
                    ax.hist(returns, bins=30, alpha=0.6, label=name)
            
            ax.set_title('策略收益分布', fontsize=16, fontweight='bold')
            ax.set_xlabel('日收益率')
            ax.set_ylabel('频次')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
        elif chart_type == 'drawdown':
            # 回撤分析
            for name, strategy in strategy_manager.strategies.items():
                if hasattr(strategy, 'equity_curve') and len(strategy.equity_curve) > 1:
                    equity_series = pd.Series(strategy.equity_curve)
                    peak = equity_series.expanding().max()
                    drawdown = (equity_series - peak) / peak * 100
                    ax.fill_between(range(len(drawdown)), drawdown, 0, alpha=0.3, label=name)
            
            ax.set_title('策略回撤分析', fontsize=16, fontweight='bold')
            ax.set_xlabel('时间')
            ax.set_ylabel('回撤 (%)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
        elif chart_type == 'performance_metrics':
            # 性能指标雷达图
            if strategy_results:
                metrics = ['total_return', 'sharpe_ratio', 'win_rate']
                strategies = list(strategy_results.keys())
                
                # 标准化指标
                data = []
                for strategy in strategies:
                    result = strategy_results[strategy]
                    data.append([
                        result.get('total_return', 0) / 100,  # 标准化到0-1
                        (result.get('sharpe_ratio', 0) + 2) / 4,  # 假设夏普比率范围-2到2
                        result.get('win_rate', 0) / 100
                    ])
                
                # 创建雷达图
                angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False)
                angles = np.concatenate((angles, [angles[0]]))
                
                ax = plt.subplot(111, projection='polar')
                
                for i, strategy in enumerate(strategies):
                    values = data[i] + [data[i][0]]  # 闭合图形
                    ax.plot(angles, values, 'o-', linewidth=2, label=strategy)
                    ax.fill(angles, values, alpha=0.25)
                
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(['总收益率', '夏普比率', '胜率'])
                ax.set_ylim(0, 1)
                ax.legend()
                ax.set_title('策略性能雷达图', fontsize=16, fontweight='bold', pad=20)
        
        # 保存图表到内存
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        
        # 编码为base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        plt.close()
        
        return jsonify({
            'success': True,
            'image': f"data:image/png;base64,{img_base64}"
        })
        
    except Exception as e:
        logger.error(f"图表生成失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/optimize_strategy', methods=['POST'])
def optimize_strategy():
    """优化策略参数"""
    try:
        data = request.get_json()
        strategy_name = data.get('strategy_name')
        
        if not current_data is not None:
            return jsonify({'success': False, 'error': '没有市场数据'})
        
        # 使用简化的优化方法
        analyzer = ContractStrategyAnalyzer(current_data)
        
        if strategy_name == "双均线":
            # 优化双均线参数
            best_params = None
            best_sharpe = -np.inf
            
            for fast in range(5, 15):
                for slow in range(15, 30):
                    if fast >= slow:
                        continue
                    
                    result = analyzer.dual_ma_crossover_strategy(fast, slow, leverage=2)
                    metrics = analyzer.calculate_performance_metrics(result['strategy_returns'])
                    
                    if metrics['sharpe_ratio'] > best_sharpe:
                        best_sharpe = metrics['sharpe_ratio']
                        best_params = {'fast_period': fast, 'slow_period': slow}
            
            return jsonify({
                'success': True,
                'best_params': best_params,
                'best_sharpe': best_sharpe
            })
        
        elif strategy_name == "RSI均值回归":
            # 优化RSI参数
            best_params = None
            best_sharpe = -np.inf
            
            for oversold in range(20, 35, 5):
                for overbought in range(65, 80, 5):
                    result = analyzer.rsi_mean_reversion_strategy(oversold=oversold, overbought=overbought, leverage=2)
                    metrics = analyzer.calculate_performance_metrics(result['strategy_returns'])
                    
                    if metrics['sharpe_ratio'] > best_sharpe:
                        best_sharpe = metrics['sharpe_ratio']
                        best_params = {'oversold': oversold, 'overbought': overbought}
            
            return jsonify({
                'success': True,
                'best_params': best_params,
                'best_sharpe': best_sharpe
            })
        
        else:
            return jsonify({'success': False, 'error': '不支持的策略类型'})
            
    except Exception as e:
        logger.error(f"策略优化失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/risk_analysis')
def risk_analysis():
    """风险分析"""
    try:
        if not strategy_results:
            return jsonify({'error': '没有策略结果'})
        
        risk_metrics = {}
        
        for name, strategy in strategy_manager.strategies.items():
            if hasattr(strategy, 'equity_curve') and len(strategy.equity_curve) > 1:
                equity_series = pd.Series(strategy.equity_curve)
                returns = equity_series.pct_change().dropna()
                
                # VaR计算
                var_95 = np.percentile(returns, 5) * 100
                var_99 = np.percentile(returns, 1) * 100
                
                # CVaR计算
                cvar_95 = returns[returns <= np.percentile(returns, 5)].mean() * 100
                cvar_99 = returns[returns <= np.percentile(returns, 1)].mean() * 100
                
                # 最大连续亏损
                losses = (returns < 0).astype(int)
                max_consecutive_losses = 0
                current_losses = 0
                
                for loss in losses:
                    if loss:
                        current_losses += 1
                        max_consecutive_losses = max(max_consecutive_losses, current_losses)
                    else:
                        current_losses = 0
                
                risk_metrics[name] = {
                    'var_95': var_95,
                    'var_99': var_99,
                    'cvar_95': cvar_95,
                    'cvar_99': cvar_99,
                    'max_consecutive_losses': max_consecutive_losses,
                    'volatility': returns.std() * np.sqrt(252) * 100
                }
        
        return jsonify({'success': True, 'risk_metrics': risk_metrics})
        
    except Exception as e:
        logger.error(f"风险分析失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export_results')
def export_results():
    """导出结果"""
    try:
        if not strategy_results:
            return jsonify({'error': '没有策略结果'})
        
        # 创建Excel文件
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 策略比较表
            comparison_df = strategy_manager.compare_strategies(strategy_results)
            comparison_df.to_excel(writer, sheet_name='策略比较', index=False)
            
            # 详细结果
            for name, result in strategy_results.items():
                result_df = pd.DataFrame([result])
                result_df.to_excel(writer, sheet_name=f'{name}_详细', index=False)
            
            # 市场数据
            if current_data is not None:
                current_data.to_excel(writer, sheet_name='市场数据')
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'futures_strategy_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
    except Exception as e:
        logger.error(f"导出失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

# 创建模板文件
def create_templates():
    """创建HTML模板"""
    template_dir = 'templates'
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    html_content = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>合约量化交易系统</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .strategy-card {
            transition: transform 0.2s;
            border-left: 4px solid #007bff;
        }
        .strategy-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .metric-positive { color: #28a745; }
        .metric-negative { color: #dc3545; }
        .loading-spinner {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
        }
        .nav-tabs .nav-link.active {
            background-color: #007bff;
            color: white;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-chart-line"></i> 合约量化交易系统
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="#" onclick="exportResults()">
                    <i class="fas fa-download"></i> 导出结果
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- 控制面板 -->
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-cogs"></i> 控制面板</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <label class="form-label">选择策略:</label>
                                <div id="strategySelection">
                                    <!-- 策略选择将在这里动态加载 -->
                                </div>
                            </div>
                            <div class="col-md-6 d-flex align-items-end">
                                <button class="btn btn-primary me-2" onclick="runBacktest()">
                                    <i class="fas fa-play"></i> 运行回测
                                </button>
                                <button class="btn btn-info me-2" onclick="generateNewData()">
                                    <i class="fas fa-refresh"></i> 生成新数据
                                </button>
                                <button class="btn btn-warning" onclick="optimizeStrategies()">
                                    <i class="fas fa-magic"></i> 参数优化
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 加载指示器 -->
        <div id="loadingSpinner" class="loading-spinner">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            <p class="mt-2">正在运行回测，请稍候...</p>
        </div>

        <!-- 结果展示 -->
        <div id="resultsContainer" style="display: none;">
            <!-- 策略比较表 -->
            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-table"></i> 策略性能比较</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table id="comparisonTable" class="table table-striped table-hover">
                                    <!-- 表格内容将动态加载 -->
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 图表展示 -->
            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <ul class="nav nav-tabs card-header-tabs" id="chartTabs">
                                <li class="nav-item">
                                    <a class="nav-link active" href="#" onclick="showChart('equity_curves')">权益曲线</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="#" onclick="showChart('returns_distribution')">收益分布</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="#" onclick="showChart('drawdown')">回撤分析</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="#" onclick="showChart('performance_metrics')">性能雷达图</a>
                                </li>
                            </ul>
                        </div>
                        <div class="card-body">
                            <div id="chartContainer" class="chart-container">
                                <!-- 图表将在这里显示 -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 风险分析 -->
            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-shield-alt"></i> 风险分析</h5>
                        </div>
                        <div class="card-body">
                            <div id="riskAnalysis">
                                <!-- 风险分析结果将在这里显示 -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentResults = {};

        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadStrategies();
        });

        // 加载策略列表
        async function loadStrategies() {
            try {
                const response = await fetch('/api/strategies');
                const data = await response.json();
                
                const container = document.getElementById('strategySelection');
                container.innerHTML = '';
                
                data.strategies.forEach(strategy => {
                    const div = document.createElement('div');
                    div.className = 'form-check';
                    div.innerHTML = `
                        <input class="form-check-input" type="checkbox" value="${strategy}" id="strategy_${strategy}" checked>
                        <label class="form-check-label" for="strategy_${strategy}">
                            ${strategy}
                        </label>
                    `;
                    container.appendChild(div);
                });
            } catch (error) {
                console.error('加载策略失败:', error);
            }
        }

        // 运行回测
        async function runBacktest() {
            const selectedStrategies = Array.from(document.querySelectorAll('#strategySelection input:checked'))
                .map(input => input.value);
            
            if (selectedStrategies.length === 0) {
                alert('请至少选择一个策略');
                return;
            }

            document.getElementById('loadingSpinner').style.display = 'block';
            document.getElementById('resultsContainer').style.display = 'none';

            try {
                const response = await fetch('/api/run_backtest', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        strategies: selectedStrategies
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    currentResults = data.results;
                    displayResults(data);
                    loadRiskAnalysis();
                } else {
                    alert('回测失败: ' + data.error);
                }
            } catch (error) {
                console.error('回测失败:', error);
                alert('回测失败: ' + error.message);
            } finally {
                document.getElementById('loadingSpinner').style.display = 'none';
            }
        }

        // 显示结果
        function displayResults(data) {
            // 显示比较表
            displayComparisonTable(data.comparison);
            
            // 显示图表
            showChart('equity_curves');
            
            // 显示结果容器
            document.getElementById('resultsContainer').style.display = 'block';
        }

        // 显示比较表
        function displayComparisonTable(comparison) {
            const table = document.getElementById('comparisonTable');
            
            if (comparison.length === 0) {
                table.innerHTML = '<tr><td>没有数据</td></tr>';
                return;
            }

            // 创建表头
            const headers = Object.keys(comparison[0]);
            let headerHtml = '<thead><tr>';
            headers.forEach(header => {
                headerHtml += `<th>${header}</th>`;
            });
            headerHtml += '</tr></thead>';

            // 创建表体
            let bodyHtml = '<tbody>';
            comparison.forEach(row => {
                bodyHtml += '<tr>';
                headers.forEach(header => {
                    let value = row[header];
                    let className = '';
                    
                    // 为数值添加颜色
                    if (typeof value === 'number') {
                        if (header.includes('Return') || header.includes('Ratio')) {
                            className = value > 0 ? 'metric-positive' : 'metric-negative';
                        }
                        value = value.toFixed(3);
                    }
                    
                    bodyHtml += `<td class="${className}">${value}</td>`;
                });
                bodyHtml += '</tr>';
            });
            bodyHtml += '</tbody>';

            table.innerHTML = headerHtml + bodyHtml;
        }

        // 显示图表
        async function showChart(chartType) {
            // 更新标签页状态
            document.querySelectorAll('#chartTabs .nav-link').forEach(link => {
                link.classList.remove('active');
            });
            event.target.classList.add('active');

            try {
                const response = await fetch(`/api/generate_chart/${chartType}`);
                const data = await response.json();
                
                if (data.success) {
                    const container = document.getElementById('chartContainer');
                    container.innerHTML = `<img src="${data.image}" class="img-fluid" alt="${chartType}">`;
                } else {
                    console.error('图表生成失败:', data.error);
                }
            } catch (error) {
                console.error('图表加载失败:', error);
            }
        }

        // 加载风险分析
        async function loadRiskAnalysis() {
            try {
                const response = await fetch('/api/risk_analysis');
                const data = await response.json();
                
                if (data.success) {
                    displayRiskAnalysis(data.risk_metrics);
                }
            } catch (error) {
                console.error('风险分析加载失败:', error);
            }
        }

        // 显示风险分析
        function displayRiskAnalysis(riskMetrics) {
            const container = document.getElementById('riskAnalysis');
            let html = '<div class="row">';
            
            Object.entries(riskMetrics).forEach(([strategy, metrics]) => {
                html += `
                    <div class="col-md-6 mb-3">
                        <div class="card strategy-card">
                            <div class="card-header">
                                <h6>${strategy} 风险指标</h6>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-6">
                                        <small class="text-muted">95% VaR</small><br>
                                        <span class="metric-negative">${metrics.var_95.toFixed(2)}%</span>
                                    </div>
                                    <div class="col-6">
                                        <small class="text-muted">99% VaR</small><br>
                                        <span class="metric-negative">${metrics.var_99.toFixed(2)}%</span>
                                    </div>
                                    <div class="col-6">
                                        <small class="text-muted">95% CVaR</small><br>
                                        <span class="metric-negative">${metrics.cvar_95.toFixed(2)}%</span>
                                    </div>
                                    <div class="col-6">
                                        <small class="text-muted">波动率</small><br>
                                        <span>${metrics.volatility.toFixed(2)}%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
        }

        // 生成新数据
        async function generateNewData() {
            try {
                const response = await fetch('/api/market_data');
                const data = await response.json();
                alert(`已生成新的市场数据，共 ${data.dates.length} 个数据点`);
            } catch (error) {
                console.error('生成数据失败:', error);
            }
        }

        // 优化策略
        async function optimizeStrategies() {
            alert('参数优化功能开发中...');
        }

        // 导出结果
        function exportResults() {
            if (Object.keys(currentResults).length === 0) {
                alert('请先运行回测');
                return;
            }
            
            window.open('/api/export_results', '_blank');
        }
    </script>
</body>
</html>
    '''
    
    with open(os.path.join(template_dir, 'futures_index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    # 创建模板文件
    create_templates()
    
    # 初始化策略
    initialize_strategies()
    
    # 生成初始数据
    generate_market_data()
    
    print("合约量化交易Web应用启动中...")
    print("访问地址: http://127.0.0.1:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

