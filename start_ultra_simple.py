#!/usr/bin/env python3
"""
Ultra-Simple Trading System for Railway
Base class for trading system inheritance chain
"""

import os
import sys
import time
import json
from datetime import datetime

# Load environment - fallback if python-dotenv not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not available, using environment variables directly")

# Core import
try:
    import alpaca_trade_api as tradeapi
    print("✅ Alpaca API ready")
except ImportError as e:
    print(f"❌ Failed to import Alpaca API: {e}")
    sys.exit(1)

class UltraSimpleTrader:
    """Ultra-minimal trading system base class"""
    
    def __init__(self):
        # Get credentials from environment
        self.api_key = os.getenv('ALPACA_PAPER_API_KEY') or os.getenv('APCA_API_KEY_ID')
        self.secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY') or os.getenv('APCA_API_SECRET_KEY')
        
        if not self.api_key or not self.secret_key:
            print("❌ Missing API credentials")
            print("Set ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY")
            sys.exit(1)
        
        try:
            self.api = tradeapi.REST(
                key_id=self.api_key,
                secret_key=self.secret_key,
                base_url='https://paper-api.alpaca.markets',
                api_version='v2'
            )
            print("✅ Connected to Alpaca Paper Trading")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            sys.exit(1)
        
        # Basic configuration
        self.cycle_delay = 120  # 2 minutes
        self.market_symbols = ['SPY', 'QQQ', 'IWM']
        
    def get_market_quotes(self):
        """Get basic market quotes"""
        quotes = []
        for symbol in self.market_symbols:
            try:
                quote = self.api.get_latest_quote(symbol)
                quotes.append({
                    'symbol': symbol,
                    'ask': float(quote.ask_price),
                    'bid': float(quote.bid_price),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"⚠️ Failed to get quote for {symbol}: {e}")
        return quotes
        
    def analyze_market_regime(self, quotes):
        """Basic market regime analysis"""
        if not quotes:
            return "uncertain", 0.5
        
        # Simple regime detection based on price movement
        return "active", 0.7
        
    def log_activity(self, activity_type, data):
        """Log trading activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': activity_type,
            'data': data
        }
        
        # Simple console logging
        print(f"📊 {activity_type}: {data}")

def main():
    """Main execution function for standalone use"""
    print("🚀 ULTRA-SIMPLE TRADER - BASE CLASS")
    print("This is a base class for the trading system inheritance chain")
    print("Use start_phase3.py for full system functionality")

if __name__ == "__main__":
    main()