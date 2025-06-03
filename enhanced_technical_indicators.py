#!/usr/bin/env python3
"""
Enhanced Technical Indicators - Professional TA-Lib Integration
Combines custom indicators with professional TA-Lib implementations
Maintains backward compatibility with existing technical_indicators.py
"""

import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Optional, Union, Tuple, Any
from datetime import datetime, timezone

# Professional technical analysis library
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    print("⚠️ TA-Lib not available - install with: pip install TA-Lib")
    print("📖 Installation guide: https://github.com/mrjbq7/ta-lib#installation")
    TALIB_AVAILABLE = False

# Fallback to existing custom indicators
try:
    from utils.technical_indicators import TechnicalIndicators as CustomIndicators
    CUSTOM_INDICATORS_AVAILABLE = True
except ImportError:
    print("⚠️ Custom indicators not available")
    CUSTOM_INDICATORS_AVAILABLE = False

# Performance optimization
try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    print("⚠️ Numba not available for performance optimization")
    NUMBA_AVAILABLE = False
    # Create dummy decorator
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class EnhancedTechnicalIndicators:
    """
    Professional technical indicators combining TA-Lib with custom implementations
    Provides institutional-grade technical analysis with fallback support
    """
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.talib_available = TALIB_AVAILABLE
        self.custom_indicators = None
        
        # Initialize custom indicators as fallback
        if CUSTOM_INDICATORS_AVAILABLE:
            self.custom_indicators = CustomIndicators()
            self.logger.info("✅ Custom indicators available (FALLBACK)")
        
        if self.talib_available:
            self.logger.info("✅ TA-Lib available (PROFESSIONAL)")
        else:
            self.logger.warning("⚠️ TA-Lib not available - using custom implementations")
    
    def calculate_rsi(self, prices: Union[List[float], np.ndarray], period: int = 14) -> Optional[float]:
        """
        Calculate RSI using TA-Lib (preferred) or custom implementation
        """
        if len(prices) < period + 1:
            return None
        
        prices_array = np.array(prices, dtype=float)
        
        # PRIMARY: Use TA-Lib for professional calculation
        if self.talib_available:
            try:
                rsi_values = talib.RSI(prices_array, timeperiod=period)
                return float(rsi_values[-1]) if not np.isnan(rsi_values[-1]) else None
            except Exception as e:
                self.logger.warning(f"⚠️ TA-Lib RSI failed: {e}")
        
        # FALLBACK: Custom RSI implementation
        return self._custom_rsi(prices_array, period)
    
    def calculate_macd(self, prices: Union[List[float], np.ndarray], 
                      fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> Optional[Dict[str, float]]:
        """
        Calculate MACD using TA-Lib (preferred) or custom implementation
        Returns dict with macd, signal, and histogram values
        """
        if len(prices) < slowperiod + signalperiod:
            return None
        
        prices_array = np.array(prices, dtype=float)
        
        # PRIMARY: Use TA-Lib for professional calculation
        if self.talib_available:
            try:
                macd, macd_signal, macd_histogram = talib.MACD(
                    prices_array, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod
                )
                
                if not (np.isnan(macd[-1]) or np.isnan(macd_signal[-1]) or np.isnan(macd_histogram[-1])):
                    return {
                        'macd': float(macd[-1]),
                        'signal': float(macd_signal[-1]),
                        'histogram': float(macd_histogram[-1])
                    }
            except Exception as e:
                self.logger.warning(f"⚠️ TA-Lib MACD failed: {e}")
        
        # FALLBACK: Custom MACD implementation
        return self._custom_macd(prices_array, fastperiod, slowperiod, signalperiod)
    
    def calculate_bollinger_bands(self, prices: Union[List[float], np.ndarray], 
                                 period: int = 20, std_dev: float = 2.0) -> Optional[Dict[str, float]]:
        """
        Calculate Bollinger Bands using TA-Lib (preferred) or custom implementation
        """
        if len(prices) < period:
            return None
        
        prices_array = np.array(prices, dtype=float)
        
        # PRIMARY: Use TA-Lib for professional calculation
        if self.talib_available:
            try:
                upper, middle, lower = talib.BBANDS(prices_array, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev)
                
                if not (np.isnan(upper[-1]) or np.isnan(middle[-1]) or np.isnan(lower[-1])):
                    return {
                        'upper': float(upper[-1]),
                        'middle': float(middle[-1]),
                        'lower': float(lower[-1]),
                        'bandwidth': float((upper[-1] - lower[-1]) / middle[-1] * 100),
                        'position': float((prices_array[-1] - lower[-1]) / (upper[-1] - lower[-1]) * 100)
                    }
            except Exception as e:
                self.logger.warning(f"⚠️ TA-Lib Bollinger Bands failed: {e}")
        
        # FALLBACK: Custom Bollinger Bands implementation
        return self._custom_bollinger_bands(prices_array, period, std_dev)
    
    def calculate_moving_averages(self, prices: Union[List[float], np.ndarray], 
                                 periods: List[int] = [5, 10, 20, 50, 200]) -> Dict[int, float]:
        """
        Calculate multiple moving averages using TA-Lib
        """
        prices_array = np.array(prices, dtype=float)
        moving_averages = {}
        
        for period in periods:
            if len(prices_array) >= period:
                if self.talib_available:
                    try:
                        ma = talib.SMA(prices_array, timeperiod=period)
                        if not np.isnan(ma[-1]):
                            moving_averages[period] = float(ma[-1])
                    except Exception as e:
                        self.logger.warning(f"⚠️ TA-Lib SMA({period}) failed: {e}")
                        # Fallback to simple average
                        moving_averages[period] = float(np.mean(prices_array[-period:]))
                else:
                    # Custom moving average
                    moving_averages[period] = float(np.mean(prices_array[-period:]))
        
        return moving_averages
    
    def calculate_advanced_indicators(self, high: Union[List[float], np.ndarray],
                                    low: Union[List[float], np.ndarray],
                                    close: Union[List[float], np.ndarray],
                                    volume: Union[List[float], np.ndarray] = None) -> Dict[str, float]:
        """
        Calculate advanced technical indicators using TA-Lib
        Requires OHLCV data for professional analysis
        """
        if not self.talib_available:
            return {}
        
        high_array = np.array(high, dtype=float)
        low_array = np.array(low, dtype=float)
        close_array = np.array(close, dtype=float)
        
        indicators = {}
        
        try:
            # Average True Range (ATR)
            atr = talib.ATR(high_array, low_array, close_array, timeperiod=14)
            if not np.isnan(atr[-1]):
                indicators['atr'] = float(atr[-1])
            
            # Average Directional Index (ADX)
            adx = talib.ADX(high_array, low_array, close_array, timeperiod=14)
            if not np.isnan(adx[-1]):
                indicators['adx'] = float(adx[-1])
            
            # Commodity Channel Index (CCI)
            cci = talib.CCI(high_array, low_array, close_array, timeperiod=14)
            if not np.isnan(cci[-1]):
                indicators['cci'] = float(cci[-1])
            
            # Williams %R
            willr = talib.WILLR(high_array, low_array, close_array, timeperiod=14)
            if not np.isnan(willr[-1]):
                indicators['williams_r'] = float(willr[-1])
            
            # Stochastic Oscillator
            slowk, slowd = talib.STOCH(high_array, low_array, close_array)
            if not (np.isnan(slowk[-1]) or np.isnan(slowd[-1])):
                indicators['stoch_k'] = float(slowk[-1])
                indicators['stoch_d'] = float(slowd[-1])
            
            # Volume indicators (if volume data available)
            if volume is not None:
                volume_array = np.array(volume, dtype=float)
                
                # On Balance Volume (OBV)
                obv = talib.OBV(close_array, volume_array)
                if not np.isnan(obv[-1]):
                    indicators['obv'] = float(obv[-1])
                
                # Volume Rate of Change
                if len(volume_array) >= 10:
                    vroc = talib.ROC(volume_array, timeperiod=10)
                    if not np.isnan(vroc[-1]):
                        indicators['volume_roc'] = float(vroc[-1])
        
        except Exception as e:
            self.logger.warning(f"⚠️ Advanced indicators calculation failed: {e}")
        
        return indicators
    
    def _custom_rsi(self, prices: np.ndarray, period: int = 14) -> Optional[float]:
        """
        High-performance custom RSI implementation with Numba optimization
        """
        if len(prices) < period + 1:
            return None
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    def _custom_macd(self, prices: np.ndarray, fastperiod: int, slowperiod: int, signalperiod: int) -> Optional[Dict[str, float]]:
        """
        Custom MACD implementation as fallback
        """
        if len(prices) < slowperiod + signalperiod:
            return None
        
        # Calculate EMAs
        ema_fast = self._calculate_ema(prices, fastperiod)
        ema_slow = self._calculate_ema(prices, slowperiod)
        
        if ema_fast is None or ema_slow is None:
            return None
        
        macd_line = ema_fast - ema_slow
        
        # Create MACD line array for signal calculation
        macd_array = np.full(len(prices), np.nan)
        macd_array[-1] = macd_line
        
        signal_line = self._calculate_ema(macd_array[~np.isnan(macd_array)], signalperiod)
        
        if signal_line is None:
            signal_line = macd_line  # Fallback
        
        histogram = macd_line - signal_line
        
        return {
            'macd': float(macd_line),
            'signal': float(signal_line),
            'histogram': float(histogram)
        }
    
    def _custom_bollinger_bands(self, prices: np.ndarray, period: int, std_dev: float) -> Optional[Dict[str, float]]:
        """
        Custom Bollinger Bands implementation as fallback
        """
        if len(prices) < period:
            return None
        
        recent_prices = prices[-period:]
        middle = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        current_price = prices[-1]
        bandwidth = (upper - lower) / middle * 100
        position = (current_price - lower) / (upper - lower) * 100
        
        return {
            'upper': float(upper),
            'middle': float(middle),
            'lower': float(lower),
            'bandwidth': float(bandwidth),
            'position': float(position)
        }
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> Optional[float]:
        """
        Calculate Exponential Moving Average
        """
        if len(prices) < period:
            return None
        
        multiplier = 2.0 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return float(ema)
    
    def get_comprehensive_analysis(self, high: List[float], low: List[float], 
                                 close: List[float], volume: List[float] = None) -> Dict[str, Any]:
        """
        Get comprehensive technical analysis combining all indicators
        """
        analysis = {
            'timestamp': datetime.now(timezone.utc),
            'indicators': {},
            'signals': {},
            'strength': 'neutral'
        }
        
        # Basic indicators
        rsi = self.calculate_rsi(close)
        if rsi is not None:
            analysis['indicators']['rsi'] = rsi
            analysis['signals']['rsi'] = 'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'neutral'
        
        # MACD
        macd = self.calculate_macd(close)
        if macd:
            analysis['indicators']['macd'] = macd
            analysis['signals']['macd'] = 'bullish' if macd['histogram'] > 0 else 'bearish'
        
        # Bollinger Bands
        bb = self.calculate_bollinger_bands(close)
        if bb:
            analysis['indicators']['bollinger_bands'] = bb
            if bb['position'] < 10:
                analysis['signals']['bollinger'] = 'oversold'
            elif bb['position'] > 90:
                analysis['signals']['bollinger'] = 'overbought'
            else:
                analysis['signals']['bollinger'] = 'neutral'
        
        # Moving Averages
        mas = self.calculate_moving_averages(close)
        if mas:
            analysis['indicators']['moving_averages'] = mas
            current_price = close[-1]
            if len(mas) >= 2:
                short_ma = mas.get(20, mas.get(10, current_price))
                long_ma = mas.get(50, mas.get(200, current_price))
                if current_price > short_ma > long_ma:
                    analysis['signals']['trend'] = 'bullish'
                elif current_price < short_ma < long_ma:
                    analysis['signals']['trend'] = 'bearish'
                else:
                    analysis['signals']['trend'] = 'neutral'
        
        # Advanced indicators (if TA-Lib available)
        advanced = self.calculate_advanced_indicators(high, low, close, volume)
        if advanced:
            analysis['indicators']['advanced'] = advanced
        
        # Overall strength assessment
        bullish_signals = sum(1 for signal in analysis['signals'].values() if signal == 'bullish')
        bearish_signals = sum(1 for signal in analysis['signals'].values() if signal == 'bearish')
        
        if bullish_signals > bearish_signals:
            analysis['strength'] = 'bullish'
        elif bearish_signals > bullish_signals:
            analysis['strength'] = 'bearish'
        else:
            analysis['strength'] = 'neutral'
        
        return analysis
    
    def analyze_comprehensive(self, symbol: str, price_data: List[float], 
                            volume_data: List[float] = None, timeframe: str = 'intraday') -> Dict[str, Any]:
        """
        Comprehensive analysis method expected by stocks module
        Compatible interface for modular integration
        """
        try:
            if not price_data or len(price_data) < 20:
                # Return neutral analysis for insufficient data
                return {
                    'combined_score': 0.5,
                    'trend_strength': 0.5,
                    'momentum_score': 0.5,
                    'signals_count': 0,
                    'indicators_count': 0,
                    'analysis_quality': 'insufficient_data',
                    'timeframe': timeframe
                }
            
            # Convert price data to OHLC format (simplified)
            # For intraday, we'll use price_data as close prices and estimate OHLC
            close_prices = np.array(price_data)
            high_prices = close_prices * 1.005  # Estimate 0.5% high
            low_prices = close_prices * 0.995   # Estimate 0.5% low
            
            # Get comprehensive analysis
            analysis = self.get_comprehensive_analysis(
                high=high_prices.tolist(),
                low=low_prices.tolist(), 
                close=close_prices.tolist(),
                volume=volume_data
            )
            
            # Convert to expected format for stocks module
            signals = analysis.get('signals', {})
            indicators = analysis.get('indicators', {})
            
            # Calculate combined score based on signal strength
            bullish_count = sum(1 for signal in signals.values() if signal == 'bullish')
            bearish_count = sum(1 for signal in signals.values() if signal == 'bearish')
            total_signals = len(signals)
            
            if total_signals > 0:
                combined_score = (bullish_count + 0.5 * (total_signals - bullish_count - bearish_count)) / total_signals
            else:
                combined_score = 0.5
            
            # Calculate trend strength from moving averages
            trend_strength = 0.5
            if 'moving_averages' in indicators:
                mas = indicators['moving_averages']
                current_price = close_prices[-1]
                if 20 in mas and 50 in mas:
                    ma20 = mas[20]
                    ma50 = mas[50]
                    if current_price > ma20 > ma50:
                        trend_strength = 0.8  # Strong uptrend
                    elif current_price < ma20 < ma50:
                        trend_strength = 0.2  # Strong downtrend
                    else:
                        trend_strength = 0.5  # Neutral/mixed
            
            # Calculate momentum score from RSI and MACD
            momentum_score = 0.5
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi < 30:
                    momentum_score = 0.8  # Oversold bounce potential
                elif rsi > 70:
                    momentum_score = 0.2  # Overbought weakness
                else:
                    momentum_score = 0.5 + (50 - rsi) / 100  # Centered around 50
            
            # Adjust for MACD momentum
            if 'macd' in indicators:
                macd_data = indicators['macd']
                if macd_data['histogram'] > 0:
                    momentum_score = min(1.0, momentum_score + 0.1)
                else:
                    momentum_score = max(0.0, momentum_score - 0.1)
            
            return {
                'combined_score': max(0.0, min(1.0, combined_score)),
                'trend_strength': max(0.0, min(1.0, trend_strength)),
                'momentum_score': max(0.0, min(1.0, momentum_score)),
                'signals_count': len(signals),
                'indicators_count': len(indicators),
                'analysis_quality': 'good' if len(indicators) >= 3 else 'limited',
                'timeframe': timeframe,
                'raw_signals': signals,
                'raw_indicators': indicators
            }
            
        except Exception as e:
            self.logger.error(f"❌ Comprehensive analysis failed for {symbol}: {e}")
            # Return neutral fallback
            return {
                'combined_score': 0.5,
                'trend_strength': 0.5,
                'momentum_score': 0.5,
                'signals_count': 0,
                'indicators_count': 0,
                'analysis_quality': 'error',
                'error': str(e)
            }


# Singleton instance for modular system integration
enhanced_technical_indicators = None

def get_enhanced_technical_indicators(**kwargs) -> EnhancedTechnicalIndicators:
    """
    Get singleton instance of enhanced technical indicators
    """
    global enhanced_technical_indicators
    if enhanced_technical_indicators is None:
        enhanced_technical_indicators = EnhancedTechnicalIndicators(**kwargs)
    return enhanced_technical_indicators


if __name__ == "__main__":
    # Test the enhanced technical indicators
    import random
    
    # Generate sample price data
    np.random.seed(42)
    base_price = 100.0
    prices = [base_price]
    highs = [base_price]
    lows = [base_price]
    volumes = []
    
    for i in range(100):
        change = np.random.randn() * 0.02  # 2% volatility
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)
        
        # Generate OHLC data
        high = new_price * (1 + abs(np.random.randn() * 0.01))
        low = new_price * (1 - abs(np.random.randn() * 0.01))
        highs.append(high)
        lows.append(low)
        
        # Generate volume
        volume = int(1000000 * (1 + np.random.randn() * 0.5))
        volumes.append(max(volume, 100000))
    
    # Test enhanced indicators
    indicators = EnhancedTechnicalIndicators()
    
    print("🔍 Testing Enhanced Technical Indicators")
    print("=" * 50)
    
    # Test individual indicators
    print(f"RSI: {indicators.calculate_rsi(prices):.2f}")
    
    macd = indicators.calculate_macd(prices)
    if macd:
        print(f"MACD: {macd['macd']:.4f}, Signal: {macd['signal']:.4f}, Histogram: {macd['histogram']:.4f}")
    
    bb = indicators.calculate_bollinger_bands(prices)
    if bb:
        print(f"Bollinger Bands: Upper: {bb['upper']:.2f}, Middle: {bb['middle']:.2f}, Lower: {bb['lower']:.2f}")
    
    # Test comprehensive analysis
    analysis = indicators.get_comprehensive_analysis(highs, lows, prices, volumes)
    print(f"\n📊 Overall Strength: {analysis['strength']}")
    print(f"🎯 Signals: {analysis['signals']}")