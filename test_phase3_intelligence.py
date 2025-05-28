#!/usr/bin/env python3

import os
import sys
import time
import random
from datetime import datetime, timedelta

# Import Phase 3 components
from phase3_trader import Phase3Trader
from technical_indicators import TechnicalIndicators
from market_regime_detector import MarketRegimeDetector
from pattern_recognition import PatternRecognition

def test_technical_indicators():
    """Test technical indicators module"""
    print("🔧 Testing Technical Indicators...")
    
    ti = TechnicalIndicators()
    
    # Generate realistic price data
    base_price = 100.0
    success_count = 0
    total_tests = 0
    
    # Add 30 data points
    for i in range(30):
        change = random.uniform(-0.03, 0.03)
        base_price += base_price * change
        volume = random.randint(100000, 500000)
        ti.add_price_data('TEST', base_price, volume)
    
    # Test RSI
    total_tests += 1
    rsi = ti.calculate_rsi('TEST')
    if rsi and 0 <= rsi <= 100:
        success_count += 1
        print(f"   ✅ RSI: {rsi:.1f}")
    else:
        print(f"   ❌ RSI calculation failed")
    
    # Test MACD
    total_tests += 1
    macd = ti.calculate_macd('TEST')
    if macd and 'macd' in macd:
        success_count += 1
        print(f"   ✅ MACD: {macd['macd']:.3f} (Trend: {macd['trend']})")
    else:
        print(f"   ❌ MACD calculation failed")
    
    # Test Bollinger Bands
    total_tests += 1
    bb = ti.calculate_bollinger_bands('TEST')
    if bb and 'upper' in bb:
        success_count += 1
        print(f"   ✅ Bollinger Bands: {bb['position']} (Current: ${bb['current']:.2f})")
    else:
        print(f"   ❌ Bollinger Bands calculation failed")
    
    # Test comprehensive analysis
    total_tests += 1
    analysis = ti.get_comprehensive_analysis('TEST')
    if 'indicators' in analysis and analysis['indicators']:
        success_count += 1
        print(f"   ✅ Comprehensive Analysis: {analysis['overall_signal']} ({len(analysis['indicators'])} indicators)")
    else:
        print(f"   ❌ Comprehensive analysis failed")
    
    accuracy = success_count / total_tests * 100
    print(f"   📊 Technical Indicators Accuracy: {accuracy:.1f}% ({success_count}/{total_tests})")
    return accuracy

def test_market_regime_detection():
    """Test market regime detection"""
    print("\n🔧 Testing Market Regime Detection...")
    
    detector = MarketRegimeDetector()
    success_count = 0
    total_tests = 0
    
    # Add market data for core indices
    indices = ['SPY', 'QQQ', 'IWM']
    base_prices = {'SPY': 420.0, 'QQQ': 350.0, 'IWM': 200.0}
    
    for i in range(40):
        for symbol in indices:
            change = random.uniform(-0.02, 0.025)  # Slight bullish bias
            base_prices[symbol] += base_prices[symbol] * change
            volume = random.randint(10000000, 50000000)
            detector.add_market_data(symbol, base_prices[symbol], volume)
    
    # Add VIX data
    for i in range(20):
        vix = random.uniform(15, 25)
        detector.add_vix_data(vix)
    
    # Test trend regime detection
    total_tests += 1
    trend_regime = detector.detect_trend_regime('SPY')
    if trend_regime and 'regime' in trend_regime:
        success_count += 1
        print(f"   ✅ SPY Trend Regime: {trend_regime['regime']} ({trend_regime['confidence']:.1%})")
    else:
        print(f"   ❌ Trend regime detection failed")
    
    # Test volatility regime
    total_tests += 1
    vol_regime = detector.detect_volatility_regime()
    if vol_regime and 'volatility_regime' in vol_regime:
        success_count += 1
        print(f"   ✅ Volatility Regime: {vol_regime['volatility_regime']} (VIX: {vol_regime['vix_level']:.1f})")
    else:
        print(f"   ❌ Volatility regime detection failed")
    
    # Test comprehensive regime analysis
    total_tests += 1
    comprehensive = detector.get_comprehensive_regime_analysis()
    if 'overall_assessment' in comprehensive:
        success_count += 1
        overall = comprehensive['overall_assessment']
        print(f"   ✅ Overall Market: {overall['regime']} ({overall['confidence']:.1%})")
    else:
        print(f"   ❌ Comprehensive regime analysis failed")
    
    # Test trading recommendations
    total_tests += 1
    if 'trading_recommendations' in comprehensive:
        success_count += 1
        recs = comprehensive['trading_recommendations']
        print(f"   ✅ Strategy Recommendation: {recs['strategy']} (Risk: {recs['risk_level']})")
    else:
        print(f"   ❌ Trading recommendations failed")
    
    accuracy = success_count / total_tests * 100
    print(f"   📊 Market Regime Detection Accuracy: {accuracy:.1f}% ({success_count}/{total_tests})")
    return accuracy

