#!/usr/bin/env python3
"""Debug crypto data fetching to see actual API responses"""

import sys
import os
sys.path.append('/Users/benjamin.pommeraud/Desktop/Alpaca')

import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta, timezone
import logging

def debug_crypto_api_data():
    """Debug actual crypto API responses"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Alpaca API
    try:
        api = tradeapi.REST(
            os.environ['ALPACA_PAPER_API_KEY'],
            os.environ['ALPACA_PAPER_SECRET_KEY'],
            base_url=os.environ['ALPACA_BASE_URL']
        )
        print("✅ Alpaca API initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Alpaca API: {e}")
        return
    
    # Test symbol
    symbol = 'BTC/USD'
    
    print(f"\n{'='*60}")
    print(f"DEBUGGING CRYPTO DATA FOR {symbol}")
    print(f"{'='*60}")
    
    try:
        # Test current price
        print(f"\n1. Testing current price...")
        try:
            quote = api.get_crypto_snapshot([symbol])
            if quote and symbol in quote:
                current_price = float(quote[symbol].latest_trade.price)
                print(f"   Current price: ${current_price}")
                print(f"   Quote timestamp: {quote[symbol].latest_trade.timestamp}")
                print(f"   Quote data: {quote[symbol]}")
            else:
                print(f"   ❌ No quote data returned")
        except Exception as e:
            print(f"   ❌ Quote fetch failed: {e}")
        
        # Test historical bars
        print(f"\n2. Testing historical bars...")
        try:
            start_time = datetime.now(timezone.utc) - timedelta(hours=30)
            start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            print(f"   Requesting bars from: {start_time_str}")
            print(f"   Symbol: {symbol}")
            print(f"   Timeframe: 1Hour")
            print(f"   Limit: 30")
            
            bars = api.get_crypto_bars(
                symbol,
                start=start_time_str,
                timeframe='1Hour',
                limit=30
            )
            
            if bars and len(bars) > 0:
                print(f"   ✅ Retrieved {len(bars)} bars")
                
                # Extract data
                prices = [float(bar.c) for bar in bars]
                volumes = [float(bar.v) for bar in bars]
                
                print(f"   First bar: {bars[0]} (close={bars[0].c})")
                print(f"   Last bar: {bars[-1]} (close={bars[-1].c})")
                print(f"   Price range: ${min(prices):.2f} - ${max(prices):.2f}")
                print(f"   Total volume: {sum(volumes):,.0f}")
                
                # Test calculations
                print(f"\n3. Testing calculations...")
                
                # RSI requirements
                if len(prices) >= 14:
                    print(f"   ✅ RSI: {len(prices)} prices available (≥14 required)")
                else:
                    print(f"   ❌ RSI: {len(prices)} prices available (<14 required)")
                
                # MACD requirements
                if len(prices) >= 26:
                    print(f"   ✅ MACD: {len(prices)} prices available (≥26 required)")
                elif len(prices) >= 21:
                    print(f"   ⚠️ MACD: {len(prices)} prices available (fallback ≥21)")
                else:
                    print(f"   ❌ MACD: {len(prices)} prices available (<21 required)")
                
                # Bollinger requirements
                if len(prices) >= 20:
                    print(f"   ✅ Bollinger: {len(prices)} prices available (≥20 required)")
                else:
                    print(f"   ❌ Bollinger: {len(prices)} prices available (<20 required)")
                
                # Volume requirements
                if volumes and all(v > 0 for v in volumes):
                    print(f"   ✅ Volume: Valid data available")
                else:
                    print(f"   ❌ Volume: Invalid data")
                
            else:
                print(f"   ❌ No bars returned")
                print(f"   Response: {bars}")
                
        except Exception as e:
            print(f"   ❌ Bars fetch failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Overall test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_crypto_api_data()