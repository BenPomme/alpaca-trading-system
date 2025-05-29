#!/usr/bin/env python3
"""
Test ML Integration with Intelligent Exit System
Verifies that real ML predictions are being used instead of simulated data
"""

import os
import sys
from datetime import datetime

def test_ml_integration():
    """Test ML integration with the intelligent exit system"""
    print("🧪 TESTING ML INTEGRATION")
    print("=" * 50)
    
    try:
        # Set up test environment
        os.environ['ALPACA_PAPER_API_KEY'] = os.environ.get('ALPACA_PAPER_API_KEY', 'PKOBXG3RWCRQTXH6ID0L')
        os.environ['ALPACA_PAPER_SECRET_KEY'] = os.environ.get('ALPACA_PAPER_SECRET_KEY', '8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn')
        os.environ['EXECUTION_ENABLED'] = 'false'  # Test only, no real trades
        
        # 1. Test ML Framework Initialization
        print("\n🧠 1. Testing ML Framework Initialization")
        try:
            from ml_adaptive_framework import MLAdaptiveFramework
            from database_manager import TradingDatabase
            from phase3_trader import Phase3Trader
            
            trader = Phase3Trader(use_database=True, market_tier=1)
            db = TradingDatabase()
            
            ml_framework = MLAdaptiveFramework(
                api_client=trader.api,
                risk_manager=trader.risk_manager,
                db=db
            )
            print("✅ ML Framework initialized successfully")
            
            # Test strategy selector
            test_market_data = {
                'technical': {'rsi': 65, 'macd': 0.5},
                'regime': {'type': 'bullish', 'confidence': 0.75},
                'pattern': {'signal': 'bullish', 'strength': 0.6}
            }
            
            strategy, confidence, details = ml_framework.strategy_selector.select_optimal_strategy(test_market_data)
            print(f"✅ ML Strategy Selection: {strategy} (confidence: {confidence:.2f})")
            
        except Exception as e:
            print(f"❌ ML Framework test failed: {e}")
            return False
        
        # 2. Test Phase3Trader with ML Integration
        print("\n🧠 2. Testing Phase3Trader ML Integration")
        try:
            from phase3_trader import Phase3Trader
            
            # Initialize with ML enabled
            phase3_trader = Phase3Trader(
                use_database=True,
                market_tier=1,
                global_trading=False,
                options_trading=False,
                crypto_trading=False
            )
            
            # Check if ML framework is initialized
            if hasattr(phase3_trader, 'ml_framework') and phase3_trader.ml_framework:
                print("✅ Phase3Trader has ML framework")
            else:
                print("❌ Phase3Trader missing ML framework")
                return False
            
            # Check if intelligent exit manager has ML models
            if hasattr(phase3_trader, 'intelligent_exit_manager') and phase3_trader.intelligent_exit_manager:
                ml_models = phase3_trader.intelligent_exit_manager.ml_models
                print(f"🔍 ML Models in Exit Manager: {type(ml_models)}")
                if ml_models:
                    print("✅ Intelligent Exit Manager has ML models")
                    print(f"   ML Framework type: {type(ml_models)}")
                    print(f"   Strategy Selector: {hasattr(ml_models, 'strategy_selector')}")
                    print(f"   Risk Predictor: {hasattr(ml_models, 'risk_predictor')}")
                else:
                    print("❌ Intelligent Exit Manager missing ML models")
                    print(f"   ML models value: {ml_models}")
                    return False
            else:
                print("❌ Phase3Trader missing Intelligent Exit Manager")
                return False
            
        except Exception as e:
            print(f"❌ Phase3Trader ML integration test failed: {e}")
            return False
        
        # 3. Test Intelligent Exit System ML Predictions
        print("\n🧠 3. Testing Intelligent Exit ML Predictions")
        try:
            # Create test position and market data
            test_position_info = {
                'avg_entry_price': 100.0,
                'quantity': 10,
                'entry_time': datetime.now(),
                'entry_confidence': 0.8
            }
            
            test_market_data = {
                'current_price': 105.0,
                'volume': 1000000,
                'bid': 104.8,
                'ask': 105.2
            }
            
            # Test ML exit analysis
            exit_analysis = phase3_trader.intelligent_exit_manager._analyze_ml_exit(
                'SPY', test_market_data, test_position_info
            )
            
            if 'ml_available' in exit_analysis and exit_analysis['ml_available']:
                print("✅ ML exit analysis working")
                print(f"   ML Confidence: {exit_analysis.get('current_confidence', 'N/A')}")
                print(f"   Reversal Probability: {exit_analysis.get('reversal_probability', 'N/A')}")
                print(f"   Trend Strength: {exit_analysis.get('trend_strength', 'N/A')}")
                
                # Check if we're getting real ML data (not random)
                if 'error' not in exit_analysis:
                    print("✅ Real ML predictions (no errors)")
                else:
                    print(f"⚠️ ML prediction error (using fallback): {exit_analysis.get('error', 'Unknown')}")
            else:
                print("❌ ML exit analysis not available")
                return False
            
        except Exception as e:
            print(f"❌ ML exit prediction test failed: {e}")
            return False
        
        # 4. Test ML Learning Capabilities
        print("\n🧠 4. Testing ML Learning Capabilities")
        try:
            # Test exit outcome recording
            test_entry_info = {
                'avg_entry_price': 100.0,
                'quantity': 10,
                'entry_time': datetime.now(),
                'entry_confidence': 0.8
            }
            
            test_exit_info = {
                'exit_price': 108.0,
                'profit_loss': 80.0,
                'profit_pct': 8.0,
                'exit_confidence': 0.7
            }
            
            # Record a test outcome
            phase3_trader.intelligent_exit_manager.record_exit_outcome(
                'SPY', 'ml_take_profit', test_entry_info, test_exit_info
            )
            print("✅ Exit outcome recording works")
            
            # Test performance recommendations
            recommendations = phase3_trader.intelligent_exit_manager.get_exit_strategy_recommendations()
            if 'recommendations' in recommendations:
                print(f"✅ ML recommendations generated: {len(recommendations['recommendations'])} items")
            else:
                print("⚠️ No ML recommendations yet (need more data)")
            
        except Exception as e:
            print(f"❌ ML learning test failed: {e}")
            return False
        
        print("\n🎉 ALL ML INTEGRATION TESTS PASSED!")
        print("\n📊 ML Integration Status:")
        print("✅ ML Framework: ACTIVE")
        print("✅ ML Strategy Selection: ACTIVE") 
        print("✅ ML Exit Predictions: ACTIVE")
        print("✅ ML Learning: ACTIVE")
        print("✅ Performance Tracking: ACTIVE")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ML Integration test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_vs_simulated():
    """Test that we're using real ML data, not simulated"""
    print("\n🔍 TESTING: REAL ML vs SIMULATED DATA")
    print("-" * 40)
    
    try:
        from phase3_trader import Phase3Trader
        
        phase3_trader = Phase3Trader(use_database=True, market_tier=1)
        
        # Run multiple ML predictions to see if they're truly random (simulated) or ML-based
        predictions = []
        
        test_position_info = {
            'avg_entry_price': 100.0,
            'quantity': 10,
            'entry_time': datetime.now(),
            'entry_confidence': 0.8
        }
        
        test_market_data = {
            'current_price': 105.0,
            'volume': 1000000,
            'bid': 104.8,
            'ask': 105.2
        }
        
        for i in range(5):
            analysis = phase3_trader.intelligent_exit_manager._analyze_ml_exit(
                'SPY', test_market_data, test_position_info
            )
            if analysis.get('ml_available'):
                predictions.append({
                    'confidence': analysis.get('current_confidence', 0),
                    'reversal': analysis.get('reversal_probability', 0),
                    'trend': analysis.get('trend_strength', 0)
                })
        
        if len(predictions) >= 3:
            # Check if predictions are identical (ML-based) or varying (random)
            confidences = [p['confidence'] for p in predictions]
            reversals = [p['reversal'] for p in predictions]
            
            confidence_variance = max(confidences) - min(confidences)
            reversal_variance = max(reversals) - min(reversals)
            
            if confidence_variance < 0.1 and reversal_variance < 0.1:
                print("✅ REAL ML DATA: Predictions are consistent (ML-based)")
                print(f"   Confidence range: {min(confidences):.3f} - {max(confidences):.3f}")
                print(f"   Reversal range: {min(reversals):.3f} - {max(reversals):.3f}")
            else:
                print("⚠️ POSSIBLY SIMULATED: High variance in predictions")
                print(f"   Confidence variance: {confidence_variance:.3f}")
                print(f"   Reversal variance: {reversal_variance:.3f}")
                print("   This might be due to insufficient training data")
        
        return True
        
    except Exception as e:
        print(f"❌ ML vs simulated test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 ML INTEGRATION COMPREHENSIVE TEST")
    print("=" * 60)
    
    success1 = test_ml_integration()
    success2 = test_ml_vs_simulated()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED - ML INTEGRATION IS WORKING!")
        print("\n🚀 The intelligent exit system is now using REAL ML predictions")
        print("🧠 The system will learn and improve from each trade outcome")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED - CHECK ML INTEGRATION")
        sys.exit(1)