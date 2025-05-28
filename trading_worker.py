#!/usr/bin/env python3
"""
Trading Bot Worker Service
Dedicated service for trading logic - runs continuously
Communicates with dashboard via shared JSON files
"""

import os
import json
import time
from datetime import datetime
from start_ultra_simple import UltraSimpleTrader

class TradingWorker:
    """Enhanced trading worker with status updates"""
    
    def __init__(self):
        self.trader = UltraSimpleTrader()
        self.status_file = 'data/worker_status.json'
        self.cycle_count = 0
        self.start_time = datetime.now()
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Initialize status
        self.update_status("Initialized - Ready to Trade")
        print("✅ Trading worker initialized")
    
    def update_status(self, status, cycle_data=None):
        """Update status file for dashboard communication"""
        try:
            status_data = {
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'cycle_count': self.cycle_count,
                'start_time': self.start_time.isoformat(),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
                'last_cycle': cycle_data,
                'worker_type': 'trading_bot',
                'version': '2.0.0'
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Status update error: {e}")
    
    def enhanced_run_cycle(self):
        """Run trading cycle with enhanced logging"""
        try:
            self.update_status("Running Trading Cycle...")
            print(f"\n🔄 WORKER CYCLE #{self.cycle_count + 1}")
            print("-" * 50)
            
            # Run the actual trading cycle
            cycle_data = self.trader.run_cycle()
            
            # Enhanced cycle data
            enhanced_cycle = {
                **cycle_data,
                'cycle_number': self.cycle_count + 1,
                'worker_timestamp': datetime.now().isoformat(),
                'execution_time': 'N/A'  # Could add timing here
            }
            
            self.cycle_count += 1
            self.update_status("Active - Monitoring Markets", enhanced_cycle)
            
            print(f"✅ Worker cycle #{self.cycle_count} completed")
            return enhanced_cycle
            
        except Exception as e:
            error_msg = f"Trading cycle error: {e}"
            self.update_status(f"Error: {error_msg}")
            print(f"❌ {error_msg}")
            return None
    
    def run_continuous_worker(self):
        """Main worker loop - dedicated trading service"""
        print("🤖 TRADING WORKER SERVICE")
        print("=" * 40)
        print(f"🕐 Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("☁️ Platform: Railway Cloud (Worker Service)")
        print("💰 Mode: Paper Trading")
        print("🔄 Type: Continuous Background Trading")
        print("📊 Communication: JSON status files")
        print()
        
        # Verify account access
        if not self.trader.check_account():
            self.update_status("Account verification failed")
            return
        
        print("🔄 Starting continuous worker monitoring...")
        print("   Worker will run indefinitely")
        print()
        
        try:
            while True:
                # Run enhanced trading cycle
                self.enhanced_run_cycle()
                
                # Wait between cycles (2 minutes)
                wait_time = 120
                self.update_status(f"Waiting {wait_time}s for next cycle...")
                print(f"⏳ Worker sleeping for {wait_time} seconds...")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            print("\n🛑 Worker stopped manually")
            self.update_status("Worker stopped manually")
        except Exception as e:
            error_msg = f"Worker system error: {e}"
            print(f"\n❌ {error_msg}")
            self.update_status(error_msg)
            print("🔄 Worker restarting in 60 seconds...")
            time.sleep(60)
            # Recursive restart
            self.run_continuous_worker()

def main():
    """Worker entry point"""
    try:
        worker = TradingWorker()
        worker.run_continuous_worker()
    except Exception as e:
        print(f"❌ Worker startup failed: {e}")
        # Create error status file
        os.makedirs('data', exist_ok=True)
        with open('data/worker_status.json', 'w') as f:
            json.dump({
                'status': f'Startup failed: {e}',
                'timestamp': datetime.now().isoformat(),
                'worker_type': 'trading_bot',
                'error': True
            }, f, indent=2)

if __name__ == "__main__":
    main()