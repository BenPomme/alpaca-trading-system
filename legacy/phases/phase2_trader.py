#!/usr/bin/env python3
"""
Phase 2 Trading System: Execution Engine
Actual paper trading with risk management and stop-loss automation
"""

import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List
from enhanced_trader_v2 import EnhancedTraderV2
from order_manager import OrderManager
from risk_manager import RiskManager
from database_manager import TradingDatabase

class Phase2Trader(EnhancedTraderV2):
    """Phase 2 trader with actual execution capabilities"""
    
    def __init__(self, use_database=True, market_tier=2):
        # Initialize enhanced trader
        super().__init__(use_database, market_tier)
        
        # Initialize execution components
        self.order_manager = OrderManager(self.api, self.db)
        self.risk_manager = RiskManager(self.api, self.db)
        
        # Execution parameters
        self.execution_enabled = True
        self.min_confidence_to_trade = 0.6
        self.trade_count_today = 0
        
        print("🚀 Phase 2 Trader initialized - EXECUTION ENABLED")
        print(f"📊 Market Tier: {market_tier}, Database: {'ON' if use_database else 'OFF'}")
    
    def should_place_trade(self, symbol: str, strategy: str, confidence: float, quotes: list) -> bool:
        """Determine if we should place an actual trade"""
        
        # Confidence threshold
        if confidence < self.min_confidence_to_trade:
            print(f"⚠️ Confidence too low for {symbol}: {confidence:.1%} < {self.min_confidence_to_trade:.1%}")
            return False
        
        # Core ETFs get priority (more reliable)
        core_symbols = ['SPY', 'QQQ', 'IWM']
        is_core_symbol = symbol in core_symbols
        
        # Strategy-based trading rules
        trade_rules = {
            'aggressive_momentum': confidence >= 0.8 and len(quotes) >= 8,
            'momentum': confidence >= 0.7 and (is_core_symbol or len(quotes) >= 6),
            'cautious_momentum': confidence >= 0.6 and is_core_symbol,
            'conservative': False  # No trades in conservative mode
        }
        
        should_trade = trade_rules.get(strategy, False)
        
        if should_trade:
            print(f"✅ Trade criteria met for {symbol}: {strategy} strategy, {confidence:.1%} confidence")
        else:
            print(f"⚠️ Trade criteria not met for {symbol}: {strategy} strategy")
        
        return should_trade
    
    def execute_trading_decisions(self, quotes: list, strategy: str, confidence: float, cycle_id: int = None) -> Dict:
        """Execute actual trading decisions based on analysis"""
        
        if not self.execution_enabled:
            print("⚠️ Trade execution disabled")
            return {
                'trades_executed': 0, 
                'trades_skipped': 0,
                'executed_trades': [],
                'skipped_trades': [],
                'strategy': strategy,
                'confidence': confidence,
                'reason': 'execution_disabled'
            }
        
        executed_trades = []
        skipped_trades = []
        
        print(f"\n💰 EXECUTING TRADING DECISIONS")
        print(f"   Strategy: {strategy}")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Available symbols: {len(quotes)}")
        print("-" * 40)
        
        # Prioritize core ETFs for stability
        core_symbols = ['SPY', 'QQQ', 'IWM']
        core_quotes = [q for q in quotes if q['symbol'] in core_symbols]
        other_quotes = [q for q in quotes if q['symbol'] not in core_symbols]
        
        # Process core symbols first
        priority_quotes = core_quotes + other_quotes[:5]  # Limit to avoid overtrading
        
        for quote in priority_quotes:
            symbol = quote['symbol']
            current_price = quote['ask']
            
            print(f"\n🔍 Evaluating {symbol} @ ${current_price:.2f}")
            
            # Check if we should trade this symbol
            if not self.should_place_trade(symbol, strategy, confidence, quotes):
                skipped_trades.append({'symbol': symbol, 'reason': 'criteria_not_met'})
                continue
            
            # Risk management check
            approved, approval_msg, trade_info = self.risk_manager.should_execute_trade(
                symbol, strategy, confidence, current_price
            )
            
            if not approved:
                print(f"❌ Trade rejected: {approval_msg}")
                skipped_trades.append({'symbol': symbol, 'reason': approval_msg})
                continue
            
            # Execute the trade
            print(f"💰 EXECUTING BUY ORDER: {symbol}")
            
            result = self.order_manager.execute_buy_order(
                symbol=symbol,
                strategy=strategy,
                confidence=confidence,
                cycle_id=cycle_id
            )
            
            if result['success']:
                executed_trades.append(result)
                self.trade_count_today += 1
                
                # Calculate and store stop-loss/take-profit levels
                entry_price = result['price']
                sl_tp = self.risk_manager.calculate_stop_loss_take_profit(entry_price, strategy)
                
                print(f"🎯 Stop Loss: ${sl_tp['stop_loss_price']:.2f} ({sl_tp['stop_loss_pct']:.1%})")
                print(f"🎯 Take Profit: ${sl_tp['take_profit_price']:.2f} ({sl_tp['take_profit_pct']:.1%})")
                
                # Store trade details in database
                if self.db:
                    try:
                        # Store actual trade record
                        trade_id = self.db.store_virtual_trade(
                            symbol=symbol,
                            action='buy_executed',
                            price=entry_price,
                            strategy=strategy,
                            regime='active',
                            confidence=confidence,
                            cycle_id=cycle_id
                        )
                        print(f"💾 Trade stored in database (ID: {trade_id})")
                    except Exception as e:
                        print(f"⚠️ Database storage error: {e}")
            else:
                print(f"❌ Trade execution failed: {result['reason']}")
                skipped_trades.append({'symbol': symbol, 'reason': result['reason']})
        
        # Summary
        total_executed = len(executed_trades)
        total_skipped = len(skipped_trades)
        
        print(f"\n📊 TRADING SUMMARY")
        print(f"   ✅ Executed: {total_executed} trades")
        print(f"   ⚠️ Skipped: {total_skipped} trades")
        print(f"   💰 Total deployed: ${sum(t.get('total_value', 0) for t in executed_trades):,.2f}")
        
        return {
            'trades_executed': total_executed,
            'trades_skipped': total_skipped,
            'executed_trades': executed_trades,
            'skipped_trades': skipped_trades,
            'strategy': strategy,
            'confidence': confidence
        }
    
    def check_and_manage_positions(self) -> Dict:
        """Check existing positions for stop-loss and take-profit"""
        
        print(f"\n🔍 POSITION MANAGEMENT CHECK")
        print("-" * 30)
        
        # Check stop losses
        executed_stops = self.order_manager.check_stop_losses()
        
        # Get current portfolio status
        portfolio = self.order_manager.get_portfolio_summary()
        
        if executed_stops:
            print(f"🛑 Executed {len(executed_stops)} stop-loss/take-profit orders")
            for stop in executed_stops:
                print(f"   {stop['symbol']}: {stop['reason']} - P&L: ${stop['profit_loss']:+.2f}")
        
        # Check for positions held too long (max 5 days)
        try:
            positions = self.api.list_positions()
            for pos in positions:
                # In a real system, we'd track entry dates from database
                # For now, we'll use a simple heuristic
                pass
        except Exception as e:
            print(f"⚠️ Position check error: {e}")
        
        return {
            'stop_losses_executed': len(executed_stops),
            'executed_stops': executed_stops,
            'portfolio_summary': portfolio
        }
    
    def run_phase2_cycle(self):
        """Enhanced trading cycle with actual execution"""
        self.cycle_count += 1
        
        print(f"\n🚀 PHASE 2 TRADING CYCLE #{self.cycle_count}")
        print("=" * 60)
        print(f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📊 Market Tier: {self.market_tier}")
        print(f"💰 Execution: {'ENABLED' if self.execution_enabled else 'DISABLED'}")
        print()
        
        # Step 1: Position Management (check stops, take profits)
        position_results = self.check_and_manage_positions()
        
        # Step 2: Market Analysis (from Phase 1)
        quotes, core_quotes, data_success_rate = self.get_expanded_market_data()
        regime, confidence, sector_health = self.enhanced_market_regime_detection(quotes, core_quotes)
        strategy = self.enhanced_strategy_selection(regime, confidence, sector_health, quotes)
        
        # Step 3: Trading Execution (NEW in Phase 2)
        execution_results = self.execute_trading_decisions(quotes, strategy, confidence, self.cycle_count)
        
        # Step 4: Enhanced Cycle Data
        cycle_data = {
            'regime': regime,
            'confidence': confidence,
            'strategy': strategy,
            'quotes_count': len(quotes),
            'core_quotes_count': len(core_quotes),
            'data_success_rate': data_success_rate,
            'sector_health': sector_health,
            'market_tier': self.market_tier,
            'execution_enabled': self.execution_enabled,
            'trades_executed': execution_results['trades_executed'],
            'trades_skipped': execution_results['trades_skipped'],
            'stop_losses_executed': position_results['stop_losses_executed'],
            'cycle_number': self.cycle_count,
            'phase2': True,
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 5: Database Storage
        cycle_id = None
        if self.use_database and self.db:
            try:
                cycle_id = self.db.store_trading_cycle(cycle_data, self.cycle_count)
                print(f"💾 Phase 2 cycle data stored (DB ID: {cycle_id})")
            except Exception as e:
                print(f"⚠️ Cycle storage error: {e}")
        
        # Step 6: Performance Summary
        self.show_phase2_performance_summary()
        
        print("✅ Phase 2 cycle completed")
        return cycle_data
    
    def show_phase2_performance_summary(self):
        """Show comprehensive performance summary"""
        try:
            portfolio = self.order_manager.get_portfolio_summary()
            risk_metrics = self.risk_manager.get_risk_metrics()
            
            print(f"\n📈 PHASE 2 PERFORMANCE SUMMARY")
            print("-" * 40)
            print(f"💰 Portfolio Value: ${portfolio.get('portfolio_value', 0):,.2f}")
            print(f"💵 Buying Power: ${portfolio.get('buying_power', 0):,.2f}")
            print(f"📊 Positions: {portfolio.get('total_positions', 0)}")
            print(f"📈 Unrealized P&L: ${portfolio.get('total_unrealized_pl', 0):+,.2f}")
            print(f"📊 Daily P&L: {risk_metrics.get('daily_pl_pct', 0):+.2f}%")
            print(f"📊 Portfolio Utilization: {risk_metrics.get('portfolio_utilization_pct', 0):.1f}%")
            
            if portfolio.get('positions'):
                print(f"\n📋 Current Positions:")
                for pos in portfolio['positions']:
                    pnl_pct = pos.get('unrealized_plpc', 0)
                    status = "📈" if pnl_pct >= 0 else "📉"
                    print(f"   {status} {pos['symbol']}: {pos['qty']:+.0f} shares, "
                          f"${pos['market_value']:,.2f} ({pnl_pct:+.1f}%)")
            
        except Exception as e:
            print(f"⚠️ Performance summary error: {e}")
    
    def run_phase2_continuous(self):
        """Phase 2 continuous monitoring with execution"""
        print("🚀 PHASE 2: EXECUTION ENGINE")
        print("=" * 50)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("☁️ Platform: Railway Cloud")
        print("💰 Mode: Paper Trading with ACTUAL EXECUTION")
        print("🧠 Version: Phase 2 - Execution Engine")
        print("📊 Features: Order Management + Risk Management + Stop-Loss Automation")
        print()
        
        # Account verification
        if not self.check_account():
            return
        
        # Show initial portfolio
        self.show_phase2_performance_summary()
        
        print(f"\n🔄 Starting Phase 2 continuous execution...")
        print("   (System will execute actual paper trades)")
        print()
        
        try:
            while True:
                print(f"📊 Phase 2 Cycle #{self.cycle_count + 1}")
                
                # Run Phase 2 cycle with execution
                cycle_data = self.run_phase2_cycle()
                
                # Show performance update every cycle
                if cycle_data.get('trades_executed', 0) > 0:
                    print(f"\n🎯 TRADES EXECUTED THIS CYCLE: {cycle_data['trades_executed']}")
                
                # Wait between cycles (2 minutes)
                wait_time = 120
                print(f"\n⏳ Next Phase 2 cycle in {wait_time} seconds...")
                print(f"   (Use this time to monitor positions)")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Phase 2 trading stopped manually")
            self.show_phase2_performance_summary()
            
        except Exception as e:
            print(f"\n❌ Phase 2 system error: {e}")
            print("🔄 Restarting in 60 seconds...")
            time.sleep(60)

def test_phase2_trader():
    """Test Phase 2 trader functionality"""
    print("🧪 Testing Phase 2 Trader...")
    
    # Test with execution disabled first
    trader = Phase2Trader(use_database=True, market_tier=1)
    trader.execution_enabled = False  # Safety first
    
    # Test single cycle
    cycle_data = trader.run_phase2_cycle()
    
    print(f"✅ Phase 2 test completed - Trades executed: {cycle_data.get('trades_executed', 0)}")
    return True

def main():
    """Phase 2 entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        return test_phase2_trader()
    
    try:
        # Get parameters from environment or arguments
        market_tier = int(os.environ.get('MARKET_TIER', '2'))
        execution_enabled = os.environ.get('EXECUTION_ENABLED', 'true').lower() == 'true'
        
        # Initialize Phase 2 trader
        trader = Phase2Trader(use_database=True, market_tier=market_tier)
        trader.execution_enabled = execution_enabled
        
        if not execution_enabled:
            print("⚠️ EXECUTION DISABLED - Running in analysis mode only")
        
        # Run Phase 2 continuous system
        trader.run_phase2_continuous()
        
    except Exception as e:
        print(f"❌ Phase 2 startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()