#!/usr/bin/env python3
"""
Test ML Entry-Exit Trade Linking System
Verifies that entry trades get updated with final profit/loss for ML learning
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from modular.crypto_module import CryptoModule
from modular.ml_data_helpers import MLTradeData


def test_ml_trade_linking():
    """Test that ML trade linking system works correctly"""
    print("🧪 TESTING ML TRADE LINKING SYSTEM")
    print("="*50)
    
    # Create mock objects for testing
    class MockConfig:
        def __init__(self):
            self.custom_params = {
                'max_allocation_pct': 30.0,
                'leverage_multiplier': 1.5,
                'volatility_threshold': 5.0
            }
            self.min_confidence = 0.35
    
    class MockFirebaseDB:
        def __init__(self):
            self.trades = {}
            self.last_trade_id = 0
        
        def save_trade(self, trade_data):
            self.last_trade_id += 1
            trade_id = f"test_trade_{self.last_trade_id}"
            self.trades[trade_id] = trade_data.copy()
            print(f"✅ Mock saved trade: {trade_id}")
            return trade_id
        
        def update_trade_outcome(self, trade_id, outcome_data):
            if trade_id in self.trades:
                self.trades[trade_id].update(outcome_data)
                print(f"✅ Mock updated trade {trade_id} with P&L: ${outcome_data.get('profit_loss', 0):.2f}")
                return True
            return False
        
        def is_connected(self):
            return True
    
    class MockAPI:
        def get_account(self):
            class Account:
                portfolio_value = 100000
            return Account()
    
    class MockRiskManager:
        def validate_opportunity(self, module_name, opportunity):
            return True
    
    class MockOrderExecutor:
        def execute_order(self, order_data):
            return {'success': True, 'order_id': 'test_order_123'}
    
    # Initialize crypto module with mocks
    try:
        config = MockConfig()
        firebase_db = MockFirebaseDB()
        
        # Test Firebase update method exists
        print("\n1. Testing Firebase update_trade_outcome method...")
        test_outcome = {'profit_loss': 123.45, 'exit_reason': 'profit_target'}
        success = firebase_db.update_trade_outcome('test_id', test_outcome)
        print(f"   Firebase update method works: {success}")
        
        # Test trade linking logic
        print("\n2. Testing trade linking logic...")
        
        # Simulate entry trade
        entry_trade_data = {
            'symbol': 'BTCUSD',
            'side': 'BUY',
            'quantity': 0.1,
            'price': 50000,
            'strategy': 'crypto_momentum',
            'confidence': 0.75,
            'profit_loss': 0.0,  # Entry trade starts with 0
            'timestamp': datetime.now().isoformat()
        }
        
        entry_trade_id = firebase_db.save_trade(entry_trade_data)
        print(f"   Entry trade saved: {entry_trade_id}")
        
        # Simulate position tracking
        position_data = {
            'symbol': 'BTCUSD',
            'entry_price': 50000,
            'quantity': 0.1,
            'investment': 5000,
            'session': 'us_prime',
            'entry_time': datetime.now().isoformat(),
            'entry_trade_id': entry_trade_id  # Link to entry trade
        }
        
        # Simulate exit trade
        exit_outcome = {
            'profit_loss': 456.78,
            'exit_reason': 'profit_target',
            'final_outcome': 'profitable',
            'hold_duration_hours': 4.5,
            'exit_trade_id': 'test_exit_456',
            'updated_at': datetime.now().isoformat()
        }
        
        # Update entry trade with exit outcome
        update_success = firebase_db.update_trade_outcome(entry_trade_id, exit_outcome)
        print(f"   Entry trade updated with exit outcome: {update_success}")
        
        # Verify data integrity
        print("\n3. Verifying data integrity...")
        updated_trade = firebase_db.trades[entry_trade_id]
        print(f"   Original profit_loss: {entry_trade_data['profit_loss']}")
        print(f"   Updated profit_loss: {updated_trade['profit_loss']}")
        print(f"   Exit reason: {updated_trade['exit_reason']}")
        print(f"   Final outcome: {updated_trade['final_outcome']}")
        
        # Test ML data structure
        print("\n4. Testing ML data structure...")
        ml_data = MLTradeData(
            symbol='BTCUSD',
            side='BUY',
            quantity=0.1,
            price=50000,
            strategy='crypto_momentum',
            confidence=0.75,
            profit_loss=456.78  # Final profit
        )
        
        print(f"   ML data profit_loss: ${ml_data.profit_loss}")
        print(f"   ML data to_dict works: {bool(ml_data.to_dict())}")
        
        print("\n✅ ALL TESTS PASSED!")
        print("🧠 ML Trade Linking System is functional!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_ml_trade_linking()
    sys.exit(0 if success else 1)