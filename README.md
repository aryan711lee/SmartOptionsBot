# 🧠 SmartOptionsBot

An advanced algorithmic options trading bot that leverages Delta, RSI, and MACD indicators to make intelligent trading decisions in volatile markets. Designed for NIFTY/BANKNIFTY weekly options, the bot includes a complete backtesting engine, paper trading system, and performance tracking — built using the Angel One SmartAPI.

---

## 🚀 Features

- 📉 **Delta-Neutral Strategy**: Dynamically hedges option positions based on Delta values to minimize directional risk.
- 📊 **Technical Indicators**: Uses **RSI** (Relative Strength Index) and **MACD** (Moving Average Convergence Divergence) for momentum-based entry and exit signals.
- 🧪 **Backtesting Engine**: Simulates strategy performance on historical data with accurate trade execution and logging.
- 💸 **Paper Trading Module**: Emulates real-time trades without financial risk using Angel One’s SmartAPI.
- 📈 **PnL Tracking**: Logs profit & loss, win rate, and trade history for performance evaluation.
- 🔧 **Modular Design**: Easy to modify strategy parameters and indicators for experimentation.

---

## 🧠 Strategy Overview

### 📌 Entry Conditions
- **RSI Crossover**: Buy call/put when RSI crosses a threshold (e.g., below 30 or above 70).
- **MACD Confirmation**: Confirm momentum with MACD crossover (signal > MACD line).
- **Delta Check**: Only enter trades with Delta values within a safe neutral range (e.g., ±0.2).

### 📌 Exit Conditions
- RSI or MACD reversal
- Target profit or stop-loss hit
- Change in Delta sensitivity or volatility spike

---

## 🛠 Tech Stack

| Tool             | Purpose                           |
|------------------|-----------------------------------|
| `Python`         | Core programming language         |
| `NumPy`          | Numerical calculations            |
| `Pandas`         | Data manipulation and analysis    |
| `Matplotlib`     | Visualizing trades and results    |
| `Angel One API`  | Market data, paper trades         |
| `datetime`       | Timeframe management              |

---

## 📈 Sample Results (Backtest)

| Metric           | Value         |
|------------------|---------------|
| Win Rate         | 64%           |
| Net PnL          | +12.5%        |
| Duration         | 3 months      |
| Trades Executed  | 94            |

> ⚠️ These results are based on backtested data and may vary in real-time conditions.

---

## 🔗 Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/SmartOptionsBot.git
cd SmartOptionsBot

