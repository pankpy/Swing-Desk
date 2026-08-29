import pandas as pd


def add_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Add the indicators used by both horizons to an OHLCV frame."""
    frame = data.copy().sort_index()
    close = frame["Close"]
    frame["EMA20"] = close.ewm(span=20, adjust=False).mean()
    frame["SMA50"] = close.rolling(50).mean()
    frame["SMA200"] = close.rolling(200).mean()
    frame["VolumeSMA20"] = frame["Volume"].rolling(20).mean()
    delta = close.diff()
    gains = delta.clip(lower=0).rolling(14).mean()
    losses = -delta.clip(upper=0).rolling(14).mean()
    frame["RSI14"] = 100 - (100 / (1 + gains.div(losses.replace(0, pd.NA))))
    fast = close.ewm(span=12, adjust=False).mean()
    slow = close.ewm(span=26, adjust=False).mean()
    frame["MACD"] = fast - slow
    frame["MACDSignal"] = frame["MACD"].ewm(span=9, adjust=False).mean()
    true_range = pd.concat(
        [frame["High"] - frame["Low"], (frame["High"] - close.shift()).abs(),
         (frame["Low"] - close.shift()).abs()], axis=1
    ).max(axis=1)
    frame["ATR14"] = true_range.rolling(14).mean()
    return frame
