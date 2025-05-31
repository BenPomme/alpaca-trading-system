#!/usr/bin/env python3
"""
Verify Railway Firebase Connection and Live System Performance
"""

import subprocess
import json
import requests
from datetime import datetime
import sys

def check_railway_status():
    """Check Railway deployment status and logs"""
    print("🚀 RAILWAY DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    try:
        # Check Railway services
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway Status:")
            print(result.stdout)
        else:
            print(f"⚠️ Railway status error: {result.stderr}")
        
        # Try to get environment variables (may need service context)
        print("\n🔧 Checking Railway Environment Variables...")
        env_result = subprocess.run(['railway', 'env'], capture_output=True, text=True)
        if env_result.returncode == 0:
            firebase_vars = [line for line in env_result.stdout.split('\n') if 'FIREBASE' in line]
            print(f"🔥 Firebase variables found: {len(firebase_vars)}")
            for var in firebase_vars[:3]:  # Show first 3 for verification
                var_name = var.split('=')[0] if '=' in var else var
                print(f"   ✅ {var_name}")
        else:
            print(f"⚠️ Could not retrieve environment variables: {env_result.stderr}")
            
        # Get recent logs to check Firebase connection
        print("\n📋 Recent Railway Logs (checking for Firebase)...")
        logs_result = subprocess.run(['railway', 'logs', '--lines', '50'], capture_output=True, text=True)
        if logs_result.returncode == 0:
            firebase_mentions = [line for line in logs_result.stdout.split('\n') if 'Firebase' in line or '🔥' in line]
            print(f"🔥 Firebase-related log entries: {len(firebase_mentions)}")
            for mention in firebase_mentions[-5:]:  # Show last 5
                print(f"   📋 {mention}")
        else:
            print(f"⚠️ Could not retrieve logs: {logs_result.stderr}")
            
    except Exception as e:
        print(f"❌ Railway CLI Error: {e}")
        return False
    
    return True

def check_live_dashboard():
    """Check if live dashboard has real data"""
    print("\n📱 LIVE DASHBOARD DATA VERIFICATION")
    print("=" * 50)
    
    # Check GitHub Pages dashboard
    try:
        dashboard_url = "https://your-username.github.io/Alpaca/api/dashboard-data.json"  # Update with actual URL
        response = requests.get(dashboard_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard accessible")
            print(f"📊 Data source: {data.get('data_source', 'unknown')}")
            print(f"💰 Portfolio value: ${data.get('portfolio', {}).get('value', 0):,.2f}")
            print(f"📈 Active positions: {len(data.get('positions', []))}")
            print(f"🕐 Last updated: {data.get('generated_at', 'unknown')}")
            
            # Check for real vs mock data
            if data.get('data_source') == 'live':
                print("✅ Dashboard showing LIVE data")
            else:
                print("⚠️ Dashboard showing mock/cached data")
                
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Dashboard check error: {e}")

def check_firebase_project():
    """Verify Firebase project configuration"""
    print("\n🔥 FIREBASE PROJECT VERIFICATION")
    print("=" * 50)
    
    try:
        # Check if firebase.json exists and is configured
        with open('firebase.json', 'r') as f:
            firebase_config = json.load(f)
            
        print("✅ Firebase project configuration found")
        print(f"📊 Project: {firebase_config}")
        
        # Check firestore rules
        with open('firestore.rules', 'r') as f:
            rules = f.read()
            
        print("✅ Firestore rules configured")
        print(f"📋 Rules length: {len(rules)} characters")
        
    except Exception as e:
        print(f"⚠️ Firebase config check error: {e}")

def analyze_trading_performance():
    """Analyze current trading performance based on available data"""
    print("\n📊 LIVE TRADING PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    try:
        # Try to connect with live API (if credentials available)
        import alpaca_trade_api as tradeapi
        import os
        
        api_key = os.getenv('ALPACA_PAPER_API_KEY')
        secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
        
        if api_key and secret_key:
            api = tradeapi.REST(
                key_id=api_key,
                secret_key=secret_key,
                base_url='https://paper-api.alpaca.markets',
                api_version='v2'
            )
            
            # Get real account data
            account = api.get_account()
            positions = api.list_positions()
            
            print("✅ Connected to live Alpaca account")
            print(f"💰 Portfolio Value: ${float(account.portfolio_value):,.2f}")
            print(f"📊 Active Positions: {len(positions)}")
            print(f"📈 Unrealized P&L: ${sum(float(pos.unrealized_pl) for pos in positions):,.2f}")
            
            # Calculate win rate from current positions
            winning_positions = len([pos for pos in positions if float(pos.unrealized_pl) > 0])
            total_positions = len(positions)
            win_rate = (winning_positions / total_positions * 100) if total_positions > 0 else 0
            
            print(f"🎯 Current Win Rate: {win_rate:.1f}% ({winning_positions}/{total_positions})")
            
            # Check if this matches our analysis
            if win_rate < 40:
                print("🚨 CRITICAL: Win rate below target (should be 45-60%)")
            elif win_rate >= 45:
                print("✅ Win rate within target range")
            else:
                print("⚠️ Win rate improving but still below target")
                
        else:
            print("⚠️ Alpaca API credentials not available locally")
            print("   (This is normal - credentials should be on Railway only)")
            
    except Exception as e:
        print(f"⚠️ Live performance check error: {e}")

def main():
    """Run comprehensive Railway Firebase verification"""
    print("🔍 COMPREHENSIVE RAILWAY FIREBASE VERIFICATION")
    print("=" * 60)
    print(f"🕐 Time: {datetime.now().isoformat()}")
    print()
    
    # Run all checks
    railway_ok = check_railway_status()
    check_live_dashboard()
    check_firebase_project()
    analyze_trading_performance()
    
    print("\n💡 SUMMARY & NEXT STEPS")
    print("=" * 50)
    
    if railway_ok:
        print("✅ Railway CLI accessible")
        print("🔍 To verify Firebase on Railway:")
        print("   1. Check Railway dashboard environment variables")
        print("   2. Monitor Railway logs for Firebase connection messages")
        print("   3. Look for '🔥 Firebase Connected' in deployment logs")
        print("   4. Verify ML learning persistence across restarts")
    else:
        print("❌ Railway CLI issues detected")
        print("🔧 Fix Railway connection first")
    
    print("\n📋 VERIFICATION CHECKLIST:")
    print("   [ ] Firebase variables set in Railway dashboard")
    print("   [ ] Railway logs show Firebase connection")
    print("   [ ] Dashboard displays live portfolio data")
    print("   [ ] ML learning persists across deployments")
    print("   [ ] Trading performance metrics accurate")

if __name__ == "__main__":
    main()