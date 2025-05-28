#!/usr/bin/env python3
"""
Phase 1 Production Entry Point
Enhanced Trading System with Intelligent Foundation
"""

import os
import sys
from datetime import datetime
from enhanced_trader_v2 import EnhancedTraderV2

def main():
    """Phase 1 production entry point"""
    print("🚀 PHASE 1: INTELLIGENT FOUNDATION")
    print("=" * 50)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("☁️ Platform: Railway Cloud")
    print("💰 Mode: Paper Trading")
    print("🧠 Version: Phase 1 - Intelligent Foundation")
    print()
    print("📊 NEW CAPABILITIES:")
    print("   • SQLite database for historical data")
    print("   • Expanded market universe (50+ stocks)")
    print("   • Enhanced market regime detection")
    print("   • Virtual trading performance tracking")
    print("   • Sector-based analysis")
    print("   • Comprehensive performance analytics")
    print()
    
    try:
        # Get market tier from environment or default to 2
        market_tier = int(os.environ.get('MARKET_TIER', '2'))
        
        # Initialize enhanced trader
        trader = EnhancedTraderV2(use_database=True, market_tier=market_tier)
        
        print(f"✅ Phase 1 system initialized (Market Tier: {market_tier})")
        print("🔄 Starting enhanced continuous monitoring...")
        print()
        
        # Run enhanced continuous system
        trader.run_enhanced_continuous()
        
    except Exception as e:
        print(f"❌ Phase 1 startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()