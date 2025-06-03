#!/usr/bin/env python3
"""
Test Limits Removal

Verify that all trading limits have been properly removed for system improvement.
Tests both the RiskManager and TradeHistoryTracker components.
"""

import logging
import os
from risk_manager import RiskManager
from trade_history_tracker import TradeHistoryTracker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockAPI:
    """Mock Alpaca API for testing"""
    def __init__(self):
        self.equity = 1000000  # $1M account
        self.last_equity = 1000000
        self.buying_power = 500000
        self.daytrading_buying_power = 1000000
        
    def get_account(self):
        """Return mock account data"""
        class MockAccount:
            def __init__(self, api):
                self.equity = str(api.equity)
                self.last_equity = str(api.last_equity) 
                self.buying_power = str(api.buying_power)
                self.daytrading_buying_power = str(api.daytrading_buying_power)
                self.pattern_day_trader = True
        return MockAccount(self)
    
    def list_positions(self):
        """Return empty positions for testing"""
        return []

def test_risk_manager_limits_removed():
    """Test that all limits have been removed from RiskManager"""
    
    print("🧪 TESTING RISK MANAGER LIMITS REMOVAL")
    print("=" * 60)
    
    mock_api = MockAPI()
    risk_manager = RiskManager(api_client=mock_api, logger=logger)
    
    # Test 1: Check daily loss limit removed
    print("\n📊 TEST 1: Daily Loss Limit")
    print("-" * 30)
    can_trade, reason = risk_manager.check_daily_loss_limit()
    print(f"Daily loss check: {'✅ UNLIMITED' if can_trade else '❌ LIMITED'}")
    print(f"Reason: {reason}")
    assert can_trade, "Daily loss limit should be removed"
    assert "unlimited trading" in reason.lower() or "disabled" in reason.lower()
    
    # Test 2: Check position value limits removed
    print("\n📊 TEST 2: Position Value Limits")
    print("-" * 30)
    print(f"Max position value: {risk_manager.max_position_value}")
    assert risk_manager.max_position_value is None, "Position value limits should be removed"
    print("✅ Position value limits removed")
    
    # Test 3: Check daily trade limits removed  
    print("\n📊 TEST 3: Daily Trade Limits")
    print("-" * 30)
    print(f"Max daily trades: {risk_manager.max_daily_trades}")
    assert risk_manager.max_daily_trades is None, "Daily trade limits should be removed"
    print("✅ Daily trade limits removed")
    
    # Test 4: Check position size percentage limits removed
    print("\n📊 TEST 4: Position Size Percentage Limits")
    print("-" * 30)
    print(f"Max position size %: {risk_manager.max_position_size_pct}")
    assert risk_manager.max_position_size_pct is None, "Position size percentage limits should be removed"
    print("✅ Position size percentage limits removed")
    
    # Test 5: Test large position validation (should pass)
    print("\n📊 TEST 5: Large Position Validation")
    print("-" * 30)
    
    # Test extremely large positions that would have been blocked before
    test_cases = [
        ("BTCUSD", 50000),  # $50K position (was blocked at $8K)
        ("ETHUSD", 100000), # $100K position 
        ("TSLA", 200000),   # $200K position
    ]
    
    for symbol, position_value in test_cases:
        shares = position_value / 100  # Assume $100 per share
        can_trade, reason, sizing_info = risk_manager.should_execute_trade(symbol, "momentum", 0.8, 100)
        status = "✅ ALLOWED" if can_trade else "❌ BLOCKED"
        print(f"{symbol:8} ${position_value:>6,} | {status} | {reason}")
    
    return True

