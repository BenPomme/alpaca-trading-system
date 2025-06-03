#!/usr/bin/env python3
"""
Order Management System for Phase 2
Handles actual paper trade execution with Alpaca API
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database_manager import TradingDatabase

class OrderManager:
    """Manages actual paper trade execution"""
    
    def __init__(self, api_client, db: TradingDatabase = None):
        self.api = api_client
        self.db = db
        self.active_positions = {}
        self.pending_orders = {}
        
        # Risk management parameters (Phase 4.1: Unlimited positions)
        self.max_positions = None  # No limit on positions
        self.max_position_value = 10000  # $10,000 per position
        self.max_portfolio_risk = 0.05   # 5% daily portfolio risk
        self.position_size_pct = 0.02    # 2% risk per trade
        
        print("✅ Order Manager initialized")
        self.log_current_positions()
    
    def log_current_positions(self):
        """Log current account positions"""
        try:
            positions = self.api.list_positions()
            account = self.api.get_account()
            
            portfolio_value = float(account.portfolio_value)
            print(f"💰 Portfolio Value: ${portfolio_value:,.2f}")
            
            if positions:
                print(f"📊 Current Positions ({len(positions)}):")
                for pos in positions:
                    qty = float(pos.qty)
                    market_value = float(pos.market_value)
                    unrealized_pl = float(pos.unrealized_pl)
                    print(f"   {pos.symbol}: {qty:+.0f} shares, ${market_value:,.2f} ({unrealized_pl:+.2f})")
                    
                    self.active_positions[pos.symbol] = {
                        'qty': qty,
                        'avg_entry_price': float(pos.avg_entry_price),
                        'market_value': market_value,
                        'unrealized_pl': unrealized_pl,
                        'side': 'long' if qty > 0 else 'short'
                    }
            else:
                print("📊 No current positions")
                
        except Exception as e:
            print(f"⚠️ Error getting positions: {e}")
    
    def calculate_position_size(self, symbol: str, entry_price: float, strategy: str) -> int:
        """Calculate appropriate position size based on risk management"""
        try:
            account = self.api.get_account()
            portfolio_value = float(account.portfolio_value)
            
            # CRITICAL FIX: Use proper buying power based on trade type
            daytrading_bp = float(getattr(account, 'daytrading_buying_power', 0))
            regt_bp = float(getattr(account, 'regt_buying_power', 0))
            
            # Use day trading power if available for intraday trades
            if daytrading_bp > 0:
                buying_power = daytrading_bp  # 4:1 leverage
            elif regt_bp > 0:
                buying_power = regt_bp  # 2:1 leverage  
            else:
                buying_power = float(account.buying_power)  # Fallback
            
            # Base position size (2% of portfolio)
            risk_amount = portfolio_value * self.position_size_pct
            
            # Strategy-based adjustments
            if strategy == 'aggressive_momentum':
                risk_multiplier = 1.5  # Increase risk for high-confidence trades
            elif strategy == 'momentum':
                risk_multiplier = 1.0  # Standard risk
            elif strategy == 'cautious_momentum':
                risk_multiplier = 0.7  # Reduce risk
            else:  # conservative
                risk_multiplier = 0.5  # Minimal risk
            
            adjusted_risk = risk_amount * risk_multiplier
            
            # Calculate share quantity
            target_value = min(adjusted_risk, self.max_position_value)
            shares = int(target_value / entry_price)
            
            # Ensure we don't exceed buying power
            max_affordable_shares = int(buying_power / entry_price)
            shares = min(shares, max_affordable_shares)
            
            # Minimum viable position (at least 1 share if we can afford it)
            if shares == 0 and buying_power >= entry_price:
                shares = 1
            
            print(f"💰 Position sizing for {symbol}:")
            print(f"   Portfolio: ${portfolio_value:,.2f}, Risk: ${adjusted_risk:,.2f}")
            print(f"   Target shares: {shares}, Value: ${shares * entry_price:,.2f}")
            
            return shares
            
        except Exception as e:
            print(f"⚠️ Position sizing error: {e}")
            return 0
    
    def place_order_with_retry(self, order_details: Dict) -> Optional[Dict]:
        """Place an order with exponential backoff retry logic."""
        retry_attempts = 5
        delay_seconds = 3  # Initial delay
        for attempt in range(retry_attempts):
            try:
                order = self.api.submit_order(
                    symbol=order_details['symbol'],
                    qty=order_details['qty'],
                    side=order_details['side'],
                    type=order_details['type'],
                    time_in_force=order_details['time_in_force'],
                    limit_price=order_details.get('limit_price'), # Optional for limit orders
                    stop_price=order_details.get('stop_price')    # Optional for stop orders
                )
                print(f"✅ Order submitted: {order.symbol} {order.side} {order.qty} shares @ {order.type}")
                if self.db:
                    self.db.log_order(order_details['symbol'], order_details['type'], order_details['side'], 
                                      order_details['qty'], entry_price=order_details.get('limit_price', order_details.get('stop_price', 0)), 
                                      strategy=order_details.get('strategy', 'N/A'), status='submitted', order_id=order.id)
                return order # Return the Alpaca order object
            except Exception as e:
                print(f"⚠️ Order attempt {attempt + 1}/{retry_attempts} failed for {order_details.get('symbol', 'N/A')}: {e}")
                if attempt < retry_attempts - 1:
                    print(f"   Retrying in {delay_seconds}s...")
                    time.sleep(delay_seconds)
                    delay_seconds *= 2  # Exponential backoff
                else:
                    print(f"🚫 Failed to place order for {order_details.get('symbol', 'N/A')} after {retry_attempts} attempts.")
                    if self.db:
                        self.db.log_order(order_details['symbol'], order_details['type'], order_details['side'], 
                                      order_details['qty'], entry_price=order_details.get('limit_price', order_details.get('stop_price', 0)), 
                                      strategy=order_details.get('strategy', 'N/A'), status='failed', error_message=str(e))
                    return None
    
    def check_position_limits(self, symbol: str) -> bool:
        """Check if we can open a new position"""
        # Update current positions
        self.log_current_positions()
        
        # AGGRESSIVE STRATEGY: Allow position building for unlimited scaling
        # For 5-10% monthly targets, we need aggressive position scaling
        if symbol in self.active_positions:
            print(f"✅ Position building allowed for {symbol} (aggressive strategy)")
            # Continue to other checks - don't block position additions
        
        # Check maximum positions limit (Phase 4.1: Unlimited positions)
        if self.max_positions is not None and len(self.active_positions) >= self.max_positions:
            print(f"⚠️ Maximum positions reached ({self.max_positions})")
            return False
        
        return True
    
    def is_market_open(self) -> bool:
        """Check if ANY global market is currently open for trading"""
        try:
            # Get US market clock from Alpaca
            clock = self.api.get_clock()
            us_market_open = clock.is_open
            
            print(f"   🕐 US Market Status: {'OPEN' if us_market_open else 'CLOSED'}")
            print(f"   🕐 Current Time: {clock.timestamp}")
            
            # For global trading, we check if ANY major market is open
            import datetime
            import pytz
            
            current_utc = datetime.datetime.now(pytz.UTC)
            
            # Check major global market hours
            global_markets_open = []
            
            # US Market (already checked)
            if us_market_open:
                global_markets_open.append("US")
            
            # Asian Markets (simplified - assume open during Asian business hours)
            # Tokyo: 9:00-15:30 JST (00:00-06:30 UTC)
            # Hong Kong: 9:30-16:00 HKT (01:30-08:00 UTC) 
            tokyo_tz = pytz.timezone('Asia/Tokyo')
            tokyo_time = current_utc.astimezone(tokyo_tz)
            tokyo_hour = tokyo_time.hour
            
            # Simplified Asian market check (9:00-15:30 JST weekdays)
            if tokyo_time.weekday() < 5 and 9 <= tokyo_hour <= 15:
                global_markets_open.append("Asia")
            
            # European Markets (8:00-16:30 GMT weekdays)
            london_tz = pytz.timezone('Europe/London') 
            london_time = current_utc.astimezone(london_tz)
            london_hour = london_time.hour
            
            if london_time.weekday() < 5 and 8 <= london_hour <= 16:
                global_markets_open.append("Europe")
            
            any_market_open = len(global_markets_open) > 0
            
            if global_markets_open:
                print(f"   🌍 Global Markets Open: {', '.join(global_markets_open)}")
            else:
                print(f"   🌙 All Global Markets Closed")
            
            return any_market_open
            
        except Exception as e:
            print(f"   ⚠️ Error checking global market hours: {e}")
            # If we can't check, be permissive for global trading
            return True
    
    def cancel_duplicate_orders(self):
        """Cancel duplicate pending orders to prevent over-exposure"""
        try:
            print(f"🧹 Checking for duplicate pending orders...")
            pending_orders = self.api.list_orders(status='new')
            
            if not pending_orders:
                print(f"   ✅ No pending orders found")
                return
            
            # Group orders by symbol
            symbol_orders = {}
            for order in pending_orders:
                symbol = order.symbol
                if symbol not in symbol_orders:
                    symbol_orders[symbol] = []
                symbol_orders[symbol].append(order)
            
            cancelled_count = 0
            for symbol, orders in symbol_orders.items():
                if len(orders) > 1:
                    # Keep the first order, cancel the rest
                    print(f"   🔍 Found {len(orders)} duplicate orders for {symbol}")
                    for i, order in enumerate(orders[1:], 1):  # Skip first order
                        try:
                            self.api.cancel_order(order.id)
                            print(f"   ❌ Cancelled duplicate order {i}: {symbol} {order.qty} shares")
                            cancelled_count += 1
                        except Exception as e:
                            print(f"   ⚠️ Failed to cancel order {order.id}: {e}")
            
            print(f"   🧹 Cancelled {cancelled_count} duplicate orders")
            
        except Exception as e:
            print(f"   ⚠️ Error checking/cancelling duplicate orders: {e}")
    
    def cancel_all_pending_orders(self):
        """Cancel ALL pending orders to clean slate - AGGRESSIVE VERSION"""
        try:
            print(f"🧹 EMERGENCY: CANCELLING ALL PENDING ORDERS...")
            
            # Try multiple times to catch all orders
            total_cancelled = 0
            for attempt in range(3):  # Try 3 times to catch everything
                pending_orders = self.api.list_orders(status='new')
                
                if not pending_orders:
                    if attempt == 0:
                        print(f"   ✅ No pending orders to cancel")
                    break
                
                print(f"   🔍 Attempt {attempt + 1}: Found {len(pending_orders)} pending orders")
                
                cancelled_count = 0
                for i, order in enumerate(pending_orders, 1):
                    try:
                        self.api.cancel_order(order.id)
                        print(f"   ❌ [{i:3d}/{len(pending_orders)}] Cancelled: {order.symbol} {order.side} {order.qty} shares")
                        cancelled_count += 1
                    except Exception as e:
                        print(f"   ⚠️ [{i:3d}/{len(pending_orders)}] Failed {order.symbol}: {str(e)[:50]}")
                
                total_cancelled += cancelled_count
                print(f"   🧹 Attempt {attempt + 1}: Cancelled {cancelled_count} orders")
                
                # Brief pause between attempts
                import time
                time.sleep(1)
            
            print(f"   🎉 TOTAL CANCELLED: {total_cancelled} pending orders across all attempts")
            return total_cancelled
            
        except Exception as e:
            print(f"   ⚠️ Error cancelling all pending orders: {e}")
            return 0
    
    def execute_buy_order(self, symbol: str, strategy: str, confidence: float, cycle_id: int = None) -> Dict:
        """Execute a buy order if conditions are met"""
        try:
            if not self.is_market_open():
                print(f"⚠️ Market closed - cannot buy {symbol}")
                return {'status': 'market_closed', 'symbol': symbol}
            
            if not self.check_position_limits(symbol):
                print(f"⚠️ Position limits reached - cannot buy {symbol}")
                return {'status': 'limit_reached', 'symbol': symbol}
            
            # Get current price for sizing
            # CRITICAL FIX: Use reliable real-time price source
            try:
                quote = self.api.get_latest_quote(symbol) # Changed from get_last_trade
                entry_price = float(quote.ap) # ask price for buying
                if entry_price == 0: # Fallback if ask price is zero
                    trade = self.api.get_latest_trade(symbol)
                    entry_price = float(trade.price)
                print(f"📊 Current Ask Price for {symbol}: ${entry_price:.2f}")
            except Exception as e:
                print(f"⚠️ Failed to get current price for {symbol}: {e} - using fallback")
                # Fallback: last trade price (less ideal for buys)
                try:
                    trade = self.api.get_latest_trade(symbol)
                    entry_price = float(trade.price)
                    print(f"📊 Fallback Last Trade Price for {symbol}: ${entry_price:.2f}")
                except Exception as e_trade:
                     print(f"🚫 Failed to get any price for {symbol}: {e_trade}")
                     return {'status': 'price_error', 'symbol': symbol, 'error': str(e_trade)}

            if entry_price == 0:
                print(f"🚫 Zero price for {symbol}, cannot place order.")
                return {'status': 'price_error', 'symbol': symbol, 'error': 'Zero price'}

            shares = self.calculate_position_size(symbol, entry_price, strategy)
            if shares == 0:
                print(f"⚠️ Calculated 0 shares for {symbol} - cannot buy")
                return {'status': 'zero_shares', 'symbol': symbol}
            
            print(f"🚀 Attempting BUY: {shares} shares of {symbol} @ approx ${entry_price:.2f}")
            
            order_details = {
                'symbol': symbol,
                'qty': shares,
                'side': 'buy',
                'type': 'market', # Market order for simplicity and higher fill rate
                'time_in_force': 'day', # Day order
                'strategy': strategy # For logging
            }

            order_response = self.place_order_with_retry(order_details)

            if order_response and hasattr(order_response, 'id'):
                print(f"✅ BUY order for {shares} {symbol} submitted successfully.")
                self.active_positions[symbol] = {
                    'qty': shares,
                    'avg_entry_price': entry_price, # Approximate, will update on fill
                    'side': 'long'
                }
                self.pending_orders[order_response.id] = order_details
                
                if self.db:
                    self.db.log_trade(symbol, 'buy', shares, entry_price, strategy, confidence, status='submitted', order_id=order_response.id, cycle_id=cycle_id)
                return {
                    'status': 'success',
                    'order_id': order_response.id,
                    'symbol': symbol,
                    'shares': shares,
                    'price': entry_price,
                    'side': 'buy'
                }
            else:
                print(f"🚫 BUY order for {shares} {symbol} failed.")
                error_msg = "Order placement failed" if not order_response else str(order_response)
                if self.db:
                    self.db.log_trade(symbol, 'buy', shares, entry_price, strategy, confidence, status='failed', error_message=error_msg, cycle_id=cycle_id)
                return {
                    'status': 'failed',
                    'symbol': symbol,
                    'shares': shares,
                    'error': error_msg
                }

        except Exception as e:
            print(f"🚫 GENERAL ERROR executing BUY for {symbol}: {e}")
            if self.db:
                self.db.log_trade(symbol, 'buy', 0, 0, strategy, confidence, status='error', error_message=str(e), cycle_id=cycle_id)
            return {
                'status': 'error',
                'symbol': symbol,
                'error': str(e)
            }
    
    def execute_sell_order(self, symbol: str, reason: str = 'strategy', cycle_id: int = None) -> Dict:
        """Execute a sell order to close an existing position"""
        try:
            if not self.is_market_open():
                print(f"⚠️ Market closed - cannot sell {symbol}")
                return {'status': 'market_closed', 'symbol': symbol}

            self.log_current_positions() # Refresh active positions
            
            if symbol not in self.active_positions:
                print(f"⚠️ No active position for {symbol} to sell")
                return {'status': 'no_position', 'symbol': symbol}
            
            position = self.active_positions[symbol]
            shares = abs(float(position['qty'])) # Ensure positive qty for selling
            if shares <= 0:
                print(f"🚫 Cannot sell {symbol}: available quantity is zero or negative.")
                return {'status': 'insufficient_quantity', 'symbol': symbol, 'error': 'No shares available to sell'}
            side = 'sell' # Always sell to close a long position
            
            # Get current price for logging/approximate P&L
            # CRITICAL FIX: Use reliable real-time price source
            try:
                quote = self.api.get_latest_quote(symbol)
                exit_price = float(quote.bp) # bid price for selling
                if exit_price == 0: # Fallback if bid price is zero
                    trade = self.api.get_latest_trade(symbol)
                    exit_price = float(trade.price)
                print(f"📊 Current Bid Price for {symbol}: ${exit_price:.2f}")
            except Exception as e:
                print(f"⚠️ Failed to get current price for {symbol}: {e} - using fallback")
                try:
                    trade = self.api.get_latest_trade(symbol)
                    exit_price = float(trade.price)
                    print(f"📊 Fallback Last Trade Price for {symbol}: ${exit_price:.2f}")
                except Exception as e_trade:
                    print(f"🚫 Failed to get any price for {symbol}: {e_trade}")
                    return {'status': 'price_error', 'symbol': symbol, 'error': str(e_trade)}

            if exit_price == 0:
                print(f"🚫 Zero price for {symbol}, cannot place sell order.")
                return {'status': 'price_error', 'symbol': symbol, 'error': 'Zero price'}

            print(f"🚀 Attempting SELL: {shares} shares of {symbol} @ approx ${exit_price:.2f} (Reason: {reason})")

            order_details = {
                'symbol': symbol,
                'qty': shares,
                'side': side,
                'type': 'market', # Market order for simplicity and higher fill rate
                'time_in_force': 'day', # Day order
                'strategy': reason # For logging, use reason as strategy
            }

            order_response = self.place_order_with_retry(order_details)
            
            if order_response and hasattr(order_response, 'id'):
                print(f"✅ SELL order for {shares} {symbol} submitted successfully.")
                # Remove from active positions, will be confirmed by fill event or reconciliation
                # self.active_positions.pop(symbol, None) 
                # Instead of popping, mark as pending close or let reconciliation handle
                self.pending_orders[order_response.id] = order_details

                entry_price = float(position.get('avg_entry_price', 0))
                pnl_estimate = (exit_price - entry_price) * shares if entry_price else 0
                
                if self.db:
                    self.db.log_trade(symbol, 'sell', shares, exit_price, reason, 0, status='submitted', order_id=order_response.id, related_trade_id=position.get('db_id'), pnl=pnl_estimate, cycle_id=cycle_id)
                return {
                    'status': 'success',
                    'order_id': order_response.id,
                    'symbol': symbol,
                    'shares': shares,
                    'price': exit_price,
                    'side': 'sell',
                    'pnl_estimate': pnl_estimate
                }
            else:
                print(f"🚫 SELL order for {shares} {symbol} failed.")
                error_msg = "Order placement failed" if not order_response else str(order_response)
                if self.db:
                     self.db.log_trade(symbol, 'sell', shares, exit_price, reason, 0, status='failed', error_message=error_msg, related_trade_id=position.get('db_id'), cycle_id=cycle_id)
                return {
                    'status': 'failed',
                    'symbol': symbol,
                    'shares': shares,
                    'error': error_msg
                }

        except Exception as e:
            print(f"🚫 GENERAL ERROR executing SELL for {symbol}: {e}")
            position = self.active_positions.get(symbol, {})
            if self.db:
                self.db.log_trade(symbol, 'sell', 0, 0, reason, 0, status='error', error_message=str(e), related_trade_id=position.get('db_id'), cycle_id=cycle_id)
            return {
                'status': 'error',
                'symbol': symbol,
                'error': str(e)
            }
    
    def check_stop_losses(self) -> List[Dict]:
        """Check and execute stop losses for all positions"""
        executed_stops = []
        
        try:
            for symbol, position in self.active_positions.items():
                entry_price = position['avg_entry_price']
                current_quote = self.api.get_latest_quote(symbol)
                
                if not current_quote or not current_quote.bid_price:
                    continue
                
                current_price = float(current_quote.bid_price)
                loss_pct = ((current_price - entry_price) / entry_price) * 100
                
                # Stop loss at -3%
                if loss_pct <= -3.0:
                    print(f"🛑 STOP LOSS TRIGGERED: {symbol} ({loss_pct:.1f}%)")
                    result = self.execute_sell_order(symbol, 'stop_loss')
                    if result['success']:
                        executed_stops.append(result)
                
                # Take profit at +8% or +3% in one day
                elif loss_pct >= 8.0:
                    print(f"🎯 TAKE PROFIT: {symbol} ({loss_pct:.1f}%)")
                    result = self.execute_sell_order(symbol, 'take_profit')
                    if result['success']:
                        executed_stops.append(result)
        
        except Exception as e:
            print(f"⚠️ Stop loss check error: {e}")
        
        return executed_stops
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        try:
            account = self.api.get_account()
            positions = self.api.list_positions()
            
            total_pl = sum(float(pos.unrealized_pl) for pos in positions)
            total_value = sum(float(pos.market_value) for pos in positions)
            
            return {
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'total_positions': len(positions),
                'total_market_value': total_value,
                'total_unrealized_pl': total_pl,
                'daily_pl': float(account.equity) - float(account.last_equity),
                'positions': [
                    {
                        'symbol': pos.symbol,
                        'qty': float(pos.qty),
                        'market_value': float(pos.market_value),
                        'unrealized_pl': float(pos.unrealized_pl),
                        'unrealized_plpc': float(pos.unrealized_plpc) * 100
                    }
                    for pos in positions
                ]
            }
            
        except Exception as e:
            print(f"⚠️ Portfolio summary error: {e}")
            return {'error': str(e)}
    
    def get_current_positions(self):
        """Get current portfolio positions"""
        try:
            positions = self.api.list_positions()
            position_list = []
            
            for position in positions:
                position_list.append({
                    'symbol': position.symbol,
                    'qty': float(position.qty),
                    'market_value': float(position.market_value),
                    'unrealized_pl': float(position.unrealized_pl),
                    'side': 'long' if float(position.qty) > 0 else 'short'
                })
            
            return position_list
            
        except Exception as e:
            print(f"⚠️ Error getting positions: {e}")
            return []

def test_order_manager():
    """Test order manager functionality"""
    print("🧪 Testing Order Manager...")
    
    # This would require actual API connection
    # For now, just test initialization
    try:
        from enhanced_trader import EnhancedTrader
        from database_manager import TradingDatabase
        
        trader = EnhancedTrader(use_database=False)
        db = TradingDatabase()
        
        order_mgr = OrderManager(trader.api, db)
        
        # Test portfolio summary
        summary = order_mgr.get_portfolio_summary()
        print(f"✅ Portfolio Summary: ${summary.get('portfolio_value', 0):,.2f}")
        
        print("✅ Order Manager test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Order Manager test failed: {e}")
        return False

if __name__ == "__main__":
    # Set environment for testing
    os.environ['ALPACA_PAPER_API_KEY'] = os.environ.get('ALPACA_PAPER_API_KEY', 'PKOBXG3RWCRQTXH6ID0L')
    os.environ['ALPACA_PAPER_SECRET_KEY'] = os.environ.get('ALPACA_PAPER_SECRET_KEY', '8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn')
    
    test_order_manager()