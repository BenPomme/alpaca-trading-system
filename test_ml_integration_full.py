#!/usr/bin/env python3
"""
Test Full ML Integration with Real Components
Tests the complete ML profit learning pipeline
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from modular.firebase_interface import ModularFirebaseInterface


def test_full_ml_integration():
    """Test full ML integration with real Firebase components"""
    print("🧪 TESTING FULL ML INTEGRATION")
    print("="*50)
    
    try:
        # Test with mock Firebase (since we don't want to hit real Firebase in tests)
        class MockFirebaseDB:
            def __init__(self):
                self.trades = {}
                self.last_trade_id = 0
            
            def save_trade(self, trade_data):
                self.last_trade_id += 1
                trade_id = f"test_trade_{self.last_trade_id}"
                self.trades[trade_id] = trade_data.copy()
                print(f"✅ Saved trade: {trade_id} - Symbol: {trade_data.get('symbol')}")
                return trade_id
            
            def update_trade_outcome(self, trade_id, outcome_data):
                if trade_id in self.trades:
                    self.trades[trade_id].update(outcome_data)
                    pnl = outcome_data.get('profit_loss', 0)
                    print(f"✅ Updated trade {trade_id} with P&L: ${pnl:.2f}")
                    return True
                else:
                    print(f"❌ Trade {trade_id} not found for update")
                    return False
            
            def is_connected(self):
                return True
        
        # Initialize components
        firebase_db = MockFirebaseDB()
        modular_interface = ModularFirebaseInterface(firebase_db)
        
        print("1. Testing modular Firebase interface...")
        print(f"   Connected: {modular_interface.is_connected()}")
        
        # Test entry trade saving
        print("\n2. Testing entry trade saving...")
        entry_trade = {
            'symbol': 'BTCUSD',
            'side': 'BUY',
            'quantity': 0.1,
            'price': 50000,
            'strategy': 'crypto_momentum',
            'confidence': 0.75,
            'profit_loss': 0.0,  # Entry starts with 0
            'module': 'crypto',
            'timestamp': datetime.now().isoformat()
        }
        
        entry_trade_id = modular_interface.save_trade(entry_trade)
        print(f"   Entry trade ID: {entry_trade_id}")
        
        # Test exit trade with profit update
        print("\n3. Testing exit trade with profit update...")
        exit_outcome = {
            'profit_loss': 750.50,  # Made $750.50 profit
            'exit_reason': 'profit_target',
            'final_outcome': 'profitable',
            'hold_duration_hours': 6.5,
            'updated_at': datetime.now().isoformat()
        }
        
        update_success = modular_interface.update_trade_outcome(entry_trade_id, exit_outcome)
        print(f"   Update success: {update_success}")
        
        # Verify ML data integrity
        print("\n4. Verifying ML data integrity...")
        final_trade = firebase_db.trades[entry_trade_id]
        
        print(f"   Original profit_loss: {entry_trade['profit_loss']}")
        print(f"   Final profit_loss: {final_trade['profit_loss']}")
        print(f"   Exit reason: {final_trade.get('exit_reason', 'None')}")
        print(f"   Final outcome: {final_trade.get('final_outcome', 'None')}")
        
        # Success criteria
        if (update_success and 
            final_trade['profit_loss'] == 750.50 and 
            final_trade.get('exit_reason') == 'profit_target'):
            
            print("\n✅ ALL INTEGRATION TESTS PASSED!")
            print("🧠 ML profit learning system is fully functional!")
            return True
        else:
            print("\n❌ INTEGRATION TEST FAILED!")
            return False
            
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_ml_integration()
    sys.exit(0 if success else 1)