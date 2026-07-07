"""
NEO — 风险预警引擎
核心功能：
1. 红绿灯风险评估
2. 套路识别器（识别常见"被割信号"）
3. 保本计算器
4. 持仓警报检查器
"""
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 常见割韭菜套路特征库
SCAM_PATTERNS = [
    {
        'name': 'FOMO话术（恐惧错过）',
        'keywords': ['最后', '马上', '即将', '暴涨', '翻倍', '千载难逢', '错过就没了', '赶紧上车'],
        'severity': 'high',
        'explanation': '庄家最喜欢用"紧迫感"让你来不及思考。真好的机会，通常给你时间想清楚。',
    },
    {
        'name': '权威背书（名人/专家推荐）',
        'keywords': ['巴菲特也买了', '专家预测', '基金经理重仓', 'XX大佬', ' insider', '内部消息'],
        'severity': 'medium',
        'explanation': '专家说的不一定错，但专家可能已经卖出了。"巴菲特也买了"——问题是你可能比巴菲特晚进场了一个月。',
    },
    {
        'name': '简单到不可思议的故事',
        'keywords': ['只要', '稳赚不赔', '闭眼买', '躺赚', '傻瓜式', '三步', '三天'],
        'severity': 'high',
        'explanation': '金融世界里，"简单"通常意味着"复杂的部分你还没看到"。如果真那么简单，为什么不是每个人都是百万富翁？',
    },
    {
        'name': '大资金进场信号',
        'keywords': ['大资金', '主力', '庄家', '放量', '资金涌入'],
        'severity': 'low',
        'explanation': '大资金进场不一定是好事——大资金也分"聪明钱"和"笨钱"。关键看他们是在买还是在卖。',
    },
    {
        'name': '历史相似论',
        'keywords': ['就像', '复刻', '2020年的', '和XX年一样', '历史重演'],
        'severity': 'medium',
        'explanation': '历史会重演，但很少是"一模一样"。用2020年的逻辑买2025年的东西，可能是最贵的学费。',
    },
    {
        'name': '技术面吹牛',
        'keywords': ['金叉', '突破', '历史新高', '均线多头', '量价齐升', '黄金交叉'],
        'severity': 'low',
        'explanation': '技术面信号有用，但单一信号太容易"被打脸"了。最好等2-3个信号同时出现再动手。',
    },
    {
        'name': '情绪化用语',
        'keywords': ['疯了', '爆了', '疯了', '史诗级', '疯狂', '杀疯了', '一路向北'],
        'severity': 'high',
        'explanation': '当一个人用"疯了"来形容行情时，通常意味着大部分人已经冲进去了——也就是即将被割了。',
    },
    {
        'name': '收益承诺',
        'keywords': ['年化', '%收益', '月入', '周赚', '年赚XX', '保底', '稳赚'],
        'severity': 'high',
        'explanation': '金融界第一铁律：承诺高收益的地方，风险一定高到你不注意的地方。"保底"在金融里基本等于"不保"。',
    },
    {
        'name': '幸存者偏差',
        'keywords': ['他赚了', '隔壁老王', '朋友圈', '晒单', '都赚了', '只有你亏', '看谁谁赚'],
        'severity': 'high',
        'explanation': '你看到的"赚了的人"是被选中的——那些亏了的人通常已经沉默了。朋友圈里晒单的基本都是赢家，亏了的人要么删了要么不说话。拿几个赢家的故事当普遍规律，是最容易被割的。',
    },
    {
        'name': '免费午餐',
        'keywords': ['免费', '送', '限时免费', '零成本', '不花', '白拿', '不用花钱', '第一份免费'],
        'severity': 'medium',
        'explanation': '天下没有免费的午餐，金融圈更没有。"免费"只是让你先入局，等你习惯了再慢慢收钱。最贵的东西通常标着"免费"。比如免费课让你先买低价课，低价课再推高价课。',
    },
    {
        'name': '紧迫感制造',
        'keywords': ['倒计时', '仅剩', '最后X个名额', '今晚24点', '明天开盘前', '犹豫就会败北', '现在不', '过时不候'],
        'severity': 'high',
        'explanation': '紧迫感是让你关掉大脑的开关。当有人说"最后3个名额"时，你大脑中的理性思考被"错过恐惧"取代。真的好东西，等明天再决定也不会少。越是急着让你今天定下来，越要留到明天再看。',
    },
    {
        'name': '权威数据',
        'keywords': ['据数据显示', '统计表明', 'XX机构统计', '数据显示', '超过XX%', '精确到小数', 'XX%的用户'],
        'severity': 'medium',
        'explanation': '数字看起来很有说服力，但"数据"本身也可以被挑选。说"87.3%的用户满意"，但你得问：是100个人里满意，还是10000个人里满意？数据源在哪？是"选了3天涨的日子"还是"选了7天涨的日子"？数字是最能骗人的东西。',
    },
    {
        'name': '恐惧营销',
        'keywords': ['再不', '到时候就', '错过这次', '以后再也', '迟早要', '最可怕', '最大的风险', '通胀吞噬'],
        'severity': 'high',
        'explanation': '恐惧和贪婪一样，都是最好的"燃料"。用恐惧推动你做决定，通常是让你从"观望"变"行动"。说"再不买就晚了"的人，可能最怕的是"你不买他就晚了"。真该买的东西不会因为你今天犹豫一天就没了。',
    },
    {
        'name': '社交证明陷阱（从众心理）',
        'keywords': ['万人抢购', '千人围观', '千人推荐', 'XX人已经买入', '好评如潮', '口碑爆棚', '全网都在买', '人手一只'],
        'severity': 'medium',
        'explanation': '当"万人抢购"时，你要想的是：谁在卖？人不会凭空消失，每只被买进去的股票都有一只被卖出来的股票。万人买的时候，可能有一万人卖。',
    },
    {
        'name': '锚定效应（价格锚）',
        'keywords': ['原价XX', '现在只要', '打了对折', '历史低点', '估值洼地', 'PE不到XX', '打了6折'],
        'severity': 'medium',
        'explanation': '锚定效应是：给大脑定一个"参照价"，让你觉得"划算"。比如原价100，现在60，你脑中说"打了六折"。问题在于：如果它跌到30呢？那"原价100"就成了最贵的学费。',
    },
    {
        'name': '故事包装（概念炒作）',
        'keywords': ['概念', '赛道', '新赛道', '风口', 'XX赛道龙头', '赛道之王', '风口上的猪', '第二增长曲线'],
        'severity': 'low',
        'explanation': '好故事不等于好股票。"赛道之王"听起来很酷，但如果赛道还在铺路阶段，王的宝座可能还没建好。先看看赛道上有多少只"王"再说。',
    },
    {
        'name': '稀缺性制造',
        'keywords': ['稀缺', '独一份', '唯一性', '护城河', '不可复制', '非它莫属', '不可多得', '仅此一家'],
        'severity': 'medium',
        'explanation': '金融圈最稀缺的不是"好标的"，而是"好价格"。就算"仅此一家"，如果价格贵到离谱，也值得等它打折再进场。真稀缺的东西，市场会给你"追高"的冲动——那通常是庄家希望你做的。',
    },
    {
        'name': '回本心理（损失厌恶）',
        'keywords': ['马上就回本', '再拿一阵就回来了', '跌到底了', '再跌就超跌了', '快回本了', '再等一等就回来了'],
        'severity': 'high',
        'explanation': '回本心理是最容易被割的。你的大脑会告诉你"再等一等就回来了"。但市场可不管你有没有"回来"——它只认趋势。如果你开始想"回本"，说明你已经从"理性买入"变成了"赌徒心态"。',
    },
    {
        'name': '锚定比较（同行对比）',
        'keywords': ['比同行', '比XX便宜', '同板块最便宜', '跟XX比才刚刚起步', '落后于', '对标XX'],
        'severity': 'medium',
        'explanation': '比较是双刃剑。"比同行便宜"是真的，但如果同行已经涨了30%而它还没动，可能是"便宜有便宜的道理"。同行对比的陷阱在于：你把A的上涨当B上涨的理由，但A和B可能处于不同的生命周期。',
    },
    {
        'name': '回测陷阱（后视镜驾驶）',
        'keywords': ['回测', '过去5年', '历史数据', '复利', '年化回报', '跑赢大盘'],
        'severity': 'low',
        'explanation': '回测是最容易"自圆其说"的工具。你选了10只股票，挑出表现最好的3只，说"年化回报15%"。但问题是：那7只"被遗忘"的股票表现怎样？回测的陷阱在于：你总是用后视镜来看前方的路。',
    },
    {
        'name': '专家分歧（利用不确定性）',
        'keywords': ['专家分歧', '看多与看少', '多空博弈', '机构意见不一', '分析师分歧'],
        'severity': 'low',
        'explanation': '当专家"意见不一"时，市场通常处于"中间地带"。这时候入场等于把硬币抛了：正面赢，反面输。与其赌硬币，不如等方向明确了再跟进。专家分歧越大，市场越"犹豫"。',
    },
    {
        'name': '锚定心理（锚定价格）',
        'keywords': ['锚定', '历史最高价', '历史最低价', '锚点在XX', '锚定在PE', '锚定估值'],
        'severity': 'low',
        'explanation': '当人们说"锚定"时，意思是"用一个固定点来判断"。问题是：锚可能"锚错地方"。比如锚定在"历史最高价"时，如果历史已经变了，最高价可能只是"高估的顶峰"。',
    },
    {
        'name': '锚定效应（锚定价值）',
        'keywords': ['内在价值', '锚定价值', '价值回归', '均值回归', '回归均值'],
        'severity': 'low',
        'explanation': '"价值回归"听起来很美，但"价值"是一个"动态的概念"。昨天的"内在价值"可能因为行业变化、竞争加剧或技术革新而"缩水"。锚定在"昨天的价值"上，可能忽略了"今天的变化"。',
    },
]

