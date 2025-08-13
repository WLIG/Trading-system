"""
增强版回测验证工具

提供更全面的策略回测验证功能，包括参数优化、风险分析、压力测试等
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class EnhancedBacktestValidator:
    """增强版回测验证器"""
    
    def __init__(self, initial_capital=100000):
        """
        初始化验证器
        
        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.results = {}
        
    def generate_multiple_market_scenarios(self, days=300):
        """
        生成多种市场情景数据
        
        Args:
            days: 天数
            
        Returns:
            dict: 包含不同市场情景的数据
        """
        scenarios = {}
        
        # 1. 牛市情景
        scenarios['bull_market'] = self._generate_trending_market(days, trend=0.001, volatility=0.02)
        
        # 2. 熊市情景
        scenarios['bear_market'] = self._generate_trending_market(days, trend=-0.001, volatility=0.025)
        
        # 3. 震荡市情景
        scenarios['sideways_market'] = self._generate_sideways_market(days, volatility=0.02)
        
        # 4. 高波动市情景
        scenarios['high_volatility'] = self._generate_trending_market(days, trend=0.0002, volatility=0.05)
        
        # 5. 低波动市情景
        scenarios['low_volatility'] = self._generate_trending_market(days, trend=0.0001, volatility=0.01)
        
        return scenarios
    
    def _generate_trending_market(self, days, trend=0.001, volatility=0.02, initial_price=50000):
        """生成趋势性市场数据"""
        np.random.seed(42)
        
        prices = [initial_price]
        for i in range(days - 1):
            # 趋势 + 随机波动
            return_rate = trend + np.random.normal(0, volatility)
            
            # 添加周期性波动
            cycle_effect = 0.0005 * np.sin(i / 20)
            return_rate += cycle_effect
            
            new_price = prices[-1] * (1 + return_rate)
            prices.append(max(new_price, 1000))
        
        return self._create_ohlcv_data(prices)
    
    def _generate_sideways_market(self, days, volatility=0.02, initial_price=50000):
        """生成震荡市场数据"""
        np.random.seed(42)
        
        prices = [initial_price]
        center_price = initial_price
        
        for i in range(days - 1):
            # 均值回归 + 随机波动
            mean_reversion = -0.001 * (prices[-1] - center_price) / center_price
            random_shock = np.random.normal(0, volatility)
            
            return_rate = mean_reversion + random_shock
            
            new_price = prices[-1] * (1 + return_rate)
            prices.append(max(new_price, 1000))
        
        return self._create_ohlcv_data(prices)
    
    def _create_ohlcv_data(self, prices):
        """创建OHLCV数据"""
        dates = pd.date_range(start='2023-01-01', periods=len(prices), freq='D')
        
        data = []
        for i, price in enumerate(prices):
            daily_vol = 0.015
            open_price = price * (1 + np.random.normal(0, daily_vol/3))
            high_price = max(open_price, price) * (1 + np.random.uniform(0, daily_vol))
            low_price = min(open_price, price) * (1 - np.random.uniform(0, daily_vol))
            volume = np.random.lognormal(15, 0.5)
            
            data.append({
                'date': dates[i],
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': price,
                'volume': volume
            })
        
        return pd.DataFrame(data).set_index('date')
    
    def parameter_optimization(self, strategy_class, data, param_ranges):
        """
        参数优化
        
        Args:
            strategy_class: 策略类
            data: 市场数据
            param_ranges: 参数范围字典
            
        Returns:
            最优参数和结果
        """
        best_params = None
        best_sharpe = -np.inf
        optimization_results = []
        
        # 生成参数组合
        param_combinations = self._generate_param_combinations(param_ranges)
        
        print(f"开始参数优化，共{len(param_combinations)}种组合...")
        
        for i, params in enumerate(param_combinations):
            try:
                # 创建策略实例
                strategy = strategy_class("BTCUSDT", **params)
                strategy.add_data(data)
                
                # 运行回测
                result = strategy.run_backtest()
                
                # 记录结果
                optimization_results.append({
                    'params': params,
                    'sharpe_ratio': result['sharpe_ratio'],
                    'total_return': result['total_return'],
                    'max_drawdown': result['max_drawdown'],
                    'win_rate': result['win_rate']
                })
                
                # 更新最佳参数
                if result['sharpe_ratio'] > best_sharpe:
                    best_sharpe = result['sharpe_ratio']
                    best_params = params
                
                if (i + 1) % 10 == 0:
                    print(f"已完成 {i + 1}/{len(param_combinations)} 组合")
                    
            except Exception as e:
                print(f"参数组合 {params} 测试失败: {e}")
                continue
        
        return best_params, best_sharpe, optimization_results
    
    def _generate_param_combinations(self, param_ranges):
        """生成参数组合"""
        import itertools
        
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        
        combinations = []
        for combo in itertools.product(*param_values):
            param_dict = dict(zip(param_names, combo))
            combinations.append(param_dict)
        
        return combinations
    
    def stress_test(self, strategy_class, scenarios, params=None):
        """
        压力测试
        
        Args:
            strategy_class: 策略类
            scenarios: 市场情景数据
            params: 策略参数
            
        Returns:
            压力测试结果
        """
        stress_results = {}
        
        for scenario_name, data in scenarios.items():
            print(f"正在进行 {scenario_name} 压力测试...")
            
            try:
                # 创建策略实例
                if params:
                    strategy = strategy_class("BTCUSDT", **params)
                else:
                    strategy = strategy_class("BTCUSDT")
                
                strategy.add_data(data)
                result = strategy.run_backtest()
                
                stress_results[scenario_name] = result
                
            except Exception as e:
                print(f"{scenario_name} 压力测试失败: {e}")
                stress_results[scenario_name] = None
        
        return stress_results
    
    def monte_carlo_simulation(self, strategy_class, base_data, num_simulations=100, params=None):
        """
        蒙特卡洛模拟
        
        Args:
            strategy_class: 策略类
            base_data: 基础数据
            num_simulations: 模拟次数
            params: 策略参数
            
        Returns:
            模拟结果
        """
        simulation_results = []
        
        print(f"开始蒙特卡洛模拟，共{num_simulations}次...")
        
        for i in range(num_simulations):
            # 生成随机数据
            randomized_data = self._randomize_data(base_data, seed=i)
            
            try:
                # 创建策略实例
                if params:
                    strategy = strategy_class("BTCUSDT", **params)
                else:
                    strategy = strategy_class("BTCUSDT")
                
                strategy.add_data(randomized_data)
                result = strategy.run_backtest()
                
                simulation_results.append(result)
                
                if (i + 1) % 20 == 0:
                    print(f"已完成 {i + 1}/{num_simulations} 次模拟")
                    
            except Exception as e:
                print(f"第{i+1}次模拟失败: {e}")
                continue
        
        return simulation_results
    
    def _randomize_data(self, data, seed=None):
        """随机化数据"""
        if seed:
            np.random.seed(seed)
        
        # 对收益率进行bootstrap重采样
        returns = data['close'].pct_change().dropna()
        
        # 重采样收益率
        resampled_returns = np.random.choice(returns, size=len(returns), replace=True)
        
        # 重构价格序列
        new_prices = [data['close'].iloc[0]]
        for ret in resampled_returns:
            new_price = new_prices[-1] * (1 + ret)
            new_prices.append(new_price)
        
        # 创建新的数据框
        new_data = data.copy()
        # 确保长度匹配
        if len(new_prices) > len(new_data):
            new_prices = new_prices[:len(new_data)]
        elif len(new_prices) < len(new_data):
            # 如果价格序列太短，用最后一个价格填充
            last_price = new_prices[-1]
            while len(new_prices) < len(new_data):
                new_prices.append(last_price)
        
        new_data['close'] = new_prices
        
        # 重新计算OHLV
        for i in range(len(new_data)):
            close_price = new_data.iloc[i]['close']
            daily_vol = 0.015
            
            open_price = close_price * (1 + np.random.normal(0, daily_vol/3))
            high_price = max(open_price, close_price) * (1 + np.random.uniform(0, daily_vol))
            low_price = min(open_price, close_price) * (1 - np.random.uniform(0, daily_vol))
            
            new_data.iloc[i, new_data.columns.get_loc('open')] = open_price
            new_data.iloc[i, new_data.columns.get_loc('high')] = high_price
            new_data.iloc[i, new_data.columns.get_loc('low')] = low_price
        
        return new_data
    
    def walk_forward_analysis(self, strategy_class, data, window_size=60, step_size=20, params=None):
        """
        滚动窗口分析
        
        Args:
            strategy_class: 策略类
            data: 市场数据
            window_size: 窗口大小
            step_size: 步长
            params: 策略参数
            
        Returns:
            滚动分析结果
        """
        walk_forward_results = []
        
        for start_idx in range(0, len(data) - window_size, step_size):
            end_idx = start_idx + window_size
            window_data = data.iloc[start_idx:end_idx]
            
            try:
                # 创建策略实例
                if params:
                    strategy = strategy_class("BTCUSDT", **params)
                else:
                    strategy = strategy_class("BTCUSDT")
                
                strategy.add_data(window_data)
                result = strategy.run_backtest()
                
                result['start_date'] = window_data.index[0]
                result['end_date'] = window_data.index[-1]
                
                walk_forward_results.append(result)
                
            except Exception as e:
                print(f"滚动窗口 {start_idx}-{end_idx} 分析失败: {e}")
                continue
        
        return walk_forward_results
    
    def generate_comprehensive_report(self, strategy_name, optimization_results, 
                                    stress_results, monte_carlo_results, walk_forward_results):
        """
        生成综合报告
        
        Args:
            strategy_name: 策略名称
            optimization_results: 优化结果
            stress_results: 压力测试结果
            monte_carlo_results: 蒙特卡洛结果
            walk_forward_results: 滚动分析结果
            
        Returns:
            综合报告
        """
        report = f"""
# {strategy_name} 策略综合验证报告

## 1. 参数优化结果

### 最优参数组合
"""
        
        if optimization_results:
            best_params, best_sharpe, all_results = optimization_results
            report += f"""
- 最佳夏普比率: {best_sharpe:.3f}
- 最优参数: {best_params}

### 参数敏感性分析
- 共测试了 {len(all_results)} 种参数组合
- 夏普比率范围: {min(r['sharpe_ratio'] for r in all_results):.3f} ~ {max(r['sharpe_ratio'] for r in all_results):.3f}
"""
        
        report += """
## 2. 压力测试结果

不同市场环境下的策略表现:
"""
        
        if stress_results:
            for scenario, result in stress_results.items():
                if result:
                    report += f"""
### {scenario}
- 总收益率: {result['total_return']:.2f}%
- 夏普比率: {result['sharpe_ratio']:.3f}
- 最大回撤: {result['max_drawdown']:.2f}%
- 胜率: {result['win_rate']:.2f}%
"""
        
        report += """
## 3. 蒙特卡洛模拟结果
"""
        
        if monte_carlo_results:
            returns = [r['total_return'] for r in monte_carlo_results if r['total_return'] is not None]
            sharpes = [r['sharpe_ratio'] for r in monte_carlo_results if r['sharpe_ratio'] is not None]
            
            if returns and sharpes:
                report += f"""
- 模拟次数: {len(monte_carlo_results)}
- 平均收益率: {np.mean(returns):.2f}%
- 收益率标准差: {np.std(returns):.2f}%
- 收益率95%置信区间: [{np.percentile(returns, 2.5):.2f}%, {np.percentile(returns, 97.5):.2f}%]
- 平均夏普比率: {np.mean(sharpes):.3f}
- 盈利概率: {sum(1 for r in returns if r > 0) / len(returns) * 100:.1f}%
"""
        
        report += """
## 4. 滚动窗口分析结果
"""
        
        if walk_forward_results:
            window_returns = [r['total_return'] for r in walk_forward_results]
            window_sharpes = [r['sharpe_ratio'] for r in walk_forward_results]
            
            report += f"""
- 分析窗口数: {len(walk_forward_results)}
- 平均窗口收益率: {np.mean(window_returns):.2f}%
- 窗口收益率稳定性: {np.std(window_returns):.2f}%
- 平均窗口夏普比率: {np.mean(window_sharpes):.3f}
- 正收益窗口比例: {sum(1 for r in window_returns if r > 0) / len(window_returns) * 100:.1f}%
"""
        
        report += """
## 5. 综合评估与建议

### 策略优势
- [根据测试结果填写]

### 策略劣势
- [根据测试结果填写]

### 改进建议
- [根据测试结果填写]

### 风险提示
- 历史回测结果不代表未来表现
- 实盘交易需要考虑滑点、手续费等因素
- 建议小资金验证后再扩大规模

---
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report
    
    def plot_comprehensive_analysis(self, optimization_results, stress_results, 
                                  monte_carlo_results, walk_forward_results):
        """绘制综合分析图表"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 参数优化结果
        if optimization_results:
            _, _, all_results = optimization_results
            sharpe_ratios = [r['sharpe_ratio'] for r in all_results]
            
            axes[0, 0].hist(sharpe_ratios, bins=20, alpha=0.7, color='blue')
            axes[0, 0].set_title('参数优化 - 夏普比率分布')
            axes[0, 0].set_xlabel('夏普比率')
            axes[0, 0].set_ylabel('频次')
            axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 压力测试结果
        if stress_results:
            scenarios = list(stress_results.keys())
            returns = [stress_results[s]['total_return'] if stress_results[s] else 0 for s in scenarios]
            
            bars = axes[0, 1].bar(scenarios, returns, color=['green' if r > 0 else 'red' for r in returns])
            axes[0, 1].set_title('压力测试 - 不同市场环境收益率')
            axes[0, 1].set_ylabel('收益率 (%)')
            axes[0, 1].tick_params(axis='x', rotation=45)
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 蒙特卡洛模拟结果
        if monte_carlo_results:
            returns = [r['total_return'] for r in monte_carlo_results if r['total_return'] is not None]
            
            axes[1, 0].hist(returns, bins=30, alpha=0.7, color='orange')
            axes[1, 0].axvline(np.mean(returns), color='red', linestyle='--', label=f'均值: {np.mean(returns):.2f}%')
            axes[1, 0].set_title('蒙特卡洛模拟 - 收益率分布')
            axes[1, 0].set_xlabel('收益率 (%)')
            axes[1, 0].set_ylabel('频次')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 滚动窗口分析
        if walk_forward_results:
            dates = [r['end_date'] for r in walk_forward_results]
            returns = [r['total_return'] for r in walk_forward_results]
            
            axes[1, 1].plot(dates, returns, marker='o', linewidth=2, markersize=4)
            axes[1, 1].axhline(0, color='red', linestyle='--', alpha=0.7)
            axes[1, 1].set_title('滚动窗口分析 - 收益率时间序列')
            axes[1, 1].set_ylabel('收益率 (%)')
            axes[1, 1].tick_params(axis='x', rotation=45)
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        return fig

