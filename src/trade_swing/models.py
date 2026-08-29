from dataclasses import dataclass
from enum import StrEnum


class Signal(StrEnum):
    STRONG = "STRONG"
    WATCH = "WATCH"
    SKIP = "SKIP"
    ERROR = "ERROR"
    NOT_FOUND = "NOT FOUND"


@dataclass(frozen=True)
class ScanResult:
    symbol: str
    short_score: int
    short_max_score: int
    positional_score: int
    positional_max_score: int
    signal: Signal
    price: float | None = None
    change_pct: float | None = None
    rsi: float | None = None
    atr_pct: float | None = None
    volume_ratio: float | None = None
    reason: str = ""

    @property
    def short_score_pct(self) -> float:
        return self.short_score / self.short_max_score * 100

    @property
    def positional_score_pct(self) -> float:
        return self.positional_score / self.positional_max_score * 100
