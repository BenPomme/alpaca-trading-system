#!/usr/bin/env python3
"""
Comprehensive Trading Performance Analysis
Analyzes all completed trades and provides detailed insights
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import json

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import TradingDatabase
from order_manager import OrderManager
import alpaca_trade_api as tradeapi

def analyze_completed_trades():
    """Analyze all completed trades for performance insights"""
    print("📊 COMPREHENSIVE TRADING PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    try:
        # Initialize API and managers
        api_key = os.getenv('ALPACA_PAPER_API_KEY')
        secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
        
        if not api_key or not secret_key:
            print("❌ Missing Alpaca API credentials")
            return
        
        api = tradeapi.REST(api_key, secret_key, base_url='https://paper-api.alpaca.markets')
        db = TradingDatabase()
        
        # Get account information
        account = api.get_account()
        print(f"💰 Current Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"💵 Available Cash: ${float(account.cash):,.2f}")
        
        # Try to get P&L data if available
        try:
            print(f"📈 Day's P&L: ${float(getattr(account, 'todays_pl', 0)):,.2f}")
            print(f"📊 Total P&L: ${float(getattr(account, 'total_pl', 0)):,.2f}")
        except:
            print(f"📈 Day's P&L: Not available")
            print(f"📊 Total P&L: Not available")
        
        # Get recent orders (completed trades)
        print(f"\n📋 ANALYZING RECENT ORDERS...")
        orders = api.list_orders(status='filled', limit=100)
        
        if not orders:
            print("❌ No completed orders found")
            return
        
        print(f"✅ Found {len(orders)} completed orders")
        
        # Organize trades by symbol (pair buy/sell orders)
        trades_by_symbol = {}
        for order in orders:
            symbol = order.symbol
            if symbol not in trades_by_symbol:
                trades_by_symbol[symbol] = {'buys': [], 'sells': []}
            
            if order.side == 'buy':
                trades_by_symbol[symbol]['buys'].append(order)
            else:
                trades_by_symbol[symbol]['sells'].append(order)
        
        # Analyze completed round-trip trades
        completed_trades = []
        for symbol, trades in trades_by_symbol.items():
            buys = sorted(trades['buys'], key=lambda x: x.filled_at)
            sells = sorted(trades['sells'], key=lambda x: x.filled_at)
            
            # Match buy/sell pairs chronologically
            for buy in buys:
                for sell in sells:
                    if sell.filled_at > buy.filled_at:
                        # Found a sell after this buy
                        entry_price = float(buy.filled_avg_price)
                        exit_price = float(sell.filled_avg_price)
                        quantity = min(float(buy.filled_qty), float(sell.filled_qty))
                        
                        profit_loss = (exit_price - entry_price) * quantity
                        profit_pct = ((exit_price - entry_price) / entry_price) * 100
                        
                        completed_trades.append({
                            'symbol': symbol,
                            'entry_time': buy.filled_at,
                            'exit_time': sell.filled_at,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'quantity': quantity,
                            'profit_loss': profit_loss,
                            'profit_pct': profit_pct,
                            'hold_duration': (sell.filled_at - buy.filled_at).total_seconds() / 3600,  # hours
                            'buy_order_id': buy.id,
                            'sell_order_id': sell.id
                        })
                        break
        
        print(f"\n📊 COMPLETED ROUND-TRIP TRADES ANALYSIS")
        print(f"🔄 Total completed trades: {len(completed_trades)}")
        
        if not completed_trades:
            print("❌ No completed round-trip trades found")
            return
        
        # Performance Statistics
        total_trades = len(completed_trades)
        winning_trades = [t for t in completed_trades if t['profit_pct'] > 0]
        losing_trades = [t for t in completed_trades if t['profit_pct'] < 0]
        breakeven_trades = [t for t in completed_trades if t['profit_pct'] == 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        loss_rate = len(losing_trades) / total_trades if total_trades > 0 else 0
        
        total_profit_loss = sum(t['profit_loss'] for t in completed_trades)
        avg_profit_loss = total_profit_loss / total_trades if total_trades > 0 else 0
        
        avg_winning_pct = sum(t['profit_pct'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_losing_pct = sum(t['profit_pct'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        avg_hold_time = sum(t['hold_duration'] for t in completed_trades) / total_trades if total_trades > 0 else 0
        
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   🎯 Win Rate: {win_rate:.1%} ({len(winning_trades)} wins, {len(losing_trades)} losses, {len(breakeven_trades)} breakeven)")
        print(f"   💰 Total P&L: ${total_profit_loss:+,.2f}")
        print(f"   📊 Average P&L per trade: ${avg_profit_loss:+,.2f}")
        print(f"   📈 Average winning trade: {avg_winning_pct:+.2f}%")
        print(f"   📉 Average losing trade: {avg_losing_pct:+.2f}%")
        print(f"   ⏱️ Average hold time: {avg_hold_time:.1f} hours")
        
        # Best and worst trades
        best_trade = max(completed_trades, key=lambda x: x['profit_pct'])
        worst_trade = min(completed_trades, key=lambda x: x['profit_pct'])
        
        print(f"\n🏆 BEST TRADE:")
        print(f"   {best_trade['symbol']}: {best_trade['profit_pct']:+.2f}% (${best_trade['profit_loss']:+,.2f})")
        print(f"   Entry: ${best_trade['entry_price']:.2f} → Exit: ${best_trade['exit_price']:.2f}")
        print(f"   Hold: {best_trade['hold_duration']:.1f} hours")
        
        print(f"\n📉 WORST TRADE:")
        print(f"   {worst_trade['symbol']}: {worst_trade['profit_pct']:+.2f}% (${worst_trade['profit_loss']:+,.2f})")
        print(f"   Entry: ${worst_trade['entry_price']:.2f} → Exit: ${worst_trade['exit_price']:.2f}")
        print(f"   Hold: {worst_trade['hold_duration']:.1f} hours")
        
        # Recent trade details
        print(f"\n📋 RECENT COMPLETED TRADES (Last 10):")
        recent_trades = sorted(completed_trades, key=lambda x: x['exit_time'], reverse=True)[:10]
        
        for i, trade in enumerate(recent_trades, 1):
            status = "🟢" if trade['profit_pct'] > 0 else "🔴" if trade['profit_pct'] < 0 else "⚪"
            print(f"   {i:2d}. {status} {trade['symbol']}: {trade['profit_pct']:+.2f}% (${trade['profit_loss']:+,.2f}) - {trade['hold_duration']:.1f}h")
        
        # Symbol performance breakdown
        print(f"\n📊 PERFORMANCE BY SYMBOL:")
        symbol_performance = {}
        for trade in completed_trades:
            symbol = trade['symbol']
            if symbol not in symbol_performance:
                symbol_performance[symbol] = {'trades': [], 'total_pl': 0, 'wins': 0}
            
            symbol_performance[symbol]['trades'].append(trade)
            symbol_performance[symbol]['total_pl'] += trade['profit_loss']
            if trade['profit_pct'] > 0:
                symbol_performance[symbol]['wins'] += 1
        
        # Sort by total P&L
        sorted_symbols = sorted(symbol_performance.items(), key=lambda x: x[1]['total_pl'], reverse=True)
        
        for symbol, perf in sorted_symbols[:10]:  # Top 10 symbols
            trade_count = len(perf['trades'])
            win_rate = perf['wins'] / trade_count if trade_count > 0 else 0
            avg_pl = perf['total_pl'] / trade_count if trade_count > 0 else 0
            
            status = "🟢" if perf['total_pl'] > 0 else "🔴"
            print(f"   {status} {symbol}: {trade_count} trades, {win_rate:.1%} win rate, ${perf['total_pl']:+,.2f} total (${avg_pl:+,.2f} avg)")
        
        # Strategy insights
        print(f"\n💡 STRATEGY INSIGHTS:")
        
        # Hold time analysis
        short_holds = [t for t in completed_trades if t['hold_duration'] < 1]  # < 1 hour
        medium_holds = [t for t in completed_trades if 1 <= t['hold_duration'] < 24]  # 1-24 hours
        long_holds = [t for t in completed_trades if t['hold_duration'] >= 24]  # > 24 hours
        
        if short_holds:
            short_win_rate = len([t for t in short_holds if t['profit_pct'] > 0]) / len(short_holds)
            short_avg_pl = sum(t['profit_loss'] for t in short_holds) / len(short_holds)
            print(f"   ⚡ Short holds (<1h): {len(short_holds)} trades, {short_win_rate:.1%} win rate, ${short_avg_pl:+,.2f} avg")
        
        if medium_holds:
            medium_win_rate = len([t for t in medium_holds if t['profit_pct'] > 0]) / len(medium_holds)
            medium_avg_pl = sum(t['profit_loss'] for t in medium_holds) / len(medium_holds)
            print(f"   🕐 Medium holds (1-24h): {len(medium_holds)} trades, {medium_win_rate:.1%} win rate, ${medium_avg_pl:+,.2f} avg")
        
        if long_holds:
            long_win_rate = len([t for t in long_holds if t['profit_pct'] > 0]) / len(long_holds)
            long_avg_pl = sum(t['profit_loss'] for t in long_holds) / len(long_holds)
            print(f"   📅 Long holds (>24h): {len(long_holds)} trades, {long_win_rate:.1%} win rate, ${long_avg_pl:+,.2f} avg")
        
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS:")
        
        if win_rate < 0.6:
            print(f"   ⚠️ Win rate is {win_rate:.1%} - consider tightening entry criteria")
        
        if avg_losing_pct < -3.0:
            print(f"   ⚠️ Average loss is {avg_losing_pct:.1f}% - consider tighter stop losses")
        
        if avg_winning_pct < 2.0:
            print(f"   💡 Average win is only {avg_winning_pct:.1f}% - let winners run longer")
        
        profit_loss_ratio = abs(avg_winning_pct / avg_losing_pct) if avg_losing_pct != 0 else float('inf')
        if profit_loss_ratio < 1.5:
            print(f"   📊 Profit/loss ratio is {profit_loss_ratio:.1f} - aim for 2:1 or better")
        
        if total_profit_loss < 0:
            print(f"   🔴 Overall losses of ${total_profit_loss:,.2f} - review strategy effectiveness")
        else:
            print(f"   🟢 Overall profits of ${total_profit_loss:,.2f} - strategy is working")
        
        # Current positions analysis
        print(f"\n📊 CURRENT OPEN POSITIONS:")
        positions = api.list_positions()
        
        if positions:
            total_unrealized = sum(float(pos.unrealized_pl) for pos in positions)
            print(f"   📈 Open positions: {len(positions)}")
            print(f"   💰 Total unrealized P&L: ${total_unrealized:+,.2f}")
            
            print(f"\n   Top positions by P&L:")
            sorted_positions = sorted(positions, key=lambda x: float(x.unrealized_pl), reverse=True)
            
            for i, pos in enumerate(sorted_positions[:5], 1):
                unrealized_pl = float(pos.unrealized_pl)
                unrealized_plpc = float(pos.unrealized_plpc) * 100
                status = "🟢" if unrealized_pl > 0 else "🔴"
                print(f"      {i}. {status} {pos.symbol}: ${unrealized_pl:+,.2f} ({unrealized_plpc:+.1f}%)")
        else:
            print(f"   📊 No open positions")
        
        print(f"\n✅ Analysis complete!")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_completed_trades()