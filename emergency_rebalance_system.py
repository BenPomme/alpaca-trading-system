#!/usr/bin/env python3
"""
EMERGENCY REBALANCING SYSTEM
Critical fix for crypto over-allocation and profitability issues
"""

import os
import alpaca_trade_api as tradeapi
import json
from datetime import datetime
import time

# Set environment variables
os.environ['ALPACA_PAPER_API_KEY'] = "PKOBXG3RWCRQTXH6ID0L"
os.environ['ALPACA_PAPER_SECRET_KEY'] = "8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn"
os.environ['ALPACA_BASE_URL'] = "https://paper-api.alpaca.markets"

class EmergencyRebalancer:
    def __init__(self, execute_trades=False):
        self.execute_trades = execute_trades
        self.api = tradeapi.REST(
            os.environ['ALPACA_PAPER_API_KEY'],
            os.environ['ALPACA_PAPER_SECRET_KEY'],
            os.environ['ALPACA_BASE_URL'],
            api_version='v2'
        )
        
        # Target allocations based on research
        self.target_allocations = {
            'crypto': 0.30,    # 30% max crypto (down from 89.5%)
            'stocks': 0.50,    # 50% stocks (up from 3.1%)
            'cash': 0.20       # 20% cash for opportunities
        }
        
        # Stop loss thresholds
        self.stop_loss_threshold = -0.15  # 15% stop loss
        self.profit_target = 0.25         # 25% profit target
        
    def analyze_current_state(self):
        """Analyze current portfolio state"""
        print("🔍 ANALYZING CURRENT PORTFOLIO STATE...")
        
        account = self.api.get_account()
        positions = self.api.list_positions()
        
        portfolio_value = float(account.portfolio_value)
        cash = float(account.cash)
        
        print(f"💰 Portfolio Value: ${portfolio_value:,.2f}")
        print(f"💵 Cash: ${cash:,.2f}")
        print(f"📊 Total Positions: {len(positions)}")
        
        # Categorize positions
        crypto_value = 0
        stock_value = 0
        crypto_positions = []
        stock_positions = []
        bleeding_positions = []
        profit_positions = []
        
        for pos in positions:
            market_value = float(pos.market_value)
            unrealized_pl = float(pos.unrealized_pl)
            unrealized_plpc = float(pos.unrealized_plpc)
            
            position_data = {
                'symbol': pos.symbol,
                'qty': float(pos.qty),
                'market_value': market_value,
                'unrealized_pl': unrealized_pl,
                'unrealized_plpc': unrealized_plpc,
                'avg_entry_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price)
            }
            
            # Categorize by asset type
            if 'USD' in pos.symbol and len(pos.symbol) <= 7:  # Crypto
                crypto_value += market_value
                crypto_positions.append(position_data)
            else:  # Stocks
                stock_value += market_value
                stock_positions.append(position_data)
            
            # Categorize by performance
            if unrealized_plpc <= self.stop_loss_threshold:
                bleeding_positions.append(position_data)
            elif unrealized_plpc >= self.profit_target:
                profit_positions.append(position_data)
        
        # Calculate allocations
        crypto_pct = (crypto_value / portfolio_value) * 100
        stock_pct = (stock_value / portfolio_value) * 100
        cash_pct = (cash / portfolio_value) * 100
        
        analysis = {
            'portfolio_value': portfolio_value,
            'cash': cash,
            'crypto_value': crypto_value,
            'stock_value': stock_value,
            'crypto_pct': crypto_pct,
            'stock_pct': stock_pct,
            'cash_pct': cash_pct,
            'crypto_positions': crypto_positions,
            'stock_positions': stock_positions,
            'bleeding_positions': bleeding_positions,
            'profit_positions': profit_positions,
            'total_positions': len(positions)
        }
        
        print(f"\n📊 CURRENT ALLOCATION:")
        print(f"  ₿ Crypto: ${crypto_value:,.2f} ({crypto_pct:.1f}%)")
        print(f"  📈 Stocks: ${stock_value:,.2f} ({stock_pct:.1f}%)")
        print(f"  💵 Cash: ${cash:,.2f} ({cash_pct:.1f}%)")
        
        print(f"\n🎯 TARGET ALLOCATION:")
        print(f"  ₿ Crypto: {self.target_allocations['crypto']*100:.1f}%")
        print(f"  📈 Stocks: {self.target_allocations['stocks']*100:.1f}%")
        print(f"  💵 Cash: {self.target_allocations['cash']*100:.1f}%")
        
        # Identify critical issues
        issues = []
        if crypto_pct > self.target_allocations['crypto'] * 100:
            excess_crypto = crypto_pct - (self.target_allocations['crypto'] * 100)
            issues.append(f"🚨 CRYPTO OVER-ALLOCATION: {excess_crypto:.1f}% excess")
        
        if stock_pct < self.target_allocations['stocks'] * 100:
            stock_deficit = (self.target_allocations['stocks'] * 100) - stock_pct
            issues.append(f"🚨 STOCK UNDER-ALLOCATION: {stock_deficit:.1f}% deficit")
        
        if bleeding_positions:
            total_bleeding = sum(p['unrealized_pl'] for p in bleeding_positions)
            issues.append(f"🩸 BLEEDING POSITIONS: {len(bleeding_positions)} positions, ${total_bleeding:+.2f}")
        
        if issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in issues:
                print(f"  {issue}")
        
        return analysis
    
    def calculate_rebalancing_trades(self, analysis):
        """Calculate what trades needed to rebalance"""
        print(f"\n🔧 CALCULATING REBALANCING TRADES...")
        
        portfolio_value = analysis['portfolio_value']
        
        # Target values
        target_crypto_value = portfolio_value * self.target_allocations['crypto']
        target_stock_value = portfolio_value * self.target_allocations['stocks']
        target_cash = portfolio_value * self.target_allocations['cash']
        
        # Current excess/deficit
        crypto_excess = analysis['crypto_value'] - target_crypto_value
        stock_deficit = target_stock_value - analysis['stock_value']
        
        print(f"📊 REBALANCING REQUIREMENTS:")
        print(f"  ₿ Crypto: Need to REDUCE by ${crypto_excess:,.2f}")
        print(f"  📈 Stocks: Need to INCREASE by ${stock_deficit:,.2f}")
        
        trades = []
        
        # 1. EMERGENCY STOP LOSSES - Close bleeding positions first
        print(f"\n🩸 EMERGENCY STOP LOSSES:")
        for pos in analysis['bleeding_positions']:
            trades.append({
                'action': 'SELL',
                'symbol': pos['symbol'],
                'qty': abs(pos['qty']),
                'reason': f"STOP LOSS ({pos['unrealized_plpc']*100:+.1f}%)",
                'priority': 'CRITICAL',
                'market_value': pos['market_value']
            })
            print(f"  🛑 SELL {pos['symbol']}: {pos['qty']} shares (${pos['unrealized_pl']:+.2f})")
        
        # 2. PROFIT TAKING - Secure gains on winners
        print(f"\n💰 PROFIT TAKING:")
        for pos in analysis['profit_positions']:
            # Take 50% profits on big winners
            sell_qty = abs(pos['qty']) * 0.5
            trades.append({
                'action': 'SELL',
                'symbol': pos['symbol'],
                'qty': sell_qty,
                'reason': f"PROFIT TAKING ({pos['unrealized_plpc']*100:+.1f}%)",
                'priority': 'HIGH',
                'market_value': pos['market_value'] * 0.5
            })
            print(f"  💰 SELL 50% of {pos['symbol']}: {sell_qty:.2f} shares (${pos['unrealized_pl']:+.2f})")
        
        # 3. CRYPTO REDUCTION - Reduce crypto to 30%
        if crypto_excess > 1000:  # Only if significant excess
            print(f"\n₿ CRYPTO REDUCTION:")
            # Sort crypto positions by performance, sell worst first
            crypto_sorted = sorted(analysis['crypto_positions'], 
                                 key=lambda x: x['unrealized_plpc'])
            
            remaining_to_sell = crypto_excess
            for pos in crypto_sorted:
                if remaining_to_sell <= 0:
                    break
                    
                # Don't double-sell positions already in stop loss
                if pos in analysis['bleeding_positions']:
                    continue
                
                # Sell portion or all of position
                sell_value = min(pos['market_value'], remaining_to_sell)
                sell_qty = (sell_value / pos['market_value']) * abs(pos['qty'])
                
                trades.append({
                    'action': 'SELL',
                    'symbol': pos['symbol'],
                    'qty': sell_qty,
                    'reason': 'CRYPTO REBALANCE',
                    'priority': 'HIGH',
                    'market_value': sell_value
                })
                
                print(f"  ₿ SELL {pos['symbol']}: {sell_qty:.2f} shares (${sell_value:,.2f})")
                remaining_to_sell -= sell_value
        
        # 4. STOCK PURCHASES - Increase stock allocation
        if stock_deficit > 1000:  # Only if significant deficit
            print(f"\n📈 STOCK PURCHASES:")
            
            # Buy high-quality stocks with available cash/proceeds
            target_stocks = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']
            cash_per_stock = stock_deficit / len(target_stocks)
            
            for stock in target_stocks:
                trades.append({
                    'action': 'BUY',
                    'symbol': stock,
                    'qty': None,  # Will calculate based on current price
                    'reason': 'STOCK REBALANCE',
                    'priority': 'MEDIUM',
                    'market_value': cash_per_stock
                })
                print(f"  📈 BUY {stock}: ${cash_per_stock:,.2f} worth")
        
        return trades
    
    def execute_rebalancing_trades(self, trades):
        """Execute the rebalancing trades"""
        if not self.execute_trades:
            print(f"\n⚠️ SIMULATION MODE - No trades will be executed")
            print(f"📋 Would execute {len(trades)} trades:")
            for trade in trades:
                print(f"  {trade['priority']}: {trade['action']} {trade['symbol']} - {trade['reason']}")
            return
        
        print(f"\n🚀 EXECUTING {len(trades)} REBALANCING TRADES...")
        
        executed_trades = []
        failed_trades = []
        
        # Sort by priority: CRITICAL > HIGH > MEDIUM
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
        trades.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        for trade in trades:
            try:
                print(f"\n🔄 {trade['priority']}: {trade['action']} {trade['symbol']}")
                
                if trade['action'] == 'SELL':
                    order = self.api.submit_order(
                        symbol=trade['symbol'],
                        qty=trade['qty'],
                        side='sell',
                        type='market',
                        time_in_force='gtc' if 'USD' in trade['symbol'] else 'day'
                    )
                    print(f"  ✅ SELL order submitted: {order.id}")
                    
                elif trade['action'] == 'BUY':
                    # Get current price to calculate quantity
                    quote = self.api.get_latest_quote(trade['symbol'])
                    price = float(quote.ask_price)
                    qty = int(trade['market_value'] / price)
                    
                    if qty > 0:
                        order = self.api.submit_order(
                            symbol=trade['symbol'],
                            qty=qty,
                            side='buy',
                            type='market',
                            time_in_force='day'
                        )
                        print(f"  ✅ BUY order submitted: {order.id} ({qty} shares @ ${price:.2f})")
                    else:
                        print(f"  ⚠️ Skipped {trade['symbol']}: Insufficient funds for 1 share")
                
                executed_trades.append(trade)
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"  ❌ FAILED: {e}")
                failed_trades.append({'trade': trade, 'error': str(e)})
        
        print(f"\n📊 EXECUTION SUMMARY:")
        print(f"  ✅ Executed: {len(executed_trades)}")
        print(f"  ❌ Failed: {len(failed_trades)}")
        
        return executed_trades, failed_trades
    
    def implement_stop_losses(self, analysis):
        """Implement stop losses on remaining positions"""
        print(f"\n🛡️ IMPLEMENTING STOP LOSSES ON REMAINING POSITIONS...")
        
        if not self.execute_trades:
            print(f"⚠️ SIMULATION MODE - No stop losses will be set")
            return
        
        # Set stop losses on positions that don't already have them
        for pos in analysis['crypto_positions'] + analysis['stock_positions']:
            # Skip positions already in bleeding category
            if pos['unrealized_plpc'] <= self.stop_loss_threshold:
                continue
            
            try:
                # Calculate stop loss price (15% below current entry)
                stop_price = pos['avg_entry_price'] * (1 + self.stop_loss_threshold)
                
                # Submit stop loss order
                order = self.api.submit_order(
                    symbol=pos['symbol'],
                    qty=abs(pos['qty']),
                    side='sell',
                    type='stop',
                    stop_price=stop_price,
                    time_in_force='gtc' if 'USD' in pos['symbol'] else 'day'
                )
                
                print(f"  🛡️ Stop loss set for {pos['symbol']}: ${stop_price:.2f}")
                
            except Exception as e:
                print(f"  ❌ Failed to set stop loss for {pos['symbol']}: {e}")
    
    def run_emergency_rebalance(self):
        """Run the complete emergency rebalancing process"""
        print("🚨 EMERGENCY PORTFOLIO REBALANCING INITIATED")
        print("=" * 60)
        
        # 1. Analyze current state
        analysis = self.analyze_current_state()
        
        # 2. Calculate rebalancing trades
        trades = self.calculate_rebalancing_trades(analysis)
        
        # 3. Execute trades (if enabled)
        executed, failed = self.execute_rebalancing_trades(trades)
        
        # 4. Implement stop losses
        self.implement_stop_losses(analysis)
        
        # 5. Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'planned_trades': len(trades),
            'executed_trades': len(executed) if executed else 0,
            'failed_trades': len(failed) if failed else 0,
            'rebalance_mode': 'EXECUTED' if self.execute_trades else 'SIMULATION'
        }
        
        with open('emergency_rebalance_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📁 Report saved to: emergency_rebalance_report.json")
        
        # Summary
        print(f"\n📊 EMERGENCY REBALANCING SUMMARY:")
        print(f"  🎯 Target Crypto Allocation: {self.target_allocations['crypto']*100:.1f}%")
        print(f"  📈 Target Stock Allocation: {self.target_allocations['stocks']*100:.1f}%")
        print(f"  💵 Target Cash: {self.target_allocations['cash']*100:.1f}%")
        print(f"  🔄 Trades Planned: {len(trades)}")
        if self.execute_trades:
            print(f"  ✅ Trades Executed: {len(executed)}")
            print(f"  ❌ Trades Failed: {len(failed)}")
        
        return report

def main():
    print("🚨 CRITICAL PORTFOLIO REBALANCING SYSTEM")
    print("=" * 60)
    
    # Ask user if they want to execute trades or simulate
    print("⚠️ WARNING: This will make real trades with your Alpaca account!")
    print("Choose mode:")
    print("1. SIMULATION (recommended) - Show what would happen")
    print("2. EXECUTE - Make real trades")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    execute_mode = choice == "2"
    
    if execute_mode:
        confirm = input("🚨 CONFIRM: Type 'EXECUTE' to proceed with real trades: ").strip()
        if confirm != "EXECUTE":
            print("❌ Aborted - No trades executed")
            return
    
    # Run rebalancing
    rebalancer = EmergencyRebalancer(execute_trades=execute_mode)
    report = rebalancer.run_emergency_rebalance()
    
    if execute_mode:
        print("\n✅ EMERGENCY REBALANCING COMPLETED!")
        print("🔍 Monitor your positions and check for order fills")
    else:
        print("\n📊 SIMULATION COMPLETED!")
        print("🚀 Run with EXECUTE mode to implement changes")

if __name__ == "__main__":
    main()