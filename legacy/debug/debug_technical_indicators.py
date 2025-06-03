#!/usr/bin/env python3
"""Debug technical indicators to find why they return None"""

import sys
import os
sys.path.append('/Users/benjamin.pommeraud/Desktop/Alpaca')

from modular.crypto_module import CryptoModule
from datetime import datetime, timezone
import logging

def debug_technical_indicators():
    """Debug crypto technical indicators with real market data"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize crypto module
    crypto_module = CryptoModule()
    
    # Test symbols
    symbols = ['BTCUSD', 'ETHUSD', 'ADAUSD']
    
    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"DEBUGGING TECHNICAL INDICATORS FOR {symbol}")
        print(f"{'='*60}")
        
        # Get market data
        market_data = crypto_module._get_crypto_market_data(symbol)
        
        if not market_data:
            print(f"❌ No market data for {symbol}")
            continue
        
        print(f"\n📊 Market Data Structure:")
        for key, value in market_data.items():
            if key == 'price_history':
                print(f"  {key}: [{len(value) if value else 0} prices]")
                if value:
                    print(f"    First 5: {value[:5]}")
                    print(f"    Last 5: {value[-5:]}")
            else:
                print(f"  {key}: {value}")
        
        # Test each indicator
        print(f"\n🔍 TESTING INDICATORS:")
        
        # 1. RSI Signals
        print(f"\n1. RSI Calculation:")
        try:
            rsi_result = crypto_module._calculate_rsi_signals(symbol, market_data)
            print(f"   Result: {rsi_result}")
            if rsi_result is None:
                prices = market_data.get('price_history', [])
                print(f"   Debug: price_history length = {len(prices)}")
                if len(prices) > 0:
                    print(f"   Debug: first few prices = {prices[:5]}")
                    print(f"   Debug: last few prices = {prices[-5:]}")
        except Exception as e:
            print(f"   ❌ RSI Exception: {e}")
            import traceback
            traceback.print_exc()
        
        # 2. MACD Signals
        print(f"\n2. MACD Calculation:")
        try:
            macd_result = crypto_module._calculate_macd_signals(symbol, market_data)
            print(f"   Result: {macd_result}")
            if macd_result is None:
                prices = market_data.get('price_history', [])
                print(f"   Debug: price_history length = {len(prices)}")
                if len(prices) >= 12:
                    ema_12 = crypto_module._calculate_ema(prices, 12)
                    print(f"   Debug: EMA-12 = {ema_12}")
                if len(prices) >= 26:
                    ema_26 = crypto_module._calculate_ema(prices, 26)
                    print(f"   Debug: EMA-26 = {ema_26}")
        except Exception as e:
            print(f"   ❌ MACD Exception: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. Bollinger Bands
        print(f"\n3. Bollinger Bands Calculation:")
        try:
            bollinger_result = crypto_module._calculate_bollinger_signals(symbol, market_data)
            print(f"   Result: {bollinger_result}")
            if bollinger_result is None:
                prices = market_data.get('price_history', [])
                current_price = market_data.get('current_price', 0)
                print(f"   Debug: price_history length = {len(prices)}")
                print(f"   Debug: current_price = {current_price}")
                if len(prices) >= 20:
                    sma_20 = sum(prices[-20:]) / 20
                    print(f"   Debug: SMA-20 = {sma_20}")
        except Exception as e:
            print(f"   ❌ Bollinger Exception: {e}")
            import traceback
            traceback.print_exc()
        
        # 4. Volume Confirmation
        print(f"\n4. Volume Confirmation:")
        try:
            volume_result = crypto_module._calculate_volume_confirmation(symbol, market_data)
            print(f"   Result: {volume_result}")
            if volume_result is None:
                volume_24h = market_data.get('volume_24h', 0)
                avg_volume = market_data.get('avg_volume_7d', 0)
                print(f"   Debug: volume_24h = {volume_24h}")
                print(f"   Debug: avg_volume_7d = {avg_volume}")
        except Exception as e:
            print(f"   ❌ Volume Exception: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n{'='*60}")

if __name__ == '__main__':
    debug_technical_indicators()