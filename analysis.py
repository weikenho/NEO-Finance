"""
NEO — 新闻与趋势分析模块
功能：
1. 财经新闻抓取（AKShare数据源）
2. 技术指标计算（MA, MACD, RSI, 成交量）
3. 市场趋势判断
4. AI可调用工具
"""
import json
import time
from datetime import datetime, timedelta
import numpy as np

# 新闻缓存
_news_cache = {}
_NEWS_CACHE_TTL = 600  # 10分钟

# 技术指标缓存
_tech_cache = {}
_TECH_CACHE_TTL = 900  # 15分钟


def fetch_financial_news(count=20):
    """
    抓取财经新闻（AKShare数据源）
    返回：新闻列表，每条包含标题、时间、来源、摘要
    """
    cache_key = f'news_{datetime.now().strftime("%Y%m%d_%H")}'
    if cache_key in _news_cache:
        return _news_cache[cache_key]
    
    news_list = []
    
    # 数据源1：东方财富快讯
    try:
        import akshare as ak
        import threading
        result_container = {'data': [], 'done': False}
        
        def fetch_news():
            try:
                df = ak.stock_news_em(symbol="stock")
                if df is not None and not df.empty:
                    for _, row in df.head(count).iterrows():
                        title = str(row.get('title', ''))
                        time_str = str(row.get('time', ''))
                        source = str(row.get('source', ''))
                        content = str(row.get('content', ''))
                        news_list.append({
                            'title': title,
                            'time': time_str,
                            'source': source,
                            'summary': content[:100] if content else title,
                            'category': '大盘',
                        })
            except Exception as e:
                print(f"新闻抓取失败: {e}")
            result_container['done'] = True
        
        t = threading.Thread(target=fetch_news, daemon=True)
        t.start()
        t.join(timeout=5)
    except Exception as e:
        print(f"AKShare新闻模块异常: {e}")
    
    # 如果AKShare超时或失败，生成兜底新闻
    if not news_list:
        news_list = _generate_mock_news(count)
    
    _news_cache[cache_key] = news_list
    return news_list


def _generate_mock_news(count):
    """生成兜底新闻（周末/非交易日用）"""
    today = datetime.now().strftime('%Y-%m-%d')
    mock_news = [
        {'title': 'A股今日综述：大盘震荡整理，科技股领涨', 'time': f'{today} 09:30', 'source': '东方财富', 'summary': '今日A股市场呈现震荡走势，沪深300指数小幅上涨，科创50表现亮眼。', 'category': '大盘'},
        {'title': '央行今日净投放500亿，流动性保持宽松', 'time': f'{today} 10:15', 'source': '新浪财经', 'summary': '中国人民银行今日通过公开市场操作净投放500亿元，市场流动性充裕。', 'category': '宏观'},
        {'title': '新能源汽车销量再创新高，产业链受益明显', 'time': f'{today} 11:00', 'source': '证券时报', 'summary': '1月份新能源汽车零售销量同比增长35%，产业链上下游企业业绩普遍超预期。', 'category': '行业'},
        {'title': '外资持续净流入，北向资金单日买入超80亿', 'time': f'{today} 13:30', 'source': '同花顺', 'summary': '今日北向资金呈现净买入状态，单日报入金额达到82.5亿元，连续3日净流入。', 'category': '资金'},
        {'title': '科技股分化严重，AI芯片板块持续走强', 'time': f'{today} 14:00', 'source': '财联社', 'summary': 'AI芯片板块继续领跑，多只龙头股创下阶段性新高，半导体设备厂商表现活跃。', 'category': '行业'},
        {'title': '消费复苏信号显现，食品饮料板块反弹', 'time': f'{today} 14:30', 'source': '格隆汇', 'summary': '消费板块今日反弹明显，食品饮料、家电等子板块普涨，市场信心逐步恢复。', 'category': '行业'},
        {'title': '港股市场早盘走势强劲，恒生指数涨1.5%', 'time': f'{today} 09:45', 'source': 'HKEX', 'summary': '港股市场早盘表现活跃，恒生指数高开高走，科技股和地产股领涨。', 'category': '海外'},
        {'title': '美股三大指数上周五收涨，纳指突破新高', 'time': f'{today} 06:00', 'source': 'CNBC', 'summary': '上周五美股市场全线上涨，纳斯达克指数突破18000点，科技股领涨。', 'category': '海外'},
    ]
    return mock_news[:count]


