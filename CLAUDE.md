# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Guidelines

NEVER USE ANY MOCK DATA OR HARDCODED DATA IN THIS PROJECT> ONLY REAL DATA AND REAL CALCULATIONS>

**BEFORE making any changes to this codebase:**
1. **Read QA.md thoroughly** - Contains 11 critical bug prevention rules from major production issues
2. **Apply ALL QA rules** - Essential for preventing inheritance, data contract, and API integration bugs
3. **Verify inheritance chains** - Check attribute/method availability before accessing (QA Rule 1 & 2)
4. **Use defensive programming** - Always use .get() methods and provide defaults (QA Rule 5)
5. **Test with minimal data** - Verify startup behavior when market data is limited (QA Rule 4)
6. **Update QA.md** - Document any new bugs/fixes discovered

## Project Architecture

### Multi-Asset Algorithmic Trading System
Production-grade system targeting 5-10% monthly returns through AI-powered trading across:
- **📊 Options Trading**: Real Alpaca API integration with sophisticated strategies
- **₿ Cryptocurrency Trading**: 24/7 trading across 9 cryptocurrencies with session awareness
- **📈 Stock Trading**: 41 symbols across 4 tiers with unlimited profitable trades
- **🧠 Market Intelligence**: OpenAI o4-mini powered analysis with web search integration

### Core Production Architecture
```
ModularOrchestrator (Production Entry Point - modular_production_main.py)
├── OptionsModule (modular/options_module.py) 
├── CryptoModule (modular/crypto_module.py) - Unlimited allocation
├── StocksModule (modular/stocks_module.py) - Unlimited positions
├── MarketIntelligenceModule (modular/market_intelligence_module.py)
├── MLOptimizer (modular/ml_optimizer.py)
├── RiskManager (risk_manager.py) - Unlimited limits for system improvement
├── OrderExecutor (modular/order_executor.py) - Firebase trade tracking
└── TradeHistoryTracker (trade_history_tracker.py) - Safety controls
```

### Modular System Integration
```python
# All modules inherit from base_module.py TradingModule
class TradingModule:
    def analyze_opportunities(self) -> List[TradingOpportunity]
    def execute_trades(self, opportunities) -> List[TradeResult]
    def monitor_positions(self) -> List[PositionUpdate]
    
# Orchestrator manages module lifecycle
orchestrator = ModularOrchestrator()
orchestrator.register_module('crypto', CryptoModule())
orchestrator.register_module('stocks', StocksModule()) 
orchestrator.register_module('options', OptionsModule())
orchestrator.run_single_cycle()  # Execute all modules
```

### ML Profit Learning System (Critical)
```python
# Entry trades linked to exit trades for complete P&L tracking
entry_trade = {
    'entry_trade_id': trade_id,  # Links to Firebase record
    'symbol': 'BTCUSD',
    'entry_price': 50000,
    'quantity': 0.1
}

# Exit processing updates entry trade with ACTUAL profit/loss
exit_outcome = {
    'profit_loss': 750.50,  # Real P&L, not execution success
    'exit_reason': 'profit_target',
    'final_outcome': 'profitable'  # Based on actual profit
}
```

## Essential Development Commands

### Primary Entry Points
```bash
# Production system (Railway deployment)
python modular_production_main.py

# Market Intelligence testing (requires OPENAI_API_KEY)
python test_production_intelligence.py

# Complete system integration test
python test_phase4_complete.py

# Local debugging with full output (LEGACY - moved to legacy/debug/)
# Use modular system for current debugging instead

# Performance analysis (mandatory weekly)
python analyze_trading_performance.py
```

