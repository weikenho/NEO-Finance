"""
NEO — 宏观数据仪表盘
覆盖：
1. 中国宏观（CPI、PMI、M2、社融）
2. 美国宏观（美联储利率、CPI、非农、PMI）
3. 资金流向（北向资金、主力净流入）
4. 市场情绪指标（QVIX恐慌指数、涨跌家数）
"""
import threading
from datetime import datetime, timedelta

# 缓存
_macro_cache = {}
_CACHE_TTL = 600  # 10分钟（宏观数据更新没行情那么快）

def fetch_macro_dashboard():
    """
    获取宏观仪表盘数据
    返回：{
        'china': { 'cpi': ..., 'pmi': ..., 'm2': ..., 'shibor': ... },
        'usa': { 'fed_rate': ..., 'cpi': ..., 'non_farm': ..., 'pmi': ... },
        'fund_flow': { 'northbound': ..., 'main_force': ..., 'retail': ... },
        'sentiment': { 'qvix': ..., 'up_count': ..., 'down_count': ... },
    }
    """
    cache_key = f'macro_{datetime.now().strftime("%Y%m%d_%H%M")}'
    if cache_key in _macro_cache:
        return _macro_cache[cache_key]
    
    result = {
        'china': _fetch_china_macro(),
        'usa': _fetch_usa_macro(),
        'fund_flow': _fetch_fund_flow(),
        'sentiment': _fetch_sentiment(),
        'updated_at': datetime.now().strftime('%H:%M:%S'),
    }
    
    _macro_cache[cache_key] = result
    return result

def _fetch_china_macro():
    """中国宏观数据"""
    data = {
        'cpi': _safe_macro('macro_china_cpi_monthly', '中国CPI月率报告'),
        'ppi': _safe_macro('macro_china_ppi', '中国PPI月率报告'),
        'pmi': _safe_macro('macro_china_cx_pmi_yearly', '财新-中国制造业PMI'),
        'm2': _safe_macro('macro_china_m2_yearly', 'M2货币供应同比增长率'),
        'shibor': _safe_macro('macro_china_shibor_all', None),
        'lpr': _safe_macro('macro_china_lpr', None),
    }
    return data

def _fetch_usa_macro():
    """美国宏观数据"""
    data = {
        'fed_rate': _safe_macro('macro_bank_usa_interest_rate', '美联储利率决议报告'),
        'cpi': _safe_macro('macro_china_cpi_monthly', '中国CPI月率报告'),  # 先放中国CPI占位
        'unemployment': _safe_macro('macro_usa_unemployment_rate', '失业率报告'),
    }
    return data

def _safe_macro(func_name, filter_keyword=None):
    """安全调用AKShare宏观函数，返回最新一条数据"""
    try:
        import akshare as ak
        
        result_container = {'data': None, 'done': False}
        
        def fetch():
            try:
                func = getattr(ak, func_name)
                df = func()
                result_container['data'] = df
            except Exception:
                pass
            result_container['done'] = True
        
        t = threading.Thread(target=fetch, daemon=True)
        t.start()
        t.join(timeout=5)
        
        df = result_container['data']
        if df is not None and not df.empty:
            # 如果有关键词过滤
            if filter_keyword is not None:
                mask = df.iloc[:, 0].astype(str).str.contains(filter_keyword, na=False)
                filtered = df[mask]
                if not filtered.empty:
                    df = filtered
            
            row = df.iloc[0]
            # 提取日期和最新值
            date_val = str(row.iloc[1]) if len(row) > 1 else ''
            val_val = float(row.iloc[2]) if len(row) > 2 and str(row.iloc[2]).replace('.', '').replace('-', '').isdigit() else None
            
            return {
                'date': date_val,
                'value': val_val,
            }
    
    except Exception:
        pass
    
    return {'date': '—', 'value': None}

