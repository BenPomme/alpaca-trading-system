# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an ultra-minimal adaptive algorithmic trading system designed for Railway cloud deployment. The system monitors market conditions every 2 minutes, adapts trading strategies based on market regime detection, and runs continuously with maximum reliability. Built specifically for paper trading with Alpaca Markets API, targeting 10% monthly returns through systematic market analysis.

## Key Commands

### Environment Setup
```bash
# Install single dependency
pip install alpaca-trade-api

# Set environment variables for Alpaca paper trading
export ALPACA_PAPER_API_KEY="your_key_here"
export ALPACA_PAPER_SECRET_KEY="your_secret_here"

# Test system locally
python start_ultra_simple.py
```

### Railway Deployment
```bash
# Deploy to Railway (automated GitHub integration)
# Railway will automatically build from Procfile and requirements.txt
# Add environment variables in Railway dashboard:
# ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY
```

### GitHub Deployment (Automated)
```bash
# Use deployment scripts (Claude handles this automatically)
bash deploy_with_token.sh
# Or follow FINAL_DEPLOY_COMMANDS.md for manual deployment
```

## Ultra-Minimal Architecture

This system prioritizes reliability over complexity with a single-file architecture:

### Core Component
- **`start_ultra_simple.py`**: Complete trading system (212 lines)
  - `UltraSimpleTrader` class: Main trading logic
  - Market regime detection via SPY/QQQ/IWM analysis
  - Strategy selection (momentum vs conservative)
  - Continuous monitoring loop with error recovery
  - JSON logging for complete transparency

### Deployment Files
- **`Procfile`**: Railway worker configuration (`worker: python start_ultra_simple.py`)
- **`requirements.txt`**: Single dependency (`alpaca-trade-api`)
- **`runtime.txt`**: Python version specification (`python-3.11`)

### Supporting Documentation
- **`README.md`**: System overview and features
- **`FINAL_DEPLOY_COMMANDS.md`**: Complete deployment instructions
- **Deployment scripts**: Automated GitHub repository creation and pushing

## Trading System Logic

### Market Regime Detection
1. **Data Collection**: Real-time quotes from SPY, QQQ, IWM every 2 minutes
2. **Regime Classification**: 
   - `active` (≥2 successful quote retrievals) → momentum strategy
   - `uncertain` (<2 quotes) → conservative strategy
3. **Confidence Scoring**: Based on data availability and market responsiveness

### Strategy Implementation
- **Momentum Strategy**: Used during active market conditions
- **Conservative Strategy**: Used during uncertain/low-data conditions
- **Adaptive Switching**: Automatic strategy selection based on real-time market regime

### Error Recovery & Reliability
- **Connection Failures**: Automatic retry with graceful degradation
- **API Errors**: Comprehensive error logging without system crash
- **Data Gaps**: Fallback to conservative strategy when market data unavailable
- **System Restart**: Automatic recovery from unexpected errors with 60-second delay

## Important Configuration

### Railway Cloud Deployment
- **Resource Requirements**: Minimal (single dependency, low CPU/memory)
- **Service Type**: Worker (continuous background process)
- **Restart Policy**: Automatic restart on failure
- **Environment Variables**: ALPACA_PAPER_API_KEY, ALPACA_PAPER_SECRET_KEY
- **Always do GitHub deployments automatically and handle Railway integration**

### Trading Parameters
- **Cycle Frequency**: 120 seconds (2 minutes) between market scans
- **Market Universe**: SPY, QQQ, IWM (broad market representation)
- **Paper Trading**: $100,000 virtual account for safe testing
- **Risk Management**: Built into strategy selection logic

## Data Persistence

### Local Logging
- **Log File**: `data/trading_log.json` (created automatically)
- **Log Retention**: Last 100 trading cycles only
- **Log Content**: Timestamp, market regime, strategy selection, quote count per cycle

### Railway Cloud Logging
- **System Logs**: Available through Railway dashboard
- **Error Tracking**: All exceptions logged with full stack traces
- **Performance Monitoring**: Cycle completion times and success rates

## Development Notes

### Minimal Dependencies
- **Single Requirement**: `alpaca-trade-api` only (eliminates complex dependency conflicts)
- **Fallback Imports**: Optional `python-dotenv` with environment variable fallback
- **No Complex Libraries**: No pandas, numpy, or technical analysis libraries for maximum reliability

### Railway Optimization
- **Build Speed**: Ultra-fast deployment due to minimal dependencies
- **Resource Efficiency**: Low memory footprint, minimal CPU usage
- **Error Resilience**: Extensive error handling prevents deployment failures
- **Automatic Scaling**: Designed for Railway's automatic restart capabilities

### GitHub Integration
- **Automated Deployment**: Claude handles all git commands and repository management
- **Token Authentication**: Uses provided GitHub personal access token
- **Repository Structure**: Minimal file count for clean deployment
- **Commit Strategy**: Descriptive commits with full system documentation

## Expected System Behavior

### Successful Operation Logs
```
✅ Alpaca API ready
✅ Connected to Alpaca Paper Trading
📊 Portfolio Value: $100,000.00
🔄 Starting continuous monitoring...
📊 Cycle #1
🔄 TRADING CYCLE - HH:MM:SS
📈 Getting market data...
   SPY: $XXX.XX
   QQQ: $XXX.XX
   IWM: $XXX.XX
🎯 Market Regime: active (80%)
🎯 Strategy: momentum
✅ Cycle completed
⏳ Next cycle in 120 seconds...
```

### Error Recovery Examples
- Missing credentials → Clean error message and system exit
- API connection failure → Error logging and automatic retry
- Market data unavailable → Conservative strategy activation
- Unexpected system error → 60-second delay and restart attempt