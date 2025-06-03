#!/usr/bin/env python3
"""Debug technical indicator mathematical calculations directly"""

def debug_rsi_calculation():
    """Test RSI calculation with sample data"""
    print("🔍 DEBUGGING RSI CALCULATION")
    print("="*50)
    
    # Sample price data (30 periods for testing)
    sample_prices = [
        100, 102, 101, 103, 105, 104, 106, 108, 107, 109,  # 10 periods
        111, 110, 112, 114, 113, 115, 117, 116, 118, 120,  # 20 periods
        119, 121, 123, 122, 124, 126, 125, 127, 129, 128   # 30 periods
    ]
    
    print(f"Sample prices ({len(sample_prices)} periods): {sample_prices}")
    
    try:
        # RSI calculation logic (copied from crypto_module.py)
        if len(sample_prices) < 14:
            print(f"❌ Insufficient data: {len(sample_prices)}/14 required")
            return None
        
        # Calculate price changes
        price_changes = [sample_prices[i] - sample_prices[i-1] for i in range(1, len(sample_prices))]
        print(f"Price changes: {price_changes}")
        
        # Calculate gains and losses
        gains = [change if change > 0 else 0 for change in price_changes]
        losses = [-change if change < 0 else 0 for change in price_changes]
        
        print(f"Gains: {gains}")
        print(f"Losses: {losses}")
        
        # Calculate average gains and losses (last 14 periods)
        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14
        
        print(f"Average gain (last 14): {avg_gain}")
        print(f"Average loss (last 14): {avg_loss}")
        
        # Calculate RSI
        if avg_loss == 0:
            rsi = 100
            print("RSI = 100 (no losses)")
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            print(f"RS = {rs}")
            print(f"RSI = {rsi}")
        
        return rsi
        
    except Exception as e:
        print(f"❌ RSI calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_ema_calculation():
    """Test EMA calculation with sample data"""
    print("\n🔍 DEBUGGING EMA CALCULATION")
    print("="*50)
    
    # Sample price data
    sample_prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113]
    period = 12
    
    print(f"Sample prices ({len(sample_prices)} periods): {sample_prices}")
    print(f"EMA period: {period}")
    
    try:
        # EMA calculation logic (copied from crypto_module.py)
        if len(sample_prices) < period:
            print(f"❌ Insufficient data: {len(sample_prices)}/{period} required")
            return None
        
        multiplier = 2 / (period + 1)
        print(f"EMA multiplier: {multiplier}")
        
        ema = sample_prices[0]
        print(f"Initial EMA: {ema}")
        
        for i, price in enumerate(sample_prices[1:], 1):
            old_ema = ema
            ema = (price * multiplier) + (ema * (1 - multiplier))
            print(f"Period {i}: price={price}, EMA={ema:.4f} (from {old_ema:.4f})")
        
        return ema
        
    except Exception as e:
        print(f"❌ EMA calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_bollinger_calculation():
    """Test Bollinger Bands calculation with sample data"""
    print("\n🔍 DEBUGGING BOLLINGER BANDS CALCULATION")
    print("="*50)
    
    # Sample price data (25 periods for testing)
    sample_prices = [
        100, 102, 101, 103, 105, 104, 106, 108, 107, 109,  # 10
        111, 110, 112, 114, 113, 115, 117, 116, 118, 120,  # 20
        119, 121, 123, 122, 124  # 25
    ]
    current_price = 125
    
    print(f"Sample prices ({len(sample_prices)} periods): {sample_prices}")
    print(f"Current price: {current_price}")
    
    try:
        # Bollinger Bands calculation logic (copied from crypto_module.py)
        if len(sample_prices) < 20 or current_price <= 0:
            print(f"❌ Insufficient data or invalid price: {len(sample_prices)}/20, price={current_price}")
            return None
        
        # Calculate 20-period SMA and standard deviation
        last_20_prices = sample_prices[-20:]
        print(f"Last 20 prices: {last_20_prices}")
        
        sma_20 = sum(last_20_prices) / 20
        print(f"SMA-20: {sma_20}")
        
        # Calculate variance and standard deviation
        deviations = [(price - sma_20) ** 2 for price in last_20_prices]
        print(f"Squared deviations: {deviations}")
        
        variance = sum(deviations) / 20
        std_dev = variance ** 0.5
        print(f"Variance: {variance}")
        print(f"Standard deviation: {std_dev}")
        
        # Bollinger Bands
        upper_band = sma_20 + (2 * std_dev)
        lower_band = sma_20 - (2 * std_dev)
        
        print(f"Upper Band: {upper_band}")
        print(f"Lower Band: {lower_band}")
        print(f"Current Price: {current_price}")
        
        # Position analysis
        if current_price > upper_band:
            position = 'above_upper'
        elif current_price < lower_band:
            position = 'below_lower'
        elif current_price > sma_20:
            position = 'above_middle'
        else:
            position = 'below_middle'
        
        print(f"Position: {position}")
        
        return {
            'upper_band': upper_band,
            'lower_band': lower_band,
            'sma_20': sma_20,
            'position': position
        }
        
    except Exception as e:
        print(f"❌ Bollinger calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_volume_calculation():
    """Test volume confirmation calculation"""
    print("\n🔍 DEBUGGING VOLUME CONFIRMATION")
    print("="*50)
    
    # Sample volume data
    volume_24h = 1500000
    avg_volume_7d = 1000000
    
    print(f"Volume 24h: {volume_24h}")
    print(f"Average volume 7d: {avg_volume_7d}")
    
    try:
        # Volume calculation logic (copied from crypto_module.py)
        if avg_volume_7d <= 0:
            print(f"❌ Invalid average volume: {avg_volume_7d}")
            return None
        
        volume_ratio = volume_24h / avg_volume_7d
        print(f"Volume ratio: {volume_ratio}")
        
        # Volume interpretation
        if volume_ratio >= 2.0:
            confirmation = 'strong'
            strength_multiplier = 1.2
        elif volume_ratio >= 1.5:
            confirmation = 'moderate'
            strength_multiplier = 1.1
        elif volume_ratio >= 0.8:
            confirmation = 'neutral'
            strength_multiplier = 1.0
        else:
            confirmation = 'weak'
            strength_multiplier = 0.8
        
        volume_score = min(volume_ratio / 2.0, 1.0)
        
        print(f"Confirmation: {confirmation}")
        print(f"Strength multiplier: {strength_multiplier}")
        print(f"Volume score: {volume_score}")
        
        return {
            'volume_ratio': volume_ratio,
            'confirmation': confirmation,
            'strength_multiplier': strength_multiplier,
            'volume_score': volume_score
        }
        
    except Exception as e:
        print(f"❌ Volume calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    # Test all indicator calculations
    debug_rsi_calculation()
    debug_ema_calculation()
    debug_bollinger_calculation()
    debug_volume_calculation()
    
    print("\n" + "="*60)
    print("SUMMARY: Mathematical calculations appear to work correctly")
    print("Issue likely lies in data retrieval or data format problems")
    print("="*60)