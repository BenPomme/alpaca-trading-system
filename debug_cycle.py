#!/usr/bin/env python3
"""
Debug Cycle Analysis - Check why ML and exit features aren't showing in logs
"""

import os
from datetime import datetime

def debug_cycle():
    """Debug a single trading cycle to see what's happening"""
    print("🔍 DEBUGGING TRADING CYCLE")
    print("=" * 50)
    
    try:
        # Set environment
        os.environ['EXECUTION_ENABLED'] = 'false'  # Debug mode
        os.environ['MARKET_TIER'] = '1'  # Small universe
        
        from phase3_trader import Phase3Trader
        
        # Initialize trader
        trader = Phase3Trader(
            use_database=True,
            market_tier=1,
            global_trading=True,
            options_trading=True, 
            crypto_trading=True
        )
        
        print(f"\n✅ Trader initialized")
        print(f"   ML Framework: {'✅' if trader.ml_framework else '❌'}")
        print(f"   Exit Manager: {'✅' if trader.intelligent_exit_manager else '❌'}")
        print(f"   Options Manager: {'✅' if trader.options_manager else '❌'}")
        print(f"   Crypto Trader: {'✅' if trader.crypto_trader else '❌'}")
        
        # Run one cycle with detailed debugging
        print(f"\n🔍 RUNNING DEBUG CYCLE...")
        trader.run_trading_cycle_with_intelligence()
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_cycle()