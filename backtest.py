import datetime as dt
import pandas as pd
import time
import csv
import os
import mplfinance as mpf
from auth_smartapi import login
from strategy import generate_signal
from SmartApi.smartConnect import SmartConnect

# Setup
symbol = "NIFTY"
symboltoken = "99926009"
exchange = "NSE"
interval = "FIVE_MINUTE"
capital = 100000  # Starting capital

# Create output directory
os.makedirs("backtest_logs", exist_ok=True)

def fetch_full_day_candles(api: SmartConnect, date_str: str):
    from_date = f"{date_str} 09:15"
    to_date = f"{date_str} 15:30"

    try:
        params = {
            "exchange": exchange,
            "symboltoken": symboltoken,
            "interval": interval,
            "fromdate": from_date,
            "todate": to_date
        }

        response = api.getCandleData(params)

        if isinstance(response, dict) and response.get("status") and response.get("data"):
            candles = response["data"]["candles"]
        else:
            print("❌ Error in candle API response:", response)
            return pd.DataFrame()

        df = pd.DataFrame(candles, columns=["datetime", "open", "high", "low", "close", "volume"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)
        return df

    except Exception as e:
        print(f"❌ Exception while fetching candles: {e}")
        return pd.DataFrame()


def backtest_day(api, date_str: str):
    df = fetch_full_day_candles(api, date_str)
    if df.empty or len(df) < 5:
        print("❌ Not enough data to backtest.")
        return pd.DataFrame()

    trades = []
    position = None
    entry_price = 0

    for i in range(5, len(df)):
        window = df.iloc[:i]
        signal = generate_signal(window)

        current_close = df.iloc[i]["close"]
        timestamp = df.index[i]

        if signal == "buy" and position is None:
            position = "long"
            entry_price = current_close
            trades.append({"time": timestamp, "action": "BUY", "price": current_close})
        elif signal == "sell" and position == "long":
            pnl = current_close - entry_price
            trades.append({"time": timestamp, "action": "SELL", "price": current_close, "pnl": pnl})
            position = None

    df_trades = pd.DataFrame(trades)
    df_trades["date"] = date_str

    log_path = f"backtest_logs/{symbol}_{date_str}.csv"
    df_trades.to_csv(log_path, index=False)
    print(f"✅ Trade log saved: {log_path}")

    # Plot safely
    try:
        if not df_trades.empty:
            buy_signals = df_trades[df_trades["action"] == "BUY"]
            sell_signals = df_trades[df_trades["action"] == "SELL"]

            apds = []

            if not buy_signals.empty:
                apds.append(mpf.make_addplot(buy_signals["price"], scatter=True, markersize=100,
                                              marker="^", color="green", panel=0))
            if not sell_signals.empty:
                apds.append(mpf.make_addplot(sell_signals["price"], scatter=True, markersize=100,
                                              marker="v", color="red", panel=0))

            mpf.plot(df, type="candle", style="charles", addplot=apds,
                     title=f"{symbol} {date_str}", ylabel="Price",
                     savefig=f"backtest_logs/{symbol}_{date_str}.png")
            print(f"📈 Chart saved to backtest_logs/{symbol}_{date_str}.png")
        else:
            print("⚠️ No trades to plot.")
    except Exception as e:
        print(f"⚠️ Plotting error: {e}")

    return df_trades

if __name__ == "__main__":
    api, token = login()
    date = input("Enter date to backtest (YYYY-MM-DD): ").strip()
    df_trades = backtest_day(api, date)

    if not df_trades.empty and "pnl" in df_trades.columns:
        total_pnl = df_trades["pnl"].sum()
        print(f"💰 Total PnL for {date}: ₹{total_pnl:.2f}")