### Testing Framework
```bash
# Core system tests (run before deployment)
python test_modular_framework.py
python test_ml_integration_full.py
python test_market_intelligence.py

# Safety system testing (CRITICAL)
python test_trade_history_tracking.py    # Trade history safety controls
python test_firebase_trade_history.py    # Firebase integration
python test_limits_removed.py            # Verify limits properly removed

# Individual module tests
python tests/modules/test_crypto_module.py  # Includes mean reversion tests
python tests/modules/test_options_module.py
python tests/modules/test_stocks_module.py

# Integration and performance tests
python test_phase4_complete.py  # Full system integration
python test_production_intelligence.py  # Market intelligence testing
python analyze_trading_performance.py  # Performance analysis (mandatory weekly)

# Run single test example
python -m pytest tests/modules/test_crypto_module.py::TestCryptoModule::test_calculate_crypto_mean_reversion_oversold -v
```

### Safety Testing (MANDATORY before deployment)
```bash
# Test that safety controls prevent rapid-fire trading
python test_trade_history_tracking.py

# Verify Firebase trade persistence
python test_firebase_trade_history.py

# Confirm all limits properly removed
python test_limits_removed.py

# Live performance monitoring
python quick_performance_check.py
```

### Emergency Commands
```bash
# Cancel all active orders immediately
python emergency_cancel_all_orders.py

# Debug specific trading cycles locally
python debug_cycle.py 2>&1 | grep -A 10 "INTELLIGENT EXIT"
python debug_cycle.py 2>&1 | grep -A 5 "ML Predictions"
```

### Railway Deployment
```bash
# Monitor deployment logs
railway logs

# Verify deployment status
railway status

# Test deployment verification
python railway_deploy.py

# Link to project (if needed)
railway link

# Deploy to production
git push  # Automatic deployment on push
```

## Critical Environment Variables

### Required for Production
```bash
# Alpaca Trading API (Paper Trading)
ALPACA_PAPER_API_KEY=your_paper_key
ALPACA_PAPER_SECRET_KEY=your_paper_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Market Intelligence (NEW - June 2025)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=o4-mini
INTELLIGENCE_CYCLE_HOURS=6

# System Configuration
EXECUTION_ENABLED=true
MODULAR_SYSTEM=true
ML_OPTIMIZATION=true
INTRADAY_CYCLE_DELAY=60
```

### Alpaca Data Quality & Subscription Tiers

**Data quality depends on Alpaca account subscription:**

**Basic Plan (Free):**
- IEX real-time data only
- 15-minute delayed historical data  
- 30 symbol WebSocket subscriptions
- 200 historical API calls/minute
- Suitable for basic algorithmic trading

**Algo Trader Plus ($99/month):**
- Full market real-time data (all exchanges)
- Unlimited historical data access
- Unlimited WebSocket subscriptions  
- 10,000 historical API calls/minute
- Optimal for high-frequency algorithmic trading

### Real-Time Data Streaming (WebSocket)

**For optimal algorithmic trading, consider WebSocket streaming instead of REST polling:**

**Stock Data Streaming:**
```python
# WebSocket endpoint: wss://stream.data.alpaca.markets/v2/{feed}
# Feed types: 'iex' (Basic), 'sip' (Algo Trader Plus), 'delayed_sip'
# Channels: trades, quotes, bars, corrections, status, imbalances
```

**Crypto Data Streaming:**
```python
# WebSocket endpoint: wss://stream.data.alpaca.markets/v1beta3/crypto/us
# Channels: trades, quotes, bars, orderbooks
# Symbols: "BTC/USD", "ETH/USD", etc.
```

**Options Data Streaming:**
```python
# WebSocket endpoint: wss://stream.data.alpaca.markets/v1beta1/{feed}
# Feed types: 'indicative', 'opra' (requires subscription)
# MsgPack format only, real-time option prices
```

**News Data Streaming:**
```python
# WebSocket endpoint: wss://stream.data.alpaca.markets/v1beta1/news
# Real-time news with symbol associations for sentiment-based trading
```

