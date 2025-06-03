#!/usr/bin/env python3
"""
Find Railway App URL

Attempt to find the active Railway deployment URL by testing common patterns.
"""

import requests
import time

def test_railway_urls():
    """Test common Railway URL patterns"""
    
    # Common Railway URL patterns
    base_patterns = [
        "satisfied-commitment",
        "alpaca-trading-system", 
        "alpaca-trading",
        "trading-system",
    ]
    
    # Railway domain suffixes
    suffixes = [
        ".railway.app",
        ".up.railway.app", 
    ]
    
    # Test all combinations
    for pattern in base_patterns:
        for suffix in suffixes:
            url = f"https://{pattern}{suffix}"
            try:
                print(f"Testing: {url}")
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ FOUND: {url}")
                    print(f"Response: {response.json()}")
                    return url
                else:
                    print(f"❌ {response.status_code}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(0.5)  # Rate limiting
    
    print("❌ No active Railway URL found")
    return None

if __name__ == "__main__":
    active_url = test_railway_urls()
    if active_url:
        print(f"\n🎯 Use this URL in monitor_live_performance.py:")
        print(f'"{active_url}"')