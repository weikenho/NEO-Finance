# ============================================================
# NEO — 多语言翻译模块 / i18n Module
# ============================================================
# 使用方式:
#   from lang import T
#   print(T.warm_trend)  # 返回当前语言的值
#
# 切换语言:
#   from lang import set_lang
#   set_lang('en') 或 set_lang('zh')
#
# 获取当前语言:
#   from lang import get_lang
#   get_lang() -> 'zh' 或 'en'
# ============================================================

_CURRENT_LANG = 'zh'


def set_lang(lang):
    global _CURRENT_LANG
    _CURRENT_LANG = lang if lang in ('zh', 'en') else 'zh'


def get_lang():
    return _CURRENT_LANG


class _LangAttr:
    """通过属性访问翻译键，例如 T.hello"""
    def __init__(self, zh, en):
        self.zh = zh
        self.en = en
    def __str__(self):
        return self.zh if _CURRENT_LANG == 'zh' else self.en
    def __repr__(self):
        return str(self)

    # 支持在 f-string 中使用
    def __format__(self, fmt):
        return format(str(self), fmt)

    # 支持 + 拼接
    def __add__(self, other):
        return str(self) + other
    def __radd__(self, other):
        return other + str(self)

    # 支持 json 序列化
    def __iter__(self):
        yield from iter(str(self))
    def __len__(self):
        return len(str(self))

    # 支持 list/dict 中直接使用
    def to_json(self):
        return str(self)


class _Translator:
    """空壳命名空间，动态挂载翻译属性"""
    pass

T = _Translator()


def _register(name, zh, en):
    setattr(T, name, _LangAttr(zh, en))


# ============================================================
# 以下为所有翻译键
# ============================================================

# --- 系统启动 ---
_register('sys_start', '🛡️ NEO（NEO）启动中...', '🛡️ NEO (Financial Guardian) starting...')
_register('sys_mode', '📊 当前模式', '📊 Current mode')
_register('sys_browser', '🌐 打开浏览器访问', '🌐 Open browser at')
_register('sys_browser_opened', '🔖 浏览器已自动打开', '🔖 Browser auto-opened')

# --- 交易模式 ---
_register('mode_paper', '模拟盘', 'Paper Trading')
_register('mode_real', '实盘', 'Live Trading')
_register('mode_paper_desc', '模拟盘（先练手再说）', 'Paper Trading (practice first)')
_register('mode_real_desc', '实盘（真金白银，小心点！）', 'Live Trading (real money, watch out!)')
_register('mode_switch_fail', '模式不对，传 PAPER（模拟盘）或 REAL（实盘）', 'Invalid mode. Use PAPER or REAL.')

# --- 账户 ---
_register('acct_no_holding', '暂无持仓数据，先看看你的账户吧！', 'No holdings yet. Check your account!')
_register('acct_checking', '检查了', 'Checked')
_register('acct_alerts_found', '个持仓，发现了', 'holdings, found')
_register('acct_alerts_ok', '条警报', 'alerts')
_register('acct_no_alerts', '持仓状态还不错，继续观察！', 'Holdings look good, keep watching!')

# --- 统计 ---
_register('stats_no_sell', '还没开始卖，先买再说！', 'Haven\'t sold yet — buy first!')
_register('stats_sold_awesome', '卖了{}次，赢了{}次（{}%），你挺厉害的嘛！', 'Sold {} times, won {} ({}) — not bad at all!')
_register('stats_sold_ok', '卖了{}次，赢了{}次（{}%），还不错，继续加油！', 'Sold {} times, won {} ({}) — keep going!')
_register('stats_sold_review', '卖了{}次，赢了{}次（{}%），该复盘一下了', 'Sold {} times, won {} ({}) — time to review')
_register('stats_earned', '\n总共赚了¥{:.0f}，钱包在变胖！', '\nTotal profit ¥{:.0f}, wallet is getting fatter!')
_register('stats_lost', '\n总共亏了¥{:.0f}，相当于少吃了几顿火锅', '\nTotal loss ¥{:.0f}, like skipping a few hotpot dinners')