### Optional Configuration
```bash
# Trading Modules
OPTIONS_TRADING=true
CRYPTO_TRADING=true  
STOCKS_TRADING=true
MARKET_INTELLIGENCE=true

# Risk Management
MARKET_TIER=2
MIN_CONFIDENCE=0.6
MIN_TECHNICAL_CONFIDENCE=0.6

# Firebase Integration (for ML learning)
FIREBASE_SERVICE_ACCOUNT={"type":"service_account",...}
```

## Data Architecture Patterns

### Trade Success Definition (Critical Fix - June 2025)
```python
# FIXED: TradeResult.success now requires ACTUAL PROFIT
@property
def success(self) -> bool:
    return (self.status == TradeStatus.EXECUTED and 
            self.pnl is not None and 
            self.pnl > 0)
```

### Quote Data Freshness Validation
```python
# All quote retrieval includes data age validation
if hasattr(quote, 'timestamp') and quote.timestamp:
    age_seconds = (datetime.now(timezone.utc) - quote.timestamp).total_seconds()
    if age_seconds > 300:  # 5-minute threshold
        self.logger.warning(f"Quote data is {age_seconds:.0f}s old")
```

### Data Optimization for Algorithmic Trading

**Current Implementation (REST API Polling):**
- 60-second trading cycles with REST API calls
- Data freshness validation on each quote
- Works with both Basic and Algo Trader Plus subscriptions

**Recommended Upgrade (WebSocket Streaming):**
```python
# For high-frequency trading, implement WebSocket streaming:
from alpaca.data.live import StockDataStream

stream = StockDataStream(api_key, secret_key)

@stream.on_quote
async def on_quote(data):
    # Real-time quote processing for immediate decisions
    symbol = data.symbol
    bid_price = data.bid_price
    ask_price = data.ask_price
    # Trigger trading logic immediately
```

**Performance Comparison:**
- **REST Polling**: 60-second cycles, potential data age issues
- **WebSocket Streaming**: Millisecond latency, true real-time responses

### Intelligence Module Response Format
```python
# All AI analysis returns standardized format
{
    'timestamp': datetime.now().isoformat(),
    'status': 'success',  # Always include
    'data': {},           # Analysis results
    'confidence': float,  # 0.0 to 1.0
    'reasoning': str      # AI explanation
}
```

## QA Rules Summary (From QA.md)

1. **Attribute Consistency**: Verify inheritance chain compatibility
2. **Method Interface**: Consistent signatures across phases  
3. **Parameter Validation**: Check parameter counts before method calls
4. **Data Structure Integrity**: Ensure complete data formats between modules
5. **Defensive Programming**: Use .get() methods, provide defaults
6. **Import Dependencies**: Verify module availability before usage
7. **Exception Handling**: Graceful degradation on failures
8. **Mock Data Detection**: Distinguish real vs test data
9. **API Response Validation**: Handle Alpaca API object variations
10. **Order Executor Implementation**: Proper dependency injection
11. **Firebase Method Signatures**: Correct parameter passing

## Production Health Monitoring

### Health Check Endpoints (Railway)
```bash
# Railway deployment URL (update with actual URL)
export RAILWAY_URL="https://satisfied-commitment.railway.app"

# Basic system health
curl $RAILWAY_URL/health

# Safety controls status (CRITICAL)
curl $RAILWAY_URL/safety

# Market Intelligence status  
curl $RAILWAY_URL/intelligence

# Comprehensive debug information
curl $RAILWAY_URL/intelligence/debug

# Current market signals
curl $RAILWAY_URL/intelligence/signals

# Safety circuit breaker reset (EMERGENCY ONLY)
curl -X POST $RAILWAY_URL/safety/reset
```

### Critical Success Indicators
```bash
✅ Alpaca API connected - Account: [account_id]
✅ Market Intelligence module registered  
✅ Active modules: ['options', 'crypto', 'stocks', 'market_intelligence']
🧠 Starting daily market intelligence cycle
🎯 Cycle X completed: {'total_opportunities': N, 'successful_trades': M}
```

