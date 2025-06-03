#!/usr/bin/env python3
"""
Emergency UNIUSD Liquidation Script
Split large position into smaller chunks to avoid $200k notional limit
"""
import os
import sys
import time
import alpaca_trade_api as tradeapi
from datetime import datetime

def main():
    # Initialize Alpaca API
    api_key = os.getenv('ALPACA_PAPER_API_KEY')
    secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
    base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    if not api_key or not secret_key:
        print("❌ API credentials not found in environment")
        return
    
    api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
    
    try:
        # Get current UNIUSD position
        positions = api.list_positions()
        uniusd_position = None
        
        for position in positions:
            if position.symbol == 'UNIUSD':
                uniusd_position = position
                break
        
        if not uniusd_position:
            print("✅ No UNIUSD position found")
            return
        
        # Position details
        quantity = float(uniusd_position.qty)
        current_price = float(uniusd_position.current_price)
        market_value = float(uniusd_position.market_value)
        unrealized_pl = float(uniusd_position.unrealized_pl)
        
        print(f"🔍 UNIUSD Position Analysis:")
        print(f"   Quantity: {quantity:,.0f} shares")
        print(f"   Current Price: ${current_price:.4f}")
        print(f"   Market Value: ${market_value:,.0f}")
        print(f"   Unrealized P&L: ${unrealized_pl:,.0f}")
        
        if quantity <= 0:
            print("✅ No long UNIUSD position to liquidate")
            return
        
        # Calculate chunk size to stay under $200k limit
        max_notional = 180000  # Stay under $200k with buffer
        max_shares_per_chunk = int(max_notional / current_price)
        
        print(f"\n📊 Liquidation Plan:")
        print(f"   Max shares per chunk: {max_shares_per_chunk:,.0f}")
        print(f"   Estimated chunks needed: {quantity / max_shares_per_chunk:.1f}")
        
        # Start liquidation process
        remaining_quantity = quantity
        chunk_number = 1
        
        while remaining_quantity > 100:  # Keep minimum threshold
            # Calculate this chunk size
            chunk_size = min(remaining_quantity, max_shares_per_chunk)
            chunk_notional = chunk_size * current_price
            
            print(f"\n🚀 Executing Chunk {chunk_number}:")
            print(f"   Shares: {chunk_size:,.0f}")
            print(f"   Estimated Value: ${chunk_notional:,.0f}")
            
            try:
                # Submit sell order
                order = api.submit_order(
                    symbol='UNIUSD',
                    qty=int(chunk_size),
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                
                print(f"✅ Order submitted: {order.id}")
                print(f"   Status: {order.status}")
                
                # Wait for order to process
                time.sleep(5)
                
                # Check order status
                updated_order = api.get_order(order.id)
                print(f"   Updated Status: {updated_order.status}")
                
                if updated_order.status in ['filled', 'partially_filled']:
                    filled_qty = float(updated_order.filled_qty) if updated_order.filled_qty else 0
                    remaining_quantity -= filled_qty
                    print(f"✅ Filled: {filled_qty:,.0f} shares")
                    print(f"   Remaining: {remaining_quantity:,.0f} shares")
                else:
                    print(f"⚠️ Order not filled: {updated_order.status}")
                    if updated_order.status == 'rejected':
                        print(f"   Rejection reason: {getattr(updated_order, 'reject_reason', 'Unknown')}")
                        break
                
                chunk_number += 1
                
                # Brief pause between chunks
                if remaining_quantity > 100:
                    print("⏳ Waiting 10 seconds before next chunk...")
                    time.sleep(10)
                    
            except Exception as e:
                print(f"❌ Error executing chunk {chunk_number}: {e}")
                break
        
        print(f"\n🎯 Liquidation Summary:")
        print(f"   Chunks executed: {chunk_number - 1}")
        print(f"   Remaining shares: {remaining_quantity:,.0f}")
        
        if remaining_quantity < 100:
            print("✅ Liquidation complete!")
        else:
            print("⚠️ Partial liquidation - manual intervention may be needed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()