def assess_market_risk(etf_data: list) -> dict:
    """
    根据ETF实时数据评估整体市场风险
    返回：红绿灯状态 + 大白话解释 + 成交量分析

    Args:
        etf_data: ETF数据列表，每项可包含：
            - change_pct: 涨跌幅(%)
            - volume: 当前成交量
            - avg_volume: 平均成交量（过去N日）
            - name: ETF名称
    """
    if not etf_data:
        return {'level': 'yellow', 'emoji': '⚠️', 'text': '数据还没来，先观望', 'details': [], 'volume_analysis': {}}

    # 统计涨跌
    up_count = sum(1 for e in etf_data if e.get('change_pct', 0) > 0)
    down_count = sum(1 for e in etf_data if e.get('change_pct', 0) < 0)
    flat_count = len(etf_data) - up_count - down_count
    avg_change = np.mean([e.get('change_pct', 0) for e in etf_data])
    max_drop = min([e.get('change_pct', 0) for e in etf_data])
    max_rise = max([e.get('change_pct', 0) for e in etf_data])

    details = []

    # ========== 成交量分析 ==========
    volume_analysis = {}
    vols = [e for e in etf_data if e.get('volume') and e.get('avg_volume') and e['avg_volume'] > 0]
    if vols:
        # 计算整体量比（当前成交量 / 平均成交量）
        volume_ratios = [e['volume'] / e['avg_volume'] for e in vols]
        avg_volume_ratio = np.mean(volume_ratios)
        max_volume_ratio = max(volume_ratios)
        min_volume_ratio = min(volume_ratios)

        # 放量/缩量的ETF数量
        expanding_count = sum(1 for v in volume_ratios if v > 1.2)
        shrinking_count = sum(1 for v in volume_ratios if v < 0.8)

        volume_analysis = {
            'avg_volume_ratio': round(avg_volume_ratio, 2),
            'max_volume_ratio': round(max_volume_ratio, 2),
            'expanding_count': expanding_count,
            'shrinking_count': shrinking_count,
            'total_analyzed': len(vols),
        }

        # 放量分析 → 加入details
        if avg_volume_ratio > 1.5:
            details.append('⚠️ 成交量放大了50%以上！放量上涨要小心"天量见天价"，放量下跌更要小心"放量出逃"')
        elif avg_volume_ratio > 1.2:
            details.append('成交量比平时大了20%+，市场开始热闹了，注意看谁是买家谁是卖家')
        elif avg_volume_ratio < 0.7:
            details.append('成交量缩得厉害，市场有点"温吞水"，缩量的时候价格波动小，适合慢慢买')
        elif avg_volume_ratio < 0.8:
            details.append('成交量比平时略小，市场不算太热，适合观察')

        # 极度放量单品提醒
        max_vol_etf = max(vols, key=lambda e: e['volume'] / e['avg_volume'])
        if max_vol_etf['volume'] / max_vol_etf['avg_volume'] > 2:
            details.append(f'"{max_vol_etf.get("name", "某ETF")}" 的成交量是平时的{round(max_vol_etf["volume"]/max_vol_etf["avg_volume"], 1)}倍，大资金在动！')

    # 红绿灯判断逻辑
    if up_count >= len(etf_data) * 0.7 and avg_change > 2:
        # 普涨且涨幅大 → 可能是"追高"时刻
        level = 'yellow'
        emoji = '⚠️'
        text = '今天涨得猛，但要小心"追高"——大家都冲进去的时候，往往是庄家开始卖的时候'
        details.insert(0, '全线上涨，市场情绪偏热，注意别追高')
    elif down_count >= len(etf_data) * 0.7 and avg_change < -2:
        # 普跌 → 可能恐慌性卖出
        level = 'red'
        emoji = '🔴'
        text = '今天跌得凶，但别急着抄底——"接飞刀"要先等它落地'
        details.insert(0, '全线下跌，市场恐慌，别急着抄底')
    elif avg_change < -1:
        level = 'yellow'
        emoji = '🟡'
        text = '今天小跌，正常波动。如果你没持仓，就让子弹飞一会儿'
        details.insert(0, '小幅回调，正常波动')
    elif avg_change > 1:
        level = 'green'
        emoji = '🟢'
        text = '今天小涨，市场状态还行。可以关注，但别一次全买'
        details.insert(0, '小幅上涨，市场状态健康')
    else:
        level = 'green'
        emoji = '🟢'
        text = '市场横着走，涨跌都不大。横盘的时候，最好的策略是"别瞎动"'
        details.insert(0, '市场震荡，保持耐心')

    return {
        'level': level, 'emoji': emoji, 'text': text,
        'details': details,
        'volume_analysis': volume_analysis,
        'stats': {
            'up_count': up_count, 'down_count': down_count, 'flat_count': flat_count,
            'avg_change': round(avg_change, 2), 'max_drop': round(max_drop, 2), 'max_rise': round(max_rise, 2)
        }
    }