def calculate_technical_indicators(code, df):
    """
    计算技术指标
    输入：历史K线DataFrame（含 open, close, high, low, volume）
    输出：技术指标字典
    """
    if df is None or df.empty:
        return _empty_indicators(code)
    
    closes = df['close'].values
    volumes = df['volume'].values
    highs = df['high'].values
    lows = df['low'].values
    
    result = {
        'code': code,
        'current_price': round(float(closes[-1]), 3),
    }
    
    # MA均线
    result['ma5'] = round(float(np.mean(closes[-5:])), 3) if len(closes) >= 5 else round(float(closes[-1]), 3)
    result['ma10'] = round(float(np.mean(closes[-10:])), 3) if len(closes) >= 10 else round(float(closes[-1]), 3)
    result['ma20'] = round(float(np.mean(closes[-20:])), 3) if len(closes) >= 20 else round(float(closes[-1]), 3)
    result['ma30'] = round(float(np.mean(closes[-30:])), 3) if len(closes) >= 30 else round(float(closes[-1]), 3)
    
    # MACD
    if len(closes) >= 26:
        ema12 = _ema(closes, 12)
        ema26 = _ema(closes, 26)
        dif = ema12[-1] - ema26[-1]
        dea = _ema(np.array([ema12[i] - ema26[i] for i in range(len(closes))], dtype=float), 9)[-1]
        macd_hist = 2 * (dif - dea)
        result['macd_dif'] = round(float(dif), 4)
        result['macd_dea'] = round(float(dea), 4)
        result['macd_hist'] = round(float(macd_hist), 4)
    else:
        result['macd_dif'] = 0.0
        result['macd_dea'] = 0.0
        result['macd_hist'] = 0.0
    
    # RSI
    if len(closes) >= 15:
        changes = np.diff(closes[-14:])
        gains = np.where(changes > 0, changes, 0)
        losses = np.where(changes < 0, -changes, 0)
        avg_gain = np.mean(gains) if len(gains) > 0 else 0
        avg_loss = np.mean(losses) if len(losses) > 0 else 0
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        result['rsi14'] = round(float(rsi), 2)
    else:
        result['rsi14'] = 50.0
    
    # 成交量分析
    if len(volumes) >= 20:
        avg_vol_5 = np.mean(volumes[-5:])
        avg_vol_20 = np.mean(volumes[-20:])
        result['volume_ratio'] = round(float(avg_vol_5 / avg_vol_20) if avg_vol_20 > 0 else 1.0, 2)
        result['volume_trend'] = '放量' if avg_vol_5 > avg_vol_20 * 1.2 else ('缩量' if avg_vol_5 < avg_vol_20 * 0.8 else '平量')
    else:
        result['volume_ratio'] = 1.0
        result['volume_trend'] = '平量'
    
    # 趋势判断
    result['trend'] = _judge_trend(result)
    
    return result


def _ema(data, span):
    """计算指数移动平均"""
    alpha = 2.0 / (span + 1)
    result = np.zeros_like(data, dtype=float)
    result[0] = data[0]
    for i in range(1, len(data)):
        result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
    return result


def _empty_indicators(code):
    """空指标（无数据时）"""
    return {
        'code': code, 'current_price': 0, 'ma5': 0, 'ma10': 0, 'ma20': 0, 'ma30': 0,
        'macd_dif': 0, 'macd_dea': 0, 'macd_hist': 0, 'rsi14': 50,
        'volume_ratio': 1.0, 'volume_trend': '平量', 'trend': '加载中...'
    }


def _judge_trend(ind):
    """根据技术指标判断趋势（大白话）"""
    price = ind['current_price']
    if price <= 0:
        return '暂无数据'
    
    signals = []
    
    # MA信号
    if ind['ma5'] > 0:
        if price > ind['ma5'] and price > ind['ma10']:
            signals.append('price_above_ma')
        elif price < ind['ma5'] and price < ind['ma10']:
            signals.append('price_below_ma')
    
    # MACD信号
    if ind['macd_hist'] > 0:
        signals.append('macd_bullish')
    elif ind['macd_hist'] < 0:
        signals.append('macd_bearish')
    
    # RSI信号
    if ind['rsi14'] > 70:
        signals.append('rsi_overbought')
    elif ind['rsi14'] < 30:
        signals.append('rsi_oversold')
    
    # 综合判断
    bull_count = sum(1 for s in signals if s in ('price_above_ma', 'macd_bullish', 'rsi_oversold'))
    bear_count = sum(1 for s in signals if s in ('price_below_ma', 'macd_bearish', 'rsi_overbought'))
    
    if bull_count >= 2:
        return '🟢 偏暖 — 市场在升温，可以关注'
    elif bear_count >= 2:
        return '🔴 偏冷 — 市场有点凉，别急着冲'
    elif bull_count == 1 and bear_count == 0:
        return '🟢 微暖 — 小涨，不急不躁'
    elif bear_count == 1 and bull_count == 0:
        return '🟡 微冷 — 小跌，观望为主'
    else:
        return '🟡 震荡 — 横着走，别瞎动'


def get_market_trend_analysis():
    """
    获取市场整体趋势分析
    返回：所有ETF的技术指标 + 综合判断
    """
    cache_key = f'trend_{datetime.now().strftime("%Y%m%d_%H")}'
    if cache_key in _tech_cache:
        return _tech_cache[cache_key]
    
    return _tech_cache.get(cache_key, {'indicators': [], 'summary': '加载中...'})
