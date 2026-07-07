"""
NEO（NEO）- 配置文件
"""

# ============================================================
# ETF 监控池（含历史参考价，周末/非交易日用这个兜底）
# ============================================================
ALLOWED_ETF_POOL = [
    {'code': '510300', 'name': '沪深300ETF', 'category': '大盘', 'ref_price': 4.035, 'ref_change': 0.42},
    {'code': '510500', 'name': '中证500ETF', 'category': '中盘', 'ref_price': 6.249, 'ref_change': -0.18},
    {'code': '159915', 'name': '创业板ETF', 'category': '成长', 'ref_price': 2.036, 'ref_change': 1.23},
    {'code': '588000', 'name': '科创50ETF', 'category': '科技', 'ref_price': 1.119, 'ref_change': -0.72},
    {'code': '510880', 'name': '红利ETF', 'category': '稳健', 'ref_price': 2.993, 'ref_change': 0.15},
    {'code': '513100', 'name': '纳指ETF', 'category': '海外', 'ref_price': 2.158, 'ref_change': 0.56},
    {'code': '513500', 'name': '标普500ETF', 'category': '海外', 'ref_price': 1.483, 'ref_change': 0.33},
    {'code': '159941', 'name': '消费ETF', 'category': '行业', 'ref_price': 1.614, 'ref_change': -0.41},
]

# ============================================================
# 模拟盘配置
# ============================================================
SIMULATION = {
    'initial_capital': 50000,   # 初始虚拟资金
    'mode': 'PAPER',            # PAPER=模拟盘, REAL=实盘
    'daily_reset': True,        # 每天重置未成交挂单
    'commission_rate': 0.0005,  # 模拟佣金率 0.05%
}

# ============================================================
# 实盘交易配置（easytrader — 天天基金 / 券商端）
# ============================================================
REAL_TRADING = {
    'enabled': False,           # 开关：True 启动实盘，False 用模拟盘
    'use_easytrader': True,     # 使用 easytrader 库
    'broker': 'tiantian',       # 经纪人：'tiantian' (天天基金) / 'hht' (华泰) / 'gtja' (国泰君安)
    # 以下路径根据 easytrader.setup(broker, ...) 自动加载
    'user_path': '',            # 用户目录，easytrader 存放 cookie / JSON 的地方
    'api_threaded': True,       # 开启多线程 API 调用（适合多只 ETF 同时挂单）
    'pre_market_minutes': 5,    # 开盘前 N 分钟开始轮询挂单
    'max_retry': 3,             # 挂单失败最大重试次数
    'retry_interval_sec': 2,    # 重试间隔（秒）
}

# ============================================================
# 风控规则
# ============================================================
RISK_RULES = {
    'single_stop_loss': 0.08,          # 单只止损 8%
    'single_take_profit': 0.15,        # 单只止盈 15%
    'total_stop_loss': 0.10,           # 总回撤 10% 触发冷静期
    'cooldown_days': 7,                # 冷静期 7 天
    'min_hold_days': 3,                # 最小持有 3 天（避免频繁交易吃佣金）
    'max_position_pct': 0.3,           # 单只最大仓位 30%
    'max_drawdown_alert': 0.12,        # 总回撤超 12% 弹出"该跑了"提醒
    'position_concentration_alert': 0.6,  # 单只占总仓位超 60% 触发"鸡蛋全在一个篮子"提醒
    'holding_stale_days': 14,         # 单只连续持有超过 14 天还没动静，触发"是不是忘了它"提醒
}

# ============================================================
# 策略参数（均线交叉 + 成交量）
# ============================================================
STRATEGY_MA = {
    'short_period': 10,      # 短期均线 MA10
    'long_period': 30,       # 长期均线 MA30
    'volume_multiplier': 1.5, # 成交量放大 1.5 倍（相对 MA10 日均量）
}

# ============================================================
# 风险等级阈值（大白话）
# ============================================================
RISK_LEVELS = {
    'safe': {'min': 0, 'emoji': '😊', 'text': '稳得很', 'color': '#27ae60'},
    'caution': {'min': -0.03, 'emoji': '⚠️', 'text': '有点小波动，留意一下', 'color': '#f39c12'},
    'warning': {'min': -0.08, 'emoji': '🟠', 'text': '亏得有点多了，该动手了', 'color': '#e67e22'},
    'danger': {'min': -0.10, 'emoji': '🔴', 'text': '钱包在流血，赶紧处理', 'color': '#e74c3c'},
    'cooldown': {'min': -1, 'emoji': '🛑', 'text': '先歇口气', 'color': '#c0392b'},
}

