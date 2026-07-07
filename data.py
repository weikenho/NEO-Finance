"""
NEO — 行情数据获取
数据源：AKShare（免费A股ETF数据）
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

def _safe_float(val, default=0.0):
    """安全转float，处理NaN/None/空字符串"""
    if val is None or val == '':
        return default
    try:
        f = float(val)
        return f if not np.isnan(f) else default
    except (ValueError, TypeError):
        return default

# 缓存：防止频繁请求被AKShare封
_data_cache = {}
_CACHE_TTL = 300  # 5分钟

def fetch_etf_realtime(etf_codes: list) -> dict:
    """获取ETF实时行情 — 帶超時機制（3秒內沒返回就用兜底數據）"""
    # 週六日/非交易日直接返回空，讓app.py用配置中的ref_price兜底
    from datetime import datetime
    today = datetime.now()
    if today.weekday() >= 5:  # 週六(5)、週日(6)
        return {}
    
    cache_key = 'realtime_' + datetime.now().strftime('%Y%m%d_%H')
    if cache_key in _data_cache:
        return _data_cache[cache_key]
    
    try:
        import akshare as ak
        import threading
        result_container = {'data': None, 'done': False}
        
        def fetch_in_thread():
            try:
                df = ak.fund_etf_spot_em()
                results = {}
                for code in etf_codes:
                    row = df[df['代码'] == code]
                    if not row.empty:
                        row = row.iloc[0]
                        results[code] = {
                            'name': row.get('名称', code),
                            'price': _safe_float(row.get('最新价', 0)),
                            'change_pct': _safe_float(row.get('涨跌幅', 0)),
                            'volume': _safe_float(row.get('成交量', 0)),
                            'high': _safe_float(row.get('最高价', 0)),
                            'low': _safe_float(row.get('最低价', 0)),
                            'prev_close': _safe_float(row.get('昨收', 0)),
                            'open': _safe_float(row.get('开盘价', 0)),
                        }
                result_container['data'] = results
            except Exception as e:
                print(f"AKShare獲取失敗: {e}")
            result_container['done'] = True
        
        # 啟動線程，3秒超時
        t = threading.Thread(target=fetch_in_thread, daemon=True)
        t.start()
        t.join(timeout=3)
        
        if result_container['done'] and result_container['data']:
            _data_cache[cache_key] = result_container['data']
            return result_container['data']
        else:
            print("AKShare超時（3秒），返回空數據用兜底")
            return {}
    except ImportError:
        return {}
    except Exception as e:
        print(f"AKShare異常: {e}，返回空數據用兜底")
        return {}

def _get_mock_realtime(etf_codes: list) -> dict:
    """Mock数据（AKShare未安装时的降级方案）"""
    import random
    results = {}
    base_prices = {
        '510300': 4.2, '510500': 6.1, '159915': 1.85, '588000': 1.1,
        '510880': 2.5, '513100': 1.9, '513500': 2.3, '159941': 1.6,
    }
    for code in etf_codes:
        base = base_prices.get(code, 1.5)
        change = random.uniform(-2, 2)
        results[code] = {
            'name': f'ETF{code}', 'price': round(base, 3),
            'change_pct': round(change, 2), 'volume': random.randint(500, 5000),
            'high': round(base * 1.02, 3), 'low': round(base * 0.98, 3),
            'prev_close': round(base / (1 + change/100), 3),
            'open': round(base * (1 + random.uniform(-0.005, 0.005)), 3),
        }
    return results

def fetch_ETF_history(code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取ETF历史K线数据"""
    # Check cache
    cache_key = f'history_{code}_{start_date}_{end_date}'
    if cache_key in _data_cache:
        return _data_cache[cache_key]
    
    try:
        import akshare as ak
        df = ak.fund_etf_hist_em(
            symbol=code,
            period='daily',
            start_date=start_date,
            end_date=end_date,
            adjust='qfq'  # 前复权
        )
        if df is not None and not df.empty:
            # 标准化列名
            col_map = {
                '日期': 'date', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume'
            }
            df = df.rename(columns=col_map)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            _data_cache[cache_key] = df
            return df
        return pd.DataFrame()
    except ImportError:
        return _generate_mock_history(code, start_date, end_date)

def _generate_mock_history(code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """生成Mock历史数据"""
    import numpy as np
    dates = pd.bdate_range(start=start_date, end=end_date)
    base_price = 4.0 if code.startswith('5103') else 6.0
    np.random.seed(hash(code) % 1000)
    returns = np.random.normal(0.0005, 0.015, len(dates))
    closes = base_price * np.cumprod(1 + returns)
    opens = closes * (1 + np.random.uniform(-0.01, 0.01, len(dates)))
    highs = np.maximum(opens, closes) * (1 + np.random.uniform(0, 0.01, len(dates)))
    lows = np.minimum(opens, closes) * (1 - np.random.uniform(0, 0.01, len(dates)))
    volumes = np.random.randint(500, 5000, len(dates)).astype(float)
    return pd.DataFrame({
        'date': dates, 'open': opens, 'close': closes,
        'high': highs, 'low': lows, 'volume': volumes
    })
