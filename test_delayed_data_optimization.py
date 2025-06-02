#!/usr/bin/env python3
"""
Test Delayed Data Optimization

Validates the delayed data trading optimization for free Alpaca accounts.
Tests data mode manager, cycle timing adjustments, and strategy optimization.
"""

import os
import sys
import logging
from unittest.mock import Mock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_data_mode_detection():
    """Test automatic data mode detection based on subscription level"""
    
    logger.info("🧪 Testing Data Mode Detection...")
    
    try:
        from data_mode_manager import DataModeManager, DataMode, SubscriptionLevel
        
        # Test free account detection
        with patch.dict(os.environ, {'ALPACA_SUBSCRIPTION_LEVEL': 'free'}, clear=False):
            manager_free = DataModeManager()
            assert manager_free.subscription_level == SubscriptionLevel.FREE
            assert manager_free.data_mode == DataMode.DELAYED
            assert manager_free.get_cycle_delay() == 900  # 15 minutes
            logger.info("✅ Free account detected correctly")
        
        # Test paid account detection
        with patch.dict(os.environ, {'ALPACA_SUBSCRIPTION_LEVEL': 'unlimited'}, clear=False):
            manager_paid = DataModeManager()
            assert manager_paid.subscription_level == SubscriptionLevel.UNLIMITED
            assert manager_paid.data_mode == DataMode.REALTIME
            assert manager_paid.get_cycle_delay() == 60  # 1 minute
            logger.info("✅ Paid account detected correctly")
        
        # Test realtime enabled override
        with patch.dict(os.environ, {'REALTIME_DATA_ENABLED': 'true'}, clear=False):
            manager_realtime = DataModeManager()
            assert manager_realtime.data_mode == DataMode.REALTIME
            logger.info("✅ Real-time override detected correctly")
        
        logger.info("✅ All data mode detection tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Data mode detection test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def test_delayed_data_configuration():
    """Test delayed data configuration parameters"""
    
    logger.info("🧪 Testing Delayed Data Configuration...")
    
    try:
        from data_mode_manager import DataModeManager
        
        # Force delayed mode
        manager = DataModeManager(subscription_level='free')
        
        # Test cycle timing
        assert manager.get_cycle_delay() == 900, f"Expected 900s cycle, got {manager.get_cycle_delay()}s"
        
        # Test quote staleness thresholds
        assert manager.is_quote_acceptable(900), "900s quote should be acceptable for delayed mode"
        assert manager.is_quote_acceptable(1200), "1200s quote should be acceptable for delayed mode"
        assert not manager.should_warn_about_staleness(600), "600s quote should not trigger warning"
        assert manager.should_warn_about_staleness(2000), "2000s quote should trigger warning"
        
        # Test risk parameters
        risk_params = manager.get_risk_parameters()
        assert risk_params['stop_loss_buffer'] == 1.5, "Stop loss buffer should be 1.5x for delayed data"
        assert risk_params['max_daily_trades'] == 8, "Max daily trades should be reduced for delayed data"
        
        # Test strategy configuration
        crypto_config = manager.get_strategy_config('crypto')
        assert 'daily_momentum' in crypto_config['enabled_strategies'], "Daily momentum should be enabled"
        assert 'scalping' in crypto_config['disabled_strategies'], "Scalping should be disabled"
        assert crypto_config['confidence_threshold'] == 0.7, "Higher confidence threshold for delayed data"
        
        logger.info("📊 Delayed Data Configuration:")
        logger.info(f"   Cycle Delay: {manager.get_cycle_delay()}s")
        logger.info(f"   Quote Staleness OK: <{manager.config['quote_staleness_threshold']}s")
        logger.info(f"   Position Size Multiplier: {manager.get_position_sizing_multiplier()}")
        logger.info(f"   Max Daily Trades: {risk_params['max_daily_trades']}")
        
        logger.info("✅ Delayed data configuration correct!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Delayed data configuration test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def test_realtime_data_configuration():
    """Test real-time data configuration parameters"""
    
    logger.info("🧪 Testing Real-Time Data Configuration...")
    
    try:
        from data_mode_manager import DataModeManager
        
        # Force real-time mode
        manager = DataModeManager(subscription_level='unlimited')
        
        # Test cycle timing
        assert manager.get_cycle_delay() == 60, f"Expected 60s cycle, got {manager.get_cycle_delay()}s"
        
        # Test quote staleness thresholds
        assert manager.is_quote_acceptable(60), "60s quote should be acceptable for real-time mode"
        assert not manager.is_quote_acceptable(300), "300s quote should not be acceptable for real-time mode"
        assert manager.should_warn_about_staleness(400), "400s quote should trigger warning"
        
        # Test risk parameters
        risk_params = manager.get_risk_parameters()
        assert risk_params['stop_loss_buffer'] == 1.0, "Stop loss buffer should be 1.0x for real-time data"
        assert risk_params['max_daily_trades'] == 50, "Max daily trades should be higher for real-time data"
        
        # Test strategy configuration
        crypto_config = manager.get_strategy_config('crypto')
        assert 'momentum_scalping' in crypto_config['enabled_strategies'], "Momentum scalping should be enabled"
        assert len(crypto_config['disabled_strategies']) == 0, "No strategies should be disabled for real-time"
        assert crypto_config['confidence_threshold'] == 0.6, "Lower confidence threshold for real-time data"
        
        logger.info("📊 Real-Time Data Configuration:")
        logger.info(f"   Cycle Delay: {manager.get_cycle_delay()}s")
        logger.info(f"   Quote Staleness OK: <{manager.config['quote_staleness_threshold']}s")
        logger.info(f"   Position Size Multiplier: {manager.get_position_sizing_multiplier()}")
        logger.info(f"   Max Daily Trades: {risk_params['max_daily_trades']}")
        
        logger.info("✅ Real-time data configuration correct!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Real-time data configuration test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def test_upgrade_recommendation():
    """Test upgrade recommendation logic"""
    
    logger.info("🧪 Testing Upgrade Recommendation...")
    
    try:
        from data_mode_manager import DataModeManager
        
        manager = DataModeManager(subscription_level='free')
        
        # Test scenarios
        scenarios = [
            (50, False, "Low profit - should not recommend upgrade"),
            (150, False, "Moderate profit - marginal benefit"),
            (300, True, "High profit - should recommend upgrade"),
            (500, True, "Very high profit - strong upgrade recommendation")
        ]
        
        for monthly_profit, expected_recommendation, description in scenarios:
            recommendation = manager.get_upgrade_recommendation(monthly_profit)
            
            logger.info(f"💰 Monthly Profit: ${monthly_profit}")
            logger.info(f"   Recommended: {recommendation['recommended']}")
            logger.info(f"   Reason: {recommendation['reason']}")
            logger.info(f"   Expected: {expected_recommendation} - {description}")
            
            # Test the actual recommendation logic
            assert recommendation['recommended'] == expected_recommendation, f"Wrong recommendation for ${monthly_profit}: got {recommendation['recommended']}, expected {expected_recommendation}"
            
            logger.info(f"   ✅ Correct recommendation")
            logger.info("")
        
        logger.info("✅ Upgrade recommendation logic working!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Upgrade recommendation test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def test_strategy_enablement():
    """Test strategy enablement based on data mode"""
    
    logger.info("🧪 Testing Strategy Enablement...")
    
    try:
        from data_mode_manager import DataModeManager, should_enable_strategy
        
        # Test delayed data mode
        manager_delayed = DataModeManager(subscription_level='free')
        
        # Should enable swing trading strategies
        assert manager_delayed.is_strategy_enabled('crypto', 'daily_momentum'), "Daily momentum should be enabled for delayed"
        assert manager_delayed.is_strategy_enabled('crypto', 'weekly_breakouts'), "Weekly breakouts should be enabled for delayed"
        
        # Should disable scalping strategies
        assert not manager_delayed.is_strategy_enabled('crypto', 'scalping'), "Scalping should be disabled for delayed"
        assert not manager_delayed.is_strategy_enabled('stocks', 'intraday_scalping'), "Intraday scalping should be disabled"
        
        # Test real-time data mode
        manager_realtime = DataModeManager(subscription_level='unlimited')
        
        # Should enable all strategies including scalping
        assert manager_realtime.is_strategy_enabled('crypto', 'momentum_scalping'), "Momentum scalping should be enabled for real-time"
        assert manager_realtime.is_strategy_enabled('stocks', 'intraday_momentum'), "Intraday momentum should be enabled"
        
        # Test convenience function
        with patch.dict(os.environ, {'ALPACA_SUBSCRIPTION_LEVEL': 'free'}, clear=False):
            assert should_enable_strategy('crypto', 'daily_momentum'), "Convenience function should work for delayed mode"
            assert not should_enable_strategy('crypto', 'scalping'), "Convenience function should disable scalping for delayed mode"
        
        logger.info("📊 Strategy Enablement Results:")
        logger.info("   Delayed Mode:")
        logger.info("     ✅ Daily momentum: Enabled")
        logger.info("     ❌ Scalping: Disabled")
        logger.info("   Real-Time Mode:")
        logger.info("     ✅ All strategies: Enabled")
        
        logger.info("✅ Strategy enablement working correctly!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Strategy enablement test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def test_production_config_integration():
    """Test production config integration with data mode manager"""
    
    logger.info("🧪 Testing Production Config Integration...")
    
    try:
        # Test with free account environment
        with patch.dict(os.environ, {'ALPACA_SUBSCRIPTION_LEVEL': 'free'}, clear=False):
            from production_config import ProductionConfig
            
            config = ProductionConfig()
            
            # Should auto-configure for delayed data
            cycle_delay = config.get_int('INTRADAY_CYCLE_DELAY')
            assert cycle_delay == 900, f"Expected 900s cycle delay for free account, got {cycle_delay}s"
            
            data_feed = config.get('ALPACA_DATA_FEED')
            assert data_feed == 'iex', f"Expected IEX data feed for free account, got {data_feed}"
            
            logger.info(f"📊 Free Account Configuration:")
            logger.info(f"   Cycle Delay: {cycle_delay}s")
            logger.info(f"   Data Feed: {data_feed}")
            logger.info(f"   Subscription: {config.get('ALPACA_SUBSCRIPTION_LEVEL')}")
        
        logger.info("✅ Production config integration working!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Production config integration test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def main():
    """Run all delayed data optimization tests"""
    
    logger.info("🚀 Starting Delayed Data Optimization Test Suite")
    logger.info("📊 Testing system optimization for 15-minute delayed data (free Alpaca account)")
    logger.info("=" * 80)
    
    test_results = []
    
    # Test 1: Data mode detection
    logger.info("🧪 Test 1: Data Mode Detection")
    test1_success = test_data_mode_detection()
    test_results.append(("Data Mode Detection", test1_success))
    
    # Test 2: Delayed data configuration
    logger.info("\n🧪 Test 2: Delayed Data Configuration")
    test2_success = test_delayed_data_configuration()
    test_results.append(("Delayed Data Config", test2_success))
    
    # Test 3: Real-time data configuration
    logger.info("\n🧪 Test 3: Real-Time Data Configuration")
    test3_success = test_realtime_data_configuration()
    test_results.append(("Real-Time Data Config", test3_success))
    
    # Test 4: Upgrade recommendation
    logger.info("\n🧪 Test 4: Upgrade Recommendation")
    test4_success = test_upgrade_recommendation()
    test_results.append(("Upgrade Recommendation", test4_success))
    
    # Test 5: Strategy enablement
    logger.info("\n🧪 Test 5: Strategy Enablement")
    test5_success = test_strategy_enablement()
    test_results.append(("Strategy Enablement", test5_success))
    
    # Test 6: Production config integration
    logger.info("\n🧪 Test 6: Production Config Integration")
    test6_success = test_production_config_integration()
    test_results.append(("Production Config Integration", test6_success))
    
    # Summary
    logger.info("\n" + "=" * 80)
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
        logger.info("📊 Delayed data optimization successfully implemented:")
        logger.info("  ⏰ 15-minute cycles (matching data freshness)")
        logger.info("  📈 Swing trading strategies enabled")
        logger.info("  🚫 Intraday scalping strategies disabled")
        logger.info("  💰 Wider stops and targets for delayed execution")
        logger.info("  🚀 Ready for instant upgrade to real-time when profitable")
        return True
    else:
        logger.error("⚠️ SOME TESTS FAILED! Please fix issues before deployment.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)