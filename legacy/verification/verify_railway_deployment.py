#!/usr/bin/env python3
"""
Railway Deployment Verification Script

Verifies that the Market Intelligence Module is properly deployed and functioning
on Railway with all debug endpoints accessible.
"""

import requests
import json
import time
from datetime import datetime

# Railway deployment URL (update with your actual URL)
RAILWAY_BASE_URL = "https://your-app.railway.app"  # Update this with your actual Railway URL

def test_deployment_endpoints():
    """Test all deployment endpoints"""
    print("🚀 VERIFYING RAILWAY DEPLOYMENT")
    print("=" * 60)
    
    endpoints = [
        ("/health", "Basic Health Check"),
        ("/status", "System Status"),
        ("/metrics", "System Metrics"),
        ("/intelligence", "Market Intelligence Status"),
        ("/intelligence/debug", "Intelligence Debug Info"),
        ("/intelligence/signals", "Current Market Signals")
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        try:
            print(f"🔍 Testing {description}...")
            url = f"{RAILWAY_BASE_URL}{endpoint}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {description}: SUCCESS")
                try:
                    data = response.json()
                    results[endpoint] = {
                        'status': 'success',
                        'data': data,
                        'response_time': response.elapsed.total_seconds()
                    }
                    
                    # Show key information
                    if endpoint == "/health":
                        print(f"   Status: {data.get('status', 'unknown')}")
                        print(f"   Uptime: {data.get('uptime_seconds', 0)} seconds")
                    elif endpoint == "/intelligence":
                        print(f"   AI Model: {data.get('ai_model', 'unknown')}")
                        print(f"   API Requests: {data.get('api_requests_made', 0)}")
                        print(f"   Success Rate: {data.get('api_success_rate', 0):.1%}")
                    elif endpoint == "/intelligence/debug":
                        print(f"   Health Status: {data.get('health_status', 'unknown')}")
                        print(f"   Current Signals: {data.get('signals_summary', {}).get('total_signals', 0)}")
                    elif endpoint == "/intelligence/signals":
                        print(f"   Signal Count: {data.get('signals_count', 0)}")
                        
                except json.JSONDecodeError:
                    print(f"   Response: {response.text[:100]}...")
                    results[endpoint] = {
                        'status': 'success_non_json',
                        'response_time': response.elapsed.total_seconds()
                    }
            else:
                print(f"❌ {description}: FAILED (HTTP {response.status_code})")
                results[endpoint] = {
                    'status': 'failed',
                    'status_code': response.status_code,
                    'error': response.text[:200]
                }
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: CONNECTION ERROR")
            print(f"   Error: {str(e)}")
            results[endpoint] = {
                'status': 'connection_error',
                'error': str(e)
            }
        except Exception as e:
            print(f"❌ {description}: UNEXPECTED ERROR")
            print(f"   Error: {str(e)}")
            results[endpoint] = {
                'status': 'unexpected_error',
                'error': str(e)
            }
        
        print()
    
    # Generate summary
    print("📊 DEPLOYMENT VERIFICATION SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results.values() if r['status'] in ['success', 'success_non_json'])
    total = len(results)
    
    print(f"✅ Successful Endpoints: {successful}/{total}")
    print(f"🎯 Success Rate: {successful/total:.1%}")
    
    if successful == total:
        print("🎉 ALL ENDPOINTS WORKING - DEPLOYMENT SUCCESSFUL!")
    elif successful >= total * 0.8:
        print("✅ MOSTLY WORKING - Minor issues to investigate")
    else:
        print("❌ SIGNIFICANT ISSUES - Deployment needs attention")
    
    print()
    print("🔧 NEXT STEPS:")
    if successful == total:
        print("   1. Monitor production performance")
        print("   2. Verify Market Intelligence analysis quality") 
        print("   3. Check ML learning progression")
    else:
        print("   1. Check Railway environment variables")
        print("   2. Verify OpenAI API key is properly set")
        print("   3. Review Railway deployment logs")
    
    return results

def test_market_intelligence_functionality():
    """Test Market Intelligence specific functionality"""
    print("🧠 TESTING MARKET INTELLIGENCE FUNCTIONALITY")
    print("=" * 60)
    
    try:
        # Test intelligence status
        url = f"{RAILWAY_BASE_URL}/intelligence"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Market Intelligence Module Active")
            print(f"   Model: {data.get('ai_model', 'unknown')}")
            print(f"   Health: {data.get('health_status', 'unknown')}")
            print(f"   Uptime: {data.get('uptime_hours', 0):.1f} hours")
            print(f"   API Success Rate: {data.get('api_success_rate', 0):.1%}")
            
            # Test debug info
            debug_url = f"{RAILWAY_BASE_URL}/intelligence/debug"
            debug_response = requests.get(debug_url, timeout=10)
            
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                print("✅ Debug Information Available")
                print(f"   Performance Metrics: {len(debug_data.get('performance_metrics', {}))}")
                print(f"   Configuration: {len(debug_data.get('configuration', {}))}")
                
            return True
        else:
            print(f"❌ Market Intelligence Not Accessible (HTTP {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Market Intelligence Test Failed: {e}")
        return False

if __name__ == "__main__":
    print(f"🕐 Verification Time: {datetime.now()}")
    print(f"🌐 Target URL: {RAILWAY_BASE_URL}")
    print()
    
    # Wait a moment for deployment to stabilize
    print("⏳ Waiting 10 seconds for deployment to stabilize...")
    time.sleep(10)
    
    # Test all endpoints
    results = test_deployment_endpoints()
    
    # Test Market Intelligence specifically
    intelligence_working = test_market_intelligence_functionality()
    
    print()
    print("🎯 FINAL VERIFICATION STATUS")
    print("=" * 60)
    
    if all(r['status'] in ['success', 'success_non_json'] for r in results.values()) and intelligence_working:
        print("🎉 DEPLOYMENT FULLY VERIFIED AND OPERATIONAL!")
        print("🧠 Market Intelligence Module: ACTIVE")
        print("📊 All Debug Endpoints: ACCESSIBLE") 
        print("🚀 Railway Deployment: SUCCESS")
    else:
        print("⚠️ DEPLOYMENT PARTIALLY WORKING")
        print("🔧 Some issues detected - check logs above")