## Smart Leverage System (5% Monthly ROI Target)

### Performance-Based Crypto Allocation
- **Emergency Mode** (Monthly loss >5%): 20% allocation
- **Learning Phase** (Win rate <45%): 25% allocation  
- **Stable Phase** (Win rate 45-60%): 40% allocation
- **Profitable Phase** (Win rate >60%): 60% allocation

### 5% Monthly ROI Mathematics
```python
# Allocation vs Required Crypto Returns for 5% Monthly Portfolio ROI:
# 25% allocation → 20% monthly crypto returns needed
# 40% allocation → 12.5% monthly crypto returns needed  
# 60% allocation → 8.3% monthly crypto returns needed
```

### Risk Management Configuration

#### Portfolio Allocation Limits
- **Options**: 30% maximum exposure
- **Crypto**: SMART ALLOCATION (20-60% performance-based) with 2x leverage  
- **Stocks**: 50% maximum, unlimited positions
- **Sector Limits**: 40% maximum per sector
- **Position Limits**: 15% maximum per symbol

#### Exit Management (Allocation-Aware)
- **Over-allocated Crypto**: 2% profit exits (vs 25% normal)
- **Over-allocated Stocks**: 1.5% profit exits  
- **Over-allocated Options**: 25% profit exits (vs 100% normal)

## Common Error Patterns & Solutions

### 1. Alpaca API Integration Issues
```python
# WRONG: Assuming all position objects have same attributes
entry_price = position.avg_entry_price

# RIGHT: Defensive attribute access (QA Rule 9)
if hasattr(position, 'avg_entry_price'):
    entry_price = float(position.avg_entry_price)
elif hasattr(position, 'cost_basis'):  
    entry_price = float(position.cost_basis)
else:
    entry_price = float(position.market_value) / float(position.qty)
```

### 2. Module Communication Patterns
```python
# All modules inherit from TradingModule base class
# Common methods: analyze_opportunities(), execute_trades(), monitor_positions()
# Use ModuleRegistry for registration and health monitoring
```

### 3. ML Learning Data Flow
```python
# Entry: save_ml_enhanced_trade() returns trade_id
trade_id = module.save_ml_enhanced_trade(trade_data)

# Exit: update_ml_trade_outcome() links final P&L  
module.update_ml_trade_outcome(trade_id, {'profit_loss': actual_pnl})
```

### Smart Allocation Methods (Critical Implementation)
```python
# Core methods for 5% monthly ROI targeting:
def _get_smart_allocation_limit(self) -> float:
    """Performance-based allocation control (20-60%)"""
    
def _calculate_current_win_rate(self) -> float:
    """Real win rate tracking across sessions"""
    
def _calculate_monthly_performance(self) -> float:
    """Monthly P&L for allocation decisions"""
```

## Current Production Status (June 3, 2025)

### ✅ Unlimited Trading System with Safety Controls
- **Live Trading**: Confirmed with real Alpaca order IDs  
- **Portfolio Value**: $978,356 (down from $1M baseline, -2.16% ROI)
- **Unlimited Trading**: All position and daily limits removed for system improvement
- **Firebase Integration**: Persistent trade history storage across deployments
- **Safety Systems**: Comprehensive trade history tracking prevents rapid-fire incidents
- **Market Intelligence**: OpenAI o4-mini integration active
- **ML Learning**: Entry-exit trade linking for profit optimization
- **Health Monitoring**: Real-time performance analysis capabilities

### Dependencies & Installation
```bash
# Core dependencies (see requirements.txt)
pip install alpaca-trade-api>=3.0.0
pip install firebase-admin>=6.2.0
pip install flask>=2.3.3
pip install openai>=1.0.0
pip install scikit-learn>=1.3.0
pip install pandas>=2.0.0
pip install numpy>=1.24.0

# Or install all at once
pip install -r requirements.txt
```

