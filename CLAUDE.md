# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Guidelines

**BEFORE making any changes to this codebase:**
1. **Read QA.md thoroughly** - Contains critical bug prevention rules and deployment lessons learned from 7+ major bugs
2. **Apply QA.md Rules** - All 7 QA rules must be followed to prevent recurring bugs (inheritance, data contracts, defensive programming)
3. **Verify inheritance chains** - Check attribute/method availability before accessing (QA Rule 1 & 6)
4. **Validate data structures** - Ensure consistent data formats between modules (QA Rule 5)
5. **Test with minimal data** - Verify startup behavior when market data is limited (QA Rule 4)
6. **Follow defensive programming** - Use .get() methods and provide defaults (QA Rule 5)
7. **Update QA.md with new lessons** - Document any new bugs/fixes for future prevention

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

# Test ML integration and intelligent exit system
python test_ml_integration.py

# Debug full trading cycle locally (when Railway logs truncated)
python debug_cycle.py

# CRITICAL: Analyze real trading performance (win rates, P&L, hold times)
python analyze_trading_performance.py

# Test current system components
python test_phase4_complete.py  # Complete Phase 4 system integration  
python test_phase3_standalone.py # Core intelligence modules (87.5% accuracy)
python test_global_trading.py   # Multi-timezone trading
python test_ml_integration.py   # ML integration verification
```

### Railway Deployment
```bash
# Deploy to Railway (automated GitHub integration)
# Railway builds from Procfile: web: python railway_deploy.py -> start_phase3.py
# Set environment variables in Railway dashboard:
# ALPACA_PAPER_API_KEY, ALPACA_PAPER_SECRET_KEY
# EXECUTION_ENABLED=true, GLOBAL_TRADING=true
# OPTIONS_TRADING=true, CRYPTO_TRADING=true
# MARKET_TIER=2, MIN_CONFIDENCE=0.6

# OPTIMIZATION: Market-aware cycle delays reduce resource usage
# - US Market Open: 2 minute cycles (active trading)
# - US Market Closed + Crypto: 10 minute cycles (crypto-only)
# - All Markets Closed: 30 minute cycles (monitoring only)
```

### Post-Deployment Verification
```bash
# Check Railway deployment status
railway status

# View Railway logs (may be truncated)
railway logs

# If Railway logs are truncated, debug locally to see full output
python debug_cycle.py | head -200

# Verify specific components working
python debug_cycle.py 2>&1 | grep -A 10 "INTELLIGENT EXIT"
python debug_cycle.py 2>&1 | grep -A 5 "ML Predictions"