# 示例使用
if __name__ == "__main__":
    # 导入策略类
    import sys
    sys.path.append('/home/ubuntu/contracts/strategies')
    from futures_strategies import DualMAStrategy, MomentumStrategy
    
    # 创建验证器
    validator = EnhancedBacktestValidator()
    
    # 生成多种市场情景
    print("生成多种市场情景数据...")
    scenarios = validator.generate_multiple_market_scenarios(days=200)
    
    # 选择一个策略进行全面验证
    strategy_class = DualMAStrategy
    strategy_name = "双均线策略"
    
    # 1. 参数优化
    print(f"\n开始 {strategy_name} 参数优化...")
    param_ranges = {
        'fast_period': [5, 8, 10, 12],
        'slow_period': [15, 20, 25, 30],
        'leverage': [1, 2]
    }
    
    optimization_results = validator.parameter_optimization(
        strategy_class, 
        scenarios['sideways_market'], 
        param_ranges
    )
    
    best_params, best_sharpe, _ = optimization_results
    print(f"最优参数: {best_params}")
    print(f"最佳夏普比率: {best_sharpe:.3f}")
    
    # 2. 压力测试
    print(f"\n开始 {strategy_name} 压力测试...")
    stress_results = validator.stress_test(strategy_class, scenarios, best_params)
    
    # 3. 蒙特卡洛模拟
    print(f"\n开始 {strategy_name} 蒙特卡洛模拟...")
    monte_carlo_results = validator.monte_carlo_simulation(
        strategy_class, 
        scenarios['sideways_market'], 
        num_simulations=50,
        params=best_params
    )
    
    # 4. 滚动窗口分析
    print(f"\n开始 {strategy_name} 滚动窗口分析...")
    walk_forward_results = validator.walk_forward_analysis(
        strategy_class,
        scenarios['sideways_market'],
        window_size=50,
        step_size=10,
        params=best_params
    )
    
    # 5. 生成综合报告
    print(f"\n生成 {strategy_name} 综合验证报告...")
    comprehensive_report = validator.generate_comprehensive_report(
        strategy_name,
        optimization_results,
        stress_results,
        monte_carlo_results,
        walk_forward_results
    )
    
    print(comprehensive_report)
    
    # 6. 绘制分析图表
    print(f"\n绘制 {strategy_name} 综合分析图表...")
    validator.plot_comprehensive_analysis(
        optimization_results,
        stress_results,
        monte_carlo_results,
        walk_forward_results
    )
    
    print("\n增强版回测验证完成！")

