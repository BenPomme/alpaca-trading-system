#!/usr/bin/env python3

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from technical_indicators import TechnicalIndicators

class MarketRegimeDetector:
    """
    Enhanced market regime detection for Phase 3 Intelligence Layer.
    Detects Bull/Bear/Sideways trends and volatility regimes.
    """
    
    def __init__(self):
        self.tech_indicators = TechnicalIndicators()
        self.vix_history = []  # VIX data for volatility regime
        self.market_indices = ['SPY', 'QQQ', 'IWM']  # Core market indicators
        self.sector_etfs = ['XLF', 'XLK', 'XLE', 'XLV', 'XLI']  # Sector rotation tracking
        
    def add_market_data(self, symbol: str, price: float, volume: int = 0, timestamp: datetime = None):
        """Add market data for regime analysis"""
        self.tech_indicators.add_price_data(symbol, price, volume, timestamp)
    
    def add_vix_data(self, vix_level: float, timestamp: datetime = None):
        """Add VIX data for volatility regime detection"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Keep last 50 VIX readings
        if len(self.vix_history) >= 50:
            self.vix_history.pop(0)
        
        self.vix_history.append({'vix': vix_level, 'timestamp': timestamp})
    
    def detect_trend_regime(self, symbol: str) -> Optional[Dict]:
        """
        Detect Bull/Bear/Sideways trend regime using multiple timeframes
        Returns: {'regime': str, 'strength': float, 'confidence': float}
        """
        ma_data = self.tech_indicators.calculate_moving_averages(symbol)
        if not ma_data or 'ma20' not in ma_data:
            return None
        
        current_price = ma_data['current']
        ma20 = ma_data.get('ma20', 0)
        ma50 = ma_data.get('ma50', 0)
        ma200 = ma_data.get('ma200', 0)
        
        # Trend scoring system
        score = 0
        indicators = 0
        
        # Price vs MA20
        if current_price > ma20:
            score += 1
        elif current_price < ma20:
            score -= 1
        indicators += 1
        
        # MA20 vs MA50
        if ma50 > 0:
            if ma20 > ma50:
                score += 1
            elif ma20 < ma50:
                score -= 1
            indicators += 1
        
        # MA50 vs MA200
        if ma200 > 0:
            if ma50 > ma200:
                score += 1
            elif ma50 < ma200:
                score -= 1
            indicators += 1
        
        # Calculate normalized score
        normalized_score = score / indicators if indicators > 0 else 0
        
        # Determine regime
        if normalized_score > 0.5:
            regime = "bull"
            strength = normalized_score
        elif normalized_score < -0.5:
            regime = "bear"  
            strength = abs(normalized_score)
        else:
            regime = "sideways"
            strength = 1 - abs(normalized_score)
        
        # Confidence based on number of indicators agreeing
        confidence = abs(normalized_score) if regime != "sideways" else strength
        
        return {
            'regime': regime,
            'strength': round(strength, 2),
            'confidence': round(confidence, 2),
            'score': normalized_score,
            'indicators_used': indicators
        }
    
    def detect_volatility_regime(self) -> Optional[Dict]:
        """
        Detect volatility regime using VIX levels
        Returns: {'volatility_regime': str, 'vix_level': float, 'description': str}
        """
        if not self.vix_history:
            return None
        
        current_vix = self.vix_history[-1]['vix']
        
        # VIX regime classification
        if current_vix < 15:
            regime = "low"
            description = "Complacent market, low fear"
        elif current_vix < 25:
            regime = "medium"
            description = "Normal market volatility"
        elif current_vix < 35:
            regime = "high"
            description = "Elevated fear, increased volatility"
        else:
            regime = "extreme"
            description = "Market panic, extreme volatility"
        
        # Calculate VIX trend
        if len(self.vix_history) >= 5:
            recent_vix = [v['vix'] for v in self.vix_history[-5:]]
            vix_trend = "rising" if recent_vix[-1] > recent_vix[0] else "falling"
        else:
            vix_trend = "stable"
        
        return {
            'volatility_regime': regime,
            'vix_level': current_vix,
            'vix_trend': vix_trend,
            'description': description
        }
    
    def analyze_sector_rotation(self) -> Dict:
        """
        Analyze sector rotation patterns to identify market phase
        Returns: {'rotation_phase': str, 'leading_sectors': List, 'strength': float}
        """
        sector_performance = {}
        
        # Analyze each sector ETF
        for sector in self.sector_etfs:
            ma_data = self.tech_indicators.calculate_moving_averages(sector)
            if ma_data and 'trend' in ma_data:
                # Score sector strength
                if ma_data['trend'] == 'strong_bullish':
                    sector_performance[sector] = 2
                elif ma_data['trend'] == 'bullish':
                    sector_performance[sector] = 1
                elif ma_data['trend'] == 'bearish':
                    sector_performance[sector] = -1
                elif ma_data['trend'] == 'strong_bearish':
                    sector_performance[sector] = -2
                else:
                    sector_performance[sector] = 0
        
        if not sector_performance:
            return {'rotation_phase': 'unknown', 'leading_sectors': [], 'strength': 0}
        
        # Calculate overall sector strength
        total_score = sum(sector_performance.values())
        avg_score = total_score / len(sector_performance)
        
        # Identify leading sectors
        leading_sectors = [sector for sector, score in sector_performance.items() if score > 0]
        lagging_sectors = [sector for sector, score in sector_performance.items() if score < 0]
        
        # Determine rotation phase
        if avg_score > 0.5:
            phase = "risk_on"  # Growth sectors leading
        elif avg_score < -0.5:
            phase = "risk_off"  # Defensive sectors preferred
        else:
            phase = "neutral"  # Mixed sector performance
        
        return {
            'rotation_phase': phase,
            'leading_sectors': leading_sectors,
            'lagging_sectors': lagging_sectors,
            'sector_scores': sector_performance,
            'overall_strength': round(avg_score, 2)
        }
    
    def get_comprehensive_regime_analysis(self) -> Dict:
        """
        Get comprehensive market regime analysis combining all factors
        Returns complete market regime assessment
        """
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'market_regimes': {},
            'overall_assessment': {}
        }
        
        # Analyze each market index
        regime_scores = []
        for index in self.market_indices:
            trend_regime = self.detect_trend_regime(index)
            if trend_regime:
                analysis['market_regimes'][index] = trend_regime
                
                # Convert regime to numerical score for averaging
                if trend_regime['regime'] == 'bull':
                    regime_scores.append(trend_regime['strength'])
                elif trend_regime['regime'] == 'bear':
                    regime_scores.append(-trend_regime['strength'])
                else:  # sideways
                    regime_scores.append(0)
        
        # Volatility regime
        vol_regime = self.detect_volatility_regime()
        if vol_regime:
            analysis['volatility'] = vol_regime
        
        # Sector rotation
        sector_analysis = self.analyze_sector_rotation()
        analysis['sector_rotation'] = sector_analysis
        
        # Overall market assessment
        if regime_scores:
            avg_regime_score = sum(regime_scores) / len(regime_scores)
            
            if avg_regime_score > 0.3:
                overall_regime = "bullish"
                market_confidence = avg_regime_score
            elif avg_regime_score < -0.3:
                overall_regime = "bearish"
                market_confidence = abs(avg_regime_score)
            else:
                overall_regime = "neutral"
                market_confidence = 1 - abs(avg_regime_score)
            
            analysis['overall_assessment'] = {
                'regime': overall_regime,
                'confidence': round(market_confidence, 2),
                'regime_score': round(avg_regime_score, 2),
                'indices_analyzed': len(regime_scores)
            }
        
        # Trading recommendations
        analysis['trading_recommendations'] = self._generate_trading_recommendations(analysis)
        
        return analysis
    
    def _generate_trading_recommendations(self, analysis: Dict) -> Dict:
        """Generate trading recommendations based on regime analysis"""
        recommendations = {
            'strategy': 'conservative',
            'risk_level': 'medium',
            'preferred_assets': [],
            'avoid_assets': [],
            'position_sizing': 'normal'
        }
        
        overall = analysis.get('overall_assessment', {})
        volatility = analysis.get('volatility', {})
        sector_rotation = analysis.get('sector_rotation', {})
        
        # Strategy based on regime
        if overall.get('regime') == 'bullish' and overall.get('confidence', 0) > 0.6:
            recommendations['strategy'] = 'aggressive_momentum'
            recommendations['risk_level'] = 'high'
            recommendations['position_sizing'] = 'large'
        elif overall.get('regime') == 'bullish':
            recommendations['strategy'] = 'momentum'
            recommendations['risk_level'] = 'medium'
        elif overall.get('regime') == 'bearish' and overall.get('confidence', 0) > 0.6:
            recommendations['strategy'] = 'defensive'
            recommendations['risk_level'] = 'low'
            recommendations['position_sizing'] = 'small'
        
        # Adjust for volatility
        if volatility.get('volatility_regime') in ['high', 'extreme']:
            recommendations['risk_level'] = 'low'
            recommendations['position_sizing'] = 'small'
        
        # Sector preferences
        if sector_rotation.get('rotation_phase') == 'risk_on':
            recommendations['preferred_assets'] = ['QQQ', 'XLK', 'XLF']  # Growth sectors
        elif sector_rotation.get('rotation_phase') == 'risk_off':
            recommendations['preferred_assets'] = ['XLV', 'XLP', 'XLU']  # Defensive sectors
        else:
            recommendations['preferred_assets'] = ['SPY', 'IWM']  # Broad market
        
        return recommendations

if __name__ == "__main__":
    # Test the market regime detector
    print("🔧 Testing Market Regime Detector")
    print("=" * 50)
    
    detector = MarketRegimeDetector()
    
    # Add some test data for market indices
    import random
    
    # Simulate market data for different regimes
    base_prices = {'SPY': 420.0, 'QQQ': 350.0, 'IWM': 200.0}
    
    print("📊 Adding market data...")
    for i in range(60):  # 60 data points for good analysis
        for symbol, base_price in base_prices.items():
            # Simulate bullish trend with some volatility
            change_pct = random.uniform(-0.02, 0.025)  # Slight bullish bias
            new_price = base_price * (1 + change_pct)
            base_prices[symbol] = new_price
            
            volume = random.randint(50000000, 150000000)
            detector.add_market_data(symbol, new_price, volume)
    
    # Add VIX data
    print("📈 Adding VIX data...")
    for i in range(30):
        vix_level = random.uniform(15, 25)  # Medium volatility
        detector.add_vix_data(vix_level)
    
    # Get comprehensive analysis
    print("\n🔍 Running comprehensive regime analysis...")
    analysis = detector.get_comprehensive_regime_analysis()
    
    print(f"\n📊 MARKET REGIME ANALYSIS")
    print(f"⏰ Timestamp: {analysis['timestamp']}")
    print("=" * 50)
    
    # Market regimes
    if 'market_regimes' in analysis:
        print("\n📈 TREND REGIMES:")
        for index, regime_data in analysis['market_regimes'].items():
            regime_emoji = "🐂" if regime_data['regime'] == 'bull' else "🐻" if regime_data['regime'] == 'bear' else "📈"
            print(f"   {regime_emoji} {index}: {regime_data['regime'].upper()} "
                  f"(Strength: {regime_data['strength']:.1%}, Confidence: {regime_data['confidence']:.1%})")
    
    # Volatility regime
    if 'volatility' in analysis:
        vol_data = analysis['volatility']
        vol_emoji = "😴" if vol_data['volatility_regime'] == 'low' else "😰" if vol_data['volatility_regime'] == 'high' else "🔥" if vol_data['volatility_regime'] == 'extreme' else "😐"
        print(f"\n🌊 VOLATILITY REGIME:")
        print(f"   {vol_emoji} {vol_data['volatility_regime'].upper()} (VIX: {vol_data['vix_level']:.1f})")
        print(f"   📝 {vol_data['description']}")
    
    # Overall assessment
    if 'overall_assessment' in analysis:
        overall = analysis['overall_assessment']
        overall_emoji = "🚀" if overall['regime'] == 'bullish' else "📉" if overall['regime'] == 'bearish' else "⚖️"
        print(f"\n🎯 OVERALL MARKET ASSESSMENT:")
        print(f"   {overall_emoji} Regime: {overall['regime'].upper()}")
        print(f"   🎯 Confidence: {overall['confidence']:.1%}")
        print(f"   📊 Score: {overall['regime_score']:.2f}")
    
    # Trading recommendations
    if 'trading_recommendations' in analysis:
        recs = analysis['trading_recommendations']
        strategy_emoji = "⚡" if recs['strategy'] == 'aggressive_momentum' else "🎯" if recs['strategy'] == 'momentum' else "🛡️"
        print(f"\n💡 TRADING RECOMMENDATIONS:")
        print(f"   {strategy_emoji} Strategy: {recs['strategy'].upper()}")
        print(f"   ⚠️ Risk Level: {recs['risk_level'].upper()}")
        print(f"   📏 Position Sizing: {recs['position_sizing'].upper()}")
        if recs['preferred_assets']:
            print(f"   ✅ Preferred Assets: {', '.join(recs['preferred_assets'])}")
    
    print("\n✅ Market Regime Detector Ready!")