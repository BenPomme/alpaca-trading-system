#!/usr/bin/env python3
"""
Debug Firebase Environment Variables
Check if Firebase credentials are properly loaded in Railway
"""

import os

def debug_firebase_env():
    """Debug Firebase environment variables"""
    print("🔍 FIREBASE ENVIRONMENT VARIABLES DEBUG")
    print("=" * 50)
    
    # Check each required environment variable
    required_vars = [
        'FIREBASE_PRIVATE_KEY_ID',
        'FIREBASE_PRIVATE_KEY',
        'FIREBASE_CLIENT_EMAIL',
        'FIREBASE_CLIENT_ID',
        'FIREBASE_CLIENT_CERT_URL'
    ]
    
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == 'FIREBASE_PRIVATE_KEY':
                # Show first/last chars of private key for security
                display_value = f"{value[:30]}...{value[-30:]}" if len(value) > 60 else "PRESENT"
                print(f"✅ {var}: {display_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            all_present = False
    
    print("\n" + "=" * 50)
    
    if all_present:
        print("✅ ALL FIREBASE ENVIRONMENT VARIABLES PRESENT")
        
        # Check private key format
        private_key = os.getenv('FIREBASE_PRIVATE_KEY', '')
        if '\\n' in private_key:
            print("✅ Private key contains \\n characters (correct format)")
        else:
            print("⚠️ Private key missing \\n characters (may need formatting)")
            
        if private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            print("✅ Private key has correct header")
        else:
            print("❌ Private key missing correct header")
            
        if private_key.endswith('-----END PRIVATE KEY-----\\n'):
            print("✅ Private key has correct footer")
        else:
            print("⚠️ Private key may be missing correct footer")
            
        # Test Firebase initialization
        print("\n🔥 Testing Firebase initialization...")
        try:
            import firebase_admin
            from firebase_admin import credentials
            
            firebase_config = {
                "type": "service_account",
                "project_id": "alpaca-12fab",
                "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                "private_key": private_key.replace('\\n', '\n'),
                "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
            }
            
            # Check if any fields are None
            missing_fields = [k for k, v in firebase_config.items() if v is None]
            if missing_fields:
                print(f"❌ Missing Firebase config fields: {missing_fields}")
            else:
                print("✅ All Firebase config fields present")
                
                # Try to create credentials (don't initialize app)
                cred = credentials.Certificate(firebase_config)
                print("✅ Firebase credentials object created successfully")
                
        except Exception as e:
            print(f"❌ Firebase initialization test failed: {e}")
            
    else:
        print("❌ MISSING FIREBASE ENVIRONMENT VARIABLES")
        print("   Add the missing variables to Railway and redeploy")
    
    print("\n🎯 RECOMMENDED ACTIONS:")
    if not all_present:
        print("1. Add missing environment variables to Railway")
        print("2. Redeploy the application")
    else:
        print("1. Check private key format (ensure \\n characters)")
        print("2. Redeploy to test Firebase connection")
        print("3. Check deployment logs for Firebase messages")

if __name__ == "__main__":
    debug_firebase_env()