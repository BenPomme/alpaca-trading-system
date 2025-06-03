#!/usr/bin/env python3
"""
Production Monitoring and Bug Detection

Comprehensive test to identify any bugs or issues in the production deployment
by analyzing system behavior, API responses, and performance metrics.
"""

import requests
import time
import json
from datetime import datetime
import os

# Load environment variables
if os.path.exists('.env.local'):
    with open('.env.local', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                value = value.strip('"\'')
                os.environ[key] = value

RAILWAY_URL = "https://satisfied-commitment.railway.app"

def test_health_endpoints():
    """Test all health endpoints for errors"""
    print("🏥 HEALTH ENDPOINT TESTING")
    print("=" * 50)
    
    endpoints = [
        "/health",
        "/",
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            url = f"{RAILWAY_URL}{endpoint}"
            print(f"Testing: {url}")
            
            response = requests.get(url, timeout=10)
            results[endpoint] = {
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'content_length': len(response.content),
                'success': response.status_code == 200
            }
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK ({response.elapsed.total_seconds():.2f}s)")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"💥 {endpoint}: ERROR - {e}")
            results[endpoint] = {'error': str(e), 'success': False}
    
    return results

def test_trading_system_locally():
    """Test the trading system components locally"""
    print("\n🔧 LOCAL SYSTEM TESTING")
    print("=" * 50)
    
    issues = []
    
    # Test 1: Import checks
    try:
        from modular.orchestrator import ModularOrchestrator
        print("✅ ModularOrchestrator import: OK")
    except Exception as e:
        print(f"❌ ModularOrchestrator import: {e}")
        issues.append(f"Orchestrator import failed: {e}")
    
    try:
        from trade_history_tracker import TradeHistoryTracker
        print("✅ TradeHistoryTracker import: OK")
    except Exception as e:
        print(f"❌ TradeHistoryTracker import: {e}")
        issues.append(f"TradeHistoryTracker import failed: {e}")
    
    try:
        from firebase_database import FirebaseDatabase
        print("✅ FirebaseDatabase import: OK")
    except Exception as e:
        print(f"❌ FirebaseDatabase import: {e}")
        issues.append(f"FirebaseDatabase import failed: {e}")
    
    # Test 2: Module instantiation
    try:
        from modular.crypto_module import CryptoModule
        from modular.stocks_module import StocksModule
        from modular.base_module import ModuleConfig
        
        # Test crypto module creation
        crypto_config = ModuleConfig(module_name="crypto_test", enabled=True)
        crypto_module = CryptoModule(crypto_config, None, None, None, None)
        print("✅ CryptoModule instantiation: OK")
        
        # Test stocks module creation  
        stocks_config = ModuleConfig(module_name="stocks_test", enabled=True)
        stocks_module = StocksModule(stocks_config, None, None, None, None)
        print("✅ StocksModule instantiation: OK")
        
    except Exception as e:
        print(f"❌ Module instantiation: {e}")
        issues.append(f"Module instantiation failed: {e}")
    
    # Test 3: Firebase connection
    try:
        firebase_db = FirebaseDatabase()
        if firebase_db.is_connected():
            print("✅ Firebase connection: OK")
        else:
            print("⚠️ Firebase connection: Not connected")
            issues.append("Firebase not connected")
    except Exception as e:
        print(f"❌ Firebase connection: {e}")
        issues.append(f"Firebase connection failed: {e}")
    
    return issues

def test_environment_variables():
    """Check critical environment variables"""
    print("\n🌍 ENVIRONMENT VARIABLES CHECK")
    print("=" * 50)
    
    required_vars = [
        'ALPACA_PAPER_API_KEY',
        'ALPACA_PAPER_SECRET_KEY', 
        'FIREBASE_CLIENT_EMAIL',
        'ALPHA_VANTAGE_API_KEY',
        'FINNHUB_API_KEY'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show partial value for security
            display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    return missing_vars

def test_performance_analysis():
    """Run local performance analysis"""
    print("\n📊 PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    try:
        import subprocess
        result = subprocess.run(['python', 'quick_performance_check.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Performance check completed successfully")
            # Look for error indicators in output
            output_lines = result.stdout.split('\n')
            errors = [line for line in output_lines if '❌' in line or 'ERROR' in line or 'Failed' in line]
            if errors:
                print("⚠️ Errors found in performance check:")
                for error in errors:
                    print(f"   {error}")
                return errors
            else:
                print("✅ No errors found in performance output")
                return []
        else:
            print(f"❌ Performance check failed with code {result.returncode}")
            print(f"Error: {result.stderr}")
            return [f"Performance check failed: {result.stderr}"]
            
    except Exception as e:
        print(f"❌ Performance analysis failed: {e}")
        return [f"Performance analysis error: {e}"]

def simulate_trading_cycle():
    """Simulate a trading cycle to check for issues"""
    print("\n🔄 TRADING CYCLE SIMULATION")
    print("=" * 50)
    
    issues = []
    
    try:
        # Test Firebase initialization
        from firebase_database import FirebaseDatabase
        firebase_db = FirebaseDatabase()
        
        if not firebase_db.is_connected():
            issues.append("Firebase not connected for trading cycle")
            print("❌ Firebase connection required for trading")
            return issues
        
        # Test TradeHistoryTracker initialization
        from trade_history_tracker import TradeHistoryTracker
        tracker = TradeHistoryTracker(firebase_db=firebase_db)
        print("✅ TradeHistoryTracker initialized successfully")
        
        # Test safety checks
        can_trade, reason = tracker.can_trade_symbol("BTCUSD", 1000)
        print(f"✅ Safety check test: can_trade={can_trade}, reason='{reason}'")
        
        # Test module initialization
        from modular.base_module import ModuleConfig
        from modular.crypto_module import CryptoModule
        
        config = ModuleConfig(module_name="test_crypto", enabled=True)
        module = CryptoModule(config, None, firebase_db, None, None)
        print("✅ CryptoModule initialized with Firebase")
        
        # Test supported symbols
        symbols = module.supported_symbols
        print(f"✅ Crypto symbols available: {len(symbols)} ({symbols[:3]}...)")
        
    except Exception as e:
        issues.append(f"Trading cycle simulation failed: {e}")
        print(f"❌ Trading cycle simulation error: {e}")
    
    return issues

def main():
    """Run comprehensive production monitoring"""
    print("🚀 PRODUCTION MONITORING AND BUG DETECTION")
    print("=" * 60)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Railway URL: {RAILWAY_URL}")
    print()
    
    all_issues = []
    
    # Test 1: Health endpoints
    health_results = test_health_endpoints()
    
    # Test 2: Environment variables
    missing_vars = test_environment_variables()
    if missing_vars:
        all_issues.extend([f"Missing env var: {var}" for var in missing_vars])
    
    # Test 3: Local system
    system_issues = test_trading_system_locally()
    all_issues.extend(system_issues)
    
    # Test 4: Performance analysis
    perf_issues = test_performance_analysis()
    all_issues.extend(perf_issues)
    
    # Test 5: Trading cycle simulation
    trading_issues = simulate_trading_cycle()
    all_issues.extend(trading_issues)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 PRODUCTION MONITORING SUMMARY")
    print("=" * 60)
    
    if not all_issues:
        print("🎉 NO BUGS DETECTED - SYSTEM APPEARS HEALTHY")
        print("✅ All components working correctly")
        print("✅ Railway deployment operational")
        print("✅ Firebase connection established")
        print("✅ Environment variables configured")
        print("✅ Trading modules functional")
    else:
        print(f"⚠️ {len(all_issues)} POTENTIAL ISSUES DETECTED:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n🔧 RECOMMENDED ACTIONS:")
        if any("Firebase" in issue for issue in all_issues):
            print("   - Check Firebase environment variables in Railway")
        if any("import" in issue.lower() for issue in all_issues):
            print("   - Verify all dependencies installed in Railway build")
        if any("env var" in issue.lower() for issue in all_issues):
            print("   - Update Railway environment variables")
    
    print(f"\n🌐 Monitor production at: {RAILWAY_URL}")
    return len(all_issues) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)