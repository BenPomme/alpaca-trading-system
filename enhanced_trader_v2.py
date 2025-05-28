#!/usr/bin/env python3
"""
Enhanced Trading System v2 - Expanded Market Universe
Phase 1 implementation with 50+ stock monitoring
"""

import os
import sys
import time
from datetime import datetime
from enhanced_trader import EnhancedTrader
from market_universe import get_symbols_by_tier, validate_symbol_availability, get_sector_symbols

class EnhancedTraderV2(EnhancedTrader):
    """Enhanced trader with expanded market universe"""
    
    def __init__(self, use_database=True, market_tier=2):
        # Initialize parent trader
        super().__init__(use_database)
        
        # Set market tier (1=core, 2=liquid, 3=nasdaq, 4=all)
        self.market_tier = market_tier
        self.symbols = get_symbols_by_tier(market_tier)
        
        print(f"📊 Market Tier: {market_tier} ({len(self.symbols)} symbols)")
        print(f"📊 Symbols: {self.symbols[:10]}{'...' if len(self.symbols) > 10 else ''}")
        
        # Validate symbol availability
        self.validate_market_access()
    
    def validate_market_access(self):
        """Validate access to expanded market data"""
        print("🔍 Validating market data access...")
        
        try:
            validation = validate_symbol_availability(self.api, self.symbols, max_test=min(10, len(self.symbols)))
            
            success_rate = validation['success_rate']
            available = len(validation['available_symbols'])
            total = validation['total_tested']
            
            print(f"✅ Market validation: {available}/{total} symbols available ({success_rate:.1%})")
            
            if success_rate < 0.5:
                print("⚠️ Low success rate - falling back to core symbols")
                self.symbols = get_symbols_by_tier(1)  # Fallback to core ETFs
                self.market_tier = 1
            
            return success_rate
            
        except Exception as e:
            print(f"⚠️ Market validation failed: {e}")
            print("⚠️ Using core symbols only")
            self.symbols = ['SPY', 'QQQ', 'IWM']
            self.market_tier = 1
            return 0.0
    
    def get_expanded_market_data(self):
        """Get market data from expanded universe"""
        quotes = []
        successful_quotes = 0
        total_attempts = len(self.symbols)
        
        print(f"📈 Getting expanded market data ({total_attempts} symbols)...")
        
        # Start with core symbols for regime detection
        core_symbols = ['SPY', 'QQQ', 'IWM']
        core_quotes = []
        
        for symbol in core_symbols:
            try:
                quote = self.get_quote_with_storage(symbol)
                if quote:
                    core_quotes.append(quote)
                    quotes.append(quote)
                    successful_quotes += 1
                    print(f"   📊 {symbol}: ${quote['ask']:.2f}")
            except Exception as e:
                print(f"   ❌ {symbol}: Failed ({e})")
        
        # Add additional symbols from expanded universe (limit to prevent timeouts)
        additional_symbols = [s for s in self.symbols if s not in core_symbols]
        max_additional = min(10, len(additional_symbols))  # Limit for performance
        
        if additional_symbols and max_additional > 0:
            print(f"   📈 Sampling {max_additional} additional symbols...")
            
            for symbol in additional_symbols[:max_additional]:
                try:
                    quote = self.get_quote_with_storage(symbol)
                    if quote:
                        quotes.append(quote)
                        successful_quotes += 1
                        print(f"   📊 {symbol}: ${quote['ask']:.2f}")
                except Exception as e:
                    print(f"   ⚠️ {symbol}: Failed")
        
        success_rate = successful_quotes / min(len(core_symbols) + max_additional, total_attempts)
        print(f"📊 Market data success: {successful_quotes} symbols ({success_rate:.1%})")
        
        return quotes, core_quotes, success_rate
    
    def enhanced_market_regime_detection(self, quotes, core_quotes):
        """Enhanced market regime detection using expanded data"""
        # Core regime detection (maintain compatibility)
        core_regime = 'active' if len(core_quotes) >= 2 else 'uncertain'
        core_confidence = 0.8 if len(core_quotes) >= 2 else 0.4
        
        # Enhanced regime analysis
        if len(quotes) >= 5:
            # Strong data availability
            regime = 'active'
            confidence = min(0.9, 0.6 + (len(quotes) * 0.02))  # Increase confidence with more data
        elif len(quotes) >= 3:
            # Moderate data availability
            regime = 'active'
            confidence = 0.7
        elif len(core_quotes) >= 2:
            # Core symbols available
            regime = 'active'
            confidence = 0.6
        else:
            # Limited data
            regime = 'uncertain'
            confidence = 0.3
        
        # Sector analysis (if we have enough data)
        sector_health = self.analyze_sector_health(quotes)
        
        # Adjust confidence based on sector analysis
        if sector_health.get('strong_sectors', 0) >= 2:
            confidence = min(0.95, confidence + 0.1)
        elif sector_health.get('weak_sectors', 0) >= 2:
            confidence = max(0.2, confidence - 0.1)
        
        print(f"🎯 Enhanced Market Regime: {regime} ({confidence:.1%})")
        if sector_health:
            print(f"🏢 Sector Health: {sector_health.get('summary', 'N/A')}")
        
        return regime, confidence, sector_health
    
    def analyze_sector_health(self, quotes):
        """Analyze sector health from quotes data"""
        try:
            sectors = get_sector_symbols()
            sector_quotes = {}
            
            # Group quotes by sector
            for quote in quotes:
                symbol = quote['symbol']
                for sector, symbols in sectors.items():
                    if symbol in symbols:
                        if sector not in sector_quotes:
                            sector_quotes[sector] = []
                        sector_quotes[sector].append(quote)
            
            # Simple sector health analysis
            strong_sectors = 0
            weak_sectors = 0
            sector_summary = []
            
            for sector, sector_data in sector_quotes.items():
                if len(sector_data) >= 2:  # Need at least 2 quotes for analysis
                    strong_sectors += 1
                    sector_summary.append(f"{sector}({len(sector_data)})")
                elif len(sector_data) == 1:
                    sector_summary.append(f"{sector}(1)")
                else:
                    weak_sectors += 1
            
            return {
                'strong_sectors': strong_sectors,
                'weak_sectors': weak_sectors,
                'sector_data': sector_quotes,
                'summary': ', '.join(sector_summary[:5])  # Limit display
            }
            
        except Exception as e:
            print(f"⚠️ Sector analysis error: {e}")
            return {}
    
    def enhanced_strategy_selection(self, regime, confidence, sector_health, quotes):
        """Enhanced strategy selection with sector awareness"""
        # Base strategy selection
        if regime == 'active':
            if confidence >= 0.8:
                strategy = 'aggressive_momentum'
            elif confidence >= 0.6:
                strategy = 'momentum'
            else:
                strategy = 'cautious_momentum'
        else:
            strategy = 'conservative'
        
        # Sector-based adjustments
        if sector_health.get('strong_sectors', 0) >= 3:
            if strategy == 'momentum':
                strategy = 'aggressive_momentum'
            elif strategy == 'cautious_momentum':
                strategy = 'momentum'
        
        elif sector_health.get('weak_sectors', 0) >= 2:
            if strategy == 'aggressive_momentum':
                strategy = 'momentum'
            elif strategy == 'momentum':
                strategy = 'cautious_momentum'
        
        print(f"🎯 Enhanced Strategy: {strategy}")
        return strategy
    
    def enhanced_run_cycle_v2(self):
        """Enhanced trading cycle v2 with expanded market analysis"""
        self.cycle_count += 1
        
        print(f"\n🔄 ENHANCED TRADING CYCLE V2 #{self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 60)
        
        # Get expanded market data
        quotes, core_quotes, data_success_rate = self.get_expanded_market_data()
        
        # Enhanced market regime detection
        regime, confidence, sector_health = self.enhanced_market_regime_detection(quotes, core_quotes)
        
        # Enhanced strategy selection
        strategy = self.enhanced_strategy_selection(regime, confidence, sector_health, quotes)
        
        # Create enhanced cycle data
        cycle_data = {
            'regime': regime,
            'confidence': confidence,
            'strategy': strategy,
            'quotes_count': len(quotes),
            'core_quotes_count': len(core_quotes),
            'data_success_rate': data_success_rate,
            'sector_health': sector_health,
            'market_tier': self.market_tier,
            'total_symbols_attempted': len(self.symbols),
            'quotes': quotes[:5],  # Store top 5 quotes to save space
            'cycle_number': self.cycle_count,
            'enhanced_v2': True
        }
        
        # Store cycle in database
        cycle_id = None
        if self.use_database and self.db:
            try:
                cycle_id = self.db.store_trading_cycle(cycle_data, self.cycle_count)
                print(f"💾 Enhanced cycle data stored (DB ID: {cycle_id})")
            except Exception as e:
                print(f"⚠️ Cycle storage error: {e}")
        
        # Enhanced virtual trading simulation
        self.simulate_enhanced_virtual_trades(quotes, strategy, regime, confidence, cycle_id, sector_health)
        
        # Log cycle (maintain compatibility)
        self.log_cycle(cycle_data)
        print("✅ Enhanced cycle v2 completed")
        
        return cycle_data
    
    def simulate_enhanced_virtual_trades(self, quotes, strategy, regime, confidence, cycle_id=None, sector_health=None):
        """Enhanced virtual trading with sector awareness"""
        if not quotes or not self.use_database or not self.db:
            return
        
        try:
            trade_count = 0
            
            # Strategy-based trading simulation
            for quote in quotes[:8]:  # Limit to top 8 for performance
                symbol = quote['symbol']
                price = quote['ask']
                
                # Enhanced trading logic
                should_trade = False
                
                if strategy == 'aggressive_momentum' and confidence > 0.8:
                    should_trade = True
                elif strategy == 'momentum' and confidence > 0.6:
                    # Trade only core symbols and strong sector stocks
                    should_trade = symbol in ['SPY', 'QQQ', 'IWM'] or trade_count < 3
                elif strategy == 'cautious_momentum' and confidence > 0.5:
                    # Trade only core ETFs
                    should_trade = symbol in ['SPY', 'QQQ', 'IWM']
                
                if should_trade:
                    trade_id = self.db.store_virtual_trade(
                        symbol=symbol,
                        action='buy',
                        price=price,
                        strategy=strategy,
                        regime=regime,
                        confidence=confidence,
                        cycle_id=cycle_id
                    )
                    print(f"📊 Virtual {strategy.upper()}: {symbol} @ ${price:.2f} (Trade ID: {trade_id})")
                    trade_count += 1
            
            if trade_count == 0:
                print(f"📊 Virtual HOLD: No trades for {strategy} strategy")
                
        except Exception as e:
            print(f"⚠️ Enhanced virtual trading error: {e}")

def test_enhanced_trader_v2():
    """Test enhanced trader v2 functionality"""
    print("🧪 Testing Enhanced Trader V2...")
    
    # Test with different market tiers
    for tier in [1, 2]:
        print(f"\n🔍 Testing Market Tier {tier}...")
        trader = EnhancedTraderV2(use_database=True, market_tier=tier)
        
        # Test enhanced cycle
        cycle_data = trader.enhanced_run_cycle_v2()
        
        print(f"✅ Tier {tier} test completed")
        time.sleep(2)  # Brief pause between tests
    
    print("✅ Enhanced trader v2 tests completed!")
    return True

def main():
    """Entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        return test_enhanced_trader_v2()
    
    try:
        # Default to tier 2 (core + liquid stocks)
        market_tier = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 2
        trader = EnhancedTraderV2(use_database=True, market_tier=market_tier)
        trader.run_enhanced_continuous()
    except Exception as e:
        print(f"❌ Enhanced v2 startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()