# NEO - Financial Monitoring Dashboard
# NEO - 财经监控仪表盘

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web-blue.svg)](https://flask.palletsprojects.com/)

**An AI-powered financial monitoring and trading assistant designed for retail investors. Monitors A-shares, ETFs, gold/metals, and macro indicators in real-time, with built-in risk warnings and scam detection.**

**一款面向散户投资者的 AI 财经监控与交易辅助系统。实时监看 A 股、ETF、贵金属/大宗商品和宏观指标，内置风险预警和套路识别。**

---

## ✨ Features / 功能特点

| Feature | 功能 |
|---------|------|
| 📈 A-Share Monitoring | A 股实时监控（蓝筹、科技、新能源、消费、医药） |
| 📊 ETF Tracking | ETF 实时追踪（沪深300、中证500、创业板、科创50 等） |
| 🥇 Gold & Metals | 贵金属 & 大宗商品监控（黄金、白银、铜、铝、镍、锌等） |
| 🌍 Macro Dashboard | 宏观数据面板（CPI、PPI、M2、社融等） |
| 🧠 AI Assistant | AI 智能助手（本地/外接 API 双模式） |
| ⚠️ Risk Engine | 风控引擎（止损/止盈/回撤预警/冷静期） |
| 🎭 Scam Detector | 套路识别器（散户常见被割套路检测） |
| 💼 Position Advisor | 仓位建议器（鸡蛋别全在一个篮子） |
| 📉 Backtest & Stress Test | 回测引擎 & 压力测试 |
| 🔄 Paper/Real Trading | 模拟盘 & 实盘交易（模拟盘/实盘双模式） |

---

## 🚀 Quick Start / 快速开始

### Prerequisites / 环境要求

- **Python 3.10+**
- **Linux / macOS / Windows**
- **Optional: Local LLM (vLLM) for AI assistant** / 可选：本地大模型 (vLLM) 驱动 AI 助手

### Installation / 安装

```bash
# Clone the repository / 克隆仓库
git clone https://github.com/weikenho/NEO-Finance.git
cd NEO-Finance

# Install dependencies / 安装依赖
pip install flask pandas easytrader

# Start the dashboard / 启动仪表盘
python app.py

# Open in browser / 浏览器打开
open http://127.0.0.1:7878
```

### Configuration / 配置

Edit `config.py` to customize:

修改 `config.py` 可自定义：

- **`ALLOWED_STOCK_POOL`** — Stocks to monitor / 监控股票池
- **`ALLOWED_ETF_POOL`** — ETFs to track / 追踪 ETF 池
- **`METAL_MONITOR`** — Metals to watch / 监控金属
- **`RISK_RULES`** — Risk thresholds / 风控阈值
- **`SIMULATION`** — Paper trading settings / 模拟盘设置
- **`REAL_TRADING`** — Live trading settings (easytrader) / 实盘设置

---

## 📁 Project Structure / 项目结构

```
NEO-Finance/
├── app.py                  # Main Flask application / 主应用
├── config.py               # Configuration / 配置文件
├── data.py                 # ETF data fetching / ETF 数据抓取
├── stock_gold_data.py      # Stock & gold data / 股票和黄金数据
├── metal_data.py           # Metal prices / 金属价格
├── macro_data.py           # Macro indicators / 宏观指标
├── risk_engine.py          # Risk engine & warnings / 风控引擎
├── analysis.py             # News & technical analysis / 新闻与技术分析
├── position_advisor.py     # Position suggestions / 仓位建议
├── backtest_engine.py      # Backtest engine / 回测引擎
├── stress_tester.py        # Stress testing / 压力测试
├── sim_trader.py           # Paper trading / 模拟交易
├── real_trader.py          # Live trading (easytrader) / 实盘交易
├── static/                 # Static assets / 静态资源
├── templates/              # Flask templates / 模板文件
├── data/                   # SQLite database / 数据库
└── requirements.txt        # Python dependencies / 依赖列表
```

---

## 🖥️ Screenshots / 界面截图

### Dashboard / 仪表盘

The main dashboard shows real-time A-shares, ETFs, gold/metals, and macro indicators:

主仪表盘显示实时 A 股、ETF、贵金属/大宗商品和宏观指标。

### Risk Warnings / 风险预警

AI-powered risk engine detects common retail investor pitfalls:

AI 风控引擎识别散户常见陷阱：止损、止盈、回撤、冷静期等。

### AI Assistant / AI 助手

Integrate local LLM or remote API for intelligent market insights:

支持接入本地大模型或远程 API，获取智能市场分析。

---

## 🎯 Why NEO? / 为什么叫 NEO？

> **NEO** stands for **"Never Expect Overvaluation"** — 永远不要高估市场。

The philosophy behind NEO is simple: **protect your principal first, then make money.**

NEO 的核心理念很简单：**先保住本金，再谈赚钱。**

---

## 📜 License / 许可证

**MIT License** — Free to use, modify, and distribute.

[MIT License](LICENSE)

---

## 🙏 Credits / 致谢

- Built with **Flask**, **Pandas**, and **EasyTrader**
- AI assistant powered by **vLLM** + **Qwen3.6**
- Market data from **Sina Finance**, **East Money**, and **Shanghai Gold Exchange**

---

## 📧 Contact / 联系

- **Author**: weikenho
- **GitHub**: https://github.com/weikenho/NEO-Finance
- **Star ⭐ if you like it!** / 喜欢就点个 Star！
