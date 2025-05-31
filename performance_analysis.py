#!/usr/bin/env python3
"""
Critical Performance Analysis
"""

# Current portfolio data from live system
portfolio_data = {
    'total_value': 98259.16,
    'positions': 60,
    'position_details': [
        ('AAPL', -38.36), ('AAVEUSD', -238.47), ('ABNB', -3.50), ('ADI', -11.36),
        ('AMAT', -42.70), ('AMD', -24.96), ('AMGN', -0.21), ('AMZN', -15.85),
        ('AVGO', -3.24), ('BIIB', -2.60), ('BTCUSD', -191.61), ('CMCSA', -3.78),
        ('COST', 28.56), ('CRM', -5.57), ('CSCO', -5.70), ('DIA', -0.54),
        ('DIS', 8.48), ('DOCU', 11.77), ('EBAY', 3.96), ('EFA', -1.81),
        ('ETHUSD', -263.66), ('FTNT', -5.94), ('GILD', 12.56), ('GOOG', -14.70),
        ('GOOGL', -20.85), ('IEFA', -1.92), ('INTC', -47.76), ('INTU', -2.33),
        ('IWM', -11.31), ('JNJ', 20.22), ('JPM', -0.15), ('KLAC', -24.52),
        ('LRCX', 0.60), ('META', -4.22), ('MRNA', 7.60), ('MRVL', -10.16),
        ('MSFT', -9.96), ('NVDA', -47.83), ('ORCL', -8.07), ('PANW', 3.01),
        ('PFE', 5.25), ('PYPL', -13.16), ('QCOM', -12.33), ('QQQ', -17.29),
        ('REGN', -13.46), ('SBUX', -8.03), ('SNPS', 13.04), ('SOLUSD', -477.09),
        ('SPY', -5.14), ('T', 9.17), ('TSLA', -24.52), ('TXN', -17.53),
        ('VEA', -3.72), ('VTI', -8.82), ('VZ', 20.47), ('WDAY', 22.25),
        ('XLF', 1.61), ('XLK', 31.61), ('XLV', 62.51), ('ZM', 2.85)
    ]
}

def analyze_performance():
    print("📊 CRITICAL PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    total_unrealized_pl = sum([pl for _, pl in portfolio_data['position_details']])
    
    print(f"💰 Portfolio Value: ${portfolio_data['total_value']:,.2f}")
    print(f"📊 Total Positions: {portfolio_data['positions']}")
    print(f"📈 Total Unrealized P&L: ${total_unrealized_pl:.2f}")
    
    # Calculate win rate
    winning_positions = [pl for _, pl in portfolio_data['position_details'] if pl > 0]
    losing_positions = [pl for _, pl in portfolio_data['position_details'] if pl < 0]
    
    win_rate = (len(winning_positions) / portfolio_data['positions']) * 100
    print(f"🎯 Win Rate: {win_rate:.1f}% ({len(winning_positions)} wins, {len(losing_positions)} losses)")
    
    if winning_positions:
        avg_win = sum(winning_positions) / len(winning_positions)
        print(f"📈 Average Winning Trade: ${avg_win:.2f}")
    
    if losing_positions:
        avg_loss = sum(losing_positions) / len(losing_positions)
        print(f"📉 Average Losing Trade: ${avg_loss:.2f}")
    
    # Identify biggest losers and winners
    sorted_positions = sorted(portfolio_data['position_details'], key=lambda x: x[1])
    
    print(f"\n🚨 BIGGEST LOSERS:")
    for symbol, loss in sorted_positions[:6]:
        print(f"   {symbol}: ${loss:.2f}")
    
    print(f"\n🚀 BIGGEST WINNERS:")
    for symbol, win in sorted_positions[-6:]:
        print(f"   {symbol}: ${win:.2f}")
    
    # Overall performance analysis
    starting_value = 100000  # Assuming $100k start
    total_return = ((portfolio_data['total_value'] - starting_value) / starting_value) * 100
    
    print(f"\n📊 OVERALL PERFORMANCE:")
    print(f"   Starting Value: ${starting_value:,}")
    print(f"   Current Value: ${portfolio_data['total_value']:,.2f}")
    print(f"   Total Return: {total_return:.2f}%")
    
    # Critical issues analysis
    print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
    
    # Crypto losses
    crypto_losses = sum([pl for symbol, pl in portfolio_data['position_details'] 
                        if 'USD' in symbol and pl < 0])
    print(f"   1. Massive crypto losses: ${crypto_losses:.2f}")
    
    # Tech stock performance
    tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'META', 'NVDA', 'AMD', 'INTC']
    tech_pl = sum([pl for symbol, pl in portfolio_data['position_details'] 
                  if symbol in tech_stocks])
    print(f"   2. Tech stock total P&L: ${tech_pl:.2f}")
    
    print(f"   3. Portfolio down {abs(total_return):.1f}% overall")
    print(f"   4. Win rate {win_rate:.1f}% - FAR BELOW target 45-60%")
    
    # Strategy analysis
    print(f"\n📋 STRATEGY EFFECTIVENESS ANALYSIS:")
    
    # Sector allocation issues
    print(f"   - Over-diversification: 60 positions is excessive")
    print(f"   - Crypto allocation: High risk, massive losses")
    print(f"   - Position sizing: Too many small positions")
    print(f"   - Exit strategy: No profit taking visible")
    
    print(f"\n💡 IMMEDIATE RECOMMENDATIONS:")
    print(f"   1. URGENT: Implement stop losses on crypto positions")
    print(f"   2. Reduce position count from 60 to <30")
    print(f"   3. Take profits on winning positions (XLV, XLK, COST)")
    print(f"   4. Review and fix exit strategy logic")
    print(f"   5. Disable or limit crypto trading until losses controlled")

if __name__ == "__main__":
    analyze_performance()