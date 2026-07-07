"""
NEO — 实盘交易引擎
功能：通过 easytrader 驱动券商交易软件，实现真实的 ETF/股票买卖
支持券商：天天基金 ('tiantian') 为默认
"""
from datetime import datetime


class RealTrader:
    """实盘交易引擎 — 用真金白银打仗"""

    def __init__(self, config=None):
        """
        初始化实盘交易引擎

        Args:
            config: 配置字典，支持以下键：
                - broker: 券商类型，默认 'tiantian'（天天基金）
                - user: 券商登录用户名
                - password: 券商登录密码
                - initial_capital: 初始资金（用于统计）
        """
        if config is None:
            config = {}

        self.broker_type = config.get('broker', 'tiantian')
        self.user = config.get('user', '')
        self.password = config.get('password', '')
        self.initial_capital = config.get('initial_capital', 50000)
        self.broker = None
        self._last_error = None
        self._local_trades = []

    def connect(self):
        """
        连接券商交易软件

        Returns:
            dict: {'success': True, 'message': str} 或 {'success': False, 'reason': str}
        """
        try:
            from easytrader import use
            self.broker = use(self.broker_type)
            self.broker.connect(user=self.user, password=self.password)
            self._last_error = None
            return {
                'success': True,
                'message': f'券商连接成功：{self.broker_type}'
            }
        except Exception as e:
            self._last_error = str(e)
            return {
                'success': False,
                'reason': '券商连接断了：' + str(e)
            }

    @property
    def connected(self):
        """检查券商是否还活着"""
        try:
            if self.broker is None:
                return False
            self.broker.position
            return True
        except Exception:
            return False

    def get_account(self):
        """
        获取账户信息
        Returns: dict with cash, initial_capital, stock_positions
        """
        try:
            balance = self.broker.balance
            positions_raw = self.broker.position

            cash = self._extract_cash(balance)
            stock_positions = self._normalize_positions(positions_raw)

            return {
                'cash': round(cash, 2),
                'initial_capital': self.initial_capital,
                'stock_positions': stock_positions
            }
        except Exception as e:
            return {
                'success': False,
                'reason': '券商连接断了：' + str(e)
            }

    def _extract_cash(self, balance):
        """从余额信息中提取可用现金"""
        if isinstance(balance, dict):
            for key in ['可用资金', '可用余额', 'available', 'cash', '余额']:
                if key in balance:
                    return float(balance[key])
            # 取第一个数值字段
            for v in balance.values():
                if isinstance(v, (int, float)):
                    return float(v)
        if isinstance(balance, list):
            if len(balance) > 0:
                return self._extract_cash(balance[0])
        return float(balance) if balance else 0

    def _normalize_positions(self, positions_raw):
        """标准化持仓列表"""
        result = []
        for p in positions_raw:
            cost = p.get('成本价', p.get('cost_price', 0))
            current_price = p.get('最新价', p.get('current_price', 0))
            shares = p.get('可用余额', p.get('shares', 0))
            result.append({
                'code': p.get('证券代码', p.get('code', '')),
                'name': p.get('证券名称', p.get('name', '')),
                'shares': float(shares),
                'avg_price': float(cost),
                'current_price': float(current_price),
                'cost': round(float(shares) * float(cost), 2),
                'current_value': round(float(shares) * float(current_price), 2),
                'pnl': round(float(shares) * (float(current_price) - float(cost)), 2),
                'pnl_pct': round((float(current_price) - float(cost)) / max(float(cost), 1) * 100, 2),
            })
        return result

    def buy(self, code, name, shares, price, reason=''):
        """
        执行买入

        Args:
            code: 证券代码 (如 '510500')
            name: 证券名称 (如 '沪深300ETF')
            shares: 买入股数
            price: 买入价格
            reason: 买入理由

        Returns:
            dict: {'success': True/False, 'message': str} 或 {'success': False, 'reason': str}
        """
        try:
            result = self.broker.buy(code, price=price, amount=int(shares))
            self._record_trade('BUY', code, name, shares, price, reason)
            return {
                'success': True,
                'message': f'买入了{name} {int(shares)}股，价格¥{price:.2f}'
            }
        except Exception as e:
            return {
                'success': False,
                'reason': '券商连接断了：' + str(e)
            }

    def sell(self, code, name, shares, price, reason=''):
        """
        执行卖出

        Args:
            code: 证券代码
            name: 证券名称
            shares: 卖出股数
            price: 卖出价格
            reason: 卖出理由

        Returns:
            dict: {'success': True/False, 'message': str} 或 {'success': False, 'reason': str}
        """
        try:
            result = self.broker.sell(code, price=price, amount=int(shares))
            self._record_trade('SELL', code, name, shares, price, reason)
            return {
                'success': True,
                'message': f'卖出了{name} {int(shares)}股，价格¥{price:.2f}'
            }
        except Exception as e:
            return {
                'success': False,
                'reason': '券商连接断了：' + str(e)
            }

    def _record_trade(self, action, code, name, shares, price, reason):
        """记录一笔本地交易（用于统计）"""
        total_amount = shares * price
        self._local_trades.append({
            'code': code,
            'name': name,
            'action': action,
            'shares': shares,
            'price': price,
            'total_amount': round(total_amount, 2),
            'trade_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'reason': reason,
        })

    def get_positions(self):
        """
        获取所有持仓

        Returns:
            list: 持仓列表，每项包含 code, name, shares, avg_price,
                  current_price, pnl, pnl_pct, cost, current_value
            或 [{'success': False, 'reason': str}]
        """
        try:
            positions_raw = self.broker.position
            return self._normalize_positions(positions_raw)
        except Exception as e:
            return [{'success': False, 'reason': '券商连接断了：' + str(e)}]

    def get_trades(self, limit=20):
        """
        获取交易记录

        Args:
            limit: 返回最近 N 条记录

        Returns:
            list: 交易记录列表
        """
        # 优先从券商获取，降级到本地记录
        try:
            trades = self.broker.today_returns
            if trades:
                return self._normalize_trades(trades)[:limit]
        except Exception:
            pass

        try:
            trades = self.broker.trade_history
            if trades:
                return self._normalize_trades(trades)[:limit]
        except Exception:
            pass

        # 降级：返回本地记录
        return list(reversed(self._local_trades))[:limit]

    def _normalize_trades(self, raw_trades):
        """标准化交易记录"""
        result = []
        for t in raw_trades:
            result.append({
                'code': t.get('证券代码', t.get('code', '')),
                'name': t.get('证券名称', t.get('name', '')),
                'action': t.get('买卖方向', t.get('action', '')),
                'shares': float(t.get('成交数量', t.get('shares', 0))),
                'price': float(t.get('成交价格', t.get('price', 0))),
                'total_amount': float(t.get('成交金额', t.get('total_amount', 0))),
                'trade_date': t.get('成交日期', t.get('trade_date', '')),
            })
        return result

    def get_trade_stats(self):
        """
        获取交易统计（大白话版）

        Returns:
            dict: {
                'total_sells': 总卖出次数,
                'wins': 赚了的次数,
                'win_rate': 胜率（百分比）,
                'avg_win': 平均每次赚多少,
                'avg_loss': 平均每次亏多少,
                'profit_loss_ratio': 盈亏比,
                'total_pnl': 总盈亏
            }
        """
        sell_trades = [t for t in self._local_trades if t['action'] == 'SELL']
        buy_trades = {t['code']: t for t in self._local_trades if t['action'] == 'BUY'}

        wins = 0
        losses = 0
        win_amounts = []
        loss_amounts = []
        total_pnl = 0

        for st in sell_trades:
            buy = buy_trades.get(st['code'])
            if buy:
                pnl = (st['price'] - buy['price']) * st['shares']
                total_pnl += pnl
                if pnl > 0:
                    wins += 1
                    win_amounts.append(pnl)
                else:
                    losses += 1
                    loss_amounts.append(pnl)

        total_sells = len(sell_trades)
        win_rate = round(wins / total_sells * 100, 1) if total_sells > 0 else 0
        avg_win = sum(win_amounts) / len(win_amounts) if win_amounts else 0
        avg_loss = sum(loss_amounts) / len(loss_amounts) if loss_amounts else 0
        profit_loss_ratio = round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else round(avg_win, 2)

        return {
            'total_sells': total_sells,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_loss_ratio': profit_loss_ratio,
            'total_pnl': round(total_pnl, 2),
        }

    def reset(self):
        """
        重置实盘（清空所有持仓 — 全部卖出）

        Returns:
            dict: {'success': True/False, 'message': str}
        """
        try:
            positions = self.broker.position
            for p in positions:
                code = p.get('证券代码', p.get('code', ''))
                name = p.get('证券名称', p.get('name', ''))
                shares = int(p.get('可用余额', p.get('shares', 0)))
                current_price = float(p.get('最新价', p.get('current_price', 0)))
                if shares > 0 and current_price > 0:
                    self.broker.sell(code, price=current_price, amount=shares)
            self._local_trades = []
            return {
                'success': True,
                'message': '实盘清空完成，所有持仓已卖出'
            }
        except Exception as e:
            return {
                'success': False,
                'reason': '券商连接断了：' + str(e)
            }
