import numpy as np
import pandas as pd
from unittest.mock import patch

from trade_swing.data_provider import MarketDataProvider
from trade_swing.models import Signal
from trade_swing.scanner import SwingScanner


def test_nse_symbol_is_sent_to_yahoo_with_ns_suffix():
    valid_frame = MarketDataProvider._demo_history("RELIANCE")

    def download(ticker, **kwargs):
        return valid_frame if ticker == "RELIANCE.NS" else pd.DataFrame()

    with patch("yfinance.download", side_effect=download) as mocked_download:
        histories, not_found = MarketDataProvider()._fetch_yahoo(["RELIANCE"])

    assert list(histories) == ["RELIANCE"]
    assert len(histories["RELIANCE"]) == len(valid_frame)
    assert [call.args[0] for call in mocked_download.call_args_list] == ["RELIANCE.NS"]


def test_not_found_stocks_are_tracked():
    with patch("yfinance.download", return_value=pd.DataFrame()) as mocked_download:
        histories, not_found = MarketDataProvider()._fetch_yahoo(["UNKNOWN"])

    assert list(histories) == []
    assert "UNKNOWN" in not_found


def test_yahoo_candidates_nse_only():
    assert MarketDataProvider._yahoo_candidates("KALYANKJIL") == "KALYANKJIL.NS"
    assert MarketDataProvider._yahoo_candidates("TCS.NS") == "TCS.NS"


def test_scan_many_preserves_schema_when_no_histories_are_loaded():
    results = SwingScanner().scan_many({})

    assert "short_score" in results.columns
    assert "positional_score" in results.columns


def test_demo_history_scans_to_a_valid_signal():
    histories, not_found = MarketDataProvider().fetch(["RELIANCE"], demo=True)
    result = SwingScanner().scan("RELIANCE", histories["RELIANCE"])
    assert result.signal in (Signal.STRONG, Signal.WATCH, Signal.SKIP)
    assert 0 <= result.short_score <= result.short_max_score
    assert result.price is not None


def test_short_history_returns_error_instead_of_crashing():
    dates = pd.date_range("2026-01-01", periods=30, freq="B")
    values = np.arange(30, dtype=float) + 100
    history = pd.DataFrame({"Open": values, "High": values + 1, "Low": values - 1, "Close": values, "Volume": 1000}, index=dates)
    result = SwingScanner().scan("TOO_SHORT", history)
    assert result.signal == Signal.ERROR
