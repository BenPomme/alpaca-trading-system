#!/usr/bin/env python3
"""
EMERGENCY: Close all positions and enable aggressive trading

This script will be deployed to Railway to:
1. Close all existing positions immediately
2. Enable aggressive trading with simplified thresholds
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging for Railway deployment"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - FORCE_CLOSE - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def close_all_positions_railway():
    """Close all positions using Railway environment"""
    logger = setup_logging()
    
    try:
        import alpaca_trade_api as tradeapi
        
        # Get credentials from Railway environment
        api_key = os.getenv('ALPACA_PAPER_API_KEY')
        secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
        base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not api_key or not secret_key:
            logger.error("❌ ALPACA API CREDENTIALS NOT FOUND IN RAILWAY ENVIRONMENT")
            return False
        
        # Initialize API
        api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
        
        # Test connection
        account = api.get_account()
        logger.info(f"✅ Connected to Alpaca - Account: {account.id}")
        logger.info(f"💰 Portfolio Value: ${float(account.portfolio_value):,.2f}")
        logger.info(f"💵 Buying Power: ${float(account.buying_power):,.2f}")
        
        # Get all positions
        positions = api.list_positions()
        logger.info(f"📊 Found {len(positions)} open positions to close")
        
        if not positions:
            logger.info("✅ No positions to close - ready for fresh trading!")
            return True
        
        # Cancel all pending orders first
        logger.info("🚫 Cancelling all pending orders...")
        orders = api.list_orders(status='open')
        for order in orders:
            try:
                api.cancel_order(order.id)
                logger.info(f"✅ Cancelled: {order.symbol} {order.side} {order.qty}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to cancel order {order.id}: {e}")
        
        # Close all positions
        logger.info("🔄 Closing all positions...")
        for position in positions:
            try:
                symbol = position.symbol
                qty = abs(float(position.qty))
                side = 'sell' if float(position.qty) > 0 else 'buy'
                unrealized_pl = float(position.unrealized_pl)
                
                logger.info(f"🔄 Closing: {symbol} {side} {qty} shares (P&L: ${unrealized_pl:.2f})")
                
                # Submit market order to close
                order = api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side=side,
                    type='market',
                    time_in_force='day'
                )
                
                logger.info(f"✅ Close order submitted: {order.id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to close {symbol}: {e}")
        
        # Wait for positions to close
        logger.info("⏳ Waiting for positions to close...")
        for i in range(30):  # Wait up to 5 minutes
            time.sleep(10)
            remaining_positions = api.list_positions()
            
            if not remaining_positions:
                logger.info("✅ ALL POSITIONS CLOSED SUCCESSFULLY!")
                break
                
            if i % 3 == 0:  # Log every 30 seconds
                logger.info(f"⏳ Still waiting... {len(remaining_positions)} positions remaining")
        
        # Final status
        final_positions = api.list_positions()
        final_account = api.get_account()
        
        logger.info("=" * 60)
        logger.info("📊 FINAL ACCOUNT STATUS")
        logger.info("=" * 60)
        logger.info(f"💰 Portfolio Value: ${float(final_account.portfolio_value):,.2f}")
        logger.info(f"💵 Cash Available: ${float(final_account.cash):,.2f}")
        logger.info(f"🔓 Buying Power: ${float(final_account.buying_power):,.2f}")
        logger.info(f"📊 Remaining Positions: {len(final_positions)}")
        
        if final_positions:
            logger.warning("⚠️ Some positions still open:")
            for pos in final_positions:
                logger.warning(f"   - {pos.symbol}: {pos.qty} shares")
        
        logger.info("✅ POSITION CLOSURE COMPLETE - READY FOR AGGRESSIVE TRADING!")
        return len(final_positions) == 0
        
    except Exception as e:
        logger.error(f"❌ Position closure failed: {e}")
        return False

def main():
    """Main function that runs on Railway"""
    logger = setup_logging()
    
    logger.info("🚀 EMERGENCY POSITION CLOSER - Railway Deployment")
    logger.info("=" * 60)
    
    # Only run during market hours to avoid confusion
    try:
        import pytz
        from datetime import datetime
        
        et = pytz.timezone('US/Eastern')
        now_et = datetime.now(et)
        is_weekday = now_et.weekday() < 5
        is_trading_hours = 9 <= now_et.hour < 16
        
        logger.info(f"🕐 Current time: {now_et.strftime('%Y-%m-%d %H:%M %Z')}")
        logger.info(f"📅 Market open: {is_weekday and is_trading_hours}")
        
        if not (is_weekday and is_trading_hours):
            logger.info("⏰ Market closed - skipping position closure")
            logger.info("💡 Positions will be closed when market opens")
            return
    except:
        pass  # Continue anyway if timezone check fails
    
    # Close all positions
    success = close_all_positions_railway()
    
    if success:
        logger.info("🎯 SUCCESS: All positions closed, ready for full buying power trading!")
    else:
        logger.error("❌ FAILED: Some positions may still be open")

if __name__ == "__main__":
    main()