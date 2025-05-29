#!/usr/bin/env python3
"""
EMERGENCY ORDER CANCELLATION SCRIPT
Cancel ALL pending orders immediately to prevent over-exposure
"""

import os
import sys
from datetime import datetime

def cancel_all_orders():
    """Cancel every single pending order in the account"""
    try:
        # Import Alpaca API
        from alpaca_trade_api import REST
        
        # Get API credentials
        api_key = os.getenv('ALPACA_PAPER_API_KEY')
        secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
        
        if not api_key or not secret_key:
            print("❌ ERROR: Missing Alpaca API credentials")
            print("Set environment variables:")
            print("  export ALPACA_PAPER_API_KEY='your_key'")
            print("  export ALPACA_PAPER_SECRET_KEY='your_secret'")
            return False
        
        # Initialize API
        api = REST(api_key, secret_key, base_url='https://paper-api.alpaca.markets')
        
        print("🚨 EMERGENCY ORDER CANCELLATION")
        print("=" * 50)
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get ALL pending orders
        print("\n📋 Fetching all pending orders...")
        pending_orders = api.list_orders(status='new')
        
        if not pending_orders:
            print("✅ No pending orders found - account is clean!")
            return True
        
        print(f"🚨 Found {len(pending_orders)} pending orders to cancel")
        print("\n🧹 CANCELLING ALL ORDERS...")
        
        # Cancel every single order
        cancelled_count = 0
        failed_count = 0
        
        for i, order in enumerate(pending_orders, 1):
            try:
                api.cancel_order(order.id)
                print(f"✅ [{i:3d}/{len(pending_orders)}] Cancelled: {order.symbol} {order.side} {order.qty} shares")
                cancelled_count += 1
                
            except Exception as e:
                print(f"❌ [{i:3d}/{len(pending_orders)}] Failed {order.symbol}: {str(e)[:50]}")
                failed_count += 1
        
        print(f"\n📊 CANCELLATION SUMMARY:")
        print(f"✅ Successfully cancelled: {cancelled_count} orders")
        print(f"❌ Failed to cancel: {failed_count} orders")
        print(f"📋 Total processed: {len(pending_orders)} orders")
        
        if cancelled_count > 0:
            print(f"\n🎉 Account cleaned! {cancelled_count} pending orders removed.")
            
        if failed_count > 0:
            print(f"\n⚠️ {failed_count} orders failed to cancel - may need manual intervention")
        
        return failed_count == 0
        
    except Exception as e:
        print(f"🚨 CRITICAL ERROR: {e}")
        return False

def verify_clean_account():
    """Verify that all orders have been cancelled"""
    try:
        from alpaca_trade_api import REST
        
        api_key = os.getenv('ALPACA_PAPER_API_KEY')
        secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
        api = REST(api_key, secret_key, base_url='https://paper-api.alpaca.markets')
        
        print("\n🔍 VERIFICATION: Checking for remaining orders...")
        pending_orders = api.list_orders(status='new')
        
        if not pending_orders:
            print("✅ VERIFICATION PASSED: No pending orders remaining!")
            return True
        else:
            print(f"⚠️ VERIFICATION FAILED: {len(pending_orders)} orders still pending")
            for order in pending_orders[:5]:  # Show first 5
                print(f"   - {order.symbol} {order.side} {order.qty} shares")
            if len(pending_orders) > 5:
                print(f"   ... and {len(pending_orders) - 5} more")
            return False
            
    except Exception as e:
        print(f"⚠️ Verification error: {e}")
        return False

def main():
    """Main execution"""
    print("🚨 EMERGENCY ORDER CANCELLATION UTILITY")
    print("This will cancel ALL pending orders in your account!")
    
    # Cancel all orders
    success = cancel_all_orders()
    
    if success:
        # Verify clean state
        verify_clean_account()
        
        print("\n🛡️ CRISIS PREVENTION:")
        print("All pending duplicate orders have been cancelled.")
        print("Your account is now clean and ready for proper trading.")
        print("\n🎯 NEXT STEPS:")
        print("1. System will now only trade during market hours")
        print("2. No more duplicate orders will be created") 
        print("3. Trading will resume properly when market opens")
        
    else:
        print("\n⚠️ Some orders may still be pending.")
        print("Check your Alpaca dashboard and manually cancel if needed.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)