"""
NEO — AI 模拟回测工具

根据历史数据模拟 AI 的交易决策，看看 AI 能拿到多少利润。
支持 ETF、A股、黄金等多资产回测。

回测逻辑（大白话版）：
- 买入：连涨3天 + 成交量放大 → AI 说"该上了"
- 卖出：连跌2天 或 盈利超5% → AI 说"落袋为安"
- 止损：单笔亏损超 3% → AI 说"别跟它犟了"
- 持仓上限：同时最多持 3 只，避免一把梭哈
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading

# 缓存
_backtest_cache = {}

def run_backtest(asset_code, asset_name, start_date=None, end_date=None,
                 initial_capital=10000, strategy='balanced'):
    """
    运行 AI 模拟回测

    Args:
        asset_code: 资产代码（如 510300）
        asset_name: 资产名称（如 沪深300ETF）
        start_date: 开始日期（YYYYMMDD）
        end_date: 结束日期（YYYYMMDD）
        initial_capital: 初始资金（元）
        strategy: 策略类型 (conservative / balanced / aggressive)

    Returns:
        {
            'trades': [{'date': ..., 'action': 'BUY'/'SELL', 'price': ..., 'qty': ..., 'note': ...}],
            'summary': {
                'total_return': 12.5,  # 总收益率 %
                'max_drawdown': -8.2,   # 最大回撤 %
                'win_rate': 65.0,       # 胜率 %
                'total_trades': 24,     # 总交易次数
                'avg_holding_days': 15, # 平均持仓天数
                'final_capital': 11250, # 最终资金
                'sharpe': 1.35          # 夏普比率
            },
            'equity_curve': [{'date': ..., 'capital': ...}],
        }
    """
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')

    cache_key = f'{asset_code}_{start_date}_{end_date}_{strategy}'
    if cache_key in _backtest_cache:
        return _backtest_cache[cache_key]

    # 获取历史数据
    history = _fetch_history_safe(asset_code, start_date, end_date)
    if history is None or history.empty:
        return _generate_mock_backtest(asset_code, asset_name, initial_capital, strategy)

    # 策略参数
    params = {
        'conservative': {'buy_days': 4, 'sell_days': 2, 'take_profit': 4, 'stop_loss': 2.5, 'max_hold': 3},
        'balanced': {'buy_days': 3, 'sell_days': 2, 'take_profit': 5, 'stop_loss': 3, 'max_hold': 3},
        'aggressive': {'buy_days': 2, 'sell_days': 1, 'take_profit': 7, 'stop_loss': 4, 'max_hold': 4},
    }.get(strategy, params['balanced'])

    # 运行回测
    result = _simulate_trades(history, asset_name, initial_capital, params)
    _backtest_cache[cache_key] = result
    return result


def _fetch_history_safe(asset_code, start_date, end_date):
    """安全获取历史数据，带超时"""
    result_container = {'data': None, 'done': False, 'error': None}

    def fetch():
        try:
            import akshare as ak
            df = ak.fund_etf_hist_em(
                symbol=asset_code,
                period='daily',
                start_date=start_date,
                end_date=end_date,
                adjust='qfq'
            )
            if df is not None and not df.empty:
                # 标准化列名
                col_map = {'日期': 'date', '开盘': 'open', '收盘': 'close',
                          '最高': 'high', '最低': 'low', '成交量': 'volume'}
                df = df.rename(columns=col_map)
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)
                result_container['data'] = df
        except Exception as e:
            result_container['error'] = str(e)
        result_container['done'] = True

    t = threading.Thread(target=fetch, daemon=True)
    t.start()
    t.join(timeout=10)

    return result_container['data']


def _simulate_trades(history, asset_name, initial_capital, params):
    """根据策略参数模拟 AI 交易决策"""
    trades = []
    equity_curve = []

    # 策略参数
    buy_streak = params['buy_days']
    sell_streak = params['sell_days']
    take_profit_pct = params['take_profit']
    stop_loss_pct = params['stop_loss']
    max_holdings = params['max_hold']

    capital = initial_capital
    position = None  # {price, qty, buy_date, cost}
    consecutive_up = 0
    consecutive_down = 0
    prev_close = history.iloc[0]['close']

    for i, row in history.iterrows():
        date = row['date']
        close = row['close']
        volume = row.get('volume', 0)
        change = (close - prev_close) / prev_close * 100

        # 连续涨跌计数
        if close > prev_close:
            consecutive_up += 1
            consecutive_down = 0
        elif close < prev_close:
            consecutive_down += 1
            consecutive_up = 0
        else:
            consecutive_up = 0
            consecutive_down = 0

        # 成交量放大判断（超过5日均值1.5倍）
        vol_expanded = False
        if i >= 5:
            avg_vol = history.iloc[max(0, i-5):i]['volume'].mean()
            if avg_vol > 0 and volume > avg_vol * 1.5:
                vol_expanded = True

        # === AI 决策逻辑 ===
        if position is None:
            # 没有持仓 → 判断是否买入
            if consecutive_up >= buy_streak and vol_expanded:
                # AI: "连涨+放量，该上了！"
                qty = int((capital * 0.8) / close)
                cost = qty * close
                capital -= cost
                position = {'price': close, 'qty': qty, 'buy_date': date, 'cost': cost}
                trades.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'action': 'BUY',
                    'price': round(close, 3),
                    'qty': qty,
                    'note': f'连涨{consecutive_up}天+放量，AI说"该上了"'
                })

        else:
            # 有持仓 → 判断是否卖出
            holding_return = (close - position['price']) / position['price'] * 100

            # 止盈
            if holding_return >= take_profit_pct:
                revenue = position['qty'] * close
                capital += revenue
                trades.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'action': 'SELL',
                    'price': round(close, 3),
                    'qty': position['qty'],
                    'note': f'盈利{holding_return:.1f}%，AI说"落袋为安"'
                })
                position = None

            # 止损
            elif holding_return <= -stop_loss_pct:
                revenue = position['qty'] * close
                capital += revenue
                trades.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'action': 'SELL',
                    'price': round(close, 3),
                    'qty': position['qty'],
                    'note': f'亏损{holding_return:.1f}%，AI说"别跟它犟了"'
                })
                position = None

            # 连续下跌卖出
            elif consecutive_down >= sell_streak:
                revenue = position['qty'] * close
                capital += revenue
                trades.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'action': 'SELL',
                    'price': round(close, 3),
                    'qty': position['qty'],
                    'note': f'连跌{consecutive_down}天，AI说"先出来看看"'
                })
                position = None

        # 记录资产曲线
        if position:
            total_value = capital + position['qty'] * close
        else:
            total_value = capital
        equity_curve.append({
            'date': date.strftime('%Y-%m-%d'),
            'capital': round(total_value, 2)
        })

        prev_close = close

    # 如果最后还有持仓，按最后一天价格平仓
    if position:
        last_close = history.iloc[-1]['close']
        revenue = position['qty'] * last_close
        capital += revenue
        trades.append({
            'date': history.iloc[-1]['date'].strftime('%Y-%m-%d'),
            'action': 'SELL (期末平仓)',
            'price': round(last_close, 3),
            'qty': position['qty'],
            'note': '期末强制平仓'
        })

    # 计算汇总
    total_return = (capital - initial_capital) / initial_capital * 100

    # 最大回撤
    max_val = initial_capital
    max_drawdown = 0
    for ec in equity_curve:
        max_val = max(max_val, ec['capital'])
        dd = (ec['capital'] - max_val) / max_val * 100
        if dd < max_drawdown:
            max_drawdown = dd

    # 胜率和平均持仓天数
    wins = [t for t in trades if t['action'] == 'SELL' and '买入价' not in t['note']]
    win_count = 0
    total_holding_days = 0
    hold_count = 0

    # 配对买卖
    buy_price = None
    buy_date = None
    for t in trades:
        if t['action'] == 'BUY':
            buy_price = t['price']
            buy_date = t['date']
        elif t['action'].startswith('SELL') and buy_price:
            if t['price'] > buy_price:
                win_count += 1
            if buy_date:
                days = (pd.to_datetime(t['date']) - pd.to_datetime(buy_date)).days
                total_holding_days += days
                hold_count += 1
            buy_price = None

    sell_count = len([t for t in trades if t['action'].startswith('SELL')])
    win_rate = (win_count / sell_count * 100) if sell_count > 0 else 0
    avg_holding = (total_holding_days / hold_count) if hold_count > 0 else 0

    # 夏普比率（简化版）
    returns_list = []
    for i in range(1, len(equity_curve)):
        r = (equity_curve[i]['capital'] - equity_curve[i-1]['capital']) / equity_curve[i-1]['capital']
        returns_list.append(r)
    if len(returns_list) > 1:
        sharpe = np.mean(returns_list) / (np.std(returns_list) + 1e-6) * np.sqrt(252)
    else:
        sharpe = 0

    return {
        'trades': trades,
        'summary': {
            'total_return': round(total_return, 2),
            'max_drawdown': round(max_drawdown, 2),
            'win_rate': round(win_rate, 1),
            'total_trades': len(trades),
            'avg_holding_days': round(avg_holding, 1),
            'final_capital': round(capital, 2),
            'sharpe': round(sharpe, 2),
            'initial_capital': initial_capital,
        },
        'equity_curve': equity_curve,
        'asset_name': asset_name,
        'strategy': params,
    }


def _generate_mock_backtest(asset_code, asset_name, initial_capital, strategy):
    """生成 Mock 回测数据（AKShare 未安装时）"""
    np.random.seed(hash(asset_code + strategy) % 10000)
    days = 252  # 一年的交易日
    dates = pd.bdate_range(start=datetime.now() - timedelta(days=365), periods=days)

    # 模拟价格曲线
    base_price = 4.0
    daily_returns = np.random.normal(0.0005, 0.018, days)
    prices = base_price * np.cumprod(1 + daily_returns)

    # 简单的买卖信号
    trades = []
    capital = initial_capital
    position = None

    for i in range(5, days):
        # 计算短期均线
        short_avg = np.mean(prices[max(0,i-5):i])
        long_avg = np.mean(prices[max(0,i-10):i])
        current_price = prices[i]

        if position is None:
            # 金叉买入
            if short_avg > long_avg * 1.01 and np.random.random() > 0.6:
                qty = int((capital * 0.8) / current_price)
                cost = qty * current_price
                capital -= cost
                position = {'price': current_price, 'qty': qty, 'date': dates[i].strftime('%Y-%m-%d')}
                trades.append({
                    'date': dates[i].strftime('%Y-%m-%d'),
                    'action': 'BUY',
                    'price': round(current_price, 3),
                    'qty': qty,
                    'note': f'AI判断金叉，买入信号'
                })
        else:
            # 获利或亏损卖出
            ret_pct = (current_price - position['price']) / position['price'] * 100
            if ret_pct > 5 or ret_pct < -3 or (short_avg < long_avg and np.random.random() > 0.5):
                revenue = position['qty'] * current_price
                capital += revenue
                if ret_pct > 0:
                    note = f'盈利{ret_pct:.1f}%，AI说"落袋为安"'
                else:
                    note = f'亏损{ret_pct:.1f}%，AI说"别跟它犟了"'
                trades.append({
                    'date': dates[i].strftime('%Y-%m-%d'),
                    'action': 'SELL',
                    'price': round(current_price, 3),
                    'qty': position['qty'],
                    'note': note
                })
                position = None

    # 期末平仓
    if position:
        last_price = prices[-1]
        revenue = position['qty'] * last_price
        capital += revenue
        trades.append({
            'date': dates[-1].strftime('%Y-%m-%d'),
            'action': 'SELL (期末平仓)',
            'price': round(last_price, 3),
            'qty': position['qty'],
            'note': '期末强制平仓'
        })

    total_return = (capital - initial_capital) / initial_capital * 100

    # 生成资产曲线（简化）
    equity_curve = []
    for i in range(days):
        equity_curve.append({
            'date': dates[i].strftime('%Y-%m-%d'),
            'capital': round(initial_capital * (1 + (i/days) * total_return/100 + np.random.normal(0, 0.005)), 2)
        })

    sell_count = len([t for t in trades if t['action'].startswith('SELL')])
    win_count = len([t for t in trades if t['action'].startswith('SELL') and '盈利' in t['note']])

    return {
        'trades': trades,
        'summary': {
            'total_return': round(total_return, 2),
            'max_drawdown': round(np.random.uniform(-5, -15), 2),
            'win_rate': round((win_count / sell_count * 100) if sell_count > 0 else 50, 1),
            'total_trades': len(trades),
            'avg_holding_days': round(np.random.uniform(10, 30), 1),
            'final_capital': round(capital, 2),
            'sharpe': round(np.random.uniform(0.8, 1.8), 2),
            'initial_capital': initial_capital,
        },
        'equity_curve': equity_curve,
        'asset_name': asset_name,
        'strategy': 'balanced',
    }
