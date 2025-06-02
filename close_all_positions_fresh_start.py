#!/usr/bin/env python3
"""
Close All Positions for Fresh Start

This script closes all open positions to allow the algorithm to start fresh
with full buying power during market hours.
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import alpaca_trade_api as tradeapi
from production_config import ProductionConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PositionCloser:
    """Close all positions for fresh algorithm start"""
    
    def __init__(self):
        """Initialize the position closer with Alpaca API"""
        self.config = ProductionConfig()
        self.api = self._initialize_alpaca_api()
        
    def _initialize_alpaca_api(self) -> tradeapi.REST:
        """Initialize Alpaca API connection"""
        try:
            api_key = self.config.get('ALPACA_PAPER_API_KEY')
            secret_key = self.config.get('ALPACA_PAPER_SECRET_KEY')
            base_url = self.config.get('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
            
            if not api_key or not secret_key:
                raise ValueError("Alpaca API credentials not found")
            
            api = tradeapi.REST(
                api_key,
                secret_key,
                base_url,
                api_version='v2'
            )
            
            # Test connection
            account = api.get_account()
            logger.info(f"✅ Connected to Alpaca - Account: {account.id}")
            
            return api
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Alpaca API: {e}")
            raise
    
    def close_all_positions(self) -> None:
        """Close all open positions"""
        try:
            logger.info("🔍 Checking for open positions...")
            
            # Get all positions
            positions = self.api.list_positions()
            
            if not positions:
                logger.info("✅ No open positions found - account is clean")
                return
            
            logger.info(f"📊 Found {len(positions)} open positions")
            
            # Cancel all pending orders first
            self._cancel_all_orders()
            
            # Close all positions
            for position in positions:
                self._close_position(position)
            
            # Wait for positions to close
            self._wait_for_positions_to_close()
            
            logger.info("✅ All positions closed successfully - ready for fresh start!")
            
        except Exception as e:
            logger.error(f"❌ Error closing positions: {e}")
            raise
    
    def _cancel_all_orders(self) -> None:
        """Cancel all pending orders"""
        try:
            orders = self.api.list_orders(status='open')
            
            if not orders:
                logger.info("✅ No pending orders to cancel")
                return
            
            logger.info(f"🚫 Cancelling {len(orders)} pending orders...")
            
            for order in orders:
                try:
                    self.api.cancel_order(order.id)
                    logger.info(f"✅ Cancelled order: {order.symbol} {order.side} {order.qty}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to cancel order {order.id}: {e}")
            
            time.sleep(2)  # Wait for cancellations to process
            
        except Exception as e:
            logger.error(f"❌ Error cancelling orders: {e}")
    
    def _close_position(self, position) -> None:
        """Close a single position"""
        try:
            symbol = position.symbol
            qty = abs(float(position.qty))
            side = 'sell' if float(position.qty) > 0 else 'buy'
            
            logger.info(f"🔄 Closing position: {symbol} {side} {qty} shares (P&L: ${float(position.unrealized_pl):.2f})")
            
            # Submit market order to close position
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='market',
                time_in_force='day'
            )
            
            logger.info(f"✅ Position close order submitted: {order.id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to close position {symbol}: {e}")
    
    def _wait_for_positions_to_close(self, max_wait_minutes: int = 5) -> None:
        """Wait for all positions to close"""
        logger.info(f"⏳ Waiting for positions to close (max {max_wait_minutes} minutes)...")
        
        for i in range(max_wait_minutes * 6):  # Check every 10 seconds
            try:
                positions = self.api.list_positions()
                
                if not positions:
                    logger.info("✅ All positions closed successfully!")
                    return
                
                if i % 6 == 0:  # Log every minute
                    logger.info(f"⏳ Still waiting... {len(positions)} positions remaining")
                
                time.sleep(10)
                
            except Exception as e:
                logger.warning(f"⚠️ Error checking positions: {e}")
                time.sleep(10)
        
        # Final check
        remaining_positions = self.api.list_positions()
        if remaining_positions:
            logger.warning(f"⚠️ {len(remaining_positions)} positions still open after {max_wait_minutes} minutes")
            for pos in remaining_positions:
                logger.warning(f"   - {pos.symbol}: {pos.qty} shares")
        else:
            logger.info("✅ All positions closed!")
    
    def show_account_summary(self) -> None:
        """Show account summary after closing positions"""
        try:
            account = self.api.get_account()
            positions = self.api.list_positions()
            
            logger.info("=" * 50)
            logger.info("📊 ACCOUNT SUMMARY AFTER POSITION CLOSURE")
            logger.info("=" * 50)
            logger.info(f"💰 Portfolio Value: ${float(account.portfolio_value):,.2f}")
            logger.info(f"💵 Cash: ${float(account.cash):,.2f}")
            logger.info(f"🔓 Buying Power: ${float(account.buying_power):,.2f}")
            logger.info(f"📊 Open Positions: {len(positions)}")
            
            if positions:
                logger.info("   Remaining positions:")
                for pos in positions:
                    logger.info(f"   - {pos.symbol}: {pos.qty} shares (${float(pos.unrealized_pl):.2f} P&L)")
            
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"❌ Error getting account summary: {e}")


def main():
    """Main execution function"""
    logger.info("🚀 POSITION CLOSER - Fresh Start Script")
    logger.info("This will close ALL open positions for a fresh algorithm start")
    
    try:
        closer = PositionCloser()
        
        # Show initial account state
        closer.show_account_summary()
        
        # Close all positions
        closer.close_all_positions()
        
        # Show final account state
        closer.show_account_summary()
        
        logger.info("✅ FRESH START COMPLETE - Algorithm ready for full buying power usage!")
        
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()