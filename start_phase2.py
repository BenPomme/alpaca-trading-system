#!/usr/bin/env python3
"""
Phase 2 Production Entry Point
Trading System with Actual Execution Engine
"""

import os
import sys
from datetime import datetime
from phase2_trader import Phase2Trader

def main():
    """Phase 2 production entry point"""
    print("🚀 PHASE 2: EXECUTION ENGINE")
    print("=" * 50)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("☁️ Platform: Railway Cloud")
    print("💰 Mode: Paper Trading with ACTUAL EXECUTION")
    print("🧠 Version: Phase 2 - Execution Engine")
    print()
    print("📊 NEW CAPABILITIES:")
    print("   • Actual paper trade execution via Alpaca API")
    print("   • Advanced risk management (5 max positions, 2% risk per trade)")
    print("   • Position sizing based on strategy and confidence")
    print("   • Automatic stop-loss (3%) and take-profit (8%)")
    print("   • Portfolio-level risk controls (5% daily loss limit)")
    print("   • Sector exposure management (40% max per sector)")
    print("   • Real-time position monitoring")
    print()
    
    try:
        # Get configuration from environment
        market_tier = int(os.environ.get('MARKET_TIER', '2'))
        execution_enabled = os.environ.get('EXECUTION_ENABLED', 'true').lower() == 'true'
        min_confidence = float(os.environ.get('MIN_CONFIDENCE', '0.7'))
        
        print(f"⚙️ CONFIGURATION:")
        print(f"   • Market Tier: {market_tier} ({'Core ETFs' if market_tier == 1 else 'Expanded Universe'})")
        print(f"   • Execution: {'ENABLED' if execution_enabled else 'DISABLED'}")
        print(f"   • Min Confidence: {min_confidence:.1%}")
        print()
        
        # Initialize Phase 2 trader
        trader = Phase2Trader(use_database=True, market_tier=market_tier)
        trader.execution_enabled = execution_enabled
        trader.min_confidence_to_trade = min_confidence
        
        if not execution_enabled:
            print("⚠️ EXECUTION DISABLED - Running in analysis mode")
            print("   Set EXECUTION_ENABLED=true to enable actual trading")
            print()
        else:
            print("🎯 EXECUTION ENABLED - System will place actual paper trades")
            print("   ⚠️ This uses real Alpaca API calls")
            print("   ⚠️ Trades will appear in your Alpaca paper account")
            print()
        
        print(f"✅ Phase 2 system initialized")
        print("🔄 Starting execution engine...")
        print()
        
        # Run Phase 2 continuous system
        trader.run_phase2_continuous()
        
    except Exception as e:
        print(f"❌ Phase 2 startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()