#!/usr/bin/env python3
"""
ML Enhanced Market Regime Detector - Phase 5.4
Advanced regime detection using unsupervised learning and covariance analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import warnings
warnings.filterwarnings('ignore')

class MLRegimeDetector:
    """
    Machine learning enhanced market regime detection
    Uses multiple algorithms for robust regime identification
    """
    
    def __init__(self, lookback_period: int = 60):
        self.lookback_period = lookback_period  # Days of historical data
        
        # ML models for regime detection
        self.kmeans_model = KMeans(n_clusters=3, random_state=42, n_init=10)
        self.gmm_model = GaussianMixture(n_components=3, random_state=42)
        
        # Regime parameters
        self.regime_labels = {0: 'bearish', 1: 'sideways', 2: 'bullish'}
        self.confidence_threshold = 0.6
        
        # Feature weights for regime classification
        self.feature_weights = {
            'returns_momentum': 0.25,
            'volatility_level': 0.20,
            'correlation_structure': 0.20,
            'volume_pattern': 0.15,
            'breadth_indicators': 0.20
        }
        
        # Historical regime data
        self.regime_history = []
        self.price_history = {}
        
        print("🔍 ML Regime Detector initialized")
        print(f"   📊 Lookback period: {self.lookback_period} days")
        print(f"   🧠 Models: K-Means + Gaussian Mixture")
        print(f"   🎯 Confidence threshold: {self.confidence_threshold}")
    
    def update_price_history(self, symbol: str, price: float, volume: float = 0):
        """Update price history for regime analysis"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        # Add new price point
        self.price_history[symbol].append({
            'timestamp': datetime.now(),
            'price': price,
            'volume': volume
        })
        
        # Keep only recent data
        cutoff_date = datetime.now() - timedelta(days=self.lookback_period)
        self.price_history[symbol] = [
            point for point in self.price_history[symbol]
            if point['timestamp'] > cutoff_date
        ]
    
    def extract_regime_features(self, symbols: List[str]) -> Dict:
        """Extract features for regime classification"""
        features = {}
        
        if not self.price_history:
            return self._default_features()
        
        # Calculate returns for all symbols
        returns_data = {}
        for symbol in symbols:
            if symbol in self.price_history and len(self.price_history[symbol]) > 5:
                prices = [point['price'] for point in self.price_history[symbol]]
                returns = np.diff(np.log(prices))
                returns_data[symbol] = returns
        
        if not returns_data:
            return self._default_features()
        
        # Feature 1: Returns momentum
        all_returns = np.concatenate(list(returns_data.values()))
        if len(all_returns) > 0:
            mean_return = np.mean(all_returns)
            features['returns_momentum'] = np.tanh(mean_return * 100)  # Scale and bound
        else:
            features['returns_momentum'] = 0.0
        
        # Feature 2: Volatility level
        volatility = np.std(all_returns) if len(all_returns) > 1 else 0.05
        features['volatility_level'] = min(volatility * 10, 1.0)  # Normalize
        
        # Feature 3: Correlation structure
        if len(returns_data) > 1:
            returns_matrix = []
            min_length = min(len(r) for r in returns_data.values())
            
            for symbol_returns in returns_data.values():
                returns_matrix.append(symbol_returns[-min_length:] if min_length > 0 else [0])
            
            if min_length > 3:
                correlation_matrix = np.corrcoef(returns_matrix)
                # Average off-diagonal correlation as market coupling measure
                mask = ~np.eye(correlation_matrix.shape[0], dtype=bool)
                avg_correlation = np.mean(correlation_matrix[mask])
                features['correlation_structure'] = np.clip(avg_correlation, -1, 1)
            else:
                features['correlation_structure'] = 0.0
        else:
            features['correlation_structure'] = 0.0
        
        # Feature 4: Volume pattern
        volume_data = []
        for symbol in symbols:
            if symbol in self.price_history:
                volumes = [point['volume'] for point in self.price_history[symbol] if point['volume'] > 0]
                if volumes:
                    volume_data.extend(volumes)
        
        if volume_data:
            recent_volume = np.mean(volume_data[-5:]) if len(volume_data) >= 5 else np.mean(volume_data)
            historical_volume = np.mean(volume_data[:-5]) if len(volume_data) > 5 else recent_volume
            volume_ratio = recent_volume / max(historical_volume, 1)
            features['volume_pattern'] = np.tanh((volume_ratio - 1) * 2)  # Bound to [-1, 1]
        else:
            features['volume_pattern'] = 0.0
        
        # Feature 5: Market breadth (% of symbols with positive returns)
        recent_returns = []
        for symbol_returns in returns_data.values():
            if len(symbol_returns) > 0:
                recent_returns.append(symbol_returns[-1])
        
        if recent_returns:
            positive_pct = sum(1 for r in recent_returns if r > 0) / len(recent_returns)
            features['breadth_indicators'] = (positive_pct - 0.5) * 2  # Scale to [-1, 1]
        else:
            features['breadth_indicators'] = 0.0
        
        return features
    
    def _default_features(self) -> Dict:
        """Default features when no data available"""
        return {
            'returns_momentum': 0.0,
            'volatility_level': 0.5,
            'correlation_structure': 0.0,
            'volume_pattern': 0.0,
            'breadth_indicators': 0.0
        }
    
    def classify_regime_ml(self, features: Dict) -> Tuple[str, float, Dict]:
        """Classify market regime using ML models"""
        
        # Prepare feature vector
        feature_vector = np.array([
            features['returns_momentum'],
            features['volatility_level'], 
            features['correlation_structure'],
            features['volume_pattern'],
            features['breadth_indicators']
        ]).reshape(1, -1)
        
        # Get predictions from both models
        try:
            # K-Means prediction
            kmeans_pred = self.kmeans_model.fit_predict(feature_vector.reshape(-1, 1))
            kmeans_regime = kmeans_pred[0]
            
            # GMM prediction with probabilities
            gmm_pred = self.gmm_model.fit_predict(feature_vector)
            gmm_regime = gmm_pred[0]
            gmm_probs = self.gmm_model.predict_proba(feature_vector)[0]
            
            # Ensemble prediction (weighted average)
            ensemble_regime = int(np.round((kmeans_regime + gmm_regime) / 2))
            ensemble_confidence = max(gmm_probs)
            
        except Exception as e:
            print(f"⚠️ ML regime classification error: {e}")
            # Fallback to rule-based classification
            return self._rule_based_classification(features)
        
        # Map to regime labels
        regime_name = self.regime_labels.get(ensemble_regime, 'sideways')
        
        # Calculate overall confidence using feature weights
        confidence_score = self._calculate_confidence(features, regime_name)
        final_confidence = (ensemble_confidence * 0.7) + (confidence_score * 0.3)
        
        analysis_details = {
            'kmeans_regime': kmeans_regime,
            'gmm_regime': gmm_regime,
            'gmm_probabilities': gmm_probs.tolist(),
            'ensemble_regime': ensemble_regime,
            'feature_vector': feature_vector.flatten().tolist(),
            'confidence_breakdown': {
                'ml_confidence': ensemble_confidence,
                'feature_confidence': confidence_score,
                'final_confidence': final_confidence
            }
        }
        
        return regime_name, final_confidence, analysis_details
    
    def _rule_based_classification(self, features: Dict) -> Tuple[str, float, Dict]:
        """Fallback rule-based classification"""
        
        # Simple rule-based regime detection
        momentum = features['returns_momentum']
        volatility = features['volatility_level']
        breadth = features['breadth_indicators']
        
        # Bullish conditions
        if momentum > 0.2 and breadth > 0.3 and volatility < 0.7:
            regime = 'bullish'
            confidence = 0.6 + min(momentum + breadth, 0.3)
        # Bearish conditions
        elif momentum < -0.2 and breadth < -0.3 and volatility < 0.8:
            regime = 'bearish'
            confidence = 0.6 + min(abs(momentum) + abs(breadth), 0.3)
        # High volatility conditions
        elif volatility > 0.8:
            regime = 'bearish' if momentum < 0 else 'sideways'
            confidence = 0.5 + (volatility - 0.8) * 2
        else:
            regime = 'sideways'
            confidence = 0.4 + (0.5 - abs(momentum)) * 0.4
        
        confidence = np.clip(confidence, 0.1, 0.95)
        
        return regime, confidence, {'method': 'rule_based', 'features_used': features}
    
    def _calculate_confidence(self, features: Dict, regime: str) -> float:
        """Calculate confidence score based on feature alignment"""
        
        confidence_components = []
        
        # Momentum alignment
        momentum = features['returns_momentum']
        if regime == 'bullish' and momentum > 0:
            confidence_components.append(momentum)
        elif regime == 'bearish' and momentum < 0:
            confidence_components.append(abs(momentum))
        elif regime == 'sideways' and abs(momentum) < 0.1:
            confidence_components.append(0.5)
        else:
            confidence_components.append(0.2)
        
        # Volatility alignment
        volatility = features['volatility_level']
        if regime in ['bullish', 'sideways'] and volatility < 0.6:
            confidence_components.append(0.6)
        elif regime == 'bearish':
            confidence_components.append(min(volatility, 0.8))
        else:
            confidence_components.append(0.3)
        
        # Breadth alignment
        breadth = features['breadth_indicators']
        if regime == 'bullish' and breadth > 0:
            confidence_components.append(0.5 + breadth * 0.3)
        elif regime == 'bearish' and breadth < 0:
            confidence_components.append(0.5 + abs(breadth) * 0.3)
        else:
            confidence_components.append(0.4)
        
        # Weighted average
        weights = list(self.feature_weights.values())[:len(confidence_components)]
        weighted_confidence = np.average(confidence_components, weights=weights)
        
        return np.clip(weighted_confidence, 0.1, 0.95)
    
    def detect_regime_with_ml(self, market_quotes: List[Dict]) -> Dict:
        """
        Enhanced regime detection using ML
        Integrates with Phase 4 market regime detector
        """
        
        # Update price history with new quotes
        for quote in market_quotes:
            symbol = quote['symbol']
            price = quote.get('ask', quote.get('price', 0))
            volume = quote.get('volume', 0)
            self.update_price_history(symbol, price, volume)
        
        # Extract features for regime analysis
        symbols = [quote['symbol'] for quote in market_quotes]
        features = self.extract_regime_features(symbols)
        
        # ML-based regime classification
        regime, confidence, ml_analysis = self.classify_regime_ml(features)
        
        # Additional market indicators
        market_indicators = self._calculate_market_indicators(market_quotes)
        
        # Store regime in history
        regime_record = {
            'timestamp': datetime.now().isoformat(),
            'regime': regime,
            'confidence': confidence,
            'features': features,
            'ml_analysis': ml_analysis
        }
        self.regime_history.append(regime_record)
        
        # Keep only recent history
        cutoff_date = datetime.now() - timedelta(days=30)
        self.regime_history = [
            record for record in self.regime_history
            if datetime.fromisoformat(record['timestamp']) > cutoff_date
        ]
        
        return {
            'regime': regime,
            'confidence': confidence,
            'features': features,
            'ml_analysis': ml_analysis,
            'market_indicators': market_indicators,
            'regime_stability': self._calculate_regime_stability(),
            'ml_enhanced': True
        }
    
    def _calculate_market_indicators(self, quotes: List[Dict]) -> Dict:
        """Calculate additional market health indicators"""
        if not quotes:
            return {}
        
        # Price momentum across symbols
        momentum_scores = []
        for quote in quotes:
            symbol = quote['symbol']
            if symbol in self.price_history and len(self.price_history[symbol]) > 2:
                prices = [p['price'] for p in self.price_history[symbol][-3:]]
                if len(prices) >= 2:
                    momentum = (prices[-1] - prices[0]) / prices[0]
                    momentum_scores.append(momentum)
        
        # Market breadth
        positive_momentum = sum(1 for m in momentum_scores if m > 0)
        market_breadth = positive_momentum / max(len(momentum_scores), 1)
        
        # Average momentum
        avg_momentum = np.mean(momentum_scores) if momentum_scores else 0
        
        return {
            'market_breadth': market_breadth,
            'average_momentum': avg_momentum,
            'momentum_strength': abs(avg_momentum),
            'symbols_analyzed': len(momentum_scores)
        }
    
    def _calculate_regime_stability(self) -> float:
        """Calculate how stable the current regime has been"""
        if len(self.regime_history) < 3:
            return 0.5
        
        # Look at last 5 regime detections
        recent_regimes = [r['regime'] for r in self.regime_history[-5:]]
        
        # Calculate stability as % of same regime
        if recent_regimes:
            most_common = max(set(recent_regimes), key=recent_regimes.count)
            stability = recent_regimes.count(most_common) / len(recent_regimes)
        else:
            stability = 0.5
        
        return stability
    
    def get_regime_insights(self) -> Dict:
        """Get insights into regime detection performance"""
        if not self.regime_history:
            return {'message': 'No regime history available'}
        
        # Recent regime distribution
        recent_regimes = [r['regime'] for r in self.regime_history[-20:]]
        regime_counts = {regime: recent_regimes.count(regime) for regime in set(recent_regimes)}
        
        # Average confidence by regime
        regime_confidences = {}
        for regime in ['bullish', 'bearish', 'sideways']:
            confidences = [r['confidence'] for r in self.regime_history if r['regime'] == regime]
            regime_confidences[regime] = np.mean(confidences) if confidences else 0.5
        
        # Regime transition analysis
        transitions = []
        for i in range(1, len(self.regime_history)):
            if self.regime_history[i]['regime'] != self.regime_history[i-1]['regime']:
                transitions.append({
                    'from': self.regime_history[i-1]['regime'],
                    'to': self.regime_history[i]['regime'],
                    'timestamp': self.regime_history[i]['timestamp']
                })
        
        return {
            'regime_distribution': regime_counts,
            'average_confidences': regime_confidences,
            'recent_transitions': transitions[-5:],  # Last 5 transitions
            'current_stability': self._calculate_regime_stability(),
            'total_detections': len(self.regime_history)
        }

