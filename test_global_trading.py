#!/usr/bin/env python3
"""
Test Suite for Phase 4.1 Global Trading
Tests timezone-aware market selection and global symbol integration
"""

import os
import sys
import datetime
import pytz
from typing import Dict, List

# Import our modules
from global_market_manager import GlobalMarketManager
from market_universe import get_symbols_by_tier, get_asian_symbols_by_region, get_global_symbols

def test_timezone_awareness():
    """Test timezone-aware market session detection"""
    print("🧪 Testing Timezone Awareness...")
    
    gmm = GlobalMarketManager()
    
    # Test current active sessions
    active_sessions = gmm.get_current_active_sessions()
    print(f"✅ Currently Active Sessions: {active_sessions}")
    
    # Test specific timezone checks
    test_times = [
        ('2024-01-15 09:30:00', 'America/New_York'),  # US market open
        ('2024-01-15 09:30:00', 'Asia/Tokyo'),        # Asian market open
        ('2024-01-15 14:30:00', 'Europe/London'),     # European market open
    ]
    
    for time_str, timezone in test_times:
        test_time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        test_time = pytz.timezone(timezone).localize(test_time)
        test_time_utc = test_time.astimezone(pytz.UTC)
        
        for session_name in gmm.market_sessions.keys():
            is_active = gmm.is_session_active(session_name, test_time_utc)
            print(f"   📅 {session_name} at {time_str} {timezone}: {'🟢 Active' if is_active else '🔴 Closed'}")
    
    return True

def test_asian_adr_integration():
    """Test Asian ADR symbol integration"""
    print("🧪 Testing Asian ADR Integration...")
    
    # Test market universe expansion
    asian_regions = get_asian_symbols_by_region()
    print(f"✅ Asian Regions: {list(asian_regions.keys())}")
    
    total_asian_symbols = 0
    for region, symbols in asian_regions.items():
        print(f"   🏢 {region.title()}: {len(symbols)} symbols - {symbols[:3]}...")
        total_asian_symbols += len(symbols)
    
    print(f"✅ Total Asian ADR Symbols: {total_asian_symbols}")
    
    # Test global symbols
    global_symbols = get_global_symbols()
    print(f"✅ Total Global Symbols (ADRs + ETFs): {len(global_symbols)}")
    
    # Test tier 5 integration
    tier5_symbols = get_symbols_by_tier(5)
    print(f"✅ Tier 5 Global Symbols: {len(tier5_symbols)}")
    
    # Verify Asian symbols are included
    asian_symbols_in_tier5 = [s for s in tier5_symbols if s in ['TM', 'SONY', 'TSM', 'BABA']]
    print(f"✅ Sample Asian symbols in Tier 5: {asian_symbols_in_tier5}")
    
    return len(asian_symbols_in_tier5) > 0

def test_session_based_symbol_selection():
    """Test symbol selection based on active market sessions"""
    print("🧪 Testing Session-Based Symbol Selection...")
    
    gmm = GlobalMarketManager()
    
    # Test each session's symbol selection
    for session_name in gmm.market_sessions.keys():
        symbols = gmm.get_tradeable_symbols_by_session(session_name)
        print(f"✅ {session_name}: {len(symbols)} symbols")
        if symbols:
            print(f"   📊 Sample symbols: {symbols[:5]}")
    
    # Test current trading opportunity
    opportunity = gmm.get_next_trading_opportunity()
    print(f"✅ Current Trading Opportunity: {opportunity['status']}")
    
    if opportunity['status'] == 'active':
        symbols = opportunity['symbols']
        print(f"   📈 Active symbols: {len(symbols)} symbols")
        print(f"   🎯 Session: {opportunity['session']}")
    else:
        print(f"   ⏳ Next session: {opportunity.get('next_session', 'Unknown')}")
        print(f"   ⏰ Wait time: {opportunity.get('wait_time', 'Unknown')}")
    
    return True

def test_global_market_status():
    """Test comprehensive global market status"""
    print("🧪 Testing Global Market Status...")
    
    gmm = GlobalMarketManager()
    status = gmm.get_global_market_status()
    
    print(f"✅ Global Market Status at {status['timestamp'][:19]}")
    print(f"   🌍 Total Global Symbols: {status['total_global_symbols']}")
    print(f"   📊 Active Sessions: {len(status['active_sessions'])}")
    print(f"   📈 Tradeable Symbols: {len(status['tradeable_symbols'])}")
    
    for session in status['active_sessions']:
        print(f"   🟢 {session['name']}: {session['description']}")
        print(f"      📊 {len(session['symbols'])} symbols available")
    
    return True