### Recent Critical Fixes (June 2025)
- **UNLIMITED TRADING**: Removed all position size, daily trade, and daily loss limits for system improvement
- **FIREBASE INTEGRATION**: Persistent trade history storage using cloud database
- **TRADE HISTORY TRACKING**: Comprehensive safety system prevents rapid-fire trading incidents
- **SAFETY CONTROLS**: 5-minute cooldowns and rapid pattern detection prevent $36K+ losses
- **PERFORMANCE MONITORING**: Real-time analysis scripts for ROI tracking and system health
- Fixed profit rate calculation bug (was counting execution as profit)
- Implemented real-time data freshness validation
- Added OpenAI Market Intelligence with comprehensive debug signals
- Deployed production-grade health monitoring endpoints

This system has encountered 11+ major bugs during development. The QA.md rules represent institutional knowledge that MUST be followed to prevent regression.

## Project Structure (Post-Cleanup June 2025)

### 🗂️ **Directory Organization**
```
/Users/benjamin.pommeraud/Desktop/Alpaca/
├── modular_production_main.py          # Main production entry point
├── modular/                           # Core production system
│   ├── orchestrator.py               # System orchestrator
│   ├── base_module.py                # Base trading module
│   ├── crypto_module.py              # 24/7 crypto trading
│   ├── stocks_module.py              # Stock trading module
│   ├── options_module.py             # Options trading module
│   └── [other active modules]
├── legacy/                           # Archived legacy code (June 2025)
│   ├── phases/                       # Old phase-based architecture
│   │   ├── phase3_trader.py         # Legacy Phase 3 trader
│   │   ├── crypto_trader.py         # Legacy crypto system
│   │   └── [other phase files]
│   ├── debug/                        # Old debug scripts
│   ├── verification/                 # One-time setup scripts
│   ├── analysis/                     # Superseded analysis tools
│   └── dashboard/                    # Legacy dashboard system
└── [current active files]
```

### 🧹 **Cleanup Summary (June 2025)**
- **Archived**: 30+ legacy files moved to `legacy/` directory
- **Removed**: 5+ completely unused utility scripts
- **Updated**: All remaining import references to use `legacy.phases.*`
- **Preserved**: All functionality for backward compatibility

### 📋 **Current Active System**
The production system now uses **only** the modular architecture:
- Entry point: `modular_production_main.py`
- Core modules in `modular/` directory
- Legacy systems preserved in `legacy/` for reference/compatibility

## Enhanced Data Integration (Phase 2 - June 2025)

### 🚀 **Multi-Source Data Architecture**
The system now supports enhanced data sources for improved market analysis:

```python
# Enhanced Data Manager - Multi-source integration
from enhanced_data_manager import get_enhanced_data_manager

# Professional Technical Indicators - TA-Lib integration
from enhanced_technical_indicators import get_enhanced_technical_indicators

# Advanced ML Models - PyTorch integration  
from enhanced_ml_models import get_enhanced_ml_framework

# Enhanced Crypto Module - All integrations combined
from modular.enhanced_crypto_module import EnhancedCryptoModule
```

### 📊 **Data Sources Hierarchy**
1. **Alpaca API** (PRIMARY - Required for trading execution)
2. **yfinance** (FALLBACK - Enhanced market data and fundamentals)
3. **Alpha Vantage** (ENRICHMENT - Technical indicators and historical data)
4. **Finnhub** (ENRICHMENT - News sentiment and fundamental data)

### 🔧 **Technical Indicators Enhancement**
- **TA-Lib Integration**: Professional-grade indicators (RSI, MACD, Bollinger Bands)
- **Advanced Indicators**: ADX, CCI, Williams %R, Stochastic Oscillator
- **Volume Analysis**: OBV, Volume Rate of Change
- **Fallback System**: Custom implementations when TA-Lib unavailable

