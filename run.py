# run.py

import time
import pandas as pd
from datetime import datetime, timedelta

from SmartApi import SmartConnect
from auth_smartapi import login
from strategy import generate_signal, should_exit
from option_selector import get_atm_option

# ========== CONFIG ==========
INDEX_SYMBOL   = "NIFTY"
INDEX_TOKEN    = "99926000"    # From instruments.csv
EXCHANGE       = "NSE"
INTERVAL       = "ONE_MINUTE" # ONE_MINUTE, FIVE_MINUTE, etc.
QUANTITY       = 50
SLEEP_SECONDS  = 60           # 5 minutes
# ============================

def is_market_open(now=None):
    now = now or datetime.now()
    # Market open window: 09:15–15:30 IST
    open_time  = now.replace(hour=9,  minute=15, second=0, microsecond=0)
    close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return open_time <= now <= close_time

def fetch_ohlc(api, symbol_token):
    """
    Fetch the last 2 FIVE_MINUTE candles up to now, but only during market hours.
    Returns a DataFrame with >=2 rows, else an empty DataFrame.
    """
    now = datetime.now()
    if not is_market_open(now):
        # Outside market hours, no intraday candles
        return pd.DataFrame()

    # Sliding window of last 2 candles = 10 minutes
    window = 4 * 1  # minutes
    from_dt = (now - timedelta(minutes=window)).strftime("%Y-%m-%d %H:%M")
    to_dt   = now.strftime("%Y-%m-%d %H:%M")

    payload = {
        "exchange":    EXCHANGE,
        "symboltoken": symbol_token,
        "interval":    INTERVAL,
        "fromdate":    from_dt,
        "todate":      to_dt
    }

    try:
        resp = api.getCandleData(payload)
        data = resp.get("data", {})
        candles = None
        if isinstance(data, dict) and "candles" in data:
            candles = data["candles"]
        elif isinstance(resp, list):
            candles = resp
        elif isinstance(data, list):
            candles = data

        if not candles or not isinstance(candles, list):
            raise ValueError("No valid candles in response")

        df = pd.DataFrame(candles, columns=["time","open","high","low","close","volume"])

        # Parse time column: try ms-epoch, else ISO
        try:
            df["time"] = pd.to_datetime(df["time"].astype(int), unit="ms")
        except Exception:
            df["time"] = pd.to_datetime(df["time"])

        df = df.sort_values("time").reset_index(drop=True)

        return df

    except Exception as e:
        print(f"❌ OHLC fetch error ({e}). Skipping this cycle.")
        return pd.DataFrame()


def fetch_ltp(api, symbol, token):
    resp = api.ltpData(EXCHANGE, symbol, token)
    # safe extraction
    return float(resp.get("data", {}).get("ltp", 0.0))

def main_loop():
    api, jwt = login()
    # SmartConnect is already authenticated—no set_session() needed

    current_pos = None
    entry_price = 0.0
    total_pnl   = 0.0

    while True:
        now = datetime.now()

        # Stop after market close
        if now.hour > 15 or (now.hour == 15 and now.minute >= 30):
            print("⏲ Market is closed. Exiting.")
            break

        # 1) Fetch intraday candles
        df_index = fetch_ohlc(api, INDEX_TOKEN)

        # 2) Ensure we have at least 2 candles
        if df_index.shape[0] < 2:
            print(f"[{now.strftime('%H:%M')}] Not enough candles ({df_index.shape[0]}). Waiting...")
            time.sleep(SLEEP_SECONDS)
            continue

        # 3) Generate signal
        try:
            signal = generate_signal(df_index)
        except Exception as e:
            print("⚠️ Signal generation error:", e)
            time.sleep(SLEEP_SECONDS)
            continue

        print(f"[{now.strftime('%H:%M')}] Signal: {signal}")

        # 4) Entry logic
        if current_pos is None and signal in ("CALL","PUT"):
            idx_ltp = df_index["close"].iloc[-1]
            opt     = get_atm_option(INDEX_SYMBOL, idx_ltp, signal)
            opt_ltp = fetch_ltp(api, opt["tradingsymbol"], opt["token"])
            current_pos = signal
            entry_price = opt_ltp
            print(f"➕ BUY {signal} @ ₹{entry_price:.2f} ({opt['tradingsymbol']})")

        # 5) Exit logic
        elif current_pos:
            if should_exit(df_index, current_pos):
                idx_ltp   = df_index["close"].iloc[-1]
                opt       = get_atm_option(INDEX_SYMBOL, idx_ltp, current_pos)
                exit_price= fetch_ltp(api, opt["tradingsymbol"], opt["token"])
                pnl = (exit_price - entry_price)*QUANTITY \
                      if current_pos=="CALL" else \
                      (entry_price - exit_price)*QUANTITY
                total_pnl += pnl
                print(f"➖ EXIT {current_pos} @ ₹{exit_price:.2f} | PnL: ₹{pnl:.2f} | Total PnL: ₹{total_pnl:.2f}")
                current_pos = None
                entry_price = 0.0
            else:
                print(f"… Holding {current_pos}")

        print(f"⏲ Sleeping for {SLEEP_SECONDS//60} min...\n")
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main_loop()
