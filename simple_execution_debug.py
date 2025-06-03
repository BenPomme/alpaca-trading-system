#!/usr/bin/env python3
"""
SIMPLE EXECUTION DEBUG - Why only UNIUSD trades?
"""

import alpaca_trade_api as tradeapi

print("🚨 EXECUTION FAILURE ANALYSIS")
print("=" * 40)

# Quick test of current system
api = tradeapi.REST(
    'PKIP9MZ4Q1WJ423JXOQU',
    'zjGO4D9sED7ATSv6J1UCKCl0xzOOep5hPHRRmRcc',
    'https://paper-api.alpaca.markets'
)

# Check positions
positions = api.list_positions()
print(f"Current Positions: {len(positions)}")
for pos in positions:
    value = float(pos.market_value)
    print(f"  {pos.symbol}: ${value:,.2f}")

# Check recent orders (last 20)
orders = api.list_orders(limit=20, status='all')
recent_symbols = set()
for order in orders:
    recent_symbols.add(order.symbol)

print(f"\nRecent Trading Symbols: {list(recent_symbols)}")
print(f"Total symbols traded recently: {len(recent_symbols)}")

# Check what symbols should be available
expected_crypto = ['BTCUSD', 'ETHUSD', 'SOLUSD', 'DOTUSD', 'LINKUSD', 'UNIUSD', 'AAVEUSD', 'AVAXUSD']
expected_stocks = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']

print(f"\nExpected crypto symbols: {len(expected_crypto)}")
print(f"Expected stock symbols: {len(expected_stocks)}")

# Quick test - try to get prices for some symbols
print(f"\n🔍 PRICE TEST:")
test_symbols = ['SPY', 'AAPL', 'BTCUSD', 'ETHUSD', 'UNIUSD']
for symbol in test_symbols:
    try:
        if 'USD' in symbol:
            # Crypto
            bars = api.get_crypto_bars(symbol, start='2025-06-03', end='2025-06-03', timeframe='1Hour').df
            if not bars.empty:
                price = bars['close'].iloc[-1]
                print(f"  {symbol}: ${price:.2f} (crypto)")
            else:
                print(f"  {symbol}: No data (crypto)")
        else:
            # Stock
            bars = api.get_bars(symbol, start='2025-06-03', end='2025-06-03', timeframe='1Hour').df
            if not bars.empty:
                price = bars['close'].iloc[-1]
                print(f"  {symbol}: ${price:.2f} (stock)")
            else:
                print(f"  {symbol}: No data (stock)")
    except Exception as e:
        print(f"  {symbol}: ERROR - {e}")

print(f"\n💡 HYPOTHESIS:")
print(f"  1. Crypto module finds opportunities but execution fails for all except UNIUSD")
print(f"  2. Stocks module finds NO opportunities (confidence too high?)")
print(f"  3. Risk management blocking trades")
print(f"  4. Order execution logic has bugs")

# Check account buying power
account = api.get_account()
print(f"\n💰 ACCOUNT STATUS:")
print(f"  Buying Power: ${float(account.buying_power):,.2f}")
print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
print(f"  Day Trading Power: ${float(account.daytrading_buying_power):,.2f}")

if len(recent_symbols) == 1:
    print(f"\n❌ CONFIRMED PROBLEM: Only trading {list(recent_symbols)[0]}")
else:
    print(f"\n✅ Multiple symbols being traded: {recent_symbols}")