### 🧠 **Machine Learning Enhancement**
- **PyTorch Models**: LSTM and Transformer networks for time series prediction
- **Traditional ML**: scikit-learn RandomForest (always available as fallback)
- **Model Persistence**: Compatible with Firebase storage
- **Performance Optimization**: Numba JIT compilation for critical calculations

### 🛡️ **Deployment Compatibility**
- **Graceful Degradation**: System works with partial library availability
- **Environment Variables**: New optional keys for enhanced features
- **Firebase Integration**: PRESERVED - All existing functionality maintained
- **Railway Deployment**: PRESERVED - Enhanced features auto-detected

### 📋 **Enhanced Environment Variables (Optional)**
```bash
# Enhanced Data Sources (Optional - system works without these)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key

# All existing variables preserved and required:
ALPACA_PAPER_API_KEY=your_paper_key
ALPACA_PAPER_SECRET_KEY=your_paper_secret
FIREBASE_SERVICE_ACCOUNT={"type":"service_account",...}
OPENAI_API_KEY=your_openai_api_key
```

### 🧪 **Testing Enhanced Integration**
```bash
# Test all enhanced features and compatibility
python test_enhanced_integration.py

# Test individual components
python enhanced_data_manager.py
python enhanced_technical_indicators.py
python enhanced_ml_models.py
```

## Trade History Safety System (Critical - June 2025)

### TradeHistoryTracker Integration
**Prevents rapid-fire trading incidents that caused $36,462 loss in 5 minutes**

```python
# Firebase-backed trade tracking with safety controls
from trade_history_tracker import TradeHistoryTracker

tracker = TradeHistoryTracker(firebase_db=firebase_db)

# Safety validation before every trade
can_trade, reason = tracker.can_trade_symbol(symbol, trade_value)
if not can_trade:
    # Trade blocked - log reason and skip
    pass
```

### Safety Controls Active
- **5-minute cooldowns**: Prevents same symbol trading within 5 minutes
- **2 trades/hour limit**: Prevents rapid trading patterns per symbol  
- **Rapid pattern detection**: Detects dangerous alternating buy/sell cycles
- **Firebase persistence**: Trade history survives Railway deployment restarts
- **Position tracking**: Monitors exposure per symbol (no limits)

### Removed Limits (For System Improvement)
- ❌ **Position size limits**: No maximum dollar amount per position
- ❌ **Daily trade limits**: No maximum trades per day
- ❌ **Daily loss limits**: No daily loss circuit breakers
- ❌ **Position percentage limits**: No portfolio percentage restrictions

## Performance Monitoring System

### Real-Time Analysis Commands
```bash
# Quick performance check with environment variables
python quick_performance_check.py

# Comprehensive performance analysis 
python performance_analysis_report.py

# Live monitoring with Firebase and Alpaca data
python monitor_live_performance.py

# Continuous monitoring (every 5 minutes)
python monitor_live_performance.py continuous 5
```

### Key Performance Metrics
- **Portfolio Value**: Current account value vs $1M baseline
- **Total Return**: Dollar amount and percentage from initial capital
- **Position Analysis**: Win rate, unrealized P&L, position diversification
- **Monthly Projection**: Estimated monthly return based on current performance
- **Target Assessment**: Performance vs 5-10% monthly target

### Firebase Data Structure
```
Collections:
├── trade_history_tracker/current_status
│   ├── position_values: {symbol -> current_position_value}
│   ├── last_trade_times: {symbol -> last_trade_timestamp}  
│   └── safety_limits: {cooldown_minutes, max_trades_per_hour}
└── trade_history_details/*
    ├── Individual trade records with full audit trail
    ├── symbol, side, quantity, price, value, timestamp
    └── order_id, metadata for complete tracking
```

## Phase 2 Enhanced Data Integration (June 2025) - COMPLETED ✅

### Multi-Source Data Architecture
**Production-ready enhanced trading system with professional-grade data sources:**

