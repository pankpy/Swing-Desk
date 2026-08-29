import logging

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)


class MarketDataProvider:
    """Fetch NSE histories from Yahoo Finance."""

    def fetch(self, symbols: list[str], demo: bool = False) -> tuple[dict[str, pd.DataFrame], list[str]]:
        """Fetch market data for NSE symbols.
        
        Args:
            symbols: List of NSE ticker symbols to fetch
            demo: When True, fetches real Yahoo Finance data. When False, also fetches real data.
                  (Both modes now use the same real data source)
        
        Returns:
            Tuple of (histories dict mapping symbol to OHLCV DataFrame, not_found symbols list)
        """
        histories, not_found = self._fetch_yahoo(symbols)
        return histories, not_found

    @staticmethod
    def _yahoo_candidates(symbol: str) -> str:
        """Convert NSE symbol to Yahoo Finance ticker.
        
        Assumes input is an NSE symbol. Adds .NS suffix if not present.
        """
        normalized = symbol.strip().upper()
        if not normalized.endswith(".NS"):
            normalized = f"{normalized}.NS"
        return normalized

    def _fetch_yahoo(self, symbols: list[str]) -> tuple[dict[str, pd.DataFrame], list[str]]:
        import yfinance as yf

        histories: dict[str, pd.DataFrame] = {}
        not_found: list[str] = []
        
        for symbol in symbols:
            normalized = symbol.strip().upper()
            base_symbol = normalized.removesuffix(".NS")
            ticker = self._yahoo_candidates(normalized)
            
            try:
                frame = yf.download(ticker, period="3y", interval="1d", auto_adjust=True, progress=False)
                if frame.empty:
                    LOGGER.warning("No Yahoo Finance data for %s", ticker)
                    not_found.append(base_symbol)
                    continue
                if isinstance(frame.columns, pd.MultiIndex):
                    frame.columns = frame.columns.get_level_values(0)
                histories[base_symbol] = frame[["Open", "High", "Low", "Close", "Volume"]].dropna()
                LOGGER.info("Loaded %s rows for %s", len(frame), base_symbol)
            except Exception as exc:
                LOGGER.exception("Market data request failed for %s", ticker)
                not_found.append(base_symbol)
        
        return histories, not_found

    @staticmethod
    def _demo_history(symbol: str) -> pd.DataFrame:
        """Generate deterministic synthetic OHLCV data for testing.
        
        Uses a fixed end date (2024-12-31) to ensure reproducible results.
        Each symbol gets a unique seed based on its name, creating consistent
        but distinct price movements.
        """
        seed = sum(ord(char) for char in symbol)
        rng = np.random.default_rng(seed)
        # Use a fixed end date to ensure demo results are reproducible and consistent
        dates = pd.date_range(end=pd.Timestamp("2024-12-31").normalize(), periods=320, freq="B")
        drift = 0.0008 if seed % 3 else -0.0002
        close = 100 * np.exp(np.cumsum(rng.normal(drift, 0.018, len(dates))))
        spread = rng.uniform(0.005, 0.025, len(dates))
        return pd.DataFrame({
            "Open": close * (1 + rng.normal(0, 0.006, len(dates))),
            "High": close * (1 + spread), "Low": close * (1 - spread), "Close": close,
            "Volume": rng.integers(500_000, 5_000_000, len(dates)),
        }, index=dates)
