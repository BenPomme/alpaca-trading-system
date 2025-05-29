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

This is a sophisticated multi-phase algorithmic trading system designed for Railway cloud deployment. The system has evolved from simple market monitoring into a comprehensive trading execution engine with actual paper trade execution, advanced risk management, and real-time position monitoring. Built for paper trading with Alpaca Markets API, featuring expanded market universe (50+ symbols), automated stop-loss/take-profit, and SQLite persistence.

## Key Commands

### Environment Setup
```bash
# Install dependencies (Phase 4.1)
pip install alpaca-trade-api flask==2.3.3 pytz

# Set environment variables for Alpaca paper trading (Phase 4.1: Global Trading)
export ALPACA_PAPER_API_KEY="your_key_here"
export ALPACA_PAPER_SECRET_KEY="your_secret_here"
export EXECUTION_ENABLED="true"
export GLOBAL_TRADING="true"
export MARKET_TIER="5"
export MIN_CONFIDENCE="0.7"
```

### Development & Testing
```bash
# Test Phase 4.1 global trading functionality  
python test_global_trading.py

# Test Phase 4.1 deployment verification
python test_phase4_deployment.py

# Test Phase 3 intelligence layer (complete system)
python test_phase3_standalone.py

# Test Phase 1 functionality (database, analysis)
python test_phase1_complete.py

# Run system locally with global trading enabled (Phase 4.1)
GLOBAL_TRADING=true MARKET_TIER=5 EXECUTION_ENABLED=true python start_phase3.py

# Test database functionality
python database_manager.py

# Run original monitoring-only system
python start_ultra_simple.py
```

### Railway Deployment
```bash
# Deploy to Railway (automated GitHub integration)
# Railway builds from Procfile: web: python start_phase3.py
# Set environment variables in Railway dashboard (Phase 4.1):
# ALPACA_PAPER_API_KEY, ALPACA_PAPER_SECRET_KEY
# EXECUTION_ENABLED=true, GLOBAL_TRADING=true, MARKET_TIER=5
# MIN_CONFIDENCE=0.7, MIN_TECHNICAL_CONFIDENCE=0.6
```

## Multi-Phase Architecture

The system evolved through systematic phases while maintaining Railway deployment simplicity:

### Phase Evolution
- **Phase 0** (`start_ultra_simple.py`): Original monitoring-only system (212 lines)
- **Phase 1** (`enhanced_trader.py`): Added database persistence and virtual trading
- **Phase 1.5** (`enhanced_trader_v2.py`): Expanded to 50+ symbol universe with sector analysis
- **Phase 2** (`start_phase2.py`): Trade execution system with risk management
- **Phase 3** (`start_phase3.py`): Current production system with intelligence layer

### Core Components (Phase 3)

#### **Entry Point & Intelligence Engine**
- **`start_phase3.py`**: Current production entry point with intelligence layer
- **`phase3_trader.py`**: Advanced trading engine with multi-factor analysis
  - Integrates technical indicators, regime detection, and pattern recognition
  - Intelligent trade decisions using combined confidence scoring
- **`technical_indicators.py`**: RSI, MACD, Bollinger Bands, Moving Averages
- **`market_regime_detector.py`**: Bull/Bear/Sideways detection with VIX analysis
- **`pattern_recognition.py`**: Breakouts, support/resistance, mean reversion patterns

#### **Execution System**
- **`order_manager.py`**: Handles actual paper trade execution via Alpaca API
  - Position sizing based on strategy confidence (1-3% of portfolio)
  - Market order placement with risk-adjusted share calculations
  - Automatic stop-loss (3%) and take-profit (8%) order placement
- **`risk_manager.py`**: Advanced portfolio-level risk controls
  - Maximum 5 concurrent positions, 40% sector exposure limits
  - 5% daily portfolio loss limit, 15% maximum position size
  - Pre-trade risk validation with detailed rejection reasons

#### **Data & Analytics**
- **`database_manager.py`**: SQLite integration for persistent data storage
  - Market quotes, trading cycles, actual trades, performance metrics
  - Comprehensive trade history and strategy performance tracking
- **`market_universe.py`**: Multi-tier symbol management (50+ symbols)
  - **Tier 1**: Core ETFs (SPY, QQQ, IWM) - always monitored
  - **Tier 2**: 15 most liquid stocks + sector ETFs
  - **Tier 3**: Top 25 NASDAQ components
  - **Tier 4**: Extended stock universe for broader opportunities

#### **Supporting Infrastructure**
- **`performance_tracker.py`**: Strategy analytics and performance monitoring
- **`dashboard_web.py`**: Real-time web dashboard for position monitoring
- **Test suites**: Comprehensive testing for all phases and components

### Current Deployment Configuration

#### **Procfile**
```
web: python start_phase3.py
```

#### **Requirements**
```
alpaca-trade-api
flask==2.3.3
```

