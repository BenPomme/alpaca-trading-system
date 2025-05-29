#!/usr/bin/env python3
"""
ML Risk Predictor - Phase 5.2  
Real-time risk prediction and dynamic position sizing
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database_manager import TradingDatabase

class MLRiskPredictor:
    """Machine learning risk prediction and position sizing"""
    
    def __init__(self, db: TradingDatabase = None):
        self.db = db
        
        # Risk prediction parameters
        self.lookback_period = 20  # Days for volatility calculation
        self.var_confidence = 0.95  # Value at Risk confidence level
        self.max_portfolio_risk = 0.20  # 20% max drawdown
        
        # ML features for risk prediction
        self.risk_features = [
            'portfolio_concentration',  # How concentrated positions are
            'sector_correlation',       # Cross-sector correlation
            'volatility_regime',        # Current volatility environment
            'leverage_ratio',           # Options and leverage exposure
            'momentum_strength',        # Trend strength
            'liquidity_score'          # Position liquidity
        ]
        
        # Kelly Criterion with ML confidence adjustment
        self.kelly_multiplier = 0.25  # Conservative Kelly fraction
        
        # Risk model parameters (learned from data)
        self.risk_model_params = {
            'base_volatility': 0.15,
            'regime_multipliers': {
                'low_vol': 0.8,
                'normal_vol': 1.0, 
                'high_vol': 1.5,
                'crisis_vol': 2.5
            },
            'correlation_penalties': {
                'low_corr': 1.0,
                'medium_corr': 1.2,
                'high_corr': 1.6
            }
        }
        
        print("🛡️ ML Risk Predictor initialized")
        print(f"   📊 VaR confidence: {self.var_confidence:.1%}")
        print(f"   🎯 Max portfolio risk: {self.max_portfolio_risk:.1%}")
        print(f"   🔧 Kelly multiplier: {self.kelly_multiplier}")
    
    def calculate_portfolio_features(self, positions: List[Dict], market_data: Dict) -> Dict:
        """Calculate risk features from current portfolio"""
        if not positions:
            return self._empty_portfolio_features()
        
        features = {}
        
        # Portfolio concentration (Herfindahl index)
        position_weights = [pos['weight'] for pos in positions if 'weight' in pos]
        if position_weights:
            hhi = sum(w**2 for w in position_weights)
            features['portfolio_concentration'] = hhi
        else:
            features['portfolio_concentration'] = 0.0
        
        # Sector correlation analysis
        sectors = [pos.get('sector', 'unknown') for pos in positions]
        unique_sectors = len(set(sectors))
        features['sector_diversification'] = unique_sectors / max(len(positions), 1)
        
        # Volatility regime detection
        vix_level = market_data.get('vix', 20)
        if vix_level < 15:
            features['volatility_regime'] = 0.8  # Low vol
        elif vix_level < 25:
            features['volatility_regime'] = 1.0  # Normal vol
        elif vix_level < 35:
            features['volatility_regime'] = 1.5  # High vol
        else:
            features['volatility_regime'] = 2.5  # Crisis vol
        
        # Leverage ratio (options + leveraged ETFs)
        total_value = sum(pos.get('market_value', 0) for pos in positions)
        leveraged_value = sum(
            pos.get('market_value', 0) for pos in positions 
            if pos.get('asset_type') in ['option', 'leveraged_etf']
        )
        features['leverage_ratio'] = leveraged_value / max(total_value, 1)
        
        # Momentum strength (average confidence across positions)
        confidences = [pos.get('entry_confidence', 0.5) for pos in positions]
        features['momentum_strength'] = np.mean(confidences) if confidences else 0.5
        
        # Liquidity score (based on average daily volume)
        liquidity_scores = []
        for pos in positions:
            symbol = pos.get('symbol', '')
            # Assign liquidity scores based on symbol type
            if symbol in ['SPY', 'QQQ', 'IWM']:
                liquidity_scores.append(1.0)  # Highly liquid
            elif symbol.endswith('USD'):  # Crypto
                liquidity_scores.append(0.8)  # Good liquidity
            elif pos.get('asset_type') == 'option':
                liquidity_scores.append(0.6)  # Moderate liquidity
            else:
                liquidity_scores.append(0.7)  # Average liquidity
        
        features['liquidity_score'] = np.mean(liquidity_scores) if liquidity_scores else 0.7
        
        return features
    
    def _empty_portfolio_features(self) -> Dict:
        """Default features for empty portfolio"""
        return {
            'portfolio_concentration': 0.0,
            'sector_diversification': 1.0,
            'volatility_regime': 1.0,
            'leverage_ratio': 0.0,
            'momentum_strength': 0.5,
            'liquidity_score': 1.0
        }
    
    def predict_position_risk(self, symbol: str, position_size: float, 
                            portfolio_value: float, confidence: float) -> Dict:
        """Predict risk metrics for a potential position"""
        
        # Base position risk (% of portfolio)
        position_weight = position_size / portfolio_value
        
        # Confidence-adjusted risk (higher confidence = lower perceived risk)
        confidence_adjustment = 0.5 + (confidence * 0.5)  # 0.5 to 1.0 range
        adjusted_risk = position_weight / confidence_adjustment
        
        # Symbol-specific risk multipliers
        risk_multipliers = {
            'SPY': 1.0, 'QQQ': 1.1, 'IWM': 1.3,  # ETFs
            'AAPL': 1.2, 'MSFT': 1.1, 'GOOGL': 1.3,  # Large caps
            'TSLA': 2.0, 'NVDA': 1.8, 'META': 1.5,  # Volatile stocks
        }
        
        # Asset type risk multipliers
        if symbol.endswith('USD'):  # Crypto
            base_multiplier = 2.5
        elif 'TQQQ' in symbol or 'UPRO' in symbol:  # 3x ETFs
            base_multiplier = 3.0
        else:
            base_multiplier = risk_multipliers.get(symbol, 1.4)
        
        final_risk = adjusted_risk * base_multiplier
        
        return {
            'position_risk': final_risk,
            'position_weight': position_weight,
            'confidence_adjustment': confidence_adjustment,
            'risk_multiplier': base_multiplier,
            'risk_category': self._categorize_risk(final_risk)
        }
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level"""
        if risk_score < 0.02:
            return 'low'
        elif risk_score < 0.05:
            return 'medium'
        elif risk_score < 0.10:
            return 'high'
        else:
            return 'extreme'
    
    def calculate_optimal_position_size(self, symbol: str, entry_price: float,
                                      strategy: str, confidence: float,
                                      portfolio_value: float, 
                                      current_positions: List[Dict]) -> Dict:
        """Calculate ML-optimized position size using Kelly Criterion"""
        
        # Get portfolio features for risk assessment
        market_data = {'vix': 20}  # Would come from real market data
        portfolio_features = self.calculate_portfolio_features(current_positions, market_data)
        
        # Base Kelly Criterion calculation
        win_probability = 0.5 + (confidence * 0.3)  # 50-80% based on confidence
        avg_win = 0.08  # 8% average win (targeting 5-10% monthly)
        avg_loss = 0.03  # 3% average loss (tight stops)
        
        kelly_fraction = (win_probability * avg_win - (1 - win_probability) * avg_loss) / avg_win
        kelly_fraction = max(0, min(kelly_fraction, 0.5)) * self.kelly_multiplier
        
        # Risk adjustments based on portfolio features
        risk_adjustments = 1.0
        
        # Concentration penalty
        if portfolio_features['portfolio_concentration'] > 0.3:
            risk_adjustments *= 0.8  # Reduce size if concentrated
        
        # Volatility regime adjustment
        vol_regime = portfolio_features['volatility_regime']
        risk_adjustments *= self.risk_model_params['regime_multipliers'].get(
            'normal_vol' if vol_regime == 1.0 else 'high_vol', 1.0
        )
        
        # Sector diversification adjustment
        if portfolio_features['sector_diversification'] < 0.5:
            risk_adjustments *= 0.9  # Reduce if not diversified
        
        # Leverage adjustment  
        if portfolio_features['leverage_ratio'] > 0.3:
            risk_adjustments *= 0.7  # Reduce if highly leveraged
        
        # Calculate final position size
        optimal_fraction = kelly_fraction * risk_adjustments
        optimal_value = portfolio_value * optimal_fraction
        optimal_shares = int(optimal_value / entry_price) if entry_price > 0 else 0
        
        # Risk prediction for this position
        risk_prediction = self.predict_position_risk(
            symbol, optimal_value, portfolio_value, confidence
        )
        
        return {
            'optimal_shares': optimal_shares,
            'optimal_value': optimal_value,
            'optimal_fraction': optimal_fraction,
            'kelly_fraction': kelly_fraction,
            'risk_adjustments': risk_adjustments,
            'win_probability': win_probability,
            'risk_prediction': risk_prediction,
            'portfolio_features': portfolio_features,
            'reasoning': f"Kelly: {kelly_fraction:.3f}, Risk adj: {risk_adjustments:.3f}, Final: {optimal_fraction:.3f}"
        }
    
    def calculate_portfolio_var(self, positions: List[Dict], confidence_level: float = 0.95) -> Dict:
        """Calculate Value at Risk for current portfolio"""
        if not positions:
            return {'var_amount': 0, 'var_percentage': 0, 'risk_level': 'none'}
        
        # Portfolio value and weights
        total_value = sum(pos.get('market_value', 0) for pos in positions)
        weights = [pos.get('market_value', 0) / total_value for pos in positions]
        
        # Estimate individual position volatilities
        volatilities = []
        for pos in positions:
            symbol = pos.get('symbol', '')
            if symbol.endswith('USD'):  # Crypto
                vol = 0.60  # 60% annual volatility
            elif 'TQQQ' in symbol or 'UPRO' in symbol:  # 3x ETFs
                vol = 0.45  # 45% annual volatility
            elif pos.get('asset_type') == 'option':
                vol = 0.80  # 80% options volatility
            elif symbol in ['SPY', 'QQQ', 'IWM']:
                vol = 0.20  # 20% ETF volatility
            else:
                vol = 0.30  # 30% stock volatility
            volatilities.append(vol)
        
        # Simple portfolio volatility (assuming 0.5 correlation)
        portfolio_variance = 0
        for i, w_i in enumerate(weights):
            for j, w_j in enumerate(weights):
                correlation = 0.5 if i != j else 1.0
                portfolio_variance += w_i * w_j * volatilities[i] * volatilities[j] * correlation
        
        portfolio_volatility = np.sqrt(portfolio_variance)
        daily_volatility = portfolio_volatility / np.sqrt(252)  # Convert to daily
        
        # VaR calculation (normal distribution assumption)
        z_score = 1.645 if confidence_level == 0.95 else 2.326  # 95% or 99%
        var_daily = total_value * daily_volatility * z_score
        var_percentage = (var_daily / total_value) * 100
        
        # Risk level assessment
        if var_percentage < 2:
            risk_level = 'low'
        elif var_percentage < 5:
            risk_level = 'medium'
        elif var_percentage < 10:
            risk_level = 'high'
        else:
            risk_level = 'extreme'
        
        return {
            'var_amount': var_daily,
            'var_percentage': var_percentage,
            'portfolio_volatility': portfolio_volatility,
            'daily_volatility': daily_volatility,
            'risk_level': risk_level,
            'confidence_level': confidence_level
        }
    
    def should_reduce_risk(self, current_positions: List[Dict], 
                          market_data: Dict) -> Tuple[bool, str, Dict]:
        """Determine if risk reduction is needed"""
        
        # Calculate current portfolio VaR
        var_analysis = self.calculate_portfolio_var(current_positions)
        
        # Get portfolio features
        features = self.calculate_portfolio_features(current_positions, market_data)
        
        # Risk reduction triggers
        triggers = []
        
        # VaR trigger
        if var_analysis['var_percentage'] > 8:  # 8% daily VaR limit
            triggers.append(f"High VaR: {var_analysis['var_percentage']:.1f}%")
        
        # Concentration trigger
        if features['portfolio_concentration'] > 0.4:
            triggers.append(f"High concentration: {features['portfolio_concentration']:.2f}")
        
        # Leverage trigger
        if features['leverage_ratio'] > 0.4:
            triggers.append(f"High leverage: {features['leverage_ratio']:.1%}")
        
        # Volatility regime trigger
        if features['volatility_regime'] > 2.0:
            triggers.append(f"Crisis volatility regime: {features['volatility_regime']:.1f}")
        
        # Market conditions trigger
        vix = market_data.get('vix', 20)
        if vix > 35:
            triggers.append(f"High VIX: {vix}")
        
        should_reduce = len(triggers) > 0
        reason = "; ".join(triggers) if triggers else "Risk levels acceptable"
        
        analysis = {
            'var_analysis': var_analysis,
            'portfolio_features': features,
            'triggers': triggers,
            'risk_score': len(triggers)
        }
        
        return should_reduce, reason, analysis

