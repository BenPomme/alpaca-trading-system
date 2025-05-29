#!/usr/bin/env python3

import os
import sys
from datetime import datetime

def debug_phase3():
    """Debug Phase 3 initialization and first cycle"""
    
    print("🔧 PHASE 3 DEBUG MODE")
    print("=" * 50)
    print(f"⏰ Debug Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    print(f"   EXECUTION_ENABLED: {os.getenv('EXECUTION_ENABLED', 'NOT SET')}")
    print(f"   MARKET_TIER: {os.getenv('MARKET_TIER', 'NOT SET')}")
    print(f"   MIN_CONFIDENCE: {os.getenv('MIN_CONFIDENCE', 'NOT SET')}")
    print(f"   ALPACA_PAPER_API_KEY: {'SET' if os.getenv('ALPACA_PAPER_API_KEY') else 'NOT SET'}")
    print(f"   ALPACA_PAPER_SECRET_KEY: {'SET' if os.getenv('ALPACA_PAPER_SECRET_KEY') else 'NOT SET'}")
    
    try:
        print("\n🧠 Testing Phase 3 Trader Import...")
        from phase3_trader import Phase3Trader
        print("✅ Phase3Trader imported successfully")
        
        print("\n🧠 Testing Phase 3 Trader Initialization...")
        trader = Phase3Trader(use_database=True, market_tier=2)
        trader.execution_enabled = False  # Safe for testing
        print("✅ Phase3Trader initialized successfully")
        
        print("\n🧠 Testing Single Intelligence Cycle...")
        trader.run_trading_cycle_with_intelligence()
        print("✅ Single cycle completed successfully")
        
        print("\n🎯 DEBUG COMPLETE - Phase 3 working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ DEBUG FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_phase3()
    sys.exit(0 if success else 1)