def _fetch_fund_flow():
    """资金流向数据"""
    data = {
        'northbound': {'net_inflow': None, 'date': '—'},
        'main_force': {'net_inflow': None, 'date': '—'},
        'retail': {'net_inflow': None, 'date': '—'},
    }
    
    try:
        import akshare as ak
        
        # 市场资金流向
        try:
            df = ak.stock_market_fund_flow()
            if df is not None and not df.empty:
                row = df.iloc[-1]
                date_val = str(row.iloc[0])
                
                # 主力净流入
                if '主力净流入-净额' in df.columns:
                    main_val = float(row['主力净流入-净额'])
                    data['main_force'] = {
                        'net_inflow': round(main_val / 1e8, 2),  # 转成亿
                        'net_ratio': None,
                        'date': date_val,
                    }
                
                # 小单（散户）净流入
                if '小单净流入-净额' in df.columns:
                    ret_val = float(row['小单净流入-净额'])
                    data['retail'] = {
                        'net_inflow': round(ret_val / 1e8, 2),
                        'date': date_val,
                    }
        except Exception:
            pass
        
        # 北向资金
        try:
            df2 = ak.stock_hsgt_fund_flow_summary_em()
            if df2 is not None and not df2.empty:
                # 筛选北向往A股的
                north_rows = df2[df2['资金方向'] == '北向']
                if not north_rows.empty:
                    row = north_rows.iloc[-1]
                    date_val = str(row.iloc[0])
                    data['northbound'] = {
                        'net_inflow': 0,
                        'date': date_val,
                    }
        except Exception:
            pass
    
    except Exception:
        pass
    
    return data

def _fetch_sentiment():
    """市场情绪指标"""
    data = {
        'qvix': {'value': None, 'date': '—', 'level': '—'},
        'up_count': None,
        'down_count': None,
    }
    
    try:
        import akshare as ak
        
        # QVIX（沪深300期权隐含波动率 = 恐慌指数）
        try:
            df = ak.index_option_300index_qvix()
            if df is not None and not df.empty:
                row = df.iloc[-1]
                val = float(row.iloc[-1]) if len(row) > 1 else None
                if val:
                    level = '冷静' if val < 15 else ('紧张' if val < 25 else ('恐慌' if val < 35 else '极度恐慌'))
                    data['qvix'] = {
                        'value': round(val, 2),
                        'date': str(row.iloc[0]),
                        'level': level,
                    }
        except Exception:
            pass
        
        # 涨跌家数（从北向数据获取）
        try:
            df2 = ak.stock_hsgt_fund_flow_summary_em()
            if df2 is not None and not df2.empty:
                row = df2.iloc[-1]
                if '上涨数' in df2.columns and '下跌数' in df2.columns:
                    data['up_count'] = int(row['上涨数'])
                    data['down_count'] = int(row['down_count'] if 'down_count' in df2.columns else row.get('下跌数', 0))
        except Exception:
            pass
    
    except Exception:
        pass
    
    return data

def get_macro_summary(macro_data):
    """生成宏观仪表盘的大白话总结"""
    lines = []
    
    # 中国PMI
    pmi = macro_data.get('china', {}).get('pmi')
    if pmi and pmi.get('value') is not None:
        val = pmi['value']
        if val > 52:
            lines.append(f'📈 中国制造业PMI {val}，高于52说明经济在"加速跑"')
        elif val > 50:
            lines.append(f'📊 中国制造业PMI {val}，刚过50说明经济在"扩产"')
        elif val > 48:
            lines.append(f'📉 中国制造业PMI {val}，快接近50的"分水岭"了')
        else:
            lines.append(f'📉 中国制造业PMI {val}，跌破50说明经济在"缩产"')
    
    # 美联储利率
    fed = macro_data.get('usa', {}).get('fed_rate')
    if fed and fed.get('value') is not None:
        val = fed['value']
        lines.append(f'💵 美联储利率 {val}%，利率高说明美元"贵"，资金容易回流美国')
    
    # 资金流向
    flow = macro_data.get('fund_flow', {})
    main = flow.get('main_force', {})
    if main.get('net_inflow') is not None:
        val = main['net_inflow']
        if val > 50:
            lines.append(f'💰 主力资金今天大幅净流入 {val}亿，大钱在进场')
        elif val > 10:
            lines.append(f'💰 主力资金今天净流入 {val}亿，大钱在慢慢进')
        elif val > -10:
            lines.append(f'💸 主力资金今天小幅净流出 {abs(val)}亿，大钱在慢慢撤')
        else:
            lines.append(f'💸 主力资金今天大幅净流出 {abs(val)}亿，大钱在跑路')
    
    # 恐慌指数
    qvix = macro_data.get('sentiment', {}).get('qvix', {})
    if qvix.get('value') is not None:
        lines.append(f'😱 市场恐慌指数(QVIX) {qvix["value"]}（{qvix["level"]}）')
    
    if not lines:
        lines.append('📊 宏观数据加载中，请稍后再看')
    
    return '\n'.join(lines)
