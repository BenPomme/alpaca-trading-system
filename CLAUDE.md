# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Guidelines

**BEFORE making any changes to this codebase:**
1. **Read QA.md thoroughly** - Contains critical bug prevention rules and deployment lessons learned from 9+ major bugs
2. **Apply all 9 QA rules** - Must be followed to prevent recurring bugs (inheritance, data contracts, defensive programming)
3. **Verify inheritance chains** - Check attribute/method availability before accessing (QA Rule 1 & 6)
4. **Validate data structures** - Ensure consistent data formats between modules (QA Rule 5)
5. **Test with minimal data** - Verify startup behavior when market data is limited (QA Rule 4)
6. **Follow defensive programming** - Use .get() methods and provide defaults (QA Rule 5)
7. **Update QA.md with new lessons** - Document any new bugs/fixes for future prevention

## Project Architecture

### Multi-Asset Trading System
This is an institutional-grade algorithmic trading system targeting 5-10% monthly returns through:
- **📊 Real Options Trading**: Alpaca API integration with 5 sophisticated strategies  
- **₿ 24/7 Cryptocurrency Trading**: 13 cryptocurrencies with session-aware strategies
- **📈 Enhanced Stock Strategies**: 3x leveraged ETFs, sector rotation, momentum amplification
- **🧠 Intelligent Exit Management**: ML-powered exit system with 5-component analysis

### Core Architecture Stack
```
Phase3Trader (Intelligence Layer)
    ↳ Phase2Trader (Execution Engine)  
        ↳ EnhancedTraderV2 (Expanded Universe)
            ↳ EnhancedTrader (Database Foundation)
```

**Alternative: Modular System** (Production)
```
ModularOrchestrator
    ↳ OptionsModule
    ↳ CryptoModule  
    ↳ StocksModule
    ↳ MLOptimizer
    ↳ RiskManager
```

### Production Deployment
- **Primary**: Railway Cloud deployment via `modular_production_main.py`
- **Legacy**: Phase 3 system via `start_phase3.py`
- **Procfile**: `web: python modular_production_main.py`
- **Environment**: Paper trading only (Alpaca Paper API)

## Development Commands

### Essential Commands
```bash
# Primary production system test
python modular_production_main.py

# Legacy intelligence system test  
python start_phase3.py

# Complete system integration test
python test_phase4_complete.py

# Debug full trading cycle locally
python debug_cycle.py

# ML integration verification
python test_ml_integration.py

# Individual component testing
python options_manager.py
python crypto_trader.py
```

### Performance Analysis (MANDATORY)
```bash
# Weekly performance analysis - REQUIRED
python analyze_trading_performance.py

# Emergency order cancellation
python emergency_cancel_all_orders.py

# Database functionality test
python database_manager.py
```

### Testing Framework
```bash
# Complete modular framework test
python test_modular_framework.py

# Phase 3 standalone test
python test_phase3_standalone.py

# Global trading test
python test_global_trading.py

# ML integration test
python test_ml_integration.py
```

### Railway Deployment
```bash
# Check deployment status
railway status

# View live logs (may be truncated)
railway logs

# Deployment verification
python railway_deploy.py

# Environment variable verification
python railway_setup_verification.py
```

## Required Environment Variables

### Core Trading API
```bash
ALPACA_PAPER_API_KEY=your_paper_key
ALPACA_PAPER_SECRET_KEY=your_paper_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

### System Configuration
```bash
EXECUTION_ENABLED=true
GLOBAL_TRADING=true
OPTIONS_TRADING=true
CRYPTO_TRADING=true
MARKET_TIER=2
MIN_CONFIDENCE=0.6
MIN_TECHNICAL_CONFIDENCE=0.6
```

### Modular System
```bash
MODULAR_SYSTEM=true
ML_OPTIMIZATION=true
INTRADAY_CYCLE_DELAY=60
```

### Firebase Integration (Optional)
```bash
# Firebase service account JSON (for cloud sync)
FIREBASE_SERVICE_ACCOUNT={"type":"service_account",...}
```

## Data Architecture

### Quote Data Format (Critical - QA Rule 5)
```python
# Standard format across all modules
{
    'symbol': str,      # Stock symbol (e.g., 'SPY')
    'bid': float,       # Bid price
    'ask': float,       # Ask price (use for buying)
    'timestamp': str    # ISO format timestamp
    'volume': int       # Optional - use .get() with default
}
```

### Intelligence Module Response Format
```python
# All intelligence modules must return complete structures
{
    'timestamp': datetime.now().isoformat(),
    'status': 'success',  # Always include status
    'data': {},           # Always include data section
    'metadata': {},       # Always include metadata
    'confidence': float,  # 0.0 to 1.0
    'note': str          # Status/limitations note
}
```

### Position Data Contracts (QA Rule 9)
```python
# Use defensive access for Alpaca Position objects
try:
    if hasattr(position, 'avg_entry_price'):
        entry_price = float(position.avg_entry_price)
    elif hasattr(position, 'cost_basis'):
        entry_price = float(position.cost_basis)
    else:
        # Calculate fallback
        entry_price = float(position.market_value) / float(position.qty)
except Exception as e:
    # Handle gracefully
    continue