# ============================================================
# A股核心监控池 — 散户最容易被割的股票
# 按类别分组：蓝筹/科技/新能源/消费/医药/热门
# ============================================================
ALLOWED_STOCK_POOL = [
    # 蓝筹大白马 — 散户最常买的
    {'code': '600519', 'name': '贵州茅台', 'category': '蓝筹', 'sector': '消费'},
    {'code': '601318', 'name': '宁德时代', 'category': '蓝筹', 'sector': '新能源'},
    {'code': '600036', 'name': '招商银行', 'category': '蓝筹', 'sector': '金融'},
    {'code': '600276', 'name': '恒瑞医药', 'category': '蓝筹', 'sector': '医药'},
    {'code': '601166', 'name': '兴业银行', 'category': '蓝筹', 'sector': '金融'},
    {'code': '600031', 'name': '三一重工', 'category': '蓝筹', 'sector': '制造业'},
    {'code': '600887', 'name': '伊利股份', 'category': '蓝筹', 'sector': '消费'},
    {'code': '601899', 'name': '紫金矿业', 'category': '蓝筹', 'sector': '资源'},
    # 科技热门股 — 波动大，最容易被割
    {'code': '603986', 'name': '兆易创新', 'category': '科技', 'sector': '半导体'},
    {'code': '600584', 'name': '长电科技', 'category': '科技', 'sector': '半导体'},
    {'code': '600658', 'name': '电科芯片', 'category': '科技', 'sector': '半导体'},
    {'code': '002475', 'name': '立讯精密', 'category': '科技', 'sector': '消费电子'},
    {'code': '000651', 'name': '格力电器', 'category': '蓝筹', 'sector': '家电'},
    {'code': '002371', 'name': '北方华创', 'category': '科技', 'sector': '半导体'},
    # 新能源/电池 — 散户热门
    {'code': '300750', 'name': '黑天鹅', 'category': '新能源', 'sector': '电池'},
    {'code': '600309', 'name': '万华化学', 'category': '蓝筹', 'sector': '化工'},
    {'code': '002594', 'name': '比亚迪', 'category': '新能源', 'sector': '汽车'},
    {'code': '601857', 'name': '中国石油', 'category': '蓝筹', 'sector': '能源'},
    {'code': '601012', 'name': '隆基绿能', 'category': '新能源', 'sector': '光伏'},
    # 消费/白酒 — 散户最爱
    {'code': '000858', 'name': '五粮液', 'category': '蓝筹', 'sector': '消费'},
    {'code': '600809', 'name': '山西汾酒', 'category': '蓝筹', 'sector': '消费'},
    {'code': '603288', 'name': '海天味业', 'category': '蓝筹', 'sector': '消费'},
    # 医药 — 散户避风港
    {'code': '300760', 'name': '安孚科技', 'category': '医药', 'sector': '制药'},
    {'code': '600196', 'name': '复星医药', 'category': '蓝筹', 'sector': '医药'},
    {'code': '300347', 'name': '泰格医药', 'category': '医药', 'sector': '医药'},
    # 金融/银行
    {'code': '600048', 'name': '保利发展', 'category': '蓝筹', 'sector': '地产'},
    {'code': '600050', 'name': '中国联通', 'category': '蓝筹', 'sector': '通信'},
]

# ============================================================
# 金属监控（贵金属 + 基本金属）
# ============================================================
METAL_MONITOR = {
    'enabled': True,
    'categories': ['贵金属', '基本金属'],
    'ref_prices': {
        '黄金': 880.60,      # 元/克
        '白银': 14019.0,     # 元/千克
        '铂': 393.95,        # 元/克
        '沪铜': 101820.0,    # 元/吨
        '沪铝': 22930.0,     # 元/吨
        '沪锌': 23885.0,     # 元/吨
        '沪镍': 129000.0,    # 元/吨
        '沪铅': 16250.0,     # 元/吨
        '沪锡': 385590.0,    # 元/吨
        '氧化铝': 2806.0,    # 元/吨
    }
}

# 兼容旧代码
GOLD_MONITOR = METAL_MONITOR