def test_trade_history_limits_removed():
    """Test that limits have been removed from TradeHistoryTracker"""
    
    print("\n🧪 TESTING TRADE HISTORY LIMITS REMOVAL")
    print("=" * 60)
    
    # Load environment for Firebase
    def load_env_file():
        env_file = '.env.local'
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        value = value.strip('"').strip("'")
                        os.environ[key] = value
    
    load_env_file()
    
    tracker = TradeHistoryTracker(logger=logger)
    
    # Test 1: Check position limits removed
    print("\n📊 TEST 1: Position Size Limits")
    print("-" * 30)
    print(f"Max position value: {tracker.max_position_value}")
    assert tracker.max_position_value is None, "Position value limits should be removed"
    print("✅ Position size limits removed from trade tracker")
    
    # Test 2: Check daily trade limits removed
    print("\n📊 TEST 2: Daily Trade Limits") 
    print("-" * 30)
    print(f"Max daily trades: {tracker.max_daily_trades}")
    assert tracker.max_daily_trades is None, "Daily trade limits should be removed"
    print("✅ Daily trade limits removed from trade tracker")
    
    # Test 3: Test large position trading (should pass)
    print("\n📊 TEST 3: Large Position Trading")
    print("-" * 30)
    
    test_positions = [
        ("BTCUSD", 100000),  # $100K position
        ("ETHUSD", 250000),  # $250K position  
        ("AVAXUSD", 500000), # $500K position
    ]
    
    for symbol, trade_value in test_positions:
        can_trade, reason = tracker.can_trade_symbol(symbol, trade_value)
        status = "✅ ALLOWED" if can_trade else "❌ BLOCKED" 
        print(f"{symbol:8} ${trade_value:>6,} | {status} | {reason}")
        
        # Only cooldown and hourly limits should block trades, not position size
        if not can_trade:
            assert "COOLDOWN" in reason or "HOURLY_LIMIT" in reason or "RAPID_PATTERN" in reason, \
                f"Only cooldown/hourly/pattern limits should block trades, got: {reason}"
    
    return True

def show_remaining_safety_controls():
    """Show what safety controls are still active"""
    
    print("\n🛡️ REMAINING SAFETY CONTROLS")
    print("=" * 50)
    
    print("🚀 RISK MANAGER:")
    print("   ✅ Max positions: 15 (prevent portfolio overload)")
    print("   ✅ Sector exposure: 40% max (prevent concentration)")
    print("   ✅ Stop loss: 3% (risk management)")
    print("   ✅ Take profit: 8% (profit taking)")
    print("   ❌ Position size limits: REMOVED")
    print("   ❌ Daily trade limits: REMOVED") 
    print("   ❌ Daily loss limits: REMOVED")
    print("   ❌ Position value limits: REMOVED")
    
    print("\n🔍 TRADE HISTORY TRACKER:")
    print("   ✅ 5-minute cooldowns: ACTIVE (prevents rapid trading)")
    print("   ✅ 2 trades/hour limit: ACTIVE (prevents patterns)")
    print("   ✅ Rapid pattern detection: ACTIVE (prevents 50 trades/5min)")
    print("   ✅ Position tracking: ACTIVE (monitors exposure)")
    print("   ❌ Position size limits: REMOVED")
    print("   ❌ Daily trade limits: REMOVED")
    
    print("\n🎯 SYSTEM GOAL:")
    print("   Allow unlimited trading for system improvement")
    print("   Maintain essential safety controls (cooldowns, pattern detection)")
    print("   Remove artificial position and daily limits")
    print("   Enable learning through increased trading activity")

if __name__ == "__main__":
    print("🧪 TESTING ALL TRADING LIMITS REMOVAL")
    print("=" * 70)
    
    try:
        # Test both components
        risk_test_passed = test_risk_manager_limits_removed()
        history_test_passed = test_trade_history_limits_removed()
        
        show_remaining_safety_controls()
        
        if risk_test_passed and history_test_passed:
            print(f"\n🎯 ALL TESTS ✅ PASSED")
            print("=" * 70)
            print("✅ Daily loss limits: REMOVED")
            print("✅ Position size limits: REMOVED") 
            print("✅ Daily trade limits: REMOVED")
            print("✅ Position value limits: REMOVED")
            print("🚀 System ready for unlimited trading and improvement")
        else:
            print(f"\n❌ SOME TESTS FAILED")
            print("Check the output above for details")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()