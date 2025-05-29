#!/usr/bin/env python3
"""
Railway Deployment Verification Script
Forces intelligent exit system to be active
"""

import os
import sys
from datetime import datetime

def main():
    print("🚀 RAILWAY DEPLOYMENT VERIFICATION")
    print("=" * 50)
    print(f"⏰ Deployment Time: {datetime.now()}")
    print(f"🐍 Python Version: {sys.version}")
    print("")
    
    # Check if intelligent exit manager file exists
    try:
        import intelligent_exit_manager
        print("✅ intelligent_exit_manager.py: FOUND")
    except ImportError as e:
        print(f"❌ intelligent_exit_manager.py: MISSING - {e}")
        return False
    
    # Check if phase3_trader has the updates
    try:
        from phase3_trader import Phase3Trader
        print("✅ phase3_trader.py: FOUND")
        
        # Check if IntelligentExitManager is imported
        import inspect
        source = inspect.getsource(Phase3Trader.__init__)
        if "intelligent_exit_manager" in source.lower():
            print("✅ IntelligentExitManager integration: FOUND")
        else:
            print("❌ IntelligentExitManager integration: MISSING")
            return False
            
    except Exception as e:
        print(f"❌ phase3_trader.py: ERROR - {e}")
        return False
    
    print("")
    print("🎯 STARTING INTELLIGENT TRADING SYSTEM...")
    
    # Import and run the actual system
    try:
        from start_phase3 import main as start_trading
        start_trading()
    except Exception as e:
        print(f"❌ SYSTEM START ERROR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("❌ DEPLOYMENT VERIFICATION FAILED")
        sys.exit(1)
    else:
        print("✅ DEPLOYMENT VERIFICATION PASSED")