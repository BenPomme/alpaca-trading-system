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

This is a sophisticated multi-phase algorithmic trading system designed for Railway cloud deployment. The system has evolved from simple market monitoring into a comprehensive trading execution engine targeting **5-10% monthly returns** with advanced risk management. Built for paper trading with Alpaca Markets API, featuring options trading, 24/7 cryptocurrency trading, global market coverage, and unlimited position scaling.

## Key Commands

### Environment Setup
```bash
# Install dependencies (Phase 4)
pip install alpaca-trade-api flask==2.3.3 pytz

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
# Test complete Phase 4 system
python test_phase4_complete.py

# Test options trading module
python options_manager.py

# Test 24/7 crypto trading
python crypto_trader.py

# Test Phase 3 intelligence layer
python test_phase3_standalone.py

# Run system locally with all Phase 4 features
OPTIONS_TRADING=true CRYPTO_TRADING=true GLOBAL_TRADING=true python start_phase3.py

# Test database functionality
python database_manager.py

# Emergency order cancellation
python emergency_cancel_all_orders.py
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
- **Phase 4** (`start_phase3.py`): **Current production system** with options + crypto + global trading

### Core Components (Phase 4)

#### **Entry Point & Intelligence Engine**
- **`start_phase3.py`**: Phase 4 entry point with options/crypto/global trading
- **`phase3_trader.py`**: Advanced trading engine with multi-asset support
  - Integrates technical indicators, regime detection, pattern recognition
  - Options trading integration with Greeks monitoring
  - 24/7 crypto trading with session-aware strategies
  - Global market coordination across timezones
- **`technical_indicators.py`**: RSI, MACD, Bollinger Bands, Moving Averages
- **`market_regime_detector.py`**: Bull/Bear/Sideways detection with VIX analysis
- **`pattern_recognition.py`**: Breakouts, support/resistance, mean reversion patterns

#### **Phase 4 Advanced Trading Modules**
- **`options_manager.py`**: Complete options trading system
  - **5 Options Strategies**: Long calls, bull call spreads, protective puts, covered calls, long straddles
  - **Greeks Monitoring**: Delta, gamma, theta, vega tracking with risk alerts
  - **Position Sizing**: 30% max portfolio allocation with 2.5x target leverage
  - **Risk Management**: Real-time exposure monitoring and limit enforcement
- **`crypto_trader.py`**: 24/7 cryptocurrency trading
  - **13 Cryptocurrencies**: BTC, ETH, ADA, SOL, DOT, LINK, MATIC, AVAX, UNI, AAVE, COMP, MANA, SAND
  - **Session-Aware Strategies**: Different approaches for Asia/Europe/US hours
  - **20% Portfolio Allocation**: Dedicated crypto exposure with 1.5x leverage
  - **Volatility-Based Sizing**: ATR-based position sizing
- **`global_market_manager.py`**: Multi-timezone trading coordination
  - **Market Session Detection**: US, Asian, European market hours
  - **Symbol Selection**: Match trading symbols to open exchanges for immediate execution

#### **Execution & Risk System**
- **`order_manager.py`**: Multi-asset trade execution via Alpaca API
  - Stocks, options, and cryptocurrency order placement
  - Confidence-based position sizing with leverage multipliers
  - Automatic stop-loss and take-profit order placement
- **`risk_manager.py`**: Advanced portfolio-level risk controls
  - **Unlimited Positions**: Removed 5-position limit for aggressive scaling
  - Dynamic position sizing based on volatility and confidence
  - Asset class exposure limits (30% options, 20% crypto)
  - 20% maximum drawdown protection

#### **Data & Analytics**
- **`database_manager.py`**: SQLite integration for persistent data storage
- **`market_universe.py`**: Multi-tier symbol management with global coverage
  - **Tier 1**: Core ETFs (SPY, QQQ, IWM) - always monitored
  - **Tier 2**: 15 most liquid stocks + sector ETFs
  - **Tier 3**: Top 25 NASDAQ components  
  - **Tier 4**: Extended stock universe + Asian ADRs + Global ETFs
  - **Tier 5**: Complete global coverage (50+ symbols)

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
```

#### **Environment Variables (Railway Phase 4)**
- `ALPACA_PAPER_API_KEY` / `ALPACA_PAPER_SECRET_KEY`: Alpaca credentials
- `EXECUTION_ENABLED`: true/false toggle for actual trading
- `GLOBAL_TRADING`: true/false for multi-timezone trading
- `OPTIONS_TRADING`: true/false for options strategies
- `CRYPTO_TRADING`: true/false for 24/7 crypto trading
- `MARKET_TIER`: 1-5 controls symbol universe size
- `MIN_CONFIDENCE`: 0.6 default, minimum confidence threshold for trades

## Trading System Logic (Phase 4)

### Aggressive Performance Target: 5-10% Monthly Returns
The system is configured for aggressive algorithmic trading with:
- **Unlimited Position Scaling**: No artificial position limits
- **Multi-Asset Leverage**: 2.5x through options, 1.5x through crypto position sizing
- **24/7 Trading Coverage**: Stocks + Options + Crypto + Global markets
- **20% Maximum Drawdown**: Appropriate risk tolerance for aggressive targets