# --- AI ---
_register('ai_thinking', '（NEO正在思考中...）', '(NEO is thinking...)')
_register('ai_settings_saved', '✅ AI设置已保存，马上生效！', '✅ AI settings saved, active now!')
_register('ai_settings_ok', '保存成功，配置已更新', 'Saved, config updated')

# --- 股票搜索 ---
_register('stock_search_empty', '输入个股票代码或名字', 'Enter a stock code or name')
_register('stock_search_not_found', '代码 "{query}" 没查到，确认一下是不是6位数字？', 'Code "{query}" not found. Is it a 6-digit number?')
_register('stock_search_query_not_found', '"{query}" 没查到。试试输入完整的6位股票代码（如 600519）或股票名字（如 茅台、宁德时代）', '"{query}" not found. Try a 6-digit stock code (e.g. 600519) or name (e.g. Moutai, CATL)')

# --- 趋势判断 ---
_register('trend_loading', '加载中...', 'Loading...')
_register('trend_warm', '🟢 偏暖 — 市场在升温，可以关注', '🟢 Warm — market is heating up, worth watching')
_register('trend_cold', '🔴 偏冷 — 市场有点凉，别急着冲', '🔴 Cool — market is cooling down, don\'t rush in')
_register('trend_warm_slight', '🟢 微暖 — 小涨，不急不躁', '🟢 Slightly warm — small gain, stay calm')
_register('trend_cold_slight', '🟡 微冷 — 小跌，观望为主', '🟡 Slightly cool — small drop, hold and watch')
_register('trend_flat', '🟡 震荡 — 横着走，别瞎动', '🟡 Flat — sideways movement, hold steady')
_register('trend_warm_overall', '🟢 整体偏暖 — 市场在升温，可以适当关注', '🟢 Overall warm — market is heating up')
_register('trend_cold_overall', '🔴 整体偏冷 — 市场有点凉，别急着冲', '🔴 Overall cool — market is cooling down')
_register('trend_flat_overall', '🟡 整体震荡 — 涨跌都有，观望为主', '🟡 Overall flat — mixed signals, hold and watch')
_register('trend_no_data', '暂无数据', 'No data yet')

# --- 成交量 ---
_register('vol_heavy', '放量', 'Heavy')
_register('vol_light', '缩量', 'Light')
_register('vol_flat', '平量', 'Flat')

# --- 风险等级 ---
_register('risk_safe', '稳得很', 'Very safe')
_register('risk_caution', '有点小波动，留意一下', 'Slight fluctuation, stay alert')
_register('risk_warning', '亏得有点多了，该动手了', 'Loss is growing, take action')
_register('risk_danger', '钱包在流血，赶紧处理', 'Wallet is bleeding, act now')
_register('risk_cooldown', '先歇口气', 'Take a breather')

# --- 宏观分析 ---
_register('macro_pmi_high', '📈 中国制造业PMI {val}，高于52说明经济在"加速跑"', '📈 China PMI {val}, above 52 means economy is "accelerating"')
_register('macro_pmi_mid', '📊 中国制造业PMI {val}，刚过50说明经济在"扩产"', '📊 China PMI {val}, just above 50 means economy is "expanding"')
_register('macro_pmi_low', '📉 中国制造业PMI {val}，快接近50的"分水岭"了', '📉 China PMI {val}, approaching the 50 "watershed"')
_register('macro_pmi_decline', '📉 中国制造业PMI {val}，跌破50说明经济在"缩产"', '📉 China PMI {val}, below 50 means economy is "contracting"')
_register('macro_fed_rate', '💵 美联储利率 {val}%，利率高说明美元"贵"，资金容易回流美国', '💵 Fed rate {val}%, high rate means USD is "expensive", capital flows to US')
_register('macro_inflow_big', '💰 主力资金今天大幅净流入 {val}亿，大钱在进场', '💰 Main capital net inflow ¥{val}B, big money entering')
_register('macro_inflow_small', '💰 主力资金今天净流入 {val}亿，大钱在慢慢进', '💰 Main capital net inflow ¥{val}B, big money trickling in')
_register('macro_outflow_small', '💸 主力资金今天小幅净流出 {val}亿，大钱在慢慢撤', '💸 Main capital net outflow ¥{val}B, big money slowly leaving')
_register('macro_outflow_big', '💸 主力资金今天大幅净流出 {val}亿，大钱在跑路', '💸 Main capital net outflow ¥{val}B, big money fleeing')
_register('macro_panic', '😱 市场恐慌指数(QVIX) {val}（{level}）', '😱 Market panic index (QVIX) {val} ({level})')
_register('macro_loading', '📊 宏观数据加载中，请稍后再看', '📊 Macro data loading, check back soon')

