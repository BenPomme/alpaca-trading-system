#!/usr/bin/env python3
"""
CLOSE ALL POSITIONS IMMEDIATELY
Emergency position closure script
"""

import os
import alpaca_trade_api as tradeapi
import time
from datetime import datetime

# Set environment variables
os.environ['ALPACA_PAPER_API_KEY'] = "PKOBXG3RWCRQTXH6ID0L"
os.environ['ALPACA_PAPER_SECRET_KEY'] = "8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn"
os.environ['ALPACA_BASE_URL'] = "https://paper-api.alpaca.markets"

def close_all_positions():
    """Close all positions immediately"""
    print("🚨 CLOSING ALL POSITIONS IMMEDIATELY")
    print("=" * 50)
    
    try:
        api = tradeapi.REST(
            os.environ['ALPACA_PAPER_API_KEY'],
            os.environ['ALPACA_PAPER_SECRET_KEY'],
            os.environ['ALPACA_BASE_URL'],
            api_version='v2'
        )
        
        # Get current positions
        positions = api.list_positions()
        
        if not positions:
            print("✅ No positions to close")
            return
        
        print(f"📊 Found {len(positions)} positions to close:")
        
        closed_orders = []
        failed_orders = []
        
        for i, position in enumerate(positions, 1):
            symbol = position.symbol
            qty = float(position.qty)
            market_value = float(position.market_value)
            unrealized_pl = float(position.unrealized_pl)
            
            print(f"\n{i}. Closing {symbol}:")
            print(f"   Quantity: {qty}")
            print(f"   Value: ${market_value:,.2f}")
            print(f"   P&L: ${unrealized_pl:+.2f}")
            
            try:
                # Determine time_in_force based on symbol type
                if 'USD' in symbol and len(symbol) <= 7:
                    # Crypto symbols
                    time_in_force = 'gtc'
                else:
                    # Stock symbols
                    time_in_force = 'day'
                
                # Submit market sell order
                order = api.submit_order(
                    symbol=symbol,
                    qty=abs(qty),  # Use absolute value to ensure positive quantity
                    side='sell',
                    type='market',
                    time_in_force=time_in_force
                )
                
                print(f"   ✅ SELL order submitted: {order.id}")
                closed_orders.append({
                    'symbol': symbol,
                    'qty': abs(qty),
                    'order_id': order.id,
                    'market_value': market_value,
                    'unrealized_pl': unrealized_pl
                })
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ FAILED to close {symbol}: {e}")
                failed_orders.append({
                    'symbol': symbol,
                    'qty': qty,
                    'error': str(e),
                    'market_value': market_value
                })
        
        # Summary
        print(f"\n" + "=" * 50)
        print(f"📊 POSITION CLOSURE SUMMARY:")
        print(f"✅ Successfully submitted: {len(closed_orders)} orders")
        print(f"❌ Failed: {len(failed_orders)} orders")
        
        if closed_orders:
            total_value_closing = sum(order['market_value'] for order in closed_orders)
            total_unrealized_pl = sum(order['unrealized_pl'] for order in closed_orders)
            
            print(f"\n💰 POSITIONS BEING CLOSED:")
            print(f"   Total Value: ${total_value_closing:,.2f}")
            print(f"   Total P&L: ${total_unrealized_pl:+,.2f}")
            
            print(f"\n📋 ORDERS SUBMITTED:")
            for order in closed_orders:
                print(f"   {order['symbol']}: {order['qty']} shares → Order {order['order_id']}")
        
        if failed_orders:
            print(f"\n❌ FAILED ORDERS:")
            for order in failed_orders:
                print(f"   {order['symbol']}: {order['error']}")
        
        # Cancel any pending orders too
        print(f"\n🧹 CANCELLING ALL PENDING ORDERS...")
        try:
            pending_orders = api.list_orders(status='open')
            
            if pending_orders:
                print(f"   Found {len(pending_orders)} pending orders to cancel")
                
                cancelled_count = 0
                for order in pending_orders:
                    try:
                        api.cancel_order(order.id)
                        print(f"   ✅ Cancelled: {order.symbol} {order.side} {order.qty}")
                        cancelled_count += 1
                    except Exception as e:
                        print(f"   ❌ Failed to cancel {order.symbol}: {e}")
                
                print(f"   ✅ Total cancelled: {cancelled_count} orders")
            else:
                print(f"   ✅ No pending orders to cancel")
                
        except Exception as e:
            print(f"   ❌ Error checking pending orders: {e}")
        
        # Wait a moment and check final status
        print(f"\n⏳ Waiting 10 seconds for order processing...")
        time.sleep(10)
        
        # Final position check
        final_positions = api.list_positions()
        if final_positions:
            print(f"\n⚠️ {len(final_positions)} positions remain (orders may still be processing):")
            for pos in final_positions:
                print(f"   {pos.symbol}: {pos.qty} shares")
        else:
            print(f"\n🎉 ALL POSITIONS SUCCESSFULLY CLOSED!")
        
        # Get final account state
        account = api.get_account()
        print(f"\n💰 FINAL ACCOUNT STATE:")
        print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"   Cash: ${float(account.cash):,.2f}")
        print(f"   Buying Power: ${float(account.buying_power):,.2f}")
        
        # Save closure report
        closure_report = {
            'timestamp': datetime.now().isoformat(),
            'positions_closed': len(closed_orders),
            'positions_failed': len(failed_orders),
            'total_value_closed': sum(order['market_value'] for order in closed_orders),
            'total_unrealized_pl': sum(order['unrealized_pl'] for order in closed_orders),
            'final_portfolio_value': float(account.portfolio_value),
            'final_cash': float(account.cash),
            'closed_orders': closed_orders,
            'failed_orders': failed_orders
        }
        
        with open('position_closure_report.json', 'w') as f:
            import json
            json.dump(closure_report, f, indent=2)
        
        print(f"\n📁 Closure report saved: position_closure_report.json")
        
        return closure_report
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return None

def main():
    print("🚨 EMERGENCY POSITION CLOSURE")
    print("⚠️ WARNING: This will close ALL positions immediately!")
    
    # Confirmation
    confirm = input("\nType 'CLOSE ALL' to confirm: ").strip()
    
    if confirm == "CLOSE ALL":
        report = close_all_positions()
        
        if report:
            print(f"\n✅ POSITION CLOSURE COMPLETED!")
            print(f"📊 Closed {report['positions_closed']} positions")
            print(f"💰 Final Portfolio Value: ${report['final_portfolio_value']:,.2f}")
            print(f"💵 Cash Available: ${report['final_cash']:,.2f}")
        else:
            print(f"\n❌ POSITION CLOSURE FAILED!")
    else:
        print("❌ Aborted - No positions closed")

if __name__ == "__main__":
    main()