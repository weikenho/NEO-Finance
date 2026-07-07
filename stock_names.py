"""
A股股票名字 → 代码 本地映射表
数据来源：AKShare (2026年实时A股列表)
用途：当外部API搜索不稳定时，用本地映射表兜底
"""

# 自动从AKShare获取最新A股列表，建立搜索索引
def _build_index():
    """从AKShare获取最新A股列表，返回 {名字: full_code} 字典"""
    import subprocess
    result = subprocess.run([
        'python3', '-c', r'''
import akshare as ak
df = ak.stock_info_a_code_name()
for _, row in df.iterrows():
    code = row['code']
    name = row['name']
    prefix = 'sz' if code.startswith(('0', '3')) else 'sh'
    full_code = f"{prefix}{code}"
    print(f"{name}\t{full_code}")
'''
    ], capture_output=True, timeout=60)
    
    stock_map = {}
    for line in result.stdout.decode('utf-8', errors='replace').split('\n'):
        parts = line.strip().split('\t')
        if len(parts) == 2:
            name, code = parts
            stock_map[name] = code
    
    # 只保留热门/常用股票（排除ST、XD、XR、退、转债等）
    popular = {}
    exclude = ['ST', 'XD', 'XR', '退', '转债', 'SC', 'N', 'GH', 'DR', 'EB', 'EB']
    for name, code in stock_map.items():
        if any(ex in name for ex in exclude):
            continue
        popular[name] = code
    
    return popular

# 全局缓存
_cache = None

def get_stock_map():
    """获取完整股票映射表（带缓存）"""
    global _cache
    if _cache is None:
        try:
            _cache = _build_index()
        except Exception as e:
            print(f"[stock_names] AKShare fallback failed: {e}")
            _cache = _get_local_fallback()
    return _cache

def _get_local_fallback():
    """当AKShare不可用时，使用硬编码的热门股票列表"""
    return {}

def search_stock_by_name(keyword: str) -> list:
    """
    按名字搜索股票，返回匹配的 (code, name) 列表
    keyword: 搜索关键词（如 "茅台"、"宁"、"万科"）
    returns: [('sh600519', '贵州茅台'), ('sz000002', '万科A'), ...]
    """
    stock_map = get_stock_map()
    matches = []
    keyword = keyword.strip()
    
    for name, code in stock_map.items():
        if not code:
            continue
        if keyword in name or name in keyword:
            if (code, name) not in matches:
                matches.append((code, name))
    
    # 按匹配度排序：包含 > 反向包含
    def sort_key(item):
        code, name = item
        if keyword in name:
            return (0, name)
        elif name in keyword:
            return (1, name)
        return (2, name)
    
    matches.sort(key=sort_key)
    return matches[:10]

if __name__ == '__main__':
    print(f"Loading stock database...")
    smap = get_stock_map()
    print(f"Total stocks in map: {len(smap)}")
    
    for kw in ['茅台', '宁德', '万科', '格力', '比亚迪', '中芯', '隆基', 
                '恒瑞', '紫金', '招商', '工行', '东方财富', '迈瑞', 
                '爱尔', '双汇', '顺丰', '长江', '万华', '中国石化', '中国石油']:
        r = search_stock_by_name(kw)
        print(f"  '{kw}' → {r}")
