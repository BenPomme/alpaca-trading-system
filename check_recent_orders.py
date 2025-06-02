#!/usr/bin/env python3
"""
Check Recent Orders Script
Checks Alpaca account for recent orders, specifically looking for Apple (AAPL) orders from June 2nd
"""

import os
import sys
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi

def check_recent_orders():
    """Check for recent orders in Alpaca account"""
    
    print("🔍 CHECKING RECENT ALPACA ORDERS")
    print("=" * 50)
    print(f"📅 Looking for orders from {datetime.now().strftime('%Y-%m-%d')}")
    
    # Get API credentials
    api_key = os.getenv('ALPACA_PAPER_API_KEY')
    secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY') 
    base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    if not api_key or not secret_key:
        print("❌ Missing Alpaca API credentials")
        print("Set ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY environment variables")
        return False
    
    try:
        # Initialize Alpaca API
        api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
        
        # Get account info
        account = api.get_account()
        print(f"✅ Connected to account: {account.id}")
        print(f"📊 Portfolio value: ${float(account.portfolio_value):,.2f}")
        
        # Get recent orders (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        print(f"\n📋 RECENT ORDERS ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}):")
        print("-" * 80)
        
        # Get all orders
        orders = api.list_orders(
            status='all',
            limit=50,
            direction='desc'
        )
        
        apple_orders_today = []
        total_orders_today = []
        
        for order in orders:
            order_date = order.created_at.date()
            today = datetime.now().date()
            
            # Check if order is from today
            if order_date == today:
                total_orders_today.append(order)
                
                # Check if it's Apple
                if order.symbol == 'AAPL':
                    apple_orders_today.append(order)
                
                print(f"📅 {order.created_at.strftime('%H:%M:%S')} | "
                      f"{order.symbol} | {order.side.upper()} {order.qty} | "
                      f"{order.status} | ${order.filled_avg_price or 'N/A'}")
        
        # Focus on Apple orders
        if apple_orders_today:
            print(f"\n🍎 APPLE (AAPL) ORDERS TODAY: {len(apple_orders_today)}")
            print("=" * 60)
            
            for order in apple_orders_today:
                print(f"⏰ Time: {order.created_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"📊 Details: {order.side.upper()} {order.qty} shares")
                print(f"💰 Price: ${order.filled_avg_price or order.limit_price or 'Market'}")
                print(f"✅ Status: {order.status}")
                print(f"🔢 Order ID: {order.id}")
                
                # Check if order was placed outside market hours
                order_hour = order.created_at.hour
                order_minute = order.created_at.minute
                order_time_decimal = order_hour + (order_minute / 60.0)
                
                # US market hours: 9:30 AM (9.5) to 4:00 PM (16.0) ET
                market_open = 9.5
                market_close = 16.0
                
                if order_time_decimal < market_open or order_time_decimal > market_close:
                    print("🚨 ⚠️ ORDER PLACED OUTSIDE MARKET HOURS! ⚠️")
                    print(f"   Market hours: 9:30 AM - 4:00 PM ET")
                    print(f"   Order time: {order.created_at.strftime('%H:%M %Z')}")
                else:
                    print("✅ Order placed during market hours")
                
                print("-" * 40)
        else:
            print("✅ No Apple (AAPL) orders found today")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total orders today: {len(total_orders_today)}")
        print(f"   Apple orders today: {len(apple_orders_today)}")
        
        # Check current positions for Apple
        positions = api.list_positions()
        apple_position = None
        
        for position in positions:
            if position.symbol == 'AAPL':
                apple_position = position
                break
        
        if apple_position:
            print(f"\n🍎 CURRENT APPLE POSITION:")
            print(f"   Quantity: {apple_position.qty}")
            print(f"   Market Value: ${float(apple_position.market_value):,.2f}")
            print(f"   Entry Price: ${float(apple_position.avg_entry_price):,.2f}")
            print(f"   Current Price: ${float(apple_position.current_price):,.2f}")
            print(f"   P&L: ${float(apple_position.unrealized_pl):,.2f}")
        else:
            print("✅ No current Apple position")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking orders: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_recent_orders()
    sys.exit(0 if success else 1)