def test_ml_risk_predictor():
    """Test ML risk prediction functionality"""
    print("🧪 Testing ML Risk Predictor...")
    
    try:
        from database_manager import TradingDatabase
        
        db = TradingDatabase()
        risk_predictor = MLRiskPredictor(db)
        
        # Mock current positions
        positions = [
            {'symbol': 'SPY', 'market_value': 10000, 'weight': 0.1, 'asset_type': 'etf'},
            {'symbol': 'AAPL', 'market_value': 8000, 'weight': 0.08, 'asset_type': 'stock'},
            {'symbol': 'TQQQ', 'market_value': 5000, 'weight': 0.05, 'asset_type': 'leveraged_etf'},
            {'symbol': 'BTCUSD', 'market_value': 7000, 'weight': 0.07, 'asset_type': 'crypto'}
        ]
        
        market_data = {'vix': 22}
        
        # Test position sizing
        sizing = risk_predictor.calculate_optimal_position_size(
            'NVDA', 450.0, 'momentum', 0.75, 100000, positions
        )
        print(f"✅ Optimal position: {sizing['optimal_shares']} shares (${sizing['optimal_value']:,.0f})")
        print(f"✅ Kelly fraction: {sizing['kelly_fraction']:.3f}")
        
        # Test VaR calculation
        var_analysis = risk_predictor.calculate_portfolio_var(positions)
        print(f"✅ Portfolio VaR: ${var_analysis['var_amount']:,.0f} ({var_analysis['var_percentage']:.1f}%)")
        
        # Test risk reduction analysis
        should_reduce, reason, analysis = risk_predictor.should_reduce_risk(positions, market_data)
        print(f"✅ Risk reduction needed: {should_reduce} - {reason}")
        
        print("✅ ML Risk Predictor test completed!")
        return True
        
    except Exception as e:
        print(f"❌ ML Risk Predictor test failed: {e}")
        return False

if __name__ == "__main__":
    test_ml_risk_predictor()