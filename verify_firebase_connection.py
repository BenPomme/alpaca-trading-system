#!/usr/bin/env python3
"""
Firebase Connection Verification Script
Verifies Firebase integration is working correctly for the trading system
"""

import os
import sys
from datetime import datetime

def check_environment_variables():
    """Check if all required Firebase environment variables are set"""
    required_vars = [
        'FIREBASE_PRIVATE_KEY_ID',
        'FIREBASE_PRIVATE_KEY', 
        'FIREBASE_CLIENT_EMAIL',
        'FIREBASE_CLIENT_ID',
        'FIREBASE_CLIENT_CERT_URL'
    ]
    
    print("🔥 FIREBASE ENVIRONMENT VARIABLES CHECK")
    print("=" * 50)
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show first 20 chars for verification without exposing secrets
            print(f"✅ {var}: {value[:20]}...")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing {len(missing_vars)} required environment variables!")
        return False
    else:
        print(f"\n✅ All {len(required_vars)} Firebase environment variables are set")
        return True

def test_firebase_connection():
    """Test Firebase connection"""
    print("\n🔥 FIREBASE CONNECTION TEST")
    print("=" * 40)
    
    try:
        print("📦 Importing Firebase modules...")
        from firebase_database import FirebaseDatabase
        print("✅ Firebase modules imported successfully")
        
        print("🔗 Initializing Firebase connection...")
        db = FirebaseDatabase()
        print("✅ FirebaseDatabase object created")
        
        print("🌐 Testing connection...")
        is_connected = db.is_connected()
        
        if is_connected:
            print("✅ 🔥 FIREBASE CONNECTION SUCCESSFUL!")
            
            # Test basic operations
            print("\n📊 Testing basic Firebase operations...")
            
            # Test saving a test record
            test_data = {
                'test_timestamp': datetime.now().isoformat(),
                'test_type': 'connection_verification',
                'system_status': 'firebase_connected'
            }
            
            try:
                cycle_id = db.save_trading_cycle(test_data)
                print(f"✅ Test trading cycle saved: {cycle_id}")
                
                # Test retrieving recent cycles
                recent_cycles = db.get_recent_trading_cycles(limit=3)
                print(f"✅ Retrieved {len(recent_cycles)} recent cycles")
                
                print("\n🎉 FIREBASE FULLY OPERATIONAL!")
                return True
                
            except Exception as op_error:
                print(f"⚠️ Firebase operations error: {op_error}")
                return False
        else:
            print("❌ 🔥 FIREBASE CONNECTION FAILED!")
            return False
            
    except ImportError as e:
        print(f"❌ Firebase import error: {e}")
        print("💡 Make sure firebase-admin and google-cloud-firestore are installed")
        return False
    except Exception as e:
        print(f"❌ Firebase connection error: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 FIREBASE VERIFICATION SCRIPT")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check environment variables
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\n❌ VERIFICATION FAILED: Missing environment variables")
        print("\n📋 REQUIRED RAILWAY ENVIRONMENT VARIABLES:")
        print("FIREBASE_PRIVATE_KEY_ID=1cc8ac3693bfd2b08e40582f3564da2a3c06d978")
        print("FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----")
        print("FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@alpaca-12fab.iam.gserviceaccount.com")
        print("FIREBASE_CLIENT_ID=105751822466253435094")
        print("FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40alpaca-12fab.iam.gserviceaccount.com")
        sys.exit(1)
    
    # Step 2: Test Firebase connection
    connection_ok = test_firebase_connection()
    
    if connection_ok:
        print("\n🎉 ✅ FIREBASE VERIFICATION SUCCESSFUL!")
        print("🔥 Firebase is properly connected and operational")
        print("🚀 Trading system can now use persistent Firebase storage")
        sys.exit(0)
    else:
        print("\n❌ FIREBASE VERIFICATION FAILED!")
        print("🔍 Check Firebase credentials and network connectivity")
        sys.exit(1)

if __name__ == "__main__":
    main()