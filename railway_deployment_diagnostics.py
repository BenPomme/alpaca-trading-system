#!/usr/bin/env python3
"""
Railway Deployment Diagnostics

Check the actual status of the Railway deployment and diagnose why
stocks and options modules are not trading.
"""

import requests
import json
import time
from datetime import datetime

def check_railway_endpoints():
    """Check all possible Railway endpoints to understand deployment status"""
    
    base_url = "https://satisfied-commitment.railway.app"
    
    endpoints_to_test = [
        "/",
        "/health", 
        "/status",
        "/api/health",
        "/trading",
        "/trading/status",
        "/modules",
        "/modules/stocks",
        "/modules/options", 
        "/modules/crypto",
        "/orchestrator",
        "/orchestrator/status",
        "/intelligence",
        "/intelligence/status",
        "/positions",
        "/orders",
        "/dashboard",
        "/metrics",
        "/logs"
    ]
    
    print("🔍 RAILWAY DEPLOYMENT DIAGNOSTICS")
    print("=" * 60)
    print(f"📡 Base URL: {base_url}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        try:
            print(f"Testing: {endpoint:20} ", end="")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print("✅ 200 OK", end="")
                try:
                    # Try to parse as JSON
                    data = response.json()
                    print(f" (JSON: {len(str(data))} chars)")
                    results[endpoint] = {"status": 200, "type": "json", "data": data}
                except:
                    # Plain text response
                    text = response.text.strip()
                    print(f" (Text: {len(text)} chars)")
                    results[endpoint] = {"status": 200, "type": "text", "data": text[:200]}
                    
            else:
                print(f"❌ {response.status_code}")
                results[endpoint] = {"status": response.status_code, "type": "error", "data": None}
                
        except requests.exceptions.ConnectTimeout:
            print("⏳ TIMEOUT")
            results[endpoint] = {"status": "timeout", "type": "error", "data": None}
        except requests.exceptions.ConnectionError:
            print("🔌 CONNECTION ERROR") 
            results[endpoint] = {"status": "connection_error", "type": "error", "data": None}
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results[endpoint] = {"status": "exception", "type": "error", "data": str(e)}
    
    return results

def analyze_results(results):
    """Analyze the endpoint test results to diagnose the issue"""
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC ANALYSIS")
    print("=" * 60)
    
    working_endpoints = [ep for ep, result in results.items() if result["status"] == 200]
    error_endpoints = [ep for ep, result in results.items() if result["status"] != 200]
    
    print(f"✅ Working endpoints: {len(working_endpoints)}")
    print(f"❌ Error endpoints: {len(error_endpoints)}")
    
    if working_endpoints:
        print(f"\n🟢 WORKING ENDPOINTS:")
        for endpoint in working_endpoints:
            result = results[endpoint]
            print(f"   {endpoint}: {result['type']}")
            if result['type'] == 'json' and isinstance(result['data'], dict):
                if 'status' in result['data']:
                    print(f"      Status: {result['data']['status']}")
                if 'modules' in result['data']:
                    print(f"      Modules: {result['data']['modules']}")
                if 'trading' in result['data']:
                    print(f"      Trading: {result['data']['trading']}")
    
    # Diagnose the issue
    print(f"\n🔍 DIAGNOSIS:")
    
    if "/" in working_endpoints and results["/"]["type"] == "text":
        root_response = results["/"]["data"]
        if "Railway API" in root_response:
            print("❌ ISSUE: Railway is serving the default Railway homepage, not our app")
            print("🔧 SOLUTION: The deployment is not running our Python application")
            print("   - Check if the build failed")
            print("   - Check if the start command is correct")
            print("   - Check if the port configuration is correct")
            
    elif "/health" in working_endpoints and results["/health"]["status"] == 200:
        print("✅ POSITIVE: Health endpoint is responding")
        if "/status" not in working_endpoints:
            print("⚠️ WARNING: No status endpoint found - application may be partially running")
            
    else:
        print("❌ ISSUE: No clear application endpoints found")
        print("🔧 SOLUTION: Application likely not starting correctly")
        
    # Check for trading-specific endpoints
    trading_endpoints = [ep for ep in working_endpoints if 'trading' in ep or 'modules' in ep]
    if not trading_endpoints:
        print("❌ ISSUE: No trading-related endpoints found")
        print("🔧 SOLUTION: Trading modules are not initialized or accessible")
        
    print(f"\n📋 NEXT STEPS:")
    print("1. Check Railway build logs: `railway logs`") 
    print("2. Verify environment variables in Railway dashboard")
    print("3. Check if Python application is starting correctly")
    print("4. Verify the correct entry point (Procfile)")

def check_market_status():
    """Check if the market should currently be open"""
    try:
        import pytz
        et = pytz.timezone('US/Eastern')
        now_et = datetime.now(et)
        is_weekday = now_et.weekday() < 5
        is_trading_hours = 9 <= now_et.hour < 16
        
        print(f"\n🏛️ MARKET STATUS:")
        print(f"Current time (ET): {now_et.strftime('%Y-%m-%d %H:%M %Z')}")
        print(f"Is weekday: {is_weekday}")
        print(f"Is trading hours: {is_trading_hours}")
        print(f"Should be trading: {is_weekday and is_trading_hours}")
        
        if is_weekday and is_trading_hours:
            print("📈 Market is OPEN - stocks and options should be trading")
        else:
            print("📴 Market is CLOSED - only crypto should be trading (24/7)")
            
    except Exception as e:
        print(f"❌ Market status check failed: {e}")

if __name__ == "__main__":
    # Run diagnostics
    results = check_railway_endpoints()
    
    # Analyze results
    analyze_results(results)
    
    # Check market status
    check_market_status()
    
    print("\n" + "=" * 60)
    print("✅ Diagnostics complete")