#!/usr/bin/env python3
"""
Test Market Hours Fix in Order Executor

Tests the critical fix that prevents stock orders outside market hours
"""

import os
import sys
import logging
from unittest.mock import Mock

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_market_hours_validation():
    """Test the market hours validation in order executor"""
    
    logger.info("🧪 Testing Market Hours Validation Fix...")
    
    try:
        from modular.order_executor import ModularOrderExecutor
        
        # Test 1: Market Closed - Should Block Stock Orders
        logger.info("📋 Test 1: Market Closed - Stock Order Blocking")
        
        class MockAPIClosed:
            def get_clock(self):
                clock = Mock()
                clock.is_open = False  # Market is closed
                return clock
        
        executor_closed = ModularOrderExecutor(MockAPIClosed(), logger)
        
        # Try to execute Apple stock order when market is closed
        apple_order = {
            'symbol': 'AAPL',
            'qty': 10,
            'side': 'buy',
            'type': 'market'
        }
        
        result = executor_closed.execute_order(apple_order)
        
        logger.info(f"Apple order result: {result}")
        assert not result['success'], "Stock order should be blocked when market is closed"
        assert 'Market closed' in result['error'], "Error should mention market closure"
        logger.info("✅ Stock orders correctly blocked when market closed")
        
        # Test 2: Market Closed - Should Allow Crypto Orders
        logger.info("📋 Test 2: Market Closed - Crypto Order Allowing")
        
        crypto_order = {
            'symbol': 'BTCUSD',
            'qty': 0.1,
            'side': 'buy',
            'type': 'market'
        }
        
        # Mock crypto price data
        executor_closed._get_current_price = lambda symbol: 50000.0
        executor_closed._has_pending_order = lambda symbol, side: False
        executor_closed.api.submit_order = lambda **kwargs: Mock(id='crypto_order_123')
        
        result = executor_closed.execute_order(crypto_order)
        
        logger.info(f"Crypto order result: {result}")
        assert result['success'], "Crypto order should be allowed when market is closed"
        logger.info("✅ Crypto orders correctly allowed when market closed")
        
        # Test 3: Market Open - Should Allow Stock Orders
        logger.info("📋 Test 3: Market Open - Stock Order Allowing")
        
        class MockAPIOpen:
            def get_clock(self):
                clock = Mock()
                clock.is_open = True  # Market is open
                return clock
            
            def submit_order(self, **kwargs):
                return Mock(id='stock_order_456')
        
        executor_open = ModularOrderExecutor(MockAPIOpen(), logger)
        executor_open._get_current_price = lambda symbol: 150.0
        executor_open._has_pending_order = lambda symbol, side: False
        
        result = executor_open.execute_order(apple_order)
        
        logger.info(f"Apple order (market open) result: {result}")
        assert result['success'], "Stock order should be allowed when market is open"
        logger.info("✅ Stock orders correctly allowed when market open")
        
        # Test 4: Symbol Detection
        logger.info("📋 Test 4: Symbol Type Detection")
        
        test_symbols = [
            ('AAPL', False, 'Stock'),
            ('BTCUSD', True, 'Crypto'),
            ('ETHUSD', True, 'Crypto'),
            ('SPY', False, 'Stock'),
            ('BTC/USD', True, 'Crypto'),
            ('TSLA', False, 'Stock')
        ]
        
        for symbol, expected_crypto, symbol_type in test_symbols:
            is_crypto = executor_closed._is_crypto_symbol(symbol)
            logger.info(f"  {symbol}: {'Crypto' if is_crypto else 'Stock'} (expected: {symbol_type})")
            assert is_crypto == expected_crypto, f"Symbol detection failed for {symbol}"
        
        logger.info("✅ Symbol type detection works correctly")
        
        logger.info("🎉 All market hours validation tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Market hours test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def main():
    """Run market hours validation tests"""
    
    logger.info("🚀 Starting Market Hours Validation Test Suite")
    logger.info("=" * 60)
    
    success = test_market_hours_validation()
    
    logger.info("=" * 60)
    if success:
        logger.info("✅ ALL MARKET HOURS TESTS PASSED!")
        logger.info("🛡️ Apple stock orders will be properly blocked outside market hours")
        return True
    else:
        logger.error("❌ MARKET HOURS TESTS FAILED!")
        logger.error("⚠️ Fix issues before deployment")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)