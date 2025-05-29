# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Guidelines

**BEFORE making any changes to this codebase:**
1. **Read QA.md thoroughly** - Contains critical bug prevention rules and deployment lessons
2. **Verify inheritance chains** - Check attribute/method availability before accessing
3. **Validate data structures** - Ensure consistent data formats between modules
4. **Test with minimal data** - Verify startup behavior when market data is limited
5. **Follow defensive programming** - Use .get() methods and provide defaults

## Project Overview

This is a sophisticated multi-phase algorithmic trading system designed for Railway cloud deployment. The system has evolved from simple market monitoring into a comprehensive trading execution engine targeting **5-10% monthly returns** with advanced risk management. Built for paper trading with Alpaca Markets API, featuring **real options trading**, 24/7 cryptocurrency trading, enhanced stock strategies, and unlimited position scaling.

## Key Commands

### Environment Setup
```bash
# Install dependencies (Phase 4)
pip install alpaca-trade-api flask==2.3.3 pytz requests

# Set environment variables for Phase 4 deployment
export ALPACA_PAPER_API_KEY="your_key_here"
export ALPACA_PAPER_SECRET_KEY="your_secret_here"
export EXECUTION_ENABLED="true"
export GLOBAL_TRADING="true"
export OPTIONS_TRADING="true"
export CRYPTO_TRADING="true"
export MARKET_TIER="2"
export MIN_CONFIDENCE="0.6"
```

### Development & Testing
```bash
# Test complete Phase 4 system with all components
python test_phase4_complete.py

# Test real options trading module
python options_manager.py

# Test 24/7 crypto trading with lowered thresholds
python crypto_trader.py

# Test Phase 3 intelligence layer (87.5% accuracy)
python test_phase3_standalone.py

# Run system locally with all Phase 4 features
OPTIONS_TRADING=true CRYPTO_TRADING=true GLOBAL_TRADING=true python start_phase3.py

# Test database functionality and persistence
python database_manager.py

# Emergency order cancellation across all asset classes
python emergency_cancel_all_orders.py

# Test individual trading phases
python test_phase1_complete.py  # Database and analysis
python test_phase2_execution.py # Execution engine
python test_global_trading.py   # Multi-timezone trading
```

### Railway Deployment
```bash
# Deploy to Railway (automated GitHub integration)
# Railway builds from Procfile: web: python start_phase3.py
# Set environment variables in Railway dashboard:
# ALPACA_PAPER_API_KEY, ALPACA_PAPER_SECRET_KEY
# EXECUTION_ENABLED=true, GLOBAL_TRADING=true
# OPTIONS_TRADING=true, CRYPTO_TRADING=true
# MARKET_TIER=2, MIN_CONFIDENCE=0.6
```

## Multi-Phase Architecture

The system evolved through systematic phases while maintaining Railway deployment simplicity:

### Phase Evolution
- **Phase 0** (`start_ultra_simple.py`): Original monitoring-only system (212 lines)
- **Phase 1** (`enhanced_trader.py`): Added database persistence and virtual trading
- **Phase 1.5** (`enhanced_trader_v2.py`): Expanded to 50+ symbol universe with sector analysis
- **Phase 2** (`start_phase2.py`): Trade execution system with risk management
- **Phase 3** (`start_phase3.py`): Intelligence layer with technical indicators
- **Phase 4** (`start_phase3.py`): **Current production system** with real options + crypto + enhanced strategies

### Core Components (Phase 4)

#### **Entry Point & Intelligence Engine**
- **`start_phase3.py`**: Phase 4 entry point with real options/crypto/enhanced strategies
- **`phase3_trader.py`**: Advanced trading engine with multi-asset support
  - Real options trading integration with Alpaca `/v2/options/contracts` API
  - 24/7 crypto trading with session-aware strategies (45-50% confidence thresholds)
  - Enhanced stock strategies: 3x Leveraged ETFs, Sector Rotation, Momentum 2x, Volatility Trading
  - Global market coordination across timezones
- **`technical_indicators.py`**: RSI, MACD, Bollinger Bands, Moving Averages
- **`market_regime_detector.py`**: Bull/Bear/Sideways detection with VIX analysis
- **`pattern_recognition.py`**: Breakouts, support/resistance, mean reversion patterns

#### **Phase 4 Advanced Trading Modules**
- **`options_manager.py`**: **REAL** options trading system (not mock data)
  - **Direct API Integration**: Uses Alpaca `/v2/options/contracts` endpoint with authentication
  - **5 Options Strategies**: Long calls, bull call spreads, protective puts, covered calls, long straddles
  - **Multi-Leg Orders**: Uses `order_class='mleg'` for spreads and complex strategies
  - **Real Options Chains**: Fetches actual strikes, expirations, and pricing from Alpaca
  - **Position Sizing**: 30% max portfolio allocation with confidence-based sizing
