"""
NEO — 模拟交易引擎
功能：模拟盘买卖、持仓管理、盈亏计算、交易记录
"""
import json
import os
from datetime import datetime

class SimTrader:
    """模拟交易引擎 — 用虚拟钱练手"""
    
    def __init__(self, initial_capital=50000):
        self.initial_capital = initial_capital
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, 'sim_trades.db')
        self._init_db()
    
    def _init_db(self):
        """初始化SQLite数据库"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY,
            cash REAL,
            initial_capital REAL,
            in_cool_down INTEGER DEFAULT 0,
            cool_down_start TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT,
            shares REAL,
            avg_price REAL,
            buy_date TEXT,
            current_price REAL
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            name TEXT,
            action TEXT,
            shares REAL,
            price REAL,
            total_amount REAL,
            pnl REAL,
            trade_date TEXT,
            reason TEXT
        )''')
        # 初始化账户
        c.execute("SELECT COUNT(*) FROM account WHERE id = 1")
        if c.fetchone()[0] == 0:
            ic = self.initial_capital
            c.execute("INSERT INTO account (id, cash, initial_capital) VALUES (1, ?, ?)",
                     (ic, ic))
        conn.commit()
        conn.close()
    
    def get_account(self):
        """获取账户信息"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM account WHERE id = 1")
        account = dict(c.fetchone())
        conn.close()
        return account
    
    def get_positions(self):
        """获取所有持仓"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM positions")
        positions = [dict(p) for p in c.fetchall()]
        conn.close()
        
        # 计算盈亏
        for p in positions:
            cost = p['shares'] * p['avg_price']
            current_value = p['shares'] * p['current_price']
            p['cost'] = round(cost, 2)
            p['current_value'] = round(current_value, 2)
            p['pnl'] = round(current_value - cost, 2)
            p['pnl_pct'] = round((p['current_price'] - p['avg_price']) / p['avg_price'] * 100, 2)
        
        return positions
    
    def update_position_price(self, code, price):
        """更新持仓当前价格"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE positions SET current_price = ? WHERE code = ?", (price, code))
        conn.commit()
        conn.close()
    
    def buy(self, code, name, shares, price, reason=''):
        """执行买入"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 检查余额
        c.execute("SELECT cash FROM account WHERE id = 1")
        cash = c.fetchone()[0]
        cost = shares * price
        
        if cost > cash:
            conn.close()
            return {'success': False, 'reason': f'口袋里的钱不够：需要¥{cost:.0f}，口袋里只有¥{cash:.0f}'}
        
        # 扣钱
        c.execute("UPDATE account SET cash = cash - ? WHERE id = 1", (cost,))
        
        # 更新持仓（加仓或新建）
        c.execute("SELECT * FROM positions WHERE code = ?", (code,))
        existing = c.fetchone()
        if existing:
            old_shares = existing[3]
            old_price = existing[4]
            new_avg = (old_price * old_shares + cost) / (old_shares + shares)
            c.execute("UPDATE positions SET shares = shares + ?, avg_price = ?, current_price = ? WHERE code = ?",
                     (shares, new_avg, price, code))
        else:
            c.execute("INSERT INTO positions (code, name, shares, avg_price, buy_date, current_price) VALUES (?, ?, ?, ?, ?, ?)",
                     (code, name, shares, price, datetime.now().strftime('%Y-%m-%d'), price))
        
        # 记录交易
        c.execute("INSERT INTO trades (code, name, action, shares, price, total_amount, trade_date, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                 (code, name, 'BUY', shares, price, cost, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), reason))
        
        conn.commit()
        conn.close()
        remaining = cash - cost
        return {
            'success': True,
            'message': f'买入了{name} {shares:.0f}股，花了¥{cost:.0f}，口袋还剩¥{remaining:.0f}',
            'remaining_cash': round(remaining, 2)
        }
    
    def sell(self, code, name, shares, price, reason=''):
        """执行卖出"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT shares, avg_price FROM positions WHERE code = ?", (code,))
        row = c.fetchone()
        if not row:
            conn.close()
            return {'success': False, 'reason': f'还没买{name}，怎么卖？'}
        
        if shares > row[0]:
            conn.close()
            return {'success': False, 'reason': f'你只买了{row[0]:.0f}股，想卖{shares:.0f}股'}
        
        # 计算盈亏
        pnl = (price - row[1]) * shares
        revenue = shares * price
        
        # 加钱
        c.execute("UPDATE account SET cash = cash + ? WHERE id = 1", (revenue,))
        
        # 更新持仓
        remaining_shares = row[0] - shares
        if remaining_shares <= 0:
            c.execute("DELETE FROM positions WHERE code = ?", (code,))
        else:
            c.execute("UPDATE positions SET shares = ?, current_price = ? WHERE code = ?",
                     (remaining_shares, price, code))
        
        # 记录交易
        c.execute("INSERT INTO trades (code, name, action, shares, price, total_amount, pnl, trade_date, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (code, name, 'SELL', shares, price, revenue, pnl, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), reason))
        
        conn.commit()
        conn.close()
        
        pnl_word = '赚了' if pnl > 0 else '亏了'
        return {
            'success': True,
            'message': f'卖出了{name} {shares:.0f}股，{pnl_word}¥{abs(pnl):.0f}，回到了口袋',
            'pnl': round(pnl, 2)
        }
    
    def get_trades(self, limit=20):
        """获取交易记录"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM trades ORDER BY id DESC LIMIT ?", (limit,))
        trades = [dict(t) for t in c.fetchall()]
        conn.close()
        return trades
    
    def get_trade_stats(self):
        """获取交易统计（大白话版）"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM trades WHERE action = 'SELL' AND pnl IS NOT NULL")
        total_sells = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM trades WHERE action = 'SELL' AND pnl > 0")
        wins = c.fetchone()[0]
        
        c.execute("SELECT AVG(pnl) FROM trades WHERE action = 'SELL' AND pnl > 0")
        avg_win = c.fetchone()[0] or 0
        
        c.execute("SELECT AVG(pnl) FROM trades WHERE action = 'SELL' AND pnl < 0")
        avg_loss = c.fetchone()[0] or 0
        
        c.execute("SELECT COALESCE(SUM(pnl), 0) FROM trades WHERE action = 'SELL'")
        total_pnl = c.fetchone()[0]
        
        conn.close()
        
        win_rate = round(wins / total_sells * 100, 1) if total_sells > 0 else 0
        profit_loss_ratio = round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else round(avg_win, 2)
        
        return {
            'total_sells': total_sells,
            'wins': wins,
            'win_rate': win_rate,
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_loss_ratio': profit_loss_ratio,
            'total_pnl': round(total_pnl, 2),
        }
    
    def reset(self, initial_capital=None):
        """重置模拟盘"""
        if initial_capital is None:
            initial_capital = self.initial_capital
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE account SET cash = ?, in_cool_down = 0, cool_down_start = NULL WHERE id = 1", (initial_capital,))
        c.execute("DELETE FROM positions")
        c.execute("DELETE FROM trades")
        conn.commit()
        conn.close()
        return {'success': True, 'message': f'模拟盘重置完成，口袋里有¥{initial_capital:.0f}'}
