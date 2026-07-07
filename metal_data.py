"""
NEO — 金属数据模块 v2
覆盖：贵金属（金/银/铂）+ 基本金属（铜/铝/锌/镍/铅/锡/氧化铝）
数据来源：上海期货交易所 (SHFE) + 国际能源交易中心 (INE) + 广州期货交易所 (GFEX)
数据源：AKShare `futures_comm_info` (实时期货主力合约价格)
"""
import threading
from datetime import datetime

# 缓存
_metal_cache = {}
_CACHE_TTL = 180  # 3分钟

# 金属品种配置
METAL_SPECIFICATIONS = [
    # ========== 贵金属 ==========
    {
        'category': '贵金属',
        'symbol': '黄金', 'prefix': 'au', 'unit': '元/克', 'lot_size': 1, 'tick': 0.05,
        'icon': '🥇', 'description': '避险之王，抗通胀首选',
    },
    {
        'category': '贵金属',
        'symbol': '白银', 'prefix': 'ag', 'unit': '元/千克', 'lot_size': 15, 'tick': 5,
        'icon': '🥈', 'description': '穷人的黄金，波动更大',
    },
    {
        'category': '贵金属',
        'symbol': '铂', 'prefix': 'pt', 'unit': '元/克', 'lot_size': 3, 'tick': 0.05,
        'icon': '💎', 'description': '汽车催化剂+首饰双驱动，跟黄金经常分叉',
    },
    # ========== 基本金属 ==========
    {
        'category': '基本金属',
        'symbol': '沪铜', 'prefix': 'cu', 'unit': '元/吨', 'lot_size': 5, 'tick': 10,
        'icon': '🟤', 'description': '铜博士——宏观经济的晴雨表',
    },
    {
        'category': '基本金属',
        'symbol': '国际铜', 'prefix': 'bc', 'unit': '元/吨', 'lot_size': 5, 'tick': 10,
        'icon': '🌐', 'description': '上期所国际铜，对标LME铜',
    },
    {
        'category': '基本金属',
        'symbol': '沪铝', 'prefix': 'al', 'unit': '元/吨', 'lot_size': 5, 'tick': 5,
        'icon': '⚙️', 'description': '轻量化趋势下的工业金属',
    },
    {
        'category': '基本金属',
        'symbol': '沪锌', 'prefix': 'zn', 'unit': '元/吨', 'lot_size': 5, 'tick': 5,
        'icon': '🔩', 'description': '镀锌+压铸，制造业风向标',
    },
    {
        'category': '基本金属',
        'symbol': '沪镍', 'prefix': 'ni', 'unit': '元/吨', 'lot_size': 1, 'tick': 10,
        'icon': '🔋', 'description': '电池金属之王，波动大',
    },
    {
        'category': '基本金属',
        'symbol': '沪铅', 'prefix': 'pb', 'unit': '元/吨', 'lot_size': 5, 'tick': 5,
        'icon': '🔋', 'description': '蓄电池+造船，老牌工业金属',
    },
    {
        'category': '基本金属',
        'symbol': '沪锡', 'prefix': 'sn', 'unit': '元/吨', 'lot_size': 1, 'tick': 10,
        'icon': '📱', 'description': '电子焊料+光伏玻璃，半导体受益',
    },
    {
        'category': '基本金属',
        'symbol': '氧化铝', 'prefix': 'ao', 'unit': '元/吨', 'lot_size': 20, 'tick': 1,
        'icon': '🏭', 'description': '铝的前身，新能源带动需求',
    },
]

def _find_main_contract(df, prefix):
    """在期货合约表中找到指定前缀的主力合约"""
    # 过滤出匹配前缀的合约
    mask = df['合约代码'].str.startswith(prefix, na=False)
    matched = df[mask]
    # 优先找"主力合约"
    main = matched[matched['备注'] == '主力合约']
    if not main.empty:
        return main.iloc[0]
    if not matched.empty:
        # 取第一个
        return matched.iloc[0]
    return None

def fetch_metals():
    """
    获取所有金属期货主力合约实时价格
    返回：{metal_type: {name, price, unit, category, ...}}
    """
    cache_key = f'metal_{datetime.now().strftime("%Y%m%d_%H%M")}'
    if cache_key in _metal_cache:
        return _metal_cache[cache_key]
    
    results = {}
    
    try:
        import akshare as ak
        
        result_container = {'data': None, 'done': False, 'error': None}
        
        def fetch():
            try:
                df = ak.futures_comm_info(symbol='所有')
                result_container['data'] = df
            except Exception as e:
                result_container['error'] = str(e)
            result_container['done'] = True
        
        t = threading.Thread(target=fetch, daemon=True)
        t.start()
        t.join(timeout=10)
        
        if result_container['data'] is not None:
            df = result_container['data']
            
            for spec in METAL_SPECIFICATIONS:
                row = _find_main_contract(df, spec['prefix'])
                if row is not None:
                    price = float(row['现价'])
                    results[spec['symbol']] = {
                        'name': spec['symbol'],
                        'full_name': spec['symbol'] + '主力',
                        'price': round(price, 2),
                        'unit': spec['unit'],
                        'category': spec['category'],
                        'icon': spec['icon'],
                        'description': spec['description'],
                        'lot_size': spec['lot_size'],
                        'change_pct': None,  # 期货主力合约没有涨跌幅，用昨结算计算
                        'contract': row['合约名称'],
                    }
        else:
            print(f"金属数据获取失败: {result_container['error']}")
    
    except Exception as e:
        print(f"AKShare金属数据异常: {e}")
    
    # 如果AKShare失败，用兜底数据
    if not results:
        results = _generate_fallback_metals()
    
    _metal_cache[cache_key] = results
    return results