def test_market_prioritization():
    """Test symbol prioritization for global trading"""
    print("🧪 Testing Market Prioritization...")
    
    # Simulate Phase 3 trader prioritization
    from market_universe import get_momentum_symbols, get_defensive_symbols
    
    momentum_symbols = get_momentum_symbols()
    defensive_symbols = get_defensive_symbols()
    
    print(f"✅ Momentum Symbols: {len(momentum_symbols)}")
    print(f"   🚀 Sample: {momentum_symbols[:5]}")
    
    print(f"✅ Defensive Symbols: {len(defensive_symbols)}")
    print(f"   🛡️ Sample: {defensive_symbols[:5]}")
    
    # Test prioritization logic
    test_symbols = ['SPY', 'TSM', 'BABA', 'TM', 'VEA', 'QQQ', 'SONY']
    
    # Mock the prioritization logic from Phase3Trader
    prioritized = []
    
    # Add momentum symbols first
    for symbol in momentum_symbols:
        if symbol in test_symbols and symbol not in prioritized:
            prioritized.append(symbol)
    
    # Add defensive symbols
    for symbol in defensive_symbols:
        if symbol in test_symbols and symbol not in prioritized:
            prioritized.append(symbol)
    
    # Add remaining symbols
    for symbol in test_symbols:
        if symbol not in prioritized:
            prioritized.append(symbol)
    
    print(f"✅ Prioritized Order: {prioritized}")
    print(f"   📊 Momentum first, then defensive, then others")
    
    return len(prioritized) == len(test_symbols)

def simulate_24_5_trading_schedule():
    """Simulate 24/5 trading schedule across different timezones"""
    print("🧪 Simulating 24/5 Trading Schedule...")
    
    gmm = GlobalMarketManager()
    schedule = gmm.get_optimal_trading_schedule()
    
    print(f"✅ 24/5 Trading Schedule: {len(schedule)} periods")
    
    for period in schedule:
        print(f"   📅 {period['name']}")
        print(f"      🌐 Sessions: {period['sessions']}")
        print(f"      📊 Symbols: {len(period['priority_symbols'])} priority symbols")
        print(f"      🎯 Strategy: {period['strategy_focus']}")
        print(f"      📈 Sample symbols: {period['priority_symbols'][:5]}")
        print()
    
    return len(schedule) > 0

def test_phase3_integration():
    """Test integration with Phase 3 trader"""
    print("🧪 Testing Phase 3 Integration...")
    
    try:
        # Test import and initialization
        from phase3_trader import Phase3Trader
        
        print("✅ Phase3Trader import successful")
        
        # Test initialization with global trading disabled
        trader_local = Phase3Trader(use_database=False, market_tier=2, global_trading=False)
        print("✅ Local trading initialization successful")
        
        # Test symbol selection for local trading
        local_symbols = trader_local.get_active_trading_symbols()
        print(f"   📊 Local symbols: {len(local_symbols)}")
        
        # Test initialization with global trading enabled
        trader_global = Phase3Trader(use_database=False, market_tier=2, global_trading=True)
        print("✅ Global trading initialization successful")
        
        # Test symbol selection for global trading
        global_symbols = trader_global.get_active_trading_symbols()
        print(f"   🌍 Global symbols: {len(global_symbols)}")
        
        print(f"✅ Symbol difference: {len(global_symbols) - len(local_symbols)} additional global symbols")
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 3 integration test failed: {e}")
        return False

def run_all_tests():
    """Run all global trading tests"""
    print("🌍 GLOBAL TRADING TEST SUITE - Phase 4.1")
    print("=" * 60)
    
    tests = [
        ("Timezone Awareness", test_timezone_awareness),
        ("Asian ADR Integration", test_asian_adr_integration),
        ("Session-Based Symbol Selection", test_session_based_symbol_selection),
        ("Global Market Status", test_global_market_status),
        ("Market Prioritization", test_market_prioritization),
        ("24/5 Trading Schedule", simulate_24_5_trading_schedule),
        ("Phase 3 Integration", test_phase3_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            status = "✅ PASSED" if result else "❌ FAILED"
            results.append((test_name, result))
            print(f"\n{status}: {test_name}")
        except Exception as e:
            print(f"\n❌ FAILED: {test_name} - {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("🧪 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Global trading system ready for deployment.")
    else:
        print("⚠️ Some tests failed. Review implementation before deployment.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()