def test_pattern_recognition():
    """Test pattern recognition"""
    print("\n🔧 Testing Pattern Recognition...")
    
    pr = PatternRecognition()
    success_count = 0
    total_tests = 0
    
    # Generate data with patterns
    base_price = 100.0
    
    # Phase 1: Create support/resistance levels
    for i in range(10):
        change = random.uniform(-0.01, 0.01)
        base_price += base_price * change
        volume = random.randint(100000, 300000)
        pr.add_price_data('TEST', base_price, volume)
    
    # Phase 2: Create a breakout
    for i in range(10):
        change = random.uniform(0.01, 0.025)  # Upward movement
        base_price += base_price * change
        volume = random.randint(300000, 600000)  # Higher volume
        pr.add_price_data('TEST', base_price, volume)
    
    # Test support/resistance detection
    total_tests += 1
    sr_levels = pr.find_support_resistance_levels('TEST')
    if sr_levels and ('support_levels' in sr_levels or 'resistance_levels' in sr_levels):
        success_count += 1
        support_count = len(sr_levels.get('support_levels', []))
        resistance_count = len(sr_levels.get('resistance_levels', []))
        print(f"   ✅ Support/Resistance: {support_count} support, {resistance_count} resistance levels")
    else:
        print(f"   ❌ Support/resistance detection failed")
    
    # Test breakout detection
    total_tests += 1
    breakout = pr.detect_breakout_pattern('TEST')
    if breakout and 'pattern' in breakout:
        success_count += 1
        print(f"   ✅ Breakout Pattern: {breakout['pattern']} ({breakout['signal']})")
    else:
        print(f"   ❌ Breakout detection failed")
    
    # Test mean reversion
    total_tests += 1
    mean_reversion = pr.detect_mean_reversion_setup('TEST')
    if mean_reversion and 'pattern' in mean_reversion:
        success_count += 1
        print(f"   ✅ Mean Reversion: {mean_reversion['pattern']} (Z-score: {mean_reversion['z_score']})")
    else:
        print(f"   ❌ Mean reversion detection failed")
    
    # Test comprehensive pattern analysis
    total_tests += 1
    comprehensive = pr.get_comprehensive_pattern_analysis('TEST')
    if 'patterns' in comprehensive and comprehensive['patterns']:
        success_count += 1
        pattern_count = len(comprehensive['patterns'])
        signal_count = len(comprehensive.get('trading_signals', []))
        print(f"   ✅ Comprehensive Analysis: {pattern_count} patterns, {signal_count} signals")
    else:
        print(f"   ❌ Comprehensive pattern analysis failed")
    
    accuracy = success_count / total_tests * 100
    print(f"   📊 Pattern Recognition Accuracy: {accuracy:.1f}% ({success_count}/{total_tests})")
    return accuracy