def _generate_fallback_metals():
    """周末/非交易日的兜底数据"""
    fallback = {
        '黄金': {'name': '黄金', 'full_name': '黄金主力', 'price': 880.60, 'unit': '元/克', 'category': '贵金属', 'icon': '🥇', 'description': '避险之王，抗通胀首选', 'lot_size': 1, 'change_pct': None, 'contract': '黄金主力'},
        '白银': {'name': '白银', 'full_name': '白银主力', 'price': 14019.0, 'unit': '元/千克', 'category': '贵金属', 'icon': '🥈', 'description': '穷人的黄金，波动更大', 'lot_size': 15, 'change_pct': None, 'contract': '白银主力'},
        '铂': {'name': '铂', 'full_name': '铂主力', 'price': 393.95, 'unit': '元/克', 'category': '贵金属', 'icon': '💎', 'description': '汽车催化剂+首饰双驱动', 'lot_size': 3, 'change_pct': None, 'contract': '铂主力'},
        '沪铜': {'name': '沪铜', 'full_name': '沪铜主力', 'price': 101820.0, 'unit': '元/吨', 'category': '基本金属', 'icon': '🟤', 'description': '铜博士——宏观经济的晴雨表', 'lot_size': 5, 'change_pct': None, 'contract': '沪铜主力'},
        '沪铝': {'name': '沪铝', 'full_name': '沪铝主力', 'price': 22930.0, 'unit': '元/吨', 'category': '基本金属', 'icon': '⚙️', 'description': '轻量化趋势下的工业金属', 'lot_size': 5, 'change_pct': None, 'contract': '沪铝主力'},
        '沪锌': {'name': '沪锌', 'full_name': '沪锌主力', 'price': 23885.0, 'unit': '元/吨', 'category': '基本金属', 'icon': '🔩', 'description': '镀锌+压铸，制造业风向标', 'lot_size': 5, 'change_pct': None, 'contract': '沪锌主力'},
        '沪镍': {'name': '沪镍', 'full_name': '沪镍主力', 'price': 129000.0, 'unit': '元/吨', 'category': '基本金属', 'icon': '🔋', 'description': '电池金属之王，波动大', 'lot_size': 1, 'change_pct': None, 'contract': '沪镍主力'},
        '沪铅': {'name': '沪铅', 'full_name': '沪铅主力', 'price': 16250.0, 'unit': '元/吨', 'category': '基本金属', 'icon': '🔋', 'description': '蓄电池+造船，老牌工业金属', 'lot_size': 5, 'change_pct': None, 'contract': '沪铅主力'},
        '沪锡': {'name': '沪锡', 'full_name': '沪锡主力', 'price': 385590.0, 'unit': '元/吨', 'category': '基本金属', 'icon': '📱', 'description': '电子焊料+光伏玻璃，半导体受益', 'lot_size': 1, 'change_pct': None, 'contract': '沪锡主力'},
        '氧化铝': {'name': '氧化铝', 'full_name': '氧化铝主力', 'price': 2806.0, 'unit': '元/吨', 'category': '基本金属', 'icon': '🏭', 'description': '铝的前身，新能源带动需求', 'lot_size': 20, 'change_pct': None, 'contract': '氧化铝主力'},
    }
    return fallback

def get_metal_advice(name, price, category):
    """金属大白话建议"""
    if category == '贵金属':
        if name == '黄金':
            if price > 900:
                return '金价很高了！历史高位区，追高要谨慎——等回调再进场更划算'
            elif price > 850:
                return '金价处于中高位，当保值工具拿着挺好。但想赚差价的，现在买可能追在山顶'
            else:
                return '金价相对温和，可以考虑分批建仓——黄金长期看是抗通胀的压舱石'
        elif name == '白银':
            return '白银波动比黄金大，适合"有耐心的人"。跌了别慌，涨了别贪'
        elif name == '铂':
            return '铂金跟黄金经常"各走各的路"——汽车销量好它就涨，黄金涨它不一定跟'
    else:
        return '工业金属跟着宏观经济走——经济好它们就涨，经济差它们就跌。适合作为"经济温度计"来观察大盘'
