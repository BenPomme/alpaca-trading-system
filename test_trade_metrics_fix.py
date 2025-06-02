#!/usr/bin/env python3
"""
Test Trade Metrics Fix - Trades Passed vs Successful Trades

Verifies the fix distinguishes between:
- Trades Passed: Orders successfully executed (filled)  
- Successful Trades: Trades that are profitable (pnl > 0)
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


def test_trade_result_metrics():
    """Test TradeResult.passed vs TradeResult.success properties"""
    
    logger.info("🧪 Testing TradeResult Metrics...")
    
    try:
        from modular.base_module import TradeResult, TradeOpportunity, TradeAction, TradeStatus
        
        # Test scenarios
        scenarios = [
            # (status, pnl, expected_passed, expected_success, description)
            (TradeStatus.EXECUTED, None, True, False, "Entry trade (no P&L yet)"),
            (TradeStatus.EXECUTED, 100.0, True, True, "Profitable exit trade"),
            (TradeStatus.EXECUTED, -50.0, True, False, "Loss-making exit trade"),
            (TradeStatus.FAILED, None, False, False, "Failed order"),
            (TradeStatus.PENDING, None, False, False, "Pending order"),
        ]
        
        logger.info("📊 Testing TradeResult metrics...")
        
        for status, pnl, expected_passed, expected_success, description in scenarios:
            # Create mock opportunity
            mock_opportunity = Mock()
            mock_opportunity.symbol = "BTCUSD"
            
            # Create trade result
            trade_result = TradeResult(
                opportunity=mock_opportunity,
                status=status,
                pnl=pnl
            )
            
            # Test properties
            actual_passed = trade_result.passed
            actual_success = trade_result.success
            
            logger.info(f"  {description}:")
            logger.info(f"    Status: {status}, P&L: {pnl}")
            logger.info(f"    Passed: {actual_passed} (expected: {expected_passed})")
            logger.info(f"    Success: {actual_success} (expected: {expected_success})")
            
            assert actual_passed == expected_passed, f"Passed mismatch for {description}"
            assert actual_success == expected_success, f"Success mismatch for {description}"
            
            logger.info(f"    ✅ Correct")
        
        logger.info("✅ All TradeResult metrics tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ TradeResult test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def test_orchestrator_counting():
    """Test orchestrator correctly counts both metrics"""
    
    logger.info("🧪 Testing Orchestrator Counting...")
    
    try:
        from modular.orchestrator import ModularOrchestrator
        from modular.base_module import TradeResult, TradeStatus, ModuleConfig, TradingModule
        
        # Mock trading module
        class MockTradingModule(TradingModule):
            def __init__(self):
                config = ModuleConfig(module_name="test", enabled=True)
                super().__init__(config, None, None, None, logger)
            
            @property
            def module_name(self) -> str:
                return "test"
            
            @property
            def supported_symbols(self) -> list:
                return ["BTCUSD"]
                
            def analyze_opportunities(self):
                return []  # No new opportunities
                
            def execute_trades(self, opportunities):
                return []  # No new trades
                
            def monitor_positions(self):
                # Return mix of passed/failed and profitable/unprofitable trades
                mock_opp = Mock()
                mock_opp.symbol = "BTCUSD"
                
                return [
                    # Executed profitable trade
                    TradeResult(opportunity=mock_opp, status=TradeStatus.EXECUTED, pnl=100.0),
                    # Executed losing trade  
                    TradeResult(opportunity=mock_opp, status=TradeStatus.EXECUTED, pnl=-50.0),
                    # Executed entry trade (no P&L yet)
                    TradeResult(opportunity=mock_opp, status=TradeStatus.EXECUTED, pnl=None),
                    # Failed trade
                    TradeResult(opportunity=mock_opp, status=TradeStatus.FAILED, pnl=None),
                ]
                
            def validate_opportunity(self, opportunity):
                return True
                
            def save_opportunity(self, opportunity):
                pass
                
            def save_result(self, result):
                pass
        
        # Create orchestrator
        orchestrator = ModularOrchestrator(
            firebase_db=Mock(),
            risk_manager=Mock(),
            order_executor=Mock(),
            logger=logger
        )
        
        # Register test module
        test_module = MockTradingModule()
        orchestrator.register_module(test_module)
        
        # Run single cycle
        results = orchestrator.run_single_cycle()
        
        logger.info("📊 Orchestrator Results:")
        logger.info(f"  Total trades: {results['summary']['total_trades']}")
        logger.info(f"  Trades passed: {results['summary']['trades_passed']}")
        logger.info(f"  Successful trades: {results['summary']['successful_trades']}")
        
        # Expected results:
        # 4 total trades: 1 profitable, 1 loss, 1 entry, 1 failed
        # 3 trades passed: 1 profitable + 1 loss + 1 entry (failed doesn't count)
        # 1 successful trade: only the profitable one
        
        expected_total = 4
        expected_passed = 3  # 3 executed orders
        expected_successful = 1  # 1 profitable trade
        
        assert results['summary']['total_trades'] == expected_total, f"Total trades: {results['summary']['total_trades']} != {expected_total}"
        assert results['summary']['trades_passed'] == expected_passed, f"Trades passed: {results['summary']['trades_passed']} != {expected_passed}"
        assert results['summary']['successful_trades'] == expected_successful, f"Successful trades: {results['summary']['successful_trades']} != {expected_successful}"
        
        logger.info("✅ Orchestrator counting correct!")
        
        # Test module-level results too
        module_result = results['modules']['test']
        logger.info(f"📊 Module Results:")
        logger.info(f"  Trades: {module_result['trades_count']}")
        logger.info(f"  Passed: {module_result['trades_passed']}")
        logger.info(f"  Successful: {module_result['successful_trades']}")
        
        assert module_result['trades_count'] == expected_total, f"Module total trades mismatch"
        assert module_result['trades_passed'] == expected_passed, f"Module trades passed mismatch" 
        assert module_result['successful_trades'] == expected_successful, f"Module successful trades mismatch"
        
        logger.info("✅ Module counting correct!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Orchestrator test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def main():
    """Run all trade metrics tests"""
    
    logger.info("🚀 Starting Trade Metrics Fix Test Suite")
    logger.info("=" * 60)
    
    test_results = []
    
    # Test 1: TradeResult properties
    logger.info("🧪 Test 1: TradeResult Properties")
    test1_success = test_trade_result_metrics()
    test_results.append(("TradeResult Properties", test1_success))
    
    # Test 2: Orchestrator counting
    logger.info("\n🧪 Test 2: Orchestrator Counting")
    test2_success = test_orchestrator_counting()
    test_results.append(("Orchestrator Counting", test2_success))
    
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
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("💰 Trade metrics now properly distinguish:")
        logger.info("  📋 Trades Passed = Orders successfully executed")
        logger.info("  💰 Successful Trades = Profitable trades only")
        return True
    else:
        logger.error("⚠️ SOME TESTS FAILED! Please fix issues before deployment.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)