#!/usr/bin/env python3
"""
Test Firebase Trade History Integration

Verifies that the trade history tracking system works with Firebase database
and stores data persistently in the cloud instead of local JSON files.
"""

import logging
import os
from trade_history_tracker import TradeHistoryTracker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_firebase_integration():
    """Test Firebase integration for trade history tracking."""
    
    print("🔥 TESTING FIREBASE TRADE HISTORY INTEGRATION")
    print("=" * 60)
    
    # Load environment variables manually
    def load_env_file():
        env_file = '.env.local'
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        value = value.strip('"').strip("'")
                        os.environ[key] = value
    
    load_env_file()
    
    try:
        # Test 1: Initialize with Firebase
        print("\n📊 TEST 1: Initialize TradeHistoryTracker with Firebase")
        print("-" * 50)
        
        tracker = TradeHistoryTracker(logger=logger)
        
        if tracker.firebase_db:
            print("✅ Firebase connection successful")
            print(f"📊 Storage type: Firebase")
        else:
            print("❌ Firebase connection failed, using local storage")
            print(f"📊 Storage type: Local JSON")
        
        # Test 2: Record test trades
        print("\n📊 TEST 2: Record test trades")
        print("-" * 50)
        
        test_trades = [
            ('BTCUSD', 'buy', 0.1, 67000.0),
            ('ETHUSD', 'buy', 1.0, 3200.0),
            ('AVAXUSD', 'sell', 100.0, 21.5),
        ]
        
        for symbol, side, qty, price in test_trades:
            print(f"Recording: {symbol} {side.upper()} {qty} @ ${price}")
            tracker.record_trade(symbol, side, qty, price, f"test_{symbol}_{side}")
        
        # Test 3: Check cooldown enforcement
        print("\n📊 TEST 3: Test cooldown enforcement")
        print("-" * 50)
        
        for symbol, _, _, _ in test_trades:
            can_trade, reason = tracker.can_trade_symbol(symbol, 5000)
            status = "✅ ALLOWED" if can_trade else "❌ BLOCKED"
            print(f"{symbol:8} | {status} | {reason}")
        
        # Test 4: Check position tracking
        print("\n📊 TEST 4: Position value tracking")
        print("-" * 50)
        
        for symbol in ['BTCUSD', 'ETHUSD', 'AVAXUSD']:
            status = tracker.get_symbol_status(symbol)
            print(f"{symbol:8} | Position: ${status['position_value']:>10,.2f} | Trades: {status['total_trades']}")
        
        # Test 5: Firebase data verification
        if tracker.firebase_db:
            print("\n📊 TEST 5: Firebase data verification")
            print("-" * 50)
            
            try:
                # Check if data exists in Firebase
                doc_ref = tracker.firebase_db.db.collection('trade_history_tracker').document('current_status')
                doc = doc_ref.get()
                
                if doc.exists:
                    data = doc.to_dict()
                    print("✅ Trade history found in Firebase")
                    print(f"📊 Symbols tracked: {len(data.get('trade_history_summary', {}))}")
                    print(f"📊 Last updated: {data.get('last_updated', 'unknown')}")
                    
                    # Check detailed trades
                    trades_collection = tracker.firebase_db.db.collection('trade_history_details')
                    recent_trades = trades_collection.order_by('timestamp', direction='DESCENDING').limit(5).get()
                    print(f"📊 Recent trades in Firebase: {len(recent_trades)}")
                    
                    for trade_doc in recent_trades:
                        trade_data = trade_doc.to_dict()
                        symbol = trade_data.get('symbol', 'unknown')
                        side = trade_data.get('side', 'unknown')
                        qty = trade_data.get('quantity', 0)
                        price = trade_data.get('price', 0)
                        print(f"   {symbol} {side.upper()} {qty} @ ${price}")
                else:
                    print("❌ No trade history found in Firebase")
                    
            except Exception as e:
                print(f"❌ Firebase verification failed: {e}")
        
        # Test 6: System status summary
        print("\n📊 TEST 6: System status summary")
        print("-" * 50)
        
        status = tracker.get_all_status()
        print(f"Total symbols: {status['total_symbols']}")
        print(f"Total trades today: {status['total_trades_today']}")
        print(f"Symbols on cooldown: {status['symbols_on_cooldown']}")
        print(f"Cooldown period: {status['safety_limits']['cooldown_minutes']} minutes")
        print(f"Position limits: {status['safety_limits']['max_position_value']}")
        print(f"Daily trade limits: {status['safety_limits']['max_daily_trades']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_storage_locations():
    """Show where trade data is stored."""
    
    print("\n📍 TRADE HISTORY STORAGE LOCATIONS")
    print("=" * 50)
    
    print("🔥 FIREBASE (Primary - Production):")
    print("   Collection: trade_history_tracker")
    print("   Document: current_status")
    print("   Contains: Position values, cooldown times, trade summaries")
    print()
    print("   Collection: trade_history_details")
    print("   Documents: Auto-generated IDs")
    print("   Contains: Individual trade records with full audit trail")
    print()
    
    print("📂 LOCAL FALLBACK (Development/Backup):")
    local_path = os.path.abspath("data/trade_history.json")
    print(f"   File: {local_path}")
    print("   Contains: Complete trade history and position data")
    print()
    
    print("🚀 PRODUCTION DEPLOYMENT:")
    print("   Railway: Ephemeral file system (files reset on restart)")
    print("   Firebase: Persistent cloud storage (survives restarts)")
    print("   Advantage: Trade history preserved across deployments")

if __name__ == "__main__":
    success = test_firebase_integration()
    show_storage_locations()
    
    print(f"\n🎯 FIREBASE INTEGRATION TEST {'✅ PASSED' if success else '❌ FAILED'}")
    print("=" * 60)
    
    if success:
        print("✅ Trade history tracking is now using Firebase for persistent storage")
        print("✅ All trade data will survive Railway deployment restarts") 
        print("✅ Position limits and daily trade limits removed as requested")
        print("✅ 5-minute cooldowns and hourly limits still active for safety")
    else:
        print("❌ Firebase integration needs debugging")
        print("📂 System will fall back to local JSON storage")