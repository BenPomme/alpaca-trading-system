#!/usr/bin/env python3
"""
EMERGENCY MARKET CORRECTION SCRIPT

The system has failed catastrophically:
- $250k buying power unused 
- Large crypto positions during bullish stock market
- Zero stock/options trading despite clear signals

This script will:
1. Close ALL crypto positions immediately
2. Buy SPY, QQQ, and other bullish stocks aggressively  
3. Force the system to trade the actual market
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging for emergency correction"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - EMERGENCY - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def emergency_market_correction():
    """Emergency correction to trade the bullish market"""
    logger = setup_logging()
    
    try:
        import alpaca_trade_api as tradeapi
        
        # Get credentials from Railway environment
        api_key = os.getenv('ALPACA_PAPER_API_KEY')
        secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
        base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not api_key or not secret_key:
            logger.error("❌ ALPACA API CREDENTIALS NOT FOUND")
            return False
        
        # Initialize API
        api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
        
        # Get account status
        account = api.get_account()
        positions = api.list_positions()
        
        logger.info("🚨 EMERGENCY MARKET CORRECTION STARTING")
        logger.info("=" * 60)
        logger.info(f"💰 Portfolio Value: ${float(account.portfolio_value):,.2f}")
        logger.info(f"💵 Cash: ${float(account.cash):,.2f}")
        logger.info(f"🔓 Buying Power: ${float(account.buying_power):,.2f}")
        logger.info(f"📊 Current Positions: {len(positions)}")
        
        # Show current allocation disaster
        crypto_value = 0
        stock_value = 0
        for pos in positions:
            value = abs(float(pos.market_value))
            if any(crypto in pos.symbol for crypto in ['BTC', 'ETH', 'SOL', 'AVAX', 'LINK', 'UNI', 'AAVE', 'DOT', 'MATIC']):
                crypto_value += value
                logger.warning(f"💰 CRYPTO: {pos.symbol} ${value:,.2f}")
            else:
                stock_value += value
                logger.info(f"📈 STOCK: {pos.symbol} ${value:,.2f}")
        
        total_invested = crypto_value + stock_value
        crypto_pct = (crypto_value / total_invested * 100) if total_invested > 0 else 0
        stock_pct = (stock_value / total_invested * 100) if total_invested > 0 else 0
        
        logger.error(f"🚨 ALLOCATION DISASTER:")
        logger.error(f"   Crypto: ${crypto_value:,.2f} ({crypto_pct:.1f}%)")
        logger.error(f"   Stocks: ${stock_value:,.2f} ({stock_pct:.1f}%)")
        logger.error(f"   UNUSED: ${float(account.buying_power):,.2f}")
        
        # EMERGENCY ACTION 1: Close ALL crypto positions
        logger.info("🚨 STEP 1: CLOSING ALL CRYPTO POSITIONS")
        crypto_positions = [pos for pos in positions 
                          if any(crypto in pos.symbol for crypto in ['BTC', 'ETH', 'SOL', 'AVAX', 'LINK', 'UNI', 'AAVE', 'DOT', 'MATIC'])]
        
        for position in crypto_positions:
            try:
                symbol = position.symbol
                qty = abs(float(position.qty))
                side = 'sell' if float(position.qty) > 0 else 'buy'
                
                logger.info(f"🔄 EMERGENCY CLOSE: {symbol} {side} {qty}")
                
                order = api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side=side,
                    type='market',
                    time_in_force='day'
                )
                
                logger.info(f"✅ CLOSED: {symbol} - Order ID: {order.id}")
                
            except Exception as e:
                logger.error(f"❌ FAILED TO CLOSE {symbol}: {e}")
        
        # Wait for crypto closes to settle
        logger.info("⏳ Waiting for crypto positions to close...")
        time.sleep(30)
        
        # Get updated account after closes
        account = api.get_account()
        available_cash = float(account.buying_power)
        
        logger.info(f"💵 Available for stock trading: ${available_cash:,.2f}")
        
        # EMERGENCY ACTION 2: Buy bullish stocks aggressively
        logger.info("🚨 STEP 2: BUYING BULLISH STOCKS AGGRESSIVELY")
        
        # Bullish stocks to buy based on today's market
        bullish_stocks = [
            {'symbol': 'SPY', 'allocation': 0.30},   # 30% - S&P 500 bullish
            {'symbol': 'QQQ', 'allocation': 0.25},   # 25% - Nasdaq bullish  
            {'symbol': 'IWM', 'allocation': 0.15},   # 15% - Small caps
            {'symbol': 'AAPL', 'allocation': 0.10},  # 10% - Tech leader
            {'symbol': 'MSFT', 'allocation': 0.10},  # 10% - Strong performer
            {'symbol': 'NVDA', 'allocation': 0.05},  # 5% - AI leader
            {'symbol': 'TSLA', 'allocation': 0.05},  # 5% - Momentum play
        ]
        
        for stock in bullish_stocks:
            try:
                symbol = stock['symbol']
                allocation = stock['allocation']
                dollar_amount = available_cash * allocation
                
                # Get current price
                quote = api.get_latest_quote(symbol)
                current_price = float(quote.ask_price) if quote.ask_price else float(quote.bid_price)
                
                # Calculate shares
                shares = int(dollar_amount / current_price)
                
                if shares > 0:
                    logger.info(f"🚀 BUYING: {symbol} {shares} shares (~${dollar_amount:,.0f})")
                    
                    order = api.submit_order(
                        symbol=symbol,
                        qty=shares,
                        side='buy',
                        type='market',
                        time_in_force='day'
                    )
                    
                    logger.info(f"✅ BOUGHT: {symbol} - Order ID: {order.id}")
                    time.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ FAILED TO BUY {symbol}: {e}")
        
        # Final status
        time.sleep(10)
        final_account = api.get_account()
        final_positions = api.list_positions()
        
        logger.info("=" * 60)
        logger.info("📊 EMERGENCY CORRECTION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"💰 Final Portfolio Value: ${float(final_account.portfolio_value):,.2f}")
        logger.info(f"💵 Final Cash: ${float(final_account.cash):,.2f}")
        logger.info(f"🔓 Final Buying Power: ${float(final_account.buying_power):,.2f}")
        logger.info(f"📊 Final Positions: {len(final_positions)}")
        
        for pos in final_positions:
            logger.info(f"   📈 {pos.symbol}: {pos.qty} shares (${float(pos.market_value):,.2f})")
        
        logger.info("✅ EMERGENCY MARKET CORRECTION COMPLETED!")
        logger.info("💡 System should now be aligned with bullish market conditions")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Emergency correction failed: {e}")
        return False

def main():
    """Main function"""
    logger = setup_logging()
    
    logger.info("🚨 EMERGENCY MARKET CORRECTION SCRIPT")
    logger.info("Fixing catastrophic allocation failure during bullish market")
    
    success = emergency_market_correction()
    
    if success:
        logger.info("🎯 SUCCESS: Portfolio realigned with bullish market!")
    else:
        logger.error("❌ FAILED: Manual intervention required")

if __name__ == "__main__":
    main()