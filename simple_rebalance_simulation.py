#!/usr/bin/env python3
"""
Simple Rebalance Simulation
Show what needs to be done to fix allocation without errors
"""

import os
import alpaca_trade_api as tradeapi
import json
from datetime import datetime

# Set environment variables
os.environ['ALPACA_PAPER_API_KEY'] = "PKOBXG3RWCRQTXH6ID0L"
os.environ['ALPACA_PAPER_SECRET_KEY'] = "8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn"
os.environ['ALPACA_BASE_URL'] = "https://paper-api.alpaca.markets"

def analyze_and_recommend():
    """Analyze current state and provide recommendations"""
    print("🚨 PORTFOLIO REBALANCING ANALYSIS")
    print("=" * 50)
    
    try:
        api = tradeapi.REST(
            os.environ['ALPACA_PAPER_API_KEY'],
            os.environ['ALPACA_PAPER_SECRET_KEY'],
            os.environ['ALPACA_BASE_URL'],
            api_version='v2'
        )
        
        # Get account and positions
        account = api.get_account()
        positions = api.list_positions()
        
        portfolio_value = float(account.portfolio_value)
        cash = float(account.cash)
        buying_power = float(account.buying_power)
        
        print(f"💰 Portfolio Value: ${portfolio_value:,.2f}")
        print(f"💵 Cash: ${cash:,.2f}")
        print(f"🏦 Buying Power: ${buying_power:,.2f}")
        print(f"📊 Total Positions: {len(positions)}")
        
        # Analyze positions
        crypto_positions = []
        stock_positions = []
        crypto_value = 0
        stock_value = 0
        bleeding_positions = []
        
        for pos in positions:
            market_value = float(pos.market_value)
            unrealized_pl = float(pos.unrealized_pl)
            unrealized_plpc = float(pos.unrealized_plpc)
            
            position_data = {
                'symbol': pos.symbol,
                'qty': float(pos.qty),
                'market_value': market_value,
                'unrealized_pl': unrealized_pl,
                'unrealized_plpc': unrealized_plpc
            }
            
            # Categorize by asset type
            if 'USD' in pos.symbol and len(pos.symbol) <= 7:  # Crypto
                crypto_value += market_value
                crypto_positions.append(position_data)
            else:  # Stocks
                stock_value += market_value
                stock_positions.append(position_data)
            
            # Track bleeding positions
            if unrealized_plpc < -0.10:  # 10%+ loss
                bleeding_positions.append(position_data)
        
        # Calculate allocations
        crypto_pct = (crypto_value / portfolio_value) * 100 if portfolio_value > 0 else 0
        stock_pct = (stock_value / portfolio_value) * 100 if portfolio_value > 0 else 0
        
        print(f"\n📊 CURRENT ALLOCATION:")
        print(f"  ₿ Crypto: ${crypto_value:,.2f} ({crypto_pct:.1f}%)")
        print(f"  📈 Stocks: ${stock_value:,.2f} ({stock_pct:.1f}%)")
        print(f"  💵 Cash: ${cash:,.2f}")
        
        print(f"\n🎯 RESEARCH-BASED TARGET ALLOCATION:")
        print(f"  ₿ Crypto: 30.0% (${portfolio_value * 0.30:,.2f})")
        print(f"  📈 Stocks: 50.0% (${portfolio_value * 0.50:,.2f})")
        print(f"  💵 Cash: 20.0% (${portfolio_value * 0.20:,.2f})")
        
        # Calculate what needs to change
        target_crypto_value = portfolio_value * 0.30
        target_stock_value = portfolio_value * 0.50
        
        crypto_excess = crypto_value - target_crypto_value
        stock_deficit = target_stock_value - stock_value
        
        print(f"\n🔧 REBALANCING NEEDED:")
        if crypto_excess > 1000:
            print(f"  ₿ REDUCE Crypto by: ${crypto_excess:,.2f} ({crypto_pct - 30:.1f}%)")
        if stock_deficit > 1000:
            print(f"  📈 INCREASE Stocks by: ${stock_deficit:,.2f}")
        
        # Show worst performing positions
        if bleeding_positions:
            print(f"\n🩸 BLEEDING POSITIONS (consider stop losses):")
            for pos in bleeding_positions:
                print(f"  {pos['symbol']}: ${pos['unrealized_pl']:+.2f} ({pos['unrealized_plpc']*100:+.1f}%)")
        
        # Show crypto positions to potentially reduce
        if crypto_excess > 1000:
            print(f"\n₿ CRYPTO POSITIONS TO REDUCE:")
            crypto_sorted = sorted(crypto_positions, key=lambda x: x['unrealized_plpc'])
            for pos in crypto_sorted:
                print(f"  {pos['symbol']}: ${pos['market_value']:,.2f} (${pos['unrealized_pl']:+.2f})")
        
        # Recommendations
        print(f"\n💡 IMMEDIATE RECOMMENDATIONS:")
        
        if crypto_pct > 60:
            print(f"  🚨 CRITICAL: Reduce crypto allocation from {crypto_pct:.1f}% to 30%")
            print(f"    - Sell ${crypto_excess:,.2f} worth of crypto positions")
            print(f"    - Start with worst performers or break-even positions")
        
        if len(bleeding_positions) > 0:
            total_bleeding = sum(p['unrealized_pl'] for p in bleeding_positions)
            print(f"  🛑 URGENT: Implement stop losses on bleeding positions")
            print(f"    - Total bleeding: ${total_bleeding:+.2f}")
            print(f"    - Consider 15% stop loss rule going forward")
        
        if stock_deficit > 1000:
            print(f"  📈 OPPORTUNITY: Increase stock allocation")
            print(f"    - Buy ${stock_deficit:,.2f} worth of quality stocks")
            print(f"    - Consider: SPY, QQQ, AAPL, MSFT, GOOGL")
        
        print(f"\n🎯 EXPECTED BENEFITS OF REBALANCING:")
        print(f"  • Reduced risk through proper diversification")
        print(f"  • Better alignment with research-based best practices")
        print(f"  • Improved potential for 5% monthly returns")
        print(f"  • Protection against crypto volatility")
        
        # Save analysis
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_value': portfolio_value,
            'current_allocations': {
                'crypto_pct': crypto_pct,
                'stock_pct': stock_pct,
                'crypto_value': crypto_value,
                'stock_value': stock_value
            },
            'target_allocations': {
                'crypto_pct': 30.0,
                'stock_pct': 50.0,
                'cash_pct': 20.0
            },
            'rebalancing_needed': {
                'crypto_excess': crypto_excess,
                'stock_deficit': stock_deficit
            },
            'bleeding_positions_count': len(bleeding_positions),
            'total_bleeding_pnl': sum(p['unrealized_pl'] for p in bleeding_positions),
            'recommendations': [
                f"Reduce crypto from {crypto_pct:.1f}% to 30%",
                f"Increase stocks from {stock_pct:.1f}% to 50%",
                f"Implement stop losses on {len(bleeding_positions)} bleeding positions"
            ]
        }
        
        with open('rebalancing_analysis.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n📁 Analysis saved to: rebalancing_analysis.json")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return None

def main():
    analysis = analyze_and_recommend()
    
    if analysis:
        print(f"\n✅ REBALANCING ANALYSIS COMPLETE!")
        print(f"🔄 To implement these changes:")
        print(f"   1. Use the emergency rebalancer script")
        print(f"   2. Gradually sell crypto positions")
        print(f"   3. Buy quality stocks with proceeds")
        print(f"   4. Set stop losses on all new positions")

if __name__ == "__main__":
    main()