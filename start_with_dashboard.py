#!/usr/bin/env python3
"""
Unified Trading System with Web Dashboard
Runs both the trading bot and web dashboard simultaneously
"""

import os
import threading
import time
from start_ultra_simple import UltraSimpleTrader
from dashboard import app

def run_trading_system():
    """Run the trading system in a separate thread"""
    print("🤖 Starting trading system...")
    try:
        trader = UltraSimpleTrader()
        trader.run_continuous()
    except Exception as e:
        print(f"❌ Trading system error: {e}")
        # Don't crash the whole app if trading fails

def run_dashboard():
    """Run the web dashboard"""
    print("🌐 Starting web dashboard...")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("🚀 UNIFIED TRADING SYSTEM WITH DASHBOARD")
    print("=" * 50)
    print(f"🕐 Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("☁️ Platform: Railway Cloud")
    print("💰 Mode: Paper Trading")
    print("🌐 Dashboard: Available at http://localhost:5000")
    print()
    
    # Start trading system in background thread
    trading_thread = threading.Thread(target=run_trading_system, daemon=True)
    trading_thread.start()
    
    # Give trading system time to initialize
    time.sleep(5)
    
    # Start web dashboard (main thread)
    run_dashboard()