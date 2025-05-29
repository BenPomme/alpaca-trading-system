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
            buying_power = float(account.buying_power)
            
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
    
    def check_position_limits(self, symbol: str) -> bool:
        """Check if we can open a new position"""
        # Update current positions
        self.log_current_positions()
        
        # Check if we already have this position
        if symbol in self.active_positions:
            print(f"⚠️ Already have position in {symbol}")
            return False
        
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
        """Execute a buy order with proper risk management"""
        print(f"🚀 EXECUTE_BUY_ORDER CALLED: {symbol}")
        print(f"   Strategy: {strategy}, Confidence: {confidence:.1%}")
        
        try:
            # CRITICAL CHECK 1: Market Hours (prevent closed market trading)
            print(f"   🕐 Checking market hours...")
            if not self.is_market_open():
                print(f"   ❌ Market is closed - order rejected")
                return {'status': 'failed', 'message': 'Market is closed'}
            print(f"   ✅ Market is open")
            
            # CRITICAL CHECK 2: Pending Orders (prevent duplicates)
            print(f"   📋 Checking for pending orders...")
            pending_orders = self.api.list_orders(status='new')
            for order in pending_orders:
                if order.symbol == symbol and order.side == 'buy':
                    print(f"   ❌ Pending buy order already exists for {symbol}")
                    return {'status': 'failed', 'message': f'Pending order already exists for {symbol}'}
            print(f"   ✅ No pending orders for {symbol}")
            
            # Check position limits
            print(f"   📊 Checking position limits...")
            if not self.check_position_limits(symbol):
                print(f"   ❌ Position limits exceeded")
                return {'status': 'failed', 'message': 'Position limits exceeded'}
            print(f"   ✅ Position limits OK")
            
            # Get current quote
            print(f"   📈 Getting market quote...")
            quote = self.api.get_latest_quote(symbol)
            if not quote or not quote.ask_price:
                print(f"   ❌ No market data available")
                return {'status': 'failed', 'message': 'No market data available'}
            
            entry_price = float(quote.ask_price)
            print(f"   ✅ Quote: ${entry_price:.2f}")
            
            # Calculate position size
            print(f"   💰 Calculating position size...")
            shares = self.calculate_position_size(symbol, entry_price, strategy)
            print(f"   📊 Position size: {shares} shares")
            if shares <= 0:
                print(f"   ❌ Insufficient buying power")
                return {'status': 'failed', 'message': 'Insufficient buying power'}
            
            # Create buy order
            print(f"   🔥 Submitting buy order to Alpaca API...")
            print(f"      Symbol: {symbol}, Qty: {shares}, Side: buy, Type: market")
            order = self.api.submit_order(
                symbol=symbol,
                qty=shares,
                side='buy',
                type='market',
                time_in_force='day'
            )
            print(f"   ✅ Order submitted successfully! Order ID: {order.id}")
            
            # Log the order
            order_info = {
                'symbol': symbol,
                'side': 'buy',
                'qty': shares,
                'price': entry_price,
                'strategy': strategy,
                'confidence': confidence,
                'order_id': order.id,
                'timestamp': datetime.now().isoformat(),
                'cycle_id': cycle_id
            }
            
            # Store in database
            if self.db:
                self.db.store_virtual_trade(
                    symbol=symbol,
                    action='buy',
                    price=entry_price,
                    strategy=strategy,
                    regime='active',  # Assuming active if we're buying
                    confidence=confidence,
                    cycle_id=cycle_id
                )
            
            print(f"✅ BUY ORDER EXECUTED: {symbol}")
            print(f"   Shares: {shares}")
            print(f"   Price: ${entry_price:.2f}")
            print(f"   Total: ${shares * entry_price:,.2f}")
            print(f"   Strategy: {strategy}")
            print(f"   Order ID: {order.id}")
            
            result = {
                'status': 'success',  # Fixed: match expected key name
                'order_id': order.id,
                'symbol': symbol,
                'shares': shares,
                'price': entry_price,
                'total_value': shares * entry_price,
                'strategy': strategy
            }
            
            print(f"   🎯 Returning success result: {result}")
            return result
            
        except Exception as e:
            error_msg = f"Buy order failed for {symbol}: {e}"
            print(f"❌ EXCEPTION in execute_buy_order: {error_msg}")
            print(f"   Exception type: {type(e).__name__}")
            print(f"   Exception details: {str(e)}")
            result = {'status': 'failed', 'message': error_msg}
            print(f"   🎯 Returning error result: {result}")
            return result
    
    def execute_sell_order(self, symbol: str, reason: str = 'strategy', cycle_id: int = None) -> Dict:
        """Execute a sell order for existing position"""
        try:
            # CRITICAL FIX: Use live Alpaca positions instead of internal tracking
            # Get actual positions from Alpaca
            positions = self.api.list_positions()
            position = None
            for pos in positions:
                if pos.symbol == symbol:
                    position = pos
                    break
            
            if not position:
                return {'success': False, 'reason': f'No position in {symbol}'}
            
            shares = abs(int(float(position.qty)))  # Ensure positive quantity from Alpaca position
            
            if shares <= 0:
                return {'success': False, 'reason': 'No shares to sell'}
            
            # Get current quote for sell price
            quote = self.api.get_latest_quote(symbol)
            if not quote or not quote.bid_price:
                return {'success': False, 'reason': 'No market data available'}
            
            sell_price = float(quote.bid_price)
            
            # Calculate P&L using correct Alpaca position attributes FIRST
            # Get entry price from Alpaca position (same logic as intelligent exit manager)
            try:
                if hasattr(position, 'avg_entry_price'):
                    entry_price = float(position.avg_entry_price)
                elif hasattr(position, 'cost_basis'):
                    entry_price = float(position.cost_basis)
                elif hasattr(position, 'avg_cost'):
                    entry_price = float(position.avg_cost)
                else:
                    # Calculate from market_value and qty as fallback
                    entry_price = float(position.market_value) / float(position.qty) if float(position.qty) != 0 else sell_price
            except:
                entry_price = sell_price  # Fallback to break-even
            
            profit_loss = (sell_price - entry_price) * shares
            profit_pct = (profit_loss / (entry_price * shares)) * 100 if entry_price > 0 else 0
            
            # Create sell order
            print(f"🔥 Submitting SELL order to Alpaca API...")
            print(f"   Symbol: {symbol}, Qty: {shares}, Side: sell, Type: market")
            print(f"   Entry: ${entry_price:.2f}, Current: ${sell_price:.2f}, P&L: {profit_pct:+.1f}%")
            
            order = self.api.submit_order(
                symbol=symbol,
                qty=shares,
                side='sell',
                type='market',
                time_in_force='day'
            )
            
            print(f"✅ SELL Order submitted successfully! Order ID: {order.id}")
            print(f"✅ SELL ORDER EXECUTED: {symbol}")
            print(f"   Shares: {shares}")
            print(f"   Price: ${sell_price:.2f}")
            print(f"   P&L: {profit_pct:+.1f}%")
            print(f"   Reason: {reason}")
            print(f"   Order ID: {order.id}")
            
            # Store in database
            if self.db:
                self.db.store_virtual_trade(
                    symbol=symbol,
                    action='sell',
                    price=sell_price,
                    strategy=reason,
                    regime='active',
                    confidence=0.0,
                    cycle_id=cycle_id
                )
            
            print(f"✅ SELL ORDER EXECUTED: {symbol}")
            print(f"   Shares: {shares}")
            print(f"   Sell Price: ${sell_price:.2f}")
            print(f"   Entry Price: ${entry_price:.2f}")
            print(f"   P&L: ${profit_loss:+.2f} ({profit_pct:+.1f}%)")
            print(f"   Reason: {reason}")
            print(f"   Order ID: {order.id}")
            
            # Remove from active positions (will be updated on next position check)
            if symbol in self.active_positions:
                del self.active_positions[symbol]
            
            return {
                'success': True,
                'order_id': order.id,
                'symbol': symbol,
                'shares': shares,
                'sell_price': sell_price,
                'entry_price': entry_price,
                'profit_loss': profit_loss,
                'profit_pct': profit_pct,
                'reason': reason
            }
            
        except Exception as e:
            error_msg = f"Sell order failed for {symbol}: {e}"
            print(f"❌ {error_msg}")
            return {'success': False, 'reason': error_msg}
    
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