def detect_scam_patterns(text: str) -> list:
    """
    套路识别器 — 分析一段文字中包含的"被割信号"
    输入：任意一段文字（标题、推送、聊天消息等）
    输出：命中的套路列表 + 大白话解释
    """
    matches = []
    text_lower = text.lower()

    for pattern in SCAM_PATTERNS:
        hit_keywords = [kw for kw in pattern['keywords'] if kw.lower() in text_lower]
        if hit_keywords:
            severity_score = {'high': 3, 'medium': 2, 'low': 1}.get(pattern['severity'], 1)
            matches.append({
                'name': pattern['name'],
                'hit_keywords': hit_keywords,
                'severity': pattern['severity'],
                'severity_score': severity_score,
                'explanation': pattern['explanation'],
            })

    # 按严重程度排序
    matches.sort(key=lambda x: x['severity_score'], reverse=True)

    # 计算总风险分（0-100）
    total_score = min(100, sum(m['severity_score'] * 15 for m in matches))

    return {
        'matches': matches,
        'risk_score': total_score,
        'risk_level': 'danger' if total_score >= 70 else ('warning' if total_score >= 40 else ('caution' if total_score >= 20 else 'safe')),
        'total_hits': len(matches),
    }

def alert_check(portfolio: dict) -> list:
    """
    持仓警报检查器 — 大白话告诉你"你的持仓有没有问题"

    检查三项：
    1. 回撤警报：整体回撤超过5% → "你亏了5%以上了，别硬扛！"
    2. 集中度警报：单只持仓超过总资产40% → "你太依赖一只了，鸡蛋都放一个篮子了"
    3. 持仓时间警报：单只持仓超过7天没动 → "你已经盯着它7天了，该想想是留还是走"

    Args:
        portfolio: 持仓信息字典
            - total_value: 当前总资产
            - peak_value: 历史最高总资产
            - holdings: 持仓列表，每项包含：
                - name: 持仓名称
                - value: 当前价值
                - buy_date: 买入日期（datetime或"2025-07-01"字符串）
            - today: 今天日期（可选，默认 datetime.today()）

    Returns:
        警报列表，每个警报包含 type, emoji, message, severity
    """
    alerts = []

    total_value = portfolio.get('total_value', 0)
    peak_value = portfolio.get('peak_value', 0)
    holdings = portfolio.get('holdings', [])
    today = portfolio.get('today', datetime.today().date())

    if isinstance(today, datetime):
        today = today.date()

    # ========== 1. 回撤警报 ==========
    if peak_value > 0:
        drawdown_pct = ((peak_value - total_value) / peak_value) * 100
        if drawdown_pct > 10:
            alerts.append({
                'type': 'drawdown',
                'emoji': '🔴',
                'severity': 'critical',
                'message': f'你的总资产从最高点跌了{drawdown_pct:.1f}%！这可不是"小回调"了，超过10%就是"大甩卖"。现在要考虑的不是"什么时候回本"，而是"要不要认栽先跑"。',
                'drawdown_pct': round(drawdown_pct, 1),
            })
        elif drawdown_pct > 5:
            alerts.append({
                'type': 'drawdown',
                'emoji': '🟡',
                'severity': 'warning',
                'message': f'你的总资产从最高点跌了{drawdown_pct:.1f}%，已经过了"喝杯咖啡就能忘记"的程度。超过5%就是身体在提醒你："该看看账本了"。',
                'drawdown_pct': round(drawdown_pct, 1),
            })
        elif drawdown_pct > 2:
            alerts.append({
                'type': 'drawdown',
                'emoji': '🟢',
                'severity': 'info',
                'message': f'你的总资产从最高点跌了{drawdown_pct:.1f}%，小波动，正常。就当市场给你做了个"热身运动"。',
                'drawdown_pct': round(drawdown_pct, 1),
            })

    # ========== 2. 集中度警报 ==========
    if total_value > 0 and holdings:
        for h in holdings:
            pct = (h.get('value', 0) / total_value) * 100
            name = h.get('name', '某持仓')
            if pct > 60:
                alerts.append({
                    'type': 'concentration',
                    'emoji': '🔴',
                    'severity': 'critical',
                    'message': f'"{name}" 占了你的总资产{pct:.0f}%！这意味着超过六成的钱都押在这一只上了。万一它打喷嚏，你的整个账户都要感冒了。',
                    'name': name,
                    'pct': round(pct, 1),
                })
            elif pct > 40:
                alerts.append({
                    'type': 'concentration',
                    'emoji': '🟡',
                    'severity': 'warning',
                    'message': f'"{name}" 占了你的总资产{pct:.0f}%，快超过四成。鸡蛋开始往同一个篮子堆了——建议看看有没有其他选择分散一下。',
                    'name': name,
                    'pct': round(pct, 1),
                })

    # ========== 3. 持仓时间警报（Stale Holding）==========
    if holdings:
        for h in holdings:
            buy_date = h.get('buy_date')
            if not buy_date:
                continue

            # 解析日期
            if isinstance(buy_date, str):
                try:
                    buy_date = datetime.strptime(buy_date, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        buy_date = datetime.strptime(buy_date, '%Y-%m-%d %H:%M:%S').date()
                    except ValueError:
                        continue
            elif isinstance(buy_date, datetime):
                buy_date = buy_date.date()

            days_held = (today - buy_date).days
            name = h.get('name', '某持仓')

            if days_held >= 14:
                alerts.append({
                    'type': 'stale_holding',
                    'emoji': '🔴',
                    'severity': 'warning',
                    'message': f'你盯住"{name}"已经{days_held}天了还没动！超过两周不动，要么是你忘了它，要么是"既非牛市也非熊市"的中间地带。问问自己：当初买它的理由还在吗？',
                    'name': name,
                    'days_held': days_held,
                })
            elif days_held >= 7:
                alerts.append({
                    'type': 'stale_holding',
                    'emoji': '🟡',
                    'severity': 'caution',
                    'message': f'你拿着"{name}"已经{days_held}天了，快过了一周还没动静。超过7天的持仓就要开始问自己："我是真的看好它，还是只是懒得卖？"',
                    'name': name,
                    'days_held': days_held,
                })

    return alerts

def calculate_preservation(principal: float, stop_loss_pct: float, take_profit_pct: float, current_pnl_pct: float) -> dict:
    """
    保本计算器 — 大白话告诉你"你的钱现在咋样"

    Args:
        principal: 本金
        stop_loss_pct: 止损百分比（如0.08 = 8%）
        take_profit_pct: 止盈百分比（如0.15 = 15%）
        current_pnl_pct: 当前盈亏百分比
    """
    max_loss = principal * stop_loss_pct
    max_profit = principal * take_profit_pct
    current_pnl = principal * current_pnl_pct

    # 距离止损线还有多少
    stop_loss_price_pct = -stop_loss_pct
    distance_to_stop = (current_pnl_pct - stop_loss_price_pct) * 100  # 百分比

    # 距离止盈线还有多少
    distance_to_profit = (take_profit_pct - current_pnl_pct) * 100

    # 大白话生成
    if current_pnl_pct > 0:
        status_text = f"你的{principal}块钱现在赚了{abs(current_pnl):.0f}块，不错！"
        status_emoji = "😊"
    elif current_pnl_pct == 0:
        status_text = f"你的{principal}块钱不赚不亏，跟银行存款一样"
        status_emoji = "😐"
    else:
        status_text = f"你的{principal}块钱现在亏了{abs(current_pnl):.0f}块，相当于少了{abs(current_pnl)}"
        status_emoji = "😟"

    # 止损提醒
    if distance_to_stop < 2:
        stop_warning = f"⚠️ 快接近止损线了！再跌{distance_to_stop:.1f}%就触发卖出，准备跑路！"
    elif distance_to_stop < 5:
        stop_warning = f"离止损线还有一小段（{distance_to_stop:.1f}%），可以留意一下"
    else:
        stop_warning = f"离止损线还挺远（{distance_to_stop:.1f}%），暂时安全"

    # 止盈提醒
    if distance_to_profit < 2:
        profit_warning = f"🎯 快到止盈线了！再涨{distance_to_profit:.1f}%就触发卖出，准备落袋为安！"
    elif distance_to_profit < 5:
        profit_warning = f"离止盈线还有一小段（{distance_to_profit:.1f}%），快赚钱了"
    else:
        profit_warning = f"离止盈线还远着呢（{distance_to_profit:.1f}%），先让它跑"

    return {
        'principal': principal,
        'current_pnl': round(current_pnl, 2),
        'current_pnl_pct': round(current_pnl_pct * 100, 2),
        'status_text': status_text,
        'status_emoji': status_emoji,
        'max_loss': round(max_loss, 2),
        'max_profit': round(max_profit, 2),
        'distance_to_stop': round(distance_to_stop, 1),
        'distance_to_profit': round(distance_to_profit, 1),
        'stop_warning': stop_warning,
        'profit_warning': profit_warning,
        'stop_loss_price': round(principal * (1 - stop_loss_pct), 2),
        'take_profit_price': round(principal * (1 + take_profit_pct), 2),
    }
