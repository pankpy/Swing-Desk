# NSE Swing Desk

Production-oriented Streamlit scanner for NSE stocks. It evaluates a symbol list using EMA20, SMA50, SMA200, RSI14, MACD, volume participation, and ATR volatility context.

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│        Streamlit Web Interface              │
│  (app.py - UI, Interactive Controls)        │
└──────────────┬──────────────────────────────┘
               │
        ┌──────┴──────┬─────────────┬──────────────┐
        │             │             │              │
┌───────▼────────┐ ┌─┴────────┐ ┌──┴────────────┐ │
│ Data Provider  │ │ Scanner  │ │ LLM Service  │ │
│ (Yahoo Finance)│ │(Signals) │ │ (AI Brief)   │ │
└────────────────┘ └──────────┘ └──────────────┘ │
                                                  │
        ┌─────────────────────────────────────────┘
        │
   ┌────▼──────────────────────┐
   │   Indicators Module        │
   │ (EMA, SMA, RSI, MACD, ATR) │
   └────────────────────────────┘
```

**Key Components:**

- **Data Provider** (`data_provider.py`) - Fetches OHLCV data from Yahoo Finance with demo mode support
- **Scanner** (`scanner.py`) - Evaluates symbols using weighted technical rules (9-point short score, 10-point positional score)
- **Indicators** (`indicators.py`) - Computes EMA20, SMA50, SMA200, RSI14, MACD, ATR14, volume participation
- **LLM Service** (`llm.py`) - Optional Groq-powered AI desk brief generator
- **Models** (`models.py`) - Data classes for signals and scan results
- **Config** (`config.py`) - Centralized configuration management

## Project Structure

```
TRADE_swing/
│
├── app.py                          # Main Streamlit application entry point
├── README.md                       # This file
├── requirements.txt                # Python dependencies
│
├── src/                            # Source code package
│   └── trade_swing/
│       ├── __init__.py
│       ├── config.py               # Configuration defaults and settings
│       ├── models.py               # Pydantic data models (ScanResult, Signal)
│       ├── data_provider.py        # Yahoo Finance data fetcher with demo mode
│       ├── indicators.py           # Technical indicator calculations
│       ├── scanner.py              # Core scanning logic and scoring
│       ├── llm.py                  # Groq LLM integration for market briefs
│       └── logging_config.py       # Logging configuration
│
├── tests/                          # Test suite
│   └── test_scanner.py             # Unit tests for scanner
│
├── logs/                           # Application logs directory
│
└── venv/                           # Python virtual environment (created locally)
```

**Directory Descriptions:**

- **`app.py`** - Streamlit UI orchestrator; manages sidebar inputs, data flow, and visualization
- **`src/trade_swing/`** - Core business logic organized into focused modules
- **`tests/`** - Pytest test suite for validation and regression testing
- **`logs/`** - Runtime logs for debugging and monitoring

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit ≥1.38 | Interactive web interface, real-time updates |
| **Data Processing** | pandas ≥2.2, numpy ≥2.0 | Time-series analysis, indicator computation |
| **Data Source** | yfinance ≥0.2.40 | NSE OHLCV data retrieval |
| **Visualization** | Plotly ≥5.24 | Interactive charts and technical analysis plots |
| **AI/LLM** | Groq ≥0.11 | Optional LLM-powered market insights (needs API key) |
| **Configuration** | python-dotenv ≥1.0 | Environment variable management |
| **Data I/O** | openpyxl ≥3.1 | Excel export support |
| **Testing** | pytest ≥8 | Unit test framework |
| **Language** | Python 3.11+ | Core application |

## Run

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = ".\src"
streamlit run app.py
```

**Supported Data Source:** Yahoo Finance provides NSE stock data. Enter NSE symbols (e.g., RELIANCE, TCS, INFY, HDFCBANK). Stocks not found in Yahoo Finance will display as "NOT FOUND" in the results table.

Copy `.env.example` to `.env` and add `GROQ_API_KEY` only when the optional AI desk brief is needed.

The short score targets 1-5 day trades. The positional score adds longer-horizon trend slope, breakout, and volatility checks for 1-3 month candidates. These outputs are screening research, not trade instructions.

## Disclaimer

**⚠️ IMPORTANT LEGAL NOTICE**

This tool is provided for **educational and research purposes only**. It is not financial advice, and it does not constitute a recommendation to buy, sell, or hold any security.

- **No Guarantee of Accuracy** - The technical indicators, scores, and signals are generated algorithmically based on historical price data. Past performance does not guarantee future results. Market conditions change rapidly and unpredictably.

- **Not Investment Advice** - The output should never be used as the sole basis for investment decisions. Always consult with a licensed financial advisor before making any trades or investment decisions.

- **Risk Disclaimer** - Trading and investing in securities involves substantial risk of loss. You could lose part or all of your investment. Only invest money you can afford to lose completely.

- **Data Quality** - This application relies on third-party data sources (Yahoo Finance). Errors, delays, or gaps in data may affect analysis accuracy.

- **Use at Your Own Risk** - Users assume full responsibility for any decisions made based on information provided by this tool. The developers and maintainers are not liable for any losses or damages resulting from its use.

- **Regulatory Compliance** - Users are responsible for complying with all applicable laws and regulations in their jurisdiction regarding securities trading and investment.

By using this application, you acknowledge that you have read, understood, and agree to these terms.