- **Enhanced Data Manager**: Multi-source integration (Alpaca, yfinance, Alpha Vantage, Finnhub)
- **Professional Technical Analysis**: TA-Lib integration with 150+ indicators
- **Advanced Machine Learning**: PyTorch LSTM/Transformer models with MPS optimization
- **Graceful Degradation**: Automatic fallback when enhanced libraries unavailable
- **API Keys Configured**: Alpha Vantage (`9W2HV5D4AQAMR70O`) + Finnhub (`d0vefg1r01qmg3ulut10`)

### Enhanced Libraries Installed & Tested
```bash
# Enhanced Data Sources
yfinance>=0.2.28          # Multi-market data fallback
alpha-vantage>=2.3.1      # Professional financial data
finnhub-python>=2.4.20   # Real-time market data + news

# Professional Technical Analysis  
TA-Lib>=0.4.25           # 150+ technical indicators

# Advanced Machine Learning
torch>=2.0.0             # PyTorch neural networks
numba>=0.59.0           # JIT compilation for performance
```

### Enhanced Module Architecture
```python
# Enhanced Crypto Module with multi-source analysis
from modular.enhanced_crypto_module import EnhancedCryptoModule

# Enhanced data integration classes
from enhanced_data_manager import EnhancedDataManager
from enhanced_technical_indicators import EnhancedTechnicalIndicators  
from enhanced_ml_models import EnhancedMLFramework
```

### Testing & Validation Status
- ✅ **All Enhanced Libraries Installed**: PyTorch, TA-Lib, yfinance, etc.
- ✅ **API Keys Verified**: Alpha Vantage + Finnhub connectivity confirmed
- ✅ **Integration Tests**: 5/5 enhanced integration tests passing
- ✅ **Apple Silicon Optimization**: PyTorch using MPS device acceleration
- ✅ **Firebase + Railway Compatibility**: Preserved existing infrastructure

### Enhanced Trading Capabilities
1. **Multi-Source Data Fusion**: Combine Alpaca + Alpha Vantage + Finnhub data
2. **Professional Technical Analysis**: TA-Lib RSI, MACD, Bollinger Bands, etc.
3. **AI-Powered Predictions**: PyTorch LSTM/Transformer models for market analysis
4. **Real-Time News Integration**: Finnhub news sentiment analysis
5. **Performance Optimization**: Numba JIT compilation for critical calculations

**Phase 2 Status**: 🎉 **COMPLETE** - Enhanced trading system ready for deployment

## Recent System Updates & Best Practices

- **P&L Calculation Fixes:** All trading modules (`crypto`, `stocks`, `options`) now poll for order fills and record actual fill prices for both entry and exit. `TradeResult.success` logic updated to reflect profitability.
- **Module Packaging & Imports:** Converted all relative imports to absolute imports. Added `__init__.py` to `modular/` and `utils/` packages for production compatibility.
- **Utils Package Refactor:** Consolidated helper scripts (`technical_indicators.py`, `pattern_recognition.py`) into a `utils` package. Provided a stub `news_sentiment.py` to avoid missing imports.
- **Risk Manager Enhancements:** Set a finite `max_positions` (25) and introduced `IGNORE_DAILY_LOSS` environment variable to bypass the daily loss limit when needed.
- **Machine Learning Persistence:** Implemented periodic ML state saves in `ml_adaptive_framework.py` after every 5 trades, and added cleanup hooks in the orchestrator to persist model state on shutdown.
- **Firebase Initialization Hardened:** Prioritize `FIREBASE_SERVICE_ACCOUNT_PATH` env var, then `GOOGLE_APPLICATION_CREDENTIALS`, falling back to individual Firebase env variables.
- **Deployment & CI/CD Workflow:** Established a `staging` branch for testing, merging into `main` for production. Added CI health checks, automated deployments (staging → QA → production), and alerting for critical errors.