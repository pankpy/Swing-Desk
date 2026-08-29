import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from trade_swing.config import DEFAULT_CONFIG
from trade_swing.data_provider import MarketDataProvider
from trade_swing.llm import TradeBriefingService
from trade_swing.logging_config import configure_logging
from trade_swing.scanner import SwingScanner

configure_logging()
st.set_page_config(page_title="NSE Swing Desk", page_icon="S", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --ink: #17221f;
    --muted: #64736d;
    --mint: #b6e3c1;
    --orange: #f28c5b;
    --paper: #f5f2e9;
}

/* Main app */
.stApp {
    background: var(--paper);
    color: var(--ink);
    font-family: 'Space Grotesk', sans-serif;
}

/* Sidebar */
[data-testid='stSidebar'] {
    background: #173b35;
}

/* Sidebar text - don't force this onto input controls */
[data-testid='stSidebar'] label,
[data-testid='stSidebar'] .stMarkdown,
[data-testid='stSidebar'] p,
[data-testid='stSidebar'] h1,
[data-testid='stSidebar'] h2,
[data-testid='stSidebar'] h3 {
    color: #eff8ed !important;
}

/* Text area */
[data-testid='stSidebar'] textarea {
    color: #17221f !important;
    background-color: #f5f2e9 !important;
    caret-color: #17221f !important;
    -webkit-text-fill-color: #17221f !important;
}

/* Text area placeholder */
[data-testid='stSidebar'] textarea::placeholder {
    color: #64736d !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #64736d !important;
}

/* Text area label */
[data-testid='stSidebar'] [data-testid='stWidgetLabel'] {
    color: #eff8ed !important;
}

/* Sidebar divider */
[data-testid='stSidebar'] hr {
    border-color: rgba(239, 248, 237, 0.25);
}

/* Headings */
h1 {
    font-size: 3.5rem !important;
    letter-spacing: -2px;
    line-height: .95 !important;
}

h2, h3 {
    letter-spacing: -1px;
}

/* Eyebrow */
.eyebrow {
    font: 500 12px 'DM Mono';
    color: var(--orange);
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* Metrics */
.metric {
    border-top: 2px solid var(--ink);
    padding-top: 10px;
}

.metric-label {
    font: 500 11px 'DM Mono';
    color: var(--muted);
    text-transform: uppercase;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
}

/* Buttons */
.stButton > button {
    border-radius: 2px;
    background: var(--orange);
    color: #17221f !important;
    border: 0;
    font-weight: 700;
}

/* DataFrame */
div[data-testid='stDataFrame'] {
    border: 1px solid #c9cec6;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">NSE / SYSTEMATIC SWING RESEARCH</div>',
    unsafe_allow_html=True
)

st.title("Swing Desk")
st.caption("A repeatable daily scan for 1-5 day trades and 1-3 month positions.")

with st.sidebar:
    st.markdown("### Scan controls")
    symbols_text = st.text_area("NSE symbols", "RELIANCE, TCS, INFY, HDFCBANK")
    run_scan = st.button("Run scan", type="primary", width="stretch")
    st.divider()
    st.markdown("**Rules**")
    st.caption("EMA20 / SMA50 / SMA200\n\nRSI14 / MACD 12,26,9\n\nVolume vs 20-day average\n\nATR14 volatility context")

if run_scan or "results" not in st.session_state:
    symbols = [item.strip().upper().removesuffix(".NS") for item in symbols_text.split(",") if item.strip()]
    with st.spinner("Reading the market..."):
        histories, not_found = MarketDataProvider().fetch(symbols)
        st.session_state.results = SwingScanner().scan_many(histories, not_found)
        st.session_state.histories = histories

results: pd.DataFrame = st.session_state.results
strong = int((results.signal == "STRONG").sum())
watch = int((results.signal == "WATCH").sum())
valid = results[results.signal.isin(["STRONG", "WATCH", "SKIP"])]
best = valid.iloc[0].symbol if not valid.empty else "-"

cols = st.columns(4)
for col, label, value in zip(cols, ["Strong setups", "Watchlist", "Stocks scanned", "Top ranked"], [strong, watch, len(results), best]):
    with col:
        st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

st.markdown("## Signal board")
display = results[["symbol", "signal", "short_score", "positional_score", "price", "change_pct", "rsi", "atr_pct", "volume_ratio", "reason"]].copy()
display.columns = ["Symbol", "Signal", "1-5 day /9", "1-3 month /10", "Price", "Day %", "RSI", "ATR %", "Vol x", "Read"]
st.dataframe(display.style.format({"Price": lambda value: f"₹{value:,.2f}" if pd.notna(value) else "-", "Day %": lambda value: f"{value:+.2f}%" if pd.notna(value) else "-", "RSI": lambda value: f"{value:.1f}" if pd.notna(value) else "-", "ATR %": lambda value: f"{value:.2f}%" if pd.notna(value) else "-", "Vol x": lambda value: f"{value:.2f}x" if pd.notna(value) else "-"}), width="stretch", hide_index=True)

if not valid.empty:
    selected = st.selectbox("Inspect a symbol", valid.symbol.tolist(), index=0)
    history = st.session_state.histories[selected]
    chart = go.Figure(go.Candlestick(x=history.index, open=history.Open, high=history.High, low=history.Low, close=history.Close, name=selected))
    chart.update_layout(height=430, template="simple_white", margin=dict(l=10, r=10, t=20, b=10), xaxis_rangeslider_visible=False)
    st.plotly_chart(chart, width="stretch")
    if st.button("Generate AI desk brief"):
        brief = TradeBriefingService(DEFAULT_CONFIG.groq_api_key, DEFAULT_CONFIG.groq_model).explain(results.head(8).to_dict("records"))
        st.info(brief)

st.caption("Research tool only. Signals are rule-based screening outputs, not investment advice. Validate liquidity, news, levels, and risk before acting.")