### Intelligence-Driven Strategy Engine
1. **Multi-Factor Analysis**: Technical indicators + Market regime + Pattern recognition
2. **Confidence Scoring**: Combined intelligence from multiple analysis modules
   - **Technical Weight**: 40% (RSI, MACD, Bollinger Bands signals)
   - **Regime Weight**: 40% (Bull/Bear/Sideways trend detection)
   - **Pattern Weight**: 20% (Breakouts, support/resistance patterns)
3. **Strategy Selection**: Intelligence-enhanced strategy variants
   - **Aggressive Momentum**: High combined confidence (80%+), options leverage
   - **Momentum**: Moderate confidence (60-80%), standard position sizing
   - **Cautious Momentum**: Lower confidence (50-60%), defensive positions
   - **Conservative**: Conflicting signals, preserve capital

### Multi-Asset Execution Flow
1. **Stock Analysis**: Technical intelligence on equity positions
2. **Options Opportunities**: Leverage and hedging strategies based on regime
3. **Crypto Trading**: 24/7 momentum and volatility strategies
4. **Global Coverage**: Multi-timezone symbol selection for continuous trading
5. **Risk Management**: Real-time monitoring across all asset classes

### Advanced Risk Management
- **Asset Class Limits**: 30% options, 20% crypto, remainder equities
- **Greeks Monitoring**: Delta, gamma, theta, vega exposure tracking
- **Volatility-Based Sizing**: Position size adjusts to market volatility
- **Session-Aware Trading**: Different strategies for different market hours
- **Emergency Controls**: Automatic order cancellation and position protection

## Data Persistence

### SQLite Database (`data/trading_system.db`)
- **Market Quotes**: Real-time price data across all asset classes
- **Trading Cycles**: Intelligence analysis, strategy selection, confidence scores
- **Multi-Asset Trades**: Stocks, options, crypto execution records with P&L
- **Performance Metrics**: Strategy analytics across all trading modules

### JSON Logging (`data/trading_log.json`)
- **Backward Compatibility**: Maintained for legacy monitoring
- **Real-time Summaries**: Multi-asset trading decisions and outcomes
- **Error Tracking**: Comprehensive failure logging across all modules

## Development Architecture

### Inheritance Chain (Critical for Maintenance)
```
Phase3Trader (entry point)
    ↳ Phase2Trader (execution engine)
        ↳ EnhancedTraderV2 (expanded universe)
            ↳ EnhancedTrader (database integration)
```

### Component Integration Flow
1. **`start_phase3.py`** → Initializes `Phase3Trader` with Phase 4 capabilities
2. **`Phase3Trader`** → Integrates intelligence + options + crypto + global trading
3. **Trading Cycle**:
   - Multi-timezone market data collection
   - Intelligence analysis (technical + regime + patterns)
   - Options opportunity analysis and Greeks monitoring
   - Crypto session-aware strategy selection
   - Multi-asset position sizing and execution
   - Risk management validation across all asset classes
   - Database persistence with complete trade records

### Testing Strategy
- **`test_phase4_complete.py`**: Complete Phase 4 system integration testing
- **`test_phase3_standalone.py`**: Core intelligence modules testing
- **Component Tests**: Individual module testing (options, crypto, global)
- **`options_manager.py`**: Standalone options module testing
- **`crypto_trader.py`**: Standalone crypto module testing

### Quality Assurance
- **`QA.md`**: Bug history, fixes, and prevention rules
  - Documents all deployment issues and their solutions
  - Establishes coding standards to prevent recurring bugs
  - Required reading before making changes to inheritance chains

## Expected System Behavior

### Successful Phase 4 Operation
```
🧠 PHASE 3 INTELLIGENCE LAYER STARTING
🌍 Global Trading: ✅ ENABLED
📊 Options Trading: ✅ ENABLED  
₿ Crypto Trading: ✅ ENABLED
🎯 Target: 5-10% monthly returns, 20% max drawdown

🧠 PHASE 3 INTELLIGENCE CYCLE - 14:30:15
📈 Collecting market data... (20 symbols)
🧠 Analyzing market intelligence...
🎯 Market Regime: bullish (75% confidence)

₿ CRYPTO TRADING CYCLE
₿ Active crypto symbols: ['BTCUSD', 'ETHUSD', 'ADAUSD', 'SOLUSD']
₿ CRYPTO TRADE: BTCUSD
   📊 BUY: 0.032100 @ $0
   🎯 Confidence: 68.5%
   🌍 Session: us_prime

📊 OPTIONS TRADING CYCLE
📊 Options exposure: 12.5%
📊 OPTIONS TRADE: SPY
   🎯 Strategy: long_calls
   💰 Contracts: 2
   🎯 Confidence: 75.0%

🧠 INTELLIGENCE TRADE: QQQ
   💰 5 shares @ $520.85
   🎯 Final Confidence: 82.3%
   📊 Intelligence: Technical supports: buy (78%)

✅ Phase 4 cycle completed in 12.8s
⏳ Next cycle in 120 seconds...
```

### Multi-Asset Risk Management Examples
- Options allocation limit enforcement (30% max)
- Crypto exposure limit protection (20% max)
- Greeks exposure monitoring (delta, theta alerts)
- Emergency order cancellation across all asset classes
- Session-aware trading halt when markets closed