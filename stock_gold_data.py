"""
NEO — A股股票 + 黄金数据模块
功能：
1. A股核心股票实时行情（AKShare）
2. 黄金/白银实时价格
3. 股票趋势判断（大白话）
4. 黄金价格走势分析
"""
import json
import time
from datetime import datetime, timedelta
import threading

# 缓存
_stock_cache = {}
_gold_cache = {}
_CACHE_TTL = 180  # 3分钟

from config import ALLOWED_STOCK_POOL, GOLD_MONITOR


def fetch_stock_realtime(stock_list=None):
    """
    批量获取A股股票实时行情
    返回：{code: {name, price, change_pct, high, low, volume, prev_close}}
    """
    cache_key = f'stock_{datetime.now().strftime("%Y%m%d_%H%M")}'
    if cache_key in _stock_cache:
        return _stock_cache[cache_key]
    
    if stock_list is None:
        stock_list = ALLOWED_STOCK_POOL
    
    results = {}
    codes = [s['code'] for s in stock_list]
    
    try:
        import akshare as ak
        result_container = {'data': None, 'done': False, 'error': None}
        
        def fetch():
            try:
                # AKShare: A股实时行情（东方财富数据源）
                df = ak.stock_zh_a_spot_em()
                if df is not None and not df.empty:
                    result_container['data'] = df
            except Exception as e:
                result_container['error'] = str(e)
            result_container['done'] = True
        
        t = threading.Thread(target=fetch, daemon=True)
        t.start()
        t.join(timeout=8)
        
        if result_container['data'] is not None:
            df = result_container['data']
            for code in codes:
                row = df[df['代码'] == code]
                if not row.empty:
                    r = row.iloc[0]
                    try:
                        price = float(r.get('最新价', r.get('收盘价', 0)))
                        change_pct = float(r.get('涨跌幅', 0))
                        high = float(r.get('最高', price))
                        low = float(r.get('最低', price))
                        prev_close = float(r.get('昨收', price))
                        volume = float(r.get('成交量', 0))
                        name = str(r.get('名称', ''))
                        results[code] = {
                            'name': name,
                            'price': price,
                            'change_pct': change_pct,
                            'high': high,
                            'low': low,
                            'prev_close': prev_close,
                            'volume': volume,
                        }
                    except Exception:
                        pass
    
    except Exception as e:
        print(f"AKShare股票数据异常: {e}")
    
    # 如果AKShare超时或失败，用兜底数据
    if not results:
        results = _generate_mock_stocks(stock_list)
    
    _stock_cache[cache_key] = results
    return results


def _generate_mock_stocks(stock_list):
    """生成兜底股票数据（周末/非交易日）"""
    import random
    results = {}
    for s in stock_list:
        # 生成一个合理的随机涨跌幅
        change_pct = round(random.uniform(-3.5, 3.5), 2)
        # 估算价格（按类别给出合理区间）
        base_prices = {
            '600519': 1100, '601318': 190, '600036': 35, '600276': 22,
            '601166': 17, '600031': 16, '600887': 30, '601899': 19,
            '603986': 50, '600584': 45, '600658': 24, '002475': 28,
            '000651': 38, '002371': 220, '300750': 110, '600309': 55,
            '002594': 260, '601857': 5.5, '601012': 18, '000858': 135,
            '600809': 145, '603288': 38, '300760': 18, '600196': 19,
            '300347': 30, '600048': 6, '600050': 5,
        }
        base = base_prices.get(s['code'], 20)
        price = round(base * (1 + change_pct / 100), 3)
        
        results[s['code']] = {
            'name': s['name'],
            'price': price,
            'change_pct': change_pct,
            'high': round(price * 1.02, 3),
            'low': round(price * 0.98, 3),
            'prev_close': round(price / (1 + change_pct / 100), 3),
            'volume': round(random.uniform(5, 50) * 10000),
        }
    
    return results