```

## File Organization

### Core Trading Components
- `phase3_trader.py` - Main intelligence trading engine
- `enhanced_trader_v2.py` - Expanded market universe trader
- `enhanced_trader.py` - Database foundation trader

### Modular Architecture
- `modular/orchestrator.py` - Main coordination system
- `modular/options_module.py` - Options trading module
- `modular/crypto_module.py` - Cryptocurrency trading
- `modular/stocks_module.py` - Enhanced stock strategies
- `modular/ml_optimizer.py` - Machine learning integration

### Asset-Specific Managers
- `options_manager.py` - Real options trading via Alpaca API
- `crypto_trader.py` - 24/7 cryptocurrency trading
- `global_market_manager.py` - Multi-timezone market coordination
- `intelligent_exit_manager.py` - ML-powered exit system

### Intelligence Components
- `market_regime_detector.py` - Bull/Bear/Sideways detection
- `technical_indicators.py` - RSI, MACD, Bollinger Bands
- `pattern_recognition.py` - Breakouts, support/resistance
- `ml_adaptive_framework.py` - Strategy selection and optimization

### Database & Analytics
- `database_manager.py` - SQLite data persistence
- `firebase_database.py` - Cloud sync capabilities
- `performance_tracker.py` - Performance analytics
- `analyze_trading_performance.py` - Comprehensive analysis

### Deployment & Monitoring
- `modular_production_main.py` - Production entry point
- `railway_deploy.py` - Railway deployment verification
- `production_health_check.py` - System health monitoring
- `debug_cycle.py` - Local debugging tool

## Testing Strategy

### Pre-Deployment Checklist (QA.md)
- [ ] Test all inheritance chain attributes and methods
- [ ] Verify method signatures match expected parameters
- [ ] Verify data structure compatibility between modules
- [ ] Test startup behavior with minimal/no market data
- [ ] Validate all expected dictionary keys exist
- [ ] Test error handling and graceful degradation
- [ ] Run standalone module tests before integration

### Integration Testing Sequence
1. `python test_modular_framework.py` - Test modular architecture
2. `python test_ml_integration.py` - Verify ML components
3. `python test_phase4_complete.py` - Full system integration
4. `python debug_cycle.py` - Local cycle verification
5. `python railway_deploy.py` - Deployment verification

## Performance Monitoring

### Key Metrics to Track
- **Win Rate**: Target 45-60% (baseline was 13.2%)
- **Average Hold Time**: Target 2-8 hours (was 6 minutes)
- **Monthly Returns**: Target 5-10%
- **Maximum Drawdown**: 20% risk tolerance
- **Position Scaling**: Unlimited positions (35+ concurrent)

### Health Check Endpoints
- `/health` - Basic system health
- `/status` - Detailed system status
- `/metrics` - Performance metrics

## Debugging Guidelines

### Railway Log Truncation Workaround
Railway often truncates logs. Use local debug for full output:
```bash
# See full system output locally
python debug_cycle.py | head -200

# Check specific components
python debug_cycle.py 2>&1 | grep -A 10 "INTELLIGENT EXIT"
python debug_cycle.py 2>&1 | grep -A 5 "ML Predictions"
```

### Common Error Patterns (From QA.md)
1. **AttributeError**: Check inheritance chains, verify parent class attributes
2. **KeyError**: Use defensive `.get()` methods, ensure complete data structures
3. **Method signature mismatch**: Check existing successful calls for patterns
4. **Silent initialization failures**: Verify all dependencies before creating objects

### Critical Success Indicators
```
✅ Trades Executed: X (should be > 0 if market conditions allow)
🧠 ML Adaptive Framework: ✅ Enabled
💼 POSITION MONITORING & EXIT MANAGEMENT
📊 OPTIONS TRADING (if enabled)
₿ CRYPTO TRADING CYCLE (if enabled)
```

## Security & Risk Management

### Portfolio-Level Controls
- **Options Allocation**: 30% maximum exposure
- **Crypto Allocation**: 20% maximum with 1.5x leverage
- **Sector Limits**: 40% maximum per sector
- **Position Limits**: 15% maximum per symbol
- **Drawdown Protection**: 20% maximum portfolio drawdown

### API Security
- **Paper Trading Only**: All operations use Alpaca Paper API
- **No Credentials in Code**: All keys via environment variables
- **Defensive Programming**: Extensive error handling and graceful degradation

## Documentation References

- **QA.md**: MANDATORY reading - contains 9 critical bug prevention rules
- **README.md**: High-level system overview and performance targets
- **MODULAR_ARCHITECTURE.md**: Detailed modular system design
- **ML_OPTIMIZATION.md**: Machine learning integration details
- **deployment_logs/**: Firebase deployment history and issues

## Development Workflow

1. **Before ANY changes**: Read QA.md rules thoroughly
2. **Inheritance modifications**: Verify all parent class attributes/methods
3. **Data structure changes**: Ensure consistency across all consumers
4. **New intelligence modules**: Always return complete, valid data structures
5. **Testing**: Run full integration tests before deployment
6. **Documentation**: Update QA.md with any new issues discovered
7. **Deployment**: Use Railway deployment verification process

Remember: This system has encountered 9+ major bugs during development. The QA.md rules are institutional knowledge that MUST be followed to prevent regression.

## 🎉 LATEST STATUS (Dec 31, 2024):

### MAJOR BREAKTHROUGH: Crypto Analysis Fixed!
- ✅ **Real crypto prices working**: AVAX=$20.99, UNI=$6.16, BTC=$67k+
- ✅ **9 crypto opportunities found** (vs 0 before fix)
- ✅ **High confidence scores**: 0.73 > 0.35 threshold
- ✅ **Correct Alpaca API usage**: get_latest_crypto_bars(), proper BTC/USD format

### Current Issues to Fix:
1. **Risk Manager**: `'NoneType' object has no attribute 'validate_opportunity'` 
2. **Firebase**: Missing `save_trade_opportunity()` method
3. **Unsupported Cryptos**: 4/13 cryptos not available in Alpaca Paper API

### See CURRENT_STATUS_DEC31.md for detailed action plan