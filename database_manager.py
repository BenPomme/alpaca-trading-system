#!/usr/bin/env python3
"""
Database Manager for Trading System
SQLite-based data persistence with minimal dependencies
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class TradingDatabase:
    """SQLite database manager for trading data"""
    
    def __init__(self, db_path='data/trading_system.db'):
        self.db_path = db_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self.init_database()
        print(f"✅ Database initialized: {db_path}")
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Market quotes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                bid_price REAL,
                ask_price REAL,
                timestamp TEXT NOT NULL,
                date_created TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trading cycles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_number INTEGER,
                regime TEXT NOT NULL,
                strategy TEXT NOT NULL,
                confidence REAL,
                quotes_count INTEGER,
                timestamp TEXT NOT NULL,
                cycle_data TEXT,
                date_created TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Real trades table (for actual executions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,  -- 'buy' or 'sell'
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                strategy TEXT NOT NULL,
                regime TEXT,
                confidence REAL,
                timestamp TEXT NOT NULL,
                order_id TEXT,
                exit_reason TEXT,
                profit_loss REAL DEFAULT 0,
                date_created TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Virtual trades table (for performance tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS virtual_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,  -- 'buy' or 'sell'
                price REAL NOT NULL,
                quantity INTEGER DEFAULT 100,
                strategy TEXT NOT NULL,
                regime TEXT NOT NULL,
                confidence REAL,
                timestamp TEXT NOT NULL,
                cycle_id INTEGER,
                profit_loss REAL DEFAULT 0,
                date_created TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cycle_id) REFERENCES trading_cycles (id)
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                period TEXT NOT NULL,  -- 'daily', 'weekly', 'monthly'
                timestamp TEXT NOT NULL,
                details TEXT,
                date_created TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quotes_symbol_timestamp ON market_quotes(symbol, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cycles_timestamp ON trading_cycles(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_symbol_timestamp ON trades(symbol, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_virtual_trades_symbol_timestamp ON virtual_trades(symbol, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy, timestamp)')
        
        conn.commit()
        conn.close()
    
    def store_market_quote(self, symbol: str, bid_price: float, ask_price: float, timestamp: str = None):
        """Store market quote data"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_quotes (symbol, bid_price, ask_price, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (symbol, bid_price, ask_price, timestamp))
        
        conn.commit()
        conn.close()
    
    def store_trading_cycle(self, cycle_data: Dict, cycle_number: int = None):
        """Store trading cycle data"""
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trading_cycles 
            (cycle_number, regime, strategy, confidence, quotes_count, timestamp, cycle_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            cycle_number,
            cycle_data.get('regime', ''),
            cycle_data.get('strategy', ''),
            cycle_data.get('confidence', 0),
            cycle_data.get('quotes_count', 0),
            timestamp,
            json.dumps(cycle_data)
        ))
        
        cycle_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return cycle_id
    
    def store_virtual_trade(self, symbol: str, action: str, price: float, 
                           strategy: str, regime: str, confidence: float = 0.0, 
                           cycle_id: int = None):
        """Store virtual trade for performance tracking"""
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO virtual_trades 
            (symbol, action, price, strategy, regime, confidence, timestamp, cycle_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, action, price, strategy, regime, confidence, timestamp, cycle_id))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return trade_id
    
    def get_recent_quotes(self, symbol: str = None, limit: int = 100) -> List[Dict]:
        """Get recent market quotes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute('''
                SELECT symbol, bid_price, ask_price, timestamp
                FROM market_quotes 
                WHERE symbol = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (symbol, limit))
        else:
            cursor.execute('''
                SELECT symbol, bid_price, ask_price, timestamp
                FROM market_quotes 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'symbol': row[0],
                'bid_price': row[1],
                'ask_price': row[2],
                'timestamp': row[3]
            })
        
        conn.close()
        return results
    
    def get_recent_cycles(self, limit: int = 20) -> List[Dict]:
        """Get recent trading cycles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, cycle_number, regime, strategy, confidence, quotes_count, timestamp, cycle_data
            FROM trading_cycles 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            cycle_data = json.loads(row[7]) if row[7] else {}
            results.append({
                'id': row[0],
                'cycle_number': row[1],
                'regime': row[2],
                'strategy': row[3],
                'confidence': row[4],
                'quotes_count': row[5],
                'timestamp': row[6],
                'cycle_data': cycle_data
            })
        
        conn.close()
        return results
    
    def get_virtual_trades(self, symbol: str = None, limit: int = 50) -> List[Dict]:
        """Get virtual trades for analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute('''
                SELECT symbol, action, price, strategy, regime, confidence, timestamp, profit_loss
                FROM virtual_trades 
                WHERE symbol = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (symbol, limit))
        else:
            cursor.execute('''
                SELECT symbol, action, price, strategy, regime, confidence, timestamp, profit_loss
                FROM virtual_trades 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'symbol': row[0],
                'action': row[1],
                'price': row[2],
                'strategy': row[3],
                'regime': row[4],
                'confidence': row[5],
                'timestamp': row[6],
                'profit_loss': row[7]
            })
        
        conn.close()
        return results
    
    def get_trades_by_strategy(self, strategy: str, days: int = 30) -> List[Dict]:
        """Get trades filtered by strategy for ML analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # First try real trades table
        cursor.execute('''
            SELECT symbol, side, price, quantity, strategy, regime, confidence, timestamp, profit_loss, exit_reason
            FROM trades 
            WHERE strategy = ? AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (strategy, cutoff_date))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'symbol': row[0],
                'side': row[1],
                'price': row[2],
                'quantity': row[3],
                'strategy': row[4],
                'regime': row[5],
                'confidence': row[6],
                'timestamp': row[7],
                'profit_loss': row[8],
                'exit_reason': row[9]
            })
        
        # If no real trades, fallback to virtual trades for analysis
        if not results:
            cursor.execute('''
                SELECT symbol, action, price, quantity, strategy, regime, confidence, timestamp, profit_loss
                FROM virtual_trades 
                WHERE strategy = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (strategy, cutoff_date))
            
            for row in cursor.fetchall():
                results.append({
                    'symbol': row[0],
                    'side': row[1],  # Map action to side
                    'price': row[2],
                    'quantity': row[3],
                    'strategy': row[4],
                    'regime': row[5],
                    'confidence': row[6],
                    'timestamp': row[7],
                    'profit_loss': row[8],
                    'exit_reason': None
                })
        
        conn.close()
        return results
    
    def store_trade(self, symbol: str, side: str, price: float, quantity: float, 
                   strategy: str, regime: str = None, confidence: float = None, 
                   order_id: str = None, exit_reason: str = None, profit_loss: float = 0):
        """Store a real trade execution"""
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (symbol, side, price, quantity, strategy, regime, confidence, 
                              timestamp, order_id, exit_reason, profit_loss)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, side, price, quantity, strategy, regime, confidence, 
              timestamp, order_id, exit_reason, profit_loss))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return trade_id
    
    def calculate_strategy_performance(self, strategy: str = None, days: int = 30) -> Dict:
        """Calculate strategy performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        if strategy:
            cursor.execute('''
                SELECT COUNT(*) as trade_count,
                       AVG(confidence) as avg_confidence,
                       COUNT(CASE WHEN profit_loss > 0 THEN 1 END) as winning_trades,
                       AVG(profit_loss) as avg_return
                FROM virtual_trades 
                WHERE strategy = ? AND timestamp > ?
            ''', (strategy, cutoff_date))
        else:
            cursor.execute('''
                SELECT COUNT(*) as trade_count,
                       AVG(confidence) as avg_confidence,
                       COUNT(CASE WHEN profit_loss > 0 THEN 1 END) as winning_trades,
                       AVG(profit_loss) as avg_return
                FROM virtual_trades 
                WHERE timestamp > ?
            ''', (cutoff_date,))
        
        row = cursor.fetchone()
        
        trade_count = row[0] or 0
        win_rate = (row[2] or 0) / trade_count if trade_count > 0 else 0
        
        performance = {
            'strategy': strategy or 'all',
            'period_days': days,
            'trade_count': trade_count,
            'avg_confidence': row[1] or 0,
            'win_rate': win_rate,
            'avg_return': row[3] or 0,
            'calculated_at': datetime.now().isoformat()
        }
        
        conn.close()
        return performance
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data to manage database size"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clean old quotes (keep more recent data)
        cursor.execute('DELETE FROM market_quotes WHERE timestamp < ?', (cutoff_date,))
        quotes_deleted = cursor.rowcount
        
        # Clean old cycles (keep less data)
        cursor.execute('DELETE FROM trading_cycles WHERE timestamp < ?', (cutoff_date,))
        cycles_deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return {
            'quotes_deleted': quotes_deleted,
            'cycles_deleted': cycles_deleted,
            'cutoff_date': cutoff_date
        }

# Test function
def test_database():
    """Test database functionality"""
    print("🧪 Testing Database Manager...")
    
    # Initialize database
    db = TradingDatabase('data/test_trading_system.db')
    
    # Test market quote storage
    db.store_market_quote('SPY', 590.00, 590.05)
    db.store_market_quote('QQQ', 520.00, 520.05)
    print("✅ Market quotes stored")
    
    # Test cycle storage
    test_cycle = {
        'regime': 'active',
        'strategy': 'momentum',
        'confidence': 0.8,
        'quotes_count': 3
    }
    cycle_id = db.store_trading_cycle(test_cycle, cycle_number=1)
    print(f"✅ Trading cycle stored (ID: {cycle_id})")
    
    # Test virtual trade storage
    trade_id = db.store_virtual_trade('SPY', 'buy', 590.02, 'momentum', 'active', 0.8, cycle_id)
    print(f"✅ Virtual trade stored (ID: {trade_id})")
    
    # Test data retrieval
    recent_quotes = db.get_recent_quotes('SPY', 5)
    recent_cycles = db.get_recent_cycles(5)
    virtual_trades = db.get_virtual_trades(limit=5)
    
    print(f"✅ Retrieved {len(recent_quotes)} quotes, {len(recent_cycles)} cycles, {len(virtual_trades)} trades")
    
    # Test performance calculation
    performance = db.calculate_strategy_performance('momentum', 30)
    print(f"✅ Performance calculated: {performance}")
    
    # Cleanup test database
    if os.path.exists('data/test_trading_system.db'):
        os.remove('data/test_trading_system.db')
        print("✅ Test database cleaned up")
    
    print("🎉 Database tests completed successfully!")

if __name__ == "__main__":
    test_database()