- **`crypto_trader.py`**: 24/7 cryptocurrency trading with aggressive thresholds
  - **13 Cryptocurrencies**: BTC, ETH, ADA, SOL, DOT, LINK, MATIC, AVAX, UNI, AAVE, COMP, MANA, SAND
  - **Session-Aware Strategies**: Asia (45%), Europe (50%), US (40%) confidence thresholds
  - **20% Portfolio Allocation**: Dedicated crypto exposure with 1.5x leverage
  - **Mock Price Fallbacks**: BTC $45k, ETH $3k for testing when API unavailable
- **`global_market_manager.py`**: Multi-timezone trading coordination
  - **Market Session Detection**: US, Asian, European market hours
  - **Symbol Selection**: Match trading symbols to open exchanges for immediate execution

#### **Enhanced Stock Strategies (Replacing Mock Options)**
- **3x Leveraged ETFs**: TQQQ, UPRO, SOXL, FAS, UDOW for amplified returns during high confidence (>70%)
- **Sector Rotation**: Technology (XLK), Healthcare (XLV), Financials (XLF), Energy (XLE), Consumer (XLY)
- **Momentum Amplification**: 2x position sizing during high confidence periods (>75%)
- **Volatility Trading**: VXX (long vol) during uncertainty, SVXY (short vol) during high confidence

#### **Execution & Risk System**
- **`order_manager.py`**: Multi-asset trade execution via Alpaca API
  - Real options orders using proper symbol format (e.g., `AAPL240119C00190000`)
  - Cryptocurrency orders with `time_in_force='gtc'`
  - Enhanced stock orders with dynamic position sizing
- **`risk_manager.py`**: Advanced portfolio-level risk controls
  - **Unlimited Positions**: Removed 5-position limit for aggressive scaling
  - **RegT Buying Power**: Fixed to use `regt_buying_power` instead of day trading power
  - Asset class exposure limits (30% options, 20% crypto, 40% sector max)
  - 20% maximum drawdown protection

#### **Data & Analytics**
- **`database_manager.py`**: SQLite integration (`data/trading_system.db`)
  - **Market Quotes**: Real-time price data across all asset classes
  - **Trading Cycles**: Intelligence analysis, strategy selection, confidence scores
  - **Multi-Asset Trades**: Stocks, options, crypto execution records with P&L
  - **Performance Metrics**: Strategy analytics across all trading modules
- **`market_universe.py`**: Multi-tier symbol management with global coverage
  - **Tier 1**: Core ETFs (SPY, QQQ, IWM) - always monitored
  - **Tier 2**: 15 most liquid stocks + sector ETFs
  - **Tier 3**: Top 25 NASDAQ components  
  - **Tier 4**: Extended stock universe + Asian ADRs + Global ETFs

### Current Deployment Configuration

#### **Procfile**
```
web: python start_phase3.py
```

#### **Requirements**
```
alpaca-trade-api
flask==2.3.3
pytz
requests
```

#### **Environment Variables (Railway Phase 4)**
- `ALPACA_PAPER_API_KEY` / `ALPACA_PAPER_SECRET_KEY`: Alpaca credentials for options API
- `EXECUTION_ENABLED`: true/false toggle for actual trading
- `GLOBAL_TRADING`: true/false for multi-timezone trading
- `OPTIONS_TRADING`: true/false for real options strategies (default: true)
- `CRYPTO_TRADING`: true/false for 24/7 crypto trading (default: true)
- `MARKET_TIER`: 1-5 controls symbol universe size
- `MIN_CONFIDENCE`: 0.6 default, minimum confidence threshold for trades

## Trading System Logic (Phase 4)

### Aggressive Performance Target: 5-10% Monthly Returns
The system is configured for aggressive algorithmic trading with:
- **Unlimited Position Scaling**: No artificial position limits (35+ concurrent positions)
- **Multi-Asset Leverage**: Real options for 2.5x, 3x ETFs for amplified returns, crypto 1.5x sizing
- **24/7 Trading Coverage**: Stocks + Real Options + Crypto + Enhanced Strategies
- **20% Maximum Drawdown**: Risk tolerance appropriate for aggressive targets

### Intelligence-Driven Strategy Engine
1. **Multi-Factor Analysis**: Technical indicators + Market regime + Pattern recognition
2. **Confidence Scoring**: Combined intelligence from multiple analysis modules
   - **Technical Weight**: 40% (RSI, MACD, Bollinger Bands signals)
   - **Regime Weight**: 40% (Bull/Bear/Sideways trend detection)
   - **Pattern Weight**: 20% (Breakouts, support/resistance patterns)
3. **Strategy Selection**: Intelligence-enhanced strategy variants
   - **Aggressive Momentum**: High confidence (80%+), real options + 3x ETFs
   - **Momentum**: Moderate confidence (60-80%), standard equity positions
   - **Sector Rotation**: Regime-based ETF selection (tech/healthcare/financials)
   - **Volatility Trading**: VXX/SVXY based on market uncertainty

### Multi-Asset Execution Flow
1. **Stock Analysis**: Technical intelligence on equity positions with enhanced strategies
2. **Real Options Trading**: Authentic options chains and multi-leg strategies
3. **Crypto Trading**: 24/7 momentum strategies with lowered confidence thresholds
4. **Enhanced Strategies**: 3x ETFs, sector rotation, momentum amplification, volatility plays
5. **Risk Management**: Real-time monitoring across all asset classes