# --- 回测 ---
_register('bt_buy_signal', 'AI判断金叉，买入信号', 'AI signals golden cross, BUY')
_register('bt_sell_profit', '盈利{ret:.1f}%，AI说"落袋为安"', 'Profit {ret:.1f}%, AI says "lock it in"')
_register('bt_sell_loss', '亏损{ret:.1f}%，AI说"别跟它犟了"', 'Loss {ret:.1f}%, AI says "cut the loss"')
_register('bt_close', '期末强制平仓', 'Period-end forced close')
_register('bt_buy_strategy', '连涨{days}天+放量，AI说"该上了"', 'Up {days} days + volume surge, AI says "get on board"')
_register('bt_sell_down', '连跌{days}天，AI说"先出来看看"', 'Down {days} days, AI says "step out and see"')

# ============================================================
# 前端 UI 翻译字典 (供 JS 使用)
# ============================================================

UI_TEXTS = {
    'zh': {
        'page_title': '🛡️ NEO — 财经防护仪表盘',
        'tagline': '保护散户不被割',
        'brand': 'NEO 防护仪表盘',
        'tab_market': '📊 行情',
        'tab_holdings': '💼 持仓',
        'tab_tools': '🧰 工具箱',
        'tab_news': '📰 新闻',
        'tab_macro': '🌍 宏观',
        'tab_metals': '🥇 金属',
        'risk_title': '市场风险红绿灯',
        'no_risk_data': '正在读取市场温度...',
        'etf_title': '实时行情',
        'etf_loading': '加载中...',
        'etf_refresh': '刷新',
        'holdings_title': '我的持仓',
        'no_holdings': '还没有持仓？点击上方买入按钮开始！',
        'wallet_total': '总资产',
        'wallet_cash': '现金',
        'wallet_pnl': '总盈亏',
        'wallet_return': '收益率',
        'btn_buy': '买入',
        'btn_sell': '卖出',
        'btn_reset': '重置',
        'btn_check': '检查警报',
        'trade_history': '交易记录',
        'no_trades': '还没有交易记录',
        'stats_title': '统计',
        'scam_title': '套路识别器',
        'scam_placeholder': '粘贴一段销售话术、投资广告、或朋友给你发的"内部消息"...',
        'scam_btn': '检测',
        'scam_safe': '看起来还行，但别忘了：没有稳赚不赔的生意',
        'scam_caution': '有点味道了，建议多看两眼',
        'scam_warning': '套路味很重！小心点！',
        'scam_danger': '极大概率在割你，跑！',
        'calc_title': '保本计算器',
        'calc_placeholder_cost': '买入单价（元）',
        'calc_placeholder_qty': '数量',
        'calc_placeholder_target': '目标收益率（%）',
        'calc_btn': '计算',
        'calc_result': '计算结果',
        'calc_cost': '总成本',
        'calc_profit_target': '目标盈利',
        'calc_selling_price': '保本卖出价',
        'calc_take_profit': '止盈价',
        'calc_stop_loss': '止损价（-8%）',
        'calc_tips': '小贴士',
        'news_title': '财经新闻',
        'news_loading': '正在抓取新闻...',
        'macro_title': '宏观仪表盘',
        'macro_loading': '宏观数据加载中...',
        'metals_title': '贵金属 & 基本金属',
        'metals_loading': '金属行情加载中...',
        'ai_title': 'NEO 助手',
        'ai_placeholder': '问NEO任何问题...',
        'ai_status': '在线',
        'ai_quick_ask1': '今天该买还是卖？',
        'ai_quick_ask2': '大盘怎么看？',
        'ai_quick_ask3': '黄金值得入手吗？',
        'ai_quick_ask4': '我的持仓怎么样？',
        'mode_paper': '模拟盘',
        'mode_real': '实盘',
        'lang_zh': '🇨🇳 中文',
        'lang_en': '🇬🇧 English',
        'system_notice': '系统公告',
        'etf_col_code': '代码',
        'etf_col_name': '名称',
        'etf_col_price': '最新价',
        'etf_col_change': '涨跌幅',
        'etf_col_volume': '成交量',
        'etf_col_trend': '趋势',
    },
    'en': {
        'page_title': '🛡️ NEO — Financial Guardian Dashboard',
        'tagline': 'Protecting Retail Investors',
        'brand': 'NEO Dashboard',
        'tab_market': '📊 Market',
        'tab_holdings': '💼 Holdings',
        'tab_tools': '🧰 Tools',
        'tab_news': '📰 News',
        'tab_macro': '🌍 Macro',
        'tab_metals': '🥇 Metals',
        'risk_title': 'Market Risk Traffic Light',
        'no_risk_data': 'Reading market temperature...',
        'etf_title': 'Live Quotes',
        'etf_loading': 'Loading...',
        'etf_refresh': 'Refresh',
        'holdings_title': 'My Holdings',
        'no_holdings': 'No holdings? Click Buy above to get started!',
        'wallet_total': 'Total Assets',
        'wallet_cash': 'Cash',
        'wallet_pnl': 'Total P&L',
        'wallet_return': 'Return Rate',
        'btn_buy': 'Buy',
        'btn_sell': 'Sell',
        'btn_reset': 'Reset',
        'btn_check': 'Check Alerts',
        'trade_history': 'Trade History',
        'no_trades': 'No trades yet',
        'stats_title': 'Statistics',
        'scam_title': 'Pattern Detector',
        'scam_placeholder': 'Paste a sales pitch, investment ad, or "inside tip" from a friend...',
        'scam_btn': 'Detect',
        'scam_safe': 'Looks okay, but remember: no sure-thing investment exists',
        'scam_caution': 'Smells fishy — double check',
        'scam_warning': 'Strong pattern detected! Watch out!',
        'scam_danger': 'High probability of a trap — RUN!',
        'calc_title': 'Break-even Calculator',
        'calc_placeholder_cost': 'Buy Price (¥)',
        'calc_placeholder_qty': 'Quantity',
        'calc_placeholder_target': 'Target Return (%)',
        'calc_btn': 'Calculate',
        'calc_result': 'Result',
        'calc_cost': 'Total Cost',
        'calc_profit_target': 'Target Profit',
        'calc_selling_price': 'Break-even Price',
        'calc_take_profit': 'Take-Profit Price',
        'calc_stop_loss': 'Stop-Loss Price (-8%)',
        'calc_tips': 'Tips',
        'news_title': 'Financial News',
        'news_loading': 'Fetching news...',
        'macro_title': 'Macro Dashboard',
        'macro_loading': 'Macro data loading...',
        'metals_title': 'Precious & Base Metals',
        'metals_loading': 'Metal quotes loading...',
        'ai_title': 'NEO Assistant',
        'ai_placeholder': 'Ask NEO anything...',
        'ai_status': 'Online',
        'ai_quick_ask1': 'Buy or sell today?',
        'ai_quick_ask2': 'How\'s the market?',
        'ai_quick_ask3': 'Is gold worth buying?',
        'ai_quick_ask4': 'How are my holdings?',
        'mode_paper': 'Paper',
        'mode_real': 'Live',
        'lang_zh': '🇨🇳 中文',
        'lang_en': '🇬🇧 English',
        'system_notice': 'System Notice',
        'etf_col_code': 'Code',
        'etf_col_name': 'Name',
        'etf_col_price': 'Price',
        'etf_col_change': 'Change %',
        'etf_col_volume': 'Volume',
        'etf_col_trend': 'Trend',
    }
}
