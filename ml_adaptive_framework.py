#!/usr/bin/env python3
"""
ML Adaptive Framework - Phase 5.3
Integrates ML strategy selection and risk prediction with Phase 4 system
"""

import os
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from ml_strategy_selector import MLStrategySelector
from ml_risk_predictor import MLRiskPredictor
from database_manager import TradingDatabase
from firebase_database import FirebaseDatabase

class MLAdaptiveFramework:
    """
    ML-enhanced adaptive trading framework
    Integrates with Phase 4 system for intelligent decision making
    """
    
    def __init__(self, api_client, risk_manager, db: TradingDatabase = None, firebase_db: FirebaseDatabase = None):
        self.api = api_client
        self.risk_manager = risk_manager
        self.db = db
        self.firebase_db = firebase_db
        
        # Initialize ML components with Firebase support
        self.strategy_selector = MLStrategySelector(db, firebase_db)
        self.risk_predictor = MLRiskPredictor(db, firebase_db)
        
        # ML configuration
        self.ml_enabled = True
        self.learning_rate = 0.1  # How quickly to adapt to new information
        self.min_trades_for_learning = 5  # Minimum trades before ML kicks in
        
        # Performance tracking
        self.ml_performance = {
            'total_trades': 0,
            'ml_trades': 0,
            'ml_wins': 0,
            'traditional_trades': 0,
            'traditional_wins': 0
        }
        
        # Integration flags
        self.use_ml_strategy_selection = True
        self.use_ml_position_sizing = True
        self.use_ml_risk_prediction = True
        
        print("🧠 ML Adaptive Framework initialized")
        print(f"   🎯 ML Strategy Selection: {'✅' if self.use_ml_strategy_selection else '❌'}")
        print(f"   📊 ML Position Sizing: {'✅' if self.use_ml_position_sizing else '❌'}")
        print(f"   🛡️ ML Risk Prediction: {'✅' if self.use_ml_risk_prediction else '❌'}")
        print(f"   🔥 Firebase Persistence: {'✅' if self.firebase_db and self.firebase_db.is_connected() else '❌'}")
        
        # Load ML model states from Firebase on startup
        self.load_ml_states_from_firebase()
    
    def load_ml_states_from_firebase(self):
        """Load ML model states from Firebase for persistence across deployments"""
        try:
            if not self.firebase_db or not self.firebase_db.is_connected():
                print("⚠️ Firebase not available - ML states will not persist")
                return
            
            # Load strategy selector model state
            strategy_state = self.firebase_db.get_ml_model_state('strategy_selector')
            if strategy_state:
                self.strategy_selector.load_state(strategy_state)
                print("✅ ML Strategy Selector state loaded from Firebase")
            
            # Load risk predictor model state
            risk_state = self.firebase_db.get_ml_model_state('risk_predictor')
            if risk_state:
                self.risk_predictor.load_state(risk_state)
                print("✅ ML Risk Predictor state loaded from Firebase")
            
            # Load performance metrics
            performance_state = self.firebase_db.get_ml_model_state('ml_performance')
            if performance_state:
                self.ml_performance.update(performance_state.get('performance', {}))
                print("✅ ML Performance metrics loaded from Firebase")
            
        except Exception as e:
            print(f"❌ Error loading ML states from Firebase: {e}")
    
    def save_ml_states_to_firebase(self):
        """Save ML model states to Firebase for persistence"""
        try:
            if not self.firebase_db or not self.firebase_db.is_connected():
                return
            
            # Save strategy selector model state
            if hasattr(self.strategy_selector, 'get_state'):
                strategy_state = self.strategy_selector.get_state()
                self.firebase_db.save_ml_model_state('strategy_selector', strategy_state)
            
            # Save risk predictor model state
            if hasattr(self.risk_predictor, 'get_state'):
                risk_state = self.risk_predictor.get_state()
                self.firebase_db.save_ml_model_state('risk_predictor', risk_state)
            
            # Save performance metrics
            performance_data = {
                'performance': self.ml_performance,
                'last_updated': datetime.now(),
                'total_trades': self.ml_performance['total_trades']
            }
            self.firebase_db.save_ml_model_state('ml_performance', performance_data)
            
            print("🔥 ML states saved to Firebase")
            
        except Exception as e:
            print(f"❌ Error saving ML states to Firebase: {e}")
    
    def enhance_market_analysis(self, market_regime: str, regime_confidence: float,
                               technical_analysis: Dict, pattern_analysis: Dict) -> Dict:
        """
        Enhance Phase 4 market analysis with ML insights
        """
        enhanced_analysis = {
            'original_regime': market_regime,
            'original_confidence': regime_confidence,
            'ml_enhanced': False
        }
        
        if not self.ml_enabled:
            return enhanced_analysis
        
        # Prepare market data for ML analysis
        market_data = {
            'technical': technical_analysis,
            'regime': {
                'type': market_regime,
                'confidence': regime_confidence,
                'strength': regime_confidence
            },
            'pattern': pattern_analysis
        }
        
        # Get ML strategy recommendation
        if self.use_ml_strategy_selection:
            ml_strategy, ml_confidence, ml_details = self.strategy_selector.select_optimal_strategy(market_data)
            
            enhanced_analysis.update({
                'ml_strategy': ml_strategy,
                'ml_confidence': ml_confidence,
                'ml_details': ml_details,
                'ml_enhanced': True
            })
            
            # Blend traditional and ML confidence
            blended_confidence = (regime_confidence * 0.6) + (ml_confidence * 0.4)
            enhanced_analysis['blended_confidence'] = blended_confidence
            
            print(f"🧠 ML Strategy: {ml_strategy} (confidence: {ml_confidence:.2f})")
            print(f"🧠 Blended confidence: {blended_confidence:.2f}")
        
        return enhanced_analysis
    
    def optimize_position_sizing(self, symbol: str, entry_price: float,
                                strategy: str, confidence: float,
                                portfolio_value: float) -> Dict:
        """
        ML-optimized position sizing that enhances traditional risk management
        """
        # Get traditional position sizing first
        traditional_shares, traditional_info = self.risk_manager.calculate_position_size(
            symbol, entry_price, strategy, confidence, portfolio_value
        )
        
        result = {
            'traditional_shares': traditional_shares,
            'traditional_info': traditional_info,
            'ml_enhanced': False,
            'final_shares': traditional_shares
        }
        
        if not self.use_ml_position_sizing or not self.ml_enabled:
            return result
        
        try:
            # Get current positions for ML analysis
            current_positions = self._get_position_data()
            
            # ML-optimized sizing
            ml_sizing = self.risk_predictor.calculate_optimal_position_size(
                symbol, entry_price, strategy, confidence, portfolio_value, current_positions
            )
            
            # Blend traditional and ML sizing (60% traditional, 40% ML)
            traditional_value = traditional_shares * entry_price
            ml_value = ml_sizing['optimal_value']
            blended_value = (traditional_value * 0.6) + (ml_value * 0.4)
            blended_shares = int(blended_value / entry_price) if entry_price > 0 else 0
            
            result.update({
                'ml_sizing': ml_sizing,
                'blended_shares': blended_shares,
                'blended_value': blended_value,
                'ml_enhanced': True,
                'final_shares': blended_shares,
                'sizing_ratio': blended_value / max(traditional_value, 1)
            })
            
            print(f"🧠 ML Position Sizing: {blended_shares} shares (${blended_value:,.0f})")
            print(f"🧠 Traditional vs ML ratio: {result['sizing_ratio']:.2f}")
            
        except Exception as e:
            print(f"⚠️ ML position sizing error: {e}")
            result['ml_error'] = str(e)
        
        return result
    
    def enhanced_risk_assessment(self, symbol: str, position_size: float,
                               portfolio_value: float, confidence: float) -> Dict:
        """
        Enhanced risk assessment combining traditional and ML approaches
        """
        # Traditional risk check
        should_trade_traditional, risk_reason, risk_details = self.risk_manager.should_execute_trade(
            symbol, 'momentum', confidence, position_size  # Default strategy for risk check
        )
        
        result = {
            'traditional_approved': should_trade_traditional,
            'traditional_reason': risk_reason,
            'traditional_details': risk_details,
            'ml_enhanced': False,
            'final_approved': should_trade_traditional
        }
        
        if not self.use_ml_risk_prediction or not self.ml_enabled:
            return result
        
        try:
            # Get current positions for ML risk analysis
            current_positions = self._get_position_data()
            market_data = {'vix': 20}  # Would get real VIX data
            
            # ML risk assessment
            should_reduce_risk, ml_risk_reason, ml_analysis = self.risk_predictor.should_reduce_risk(
                current_positions, market_data
            )
            
            # Risk prediction for this specific position
            risk_prediction = self.risk_predictor.predict_position_risk(
                symbol, position_size, portfolio_value, confidence
            )
            
            # Combined decision (both must approve)
            ml_approved = not should_reduce_risk and risk_prediction['risk_category'] != 'extreme'
            final_approved = should_trade_traditional and ml_approved
            
            result.update({
                'ml_approved': ml_approved,
                'ml_risk_reason': ml_risk_reason,
                'ml_analysis': ml_analysis,
                'risk_prediction': risk_prediction,
                'ml_enhanced': True,
                'final_approved': final_approved
            })
            
            if not ml_approved:
                print(f"🛡️ ML Risk Block: {ml_risk_reason}")
            
        except Exception as e:
            print(f"⚠️ ML risk assessment error: {e}")
            result['ml_error'] = str(e)
        
        return result
    
    def adaptive_confidence_adjustment(self, base_confidence: float,
                                     recent_performance: Dict) -> float:
        """
        Adaptively adjust confidence based on recent performance
        """
        if not self.ml_enabled:
            return base_confidence
        
        # Get ML model insights
        ml_insights = self.strategy_selector.get_ml_insights()
        model_confidence = ml_insights.get('model_confidence', 0.5)
        
        # Recent performance adjustment
        recent_win_rate = recent_performance.get('win_rate', 0.5)
        performance_adjustment = (recent_win_rate - 0.5) * 0.2  # ±10% max adjustment
        
        # Model confidence adjustment
        model_adjustment = (model_confidence - 0.5) * 0.1  # ±5% max adjustment
        
        # Combined adjustment
        adjusted_confidence = base_confidence + performance_adjustment + model_adjustment
        adjusted_confidence = max(0.1, min(0.95, adjusted_confidence))  # Clamp to reasonable range
        
        if abs(adjusted_confidence - base_confidence) > 0.05:
            print(f"🧠 Confidence adjusted: {base_confidence:.2f} → {adjusted_confidence:.2f}")
        
        return adjusted_confidence
    
    def _get_position_data(self) -> List[Dict]:
        """Get current position data for ML analysis"""
        try:
            positions = self.api.list_positions()
            position_data = []
            
            for pos in positions:
                position_data.append({
                    'symbol': pos.symbol,
                    'market_value': float(pos.market_value),
                    'weight': float(pos.market_value) / float(self.api.get_account().portfolio_value),
                    'asset_type': self._classify_asset_type(pos.symbol),
                    'sector': self._get_sector(pos.symbol),
                    'entry_confidence': 0.6  # Would track this in real system
                })
            
            return position_data
            
        except Exception as e:
            print(f"⚠️ Error getting position data: {e}")
            return []
    
    def _classify_asset_type(self, symbol: str) -> str:
        """Classify asset type for risk analysis"""
        if symbol.endswith('USD'):
            return 'crypto'
        elif symbol in ['TQQQ', 'UPRO', 'SOXL', 'FAS', 'UDOW']:
            return 'leveraged_etf'
        elif symbol in ['SPY', 'QQQ', 'IWM', 'XLK', 'XLV', 'XLF']:
            return 'etf'
        elif len(symbol) > 10:  # Option symbols are long
            return 'option'
        else:
            return 'stock'
    
    def _get_sector(self, symbol: str) -> str:
        """Get sector classification"""
        sector_map = {
            'SPY': 'market', 'QQQ': 'technology', 'IWM': 'small_cap',
            'AAPL': 'technology', 'MSFT': 'technology', 'GOOGL': 'technology',
            'NVDA': 'technology', 'TSLA': 'technology', 'META': 'technology',
            'JPM': 'finance', 'BAC': 'finance', 'XLF': 'finance',
            'JNJ': 'healthcare', 'PFE': 'healthcare', 'XLV': 'healthcare',
            'XOM': 'energy', 'XLE': 'energy',
            'XLK': 'technology', 'XLY': 'consumer'
        }
        
        if symbol.endswith('USD'):
            return 'crypto'
        
        return sector_map.get(symbol, 'unknown')
    
    def record_trade_outcome(self, symbol: str, strategy: str, confidence: float,
                           entry_price: float, exit_price: float, ml_enhanced: bool):
        """Record trade outcome for learning"""
        trade_return = (exit_price - entry_price) / entry_price
        success = trade_return > 0
        
        trade_result = {
            'return_pct': trade_return,
            'success': success,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
        
        # Update strategy performance
        self.strategy_selector.update_strategy_performance(strategy, trade_result)
        
        # Update ML performance tracking
        self.ml_performance['total_trades'] += 1
        
        if ml_enhanced:
            self.ml_performance['ml_trades'] += 1
            if success:
                self.ml_performance['ml_wins'] += 1
        else:
            self.ml_performance['traditional_trades'] += 1
            if success:
                self.ml_performance['traditional_wins'] += 1
        
        # Log performance
        if self.ml_performance['total_trades'] % 10 == 0:
            self._log_ml_performance()
    
    def _log_ml_performance(self):
        """Log ML vs traditional performance"""
        total = self.ml_performance['total_trades']
        ml_trades = self.ml_performance['ml_trades']
        traditional_trades = self.ml_performance['traditional_trades']
        
        if ml_trades > 0:
            ml_win_rate = self.ml_performance['ml_wins'] / ml_trades
        else:
            ml_win_rate = 0
        
        if traditional_trades > 0:
            traditional_win_rate = self.ml_performance['traditional_wins'] / traditional_trades
        else:
            traditional_win_rate = 0
        
        print(f"\n📊 ML PERFORMANCE SUMMARY (Last {total} trades)")
        print(f"   🧠 ML Enhanced: {ml_trades} trades, {ml_win_rate:.1%} win rate")
        print(f"   📈 Traditional: {traditional_trades} trades, {traditional_win_rate:.1%} win rate")
        
        if ml_trades > 5 and traditional_trades > 5:
            improvement = ml_win_rate - traditional_win_rate
            print(f"   🎯 ML Improvement: {improvement:+.1%}")
    
    def get_ml_status(self) -> Dict:
        """Get current ML system status"""
        return {
            'ml_enabled': self.ml_enabled,
            'components': {
                'strategy_selection': self.use_ml_strategy_selection,
                'position_sizing': self.use_ml_position_sizing,
                'risk_prediction': self.use_ml_risk_prediction
            },
            'performance': self.ml_performance,
            'model_insights': self.strategy_selector.get_ml_insights()
        }

def test_ml_adaptive_framework():
    """Test ML adaptive framework integration"""
    print("🧪 Testing ML Adaptive Framework...")
    
    try:
        # Mock API and risk manager for testing
        class MockAPI:
            def list_positions(self):
                return []
            def get_account(self):
                class Account:
                    portfolio_value = 100000
                return Account()
        
        class MockRiskManager:
            def calculate_position_size(self, symbol, price, strategy, confidence, portfolio_value):
                shares = int(5000 / price)  # $5K position
                return shares, {'target_value': shares * price}
            
            def should_execute_trade(self, symbol, strategy, confidence, price):
                return True, "Trade approved", {}
        
        api = MockAPI()
        risk_mgr = MockRiskManager()
        
        # Initialize framework
        ml_framework = MLAdaptiveFramework(api, risk_mgr)
        
        # Test market analysis enhancement
        enhanced = ml_framework.enhance_market_analysis(
            'bullish', 0.7,
            {'rsi': 65, 'confidence': 0.7},
            {'breakout_probability': 0.6, 'confidence': 0.65}
        )
        print(f"✅ Enhanced analysis: {enhanced.get('ml_strategy', 'N/A')} strategy")
        
        # Test position sizing
        sizing = ml_framework.optimize_position_sizing(
            'AAPL', 200.0, 'momentum', 0.75, 100000
        )
        print(f"✅ Optimized sizing: {sizing['final_shares']} shares")
        
        # Test risk assessment
        risk = ml_framework.enhanced_risk_assessment(
            'AAPL', 5000, 100000, 0.75
        )
        print(f"✅ Risk assessment: {risk['final_approved']}")
        
        # Test status
        status = ml_framework.get_ml_status()
        print(f"✅ ML enabled: {status['ml_enabled']}")
        
        print("✅ ML Adaptive Framework test completed!")
        return True
        
    except Exception as e:
        print(f"❌ ML Adaptive Framework test failed: {e}")
        return False

if __name__ == "__main__":
    test_ml_adaptive_framework()