### Real Options Trading Implementation
- **API Integration**: Direct calls to `https://paper-api.alpaca.markets/v2/options/contracts`
- **Authentication**: Uses ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY
- **Order Execution**: Standard `submit_order()` with option symbols, multi-leg with `order_class='mleg'`
- **Strategies Available**: Long calls, bull spreads, protective puts, covered calls, straddles
- **Real Pricing**: Fetches actual bid/ask from market data, fallbacks to reasonable estimates

## Data Persistence & Memory System

### SQLite Database (`data/trading_system.db`)
- **Market Quotes Table**: Real-time price data across all asset classes
- **Trading Cycles Table**: Intelligence analysis, strategy selection, confidence scores  
- **Trades Table**: Complete execution records with P&L tracking across stocks/options/crypto
- **Performance Metrics Table**: Strategy analytics and portfolio performance tracking

### JSON Logging (`data/trading_log.json`)
- **Backward Compatibility**: Maintained for legacy monitoring
- **Real-time Summaries**: Multi-asset trading decisions and outcomes
- **Error Tracking**: Comprehensive failure logging across all modules

### Memory & Learning
- **Pattern Recognition**: Remembers successful setups and conditions
- **Strategy Performance**: Tracks win rates and returns by strategy type
- **Risk Adaptation**: Adjusts position sizing based on recent performance
- **Market Regime Memory**: Adapts strategies based on historical regime performance

## Development Architecture

### Inheritance Chain (Critical for Maintenance)
```
Phase3Trader (entry point)
    ↳ Phase2Trader (execution engine)
        ↳ EnhancedTraderV2 (expanded universe)
            ↳ EnhancedTrader (database integration)
```

### Component Integration Flow
1. **`start_phase3.py`** → Initializes `Phase3Trader` with all Phase 4 capabilities
2. **Intelligence Cycle** → Technical + Regime + Pattern analysis every 2 minutes
3. **Multi-Asset Trading**:
   - Real options chains fetched and analyzed
   - Crypto opportunities evaluated with session-aware strategies
   - Enhanced stock strategies triggered by confidence levels
   - Risk management validation across all asset classes
4. **Database Persistence** → Complete trade records and performance tracking

### Testing Strategy
- **`test_phase4_complete.py`**: Complete Phase 4 system integration testing
- **`test_phase3_standalone.py`**: Core intelligence modules testing (87.5% accuracy)
- **Component Tests**: Individual module testing (options, crypto, enhanced strategies)
- **`options_manager.py`**: Standalone real options module testing
- **`crypto_trader.py`**: Standalone crypto module testing

### Quality Assurance
- **`QA.md`**: Bug history, fixes, and prevention rules
  - Documents all deployment issues and their solutions (7 major bugs resolved)
  - Establishes coding standards to prevent recurring bugs
  - Required reading before making changes to inheritance chains or API integrations

## Expected System Behavior

### Successful Phase 4 Operation
```
🧠 PHASE 3 INTELLIGENCE LAYER STARTING
🌍 Global Trading: ✅ ENABLED
📊 Options Trading: ✅ ENABLED  
₿ Crypto Trading: ✅ ENABLED
🎯 Target: 5-10% monthly returns, 20% max drawdown

📊 REAL OPTIONS TRADING
✅ Retrieved 100 calls, 0 puts for SPY
✅ Retrieved 77 calls, 23 puts for AAPL
📊 OPTIONS TRADE: SPY
   🎯 Strategy: long_calls
   💰 Contracts: 2

📊 ENHANCED STOCK STRATEGIES
📊 LEVERAGED ETF: TQQQ
   💰 15 shares @ $67.85
   🎯 3x Leverage Effect

₿ CRYPTO TRADING CYCLE
₿ BTCUSD: confidence=52%, min=50%, tradeable=true
₿ CRYPTO TRADE: BTCUSD
   📊 BUY: 0.044000 @ $45000

💰 Portfolio Value: $99,941.79
📊 Current Positions (35): [showing unlimited position scaling]
```

### Multi-Asset Risk Management Examples
- Real options allocation limit enforcement (30% max)
- Crypto exposure limit protection (20% max) 
- Sector exposure limits (40% max per sector)
- Emergency order cancellation across all asset classes
- RegT buying power management ($130k+ available)
- Session-aware trading halt when markets closed

## Critical Implementation Notes

### Real Options Trading
- Never use mock/fake options data - always fetch real chains from Alpaca API
- Handle API rate limits with retries (visible as "sleep 3 seconds and retrying")
- Use proper option symbol format: `AAPL240119C00190000`
- Multi-leg orders require `order_class='mleg'` and proper leg structure

### Crypto Trading Execution
- Lowered confidence thresholds (45-50%) to enable actual trading
- Mock price fallbacks ensure system continues during API issues
- Session-aware strategies change throughout 24-hour trading cycle

### Risk Management
- Unlimited positions (35+ concurrent) with proper exposure limits
- RegT buying power detection for accurate position sizing
- Emergency order cancellation prevents accumulation of wrong orders