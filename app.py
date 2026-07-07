"""
NEO — 主应用
Flask后端 + 风险预警 + 双模式交易（模拟盘/实盘）+ 套路识别器
"""
import os
import json
import urllib.request
import urllib.error
import pandas as pd
from flask import Flask, render_template, jsonify, request
from datetime import datetime

from config import ALLOWED_ETF_POOL, SIMULATION, RISK_RULES, STRATEGY_MA, REAL_TRADING, ALLOWED_STOCK_POOL, GOLD_MONITOR
from data import fetch_etf_realtime
from risk_engine import assess_market_risk, detect_scam_patterns, calculate_preservation, alert_check
from analysis import fetch_financial_news
from stock_gold_data import fetch_stock_realtime, get_stock_trend_signal
from metal_data import fetch_metals, METAL_SPECIFICATIONS
from macro_data import fetch_macro_dashboard, get_macro_summary
from position_advisor import position_advice
from backtest_engine import run_backtest
from stress_tester import run_stress_test
from sim_trader import SimTrader
from real_trader import RealTrader

# ============================================================
# AI 配置 — 本地AI + 外接API 双模式，持久化到JSON文件
# ============================================================
AI_PERSONALITY = "你是NEO，NEO的AI助手。说话用大白话，8岁小孩和80岁老奶奶都能听懂。核心使命：保护散户不被割。口头禅：先保住本金再谈赚钱。回答要简短有力，不超过5句话。"

AI_CONFIG_FILE = os.path.expanduser('~/.hermes/neo_ai_settings.json')

def _default_ai_settings():
    """AI配置默认值"""
    return {
        'use_local_ai': True,       # 默认用本地AI
        'local': {
            'base_url': 'http://127.0.0.1:8000/v1',
            'model': 'anthropic-claude-4',
            'api_key': 'sk-xxx'
        },
        'remote': {
            'base_url': 'https://api.openai.com/v1',
            'model': 'gpt-4o',
            'api_key': 'sk-xxx'
        }
    }