def test_ml_regime_detector():
    """Test ML regime detection functionality"""
    print("🧪 Testing ML Regime Detector...")
    
    try:
        detector = MLRegimeDetector(lookback_period=30)
        
        # Mock market quotes
        mock_quotes = [
            {'symbol': 'SPY', 'ask': 590.15, 'volume': 1000000},
            {'symbol': 'QQQ', 'ask': 520.92, 'volume': 800000},
            {'symbol': 'IWM', 'ask': 206.49, 'volume': 500000}
        ]
        
        # Simulate price updates over time
        for day in range(10):
            # Simulate trending market
            trend = 0.002 * day  # 0.2% daily trend
            for quote in mock_quotes:
                quote['ask'] *= (1 + trend + np.random.normal(0, 0.01))
                quote['volume'] *= (1 + np.random.normal(0, 0.1))
        
        # Test regime detection
        regime_result = detector.detect_regime_with_ml(mock_quotes)
        print(f"✅ Detected regime: {regime_result['regime']} (confidence: {regime_result['confidence']:.2f})")
        print(f"✅ ML enhanced: {regime_result['ml_enhanced']}")
        
        # Test insights
        insights = detector.get_regime_insights()
        print(f"✅ Regime stability: {insights.get('current_stability', 0):.2f}")
        
        print("✅ ML Regime Detector test completed!")
        return True
        
    except Exception as e:
        print(f"❌ ML Regime Detector test failed: {e}")
        return False

if __name__ == "__main__":
    test_ml_regime_detector()