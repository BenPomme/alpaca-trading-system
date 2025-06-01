"""
Order Executor for Modular Trading System

This module provides order execution functionality for the modular trading architecture.
It wraps the existing OrderManager functionality in a clean interface that integrates
with the modular system.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime


class ModularOrderExecutor:
    """
    Order executor for the modular trading system.
    
    Provides a clean interface for executing orders from trading modules
    while handling the underlying Alpaca API interactions.
    """
    
    def __init__(self, api_client, logger=None):
        """
        Initialize the order executor.
        
        Args:
            api_client: Alpaca API client
            logger: Logger instance
        """
        self.api = api_client
        self.logger = logger or logging.getLogger(__name__)
        
        # Execution configuration
        self.execution_enabled = True  # Enable real order execution
        self.dry_run_mode = False  # Set to True for testing
        
        # Order tracking
        self.pending_orders = {}
        self.executed_orders = {}
        
        self.logger.info("✅ Modular Order Executor initialized")
        
    def execute_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trading order.
        
        Args:
            order_data: Dictionary containing order details:
                - symbol: str
                - qty: float
                - side: str ('buy' or 'sell')
                - type: str ('market', 'limit', etc.)
                - time_in_force: str ('gtc', 'day', etc.)
                
        Returns:
            Dictionary with execution results:
                - success: bool
                - order_id: str (if successful)
                - error: str (if failed)
                - execution_price: float (if successful)
        """
        try:
            symbol = order_data.get('symbol')
            qty = order_data.get('qty', 0)
            side = order_data.get('side', 'buy')
            order_type = order_data.get('type', 'market')
            time_in_force = order_data.get('time_in_force', 'gtc')
            
            self.logger.info(f"🚀 Executing {side.upper()} order: {symbol} {qty} shares")
            
            # Validation checks
            if not symbol or qty <= 0:
                return {
                    'success': False,
                    'error': f'Invalid order data: symbol={symbol}, qty={qty}'
                }
            
            # Check if execution is enabled
            if not self.execution_enabled or self.dry_run_mode:
                self.logger.info(f"🔍 DRY RUN: Would execute {side} {qty} {symbol}")
                return {
                    'success': True,
                    'order_id': f'dry_run_{symbol}_{int(datetime.now().timestamp())}',
                    'execution_price': self._get_estimated_price(symbol),
                    'message': 'Dry run execution - no real order placed'
                }
            
            # Check for duplicate pending orders
            if self._has_pending_order(symbol, side):
                return {
                    'success': False,
                    'error': f'Pending {side} order already exists for {symbol}'
                }
            
            # Get current market price for validation
            current_price = self._get_current_price(symbol)
            if not current_price:
                return {
                    'success': False,
                    'error': f'Unable to get market price for {symbol}'
                }
            
            # Prepare Alpaca order
            alpaca_order_data = {
                'symbol': symbol,
                'qty': qty,
                'side': side,
                'type': order_type,
                'time_in_force': time_in_force
            }
            
            # Execute order via Alpaca API
            order = self.api.submit_order(**alpaca_order_data)
            
            # Track the order
            self.pending_orders[order.id] = {
                'symbol': symbol,
                'side': side,
                'qty': qty,
                'order': order,
                'timestamp': datetime.now()
            }
            
            self.logger.info(f"✅ Order submitted successfully: {order.id}")
            
            return {
                'success': True,
                'order_id': order.id,
                'execution_price': current_price,
                'message': f'{side.title()} order submitted for {symbol}'
            }
            
        except Exception as e:
            error_msg = f"Order execution failed: {e}"
            self.logger.error(f"❌ {error_msg}")
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def _has_pending_order(self, symbol: str, side: str) -> bool:
        """Check if there's already a pending order for this symbol and side."""
        try:
            pending_orders = self.api.list_orders(status='new')
            for order in pending_orders:
                if order.symbol == symbol and order.side == side:
                    return True
            return False
        except Exception as e:
            self.logger.warning(f"Could not check pending orders: {e}")
            return False
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price for a symbol."""
        try:
            # Handle crypto symbols differently
            if 'USD' in symbol and len(symbol) <= 7:
                # Crypto symbol - convert format
                if '/' not in symbol:
                    base_symbol = symbol.replace('USD', '')
                    formatted_symbol = f"{base_symbol}/USD"
                else:
                    formatted_symbol = symbol
                
                # Try crypto-specific methods with data freshness validation
                try:
                    quotes = self.api.get_latest_crypto_quotes(formatted_symbol)
                    if quotes and formatted_symbol in quotes:
                        quote = quotes[formatted_symbol]
                        
                        # Validate data freshness for critical trade execution
                        if hasattr(quote, 't') and quote.t:
                            from datetime import datetime, timezone
                            quote_time = quote.t.replace(tzinfo=timezone.utc) if quote.t.tzinfo is None else quote.t
                            age_seconds = (datetime.now(timezone.utc) - quote_time).total_seconds()
                            
                            if age_seconds > 120:  # Stricter threshold for trade execution
                                self.logger.warning(f"⚠️ EXECUTION: {symbol} quote is {age_seconds:.0f}s old - execution may be suboptimal")
                        
                        if hasattr(quote, 'ap') and quote.ap:
                            return float(quote.ap)
                        elif hasattr(quote, 'bp') and quote.bp:
                            return float(quote.bp)
                except Exception:
                    pass
                
                try:
                    trades = self.api.get_latest_crypto_trades(formatted_symbol)
                    if trades and formatted_symbol in trades:
                        trade = trades[formatted_symbol]
                        if hasattr(trade, 'p') and trade.p:
                            return float(trade.p)
                except Exception:
                    pass
            else:
                # Stock symbol with data freshness validation  
                try:
                    quote = self.api.get_latest_quote(symbol)
                    if quote:
                        # Validate data freshness for critical trade execution
                        if hasattr(quote, 'timestamp') and quote.timestamp:
                            from datetime import datetime, timezone
                            quote_time = quote.timestamp.replace(tzinfo=timezone.utc) if quote.timestamp.tzinfo is None else quote.timestamp
                            age_seconds = (datetime.now(timezone.utc) - quote_time).total_seconds()
                            
                            if age_seconds > 120:  # Stricter threshold for trade execution
                                self.logger.warning(f"⚠️ EXECUTION: {symbol} quote is {age_seconds:.0f}s old - execution may be suboptimal")
                        
                        if hasattr(quote, 'ask_price') and quote.ask_price:
                            return float(quote.ask_price)
                        elif hasattr(quote, 'bid_price') and quote.bid_price:
                            return float(quote.bid_price)
                except Exception:
                    pass
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error getting price for {symbol}: {e}")
            return None
    
    def _get_estimated_price(self, symbol: str) -> float:
        """Get estimated price for dry run mode."""
        real_price = self._get_current_price(symbol)
        if real_price:
            return real_price
        
        # Fallback estimates for dry run
        crypto_estimates = {
            'BTCUSD': 67000.0,
            'ETHUSD': 3200.0,
            'SOLUSD': 140.0,
            'AVAXUSD': 21.0,
            'UNIUSD': 6.0,
            'AAVEUSD': 100.0
        }
        
        return crypto_estimates.get(symbol, 100.0)  # Default estimate
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel a pending order."""
        try:
            self.api.cancel_order(order_id)
            
            # Remove from tracking
            if order_id in self.pending_orders:
                del self.pending_orders[order_id]
            
            self.logger.info(f"✅ Order cancelled: {order_id}")
            return {'success': True, 'message': f'Order {order_id} cancelled'}
            
        except Exception as e:
            error_msg = f"Failed to cancel order {order_id}: {e}"
            self.logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get the status of an order."""
        try:
            order = self.api.get_order(order_id)
            
            return {
                'success': True,
                'order_id': order.id,
                'status': order.status,
                'filled_qty': float(order.filled_qty) if order.filled_qty else 0.0,
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to get order status: {e}"
            }
    
    def set_execution_mode(self, enabled: bool, dry_run: bool = False):
        """Set execution mode for testing/production."""
        self.execution_enabled = enabled
        self.dry_run_mode = dry_run
        
        mode = "DISABLED" if not enabled else ("DRY_RUN" if dry_run else "LIVE")
        self.logger.info(f"🔧 Order execution mode: {mode}")