def _load_ai_settings():
    """从JSON文件加载AI设置"""
    try:
        if os.path.exists(AI_CONFIG_FILE):
            with open(AI_CONFIG_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            # 合并默认值，防止新增字段丢失
            defaults = _default_ai_settings()
            for k, v in defaults.items():
                if k == 'local' or k == 'remote':
                    saved.setdefault(k, v)
                    if k in saved and isinstance(v, dict):
                        for sk, sv in v.items():
                            saved[k].setdefault(sk, sv)
                else:
                    saved.setdefault(k, v)
            return saved
    except Exception:
        pass
    return _default_ai_settings()

def _save_ai_settings(settings):
    """保存AI设置到JSON文件"""
    try:
        with open(AI_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False

def _get_active_ai_config():
    """获取当前激活的AI配置（本地或外接）"""
    settings = _load_ai_settings()
    if settings.get('use_local_ai'):
        cfg = settings.get('local', {})
        cfg['type'] = 'local'
        cfg['base_url'] = cfg.get('base_url', 'http://127.0.0.1:8000/v1')
        cfg['model'] = cfg.get('model', 'anthropic-claude-4')
        cfg['api_key'] = cfg.get('api_key', 'sk-xxx')
    else:
        cfg = settings.get('remote', {})
        cfg['type'] = 'remote'
        cfg['base_url'] = cfg.get('base_url', 'https://api.openai.com/v1')
        cfg['model'] = cfg.get('model', 'gpt-4o')
        cfg['api_key'] = cfg.get('api_key', 'sk-xxx')
    return cfg

app = Flask(__name__)

# ============================================================
# 双模式交易引擎
# ============================================================
MODE_FILE = os.path.expanduser('~/.hermes/anti_harvest_mode.txt')

# 模拟盘（始终可用）
_sim_trader = SimTrader(initial_capital=SIMULATION['initial_capital'])

# 实盘（按配置初始化）
_real_trader = RealTrader(config={
    'broker': REAL_TRADING.get('broker', 'tiantian'),
    'user': REAL_TRADING.get('user', ''),
    'password': REAL_TRADING.get('password', ''),
    'initial_capital': REAL_TRADING.get('initial_capital', SIMULATION['initial_capital']),
})

def _load_mode():
    """从文件加载当前交易模式"""
    try:
        if os.path.exists(MODE_FILE):
            with open(MODE_FILE, 'r') as f:
                mode = f.read().strip()
            return mode if mode in ('PAPER', 'REAL') else 'PAPER'
    except Exception:
        pass
    return 'PAPER'

def _save_mode(mode):
    """将当前交易模式持久化到文件"""
    try:
        with open(MODE_FILE, 'w') as f:
            f.write(mode)
    except Exception:
        pass

# 启动时加载模式
_current_mode = _load_mode()

def _get_trader():
    """根据当前模式返回对应的交易引擎"""
    return _real_trader if _current_mode == 'REAL' else _sim_trader

def _get_mode_display(mode):
    """返回模式的大白话描述"""
    if mode == 'REAL':
        return '实盘（真金白银，小心点！）'
    return '模拟盘（先练手再说）'

# 扫描缓存
_scan_cache = {}
_SCAN_CACHE_TTL = 180  # 3分钟

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/market/risk')
def api_market_risk():
    """获取市场风险红绿灯"""
    etf_data = _get_all_etf_data()
    risk = assess_market_risk(etf_data)
    return jsonify(risk)

@app.route('/api/etf/list')
def api_etf_list():
    """获取所有ETF实时数据"""
    data = _get_all_etf_data()
    # 模拟盘模式下更新持仓价格（实盘模式下价格从券商拉取）
    if _current_mode == 'PAPER':
        for etf in data:
            _sim_trader.update_position_price(etf['code'], etf.get('price', 0))
    return jsonify(data)

@app.route('/api/trade/mode')
def api_trade_mode_get():
    """获取当前交易模式"""
    trader = _get_trader()
    connected = False
    if _current_mode == 'REAL':
        connected = trader.connected if hasattr(trader, 'connected') else False
    return jsonify({
        'mode': _current_mode,
        'display': _get_mode_display(_current_mode),
        'connected': connected,
    })

@app.route('/api/trade/mode', methods=['POST'])
def api_trade_mode_set():
    """
    切换交易模式
    请求体: {"mode": "PAPER"} 或 {"mode": "REAL"}
    """
    global _current_mode
    data = request.json or {}
    new_mode = data.get('mode', _current_mode).upper()

    if new_mode not in ('PAPER', 'REAL'):
        return jsonify({
            'success': False,
            'reason': '模式不对，传 PAPER（模拟盘）或 REAL（实盘）'
        }), 400
    _current_mode = new_mode
    _save_mode(new_mode)

    connected = False
    if new_mode == 'REAL':
        connected = _real_trader.connected if hasattr(_real_trader, 'connected') else False

    return jsonify({
        'success': True,
        'mode': new_mode,
        'display': _get_mode_display(new_mode),
        'connected': connected,
        'message': f'已切换到{_get_mode_display(new_mode)}'
    })

@app.route('/api/alerts')
def api_alerts():
    """
    持仓警报检查
    可选参数（JSON POST body）:
      - peak_value: 历史最高总资产（用于计算回撤）
      - today: 今天日期（默认 datetime.today().date()）
    如果不传参数，自动从当前持仓构建 portfolio。
    """
    trader = _get_trader()

    # 尝试获取账户和持仓
    account_result = trader.get_account()
    positions = trader.get_positions()

    # 如果返回的是错误列表（如 RealTrader.get_positions 返回 [{'success': False, ...}]）
    if positions and isinstance(positions, list) and len(positions) > 0 and 'success' in positions[0]:
        return jsonify({
            'alerts': [],
            'portfolio': {},
            'message': '暂无持仓数据，先看看你的账户吧！'
        })

    cash = account_result.get('cash', 0)
    stock_positions = account_result.get('stock_positions', [])

    # 计算总资产
    total_value = cash + sum(p.get('current_value', 0) for p in stock_positions)

    # 构建 holdings 列表
    holdings = []
    for p in stock_positions:
        holdings.append({
            'name': p.get('name', '未知'),
            'value': p.get('current_value', 0),
            'buy_date': None,
        })

    # 如果用户通过 POST body 传了 peak_value 或 today，覆盖默认值
    if request.method == 'POST':
        body = request.json or {}
        portfolio = {
            'total_value': total_value,
            'peak_value': body.get('peak_value', total_value),
            'holdings': holdings,
            'today': body.get('today', datetime.today().date()),
        }
    else:
        portfolio = {
            'total_value': total_value,
            'peak_value': total_value,
            'holdings': holdings,
        }

    alerts = alert_check(portfolio)

    return jsonify({
        'alerts': alerts,
        'total_alerts': len(alerts),
        'portfolio': {
            'total_value': round(total_value, 2),
            'cash': round(cash, 2),
            'holdings_count': len(holdings),
        },
        'message': f'检查了{len(holdings)}个持仓，发现了{len(alerts)}条警报' if alerts else '持仓状态还不错，继续观察！'
    })

@app.route('/api/scam/detect', methods=['POST'])
def api_scam_detect():
    """套路识别器 — 输入文字，检测被割信号"""
    data = request.json
    text = data.get('text', '')
    result = detect_scam_patterns(text)
    result['input_text'] = text
    return jsonify(result)

@app.route('/api/preservation/calculate', methods=['POST'])
def api_preservation_calculate():
    """保本计算器"""
    data = request.json
    principal = data.get('principal', 50000)
    stop_loss = data.get('stop_loss_pct', 8) / 100
    take_profit = data.get('take_profit_pct', 15) / 100
    current_pnl = data.get('current_pnl_pct', 0) / 100
    result = calculate_preservation(principal, stop_loss, take_profit, current_pnl)
    return jsonify(result)

@app.route('/api/account')
def api_account():
    """获取账户信息"""
    trader = _get_trader()
    account = trader.get_account()
    positions = trader.get_positions()

    # 处理 RealTrader 返回的错误列表
    if isinstance(positions, list) and len(positions) > 0 and 'success' in positions[0]:
        positions = []

    market_value = sum(p.get('current_value', 0) for p in positions)
    total_capital = account.get('cash', 0) + market_value
    initial_capital = account.get('initial_capital', SIMULATION['initial_capital'])
    pnl = total_capital - initial_capital
    pnl_pct = pnl / initial_capital * 100

    risk_level = 'safe'
    if pnl_pct < -10:
        risk_level = 'danger'
    elif pnl_pct < -8:
        risk_level = 'warning'
    elif pnl_pct < -3:
        risk_level = 'caution'

    return jsonify({
        'cash': round(account.get('cash', 0), 2),
        'market_value': round(market_value, 2),
        'total_capital': round(total_capital, 2),
        'initial_capital': initial_capital,
        'pnl': round(pnl, 2),
        'pnl_pct': round(pnl_pct, 2),
        'risk_level': risk_level,
        'positions_count': len(positions),
    })

@app.route('/api/positions')
def api_positions():
    """获取持仓列表"""
    trader = _get_trader()
    positions = trader.get_positions()

    # 处理 RealTrader 返回的错误列表
    if isinstance(positions, list) and len(positions) > 0 and 'success' in positions[0]:
        return jsonify(positions)

    for p in positions:
        if p.get('pnl_pct') is not None:
            if p['pnl_pct'] >= 0:
                p['color'] = 'green'
            elif p['pnl_pct'] >= -5:
                p['color'] = 'yellow'
            else:
                p['color'] = 'red'
    return jsonify(positions)

@app.route('/api/trade/buy', methods=['POST'])
def api_buy():
    """买入（根据模式走模拟盘或实盘）"""
    trader = _get_trader()
    data = request.json
    code = data.get('code')
    name = data.get('name', '')
    shares = data.get('shares', 100)
    price = data.get('price')
    reason = data.get('reason', '')
    result = trader.buy(code, name, shares, price, reason)
    return jsonify(result)

@app.route('/api/trade/sell', methods=['POST'])
def api_sell():
    """卖出（根据模式走模拟盘或实盘）"""
    trader = _get_trader()
    data = request.json
    code = data.get('code')
    name = data.get('name', '')
    shares = data.get('shares', 100)
    price = data.get('price')
    reason = data.get('reason', '')
    result = trader.sell(code, name, shares, price, reason)
    return jsonify(result)

@app.route('/api/trades')
def api_trades():
    """获取交易记录"""
    trader = _get_trader()
    trades = trader.get_trades(20)
    return jsonify(trades)

@app.route('/api/stats')
def api_stats():
    """获取统计信息（大白话）"""
    trader = _get_trader()
    stats = trader.get_trade_stats()

    # 大白话翻译
    if stats['total_sells'] == 0:
        summary = "还没开始卖，先买再说！"
    elif stats['win_rate'] >= 60:
        summary = "卖了{}次，赢了{}次（{}%），你挺厉害的嘛！".format(
            stats['total_sells'], stats['wins'], stats['win_rate'])
    elif stats['win_rate'] >= 40:
        summary = "卖了{}次，赢了{}次（{}%），还不错，继续加油！".format(
            stats['total_sells'], stats['wins'], stats['win_rate'])
    else:
        summary = "卖了{}次，赢了{}次（{}%），该复盘一下了".format(
            stats['total_sells'], stats['wins'], stats['win_rate'])

    if stats['total_pnl'] > 0:
        summary += "\n总共赚了¥{:.0f}，钱包在变胖！".format(stats['total_pnl'])
    elif stats['total_pnl'] < 0:
        summary += "\n总共亏了¥{:.0f}，相当于少吃了几顿火锅".format(abs(stats['total_pnl']))

    stats['summary'] = summary
    return jsonify(stats)

@app.route('/api/reset', methods=['POST'])
def api_reset():
    """重置交易（模拟盘：清空记录；实盘：全部卖出）"""
    trader = _get_trader()
    result = trader.reset()
    return jsonify(result)

def _call_vllm(messages, max_tokens=4096):
    """调用AI模型（从配置中读取当前激活的AI）"""
    cfg = _get_active_ai_config()
    url = cfg['base_url'].rstrip('/') + '/chat/completions'
    try:
        data = json.dumps({
            'model': cfg['model'],
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': 0.7
        }).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + cfg['api_key']
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            msg = result['choices'][0]['message']
            content = msg.get('content')
            reasoning = msg.get('reasoning')
            # vLLM可能把内容放在 reasoning 而不是 content
            if content:
                return content.strip()
            elif reasoning:
                return reasoning.strip()
            return '（NEO正在思考中...）'
    except Exception as e:
        return f"（NEO正在思考中...）{str(e)}"

@app.route('/api/ai/settings')
def api_ai_settings_get():
    """获取当前AI设置"""
    settings = _load_ai_settings()
    return jsonify({
        'success': True,
        'settings': settings
    })

@app.route('/api/ai/settings', methods=['POST'])
def api_ai_settings_save():
    """保存AI设置（本地AI和外接API）"""
    data = request.json or {}
    # 先读取现有设置，合并新值
    settings = _load_ai_settings()
    
    # 切换本地/外接
    if 'use_local_ai' in data:
        settings['use_local_ai'] = data['use_local_ai']
    
    # 更新本地AI配置
    if 'local' in data:
        if 'base_url' in data['local']:
            settings['local']['base_url'] = data['local']['base_url']
        if 'model' in data['local']:
            settings['local']['model'] = data['local']['model']
        if 'api_key' in data['local']:
            settings['local']['api_key'] = data['local']['api_key']
    
    # 更新外接API配置
    if 'remote' in data:
        if 'base_url' in data['remote']:
            settings['remote']['base_url'] = data['remote']['base_url']
        if 'model' in data['remote']:
            settings['remote']['model'] = data['remote']['model']
        if 'api_key' in data['remote']:
            settings['remote']['api_key'] = data['remote']['api_key']
    
    ok = _save_ai_settings(settings)
    return jsonify({
        'success': ok,
        'message': '✅ AI设置已保存，马上生效！' if ok else '保存成功，配置已更新',
        'settings': settings
    })

def _get_stock_info(scode):
    """根据股票代码获取完整信息 — 使用腾讯行情API (qt.gtimg.cn)"""
    scode = str(scode).replace('.', '')
    if len(scode) < 6:
        return None

    # 确定前缀：沪市 sh，深市 sz
    prefix = ''
    if scode.startswith('6'):
        prefix = 'sh'  # 沪市
    elif scode.startswith(('0', '3')):
        prefix = 'sz'  # 深市
    else:
        # 不确定，两个都试
        for p in ['sh', 'sz']:
            info = _get_stock_info(p + scode)
            if info:
                return info
        return None

    try:
        url = f'https://qt.gtimg.cn/q={prefix}{scode}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=8)
        raw = resp.read().decode('gbk', errors='replace')
        # 腾讯行情格式: "1~贵州茅台~600519~1194.45~1203.00~..."
        if not raw or '~' not in raw:
            return None
        # 提取引号后的数据
        data_str = raw
        if '="' in raw:
            data_str = raw.split('="')[1].rstrip('"')
        parts = data_str.split('~')
        if len(parts) < 40:
            return None
        name = parts[1]
        price = float(parts[3])
        prev_close = float(parts[4])
        change_amt = float(parts[31])  # 涨跌额
        change_pct = float(parts[32])  # 涨跌幅 %
        open_p = float(parts[5])  # 今开
        volume = int(parts[6])  # 成交量 (手)
        high = float(parts[33])  # 最高
        low = float(parts[34])  # 最低
        amount = float(parts[37])  # 成交额 (万元)
        turnover = float(parts[38])  # 换手率 %
        pe = float(parts[39]) if parts[39] else 0
        if pe == 0: pe = float('inf')

        sector = _classify_sector(scode)
        return {
            'code': scode, 'name': name, 'price': round(price, 3),
            'change_pct': round(change_pct, 2), 'change_amt': round(change_amt, 3),
            'open': round(open_p, 3), 'high': round(high, 3), 'low': round(low, 3),
            'prev_close': round(prev_close, 3),
            'volume': volume, 'amount': amount, 'turnover': round(turnover, 2),
            'pe': pe, 'total_market': 0, 'sector': sector,
            'amplitude': round(abs(high - low) / prev_close * 100, 2) if prev_close > 0 else 0,
        }
    except Exception as e:
        print(f'_get_stock_info({prefix}{scode}) error: {e}')
        return None

def _classify_sector(code):
    """根据代码分类板块"""
    if not code: code = ''
    if code.startswith(('600','601','603')): return '主板'
    elif code.startswith('688'): return '科创板'
    elif code.startswith('300'): return '创业板'
    elif code.startswith(('002','001')): return '中小板'
    elif code.startswith('000'): return '深主板'
    elif code.startswith('301'): return '创业板'
    return '其他'

def _search_stocks_by_name(keyword):
    """按名字模糊搜索股票，返回结果列表。
    搜索顺序：东方财富API → 腾讯API → 本地映射表兜底
    """
    results = []
    # 方法1: 东方财富直接搜索
    try:
        search_url = f'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=10&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:0&fields=f12,f14,f2,f3,f4&sort=f2&order=desc&keyword={urllib.parse.quote(keyword)}'
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=8)
        d = json.loads(resp.read().decode())
        dts = d.get('data', {}).get('diff', []) or []
        for item in dts[:10]:
            scode = str(item.get('f12', '')).split('.')[-1]
            sname = str(item.get('f14', ''))
            if scode and keyword in sname:
                info = _get_stock_info(scode)
                if info:
                    results.append(info)
            if len(results) >= 5:
                break
    except Exception:
        pass
    # 方法2: 腾讯搜索
    if not results:
        try:
            search_url = f'https://search.api.t.qq.com/mf/stock/search?query={urllib.parse.quote(keyword)}&ver=3.3&listnum=10'
            req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=8)
            d = json.loads(resp.read().decode())
            items = d.get('list', []) or d.get('data', []) or []
            for item in items[:10]:
                scode = str(item.get('code', item.get('s_code', '')))
                if scode and len(scode) >= 6:
                    info = _get_stock_info(scode)
                    if info:
                        results.append(info)
                if len(results) >= 5:
                    break
        except Exception:
            pass
    # 方法3: 本地映射表兜底
    if not results:
        try:
            from stock_names import search_stock_by_name as _local_search
            local_hits = _local_search(keyword)
            for code, name in local_hits:
                info = _get_stock_info(code)
                if info:
                    results.append(info)
                if results:
                    break
        except Exception:
            pass
    return results[:5]