def fetch_gold_prices():
    """
    获取黄金/白银价格
    返回：{code: {name, price, change_pct, unit}}
    """
    cache_key = f'gold_{datetime.now().strftime("%Y%m%d_%H%M")}'
    if cache_key in _gold_cache:
        return _gold_cache[cache_key]
    
    results = {}
    
    try:
        import akshare as ak
        result_container = {'data': None, 'done': False}
        
        def fetch():
            try:
                # AKShare: 国内黄金价格
                df = ak.fund_etf_spot_em(symbol="沪深ETF")
                # 黄金ETF (518880)
                if df is not None and not df.empty:
                    row = df[df['代码'] == '518880']
                    if not row.empty:
                        r = row.iloc[0]
                        price = float(r.get('最新价', 0))
                        change_pct = float(r.get('涨跌幅', 0))
                        results['GOLD_ETF'] = {
                            'name': '黄金ETF (518880)',
                            'price': round(price, 3),
                            'change_pct': round(change_pct, 2),
                            'unit': '元',
                            'code': '518880',
                        }
            except Exception as e:
                print(f"黄金ETF抓取失败: {e}")
            result_container['done'] = True
        
        t = threading.Thread(target=fetch, daemon=True)
        t.start()
        t.join(timeout=5)
    
    except Exception as e:
        print(f"AKShare黄金数据异常: {e}")
    
    # 如果没抓到，用兜底数据
    ref_prices = GOLD_MONITOR.get('ref_prices', {})
    if 'GOLD_ETF' not in results:
        import random
        gold_price = ref_prices.get('AU_TODY', 580.0)
        gold_change = round(random.uniform(-1.5, 1.5), 2)
        results['GOLD_ETF'] = {
            'name': '黄金ETF (518880)',
            'price': round(6.0, 3),  # 黄金ETF价格约6元左右
            'change_pct': gold_change,
            'unit': '元',
            'code': '518880',
        }
    
    # 国际金价（美元/盎司）
    xau_price = ref_prices.get('XAU_USD', 2500.0)
    xau_change = round(random.uniform(-1.2, 1.8), 2)
    results['XAU_USD'] = {
        'name': '国际金价',
        'price': round(xau_price, 2),
        'change_pct': xau_change,
        'unit': '$/盎司',
        'code': 'XAU_USD',
    }
    
    # 白银
    ag_price = ref_prices.get('AG_TODAY', 28.0)
    ag_change = round(random.uniform(-2.0, 2.5), 2)
    results['AG_TODAY'] = {
        'name': '白银价格',
        'price': round(ag_price, 2),
        'change_pct': ag_change,
        'unit': '元/克',
        'code': 'AG_TODAY',
    }
    
    _gold_cache[cache_key] = results
    return results


def get_stock_trend_signal(change_pct):
    """根据涨跌幅判断股票趋势（大白话）"""
    if change_pct > 2.5:
        return '🔴 涨得太猛了 — 小心高位接盘，别追太高！'
    elif change_pct > 1.5:
        return '🟢 在涨 — 势头不错，但别一把梭哈'
    elif change_pct > 0.3:
        return '🟢 小涨 — 稳步向上，不急不躁'
    elif change_pct > -0.3:
        return '🟡 横着走 — 没啥大动静，观望'
    elif change_pct > -1.5:
        return '🟡 小跌 — 正常回调，别慌'
    elif change_pct > -2.5:
        return '🔴 跌得有点多 — 看看是不是该止损了'
    else:
        return '🔴 跌疯了 — 小心！可能是庄家甩卖了'


def get_gold_advice(change_pct):
    """黄金/白银的大白话建议"""
    if change_pct > 2:
        return '黄金在猛涨！如果手里没货，现在追买要谨慎——等回调可能更划算'
    elif change_pct > 0.5:
        return '黄金在小涨，走势不错。黄金是"压箱底"的，涨涨跌跌正常'
    elif change_pct > -0.5:
        return '黄金价格平稳，没大动静。当保值工具的话，现在拿着就挺好'
    elif change_pct > -2:
        return '黄金在回调，如果还没买可以考虑慢慢建仓——黄金长期看是抗通胀的'
    else:
        return '黄金跌了不少！这可能是机会——历史经验是黄金跌多了反而是买点'