# Test ML integration is working
python test_ml_integration.py
```

## Multi-Phase Architecture

The system evolved through systematic phases while maintaining Railway deployment simplicity:

### Phase Evolution
- **Phase 0** (`start_ultra_simple.py`): Original monitoring-only system (212 lines)
- **Phase 1** (`enhanced_trader.py`): Added database persistence and virtual trading
- **Phase 1.5** (`enhanced_trader_v2.py`): Expanded to 50+ symbol universe with sector analysis
- **Phase 2** (`start_phase2.py`): Trade execution system with risk management
- **Phase 3** (`start_phase3.py`): Intelligence layer with technical indicators
- **Phase 4** (`start_phase3.py`): Real options + crypto + enhanced strategies
- **Phase 5** (`start_phase3.py`): **Current production system** with full ML integration and intelligent exits
- **Phase 5.1** (Critical Fixes): Exit system fixes for 13.2% win rate → targeting 45-60% win rate

### Core Components (Phase 5 - Current Production)

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
- **`intelligent_exit_manager.py`**: **BREAKTHROUGH** Intelligent exit system leveraging all ML capabilities
  - **5 Analysis Components**: Market regime, technical indicators, ML confidence, pattern recognition, time-based
  - **Partial Profit Taking**: 20% at +6%, 30% at +10%, 40% at +15% (more conservative thresholds)
  - **Market Adaptive Targets**: Bull markets 1.5x targets, Bear markets 0.6x targets, Neutral 1.0x
  - **REAL ML Integration**: Uses actual ML predictions for confidence, reversal probability, trend strength
  - **Iterative Learning**: Records exit outcomes and adapts strategies based on performance
  - **Performance Tracking**: Win rates and profitability by exit strategy with recommendations
  - **🚨 CRITICAL FIX (Phase 5.1)**: Minimum 2-hour hold time, 8% stop loss, 80% confidence + profit required for intelligence exits
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
- **`ml_adaptive_framework.py`**: **NEW** Machine Learning integration for iterative improvement
  - **ML Strategy Selection**: Ensemble approach with confidence-based strategy selection
  - **ML Risk Prediction**: Position sizing and risk assessment using ML models
  - **Performance Tracking**: ML vs traditional strategy performance comparison
  - **Adaptive Learning**: Continuously improves based on trade outcomes

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
1. **Position Monitoring**: Intelligent exit analysis on all 35+ open positions every 2 minutes
2. **Stock Analysis**: Technical intelligence on equity positions with enhanced strategies
3. **Real Options Trading**: Authentic options chains and multi-leg strategies
4. **Crypto Trading**: 24/7 momentum strategies with lowered confidence thresholds
5. **Enhanced Strategies**: 3x ETFs, sector rotation, momentum amplification, volatility plays
6. **Intelligent Exits**: 5-component analysis with partial profit taking and adaptive targets
7. **Risk Management**: Real-time monitoring across all asset classes

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

## ML Integration Architecture (Phase 5)

### Full ML Integration Achievement

Phase 5 represents the complete integration of machine learning throughout the trading system:

#### **Real ML Predictions (No More Simulated Data)**
- **Before**: `random.uniform(0.2, 0.9)` # FAKE DATA
- **After**: `self.ml_models.strategy_selector.select_optimal_strategy(ml_market_data)`
- **Impact**: Real ML confidence scores, reversal probability, trend strength

#### **Intelligent Exit System with ML Learning**
```python
# Real ML integration in intelligent_exit_manager.py
ml_strategy, current_confidence, ml_details = self.ml_models.strategy_selector.select_optimal_strategy(ml_market_data)
risk_analysis = self.ml_models.risk_predictor.predict_position_risk(...)
regime_analysis = self.ml_models.strategy_selector.regime_detector.analyze_market_regime(...)
```

#### **Iterative Learning System**
- **Exit Outcome Recording**: Every trade exit recorded with P&L, confidence, reasoning
- **Performance Tracking**: Win rates by exit strategy (stop_loss, profit_protection, etc.)
- **Strategy Adaptation**: ML models learn from successful/failed exits
- **Recommendations**: System provides improvement suggestions

#### **ML Framework Components**
1. **`ml_adaptive_framework.py`**: Central ML coordination
2. **`ml_strategy_selector.py`**: ML-based strategy selection with ensemble approach
3. **`ml_risk_predictor.py`**: Position sizing and risk assessment using ML
4. **`ml_regime_detector.py`**: Market regime classification with unsupervised learning

#### **Deployment Verification Process**
Due to Railway log truncation, use systematic verification:
```bash
# Deploy verification workflow
git push                    # Deploy to Railway
railway logs               # Check Railway logs (may be truncated)
python debug_cycle.py      # Run local debug if needed
python test_ml_integration.py  # Verify ML components
```

#### **ML Learning Examples**
```
🧠 ML Learning: Recorded exit outcome for PANW (major_profit_protection)
📊 Exit Strategy 'stop_loss': 65% win rate, -2.1% avg
📊 Exit Strategy 'profit_protection': 78% win rate, +15.3% avg
```

### Railway Log Analysis Best Practices

**Issue**: Railway truncates logs, hiding ML and exit system activity
**Solution**: Local debug reveals full system operation

**What Railway Logs Show (Truncated)**:
```
✅ Trades Executed: 4
🎯 Trades Attempted: 6
```

**What Local Debug Shows (Complete)**:
```
💼 POSITION MONITORING & EXIT MANAGEMENT
📊 Monitoring 42 open positions for intelligent exits...
🧠 INTELLIGENT EXIT TRIGGERED: PANW
   📊 Reason: major_profit_protection  
   🎯 Confidence: 22.4%
   💰 Exit Portion: 70% (partial exit)
   📈 P&L: +78.9% (MAJOR WIN!)
