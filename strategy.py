
# strategy.py

from indicators import calculate_rsi, calculate_macd
import pandas as pd

def generate_signal(df):
    """
    Accepts a dataframe with OHLCV data and returns a trading signal.
    Returns: 'CALL', 'PUT', or None
    """
    df = df.copy()
    
    # Calculate indicators
    df['rsi'] = calculate_rsi(df)
    df['macd'], df['signal'] = calculate_macd(df)
    
    # Get latest values
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # ENTRY LOGIC
    if latest['rsi'] < 30 and prev['macd'] < prev['signal'] and latest['macd'] > latest['signal']:
        return 'CALL'
    elif latest['rsi'] > 70 and prev['macd'] > prev['signal'] and latest['macd'] < latest['signal']:
        return 'PUT'
    else:
        return None

def should_exit(df, current_position):
    """
    Exits if RSI crosses back near 50 or MACD re-crosses.
    """
    df = df.copy()
    df['rsi'] = calculate_rsi(df)
    df['macd'], df['signal'] = calculate_macd(df)

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    if current_position == 'CALL' and latest['rsi'] > 50:
        return True
    if current_position == 'PUT' and latest['rsi'] < 50:
        return True
    if current_position == 'CALL' and prev['macd'] > prev['signal'] and latest['macd'] < latest['signal']:
        return True
    if current_position == 'PUT' and prev['macd'] < prev['signal'] and latest['macd'] > latest['signal']:
        return True

    return False
