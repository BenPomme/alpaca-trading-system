#!/usr/bin/env python3
"""
Automatic Dashboard Updater
Runs continuously and updates dashboard data automatically
"""

import time
import subprocess
import sys
import os
from datetime import datetime, time as dt_time
import schedule

class DashboardAutoUpdater:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.running = True
        
    def update_dashboard(self):
        """Run the dashboard update"""
        try:
            print(f"🔄 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Starting dashboard update...")
            
            # Change to script directory
            os.chdir(self.script_dir)
            
            # Run the manual update script
            result = subprocess.run([sys.executable, "manual_update.py"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {datetime.now().strftime('%H:%M:%S')} - Dashboard updated successfully!")
                if "No changes to dashboard data" in result.stdout:
                    print("ℹ️ No new data changes")
                else:
                    print("📊 New data pushed to GitHub Pages")
            else:
                print(f"❌ {datetime.now().strftime('%H:%M:%S')} - Update failed:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ {datetime.now().strftime('%H:%M:%S')} - Error: {e}")
    
    def is_market_hours(self):
        """Check if it's during market hours (9:30 AM - 4:00 PM ET, Mon-Fri)"""
        now = datetime.now()
        
        # Check if it's a weekday (Monday = 0, Sunday = 6)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
            
        # Check if it's during market hours (9:30 AM - 4:00 PM)
        market_open = dt_time(9, 30)
        market_close = dt_time(16, 0)
        current_time = now.time()
        
        return market_open <= current_time <= market_close
    
    def start(self):
        """Start the automatic updater"""
        print("🚀 Dashboard Auto-Updater Starting...")
        print("📊 Market Hours: Every 10 minutes (9:30 AM - 4:00 PM, Mon-Fri)")
        print("🌙 After Hours: Every 30 minutes (24/7 crypto tracking)")
        print("⏹️ Press Ctrl+C to stop")
        print("-" * 50)
        
        # Schedule market hours updates (every 10 minutes)
        schedule.every(10).minutes.do(self.market_hours_update)
        
        # Schedule after-hours updates (every 30 minutes)
        schedule.every(30).minutes.do(self.after_hours_update)
        
        # Run an initial update
        self.update_dashboard()
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            print("\n⏹️ Auto-updater stopped by user")
        except Exception as e:
            print(f"\n❌ Auto-updater error: {e}")
            
    def market_hours_update(self):
        """Update during market hours only"""
        if self.is_market_hours():
            print("📈 Market hours update triggered")
            self.update_dashboard()
        
    def after_hours_update(self):
        """Update during after hours (for crypto)"""
        if not self.is_market_hours():
            print("🌙 After-hours update triggered (crypto)")
            self.update_dashboard()

def main():
    """Main function"""
    print("🎯 Alpaca Trading System - Auto Dashboard Updater")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("manual_update.py"):
        print("❌ Error: manual_update.py not found in current directory")
        print("Please run this script from the Alpaca trading system directory")
        sys.exit(1)
    
    # Check if we can access the API
    if not os.path.exists(".env"):
        print("⚠️ Warning: .env file not found")
        print("Make sure your Alpaca API keys are configured")
    
    # Start the auto-updater
    updater = DashboardAutoUpdater()
    updater.start()

if __name__ == "__main__":
    main()