@app.route('/api/stock/search', methods=['POST'])
def api_stock_search():
    """股票搜索 — 支持股票代码精确查询 + 名字模糊查询"""
    data = request.json or {}
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'success': False, 'reason': '输入个股票代码或名字'}), 400

    # 纯数字或带点号的代码 = 精确查询
    if query.replace('.', '').isdigit():
        info = _get_stock_info(query)
        if info:
            return jsonify({'success': True, 'count': 1, 'results': [info]})
        return jsonify({'success': False, 'reason': f'代码 "{query}" 没查到，确认一下是不是6位数字？'})

    # 包含数字但不是纯数字 = 可能是"山东创新"或"豪美"等名字
    # 或者就是纯中文 = 名字模糊查询
    results = _search_stocks_by_name(query)
    if results:
        return jsonify({'success': True, 'count': len(results), 'results': results})

    return jsonify({
        'success': False,
        'reason': f'"{query}" 没查到。试试输入完整的6位股票代码（如 600519）或股票名字（如 茅台、宁德时代）'
    })
@app.route('/api/news/list')
def api_news_list():
    """获取财经新闻列表"""
    news = fetch_financial_news(15)
    return jsonify({
        'success': True,
        'news': news,
        'count': len(news),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trend/analysis')
def api_trend_analysis():
    """获取市场趋势分析（技术指标 + 大白话判断）"""
    etf_data = _get_all_etf_data()
    results = []
    for etf in etf_data:
        code = etf['code']
        # 生成简单的趋势判断
        change = etf.get('change_pct', 0)
        trend_signal = _simple_trend_signal(change)
        results.append({
            'code': code,
            'name': etf['name'],
            'price': etf['price'],
            'change_pct': change,
            'trend': trend_signal,
        } if trend_signal != '加载中...' else {
            'code': code,
            'name': etf['name'],
            'price': etf['price'],
            'change_pct': change,
            'trend': '🟡 震荡 — 横着走，别瞎动',
        })
    
    # 综合判断
    green_count = sum(1 for r in results if '🟢' in r['trend'])
    red_count = sum(1 for r in results if '🔴' in r['trend'])
    if green_count > red_count + 2:
        summary = '🟢 整体偏暖 — 市场在升温，可以适当关注'
    elif red_count > green_count + 2:
        summary = '🔴 整体偏冷 — 市场有点凉，别急着冲'
    else:
        summary = '🟡 整体震荡 — 涨跌都有，观望为主'
    
    return jsonify({
        'success': True,
        'etf_trends': results,
        'summary': summary,
        'timestamp': datetime.now().isoformat()
    })

def _simple_trend_signal(change_pct):
    """根据涨跌幅简单判断趋势"""
    if change_pct > 1.5:
        return '🟢 偏暖 — 市场在升温，可以关注'
    elif change_pct > 0.5:
        return '🟢 微暖 — 小涨，不急不躁'
    elif change_pct < -1.5:
        return '🔴 偏冷 — 市场有点凉，别急着冲'
    elif change_pct < -0.5:
        return '🟡 微冷 — 小跌，观望为主'
    else:
        return '🟡 震荡 — 横着走，别瞎动'

@app.route('/api/ai/chat', methods=['POST'])
def api_ai_chat():
    """AI Agent聊天接口 — 带新闻+趋势+账户上下文"""
    data = request.json or {}
    user_msg = data.get('message', '')
    
    # 获取所有上下文数据
    trader = _get_trader()
    account = trader.get_account()
    positions = trader.get_positions()
    
    # 处理 RealTrader返回的错误列表
    if isinstance(positions, list) and len(positions) > 0 and 'success' in positions[0]:
        positions = []
    
    # 市场数据
    etf_data = _get_all_etf_data()
    market_info = []
    for etf in etf_data:
        market_info.append(f"- {etf['name']}: ¥{etf['price']}, 涨跌{etf['change_pct']:.1f}%")
    
    # 财经新闻
    news = fetch_financial_news(8)
    news_text = ''
    for n in news:
        news_text += f"• {n.get('title', '')}（{n.get('source', '')}）: {n.get('summary', '')}\n"
    
    # 趋势分析
    trends = []
    for etf in etf_data:
        change = etf.get('change_pct', 0)
        trend_signal = _simple_trend_signal(change)
        trends.append(f"- {etf['name']}: {trend_signal}")
    
    # 账户信息
    cash = account.get('cash', 0)
    total = account.get('cash', 0)
    
    # 构建系统消息 — 给AI更多上下文
    system_msg = f"""{AI_PERSONALITY}

当前时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}
当前模式：{'模拟盘' if _current_mode == 'PAPER' else '实盘'}

你的账户信息：
- 现金：¥{cash:,.0f}
- 总资产：¥{total:,.0f}

市场快照：
{'\n'.join(market_info)}

近期财经新闻（前8条）：
{news_text}

市场趋势判断：
{'\n'.join(trends)}

请根据以上信息，用大白话回答用户的问题。如果用户问的是"买"或"卖"，给出具体建议并说明理由。回答要简洁，不超过5句话。"""
    
    # 调用vLLM
    messages = [
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': user_msg}
    ]
    
    response = _call_vllm(messages)
    
    return jsonify({
        'success': True,
        'response': response,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/ai/analyze_market', methods=['POST'])
def api_ai_analyze_market():
    """AI综合分析 — 新闻+趋势+市场数据"""
    etf_data = _get_all_etf_data()
    news = fetch_financial_news(6)
    
    market_summary = []
    for etf in etf_data:
        change = etf.get('change_pct', 0)
        direction = '涨' if change > 0 else ('跌' if change < 0 else '平')
        trend_signal = _simple_trend_signal(change)
        market_summary.append(f"{etf['name']}({etf['code']}）：{direction}{abs(change):.1f}%，趋势：{trend_signal}")
    
    news_summary = ''
    for n in news:
        news_summary += f"• {n.get('title', '')}: {n.get('summary', '')}\n"
    
    user_msg = f"""请综合以下信息，用大白话告诉我：
1. 现在整体市场是什么情况？
2. 最近有什么重要新闻？
3. 现在是该买还是该卖？
4. 有什么风险？

市场数据：
{'\n'.join(market_summary)}

近期新闻：
{news_summary}"""
    
    system_msg = f"{AI_PERSONALITY}\n\n用大白话回答，8岁小孩和80岁老奶奶都能听懂。回答要简洁有力。"
    
    messages = [
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': user_msg}
    ]
    
    response = _call_vllm(messages, max_tokens=1500)
    
    return jsonify({
        'success': True,
        'response': response,
        'market_data': etf_data,
        'news': news
    })

def _get_all_etf_data():
    """获取所有ETF数据（带缓存），非交易日用历史参考价兜底"""
    now = datetime.now()
    cache_key = now.strftime('%Y%m%d_H%M')

    if cache_key in _scan_cache:
        return _scan_cache[cache_key]

    etf_codes = [e['code'] for e in ALLOWED_ETF_POOL]
    raw_data = fetch_etf_realtime(etf_codes)

    results = []
    for etf in ALLOWED_ETF_POOL:
        code = etf['code']
        rt = raw_data.get(code, {})
        # 如果AKShare返回的价格是0（周末/非交易日），用历史参考价兜底
        price = rt.get('price', 0)
        change = rt.get('change_pct', 0)
        if price == 0:
            price = etf.get('ref_price', 0)
            change = etf.get('ref_change', 0)
        results.append({
            'code': code,
            'name': rt.get('name', etf['name']),
            'category': etf['category'],
            'price': price,
            'change_pct': change,
            'volume': rt.get('volume', 0),
            'high': rt.get('high', 0) or price,
            'low': rt.get('low', 0) or price,
            'prev_close': rt.get('prev_close', 0) or price,
        })

    _scan_cache[cache_key] = results
    return results

@app.route('/api/stock/list')
def api_stock_list():
    """获取A股核心股票实时行情"""
    raw_data = fetch_stock_realtime()
    results = []
    for stock in ALLOWED_STOCK_POOL:
        code = stock['code']
        rt = raw_data.get(code, {})
        price = rt.get('price', 0)
        change = rt.get('change_pct', 0)
        trend_signal = get_stock_trend_signal(change)
        results.append({
            'code': code,
            'name': rt.get('name', stock['name']),
            'category': stock['category'],
            'sector': stock['sector'],
            'price': price,
            'change_pct': change,
            'high': rt.get('high', 0),
            'low': rt.get('low', 0),
            'volume': rt.get('volume', 0),
            'trend': trend_signal,
        })
    return jsonify(results)

@app.route('/api/gold/list')
@app.route('/api/gold/prices')
@app.route('/api/metal/list')
def api_metal_list():
    """获取贵金属 + 基本金属实时价格"""
    metal_data = fetch_metals()
    results = []
    for name, d in metal_data.items():
        results.append({
            'code': d.get('contract', name),
            'name': d['name'],
            'price': d['price'],
            'change_pct': d.get('change_pct'),
            'unit': d.get('unit', ''),
            'category': d.get('category', '贵金属'),
            'icon': d.get('icon', '📊'),
            'description': d.get('description', ''),
        })
    return jsonify(results)

@app.route('/api/macro/dashboard')
def api_macro_dashboard():
    """宏观仪表盘"""
    import math
    macro_data = fetch_macro_dashboard()
    summary = get_macro_summary(macro_data)
    # 清洗 NaN 值（JSON标准里 NaN 不是合法值，浏览器会报错）
    def sanitize(obj):
        if isinstance(obj, float) and math.isnan(obj):
            return None
        elif isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [sanitize(v) for v in obj]
        return obj
    return jsonify({
        'data': sanitize(macro_data),
        'summary': summary,
        'updated_at': macro_data.get('updated_at', '—'),
    })

@app.route('/api/position/advice', methods=['POST'])
def api_position_advice():
    """仓位管理建议器"""
    data = request.json or {}
    total_capital = data.get('total_capital', 50000)
    positions = data.get('positions', [])
    market_risk = data.get('market_risk', {'level': 'yellow', 'text': '—'})
    result = position_advice(total_capital, positions, market_risk)
    return jsonify(result)

@app.route('/api/backtest', methods=['POST'])
def api_backtest():
    """AI 模拟回测"""
    data = request.json or {}
    asset_code = data.get('asset_code', '510300')
    asset_name = data.get('asset_name', '沪深300ETF')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    initial_capital = data.get('initial_capital', 10000)
    strategy = data.get('strategy', 'balanced')
    result = run_backtest(asset_code, asset_name, start_date, end_date,
                         initial_capital, strategy)
    return jsonify(result)

@app.route('/api/stress-test', methods=['POST'])
def api_stress_test():
    """防套路压力测试"""
    data = request.json or {}
    asset_code = data.get('asset_code', '510300')
    asset_name = data.get('asset_name', '沪深300ETF')
    days = data.get('days', 365)
    result = run_stress_test(asset_code, asset_name, days)
    return jsonify(result)

if __name__ == '__main__':
    mode_display = _get_mode_display(_current_mode)
    print(f"🛡️ NEO（NEO）启动中...")
    print(f"📊 当前模式：{mode_display}")
    print(f"🌐 打开浏览器访问: http://127.0.0.1:8700")
    import threading
    def _open_browser():
        import time, webbrowser
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:8700")
        print("🔖 浏览器已自动打开")
    threading.Thread(target=_open_browser, daemon=True).start()
    app.run(host='0.0.0.0', port=8700, threaded=True, debug=False)
