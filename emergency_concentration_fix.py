#!/usr/bin/env python3
"""
EMERGENCY CONCENTRATION FIX
Force diversification by reducing concentrated positions
"""

import alpaca_trade_api as tradeapi
from datetime import datetime

print("🚨 EMERGENCY CONCENTRATION LIQUIDATION")
print("=" * 50)

# Initialize API
api = tradeapi.REST(
    'PKIP9MZ4Q1WJ423JXOQU',
    'zjGO4D9sED7ATSv6J1UCKCl0xzOOep5hPHRRmRcc',
    'https://paper-api.alpaca.markets'
)

def check_concentration_risk():
    """Check and fix concentration risk"""
    account = api.get_account()
    positions = api.list_positions()
    portfolio_value = float(account.portfolio_value)
    
    print(f"Portfolio Value: ${portfolio_value:,.2f}")
    print(f"Current Positions: {len(positions)}")
    
    concentration_violations = []
    
    for pos in positions:
        symbol = pos.symbol
        market_value = float(pos.market_value)
        concentration = (market_value / portfolio_value) * 100
        qty = float(pos.qty)
        pnl = float(pos.unrealized_pl)
        
        print(f"\n📊 {symbol}:")
        print(f"  Value: ${market_value:,.2f}")
        print(f"  Concentration: {concentration:.1f}%")
        print(f"  Quantity: {qty:,.0f}")
        print(f"  P&L: ${pnl:,.2f}")
        
        # Check concentration limits
        MAX_CONCENTRATION = 15.0  # 15% max per position
        
        if concentration > MAX_CONCENTRATION:
            violation = {
                'symbol': symbol,
                'current_concentration': concentration,
                'current_value': market_value,
                'target_concentration': MAX_CONCENTRATION,
                'qty': qty,
                'pnl': pnl
            }
            
            # Calculate reduction needed
            target_value = portfolio_value * (MAX_CONCENTRATION / 100)
            reduction_needed = market_value - target_value
            reduction_pct = (reduction_needed / market_value) * 100
            
            # Calculate shares to sell
            if qty > 0:
                avg_price = market_value / qty
                shares_to_sell = int(reduction_needed / avg_price)
                
                violation.update({
                    'target_value': target_value,
                    'reduction_needed': reduction_needed,
                    'reduction_pct': reduction_pct,
                    'shares_to_sell': shares_to_sell,
                    'avg_price': avg_price
                })
                
                concentration_violations.append(violation)
                
                print(f"  ❌ VIOLATION: {concentration:.1f}% > {MAX_CONCENTRATION:.1f}% limit")
                print(f"  📉 MUST REDUCE: ${reduction_needed:,.2f} ({reduction_pct:.1f}%)")
                print(f"  🔥 SELL ORDER: {shares_to_sell:,} shares @ ~${avg_price:.4f}")
    
    return concentration_violations

def execute_emergency_rebalancing(violations, dry_run=True):
    """Execute emergency rebalancing orders"""
    print(f"\n🚨 EMERGENCY REBALANCING {'(DRY RUN)' if dry_run else '(LIVE EXECUTION)'}")
    print("=" * 50)
    
    for violation in violations:
        symbol = violation['symbol']
        shares_to_sell = violation['shares_to_sell']
        current_concentration = violation['current_concentration']
        target_concentration = violation['target_concentration']
        
        print(f"\n🎯 {symbol} REBALANCING:")
        print(f"  Current: {current_concentration:.1f}% → Target: {target_concentration:.1f}%")
        print(f"  Action: SELL {shares_to_sell:,} shares")
        
        if not dry_run:
            try:
                # Execute sell order
                order = api.submit_order(
                    symbol=symbol,
                    qty=shares_to_sell,
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
                print(f"  ✅ ORDER SUBMITTED: {order.id}")
                print(f"  📋 Status: {order.status}")
            except Exception as e:
                print(f"  ❌ ORDER FAILED: {e}")
        else:
            print(f"  📝 DRY RUN: Would sell {shares_to_sell:,} shares")

def main():
    """Main emergency fix function"""
    print(f"⏰ Emergency Fix Time: {datetime.now()}")
    
    # Check current concentration
    violations = check_concentration_risk()
    
    if not violations:
        print(f"\n✅ NO CONCENTRATION VIOLATIONS FOUND")
        return
    
    print(f"\n🚨 FOUND {len(violations)} CONCENTRATION VIOLATIONS")
    
    # Ask for confirmation
    response = input(f"\n❓ Execute emergency rebalancing? (y/n): ").lower().strip()
    
    if response == 'y':
        # First show dry run
        execute_emergency_rebalancing(violations, dry_run=True)
        
        # Confirm live execution
        confirm = input(f"\n❓ Confirm LIVE execution? (yes/no): ").lower().strip()
        
        if confirm == 'yes':
            execute_emergency_rebalancing(violations, dry_run=False)
            print(f"\n🎉 EMERGENCY REBALANCING COMPLETED")
        else:
            print(f"\n❌ Live execution cancelled")
    else:
        print(f"\n❌ Emergency rebalancing cancelled")

if __name__ == "__main__":
    main()