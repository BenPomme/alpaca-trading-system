#!/usr/bin/env python3
"""
Enhanced Trading System with Database Integration
Phase 1 implementation - adds persistent data storage
"""

import os
import sys
from datetime import datetime
from start_ultra_simple import UltraSimpleTrader
from database_manager import TradingDatabase

class EnhancedTrader(UltraSimpleTrader):
    """Enhanced trader with database integration"""
    
    def __init__(self, use_database=True):
        # Initialize parent trader
        super().__init__()
        
        # Initialize database if requested
        self.use_database = use_database
        if use_database:
            try:
                self.db = TradingDatabase()
                print("✅ Database integration enabled")
            except Exception as e:
                print(f"⚠️ Database initialization failed: {e}")
                print("⚠️ Continuing without database...")
                self.use_database = False
                self.db = None
        else:
            self.db = None
            print("⚠️ Database integration disabled")
        
        self.cycle_count = 0
    
    def get_quote_with_storage(self, symbol):
        """Enhanced quote retrieval with database storage"""
        quote = self.get_quote(symbol)
        
        if quote and self.use_database and self.db:
            try:
                # Store quote in database
                self.db.store_market_quote(
                    symbol=symbol,
                    bid_price=quote['bid'],
                    ask_price=quote['ask'],
                    timestamp=quote['timestamp']
                )
            except Exception as e:
                print(f"⚠️ Quote storage error for {symbol}: {e}")
        
        return quote
    
    def enhanced_analyze_market(self):
        """Enhanced market analysis with database storage"""
        symbols = ['SPY', 'QQQ', 'IWM']
        quotes = []
        
        print("📈 Getting market data...")
        for symbol in symbols:
            quote = self.get_quote_with_storage(symbol)
            if quote:
                quotes.append(quote)
                print(f"   {symbol}: ${quote['ask']:.2f}")
        
        # Determine regime (same logic as original)
        if len(quotes) >= 2:
            regime = 'active'
            confidence = 0.8
        else:
            regime = 'uncertain'
            confidence = 0.5
            
        print(f"🎯 Market Regime: {regime} ({confidence:.0%})")
        return regime, confidence, quotes
    
    def enhanced_run_cycle(self):
        """Enhanced trading cycle with database integration"""
        self.cycle_count += 1
        
        print(f"\n🔄 ENHANCED TRADING CYCLE #{self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        
        # Enhanced market analysis
        regime, confidence, quotes = self.enhanced_analyze_market()
        
        # Strategy selection (same logic as original)
        if regime == 'active':
            strategy = 'momentum'
        else:
            strategy = 'conservative'
        
        print(f"🎯 Strategy: {strategy}")
        
        # Create enhanced cycle data
        cycle_data = {
            'regime': regime,
            'confidence': confidence,
            'strategy': strategy,
            'quotes_count': len(quotes),
            'quotes': quotes,  # Store actual quote data
            'cycle_number': self.cycle_count,
            'enhanced': True  # Flag to identify enhanced cycles
        }
        
        # Store cycle in database
        cycle_id = None
        if self.use_database and self.db:
            try:
                cycle_id = self.db.store_trading_cycle(cycle_data, self.cycle_count)
                print(f"💾 Cycle data stored (DB ID: {cycle_id})")
            except Exception as e:
                print(f"⚠️ Cycle storage error: {e}")
        
        # Simulate virtual trading decisions
        self.simulate_virtual_trades(quotes, strategy, regime, confidence, cycle_id)
        
        # Log cycle (maintain compatibility with original logging)
        self.log_cycle(cycle_data)
        print("✅ Enhanced cycle completed")
        
        return cycle_data
    
    def simulate_virtual_trades(self, quotes, strategy, regime, confidence, cycle_id=None):
        """Simulate trading decisions for performance tracking"""
        if not quotes or not self.use_database or not self.db:
            return
        
        try:
            # Simple trading simulation based on strategy
            for quote in quotes:
                symbol = quote['symbol']
                price = quote['ask']
                
                # Simple momentum strategy simulation
                if strategy == 'momentum' and confidence > 0.7:
                    # Simulate buy decision
                    trade_id = self.db.store_virtual_trade(
                        symbol=symbol,
                        action='buy',
                        price=price,
                        strategy=strategy,
                        regime=regime,
                        confidence=confidence,
                        cycle_id=cycle_id
                    )
                    print(f"📊 Virtual BUY: {symbol} @ ${price:.2f} (Trade ID: {trade_id})")
                
                elif strategy == 'conservative' and confidence < 0.6:
                    # Simulate hold/no action for conservative strategy
                    print(f"📊 Virtual HOLD: {symbol} @ ${price:.2f} (conservative)")
        
        except Exception as e:
            print(f"⚠️ Virtual trading simulation error: {e}")
    
    def get_performance_summary(self):
        """Get performance summary from database"""
        if not self.use_database or not self.db:
            return {"error": "Database not available"}
        
        try:
            # Get overall performance
            overall_perf = self.db.calculate_strategy_performance(days=30)
            
            # Get momentum strategy performance
            momentum_perf = self.db.calculate_strategy_performance('momentum', days=30)
            
            # Get conservative strategy performance
            conservative_perf = self.db.calculate_strategy_performance('conservative', days=30)
            
            # Get recent cycles
            recent_cycles = self.db.get_recent_cycles(5)
            
            # Get recent trades
            recent_trades = self.db.get_virtual_trades(limit=10)
            
            return {
                'overall': overall_perf,
                'momentum_strategy': momentum_perf,
                'conservative_strategy': conservative_perf,
                'recent_cycles': len(recent_cycles),
                'recent_trades': len(recent_trades),
                'database_enabled': True
            }
        
        except Exception as e:
            return {"error": f"Performance calculation failed: {e}"}
    
    def run_enhanced_continuous(self):
        """Enhanced continuous monitoring with database features"""
        print("🚀 ENHANCED ADAPTIVE TRADING SYSTEM")
        print("=" * 50)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("☁️ Platform: Railway Cloud")
        print("💰 Mode: Paper Trading")
        print("💾 Database: Enabled" if self.use_database else "💾 Database: Disabled")
        print("🔄 Enhancement: Phase 1 - Intelligent Foundation")
        print()
        
        # Account verification
        if not self.check_account():
            return
        
        print("🔄 Starting enhanced continuous monitoring...")
        print("   (Ctrl+C to stop)")
        print()
        
        try:
            while True:
                print(f"📊 Enhanced Cycle #{self.cycle_count + 1}")
                
                # Run enhanced trading cycle
                cycle_data = self.enhanced_run_cycle()
                
                # Show performance summary every 5 cycles
                if self.cycle_count % 5 == 0:
                    print("\n📈 PERFORMANCE SUMMARY")
                    print("-" * 30)
                    summary = self.get_performance_summary()
                    if 'error' not in summary:
                        print(f"📊 Total trades: {summary['overall']['trade_count']}")
                        print(f"📊 Win rate: {summary['overall']['win_rate']:.1%}")
                        print(f"📊 Avg confidence: {summary['overall']['avg_confidence']:.2f}")
                    else:
                        print(f"⚠️ {summary['error']}")
                    print()
                
                # Wait between cycles
                wait_time = 120  # 2 minutes
                print(f"⏳ Next enhanced cycle in {wait_time} seconds...")
                import time
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            print("\n🛑 Enhanced trading stopped")
            
            # Show final performance summary
            print("\n📈 FINAL PERFORMANCE SUMMARY")
            print("=" * 40)
            summary = self.get_performance_summary()
            if 'error' not in summary:
                print(f"📊 Total cycles: {self.cycle_count}")
                print(f"📊 Total virtual trades: {summary['overall']['trade_count']}")
                print(f"📊 Overall win rate: {summary['overall']['win_rate']:.1%}")
                print(f"📊 Database records: {summary['recent_cycles']} cycles, {summary['recent_trades']} trades")
            
        except Exception as e:
            print(f"\n❌ Enhanced system error: {e}")
            print("🔄 Restarting in 60 seconds...")
            import time
            time.sleep(60)

def test_enhanced_trader():
    """Test enhanced trader functionality"""
    print("🧪 Testing Enhanced Trader...")
    
    trader = EnhancedTrader(use_database=True)
    
    # Test enhanced cycle
    cycle_data = trader.enhanced_run_cycle()
    
    # Test performance summary
    summary = trader.get_performance_summary()
    print(f"📊 Performance summary: {summary}")
    
    print("✅ Enhanced trader test completed!")
    return True

def main():
    """Entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        return test_enhanced_trader()
    
    try:
        trader = EnhancedTrader(use_database=True)
        trader.run_enhanced_continuous()
    except Exception as e:
        print(f"❌ Enhanced startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()