🤖 ML Predictions: strategy=conservative, confidence=0.60, reversal=0.35
```

### ML Integration Success Metrics

**✅ Verified Working Components:**
- Real ML predictions replacing all simulated data
- Intelligent exit system with 5-component analysis
- Partial profit taking (70% exit on +78.9% gain)
- Stop loss protection (-6.5% ADI exit)
- ML learning from exit outcomes
- Performance tracking by exit strategy

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

### Market Hours Optimization (Phase 5.2)
**BREAKTHROUGH**: Smart cycle delays based on market status prevent unnecessary processing

**Optimization Logic**:
- **US Market Open**: 2-minute cycles for active stock/options trading
- **US Market Closed + Crypto Enabled**: 10-minute cycles for crypto-only trading
- **All Markets Closed**: 30-minute cycles for position monitoring only

**Resource Savings**:
- 80% reduction in processing during off-hours (10 min vs 2 min cycles)
- US stock/options analysis skipped when markets closed
- Crypto trading continues 24/7 regardless of US market status

**Implementation**:
```python
# Smart cycle delay based on market status
def get_market_aware_cycle_delay(self) -> int:
    us_market_open = self.api.get_clock().is_open
    if us_market_open:
        return 120  # 2 minutes - active trading
    elif self.crypto_trading:
        return 600  # 10 minutes - crypto only
    else:
        return 1800  # 30 minutes - monitoring
```

## 🚨 CRITICAL: Performance Monitoring & Analysis

### Real Performance Tracking
The system requires regular performance analysis to prevent systematic failures:

```bash
# Weekly performance analysis (MANDATORY)
python analyze_trading_performance.py

# Key metrics to monitor:
# - Win rate: Target 45-60% (was 13.2% before fixes)
# - Average hold time: Target 2-8 hours (was 6 minutes)
# - P&L profile: Positive total P&L trend
# - Exit frequency: Reduced premature exits
```

### Performance Analysis Output
```
📊 PERFORMANCE METRICS:
   🎯 Win Rate: 13.2% (5 wins, 33 losses) ← CRITICAL ISSUE
   💰 Total P&L: $-17.99
   📊 Average hold time: 0.1 hours ← TRADES CLOSED IMMEDIATELY
   
🎯 RECOMMENDATIONS:
   ⚠️ Win rate too low - intelligent exit system too aggressive
   💡 Average hold time indicates premature exits
```

### Exit System Critical Fixes Applied (Phase 5.1)
**Problem**: 13.2% win rate due to trades closing within 6 minutes
**Root Cause**: Intelligence-based exits triggered immediately without profit requirements
**Fixes**:
- Minimum 2-hour hold period before intelligence exits
- Stop loss: 5% → 8% (more volatility tolerance)
- Intelligence exits require 80% confidence AND +2% profit
- Multiple signals threshold: 3 → 5 signals needed

### Monitoring Commands
```bash
# Check for improved hold times
python debug_cycle.py 2>&1 | grep "min_hold_period"

# Verify reduced exit frequency  
python debug_cycle.py 2>&1 | grep "INTELLIGENT EXIT"

# Track win rate improvements
python analyze_trading_performance.py | grep "Win Rate"
```

### Performance Recovery Timeline
- **Immediate (24-48h)**: Longer hold times, "min_hold_period" messages
- **Weekly**: Win rate improvement >30%, hold time >2 hours
- **Monthly**: Win rate 45-60%, positive P&L trend

**⚠️ CRITICAL**: If win rate remains <30% after 1 week, further exit system adjustments needed.