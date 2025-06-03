#!/usr/bin/env python3
"""
Loss Analysis Script
Analyze the rapid-fire trading pattern that caused 2% capital loss
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal, getcontext

# Set precision for accurate financial calculations
getcontext().prec = 28

# Load environment variables manually
def load_env_file():
    env_file = '.env.local'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"').strip("'")
                    os.environ[key] = value

load_env_file()

# Trade data from your message
trades_data = """
AVAXUSD,Market,sell,1104.52075461,1104.52075461,21.121402,filled,Jun 03 2025 11:39:29 AM
DOTUSD,Market,sell,5651.95965355,5651.95965355,4.10215,filled,Jun 03 2025 11:39:27 AM
LINKUSD,Market,sell,5019.61884775,5019.61884775,13.886219,filled,Jun 03 2025 11:39:25 AM
UNIUSD,Market,buy,3686.58249897,3686.58249897,6.45862,filled,Jun 03 2025 11:39:22 AM
AVAXUSD,Market,buy,1107.16276876,1107.16276876,21.468516,filled,Jun 03 2025 11:39:20 AM
LINKUSD,Market,buy,1673.83802878,1673.83802878,14.15018,filled,Jun 03 2025 11:39:18 AM
DOTUSD,Market,buy,5662.836963,5662.836963,4.222807,filled,Jun 03 2025 11:39:16 AM
ETHUSD,Market,buy,9.01857093,9.01857093,2616.751354,filled,Jun 03 2025 11:39:14 AM
ETHUSD,Market,sell,18.06032177,18.06032177,2611.430112,filled,Jun 03 2025 11:38:29 AM
AVAXUSD,Market,sell,2216.43272636,2216.43272636,20.971944,filled,Jun 03 2025 11:38:27 AM
DOTUSD,Market,sell,11341.7846379,11341.7846379,4.087778,filled,Jun 03 2025 11:38:25 AM
UNIUSD,Market,buy,3696.2426237,3696.2426237,6.452847,filled,Jun 03 2025 11:38:23 AM
AVAXUSD,Market,buy,1110.0639192,1110.0639192,21.465471,filled,Jun 03 2025 11:38:20 AM
LINKUSD,Market,buy,1678.22406494,1678.22406494,14.150186,filled,Jun 03 2025 11:38:18 AM
DOTUSD,Market,buy,5677.67555983,5677.67555983,4.222963,filled,Jun 03 2025 11:38:16 AM
ETHUSD,Market,buy,9.04220272,9.04220272,2615.304134,filled,Jun 03 2025 11:38:14 AM
UNIUSD,Market,buy,3697.25927899,3697.25927899,6.454645,filled,Jun 03 2025 11:37:32 AM
AVAXUSD,Market,buy,1111.67272813,1111.67272813,21.462973,filled,Jun 03 2025 11:37:30 AM
LINKUSD,Market,buy,1680.1372524,1680.1372524,14.149892,filled,Jun 03 2025 11:37:28 AM
DOTUSD,Market,buy,5685.90418068,5685.90418068,4.223323,filled,Jun 03 2025 11:37:26 AM
ETHUSD,Market,buy,9.05530753,9.05530753,2663.769532,filled,Jun 03 2025 11:37:14 AM
ETHUSD,Market,sell,54.78031337,54.78031337,2611.660445,filled,Jun 03 2025 11:36:31 AM
LINKUSD,Market,sell,1678.31681714,1678.31681714,14.020469,filled,Jun 03 2025 11:36:29 AM
AVAXUSD,Market,sell,1111.20517094,1111.20517094,21.110614,filled,Jun 03 2025 11:36:27 AM
DOTUSD,Market,sell,5684.59259569,5684.59259569,4.103568,filled,Jun 03 2025 11:36:25 AM
UNIUSD,Market,buy,3700.34307116,3700.34307116,6.466061,filled,Jun 03 2025 11:36:22 AM
AVAXUSD,Market,buy,1113.85749718,1113.85749718,21.472206,filled,Jun 03 2025 11:36:20 AM
LINKUSD,Market,buy,1682.52312496,1682.52312496,14.173844,filled,Jun 03 2025 11:36:18 AM
DOTUSD,Market,buy,5695.50192758,5695.50192758,4.226541,filled,Jun 03 2025 11:36:16 AM
ETHUSD,Market,buy,9.06849364,9.06849364,2618.20,filled,Jun 03 2025 11:36:14 AM
AAVEUSD,Market,sell,92.71002558,92.71002558,258.487592,filled,Jun 03 2025 11:35:42 AM
LINKUSD,Market,sell,1686.66573962,1686.66573962,14.015337,filled,Jun 03 2025 11:35:40 AM
SOLUSD,Market,sell,298.41329021,298.41329021,156.043934,filled,Jun 03 2025 11:35:33 AM
AVAXUSD,Market,sell,1115.65734484,1115.65734484,21.087792,filled,Jun 03 2025 11:35:31 AM
DOTUSD,Market,sell,5710.43626802,5710.43626802,4.097048,filled,Jun 03 2025 11:35:29 AM
UNIUSD,Market,buy,3717.71846651,3717.71846651,6.454386,filled,Jun 03 2025 11:35:26 AM
AVAXUSD,Market,buy,1118.32766134,1118.32766134,21.445347,filled,Jun 03 2025 11:35:24 AM
LINKUSD,Market,buy,1690.89297205,1690.89297205,14.146624,filled,Jun 03 2025 11:35:22 AM
DOTUSD,Market,buy,5721.3853871,5721.3853871,4.218142,filled,Jun 03 2025 11:35:20 AM
SOLUSD,Market,buy,149.2976206,149.2976206,159.515476,filled,Jun 03 2025 11:35:18 AM
ETHUSD,Market,buy,9.11188674,9.11188674,2611.564613,filled,Jun 03 2025 11:35:16 AM
LINKUSD,Market,sell,1694.0973039,1694.0973039,13.988727,filled,Jun 03 2025 11:34:33 AM
AVAXUSD,Market,sell,2245.98050611,2245.98050611,20.934048,filled,Jun 03 2025 11:34:31 AM
DOTUSD,Market,sell,11480.93099174,11480.93099174,4.080032,filled,Jun 03 2025 11:34:29 AM
UNIUSD,Market,buy,3734.90745868,3734.90745868,6.451074,filled,Jun 03 2025 11:34:26 AM
AVAXUSD,Market,buy,1123.35898233,1123.35898233,21.422163,filled,Jun 03 2025 11:34:24 AM
LINKUSD,Market,buy,1698.3431618,1698.3431618,14.130068,filled,Jun 03 2025 11:34:22 AM
DOTUSD,Market,buy,5739.66014545,5739.66014545,4.216262,filled,Jun 03 2025 11:34:20 AM
SOLUSD,Market,buy,149.8635726,149.8635726,159.37028,filled,Jun 03 2025 11:34:18 AM
ETHUSD,Market,buy,9.14281446,9.14281446,2610.866402,filled,Jun 03 2025 11:34:16 AM
"""

def parse_trades():
    """Parse the trade data into structured format"""
    trades = []
    lines = trades_data.strip().split('\n')
    
    for line in lines:
        if line.strip():
            parts = line.split(',')
            if len(parts) >= 7:
                trade = {
                    'symbol': parts[0],
                    'side': parts[2],
                    'quantity': Decimal(parts[3]),
                    'price': Decimal(parts[5]),
                    'timestamp': parts[7] if len(parts) > 7 else parts[6]
                }
                trades.append(trade)
    
    return trades

def analyze_trading_pattern():
    """Analyze the rapid-fire trading pattern"""
    print("🚨 RAPID-FIRE TRADING LOSS ANALYSIS")
    print("=" * 60)
    
    trades = parse_trades()
    print(f"📊 Total trades analyzed: {len(trades)}")
    
    # Group by symbol
    symbol_trades = {}
    for trade in trades:
        symbol = trade['symbol']
        if symbol not in symbol_trades:
            symbol_trades[symbol] = []
        symbol_trades[symbol].append(trade)
    
    print(f"📊 Symbols traded: {len(symbol_trades)}")
    
    # Analyze each symbol's P&L
    total_losses = Decimal('0')
    total_volume = Decimal('0')
    
    print("\n💰 SYMBOL-BY-SYMBOL P&L ANALYSIS")
    print("-" * 50)
    
    for symbol in sorted(symbol_trades.keys()):
        symbol_pnl = Decimal('0')
        symbol_volume = Decimal('0')
        buy_total = Decimal('0')
        sell_total = Decimal('0')
        
        for trade in symbol_trades[symbol]:
            trade_value = trade['quantity'] * trade['price']
            symbol_volume += trade_value
            
            if trade['side'] == 'buy':
                buy_total += trade_value
            else:  # sell
                sell_total += trade_value
        
        # Calculate P&L (assuming positions were closed)
        symbol_pnl = sell_total - buy_total
        total_losses += symbol_pnl
        total_volume += symbol_volume
        
        print(f"{symbol:8} | Buy: ${buy_total:>12,.2f} | Sell: ${sell_total:>12,.2f} | P&L: ${symbol_pnl:>+10,.2f}")
    
    print("-" * 50)
    print(f"{'TOTAL':8} | Volume: ${total_volume:>10,.2f} | Net P&L: ${total_losses:>+10,.2f}")
    
    # Calculate percentage loss
    initial_capital = Decimal('1000000')  # $1M starting capital
    loss_percentage = (abs(total_losses) / initial_capital) * 100
    
    print(f"\n🚨 LOSS SUMMARY:")
    print(f"   Total Net Loss: ${total_losses:+,.2f}")
    print(f"   Loss Percentage: {loss_percentage:.2f}%")
    print(f"   Trading Volume: ${total_volume:,.2f}")
    
    # Analyze timing pattern
    print(f"\n⏰ TIMING ANALYSIS:")
    timestamps = [trade['timestamp'] for trade in trades]
    print(f"   Trading Period: {timestamps[-1]} to {timestamps[0]}")
    print(f"   Duration: ~5 minutes")
    print(f"   Trade Frequency: {len(trades)/5:.1f} trades per minute")
    
    return symbol_trades, total_losses

def identify_root_causes():
    """Identify why this happened"""
    print(f"\n🔍 ROOT CAUSE ANALYSIS")
    print("=" * 40)
    
    print("❌ IDENTIFIED ISSUES:")
    print("   1. NO POSITION TRACKING: System buying/selling same symbols repeatedly")
    print("   2. NO COOLDOWN PERIOD: Trades every 2 seconds without pause")
    print("   3. LARGE POSITION SIZES: $23K+ positions on each trade")
    print("   4. BID-ASK SPREAD LOSSES: Market orders losing to spread on each round trip")
    print("   5. NO EXIT STRATEGY: Positions opened and closed within minutes")
    print("   6. OVERCONFIDENT SYSTEM: Making large bets without validation")
    
    print(f"\n🛠️ REQUIRED FIXES:")
    print("   1. POSITION AWARENESS: Check existing positions before new trades")
    print("   2. TRADE COOLDOWN: Minimum 5-10 minute delay between symbol trades")
    print("   3. POSITION SIZE LIMITS: Cap individual trades at $5K-$10K max")
    print("   4. EXIT LOGIC: Define clear profit/loss exit criteria")
    print("   5. CONFIDENCE THRESHOLDS: Require >80% confidence for large trades")
    print("   6. ROUND-TRIP ANALYSIS: Account for bid-ask spread costs")

def analyze_specific_symbol(symbol_trades, symbol):
    """Analyze specific symbol trading pattern"""
    if symbol not in symbol_trades:
        print(f"❌ {symbol} not found in trades")
        return
    
    print(f"\n📊 {symbol} DETAILED ANALYSIS")
    print("-" * 30)
    
    trades = symbol_trades[symbol]
    for i, trade in enumerate(trades):
        trade_value = trade['quantity'] * trade['price']
        print(f"   {i+1}. {trade['side'].upper():4} {trade['quantity']:>12.8f} @ ${trade['price']:>8.2f} = ${trade_value:>12,.2f}")
    
    # Calculate average prices
    buy_trades = [t for t in trades if t['side'] == 'buy']
    sell_trades = [t for t in trades if t['side'] == 'sell']
    
    if buy_trades and sell_trades:
        avg_buy_price = sum(t['price'] * t['quantity'] for t in buy_trades) / sum(t['quantity'] for t in buy_trades)
        avg_sell_price = sum(t['price'] * t['quantity'] for t in sell_trades) / sum(t['quantity'] for t in sell_trades)
        
        print(f"\n   Average Buy Price:  ${avg_buy_price:.6f}")
        print(f"   Average Sell Price: ${avg_sell_price:.6f}")
        print(f"   Price Difference:   ${avg_sell_price - avg_buy_price:+.6f}")
        print(f"   Spread Loss:        {((avg_buy_price - avg_sell_price) / avg_buy_price * 100):+.3f}%")

if __name__ == "__main__":
    symbol_trades, total_losses = analyze_trading_pattern()
    identify_root_causes()
    
    # Analyze AVAX specifically as requested
    analyze_specific_symbol(symbol_trades, 'AVAXUSD')
    
    print(f"\n🚨 CRITICAL RECOMMENDATION:")
    print("   IMMEDIATELY IMPLEMENT POSITION TRACKING AND TRADE COOLDOWNS")
    print("   The system is functioning but needs safety controls to prevent losses.")