#!/usr/bin/env python3

import os
import sys
from datetime import datetime

def main():
    """
    Phase 3 Intelligence Layer Entry Point
    
    Launches the sophisticated algorithmic trading system with:
    - Technical indicators (RSI, MACD, Bollinger Bands)
    - Enhanced market regime detection (Bull/Bear/Sideways)
    - Pattern recognition (breakouts, support/resistance, mean reversion)
    - Intelligent trade execution with multi-factor analysis
    """
    
    print("🧠 PHASE 3 INTELLIGENCE LAYER STARTING")
    print("=" * 60)
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration from environment variables
    execution_enabled = os.getenv('EXECUTION_ENABLED', 'true').lower() == 'true'  # Default to enabled for Phase 3
    market_tier = int(os.getenv('MARKET_TIER', '2'))
    min_confidence = float(os.getenv('MIN_CONFIDENCE', '0.6'))  # Lowered from 0.7 to enable trading
    min_technical_confidence = float(os.getenv('MIN_TECHNICAL_CONFIDENCE', '0.6'))
    global_trading = os.getenv('GLOBAL_TRADING', 'true').lower() == 'true'  # Phase 4.1: Global markets - ENABLED by default
    options_trading = os.getenv('OPTIONS_TRADING', 'true').lower() == 'true'  # Phase 4.3: Options trading - ENABLED with real API
    crypto_trading = os.getenv('CRYPTO_TRADING', 'true').lower() == 'true'  # Phase 4.4: 24/7 crypto trading - ENABLED by default
    
    print(f"⚡ Execution: {'ENABLED' if execution_enabled else 'DISABLED'}")
    print(f"🎯 Market Tier: {market_tier}")
    print(f"📊 Min Confidence: {min_confidence:.1%}")
    print(f"🧠 Min Technical Confidence: {min_technical_confidence:.1%}")
    print(f"🌍 Global Trading: {'ENABLED' if global_trading else 'DISABLED'}")
    print(f"📊 Options Trading: {'ENABLED' if options_trading else 'DISABLED'}")
    print(f"₿ Crypto Trading: {'ENABLED' if crypto_trading else 'DISABLED'}")
    
    # Check for required credentials
    alpaca_key = os.getenv('ALPACA_PAPER_API_KEY')
    alpaca_secret = os.getenv('ALPACA_PAPER_SECRET_KEY')
    
    if not alpaca_key or not alpaca_secret:
        print("\n❌ ERROR: Missing Alpaca API credentials")
        print("Set environment variables:")
        print("  ALPACA_PAPER_API_KEY")
        print("  ALPACA_PAPER_SECRET_KEY")
        return 1
    
    try:
        # Initialize cloud database sync for Railway deployment
        print("\n☁️ Initializing cloud database sync...")
        try:
            from cloud_database import CloudDatabase
            cloud_db = CloudDatabase()
            # Sync from cloud to get latest trading data
            cloud_db.sync_from_github()
            print("✅ Cloud database sync completed")
        except Exception as e:
            print(f"⚠️ Cloud sync failed: {e} - continuing with local data")
        
        # Import and initialize Phase 3 trader
        from phase3_trader import Phase3Trader
        
        print("\n🧠 Initializing Phase 3 Intelligence Trader...")
        
        trader = Phase3Trader(
            use_database=True, 
            market_tier=market_tier, 
            global_trading=global_trading,
            options_trading=options_trading,
            crypto_trading=crypto_trading
        )
        trader.execution_enabled = execution_enabled
        trader.min_confidence_to_trade = min_confidence
        trader.min_technical_confidence = min_technical_confidence
        
        print("✅ Phase 3 Trader initialized successfully")
        
        # Display system capabilities
        print(f"\n🎯 PHASE 4 CAPABILITIES:")
        print(f"   📊 Technical Indicators: RSI, MACD, Bollinger Bands, Moving Averages")
        print(f"   🎯 Market Regime Detection: Bull/Bear/Sideways with confidence scoring")
        print(f"   🔍 Pattern Recognition: Breakouts, Support/Resistance, Mean Reversion")
        print(f"   🧠 Intelligence Integration: Multi-factor decision making")
        print(f"   💼 Risk Management: Advanced portfolio-level controls")
        print(f"   📊 Enhanced Stock Strategies: 3x Leveraged ETFs, Sector Rotation, Momentum 2x, Volatility Trading")
        if options_trading:
            print(f"   📊 Real Options Trading: Long calls, bull spreads, protective puts, covered calls, straddles")
        if crypto_trading:
            print(f"   ₿ 24/7 Crypto Trading: BTC, ETH, ADA, SOL + momentum strategies")
        if global_trading:
            print(f"   🌍 Global Markets: Asian ADRs, European ETFs, multi-timezone trading")
        print(f"   📈 Aggressive Target: 5-10% monthly returns, 20% max drawdown")
        
        # Start continuous trading
        print(f"\n🚀 Starting continuous intelligent trading...")
        trader.run_continuous_intelligence_trading()
        
        return 0
        
    except ImportError as e:
        print(f"\n❌ Import Error: {str(e)}")
        print("Install required dependencies:")
        print("  pip install alpaca-trade-api")
        return 1
    
    except Exception as e:
        print(f"\n❌ System Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())