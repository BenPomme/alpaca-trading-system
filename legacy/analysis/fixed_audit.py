#!/usr/bin/env python3
"""
Fixed audit script - work around API issues
"""

import os
import alpaca_trade_api as tradeapi
import json
from datetime import datetime, timedelta

# Set environment variables
os.environ['ALPACA_PAPER_API_KEY'] = "PKOBXG3RWCRQTXH6ID0L"
os.environ['ALPACA_PAPER_SECRET_KEY'] = "8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn"
os.environ['ALPACA_BASE_URL'] = "https://paper-api.alpaca.markets"

def main():
    print("🚨 FIXED TRADING SYSTEM AUDIT")
    print("=" * 50)
    
    try:
        api = tradeapi.REST(
            os.environ['ALPACA_PAPER_API_KEY'],
            os.environ['ALPACA_PAPER_SECRET_KEY'],
            os.environ['ALPACA_BASE_URL'],
            api_version='v2'
        )
        
        # Get account
        account = api.get_account()
        portfolio_value = float(account.portfolio_value)
        cash = float(account.cash)
        buying_power = float(account.buying_power)
        
        print(f"✅ CONNECTED TO ACCOUNT: {account.id}")
        print(f"💰 Portfolio Value: ${portfolio_value:,.2f}")
        print(f"💵 Cash: ${cash:,.2f}")  
        print(f"🏦 Buying Power: ${buying_power:,.2f}")
        
        # Get positions manually
        positions = api.list_positions()
        print(f"\n📊 POSITIONS ({len(positions)} total):")
        
        crypto_value = 0
        stock_value = 0
        total_unrealized_pl = 0
        position_details = []
        
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
            
            position_details.append({
                'symbol': pos.symbol,
                'category': category,
                'qty': float(pos.qty),
                'avg_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price),
                'market_value': market_value,
                'unrealized_pl': unrealized_pl,
                'unrealized_plpc': unrealized_plpc
            })
            
            print(f"  {category} {pos.symbol}: {pos.qty} @ ${float(pos.avg_entry_price):.2f} → "
                  f"${float(pos.current_price):.2f} = ${market_value:,.2f} "
                  f"(${unrealized_pl:+.2f}, {unrealized_plpc:+.1f}%)")
        
        # Calculate allocations
        crypto_pct = (crypto_value / portfolio_value) * 100 if portfolio_value > 0 else 0
        stock_pct = (stock_value / portfolio_value) * 100 if portfolio_value > 0 else 0
        cash_pct = (cash / portfolio_value) * 100 if portfolio_value > 0 else 0
        
        print(f"\n📊 ALLOCATION ANALYSIS:")
        print(f"  ₿ Crypto: ${crypto_value:,.2f} ({crypto_pct:.1f}%)")
        print(f"  📈 Stocks: ${stock_value:,.2f} ({stock_pct:.1f}%)")
        print(f"  💵 Cash: ${cash:,.2f} ({cash_pct:.1f}%)")
        print(f"  💸 Total Unrealized P&L: ${total_unrealized_pl:+,.2f}")
        
        # Get recent orders (with fixed date format)
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            orders = api.list_orders(
                status='all',
                after=start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                limit=100
            )
            
            filled_orders = [o for o in orders if o.status == 'filled']
            pending_orders = [o for o in orders if o.status in ['new', 'partially_filled', 'pending_new']]
            rejected_orders = [o for o in orders if o.status in ['rejected', 'cancelled']]
            
            print(f"\n📋 RECENT ORDERS (last 7 days):")
            print(f"  ✅ Filled: {len(filled_orders)}")
            print(f"  ⏳ Pending: {len(pending_orders)}")
            print(f"  ❌ Rejected/Cancelled: {len(rejected_orders)}")
            
            if filled_orders:
                print(f"\n📈 RECENT FILLED ORDERS:")
                for order in filled_orders[:10]:
                    filled_price = float(order.filled_avg_price) if order.filled_avg_price else 0
                    print(f"  {order.submitted_at[:16]} {order.side.upper()} {order.qty} {order.symbol} @ ${filled_price:.2f}")
            
        except Exception as e:
            print(f"❌ Error getting orders: {e}")
            filled_orders, pending_orders, rejected_orders = [], [], []
        
        # CRITICAL ANALYSIS
        print("\n" + "=" * 50)
        print("🚨 CRITICAL ISSUES ANALYSIS:")
        
        issues = []
        warnings = []
        
        # Check crypto allocation (should be <60% ideally)
        if crypto_pct > 80:
            issues.append(f"🔴 EXTREME CRYPTO OVER-ALLOCATION: {crypto_pct:.1f}% (DANGER ZONE)")
        elif crypto_pct > 60:
            warnings.append(f"🟡 HIGH CRYPTO ALLOCATION: {crypto_pct:.1f}% (monitor closely)")
        
        # Check total losses
        if total_unrealized_pl < -2000:
            issues.append(f"🔴 MAJOR PORTFOLIO LOSSES: ${total_unrealized_pl:+,.2f}")
        elif total_unrealized_pl < -1000:
            warnings.append(f"🟡 SIGNIFICANT LOSSES: ${total_unrealized_pl:+,.2f}")
        
        # Check position count
        if len(positions) > 30:
            issues.append(f"🔴 TOO MANY POSITIONS: {len(positions)} (should be <30)")
        elif len(positions) > 20:
            warnings.append(f"🟡 HIGH POSITION COUNT: {len(positions)} (consider reducing)")
        
        # Check trading activity
        if len(filled_orders) == 0:
            issues.append(f"🔴 NO TRADING ACTIVITY: 0 filled orders in 7 days")
        elif len(filled_orders) < 5:
            warnings.append(f"🟡 LOW TRADING ACTIVITY: {len(filled_orders)} orders in 7 days")
        
        # Check portfolio decline
        original_value = 100000  # Assumed starting value
        decline_pct = ((portfolio_value - original_value) / original_value) * 100
        if decline_pct < -5:
            issues.append(f"🔴 MAJOR PORTFOLIO DECLINE: {decline_pct:.1f}% from start")
        elif decline_pct < -2:
            warnings.append(f"🟡 PORTFOLIO DECLINE: {decline_pct:.1f}% from start")
        
        # Print issues
        if issues:
            print("\n🚨 CRITICAL ISSUES (IMMEDIATE ACTION REQUIRED):")
            for issue in issues:
                print(f"  {issue}")
        
        if warnings:
            print("\n⚠️ WARNINGS (MONITOR CLOSELY):")
            for warning in warnings:
                print(f"  {warning}")
        
        if not issues and not warnings:
            print("  ✅ No critical issues detected")
        
        # Specific position analysis
        print(f"\n📊 WORST PERFORMING POSITIONS:")
        worst_positions = sorted(position_details, key=lambda x: x['unrealized_pl'])[:5]
        for pos in worst_positions:
            if pos['unrealized_pl'] < 0:
                print(f"  {pos['category']} {pos['symbol']}: ${pos['unrealized_pl']:+.2f} ({pos['unrealized_plpc']:+.1f}%)")
        
        print(f"\n📊 BEST PERFORMING POSITIONS:")
        best_positions = sorted(position_details, key=lambda x: x['unrealized_pl'], reverse=True)[:5]
        for pos in best_positions:
            if pos['unrealized_pl'] > 0:
                print(f"  {pos['category']} {pos['symbol']}: ${pos['unrealized_pl']:+.2f} ({pos['unrealized_plpc']:+.1f}%)")
        
        # Generate summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_value': portfolio_value,
            'total_unrealized_pl': total_unrealized_pl,
            'crypto_allocation_pct': crypto_pct,
            'stock_allocation_pct': stock_pct,
            'cash_pct': cash_pct,
            'position_count': len(positions),
            'recent_filled_orders': len(filled_orders),
            'critical_issues_count': len(issues),
            'warnings_count': len(warnings),
            'worst_position_loss': min([p['unrealized_pl'] for p in position_details]),
            'best_position_gain': max([p['unrealized_pl'] for p in position_details]),
            'portfolio_decline_pct': decline_pct,
            'position_details': position_details,
            'issues': issues,
            'warnings': warnings
        }
        
        # Save results
        with open('complete_audit_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📁 Complete audit saved to: complete_audit_results.json")
        
        # Recommendations
        print(f"\n💡 IMMEDIATE RECOMMENDATIONS:")
        if crypto_pct > 70:
            print(f"  1. 🚨 REDUCE CRYPTO ALLOCATION from {crypto_pct:.1f}% to <60%")
        if total_unrealized_pl < -1000:
            print(f"  2. 🚨 IMPLEMENT STOP LOSSES to prevent further bleeding")
        if len(positions) > 20:
            print(f"  3. 🚨 CLOSE WEAK POSITIONS to focus on best performers")
        if len(filled_orders) == 0:
            print(f"  4. 🚨 CHECK SYSTEM - No trading activity detected")
        
        print(f"\n📈 PERFORMANCE TARGET ANALYSIS:")
        monthly_target = portfolio_value * 0.05  # 5% monthly target
        daily_target = monthly_target / 22  # 22 trading days
        print(f"  Target 5% monthly return: ${monthly_target:.2f}")
        print(f"  Required daily profit: ${daily_target:.2f}")
        print(f"  Current daily trend: {'📉 LOSING' if total_unrealized_pl < 0 else '📈 GAINING'}")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    main()