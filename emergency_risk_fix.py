#!/usr/bin/env python3
"""
EMERGENCY RISK MANAGEMENT FIX
Restore critical position limits and force diversification
"""

import alpaca_trade_api as tradeapi

print("🚨 EMERGENCY RISK MANAGEMENT FIX")
print("=" * 50)

# Initialize API
api = tradeapi.REST(
    'PKIP9MZ4Q1WJ423JXOQU',
    'zjGO4D9sED7ATSv6J1UCKCl0xzOOep5hPHRRmRcc',
    'https://paper-api.alpaca.markets'
)

# Get current status
account = api.get_account()
positions = api.list_positions()
portfolio_value = float(account.portfolio_value)

print(f"Portfolio Value: ${portfolio_value:,.2f}")
print(f"Current Positions: {len(positions)}")

# Analyze concentration risk
for pos in positions:
    symbol = pos.symbol
    market_value = float(pos.market_value)
    concentration = (market_value / portfolio_value) * 100
    pnl = float(pos.unrealized_pl)
    
    print(f"\n🔍 {symbol}:")
    print(f"  Value: ${market_value:,.2f}")
    print(f"  Concentration: {concentration:.1f}%")
    print(f"  P&L: ${pnl:,.2f}")
    
    # CRITICAL RISK CHECK
    if concentration > 20:
        print(f"  ❌ CRITICAL: {concentration:.1f}% concentration exceeds 20% limit!")
        
        if concentration > 50:
            print(f"  🚨 EMERGENCY: {concentration:.1f}% concentration is EXTREMELY DANGEROUS!")
            
            # Calculate reduction needed
            target_allocation = 0.15  # 15% max
            current_allocation = concentration / 100
            reduction_needed = current_allocation - target_allocation
            reduction_value = portfolio_value * reduction_needed
            
            print(f"  📉 REQUIRED REDUCTION: ${reduction_value:,.2f} ({reduction_needed:.1%})")
            
            # Calculate shares to sell
            current_price = market_value / abs(float(pos.qty))
            shares_to_sell = int(reduction_value / current_price)
            
            print(f"  📊 SUGGESTED ACTION: Sell {shares_to_sell} shares to reduce to 15%")

print(f"\n💡 CRITICAL FIXES NEEDED:")
print(f"  1. Restore position size limits (15% max per symbol)")
print(f"  2. Force diversification (minimum 5 positions)")
print(f"  3. Fix crypto execution (why only UNIUSD?)")
print(f"  4. Enable stock trading (fix data access)")
print(f"  5. Lower confidence thresholds for more opportunities")

print(f"\n🎯 TARGET PORTFOLIO:")
print(f"  - Maximum 15% per position")
print(f"  - Minimum 5-10 positions")
print(f"  - Mix of stocks, crypto, ETFs")
print(f"  - No single asset >20% of portfolio")

# Check what symbols SHOULD be trading
expected_cryptos = ['BTCUSD', 'ETHUSD', 'SOLUSD', 'DOTUSD', 'LINKUSD']
expected_stocks = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA']

print(f"\n📋 EXPECTED DIVERSIFICATION:")
print(f"  Crypto symbols: {expected_cryptos}")
print(f"  Stock symbols: {expected_stocks}")
print(f"  Current symbols: {[pos.symbol for pos in positions]}")
print(f"  Missing diversity: {len(expected_cryptos) + len(expected_stocks) - len(positions)} positions")