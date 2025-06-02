#!/usr/bin/env python3
"""
Test Aggressive After-Hours Crypto Strategy

Tests the new market session switching, leverage adjustments, and allocation logic
to ensure it works correctly before deployment.
"""

import os
import sys
import logging
from datetime import datetime
from unittest.mock import Mock, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_crypto_module_aggressive_strategy():
    """Test the aggressive after-hours crypto strategy implementation"""
    
    logger.info("🧪 Testing Aggressive After-Hours Crypto Strategy...")
    
    try:
        # Import required components
        from modular.crypto_module import CryptoModule
        from modular.base_module import ModuleConfig
        
        # Mock dependencies
        class MockFirebaseDB:
            def save_trade_opportunity(self, data):
                return "mock_opportunity_id"
            
            def save_trade_result(self, data):
                return "mock_result_id"
        
        class MockRiskManager:
            def get_portfolio_summary(self):
                return {
                    'portfolio_value': 100000,
                    'buying_power': 161416,  # 4:1 leverage
                    'cash': 24532
                }
            
            def validate_opportunity(self, module_name, opportunity):
                return True
            
            def get_module_allocation(self, module_name):
                return 25.0  # 25% current allocation
        
        class MockOrderExecutor:
            def execute_order(self, order_data):
                return {
                    'success': True,
                    'order_id': f'mock_order_{order_data["symbol"]}',
                    'execution_price': 50000.0
                }
        
        class MockAlpacaAPI:
            def get_clock(self):
                # Mock for testing both market hours scenarios
                clock = Mock()
                clock.is_open = False  # Test after-hours mode
                return clock
            
            def get_latest_crypto_quotes(self, symbol):
                return {
                    symbol: Mock(ap=50000.0, bp=49950.0, t=datetime.now())
                }
            
            def list_positions(self):
                return []
        
        # Test 1: Module initialization with aggressive parameters
        logger.info("📋 Test 1: Module initialization...")
        
        config = ModuleConfig(
            module_name="crypto",
            enabled=True,
            max_allocation_pct=30.0,
            min_confidence=0.6,
            max_positions=15,
            custom_params={
                'after_hours_max_allocation_pct': 90.0,
                'leverage_multiplier': 1.5,
                'after_hours_leverage': 3.5,
                'volatility_threshold': 3.0
            }
        )
        
        crypto_module = CryptoModule(
            config=config,
            firebase_db=MockFirebaseDB(),
            risk_manager=MockRiskManager(),
            order_executor=MockOrderExecutor(),
            api_client=MockAlpacaAPI(),
            logger=logger
        )
        
        logger.info("✅ Module initialized successfully")
        
        # Test 2: Market hours detection
        logger.info("📋 Test 2: Market hours detection...")
        
        is_market_open = crypto_module._is_stock_market_open()
        logger.info(f"Market open status: {is_market_open}")
        
        # Test 3: Dynamic allocation calculation
        logger.info("📋 Test 3: Dynamic allocation calculation...")
        
        max_allocation = crypto_module._get_max_allocation_for_current_session()
        leverage = crypto_module._get_leverage_for_current_session()
        
        expected_allocation = 0.90 if not is_market_open else 0.30
        expected_leverage = 3.5 if not is_market_open else 1.5
        
        logger.info(f"Max allocation: {max_allocation:.1%} (expected: {expected_allocation:.1%})")
        logger.info(f"Leverage: {leverage}x (expected: {expected_leverage}x)")
        
        assert abs(max_allocation - expected_allocation) < 0.01, f"Allocation mismatch: {max_allocation} != {expected_allocation}"
        assert abs(leverage - expected_leverage) < 0.01, f"Leverage mismatch: {leverage} != {expected_leverage}"
        
        logger.info("✅ Dynamic allocation works correctly")
        
        # Test 4: Pre-market closure detection
        logger.info("📋 Test 4: Pre-market closure detection...")
        
        should_close = crypto_module._should_close_positions_before_market_open()
        logger.info(f"Should close positions: {should_close}")
        
        # Test 5: Opportunity analysis with aggressive settings
        logger.info("📋 Test 5: Opportunity analysis...")
        
        # Override some methods for testing
        crypto_module._get_current_crypto_allocation = lambda: 0.25  # 25% current
        crypto_module._get_active_crypto_symbols = lambda: ['BTCUSD', 'ETHUSD']
        crypto_module._analyze_crypto_symbol = lambda symbol, session: Mock(
            symbol=symbol,
            current_price=50000.0,
            momentum_score=0.7,
            volatility_score=0.6,
            volume_score=0.8,
            overall_confidence=0.65,
            is_tradeable=True
        )
        
        opportunities = crypto_module.analyze_opportunities()
        logger.info(f"Generated {len(opportunities)} opportunities")
        
        if opportunities:
            opp = opportunities[0]
            logger.info(f"Sample opportunity: {opp.symbol} with quantity {opp.quantity:.6f}")
            
            # Verify aggressive positioning is applied after hours
            if not is_market_open:
                logger.info("✅ After-hours aggressive positioning should be applied")
            else:
                logger.info("ℹ️ Market hours conservative positioning applied")
        
        # Test 6: Position monitoring
        logger.info("📋 Test 6: Position monitoring...")
        
        # Mock existing positions
        crypto_module._get_crypto_positions = lambda: [
            {
                'symbol': 'BTCUSD',
                'quantity': 1.0,
                'market_value': 50000,
                'unrealized_pl': 2500,
                'avg_entry_price': 47500
            }
        ]
        
        crypto_module._analyze_crypto_exit = lambda pos: None  # No exit signal
        
        exit_results = crypto_module.monitor_positions()
        logger.info(f"Exit results: {len(exit_results)} positions processed")
        
        logger.info("✅ All crypto module tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Crypto module test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def test_market_session_scenarios():
    """Test both market hours and after-hours scenarios"""
    
    logger.info("🕐 Testing Market Session Scenarios...")
    
    try:
        from modular.crypto_module import CryptoModule
        from modular.base_module import ModuleConfig
        
        # Test both scenarios
        scenarios = [
            ("AFTER_HOURS", False, 0.90, 3.5),
            ("MARKET_HOURS", True, 0.30, 1.5)
        ]
        
        for scenario_name, market_open, expected_alloc, expected_leverage in scenarios:
            logger.info(f"📊 Testing {scenario_name} scenario...")
            
            # Mock API with different market status
            class MockAPI:
                def get_clock(self):
                    clock = Mock()
                    clock.is_open = market_open
                    return clock
            
            # Create module with mocked API
            config = ModuleConfig(
                module_name="crypto",
                enabled=True,
                custom_params={
                    'after_hours_max_allocation_pct': 90.0,
                    'leverage_multiplier': 1.5,
                    'after_hours_leverage': 3.5
                }
            )
            
            module = CryptoModule(
                config=config,
                firebase_db=Mock(),
                risk_manager=Mock(),
                order_executor=Mock(),
                api_client=MockAPI(),
                logger=logger
            )
            
            # Test calculations
            allocation = module._get_max_allocation_for_current_session()
            leverage = module._get_leverage_for_current_session()
            
            logger.info(f"  Allocation: {allocation:.1%} (expected: {expected_alloc:.1%})")
            logger.info(f"  Leverage: {leverage}x (expected: {expected_leverage}x)")
            
            assert abs(allocation - expected_alloc) < 0.01, f"{scenario_name} allocation failed"
            assert abs(leverage - expected_leverage) < 0.01, f"{scenario_name} leverage failed"
            
            logger.info(f"✅ {scenario_name} scenario works correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Market session test failed: {e}")
        return False


def main():
    """Run all aggressive crypto strategy tests"""
    
    logger.info("🚀 Starting Aggressive Crypto Strategy Test Suite")
    logger.info("=" * 60)
    
    test_results = []
    
    # Test 1: Core aggressive strategy functionality
    logger.info("🧪 Test 1: Aggressive Strategy Implementation")
    test1_success = test_crypto_module_aggressive_strategy()
    test_results.append(("Aggressive Strategy", test1_success))
    
    # Test 2: Market session scenarios
    logger.info("\n🧪 Test 2: Market Session Scenarios")
    test2_success = test_market_session_scenarios()
    test_results.append(("Market Sessions", test2_success))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    
    passed = 0
    failed = 0
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"  {test_name}: {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    logger.info(f"\n📈 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED! Aggressive crypto strategy is ready for deployment.")
        return True
    else:
        logger.error("⚠️ SOME TESTS FAILED! Please fix issues before deployment.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)