#### **Environment Variables (Railway)**
- `ALPACA_PAPER_API_KEY` / `ALPACA_PAPER_SECRET_KEY`: Alpaca credentials
- `EXECUTION_ENABLED`: true/false toggle for actual trading
- `MARKET_TIER`: 1-4 controls symbol universe size
- `MIN_CONFIDENCE`: 0.7 default, minimum confidence threshold for trades
- `MIN_TECHNICAL_CONFIDENCE`: 0.6 default, minimum technical analysis confidence

## Trading System Logic

### Intelligence-Driven Strategy Engine (Phase 3)
1. **Multi-Factor Analysis**: Technical indicators + Market regime + Pattern recognition
2. **Confidence Scoring**: Combined intelligence from multiple analysis modules
   - **Technical Weight**: 40% (RSI, MACD, Bollinger Bands signals)
   - **Regime Weight**: 40% (Bull/Bear/Sideways trend detection)
   - **Pattern Weight**: 20% (Breakouts, support/resistance patterns)
3. **Strategy Selection**: Intelligence-enhanced strategy variants
   - **Aggressive Momentum**: High combined confidence (80%+), technical support
   - **Momentum**: Moderate confidence (60-80%), regime alignment
   - **Cautious Momentum**: Lower confidence (50-60%), pattern confirmation
   - **Conservative**: Conflicting signals, preserve capital

### Execution & Risk Management
1. **Pre-Trade Risk Assessment**: 
   - Portfolio exposure limits, position count, sector concentration
   - Daily loss limits, position sizing validation
2. **Order Execution**:
   - Market orders with confidence-based position sizing
   - Automatic stop-loss and take-profit order placement
3. **Position Monitoring**:
   - Real-time P&L tracking, automated exit conditions
   - Portfolio rebalancing based on strategy changes

### Error Recovery & Reliability
- **Execution Disabled Mode**: Safe testing without actual trades
- **Connection Failures**: Automatic retry with graceful degradation
- **API Errors**: Comprehensive error logging without system crash
- **Database Failures**: Fallback to JSON logging for continuity
- **Risk Limit Breaches**: Automatic position protection and trade rejection

## Data Persistence

### SQLite Database (`data/trading_system.db`)
- **Market Quotes**: Real-time price data across all tiers
- **Trading Cycles**: Regime detection, strategy selection, confidence scores
- **Actual Trades**: Complete execution records with P&L tracking
- **Performance Metrics**: Strategy analytics and portfolio performance

### JSON Logging (`data/trading_log.json`)
- **Backward Compatibility**: Maintained for legacy monitoring
- **Real-time Summaries**: Cycle-by-cycle trading decisions and outcomes
- **Error Tracking**: Comprehensive failure logging and recovery actions

## Development Architecture

### Component Interaction Flow
1. **`start_phase2.py`** → Initializes `Phase2Trader` with environment configuration
2. **`Phase2Trader`** → Inherits enhanced analysis from `EnhancedTraderV2`
3. **Trading Cycle**:
   - Market data collection across selected tier
   - Regime detection and confidence scoring
   - Strategy selection and position size calculation
   - Risk management validation (`RiskManager`)
   - Trade execution or rejection (`OrderManager`)
   - Database persistence (`TradingDatabase`)
   - Position monitoring and exit management

### Testing Strategy
- **`test_phase3_intelligence.py`**: Complete intelligence layer testing with trade execution
- **`test_phase3_standalone.py`**: Core intelligence modules testing (87.5% accuracy)
- **`test_phase2_execution.py`**: Execution engine validation
- **Component Tests**: Individual module testing (technical indicators, pattern recognition)

### Quality Assurance
- **`QA.md`**: Bug history, fixes, and prevention rules
  - Documents all deployment issues and their solutions
  - Establishes coding standards to prevent recurring bugs
  - Required reading before making changes to inheritance chains or data structures

## Expected System Behavior

### Successful Phase 3 Operation
```
🧠 Phase 3 Intelligence Layer initialized (Execution: ENABLED)
✅ Database connected: data/trading_system.db
🧠 Technical Indicators: ✅ Enabled
🎯 Market Regime Detection: Enhanced
🔍 Pattern Recognition: Active
📊 Portfolio Value: $100,000.00
🔄 Starting continuous intelligent trading...

🧠 PHASE 3 INTELLIGENCE CYCLE - 14:30:15
📈 Collecting market data... (15 symbols)
🧠 Analyzing market intelligence...
🎯 Market Regime: bullish (75% confidence)
🎯 Strategy: momentum
🧠 INTELLIGENCE TRADE: QQQ
   💰 3 shares @ $520.85
   🎯 Final Confidence: 82.3%
   📊 Intelligence: Technical supports: buy (78%)
✅ Phase 3 cycle completed in 8.2s
⏳ Next cycle in 120 seconds...
```

### Risk Management Examples
- Trade rejection due to position limits
- Sector exposure limit protection
- Daily loss limit enforcement
- Automatic stop-loss execution