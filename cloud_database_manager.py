#!/usr/bin/env python3
"""
Cloud-Aware Database Manager for Trading System
Integrates local SQLite with cloud JSON storage for 24/7 persistence
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database_manager import TradingDatabase
from cloud_database import CloudDatabase

class CloudTradingDatabase(TradingDatabase):
    """Enhanced database manager with cloud synchronization"""
    
    def __init__(self, db_path='data/trading_system.db', auto_sync=True):
        self.cloud_db = CloudDatabase()
        self.auto_sync = auto_sync
        self.sync_interval = 300  # Sync every 5 minutes
        self.last_sync = None
        
        # Try to sync from cloud first (for Railway/GitHub Actions)
        if not os.path.exists(db_path):
            print("🔄 No local database found, attempting cloud sync...")
            self.sync_from_cloud()
        
        # Initialize parent database
        super().__init__(db_path)
        
        print("✅ Cloud-aware database initialized")
    
    def sync_from_cloud(self):
        """Sync data from cloud to local database"""
        try:
            print("📥 Syncing trading data from cloud...")
            
            # Import cloud data to local database
            if self.cloud_db.import_cloud_to_local_db():
                print("✅ Successfully synced from cloud")
                self.last_sync = datetime.now()
                return True
            else:
                print("⚠️ No cloud data available")
                return False
                
        except Exception as e:
            print(f"❌ Error syncing from cloud: {e}")
            return False
    
    def sync_to_cloud(self):
        """Sync local database to cloud storage"""
        try:
            print("📤 Syncing trading data to cloud...")
            
            # Export local database and sync to GitHub
            if self.cloud_db.full_sync_cycle():
                print("✅ Successfully synced to cloud")
                self.last_sync = datetime.now()
                return True
            else:
                print("❌ Cloud sync failed")
                return False
                
        except Exception as e:
            print(f"❌ Error syncing to cloud: {e}")
            return False
    
    def should_auto_sync(self):
        """Check if automatic sync should be performed"""
        if not self.auto_sync:
            return False
            
        if self.last_sync is None:
            return True
            
        time_since_sync = (datetime.now() - self.last_sync).total_seconds()
        return time_since_sync >= self.sync_interval
    
    def store_market_quote(self, symbol, bid_price, ask_price, timestamp=None):
        """Store market quote with optional cloud sync"""
        # Store in local database
        result = super().store_market_quote(symbol, bid_price, ask_price, timestamp)
        
        # Auto-sync to cloud if needed
        if self.should_auto_sync():
            self.sync_to_cloud()
        
        return result
    
    def store_trading_cycle(self, symbol, intelligence_analysis, strategy_decision, 
                          confidence_score, executed_trade=None, timestamp=None):
        """Store trading cycle with optional cloud sync"""
        # Store in local database
        result = super().store_trading_cycle(symbol, intelligence_analysis, 
                                           strategy_decision, confidence_score, 
                                           executed_trade, timestamp)
        
        # Auto-sync to cloud if needed
        if self.should_auto_sync():
            self.sync_to_cloud()
        
        return result
    
    def store_trade(self, symbol, side, quantity, price, order_id=None, 
                   strategy=None, profit_loss=None, timestamp=None):
        """Store trade with optional cloud sync"""
        # Store in local database
        result = super().store_trade(symbol, side, quantity, price, order_id, 
                                   strategy, profit_loss, timestamp)
        
        # Auto-sync to cloud if needed
        if self.should_auto_sync():
            self.sync_to_cloud()
        
        return result
    
    def get_trading_history_for_dashboard(self):
        """Get comprehensive trading history for dashboard"""
        try:
            # First try to get from local database
            if os.path.exists(self.db_path):
                return self._get_local_trading_history()
            
            # Fallback to cloud data
            return self._get_cloud_trading_history()
            
        except Exception as e:
            print(f"❌ Error getting trading history: {e}")
            return {}
    
    def _get_local_trading_history(self):
        """Get trading history from local SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        history = {}
        
        try:
            # Get recent trades
            cursor.execute("""
                SELECT * FROM virtual_trades 
                ORDER BY timestamp DESC 
                LIMIT 100
            """)
            columns = [description[0] for description in cursor.description]
            trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
            history['trades'] = trades
            
            # Get trading cycles
            cursor.execute("""
                SELECT * FROM trading_cycles 
                ORDER BY timestamp DESC 
                LIMIT 50
            """)
            columns = [description[0] for description in cursor.description]
            cycles = [dict(zip(columns, row)) for row in cursor.fetchall()]
            history['cycles'] = cycles
            
            print(f"📊 Retrieved {len(trades)} trades and {len(cycles)} cycles from local DB")
            
        except Exception as e:
            print(f"❌ Error reading local database: {e}")
        
        conn.close()
        return history
    
    def _get_cloud_trading_history(self):
        """Get trading history from cloud JSON data"""
        try:
            cloud_data = self.cloud_db.get_cloud_data_for_api()
            
            if not cloud_data or 'tables' not in cloud_data:
                return {}
            
            history = {}
            tables = cloud_data['tables']
            
            # Extract trades
            if 'virtual_trades' in tables:
                trade_table = tables['virtual_trades']
                columns = trade_table['columns']
                rows = trade_table['rows']
                history['trades'] = [dict(zip(columns, row)) for row in rows]
            
            # Extract cycles
            if 'trading_cycles' in tables:
                cycle_table = tables['trading_cycles']
                columns = cycle_table['columns'] 
                rows = cycle_table['rows']
                history['cycles'] = [dict(zip(columns, row)) for row in rows]
            
            trades_count = len(history.get('trades', []))
            cycles_count = len(history.get('cycles', []))
            print(f"📊 Retrieved {trades_count} trades and {cycles_count} cycles from cloud data")
            
            return history
            
        except Exception as e:
            print(f"❌ Error reading cloud data: {e}")
            return {}
    
    def manual_cloud_sync(self):
        """Manually trigger cloud synchronization"""
        print("🔄 Manual cloud synchronization...")
        
        # Export current data to cloud
        if self.sync_to_cloud():
            print("✅ Manual sync completed successfully")
            return True
        else:
            print("❌ Manual sync failed")
            return False

def main():
    """Test cloud database integration"""
    print("🧪 Testing Cloud Database Integration")
    print("=" * 50)
    
    # Test cloud-aware database
    cloud_db = CloudTradingDatabase()
    
    # Test data retrieval
    history = cloud_db.get_trading_history_for_dashboard()
    
    print(f"📊 Trading History Summary:")
    print(f"   Trades: {len(history.get('trades', []))}")
    print(f"   Cycles: {len(history.get('cycles', []))}")
    
    # Test manual sync
    cloud_db.manual_cloud_sync()

if __name__ == "__main__":
    main()