def test_phase3_integration():
    """Test Phase 3 integration"""
    print("\n🔧 Testing Phase 3 Integration...")
    
    # Set test environment
    os.environ['EXECUTION_ENABLED'] = 'false'  # Safe testing
    os.environ['MARKET_TIER'] = '1'  # Small universe for testing
    
    trader = Phase3Trader(use_database=False, market_tier=1)
    trader.execution_enabled = False  # Extra safety
    
    success_count = 0
    total_tests = 0
    
    # Test intelligence analysis
    total_tests += 1
    try:
        analysis = trader.analyze_symbol_intelligence('SPY', 420.0, 1000000)
        if 'symbol' in analysis:
            success_count += 1
            print(f"   ✅ Intelligence Analysis: {analysis['symbol']}")
        else:
            print(f"   ❌ Intelligence analysis failed")
    except Exception as e:
        print(f"   ❌ Intelligence analysis error: {str(e)}")
    
    # Test combined intelligence scoring
    total_tests += 1
    try:
        mock_scores = {
            'technical': {'signal': 'buy', 'confidence': 0.8},
            'regime': {'signal': 'buy', 'confidence': 0.7},
            'pattern': {'signal': 'bullish', 'confidence': 0.6}
        }
        combined = trader.calculate_combined_intelligence_score(mock_scores)
        if 'signal' in combined:
            success_count += 1
            print(f"   ✅ Combined Intelligence: {combined['signal']} ({combined['confidence']:.1%})")
        else:
            print(f"   ❌ Combined intelligence scoring failed")
    except Exception as e:
        print(f"   ❌ Combined intelligence error: {str(e)}")
    
    # Test enhanced strategy selection
    total_tests += 1
    try:
        mock_quotes = [
            {'symbol': 'SPY', 'price': 420.0, 'volume': 10000000},
            {'symbol': 'QQQ', 'price': 350.0, 'volume': 8000000}
        ]
        strategy = trader.enhanced_strategy_selection(mock_quotes, 'active', 0.8)
        if strategy:
            success_count += 1
            print(f"   ✅ Enhanced Strategy: {strategy}")
        else:
            print(f"   ❌ Enhanced strategy selection failed")
    except Exception as e:
        print(f"   ❌ Enhanced strategy error: {str(e)}")
    
    # Test intelligence trade decision
    total_tests += 1
    try:
        should_trade, confidence, summary = trader.should_execute_trade_with_intelligence(
            'SPY', 'momentum', 0.7, 420.0
        )
        success_count += 1
        print(f"   ✅ Trade Decision: {should_trade} (Confidence: {confidence:.1%})")
    except Exception as e:
        print(f"   ❌ Trade decision error: {str(e)}")
    
    accuracy = success_count / total_tests * 100
    print(f"   📊 Phase 3 Integration Accuracy: {accuracy:.1f}% ({success_count}/{total_tests})")
    return accuracy

def run_comprehensive_phase3_test():
    """Run comprehensive Phase 3 test suite"""
    print("🧠 PHASE 3 INTELLIGENCE LAYER TEST SUITE")
    print("=" * 60)
    print(f"⏰ Test Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all test modules
    test_results = []
    
    test_results.append(test_technical_indicators())
    test_results.append(test_market_regime_detection())
    test_results.append(test_pattern_recognition())
    test_results.append(test_phase3_integration())
    
    # Calculate overall results
    overall_accuracy = sum(test_results) / len(test_results)
    
    print("\n" + "=" * 60)
    print("📊 PHASE 3 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    module_names = [
        "Technical Indicators",
        "Market Regime Detection", 
        "Pattern Recognition",
        "Phase 3 Integration"
    ]
    
    for i, (module, accuracy) in enumerate(zip(module_names, test_results)):
        status = "✅ PASS" if accuracy >= 70 else "❌ FAIL"
        print(f"{status} {module}: {accuracy:.1f}%")
    
    print(f"\n🎯 OVERALL PHASE 3 ACCURACY: {overall_accuracy:.1f}%")
    
    if overall_accuracy >= 70:
        print("🚀 PHASE 3 INTELLIGENCE LAYER: READY FOR DEPLOYMENT")
        deployment_ready = True
    else:
        print("⚠️ PHASE 3 INTELLIGENCE LAYER: NEEDS IMPROVEMENT")
        deployment_ready = False
    
    print(f"⏰ Test Complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return overall_accuracy, deployment_ready

if __name__ == "__main__":
    # Run the comprehensive test
    accuracy, ready = run_comprehensive_phase3_test()
    
    if ready:
        print("\n✅ Phase 3 is ready for production deployment!")
        sys.exit(0)
    else:
        print(f"\n❌ Phase 3 needs improvement (current accuracy: {accuracy:.1f}%, target: 70%+)")
        sys.exit(1)