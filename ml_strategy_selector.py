#!/usr/bin/env python3
"""
ML Strategy Selector - Phase 5.1
Adaptive strategy selection using machine learning
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from database_manager import TradingDatabase

class MLStrategySelector:
    """Machine learning-enhanced strategy selection"""
    
    def __init__(self, db: TradingDatabase = None, firebase_db = None):
        self.db = db
        self.firebase_db = firebase_db
        
        # Strategy performance tracking
        self.strategy_history = {}
        self.performance_window = 30  # Days to look back
        
        # ML weights for ensemble decision making
        self.feature_weights = {
            'technical_confidence': 0.35,
            'regime_confidence': 0.35, 
            'pattern_strength': 0.20,
            'recent_performance': 0.10
        }
        
        # Strategy confidence thresholds (adaptive)
        self.base_thresholds = {
            'aggressive_momentum': 0.75,  # High confidence required
            'momentum': 0.60,             # Moderate confidence
            'sector_rotation': 0.50,      # Lower confidence ok
            'volatility_trading': 0.45,   # Opportunistic
            'defensive': 0.30             # Low confidence fallback
        }
        
        # Performance metrics for adaptation
        self.strategy_metrics = {}
        
        print("🧠 ML Strategy Selector initialized")
        print(f"   📊 Performance window: {self.performance_window} days")
        print(f"   🎯 Adaptive thresholds: {len(self.base_thresholds)} strategies")
    
    def analyze_market_features(self, market_data: Dict) -> Dict:
        """Extract ML features from market data"""
        features = {}
        
        # Technical indicators features
        if 'technical' in market_data:
            tech = market_data['technical']
            features['rsi_signal'] = 1 if tech.get('rsi', 50) > 70 else -1 if tech.get('rsi', 50) < 30 else 0
            features['macd_signal'] = 1 if tech.get('macd_signal', 'neutral') == 'bullish' else -1 if tech.get('macd_signal', 'neutral') == 'bearish' else 0
            features['bb_position'] = tech.get('bb_position', 0.5)  # 0-1 within bands
            features['technical_confidence'] = tech.get('confidence', 0.5)
        
        # Market regime features
        if 'regime' in market_data:
            regime = market_data['regime']
            features['regime_type'] = 1 if regime.get('type') == 'bullish' else -1 if regime.get('type') == 'bearish' else 0
            features['regime_strength'] = regime.get('strength', 0.5)
            features['regime_confidence'] = regime.get('confidence', 0.5)
            features['vix_level'] = regime.get('vix', 20) / 40  # Normalize VIX
        
        # Pattern recognition features
        if 'pattern' in market_data:
            pattern = market_data['pattern']
            features['breakout_strength'] = pattern.get('breakout_probability', 0.5)
            features['support_distance'] = pattern.get('support_distance', 0.05)
            features['resistance_distance'] = pattern.get('resistance_distance', 0.05)
            features['pattern_strength'] = pattern.get('confidence', 0.5)
        
        # Market timing features
        features['hour_of_day'] = datetime.now().hour / 24
        features['day_of_week'] = datetime.now().weekday() / 7
        features['volatility_rank'] = market_data.get('volatility_rank', 0.5)
        
        return features
    
    def get_strategy_performance(self, strategy: str, days: int = 30) -> Dict:
        """Get recent performance metrics for a strategy"""
        if not self.db:
            return {'win_rate': 0.5, 'avg_return': 0.0, 'sharpe_ratio': 0.0, 'trade_count': 0}
        
        try:
            # Query recent trades for this strategy
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # This would query the database for strategy performance
            # PRODUCTION FIX: Use real database performance data instead of hardcoded values
            if self.db:
                # Query actual performance from database
                try:
                    # Get trades for this strategy
                    trades = self.db.get_trades_by_strategy(strategy)
                    if trades and len(trades) > 0:
                        # Calculate real performance metrics
                        wins = sum(1 for trade in trades if trade.get('profit_loss', 0) > 0)
                        total_trades = len(trades)
                        win_rate = wins / total_trades if total_trades > 0 else 0.5
                        
                        # Calculate average return
                        returns = [trade.get('profit_loss', 0) for trade in trades]
                        avg_return = sum(returns) / len(returns) if returns else 0.0
                        
                        # Simplified Sharpe ratio calculation
                        if len(returns) > 1:
                            import statistics
                            return_std = statistics.stdev(returns) if len(returns) > 1 else 1.0
                            sharpe_ratio = avg_return / return_std if return_std > 0 else 0.0
                        else:
                            sharpe_ratio = 0.0
                        
                        return {
                            'win_rate': win_rate,
                            'avg_return': avg_return,
                            'sharpe_ratio': sharpe_ratio,
                            'trade_count': total_trades
                        }
                except Exception as db_error:
                    print(f"⚠️ Database query failed for {strategy}: {db_error}")
            
            # Fallback to neutral baseline for unknown strategies
            return {'win_rate': 0.5, 'avg_return': 0.0, 'sharpe_ratio': 0.0, 'trade_count': 0}
            
        except Exception as e:
            print(f"⚠️ Error getting strategy performance: {e}")
            return {'win_rate': 0.5, 'avg_return': 0.0, 'sharpe_ratio': 0.0, 'trade_count': 0}
    
    def calculate_strategy_scores(self, features: Dict) -> Dict:
        """Calculate ML-based scores for each strategy"""
        scores = {}
        
        # Get recent performance for all strategies
        for strategy in self.base_thresholds.keys():
            perf = self.get_strategy_performance(strategy)
            
            # Base score from market features
            base_score = 0.5
            
            # Technical analysis component
            if strategy in ['aggressive_momentum', 'momentum']:
                tech_score = features.get('technical_confidence', 0.5)
                base_score += (tech_score - 0.5) * 0.4
            
            # Regime analysis component  
            regime_score = features.get('regime_confidence', 0.5)
            if strategy == 'aggressive_momentum' and features.get('regime_type', 0) > 0:
                base_score += regime_score * 0.4
            elif strategy == 'defensive' and features.get('regime_type', 0) < 0:
                base_score += regime_score * 0.4
            elif strategy == 'volatility_trading' and features.get('vix_level', 0.5) > 0.6:
                base_score += 0.3
            
            # Pattern strength component
            pattern_score = features.get('pattern_strength', 0.5)
            if strategy in ['momentum', 'aggressive_momentum']:
                base_score += (pattern_score - 0.5) * 0.2
            
            # Recent performance adjustment
            win_rate_bonus = (perf['win_rate'] - 0.5) * 0.2
            sharpe_bonus = min(perf['sharpe_ratio'] / 2.0, 0.2)
            base_score += win_rate_bonus + sharpe_bonus
            
            # Normalize to 0-1 range
            scores[strategy] = max(0, min(1, base_score))
        
        return scores
    
    def select_optimal_strategy(self, market_data: Dict) -> Tuple[str, float, Dict]:
        """Select optimal strategy using ML ensemble approach"""
        
        # Extract features
        features = self.analyze_market_features(market_data)
        
        # Calculate strategy scores
        strategy_scores = self.calculate_strategy_scores(features)
        
        # Find best strategy
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])
        strategy_name = best_strategy[0]
        confidence = best_strategy[1]
        
        # Adaptive threshold adjustment
        base_threshold = self.base_thresholds[strategy_name]
        recent_perf = self.get_strategy_performance(strategy_name)
        
        # Lower threshold if strategy is performing well
        performance_adjustment = (recent_perf['win_rate'] - 0.5) * 0.2
        adjusted_threshold = max(0.3, base_threshold - performance_adjustment)
        
        # Check if confidence meets threshold
        if confidence >= adjusted_threshold:
            final_strategy = strategy_name
            final_confidence = confidence
        else:
            # Fallback to defensive strategy
            final_strategy = 'defensive'
            final_confidence = strategy_scores['defensive']
        
        selection_details = {
            'all_scores': strategy_scores,
            'features': features,
            'threshold_used': adjusted_threshold,
            'performance_data': recent_perf,
            'selection_reason': f"Confidence {confidence:.2f} >= threshold {adjusted_threshold:.2f}"
        }
        
        return final_strategy, final_confidence, selection_details
    
    def update_strategy_performance(self, strategy: str, trade_result: Dict):
        """Update performance tracking for adaptive learning"""
        if strategy not in self.strategy_metrics:
            self.strategy_metrics[strategy] = {
                'trades': [],
                'total_return': 0.0,
                'win_count': 0,
                'total_trades': 0
            }
        
        # Record trade result
        self.strategy_metrics[strategy]['trades'].append({
            'timestamp': datetime.now().isoformat(),
            'return': trade_result.get('return_pct', 0.0),
            'success': trade_result.get('success', False)
        })
        
        # Update aggregated metrics
        self.strategy_metrics[strategy]['total_return'] += trade_result.get('return_pct', 0.0)
        self.strategy_metrics[strategy]['total_trades'] += 1
        if trade_result.get('success', False):
            self.strategy_metrics[strategy]['win_count'] += 1
        
        # Keep only recent trades (rolling window)
        cutoff_date = datetime.now() - timedelta(days=self.performance_window)
        self.strategy_metrics[strategy]['trades'] = [
            trade for trade in self.strategy_metrics[strategy]['trades']
            if datetime.fromisoformat(trade['timestamp']) > cutoff_date
        ]
        
        print(f"📊 Updated performance for {strategy}: "
              f"Win rate: {self.strategy_metrics[strategy]['win_count'] / max(1, self.strategy_metrics[strategy]['total_trades']):.1%}")
    
    def get_ml_insights(self) -> Dict:
        """Get current ML model insights and performance"""
        insights = {
            'strategy_rankings': {},
            'feature_importance': {},
            'recent_performance': {},
            'model_confidence': 0.0
        }
        
        # Calculate strategy rankings based on recent performance
        for strategy in self.base_thresholds.keys():
            perf = self.get_strategy_performance(strategy, 7)  # Last 7 days
            score = perf['win_rate'] * 0.6 + (perf['sharpe_ratio'] / 2.0) * 0.4
            insights['strategy_rankings'][strategy] = score
        
        # Feature importance (based on weights)
        insights['feature_importance'] = self.feature_weights.copy()
        
        # Recent performance summary
        for strategy, metrics in self.strategy_metrics.items():
            if metrics['total_trades'] > 0:
                insights['recent_performance'][strategy] = {
                    'win_rate': metrics['win_count'] / metrics['total_trades'],
                    'avg_return': metrics['total_return'] / metrics['total_trades'],
                    'trade_count': len(metrics['trades'])
                }
        
        # Overall model confidence (based on recent performance)
        if insights['recent_performance']:
            avg_win_rate = np.mean([p['win_rate'] for p in insights['recent_performance'].values()])
            insights['model_confidence'] = min(avg_win_rate * 1.5, 1.0)
        
        return insights

def test_ml_strategy_selector():
    """Test ML strategy selection functionality"""
    print("🧪 Testing ML Strategy Selector...")
    
    try:
        from database_manager import TradingDatabase
        
        db = TradingDatabase()
        ml_selector = MLStrategySelector(db)
        
        # Mock market data
        market_data = {
            'technical': {
                'rsi': 65,
                'macd_signal': 'bullish',
                'bb_position': 0.8,
                'confidence': 0.7
            },
            'regime': {
                'type': 'bullish',
                'strength': 0.8,
                'confidence': 0.75,
                'vix': 18
            },
            'pattern': {
                'breakout_probability': 0.6,
                'support_distance': 0.02,
                'resistance_distance': 0.04,
                'confidence': 0.65
            },
            'volatility_rank': 0.4
        }
        
        # Test strategy selection
        strategy, confidence, details = ml_selector.select_optimal_strategy(market_data)
        print(f"✅ Selected strategy: {strategy} (confidence: {confidence:.2f})")
        print(f"✅ All scores: {details['all_scores']}")
        
        # Test performance update
        trade_result = {'return_pct': 0.03, 'success': True}
        ml_selector.update_strategy_performance(strategy, trade_result)
        
        # Test insights
        insights = ml_selector.get_ml_insights()
        print(f"✅ Model confidence: {insights['model_confidence']:.2f}")
        
        print("✅ ML Strategy Selector test completed!")
        return True
        
    except Exception as e:
        print(f"❌ ML Strategy Selector test failed: {e}")
        return False

if __name__ == "__main__":
    test_ml_strategy_selector()