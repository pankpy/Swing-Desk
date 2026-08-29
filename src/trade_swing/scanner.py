import logging
from dataclasses import asdict

import pandas as pd

from .indicators import add_indicators
from .models import ScanResult, Signal

LOGGER = logging.getLogger(__name__)


class SwingScanner:
    """Evaluate a stock's OHLCV history with transparent, weighted rules."""

    SHORT_MAX = 9
    POSITIONAL_MAX = 10

    def scan(self, symbol: str, daily_data: pd.DataFrame) -> ScanResult:
        try:
            frame = add_indicators(daily_data).dropna(
                subset=["EMA20", "SMA50", "SMA200", "VolumeSMA20", "RSI14", "MACD", "MACDSignal", "ATR14"]
            )
            full_frame = add_indicators(daily_data)
            if frame.empty or len(full_frame) < 2:
                raise ValueError("not enough history after indicator warm-up")
            row = frame.iloc[-1]
            previous = full_frame.loc[:row.name].iloc[-2]
            prior_breakout = full_frame["Close"].rolling(20).max().shift(1).loc[row.name]
            short_score = sum([
                row.Close > row.EMA20, row.EMA20 > row.SMA50, row.SMA50 > row.SMA200,
                row.RSI14 > 50, row.RSI14 > 60, row.MACD > row.MACDSignal,
                row.MACD > 0, row.Volume > row.VolumeSMA20, row.Close > previous.Close,
            ])
            positional_score = sum([
                row.Close > row.EMA20, row.EMA20 > row.SMA50, row.SMA50 > row.SMA200,
                row.SMA50 > previous.SMA50, row.RSI14 > 50, row.MACD > row.MACDSignal,
                row.MACD > 0, row.Volume > row.VolumeSMA20,
                row.Close > prior_breakout, row.ATR14 / row.Close > 0.01,
            ])
            signal = Signal.STRONG if short_score >= 7 else Signal.WATCH if short_score >= 5 else Signal.SKIP
            return ScanResult(
                symbol=symbol, short_score=short_score, short_max_score=self.SHORT_MAX,
                positional_score=positional_score, positional_max_score=self.POSITIONAL_MAX,
                signal=signal, price=float(row.Close),
                change_pct=float((row.Close / previous.Close - 1) * 100),
                rsi=float(row.RSI14), atr_pct=float(row.ATR14 / row.Close * 100),
                volume_ratio=float(row.Volume / row.VolumeSMA20), reason=self._reason(short_score),
            )
        except Exception as exc:
            LOGGER.exception("Failed scanning %s", symbol)
            return ScanResult(symbol, 0, self.SHORT_MAX, 0, self.POSITIONAL_MAX, Signal.ERROR, reason=str(exc))

    @staticmethod
    def _reason(score: int) -> str:
        if score >= 7:
            return "Trend, momentum and participation align"
        if score >= 5:
            return "Partial alignment; confirm price action"
        return "Trend or momentum confirmation is missing"

    def scan_many(self, histories: dict[str, pd.DataFrame], not_found: list[str] | None = None) -> pd.DataFrame:
        """Scan multiple symbols.
        
        Args:
            histories: Dictionary mapping symbol to OHLCV DataFrame
            not_found: List of symbols that were not found in data source
        
        Returns:
            DataFrame with scan results for all symbols
        """
        if not_found is None:
            not_found = []
        
        results = [asdict(self.scan(symbol, history)) for symbol, history in histories.items()]
        
        # Add NOT_FOUND results for stocks not available in Yahoo Finance
        for symbol in not_found:
            results.append(asdict(ScanResult(
                symbol=symbol, short_score=0, short_max_score=self.SHORT_MAX,
                positional_score=0, positional_max_score=self.POSITIONAL_MAX,
                signal=Signal.NOT_FOUND, reason="Not found in Yahoo Finance"
            )))
        
        columns = list(ScanResult.__dataclass_fields__)
        return pd.DataFrame(results, columns=columns).sort_values(["short_score", "positional_score"], ascending=False)
