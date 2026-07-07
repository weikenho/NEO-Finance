"""
NEO — 仓位管理建议器
根据用户总资金、当前持仓、市场状态，动态给出"买多少、留多少现金"的建议
"""

def position_advice(total_capital, positions, market_risk=None):
    """
    仓位管理建议
    
    Args:
        total_capital: 总资产（现金 + 持仓市值）
        positions: 持仓列表，每项 {name, code, value, pnl_pct}
        market_risk: 市场风险状态 {level: green/yellow/red, text: ...}
    
    Returns:
        {
            'total_capital': 总资产,
            'cash': 现金,
            'market_value': 持仓市值,
            'cash_ratio': 现金占比,
            'position_ratio': 仓位占比,
            'suggested_action': 建议动作,
            'suggested_amount': 建议买入金额,
            'max_single_pct': 单只最大仓位建议,
            'details': [大白话建议列表],
            'risk_advice': 基于风险的仓位建议,
        }
    """
    if market_risk is None:
        market_risk = {'level': 'yellow', 'text': '未知'}
    
    cash = total_capital - sum(p.get('value', 0) for p in positions)
    market_value = total_capital - cash
    cash_ratio = (cash / total_capital * 100) if total_capital > 0 else 0
    position_ratio = (market_value / total_capital * 100) if total_capital > 0 else 0
    
    # 根据市场风险等级确定目标仓位
    risk_level = market_risk.get('level', 'yellow')
    if risk_level == 'green':
        target_position = 70  # 市场好，目标7成仓
        action = '可以适当加仓'
    elif risk_level == 'yellow':
        target_position = 50  # 市场一般，目标5成仓
        action = '保持现状，别太激进'
    else:
        target_position = 30  # 市场差，目标3成仓
        action = '考虑减仓，保住本金'
    
    # 计算建议买入/卖出金额
    target_market_value = total_capital * (target_position / 100)
    suggested_amount = target_market_value - market_value
    
    # 生成建议
    details = []
    
    # 1. 现金占比建议
    if cash_ratio > 60:
        if risk_level == 'green':
            details.append(f'你的现金占了{cash_ratio:.0f}%，市场好的时候现金太多会"跑输大盘"。建议拿{position_ratio:.0f}%的钱进场试试')
        else:
            details.append(f'你的现金占了{cash_ratio:.0f}%，市场震荡/下跌时多留现金是对的——"手里有粮，心中不慌"')
    elif cash_ratio < 20:
        details.append(f'你的现金只剩{cash_ratio:.0f}%了！仓位太重，一旦跌起来没缓冲——建议至少留20%现金')
    
    # 2. 单只仓位集中度
    for p in positions:
        pct = (p.get('value', 0) / total_capital * 100) if total_capital > 0 else 0
        name = p.get('name', '某只')
        if pct > 30:
            details.append(f'"{name}" 占了总仓位{pct:.0f}%，建议单只别超过20%——鸡蛋别全放一个篮子')
        elif pct > 15:
            details.append(f'"{name}" 占了{pct:.0f}%，还行但别再加了')
    
    # 3. 持仓数量建议
    if len(positions) > 0:
        if total_capital >= 200000:
            optimal_count = min(8, max(4, len(positions)))
            if len(positions) < 3:
                details.append(f'你的资金有{total_capital:,.0f}元，但只持有了{len(positions)}只——太少不够分散，建议4-6只')
            elif len(positions) > 8:
                details.append(f'持有了{len(positions)}只，超过8只就变成"买了一盘散沙"——建议集中到4-6只')
    
    # 4. 市场风险对应的仓位建议
    if risk_level == 'red':
        details.insert(0, f'🔴 市场风险偏高！建议把总仓位控制在30%以内，先活下来再说')
    elif risk_level == 'yellow':
        details.insert(0, f'🟡 市场有风险信号，建议仓位控制在50%以内，别一把梭哈')
    else:
        details.insert(0, f'🟢 市场状态尚可，可以保持60-70%仓位，慢慢加')
    
    # 安全上限
    max_single_pct = min(25, max(10, 100 // max(len(positions) + 1, 3)))
    
    return {
        'total_capital': round(total_capital, 2),
        'cash': round(cash, 2),
        'market_value': round(market_value, 2),
        'cash_ratio': round(cash_ratio, 1),
        'position_ratio': round(position_ratio, 1),
        'target_position': target_position,
        'suggested_action': action,
        'suggested_amount': round(suggested_amount, 2),
        'max_single_pct': max_single_pct,
        'details': details,
    }
