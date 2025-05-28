#!/usr/bin/env python3
"""
Testing Framework for Trading System
Ensures each development step can be tested and reverted safely
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from start_ultra_simple import UltraSimpleTrader

class TradingSystemTester:
    """Test framework for safe development"""
    
    def __init__(self):
        self.test_results = []
        self.backup_files = []
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def backup_file(self, filepath):
        """Create backup of file before modification"""
        if os.path.exists(filepath):
            backup_path = f"{filepath}.backup_{int(datetime.now().timestamp())}"
            os.system(f"cp {filepath} {backup_path}")
            self.backup_files.append((filepath, backup_path))
            self.log_test("File Backup", "PASS", f"Backed up {filepath}")
            return backup_path
        return None
    
    def test_basic_system(self):
        """Test current system functionality"""
        try:
            # Test trader initialization
            trader = UltraSimpleTrader()
            self.log_test("Trader Initialization", "PASS")
            
            # Test account connection
            account_ok = trader.check_account()
            status = "PASS" if account_ok else "FAIL"
            self.log_test("Account Connection", status)
            
            # Test market data
            quote = trader.get_quote('SPY')
            status = "PASS" if quote and quote.get('ask', 0) > 0 else "FAIL"
            self.log_test("Market Data", status, f"SPY: ${quote.get('ask', 'N/A')}")
            
            # Test cycle execution
            cycle_data = trader.run_cycle()
            status = "PASS" if cycle_data else "FAIL"
            self.log_test("Trading Cycle", status, f"Regime: {cycle_data.get('regime', 'N/A')}")
            
            return all(r['status'] == 'PASS' for r in self.test_results[-4:])
            
        except Exception as e:
            self.log_test("Basic System Test", "FAIL", str(e))
            return False
    
    def test_database_functionality(self):
        """Test SQLite database operations"""
        try:
            # Test database creation
            db_path = 'data/test_market_data.db'
            os.makedirs('data', exist_ok=True)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Test table creation
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            self.log_test("Database Creation", "PASS")
            
            # Test data insertion
            test_data = ('SPY', 590.50, datetime.now().isoformat())
            cursor.execute('INSERT INTO market_quotes (symbol, price, timestamp) VALUES (?, ?, ?)', test_data)
            conn.commit()
            self.log_test("Data Insertion", "PASS")
            
            # Test data retrieval
            cursor.execute('SELECT * FROM market_quotes WHERE symbol = ?', ('SPY',))
            result = cursor.fetchone()
            status = "PASS" if result else "FAIL"
            self.log_test("Data Retrieval", status, f"Retrieved: {result}")
            
            conn.close()
            
            # Cleanup test database
            if os.path.exists(db_path):
                os.remove(db_path)
                self.log_test("Database Cleanup", "PASS")
            
            return True
            
        except Exception as e:
            self.log_test("Database Test", "FAIL", str(e))
            return False
    
    def test_enhanced_market_data(self, symbols_list):
        """Test expanded market data collection"""
        try:
            trader = UltraSimpleTrader()
            successful_quotes = 0
            total_symbols = len(symbols_list)
            
            for symbol in symbols_list[:5]:  # Test first 5 symbols
                try:
                    quote = trader.get_quote(symbol)
                    if quote and quote.get('ask', 0) > 0:
                        successful_quotes += 1
                except:
                    pass
            
            success_rate = successful_quotes / min(5, total_symbols)
            status = "PASS" if success_rate >= 0.6 else "WARN" if success_rate >= 0.4 else "FAIL"
            
            self.log_test("Enhanced Market Data", status, 
                         f"{successful_quotes}/{min(5, total_symbols)} symbols successful ({success_rate:.1%})")
            
            return success_rate >= 0.4
            
        except Exception as e:
            self.log_test("Enhanced Market Data", "FAIL", str(e))
            return False
    
    def rollback_changes(self):
        """Rollback all backed up files"""
        print("\n🔄 Rolling back changes...")
        for original_path, backup_path in self.backup_files:
            if os.path.exists(backup_path):
                os.system(f"cp {backup_path} {original_path}")
                print(f"✅ Restored {original_path}")
        
        print("🔄 Rollback completed")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 TEST REPORT")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        warnings = sum(1 for r in self.test_results if r['status'] == 'WARN')
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings: {warnings}")
        print(f"📊 Total: {len(self.test_results)}")
        
        if failed == 0:
            print("\n🎉 All tests passed! Safe to proceed.")
            return True
        else:
            print("\n⚠️ Some tests failed. Review before proceeding.")
            return False

def run_pre_development_tests():
    """Run comprehensive tests before starting development"""
    print("🧪 TRADING SYSTEM TESTING FRAMEWORK")
    print("=" * 50)
    print("Testing current system before Phase 1 development...")
    print()
    
    tester = TradingSystemTester()
    
    # Test basic system
    print("🔍 Testing Basic System...")
    basic_ok = tester.test_basic_system()
    
    # Test database functionality
    print("\n🔍 Testing Database Functionality...")
    db_ok = tester.test_database_functionality()
    
    # Test sample enhanced market data
    print("\n🔍 Testing Enhanced Market Data...")
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    market_ok = tester.test_enhanced_market_data(test_symbols)
    
    # Generate report
    success = tester.generate_test_report()
    
    return tester, success

if __name__ == "__main__":
    # Set environment variables for testing
    os.environ['ALPACA_PAPER_API_KEY'] = os.environ.get('ALPACA_PAPER_API_KEY', 'PKOBXG3RWCRQTXH6ID0L')
    os.environ['ALPACA_PAPER_SECRET_KEY'] = os.environ.get('ALPACA_PAPER_SECRET_KEY', '8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn')
    
    tester, success = run_pre_development_tests()
    
    if not success:
        print("\n⚠️ Fix issues before proceeding with Phase 1 development")
        sys.exit(1)
    else:
        print("\n🚀 System ready for Phase 1 development!")
        sys.exit(0)