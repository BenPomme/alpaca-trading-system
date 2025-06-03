#!/usr/bin/env python3

import math
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta

class TechnicalIndicators:
    """
    Technical analysis indicators for Phase 3 Intelligence Layer.
    Implements RSI, MACD, Bollinger Bands, and Volume analysis.
    """
    
    def __init__(self):
        self.price_history = {}  # symbol -> list of prices
        self.volume_history = {}  # symbol -> list of volumes
        self.initialized_symbols = set()
        self.macd_history = {} # symbol -> list of macd values for signal line calculation
    
    def add_price_data(self, symbol: str, price: float, volume: int = 0, timestamp: datetime = None, high: Optional[float]=None, low: Optional[float]=None):
        """Add new price, volume, high, and low data for a symbol"""
        if timestamp is None:
            timestamp = datetime.now()
            
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            self.volume_history[symbol] = []
            self.macd_history[symbol] = [] # Initialize for MACD

        # Store more data points if needed for longer period calculations like ADX
        # Max length could be adjusted based on longest period (e.g., ADX might need ~50 for 14-period)
        max_data_points = 250 # Increased for longer indicators
        
        if len(self.price_history[symbol]) >= max_data_points:
            self.price_history[symbol].pop(0)
            self.volume_history[symbol].pop(0)
            if self.macd_history[symbol]: self.macd_history[symbol].pop(0)

        data_point = {'price': price, 'timestamp': timestamp}
        if high is not None: data_point['high'] = high
        if low is not None: data_point['low'] = low
        
        self.price_history[symbol].append(data_point)
        self.volume_history[symbol].append({'volume': volume, 'timestamp': timestamp})
        
        # Mark as initialized once we have enough data (e.g., for a 20-period MA or RSI)
        if len(self.price_history[symbol]) >= 20: # Basic initialization
            self.initialized_symbols.add(symbol)
    
    def calculate_rsi(self, symbol: str, period: int = 14) -> Optional[float]:
        """
        Calculate RSI (Relative Strength Index)
        RSI < 30: Oversold (potential buy signal)
        RSI > 70: Overbought (potential sell signal)
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < period + 1:
            return None
        
        prices = [p['price'] for p in self.price_history[symbol]]
        
        # Calculate price changes
        deltas = []
        for i in range(1, len(prices)):
            deltas.append(prices[i] - prices[i-1])
        
        if len(deltas) < period:
            return None
        
        # Separate gains and losses
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        # Calculate average gain and loss
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def calculate_macd(self, symbol: str, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Optional[Dict]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        Returns: {'macd': float, 'signal': float, 'histogram': float, 'trend': str}
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < slow_period + signal_period:
            return None
        
        prices = [p['price'] for p in self.price_history[symbol]]
        
        # Calculate EMAs
        def calculate_ema(data: List[float], period: int) -> float:
            multiplier = 2 / (period + 1)
            ema = data[0]
            for price in data[1:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))
            return ema
        
        if len(prices) < slow_period:
            return None
        
        # Fast and slow EMA
        fast_ema = calculate_ema(prices[-fast_period:], fast_period)
        slow_ema = calculate_ema(prices[-slow_period:], slow_period)
        
        # MACD line
        macd_line = fast_ema - slow_ema
        
        # Add current MACD to history for signal line calculation
        self.macd_history[symbol].append(macd_line)
        
        # Calculate signal line (EMA of MACD line)
        if len(self.macd_history[symbol]) >= signal_period:
            # Use proper EMA calculation for signal line - use ALL available MACD values
            signal_line = self._calculate_ema_from_values(
                self.macd_history[symbol], 
                signal_period
            )
        else:
            # Not enough MACD history - use simple average as approximation
            signal_line = sum(self.macd_history[symbol]) / len(self.macd_history[symbol])
        
        # Histogram
        histogram = macd_line - signal_line
        
        # Trend determination
        trend = "bullish" if macd_line > signal_line else "bearish"
        
        return {
            'macd': round(macd_line, 4),
            'signal': round(signal_line, 4),
            'histogram': round(histogram, 4),
            'trend': trend
        }
    
    def calculate_bollinger_bands(self, symbol: str, period: int = 20, std_dev: float = 2.0) -> Optional[Dict]:
        """
        Calculate Bollinger Bands
        Returns: {'upper': float, 'middle': float, 'lower': float, 'position': str}
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < period:
            return None
        
        prices = [p['price'] for p in self.price_history[symbol][-period:]]
        current_price = prices[-1]
        
        # Simple Moving Average (middle band)
        sma = sum(prices) / len(prices)
        
        # Standard deviation
        variance = sum((price - sma) ** 2 for price in prices) / len(prices)
        std = math.sqrt(variance)
        
        # Bollinger Bands
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        # Determine position
        if current_price > upper_band:
            position = "above_upper"  # Potential sell signal
        elif current_price < lower_band:
            position = "below_lower"  # Potential buy signal
        else:
            position = "middle"  # Normal range
        
        return {
            'upper': round(upper_band, 2),
            'middle': round(sma, 2),
            'lower': round(lower_band, 2),
            'current': round(current_price, 2),
            'position': position
        }
    
    def calculate_moving_averages(self, symbol: str) -> Optional[Dict]:
        """
        Calculate multiple moving averages for trend analysis
        Returns: {'ma20': float, 'ma50': float, 'ma200': float, 'trend': str}
        """
        if symbol not in self.price_history:
            return None
        
        prices = [p['price'] for p in self.price_history[symbol]]
        current_price = prices[-1] if prices else 0
        
        result = {'current': current_price}
        
        # Calculate available MAs
        for period in [20, 50, 200]:
            if len(prices) >= period:
                ma = sum(prices[-period:]) / period
                result[f'ma{period}'] = round(ma, 2)
        
        # Determine trend if we have at least MA20
        if 'ma20' in result:
            if len(prices) >= 50 and 'ma50' in result:
                if result['ma20'] > result['ma50'] and current_price > result['ma20']:
                    trend = "strong_bullish"
                elif result['ma20'] > result['ma50']:
                    trend = "bullish"
                elif result['ma20'] < result['ma50'] and current_price < result['ma20']:
                    trend = "strong_bearish"
                else:
                    trend = "bearish"
            else:
                trend = "bullish" if current_price > result['ma20'] else "bearish"
            
            result['trend'] = trend
        
        return result
    
    def analyze_volume_profile(self, symbol: str, period: int = 20) -> Optional[Dict]:
        """
        Analyze volume patterns for institutional activity detection
        Returns: {'avg_volume': int, 'current_volume': int, 'volume_ratio': float, 'activity': str}
        """
        if symbol not in self.volume_history or len(self.volume_history[symbol]) < period:
            return None
        
        volumes = [v['volume'] for v in self.volume_history[symbol][-period:]]
        current_volume = volumes[-1] if volumes else 0
        
        # Calculate average volume (excluding current)
        avg_volume = sum(volumes[:-1]) / (len(volumes) - 1) if len(volumes) > 1 else current_volume
        
        # Volume ratio
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Activity classification
        if volume_ratio > 2.0:
            activity = "high"  # Institutional activity likely
        elif volume_ratio > 1.5:
            activity = "elevated"
        elif volume_ratio < 0.5:
            activity = "low"
        else:
            activity = "normal"
        
        return {
            'avg_volume': int(avg_volume),
            'current_volume': current_volume,
            'volume_ratio': round(volume_ratio, 2),
            'activity': activity
        }
    
    def _calculate_ema_from_values(self, values: List[float], period: int) -> Optional[float]:
        """Helper to calculate EMA from a list of values."""
        if not values or len(values) < period:
            return None
        if len(values) == period: # First EMA is SMA for the period
            return sum(values) / period
        
        # For subsequent EMAs if we had full history. Here we assume 'values' are enough.
        # More robust EMA needs prior EMA. For a rolling window, recalculate or use SMA.
        # This simplified EMA is for cases like calculating signal line from existing MACD values.
        multiplier = 2 / (period + 1)
        ema = values[0] # Simplistic start, better to SMA first 'period' values
        # A more standard way for rolling EMA on a list of values for 'period':
        # Slice the list to relevant part for EMA calculation.
        # If values are e.g. [p1, p2, ..., pN] and we want EMA(period) at N:
        
        # Let's use a standard EMA calculation for a series
        if len(values) < period: return None
        
        # Calculate initial SMA for the first period
        sma = sum(values[:period]) / period
        ema_values = [sma]
        
        for i in range(period, len(values)):
            ema = (values[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        return ema_values[-1] if ema_values else None

    def calculate_rsi_slope(self, symbol: str, rsi_period: int = 14, slope_period: int = 5) -> Optional[float]:
        """
        Calculate the slope of the RSI over the last 'slope_period' points.
        A positive slope indicates rising momentum, negative indicates falling.
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < rsi_period + slope_period:
            return None

        rsi_values = []
        # Temporarily get more prices if needed for rolling RSI calculation
        prices_full = [p['price'] for p in self.price_history[symbol]]

        for i in range(slope_period):
            # Calculate RSI for the window ending at 'i' steps from the end
            # prices_for_rsi_calc = prices_full[-(rsi_period + slope_period - 1 - i) : -(slope_period - 1 - i) if (slope_period - 1 - i) > 0 else None]
            # This slicing is tricky. Simpler: calculate RSI for the last (rsi_period + slope_period -1) prices
            # then take the last 'slope_period' RSI values.
            
            # To get RSI at point t, we need prices up to t.
            # For RSI slope over `slope_period`, we need `slope_period` RSI values.
            # The last RSI value uses prices up to T.
            # The first RSI value (for the slope) uses prices up to T - slope_period + 1.
            # Each RSI calculation itself needs `rsi_period` price changes (i.e., `rsi_period + 1` prices).

            # Let's grab enough historical prices to calculate `slope_period` RSI values
            # Total prices needed: rsi_period (for the first RSI) + slope_period (for subsequent RSI values)
            if len(prices_full) < rsi_period + slope_period: # Need enough data points overall
                 return None

            # Calculate RSI for the latest `slope_period` points
            # We need to simulate `self.price_history` for each point to call `calculate_rsi`
            # This is inefficient. Better to calculate RSI series directly.
            
            # Direct RSI series calculation:
            deltas = [prices_full[j] - prices_full[j-1] for j in range(1, len(prices_full))]
            if len(deltas) < rsi_period + slope_period - 1:
                return None

            current_rsi_series = []
            for k in range(slope_period):
                # Window for RSI calculation moves back in time
                # Last RSI point uses deltas[-rsi_period:]
                # Second to last uses deltas[-(rsi_period+1):-1], etc.
                end_index = len(deltas) - k
                start_index = end_index - rsi_period
                if start_index < 0: break # Not enough data for this RSI point

                period_deltas = deltas[start_index:end_index]
                
                gains = [d for d in period_deltas if d > 0]
                losses = [-d for d in period_deltas if d < 0]

                avg_gain = sum(gains) / rsi_period if gains else 0
                avg_loss = sum(losses) / rsi_period if losses else 0.00001 # Avoid division by zero

                if avg_loss == 0: rs = float('inf') # Effectively 100 RSI
                else: rs = avg_gain / avg_loss
                
                rsi = 100 - (100 / (1 + rs))
                current_rsi_series.append(rsi)
            
            if len(current_rsi_series) < slope_period: return None
            rsi_values_for_slope = list(reversed(current_rsi_series)) # Ensure chronological order for slope

        # Linear regression: y = mx + c where y is RSI, x is time index (0, 1, ..., slope_period-1)
        n = float(slope_period)
        x_series = list(range(slope_period))
        y_series = rsi_values_for_slope

        sum_x = sum(x_series)
        sum_y = sum(y_series)
        sum_xy = sum(x * y for x, y in zip(x_series, y_series))
        sum_x_sq = sum(x**2 for x in x_series)

        numerator = (n * sum_xy) - (sum_x * sum_y)
        denominator = (n * sum_x_sq) - (sum_x**2)

        if denominator == 0:
            return 0.0  # Flat line, slope is 0
        
        slope = numerator / denominator
        return round(slope, 3)

    def calculate_adx(self, symbol: str, period: int = 14) -> Optional[float]:
        """
        Calculate ADX (Average Directional Index).
        Requires High, Low, Close prices. Current implementation is a placeholder
        as add_price_data might not consistently provide HLC.
        ADX < 20: Weak trend or ranging market.
        ADX > 25-30: Strong trend (either up or down).
        ADX > 50: Very strong trend.
        """
        # Placeholder: Full ADX requires High, Low, Close data points.
        # Ensure add_price_data is called with high and low prices.
        # For now, returning a neutral value or None.
        self.logger.warning(f"ADX calculation for {symbol} requires HLC data. Current impl is a placeholder.")
        
        prices_data = self.price_history.get(symbol, [])
        if len(prices_data) < period + period: # Need enough data for smoothing, e.g. period for TR/DM, period for ADX smoothing
             # self.logger.debug(f"Insufficient data for ADX {symbol}: have {len(prices_data)}, need ~{2*period}")
             return None

        # Check if HLC data is available
        if not all('high' in p and 'low' in p and 'price' in p for p in prices_data[- (2*period):]): # Check recent data needed
            # self.logger.warning(f"HLC data missing for ADX calculation of {symbol}. Fallback or skip.")
            return None # Or a mock value like 25.0

        highs = [p['high'] for p in prices_data]
        lows = [p['low'] for p in prices_data]
        closes = [p['price'] for p in prices_data]

        tr_values = []
        plus_dm_values = []
        minus_dm_values = []

        for i in range(1, len(prices_data)):
            # True Range
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            tr = max(tr1, tr2, tr3)
            tr_values.append(tr)

            # Directional Movement
            up_move = highs[i] - highs[i-1]
            down_move = lows[i-1] - lows[i]
            
            pdm = up_move if (up_move > down_move and up_move > 0) else 0
            mdm = down_move if (down_move > up_move and down_move > 0) else 0
            plus_dm_values.append(pdm)
            minus_dm_values.append(mdm)
        
        if len(tr_values) < period: return None # Not enough TR/DM values

        # Wilder's Smoothing (similar to EMA but with alpha = 1/period)
        def wilder_smooth(values: List[float], n: int) -> List[float]:
            smoothed = [0.0] * len(values)
            if not values: return []
            smoothed[n-1] = sum(values[:n]) # Initial sum for first 'smoothed' value
            for k in range(n, len(values)):
                smoothed[k] = smoothed[k-1] - (smoothed[k-1] / n) + values[k]
            return smoothed # Returns full list, typically want the last or a series

        # Calculate ATR, Smoothed +DM, Smoothed -DM
        # We need 'period' length series for these
        if len(tr_values) < period -1 + period: # Check if we have enough data to smooth over 'period' elements and then for DI calc
            return None

        # Smooth the last 'period' available DM/TR values.
        # For a 14-period ADX, we'd typically smooth the last 14 +DM, -DM, TR values.
        # Let's use the _calculate_ema_from_values for simplicity with alpha = 1/period
        # This is not exactly Wilder's but a common EMA approach.
        # Wilder's uses: current_ema = (previous_ema * (n-1) + current_value) / n
        
        # For simplicity, use SMA for initial smoothing if _calculate_ema_from_values is tricky
        # For a proper ADX, a dedicated Wilder smoothing is better.
        
        # Simplified smoothing using SMA for the first value then EMA-like for subsequent
        def get_smoothed_series(values: List[float], n: int) -> List[float]:
            if len(values) < n: return []
            # First value is simple average
            s_values = [sum(values[i-n+1:i+1])/n for i in range(n-1, len(values))]
            return s_values

        atr_series = get_smoothed_series(tr_values, period)
        plus_di_series_num = get_smoothed_series(plus_dm_values, period)
        minus_di_series_num = get_smoothed_series(minus_dm_values, period)

        if not atr_series or not plus_di_series_num or not minus_di_series_num: return None
        
        # Ensure all smoothed series have same length for DI calculation
        min_len = min(len(atr_series), len(plus_di_series_num), len(minus_di_series_num))
        if min_len == 0: return None

        atr_series = atr_series[-min_len:]
        plus_di_series_num = plus_di_series_num[-min_len:]
        minus_di_series_num = minus_di_series_num[-min_len:]

        plus_di = [(pdm / atr * 100) if atr > 0 else 0 for pdm, atr in zip(plus_di_series_num, atr_series)]
        minus_di = [(mdm / atr * 100) if atr > 0 else 0 for mdm, atr in zip(minus_di_series_num, atr_series)]

        if not plus_di or not minus_di: return None

        dx_series = []
        for pdi, mdi in zip(plus_di, minus_di):
            di_sum = pdi + mdi
            dx = (abs(pdi - mdi) / di_sum * 100) if di_sum > 0 else 0
            dx_series.append(dx)

        if len(dx_series) < period: return None # Need enough DX values to smooth for ADX

        adx_values = get_smoothed_series(dx_series, period) # ADX is smoothed DX
        
        return round(adx_values[-1], 2) if adx_values else None

    def get_trend_strength_indicators(self, symbol: str, rsi_period: int = 14, rsi_slope_period: int = 5, adx_period: int = 14) -> Dict:
        """
        Combines RSI, RSI Slope, and ADX for a comprehensive trend strength assessment.
        """
        rsi = self.calculate_rsi(symbol, period=rsi_period)
        rsi_slope = self.calculate_rsi_slope(symbol, rsi_period=rsi_period, slope_period=rsi_slope_period)
        adx = self.calculate_adx(symbol, period=adx_period) # Will be None if HLC data is missing

        trend_description = "N/A"
        if adx is not None:
            if adx > 25:
                if rsi is not None and rsi > 50 and (rsi_slope is None or rsi_slope > 0): # Added rsi_slope check
                    trend_description = "Strong Bullish Trend"
                elif rsi is not None and rsi < 50 and (rsi_slope is None or rsi_slope < 0): # Added rsi_slope check
                    trend_description = "Strong Bearish Trend"
                else:
                    trend_description = "Strong Trend (Mixed RSI)"
            elif adx < 20:
                trend_description = "Weak/No Trend (Ranging)"
            else: # ADX between 20 and 25
                trend_description = "Developing Trend"
        else: # ADX is None
            if rsi is not None and rsi_slope is not None:
                if rsi > 55 and rsi_slope > 0.5: trend_description = "Likely Bullish Momentum"
                elif rsi < 45 and rsi_slope < -0.5: trend_description = "Likely Bearish Momentum"
                else: trend_description = "Indeterminate Trend (RSI based)"

        return {
            "rsi": rsi,
            "rsi_slope": rsi_slope,
            "adx": adx, # This might be None
            "trend_description": trend_description,
            "notes": "ADX requires High, Low, Close prices for full accuracy." if adx is None else "ADX calculated."
        }

    def get_comprehensive_analysis(self, symbol: str) -> Dict:
        """
        Get comprehensive technical analysis for a symbol
        Returns all indicators with trading signals
        """
        if symbol not in self.initialized_symbols:
            return {'error': f'Insufficient data for {symbol}'}
        
        analysis = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'indicators': {}
        }
        
        # RSI Analysis
        rsi = self.calculate_rsi(symbol)
        if rsi:
            analysis['indicators']['rsi'] = {
                'value': rsi,
                'signal': 'buy' if rsi < 30 else 'sell' if rsi > 70 else 'hold'
            }
        
        # MACD Analysis
        macd = self.calculate_macd(symbol)
        if macd:
            analysis['indicators']['macd'] = macd
        
        # Bollinger Bands Analysis
        bb = self.calculate_bollinger_bands(symbol)
        if bb:
            signal = 'buy' if bb['position'] == 'below_lower' else 'sell' if bb['position'] == 'above_upper' else 'hold'
            analysis['indicators']['bollinger_bands'] = {**bb, 'signal': signal}
        
        # Moving Averages Analysis
        ma = self.calculate_moving_averages(symbol)
        if ma:
            analysis['indicators']['moving_averages'] = ma
        
        # Volume Analysis
        volume = self.analyze_volume_profile(symbol)
        if volume:
            analysis['indicators']['volume'] = volume
        
        # Trend Strength Analysis
        trend = self.get_trend_strength_indicators(symbol)
        if trend:
            analysis['indicators']['trend_strength'] = trend
        
        # Overall signal strength
        signals = []
        if 'rsi' in analysis['indicators']:
            signals.append(analysis['indicators']['rsi']['signal'])
        if 'bollinger_bands' in analysis['indicators']:
            signals.append(analysis['indicators']['bollinger_bands']['signal'])
        
        buy_signals = signals.count('buy')
        sell_signals = signals.count('sell')
        
        if buy_signals > sell_signals:
            analysis['overall_signal'] = 'buy'
            analysis['signal_strength'] = buy_signals / len(signals) if signals else 0
        elif sell_signals > buy_signals:
            analysis['overall_signal'] = 'sell'
            analysis['signal_strength'] = sell_signals / len(signals) if signals else 0
        else:
            analysis['overall_signal'] = 'hold'
            analysis['signal_strength'] = 0.5
        
        return analysis

if __name__ == "__main__":
    # Test the technical indicators
    ti = TechnicalIndicators()
    
    # Add some test data
    import random
    base_price = 100.0
    
    print("🔧 Testing Technical Indicators Module")
    print("=" * 50)
    
    # Simulate 50 data points with realistic price movement
    for i in range(50):
        # Random walk with slight upward bias
        change = random.uniform(-2, 2.5)
        base_price += change
        volume = random.randint(100000, 500000)
        
        ti.add_price_data('TEST', base_price, volume)
    
    # Get comprehensive analysis
    analysis = ti.get_comprehensive_analysis('TEST')
    
    print(f"📊 Analysis for {analysis['symbol']}:")
    print(f"⏰ Timestamp: {analysis['timestamp']}")
    print()
    
    for indicator, data in analysis['indicators'].items():
        print(f"📈 {indicator.upper().replace('_', ' ')}:")
        if isinstance(data, dict):
            for key, value in data.items():
                if key != 'signal':
                    print(f"   {key}: {value}")
            if 'signal' in data:
                signal_emoji = "🟢" if data['signal'] == 'buy' else "🔴" if data['signal'] == 'sell' else "🟡"
                print(f"   {signal_emoji} Signal: {str(data['signal']).upper()}")
        print()
    
    print(f"🎯 OVERALL SIGNAL: {analysis['overall_signal'].upper()}")
    print(f"💪 Signal Strength: {analysis['signal_strength']:.1%}")
    print()
    print("✅ Technical Indicators Module Ready!")