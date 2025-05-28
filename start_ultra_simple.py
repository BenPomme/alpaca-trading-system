#!/usr/bin/env python3
"""
Ultra-Simple Trading System for Railway
Minimal dependencies, maximum reliability
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
    """Ultra-minimal trading system"""
    
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
    
    def check_account(self):
        """Verify account access"""
        try:
            account = self.api.get_account()
            portfolio_value = float(account.portfolio_value)
            print(f"📊 Portfolio Value: ${portfolio_value:,.2f}")
            return True
        except Exception as e:
            print(f"❌ Account check failed: {e}")
            return False
    
    def get_quote(self, symbol):
        """Get simple quote data"""
        try:
            quote = self.api.get_latest_quote(symbol)
            return {
                'symbol': symbol,
                'bid': float(quote.bid_price) if quote.bid_price else 0,
                'ask': float(quote.ask_price) if quote.ask_price else 0,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Failed to get quote for {symbol}: {e}")
            return None
    
    def analyze_market(self):
        """Simple market analysis"""
        symbols = ['SPY', 'QQQ', 'IWM']
        quotes = []
        
        print("📈 Getting market data...")
        for symbol in symbols:
            quote = self.get_quote(symbol)
            if quote:
                quotes.append(quote)
                print(f"   {symbol}: ${quote['ask']:.2f}")
        
        if len(quotes) >= 2:
            regime = 'active'
            confidence = 0.8
        else:
            regime = 'uncertain'
            confidence = 0.5
            
        print(f"🎯 Market Regime: {regime} ({confidence:.0%})")
        return regime, confidence, quotes
    
    def log_cycle(self, cycle_data):
        """Log trading cycle"""
        try:
            # Create data directory
            os.makedirs('data', exist_ok=True)
            
            # Simple logging
            log_file = 'data/trading_log.json'
            entry = {
                'timestamp': datetime.now().isoformat(),
                'cycle': cycle_data
            }
            
            # Append to log (keep simple)
            logs = []
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                except:
                    logs = []
            
            logs.append(entry)
            # Keep last 100 entries only
            logs = logs[-100:]
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Logging error: {e}")
    
    def run_cycle(self):
        """Run one trading cycle"""
        print(f"\n🔄 TRADING CYCLE - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 40)
        
        # Simple market analysis
        regime, confidence, quotes = self.analyze_market()
        
        # Strategy selection
        if regime == 'active':
            strategy = 'momentum'
        else:
            strategy = 'conservative'
        
        print(f"🎯 Strategy: {strategy}")
        
        # Log cycle
        cycle_data = {
            'regime': regime,
            'confidence': confidence,
            'strategy': strategy,
            'quotes_count': len(quotes)
        }
        
        self.log_cycle(cycle_data)
        print("✅ Cycle completed")
        
        return cycle_data
    
    def run_continuous(self):
        """Main trading loop"""
        print("🚀 ULTRA-SIMPLE ADAPTIVE TRADING SYSTEM")
        print("=" * 50)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("☁️ Platform: Railway Cloud")
        print("💰 Mode: Paper Trading")
        print()
        
        # Account verification
        if not self.check_account():
            return
        
        print("🔄 Starting continuous monitoring...")
        print("   (Ctrl+C to stop)")
        print()
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                print(f"📊 Cycle #{cycle_count}")
                
                # Run trading cycle
                self.run_cycle()
                
                # Wait between cycles
                wait_time = 120  # 2 minutes
                print(f"⏳ Next cycle in {wait_time} seconds...")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            print("\n🛑 Trading stopped")
        except Exception as e:
            print(f"\n❌ System error: {e}")
            print("🔄 Restarting in 60 seconds...")
            time.sleep(60)

def main():
    """Entry point"""
    try:
        trader = UltraSimpleTrader()
        trader.run_continuous()
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()