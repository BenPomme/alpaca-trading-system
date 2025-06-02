#!/usr/bin/env python3

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math

class PatternRecognition:
    """
    Pattern recognition for Phase 3 Intelligence Layer.
    Detects support/resistance levels, breakouts, and mean reversion patterns.
    """
    
    def __init__(self, lookback_period: int = 20):
        self.lookback_period = lookback_period
        self.price_history = {}  # symbol -> list of price data
        self.volume_history = {}  # symbol -> list of volume data
        self.support_resistance_cache = {}  # Cache for S/R levels
    
    def add_price_data(self, symbol: str, price: float, volume: int = 0, timestamp: datetime = None):
        """Add new price and volume data for pattern analysis"""
        if timestamp is None:
            timestamp = datetime.now()
            
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            self.volume_history[symbol] = []
        
        # Keep last 50 data points for pattern analysis
        if len(self.price_history[symbol]) >= 50:
            self.price_history[symbol].pop(0)
            self.volume_history[symbol].pop(0)
        
        self.price_history[symbol].append({
            'price': price, 
            'volume': volume,
            'timestamp': timestamp,
            'high': price,  # Simplified - in real implementation would track OHLC
            'low': price,
            'close': price
        })
        
        # Clear S/R cache when new data added
        if symbol in self.support_resistance_cache:
            del self.support_resistance_cache[symbol]
    
    def find_support_resistance_levels(self, symbol: str, sensitivity: float = 0.02) -> Optional[Dict]:
        """
        Find dynamic support and resistance levels
        Returns: {'support_levels': List[float], 'resistance_levels': List[float], 'current_price': float}
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < self.lookback_period:
            return None
        
        # Check cache first
        if symbol in self.support_resistance_cache:
            return self.support_resistance_cache[symbol]
        
        prices = [p['price'] for p in self.price_history[symbol]]
        current_price = prices[-1]
        
        # Find local minima (potential support) and maxima (potential resistance)
        support_levels = []
        resistance_levels = []
        
        # Look for pivot points in the last lookback_period
        for i in range(2, len(prices) - 2):
            price = prices[i]
            
            # Check for local minimum (support)
            if (prices[i] < prices[i-1] and prices[i] < prices[i-2] and 
                prices[i] < prices[i+1] and prices[i] < prices[i+2]):
                support_levels.append(price)
            
            # Check for local maximum (resistance)
            if (prices[i] > prices[i-1] and prices[i] > prices[i-2] and 
                prices[i] > prices[i+1] and prices[i] > prices[i+2]):
                resistance_levels.append(price)
        
        # Remove levels too close to each other (within sensitivity)
        def consolidate_levels(levels):
            if not levels:
                return []
            
            levels.sort()
            consolidated = [levels[0]]
            
            for level in levels[1:]:
                if abs(level - consolidated[-1]) / consolidated[-1] > sensitivity:
                    consolidated.append(level)
            
            return consolidated
        
        support_levels = consolidate_levels(support_levels)
        resistance_levels = consolidate_levels(resistance_levels)
        
        # Keep only the most relevant levels (closest to current price)
        def filter_relevant_levels(levels, current_price, max_levels=3):
            if not levels:
                return []
            
            # Sort by distance from current price
            levels_with_distance = [(level, abs(level - current_price) / current_price) for level in levels]
            levels_with_distance.sort(key=lambda x: x[1])
            
            return [level for level, _ in levels_with_distance[:max_levels]]
        
        relevant_support = filter_relevant_levels([s for s in support_levels if s < current_price], current_price)
        relevant_resistance = filter_relevant_levels([r for r in resistance_levels if r > current_price], current_price)
        
        result = {
            'support_levels': relevant_support,
            'resistance_levels': relevant_resistance,
            'current_price': current_price,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache the result
        self.support_resistance_cache[symbol] = result
        
        return result
    
    def detect_breakout_pattern(self, symbol: str, volume_confirmation: bool = True) -> Optional[Dict]:
        """
        Detect breakout patterns above resistance or below support
        Returns: {'pattern': str, 'level': float, 'volume_confirmed': bool, 'strength': float}
        """
        sr_levels = self.find_support_resistance_levels(symbol)
        if not sr_levels:
            return None
        
        if symbol not in self.price_history or len(self.price_history[symbol]) < 5:
            return None
        
        current_data = self.price_history[symbol][-1]
        current_price = current_data['price']
        current_volume = current_data['volume']
        
        # Calculate average volume for comparison
        recent_volumes = [p['volume'] for p in self.price_history[symbol][-10:] if p['volume'] > 0]
        avg_volume = sum(recent_volumes) / len(recent_volumes) if recent_volumes else 0
        
        # Check for resistance breakout
        for resistance in sr_levels['resistance_levels']:
            if current_price > resistance:
                # Calculate breakout strength
                breakout_percentage = (current_price - resistance) / resistance
                
                # Volume confirmation
                volume_confirmed = False
                if volume_confirmation and avg_volume > 0:
                    volume_ratio = current_volume / avg_volume
                    volume_confirmed = volume_ratio > 1.5  # 50% above average
                
                return {
                    'pattern': 'resistance_breakout',
                    'level': resistance,
                    'current_price': current_price,
                    'breakout_percentage': round(breakout_percentage * 100, 2),
                    'volume_confirmed': volume_confirmed,
                    'volume_ratio': round(current_volume / avg_volume, 2) if avg_volume > 0 else 0,
                    'strength': min(breakout_percentage * 10, 1.0),  # Normalize to 0-1
                    'signal': 'bullish'
                }
        
        # Check for support breakdown
        for support in sr_levels['support_levels']:
            if current_price < support:
                # Calculate breakdown strength
                breakdown_percentage = (support - current_price) / support
                
                # Volume confirmation
                volume_confirmed = False
                if volume_confirmation and avg_volume > 0:
                    volume_ratio = current_volume / avg_volume
                    volume_confirmed = volume_ratio > 1.5
                
                return {
                    'pattern': 'support_breakdown',
                    'level': support,
                    'current_price': current_price,
                    'breakdown_percentage': round(breakdown_percentage * 100, 2),
                    'volume_confirmed': volume_confirmed,
                    'volume_ratio': round(current_volume / avg_volume, 2) if avg_volume > 0 else 0,
                    'strength': min(breakdown_percentage * 10, 1.0),
                    'signal': 'bearish'
                }
        
        return None
    
    def detect_mean_reversion_setup(self, symbol: str, std_dev_threshold: float = 2.0) -> Optional[Dict]:
        """
        Detect mean reversion opportunities when price is far from average
        Returns: {'pattern': str, 'deviation': float, 'signal': str, 'strength': float}
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < self.lookback_period:
            return None
        
        prices = [p['price'] for p in self.price_history[symbol][-self.lookback_period:]]
        current_price = prices[-1]
        
        # Calculate mean and standard deviation
        mean_price = sum(prices) / len(prices)
        variance = sum((price - mean_price) ** 2 for price in prices) / len(prices)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return None
        
        # Calculate z-score (how many standard deviations from mean)
        z_score = (current_price - mean_price) / std_dev
        
        # Check for mean reversion setup
        if abs(z_score) >= std_dev_threshold:
            if z_score > 0:
                # Price is significantly above mean - potential sell
                signal = 'bearish'
                pattern = 'overbought_reversion'
            else:
                # Price is significantly below mean - potential buy
                signal = 'bullish'
                pattern = 'oversold_reversion'
            
            # Calculate strength based on how far from mean
            strength = min(abs(z_score) / 3.0, 1.0)  # Normalize to 0-1, cap at 3 std devs
            
            return {
                'pattern': pattern,
                'z_score': round(z_score, 2),
                'deviation_percentage': round((current_price - mean_price) / mean_price * 100, 2),
                'mean_price': round(mean_price, 2),
                'current_price': current_price,
                'signal': signal,
                'strength': round(strength, 2),
                'std_dev': round(std_dev, 2)
            }
        
        return None
    
    def detect_consolidation_pattern(self, symbol: str, volatility_threshold: float = 0.02) -> Optional[Dict]:
        """
        Detect consolidation patterns (low volatility periods before potential breakouts)
        Returns: {'pattern': str, 'volatility': float, 'duration': int, 'breakout_probability': float}
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < 10:
            return None
        
        recent_prices = [p['price'] for p in self.price_history[symbol][-10:]]
        
        # Calculate recent volatility
        if len(recent_prices) < 2:
            return None
        
        price_changes = []
        for i in range(1, len(recent_prices)):
            change_pct = abs(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
            price_changes.append(change_pct)
        
        avg_volatility = sum(price_changes) / len(price_changes)
        
        # Check if we're in a low volatility period
        if avg_volatility < volatility_threshold:
            # Calculate consolidation duration
            consolidation_duration = 0
            for i in range(len(price_changes) - 1, -1, -1):
                if price_changes[i] < volatility_threshold:
                    consolidation_duration += 1
                else:
                    break
            
            # Calculate breakout probability (longer consolidation = higher probability)
            breakout_probability = min(consolidation_duration / 10.0, 0.8)  # Cap at 80%
            
            # Determine price range during consolidation
            consolidation_prices = recent_prices[-consolidation_duration-1:]
            price_range = max(consolidation_prices) - min(consolidation_prices)
            range_percentage = price_range / recent_prices[-1] * 100
            
            return {
                'pattern': 'consolidation',
                'volatility': round(avg_volatility * 100, 2),  # Convert to percentage
                'duration': consolidation_duration,
                'breakout_probability': round(breakout_probability, 2),
                'price_range_pct': round(range_percentage, 2),
                'signal': 'neutral',
                'strength': breakout_probability
            }
        
        return None
    
    def get_comprehensive_pattern_analysis(self, symbol: str) -> Dict:
        """
        Get comprehensive pattern analysis combining all pattern types
        Returns complete pattern recognition results
        """
        analysis = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'patterns': {},
            'trading_signals': []
        }
        
        # Support/Resistance levels
        sr_levels = self.find_support_resistance_levels(symbol)
        if sr_levels:
            analysis['patterns']['support_resistance'] = sr_levels
        
        # Breakout patterns
        breakout = self.detect_breakout_pattern(symbol)
        if breakout:
            analysis['patterns']['breakout'] = breakout
            analysis['trading_signals'].append({
                'signal': breakout['signal'],
                'strength': breakout['strength'],
                'pattern': breakout['pattern'],
                'confidence': 'high' if breakout['volume_confirmed'] else 'medium'
            })
        
        # Mean reversion patterns
        mean_reversion = self.detect_mean_reversion_setup(symbol)
        if mean_reversion:
            analysis['patterns']['mean_reversion'] = mean_reversion
            analysis['trading_signals'].append({
                'signal': mean_reversion['signal'],
                'strength': mean_reversion['strength'],
                'pattern': mean_reversion['pattern'],
                'confidence': 'high' if mean_reversion['strength'] > 0.7 else 'medium'
            })
        
        # Consolidation patterns
        consolidation = self.detect_consolidation_pattern(symbol)
        if consolidation:
            analysis['patterns']['consolidation'] = consolidation
            if consolidation['breakout_probability'] > 0.6:
                analysis['trading_signals'].append({
                    'signal': 'watch',
                    'strength': consolidation['breakout_probability'],
                    'pattern': 'consolidation_breakout_setup',
                    'confidence': 'medium'
                })
        
        # Overall pattern assessment
        if analysis['trading_signals']:
            # Count signals by type
            bullish_signals = len([s for s in analysis['trading_signals'] if s['signal'] == 'bullish'])
            bearish_signals = len([s for s in analysis['trading_signals'] if s['signal'] == 'bearish'])
            
            if bullish_signals > bearish_signals:
                overall_signal = 'bullish'
                signal_strength = bullish_signals / len(analysis['trading_signals'])
            elif bearish_signals > bullish_signals:
                overall_signal = 'bearish'
                signal_strength = bearish_signals / len(analysis['trading_signals'])
            else:
                overall_signal = 'neutral'
                signal_strength = 0.5
            
            analysis['overall_assessment'] = {
                'signal': overall_signal,
                'strength': round(signal_strength, 2),
                'pattern_count': len(analysis['patterns']),
                'signal_count': len(analysis['trading_signals'])
            }
        
        return analysis

if __name__ == "__main__":
    # Test pattern recognition
    print("🔧 Testing Pattern Recognition Module")
    print("=" * 50)
    
    pattern_rec = PatternRecognition()
    
    # Generate test data with patterns
    import random
    
    print("📊 Generating test data with patterns...")
    
    # Simulate a stock with consolidation followed by breakout
    base_price = 100.0
    prices = []
    
    # Phase 1: Consolidation (low volatility)
    for i in range(15):
        change = random.uniform(-0.01, 0.01)  # Low volatility
        base_price += base_price * change
        volume = random.randint(100000, 200000)
        pattern_rec.add_price_data('TEST', base_price, volume)
        prices.append(base_price)
    
    # Phase 2: Breakout (higher volatility and volume)
    for i in range(10):
        change = random.uniform(0.01, 0.03)  # Upward breakout
        base_price += base_price * change
        volume = random.randint(300000, 500000)  # Higher volume
        pattern_rec.add_price_data('TEST', base_price, volume)
        prices.append(base_price)
    
    print(f"📈 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
    print(f"📊 Total data points: {len(prices)}")
    
    # Get comprehensive analysis
    print("\n🔍 Running pattern analysis...")
    analysis = pattern_rec.get_comprehensive_pattern_analysis('TEST')
    
    print(f"\n📊 PATTERN ANALYSIS FOR {analysis['symbol']}")
    print(f"⏰ Timestamp: {analysis['timestamp']}")
    print("=" * 50)
    
    # Display detected patterns
    for pattern_type, pattern_data in analysis['patterns'].items():
        print(f"\n📈 {pattern_type.upper().replace('_', ' ')} PATTERN:")
        
        if pattern_type == 'support_resistance':
            if pattern_data['support_levels']:
                print(f"   🛡️ Support Levels: {[f'${s:.2f}' for s in pattern_data['support_levels']]}")
            if pattern_data['resistance_levels']:
                print(f"   🚧 Resistance Levels: {[f'${r:.2f}' for r in pattern_data['resistance_levels']]}")
            print(f"   💰 Current Price: ${pattern_data['current_price']:.2f}")
        
        elif pattern_type == 'breakout':
            signal_emoji = "🚀" if pattern_data['signal'] == 'bullish' else "📉"
            volume_emoji = "📊" if pattern_data['volume_confirmed'] else "❓"
            print(f"   {signal_emoji} Pattern: {pattern_data['pattern'].replace('_', ' ').title()}")
            print(f"   🎯 Level: ${pattern_data['level']:.2f}")
            print(f"   💪 Strength: {pattern_data['strength']:.1%}")
            print(f"   {volume_emoji} Volume Confirmed: {pattern_data['volume_confirmed']}")
        
        elif pattern_type == 'mean_reversion':
            signal_emoji = "🔄" if pattern_data['signal'] == 'bullish' else "🔽"
            print(f"   {signal_emoji} Pattern: {pattern_data['pattern'].replace('_', ' ').title()}")
            print(f"   📏 Z-Score: {pattern_data['z_score']}")
            print(f"   📊 Deviation: {pattern_data['deviation_percentage']:.1f}%")
            print(f"   💪 Strength: {pattern_data['strength']:.1%}")
        
        elif pattern_type == 'consolidation':
            print(f"   📦 Volatility: {pattern_data['volatility']:.2f}%")
            print(f"   ⏱️ Duration: {pattern_data['duration']} periods")
            print(f"   🎯 Breakout Probability: {pattern_data['breakout_probability']:.1%}")
    
    # Trading signals
    if analysis['trading_signals']:
        print(f"\n💡 TRADING SIGNALS:")
        for signal in analysis['trading_signals']:
            signal_emoji = "🟢" if signal['signal'] == 'bullish' else "🔴" if signal['signal'] == 'bearish' else "🟡"
            print(f"   {signal_emoji} {signal['signal'].upper()} - {signal['pattern'].replace('_', ' ').title()}")
            print(f"      💪 Strength: {signal['strength']:.1%} | 🎯 Confidence: {signal['confidence'].upper()}")
    
    # Overall assessment
    if 'overall_assessment' in analysis:
        overall = analysis['overall_assessment']
        overall_emoji = "🚀" if overall['signal'] == 'bullish' else "📉" if overall['signal'] == 'bearish' else "⚖️"
        print(f"\n🎯 OVERALL PATTERN ASSESSMENT:")
        print(f"   {overall_emoji} Signal: {overall['signal'].upper()}")
        print(f"   💪 Strength: {overall['strength']:.1%}")
        print(f"   📊 Patterns Detected: {overall['pattern_count']}")
    
    print("\n✅ Pattern Recognition Module Ready!")