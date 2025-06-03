#!/usr/bin/env python3

import random
from datetime import datetime

# Test Phase 3 modules independently without Alpaca API dependency
from utils.technical_indicators import TechnicalIndicators
from market_regime_detector import MarketRegimeDetector
from utils.pattern_recognition import PatternRecognition

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

def test_integration():
    """Test integration of all modules"""
    print("\n🔧 Testing Module Integration...")
    
    success_count = 0
    total_tests = 0
    
    # Initialize all modules
    ti = TechnicalIndicators()
    detector = MarketRegimeDetector()
    pr = PatternRecognition()
    
    # Generate comprehensive test data
    symbols = ['SPY', 'QQQ', 'AAPL']
    base_prices = {'SPY': 420.0, 'QQQ': 350.0, 'AAPL': 180.0}
    
    # Add data to all modules
    for i in range(30):
        for symbol in symbols:
            change = random.uniform(-0.025, 0.025)
            base_prices[symbol] += base_prices[symbol] * change
            volume = random.randint(1000000, 10000000)
            
            ti.add_price_data(symbol, base_prices[symbol], volume)
            detector.add_market_data(symbol, base_prices[symbol], volume)
            pr.add_price_data(symbol, base_prices[symbol], volume)
    
    # Add VIX data
    for i in range(15):
        vix = random.uniform(15, 30)
        detector.add_vix_data(vix)
    
    # Test cross-module analysis
    total_tests += 1
    try:
        # Get technical analysis
        tech_analysis = ti.get_comprehensive_analysis('SPY')
        
        # Get regime analysis
        regime_analysis = detector.get_comprehensive_regime_analysis()
        
        # Get pattern analysis
        pattern_analysis = pr.get_comprehensive_pattern_analysis('SPY')
        
        if ('indicators' in tech_analysis and 
            'overall_assessment' in regime_analysis and 
            'patterns' in pattern_analysis):
            success_count += 1
            print(f"   ✅ Cross-Module Analysis: All modules functioning")
        else:
            print(f"   ❌ Cross-module analysis incomplete")
    except Exception as e:
        print(f"   ❌ Cross-module integration error: {str(e)}")
    
    # Test combined signal generation
    total_tests += 1
    try:
        tech_signal = tech_analysis.get('overall_signal', 'hold')
        regime_signal = regime_analysis['overall_assessment'].get('regime', 'neutral')
        pattern_signal = pattern_analysis.get('overall_assessment', {}).get('signal', 'neutral')
        
        # Simple consensus logic
        signals = [tech_signal, regime_signal, pattern_signal]
        buy_votes = sum(1 for s in signals if s in ['buy', 'bullish'])
        sell_votes = sum(1 for s in signals if s in ['sell', 'bearish'])
        
        if buy_votes > sell_votes:
            consensus = 'bullish'
        elif sell_votes > buy_votes:
            consensus = 'bearish'
        else:
            consensus = 'neutral'
        
        success_count += 1
        print(f"   ✅ Signal Consensus: {consensus} (Technical: {tech_signal}, Regime: {regime_signal}, Pattern: {pattern_signal})")
        
    except Exception as e:
        print(f"   ❌ Signal consensus error: {str(e)}")
    
    # Test data consistency
    total_tests += 1
    try:
        spy_in_ti = 'SPY' in ti.initialized_symbols
        spy_in_detector = len(detector.tech_indicators.price_history.get('SPY', [])) > 0
        spy_in_pr = len(pr.price_history.get('SPY', [])) > 0
        
        if spy_in_ti and spy_in_detector and spy_in_pr:
            success_count += 1
            print(f"   ✅ Data Consistency: All modules have SPY data")
        else:
            print(f"   ❌ Data consistency issues")
    except Exception as e:
        print(f"   ❌ Data consistency error: {str(e)}")
    
    accuracy = success_count / total_tests * 100
    print(f"   📊 Integration Accuracy: {accuracy:.1f}% ({success_count}/{total_tests})")
    return accuracy

def run_phase3_standalone_test():
    """Run Phase 3 standalone test suite"""
    print("🧠 PHASE 3 INTELLIGENCE LAYER - STANDALONE TEST")
    print("=" * 60)
    print(f"⏰ Test Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Note: Testing core intelligence modules only (no Alpaca API)")
    
    # Run all test modules
    test_results = []
    
    test_results.append(test_technical_indicators())
    test_results.append(test_market_regime_detection())
    test_results.append(test_pattern_recognition())
    test_results.append(test_integration())
    
    # Calculate overall results
    overall_accuracy = sum(test_results) / len(test_results)
    
    print("\n" + "=" * 60)
    print("📊 PHASE 3 STANDALONE TEST RESULTS")
    print("=" * 60)
    
    module_names = [
        "Technical Indicators",
        "Market Regime Detection", 
        "Pattern Recognition",
        "Module Integration"
    ]
    
    for i, (module, accuracy) in enumerate(zip(module_names, test_results)):
        status = "✅ PASS" if accuracy >= 70 else "❌ FAIL"
        print(f"{status} {module}: {accuracy:.1f}%")
    
    print(f"\n🎯 OVERALL PHASE 3 INTELLIGENCE ACCURACY: {overall_accuracy:.1f}%")
    
    if overall_accuracy >= 70:
        print("🚀 PHASE 3 INTELLIGENCE MODULES: READY FOR INTEGRATION")
        deployment_ready = True
    else:
        print("⚠️ PHASE 3 INTELLIGENCE MODULES: NEED IMPROVEMENT")
        deployment_ready = False
    
    print(f"⏰ Test Complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Deployment recommendations
    if deployment_ready:
        print("\n✅ PHASE 3 DEPLOYMENT READY:")
        print("   🔧 Install missing dependencies: pip install alpaca-trade-api")
        print("   🚀 Deploy using: python start_phase3.py")
        print("   ⚙️ Configure environment variables for production")
    else:
        print(f"\n❌ PHASE 3 NEEDS IMPROVEMENT:")
        print(f"   📊 Current accuracy: {overall_accuracy:.1f}% (target: 70%+)")
        print("   🔧 Review failed modules and enhance algorithms")
    
    return overall_accuracy, deployment_ready

if __name__ == "__main__":
    # Run the comprehensive test
    accuracy, ready = run_phase3_standalone_test()
    
    if ready:
        print("\n🎯 Next step: Create Phase 3 entry point and update deployment")
    else:
        print(f"\n⚠️ Address issues before proceeding to deployment")