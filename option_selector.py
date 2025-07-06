# option_selector.py

import pandas as pd
from datetime import datetime

INSTRUMENTS_CSV = "instruments.csv"

def load_instruments():
    return pd.read_csv(INSTRUMENTS_CSV, low_memory=False)

def get_atm_option(symbol, ltp, option_type="CE"):
    """
    Returns the ATM option (closest strike to LTP) for the given
    index symbol and its LTP, for the nearest expiry.
    """
    df = load_instruments()

    # 1. Filter to NFO options on that underlying
    df = df[(df['instrumenttype'] == 'OPTIDX') &
            (df['exch_seg']       == 'NFO') &
            (df['name']           == symbol) ]

    # 2. Filter by CALL/PUT via symbol suffix
    df = df[df['symbol'].str.endswith(option_type)]

    # 3. Parse expiry and pick the nearest future one
    df['expiry_dt'] = pd.to_datetime(df['expiry'], format='%d%b%Y', errors='coerce')
    today = pd.to_datetime(datetime.now().date())
    df = df[df['expiry_dt'] >= today]
    nearest_expiry = df['expiry_dt'].min()
    df = df[df['expiry_dt'] == nearest_expiry]

    # 4. Compute strike in rupees, then find closest to LTP
    #    File’s 'strike' is in paise (×100), so divide by 100
    df['strike_rupee'] = df['strike'] / 100.0

    # Find row with minimal |strike_rupee - ltp|
    df['diff'] = (df['strike_rupee'] - ltp).abs()
    atm_row = df.loc[df['diff'].idxmin()]

    return {
        "tradingsymbol": atm_row['symbol'],     # e.g. "NIFTY10JUL2523200CE"
        "token"        : str(atm_row['token']), # e.g. "36688"
        "strike"       : atm_row['strike_rupee']
    }
