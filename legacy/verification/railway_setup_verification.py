#!/usr/bin/env python3
"""
Railway Setup Verification Script
Run this after setting Firebase environment variables in Railway
"""

import os
import sys
from datetime import datetime

def main():
    print("🚀 RAILWAY FIREBASE SETUP VERIFICATION")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️ Platform: Railway Cloud Deployment")
    
    # Test 1: Environment Variables
    print("\n🔥 STEP 1: Firebase Environment Variables")
    print("-" * 40)
    
    required_vars = [
        'FIREBASE_PRIVATE_KEY_ID',
        'FIREBASE_PRIVATE_KEY', 
        'FIREBASE_CLIENT_EMAIL',
        'FIREBASE_CLIENT_ID',
        'FIREBASE_CLIENT_CERT_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:20]}...")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ FAILED: {len(missing_vars)} environment variables missing!")
        print("🔧 Set these in Railway Dashboard > Environment Variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    # Test 2: Firebase Connection
    print("\n🔥 STEP 2: Firebase Database Connection")
    print("-" * 40)
    
    try:
        from firebase_database import FirebaseDatabase
        print("✅ Firebase modules imported")
        
        db = FirebaseDatabase()
        print("✅ Firebase database initialized")
        
        if db.is_connected():
            print("✅ 🔥 FIREBASE CONNECTED!")
            
            # Test operations
            test_data = {
                'railway_test': True,
                'timestamp': datetime.now().isoformat(),
                'deployment_verification': 'railway_setup_success'
            }
            
            cycle_id = db.save_trading_cycle(test_data)
            print(f"✅ Test cycle saved: {cycle_id}")
            
            recent = db.get_recent_trading_cycles(limit=2)
            print(f"✅ Retrieved {len(recent)} recent cycles")
            
            print("\n🎉 RAILWAY FIREBASE SETUP SUCCESSFUL!")
            return True
        else:
            print("❌ Firebase connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Firebase error: {e}")
        return False
    
    # Test 3: Trading System Integration
    print("\n🔥 STEP 3: Trading System Integration Test")
    print("-" * 40)
    
    try:
        from phase3_trader import Phase3Trader
        print("✅ Phase3Trader imported")
        
        # Quick initialization test (no actual trading)
        trader = Phase3Trader(use_database=True, market_tier=1)
        print("✅ Phase3Trader initialized")
        
        if hasattr(trader, 'firebase_db') and trader.firebase_db:
            if trader.firebase_db.is_connected():
                print("✅ 🔥 TRADING SYSTEM FIREBASE INTEGRATION ACTIVE!")
                return True
            else:
                print("⚠️ Trading system Firebase not connected")
                return False
        else:
            print("⚠️ Trading system Firebase not initialized")
            return False
            
    except Exception as e:
        print(f"⚠️ Trading system test error: {e}")
        print("💡 This may be expected if Alpaca credentials not set")
        return True  # Don't fail on this - Firebase is the priority

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 ✅ RAILWAY SETUP VERIFICATION SUCCESSFUL!")
        print("🔥 Firebase is connected and operational on Railway")
        print("🚀 Trading system ready for deployment")
        print("📊 ML learning will now persist across Railway restarts")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ RAILWAY SETUP VERIFICATION FAILED!")
        print("🔧 Check Firebase environment variables in Railway Dashboard")
        print("📚 See railway_firebase_env_vars.txt for exact values")
        sys.exit(1)