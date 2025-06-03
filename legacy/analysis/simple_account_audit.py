#!/usr/bin/env python3
"""
Simple account audit - get basic data without causing attribute errors
"""

import os
import alpaca_trade_api as tradeapi
import json
from datetime import datetime, timedelta

# Set environment variables
os.environ['ALPACA_PAPER_API_KEY'] = "PKOBXG3RWCRQTXH6ID0L"
os.environ['ALPACA_PAPER_SECRET_KEY'] = "8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn"
os.environ['ALPACA_BASE_URL'] = "https://paper-api.alpaca.markets"

def get_account_info():
    """Get account information safely"""
    try:
        api = tradeapi.REST(
            os.environ['ALPACA_PAPER_API_KEY'],
            os.environ['ALPACA_PAPER_SECRET_KEY'],
            os.environ['ALPACA_BASE_URL'],
            api_version='v2'
        )
        
        account = api.get_account()
        
        # Print all available attributes to see what's available
        print("🔍 ACCOUNT ATTRIBUTES:")
        account_dict = account._raw
        for key, value in account_dict.items():
            print(f"  {key}: {value}")
        
        print(f"\n💰 ACCOUNT SUMMARY:")
        print(f"  Account ID: {account.id}")
        print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"  Cash: ${float(account.cash):,.2f}")
        print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        print(f"  Day Trading Buying Power: ${float(account.daytrading_buying_power):,.2f}")
        print(f"  Equity: ${float(account.equity):,.2f}")
        
        # Check for P&L fields
        if hasattr(account, 'unrealized_pl'):
            print(f"  Unrealized P&L: ${float(account.unrealized_pl):,.2f}")
        elif hasattr(account, 'unrealized_plpc'):
            print(f"  Unrealized P&L %: {float(account.unrealized_plpc)*100:.2f}%")
        
        return account
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_positions():
    """Get positions safely"""
    try:
        api = tradeapi.REST(
            os.environ['ALPACA_PAPER_API_KEY'],
            os.environ['ALPACA_PAPER_SECRET_KEY'],
            os.environ['ALPACA_BASE_URL'],
            api_version='v2'
        )
        
        positions = api.list_positions()
        print(f"\n📊 POSITIONS ({len(positions)} total):")
        
        crypto_value = 0
        stock_value = 0
        total_unrealized_pl = 0
        
        for pos in positions:
            market_value = float(pos.market_value)
            unrealized_pl = float(pos.unrealized_pl)
            unrealized_plpc = float(pos.unrealized_plpc) * 100
            
            total_unrealized_pl += unrealized_pl
            
            # Categorize
            if 'USD' in pos.symbol and len(pos.symbol) <= 7:
                crypto_value += market_value
                category = "₿"
            else:
                stock_value += market_value  
                category = "📈"
            
            print(f"  {category} {pos.symbol}: {pos.qty} @ ${float(pos.avg_entry_price):.2f} → "
                  f"${float(pos.current_price):.2f} = ${market_value:,.2f} "
                  f"(${unrealized_pl:+.2f}, {unrealized_plpc:+.1f}%)")
        
        portfolio_value = float(positions[0].account.portfolio_value) if positions else 0
        
        print(f"\n📊 ALLOCATION:")
        if portfolio_value > 0:
            crypto_pct = (crypto_value / portfolio_value) * 100
            stock_pct = (stock_value / portfolio_value) * 100
            print(f"  ₿ Crypto: ${crypto_value:,.2f} ({crypto_pct:.1f}%)")
            print(f"  📈 Stocks: ${stock_value:,.2f} ({stock_pct:.1f}%)")
        print(f"  💸 Total Unrealized P&L: ${total_unrealized_pl:+,.2f}")
        
        return positions, crypto_value, stock_value, total_unrealized_pl
        
    except Exception as e:
        print(f"❌ Error getting positions: {e}")
        return None, 0, 0, 0

def get_recent_orders():
    """Get recent orders"""
    try:
        api = tradeapi.REST(
            os.environ['ALPACA_PAPER_API_KEY'],
            os.environ['ALPACA_PAPER_SECRET_KEY'],
            os.environ['ALPACA_BASE_URL'],
            api_version='v2'
        )
        
        # Get orders from last week
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        orders = api.list_orders(
            status='all',
            after=start_date.isoformat(),
            limit=100
        )
        
        filled_orders = [o for o in orders if o.status == 'filled']
        pending_orders = [o for o in orders if o.status in ['new', 'partially_filled', 'pending_new']]
        rejected_orders = [o for o in orders if o.status in ['rejected', 'cancelled']]
        
        print(f"\n📋 RECENT ORDERS (last 7 days):")
        print(f"  ✅ Filled: {len(filled_orders)}")
        print(f"  ⏳ Pending: {len(pending_orders)}")
        print(f"  ❌ Rejected/Cancelled: {len(rejected_orders)}")
        
        print(f"\n📈 LAST 10 FILLED ORDERS:")
        for order in filled_orders[:10]:
            filled_price = float(order.filled_avg_price) if order.filled_avg_price else 0
            print(f"  {order.submitted_at[:16]} {order.side.upper()} {order.qty} {order.symbol} @ ${filled_price:.2f}")
        
        return len(filled_orders), len(pending_orders), len(rejected_orders)
        
    except Exception as e:
        print(f"❌ Error getting orders: {e}")
        return 0, 0, 0

def main():
    print("🚨 SIMPLE ACCOUNT AUDIT")
    print("=" * 50)
    
    account = get_account_info()
    positions, crypto_value, stock_value, total_unrealized_pl = get_positions()
    filled_count, pending_count, rejected_count = get_recent_orders()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CRITICAL ISSUES CHECK:")
    
    if account:
        portfolio_value = float(account.portfolio_value)
        crypto_pct = (crypto_value / portfolio_value) * 100 if portfolio_value > 0 else 0
        
        issues = []
        if crypto_pct > 60:
            issues.append(f"🚨 CRYPTO OVER-ALLOCATION: {crypto_pct:.1f}% (should be <60%)")
        if total_unrealized_pl < -1000:
            issues.append(f"🚨 MAJOR LOSSES: ${total_unrealized_pl:+,.2f}")
        if len(positions) > 30:
            issues.append(f"🚨 TOO MANY POSITIONS: {len(positions)} (should be <30)")
        if filled_count == 0:
            issues.append(f"🚨 NO TRADING ACTIVITY: 0 filled orders in 7 days")
        
        if issues:
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  ✅ No critical issues detected")
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'portfolio_value': float(account.portfolio_value) if account else 0,
        'crypto_allocation_pct': (crypto_value / float(account.portfolio_value)) * 100 if account and float(account.portfolio_value) > 0 else 0,
        'total_positions': len(positions) if positions else 0,
        'total_unrealized_pl': total_unrealized_pl,
        'recent_orders': {
            'filled': filled_count,
            'pending': pending_count,
            'rejected': rejected_count
        }
    }
    
    with open('account_audit_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to: account_audit_results.json")

if __name__ == "__main__":
    main()