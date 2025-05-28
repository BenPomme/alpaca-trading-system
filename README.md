# Ultra-Simple Adaptive Trading System

Minimal algorithmic trading system for Railway deployment.

## ✅ What This Does

- **Market Analysis**: Monitors SPY, QQQ, IWM every 2 minutes
- **Strategy Selection**: Adaptive momentum vs conservative based on market activity
- **Continuous Operation**: Runs 24/7 on Railway cloud
- **Complete Logging**: All activity logged with timestamps
- **Paper Trading**: Safe testing with $100K virtual account

## 🚀 Deployment

**Railway Auto-Deployment:**
1. Connected to GitHub repo for automatic updates
2. Single dependency: `alpaca-trade-api`
3. Worker service runs continuously
4. Environment variables configured for Alpaca paper trading

**Expected Logs:**
```
✅ Alpaca API ready
✅ Connected to Alpaca Paper Trading
📊 Portfolio Value: $100,000.00
🔄 Starting continuous monitoring...

📊 Cycle #1
🔄 TRADING CYCLE - 15:30:15
📈 Getting market data...
   SPY: $591.60
   QQQ: $522.34
   IWM: $207.92
🎯 Market Regime: active (80%)
🎯 Strategy: momentum
✅ Cycle completed
⏳ Next cycle in 120 seconds...
```

## 🎯 System Features

- **Ultra-Minimal**: Only essential dependencies for maximum reliability
- **Error Recovery**: Automatic restart on failures
- **Resource Efficient**: Minimal CPU/memory usage
- **Transparent**: Complete activity logging in JSON format
- **Scalable**: Can be extended with additional strategies

## 📊 Performance

- **Cycle Frequency**: Every 2 minutes
- **Market Coverage**: SPY, QQQ, IWM (broad market representation)
- **Regime Detection**: Active vs uncertain market classification
- **Strategy Adaptation**: Momentum for active markets, conservative for uncertain

Targeting 10% monthly returns through systematic adaptation and intelligent market analysis.

---

**🤖 Generated with Claude Code (https://claude.ai/code)**

**⚠️ Disclaimer**: This is experimental trading software for paper trading only. Not financial advice.