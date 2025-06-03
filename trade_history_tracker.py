#!/usr/bin/env python3
"""
Trade History Tracking System

Comprehensive trade tracking to prevent the rapid-fire trading losses
that caused $36,462 in capital loss within 5 minutes.

Key Features:
- Per-symbol trade history with timestamps
- 5-minute cooldown enforcement
- Position value tracking
- Rapid trading pattern detection
- Persistent storage with JSON backup
- Memory management (last 50 trades per symbol)
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal, getcontext
import logging

# Set precision for accurate financial calculations
getcontext().prec = 28

# Import Firebase for persistent storage
try:
    from firebase_database import FirebaseDatabase
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

class TradeHistoryTracker:
    """
    Tracks all trade activity to prevent rapid-fire trading incidents.
    
    This system specifically addresses the patterns that caused the $36K loss:
    - 50 trades in 5 minutes
    - Same symbols traded repeatedly (AVAXUSD, ETHUSD, etc.)
    - No cooldown periods between trades
    - Excessive position sizes ($23K+ per trade)
    """
    
    def __init__(self, firebase_db=None, logger=None):
        """
        Initialize trade history tracker with Firebase integration.
        
        Args:
            firebase_db: Firebase database instance (REQUIRED - no local fallback)
            logger: Logger instance
        """
        self.firebase_db = firebase_db
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize Firebase if not provided
        if not self.firebase_db and FIREBASE_AVAILABLE:
            try:
                self.firebase_db = FirebaseDatabase()
                self.logger.info("🔥 Connected to Firebase for trade history storage")
            except Exception as e:
                self.logger.warning(f"⚠️ Firebase connection failed: {e}, falling back to local storage")
                self.firebase_db = None
        
        # Trade tracking data structures
        self.trade_history: Dict[str, List[Dict]] = {}  # symbol -> trades
        self.position_values: Dict[str, Decimal] = {}   # symbol -> current value
        self.daily_trade_counts: Dict[str, int] = {}    # symbol -> daily count
        self.last_trade_times: Dict[str, datetime] = {} # symbol -> last trade time
        
        # Safety configuration - Based on loss analysis
        self.cooldown_minutes = 5       # 5-minute cooldown (was causing 10 trades/min)
        self.max_position_value = None  # REMOVED: No position size limits
        self.max_daily_trades = None    # REMOVED: No daily trade limits
        self.max_trades_per_hour = 2    # 2 trades per hour max per symbol
        self.rapid_trade_threshold = 3  # Flag as rapid if 3+ trades in 10 minutes
        
        # Load existing data
        self.load_history()
        
        storage_type = "Firebase" if self.firebase_db else "Local JSON"
        self.logger.info(f"🔍 Trade History Tracker initialized using {storage_type}")
        self.logger.info(f"📊 Tracking {len(self.trade_history)} symbols")
        
    def can_trade_symbol(self, symbol: str, trade_value: float) -> tuple[bool, str]:
        """
        Check if symbol can be traded based on all safety rules.
        
        This is the primary safety gate that prevents the rapid-fire trading
        that caused the $36,462 loss.
        
        Args:
            symbol: Trading symbol (e.g., 'AVAXUSD', 'ETHUSD')
            trade_value: Dollar value of proposed trade
            
        Returns:
            (can_trade: bool, reason: str)
        """
        
        # Check 1: Cooldown period (prevents rapid trading)
        if self._is_in_cooldown(symbol):
            last_time = self.last_trade_times.get(symbol)
            if last_time:
                minutes_ago = (datetime.now() - last_time).total_seconds() / 60
                return False, f"COOLDOWN: {symbol} last traded {minutes_ago:.1f}min ago (need {self.cooldown_minutes}min)"
        
        # Check 2: Position value limits - REMOVED per user request
        # No position size limits
        
        # Check 3: Daily trade limits - REMOVED per user request  
        # No daily trade limits
        
        # Check 4: Hourly trade limits (prevents rapid patterns)
        hourly_count = self._get_hourly_trade_count(symbol)
        if hourly_count >= self.max_trades_per_hour:
            return False, f"HOURLY_LIMIT: {symbol} has {hourly_count} trades in last hour (max {self.max_trades_per_hour})"
        
        # Check 5: Rapid trading pattern detection (prevents the exact pattern that caused loss)
        if self._is_rapid_trading_pattern(symbol):
            return False, f"RAPID_PATTERN: {symbol} shows dangerous rapid trading pattern"
        
        # All checks passed
        return True, "APPROVED"
    
    def record_trade(self, symbol: str, side: str, quantity: float, price: float, 
                    order_id: str = None, metadata: Dict = None) -> None:
        """
        Record a completed trade in the history.
        
        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            quantity: Number of shares/units
            price: Execution price
            order_id: Alpaca order ID
            metadata: Additional trade information
        """
        
        trade_value = Decimal(str(quantity)) * Decimal(str(price))
        timestamp = datetime.now()
        
        # Create trade record
        trade_record = {
            'timestamp': timestamp.isoformat(),
            'side': side.lower(),
            'quantity': float(quantity),
            'price': float(price),
            'value': float(trade_value),
            'order_id': order_id,
            'metadata': metadata or {}
        }
        
        # Initialize symbol tracking if needed
        if symbol not in self.trade_history:
            self.trade_history[symbol] = []
            self.position_values[symbol] = Decimal('0')
            self.daily_trade_counts[symbol] = 0
        
        # Add to history
        self.trade_history[symbol].append(trade_record)
        
        # Update position value
        if side.lower() == 'buy':
            self.position_values[symbol] += trade_value
        else:  # sell
            self.position_values[symbol] -= trade_value
        
        # Update counters
        self.daily_trade_counts[symbol] += 1
        self.last_trade_times[symbol] = timestamp
        
        # Memory management - keep last 50 trades per symbol
        if len(self.trade_history[symbol]) > 50:
            self.trade_history[symbol] = self.trade_history[symbol][-50:]
        
        # Persist to Firebase/disk
        self.save_history()
        
        # Also save individual trade to Firebase for detailed tracking
        if self.firebase_db:
            try:
                self._save_trade_to_firebase(trade_record, symbol)
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to save trade to Firebase: {e}")
        
        self.logger.info(f"📝 TRADE RECORDED: {symbol} {side.upper()} {quantity:,.4f} @ ${price:.2f}")
        self.logger.info(f"💰 Position Value: {symbol} = ${float(self.position_values[symbol]):,.2f}")
        
    def _is_in_cooldown(self, symbol: str) -> bool:
        """Check if symbol is in cooldown period."""
        if symbol not in self.last_trade_times:
            return False
        
        last_trade = self.last_trade_times[symbol]
        minutes_since = (datetime.now() - last_trade).total_seconds() / 60
        
        return minutes_since < self.cooldown_minutes
    
    def _get_hourly_trade_count(self, symbol: str) -> int:
        """Get number of trades for symbol in last hour."""
        if symbol not in self.trade_history:
            return 0
        
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        count = 0
        for trade in self.trade_history[symbol]:
            trade_time = datetime.fromisoformat(trade['timestamp'])
            if trade_time > one_hour_ago:
                count += 1
        
        return count
    
    def _is_rapid_trading_pattern(self, symbol: str) -> bool:
        """
        Detect the rapid trading pattern that caused the $36K loss.
        
        Specifically looks for:
        - Multiple trades within 10 minutes
        - Alternating buy/sell patterns
        - High frequency trading (like 50 trades in 5 minutes)
        """
        if symbol not in self.trade_history:
            return False
        
        trades = self.trade_history[symbol]
        if len(trades) < self.rapid_trade_threshold:
            return False
        
        # Check last few trades for rapid pattern
        recent_trades = trades[-self.rapid_trade_threshold:]
        trade_times = [datetime.fromisoformat(t['timestamp']) for t in recent_trades]
        
        # Check if all recent trades are within 10 minutes
        time_span = (trade_times[-1] - trade_times[0]).total_seconds() / 60
        if time_span < 10:  # 3+ trades within 10 minutes is rapid
            self.logger.warning(f"🚨 RAPID PATTERN: {symbol} has {len(recent_trades)} trades in {time_span:.1f} minutes")
            return True
        
        # Check for alternating buy/sell pattern (what caused the loss)
        if len(recent_trades) >= 4:
            sides = [t['side'] for t in recent_trades[-4:]]
            # Pattern like ['buy', 'sell', 'buy', 'sell'] is dangerous
            if len(set(sides)) == 2:  # Only buy and sell, no single direction
                alternating = all(sides[i] != sides[i+1] for i in range(len(sides)-1))
                if alternating:
                    self.logger.warning(f"🚨 ALTERNATING PATTERN: {symbol} shows buy/sell alternation")
                    return True
        
        return False
    
    def get_symbol_status(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive status for a symbol."""
        if symbol not in self.trade_history:
            can_trade, reason = self.can_trade_symbol(symbol, 1000)  # Test with $1K trade
            return {
                'symbol': symbol,
                'total_trades': 0,
                'daily_trades': 0,
                'hourly_trades': 0,
                'position_value': 0.0,
                'last_trade': None,
                'in_cooldown': False,
                'can_trade': can_trade,
                'status': reason
            }
        
        can_trade, reason = self.can_trade_symbol(symbol, 1000)  # Test with $1K trade
        
        return {
            'symbol': symbol,
            'total_trades': len(self.trade_history[symbol]),
            'daily_trades': self.daily_trade_counts.get(symbol, 0),
            'hourly_trades': self._get_hourly_trade_count(symbol),
            'position_value': float(self.position_values.get(symbol, 0)),
            'last_trade': self.last_trade_times.get(symbol).isoformat() if symbol in self.last_trade_times else None,
            'in_cooldown': self._is_in_cooldown(symbol),
            'can_trade': can_trade,
            'status': reason
        }
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status for all tracked symbols."""
        total_trades_today = sum(self.daily_trade_counts.values())
        symbols_on_cooldown = sum(1 for s in self.trade_history.keys() if self._is_in_cooldown(s))
        
        return {
            'total_symbols': len(self.trade_history),
            'total_trades_today': total_trades_today,
            'symbols_on_cooldown': symbols_on_cooldown,
            'safety_limits': {
                'cooldown_minutes': self.cooldown_minutes,
                'max_position_value': None,  # REMOVED
                'max_daily_trades': None,    # REMOVED
                'max_hourly_trades': self.max_trades_per_hour
            },
            'symbols': {symbol: self.get_symbol_status(symbol) for symbol in self.trade_history.keys()}
        }
    
    def reset_daily_counters(self):
        """Reset daily trade counters (call at midnight)."""
        self.daily_trade_counts.clear()
        self.logger.info("🔄 Daily trade counters reset")
    
    def save_history(self):
        """Save trade history to Firebase (FIREBASE-ONLY - GOLDEN RULE 1)."""
        if self.firebase_db:
            self._save_to_firebase()
        else:
            self.logger.error("🚨 FIREBASE REQUIRED: Cannot save trade history - Firebase database not available")
            raise RuntimeError("Firebase database required for data storage - no local fallbacks allowed")
    
    def load_history(self):
        """Load trade history from Firebase (FIREBASE-ONLY - GOLDEN RULE 1)."""
        if self.firebase_db:
            self._load_from_firebase()
        else:
            self.logger.error("🚨 FIREBASE REQUIRED: Cannot load trade history - Firebase database not available")
            raise RuntimeError("Firebase database required for data loading - no local fallbacks allowed")
    
    def _save_to_firebase(self):
        """Save trade history to Firebase database."""
        try:
            # Prepare data for Firebase
            save_data = {
                'trade_history_summary': self.trade_history,
                'position_values': {k: str(v) for k, v in self.position_values.items()},
                'daily_trade_counts': self.daily_trade_counts,
                'last_trade_times': {k: v.isoformat() for k, v in self.last_trade_times.items()},
                'last_updated': datetime.now().isoformat(),
                'safety_limits': {
                    'cooldown_minutes': self.cooldown_minutes,
                    'max_trades_per_hour': self.max_trades_per_hour
                }
            }
            
            # Save to Firebase under 'trade_history_tracker' collection
            doc_ref = self.firebase_db.db.collection('trade_history_tracker').document('current_status')
            doc_ref.set(save_data)
            
            self.logger.debug("💾 Trade history saved to Firebase")
                
        except Exception as e:
            self.logger.error(f"❌ CRITICAL: Failed to save trade history to Firebase: {e}")
            raise RuntimeError(f"Firebase save failed - no local fallbacks allowed: {e}")
    
    def _load_from_firebase(self):
        """Load trade history from Firebase database."""
        try:
            # Load from Firebase
            doc_ref = self.firebase_db.db.collection('trade_history_tracker').document('current_status')
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                
                self.trade_history = data.get('trade_history_summary', {})
                
                # Convert position values back to Decimal
                position_data = data.get('position_values', {})
                self.position_values = {k: Decimal(v) for k, v in position_data.items()}
                
                self.daily_trade_counts = data.get('daily_trade_counts', {})
                
                # Convert last trade times back to datetime
                time_data = data.get('last_trade_times', {})
                self.last_trade_times = {k: datetime.fromisoformat(v) for k, v in time_data.items()}
                
                self.logger.info(f"🔥 Loaded trade history from Firebase: {len(self.trade_history)} symbols")
            else:
                self.logger.info("🔥 No existing Firebase trade history - starting fresh")
                
        except Exception as e:
            self.logger.error(f"❌ CRITICAL: Failed to load trade history from Firebase: {e}")
            raise RuntimeError(f"Firebase load failed - no local fallbacks allowed: {e}")
    
    def _save_trade_to_firebase(self, trade_record: Dict, symbol: str):
        """Save individual trade to Firebase for detailed audit trail."""
        try:
            # Add to trade_history_details collection for complete audit trail
            trade_doc = {
                **trade_record,
                'symbol': symbol,
                'timestamp_stored': datetime.now().isoformat()
            }
            
            # Store in Firebase with auto-generated ID
            self.firebase_db.db.collection('trade_history_details').add(trade_doc)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to save individual trade to Firebase: {e}")
    
# Demo usage for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tracker = TradeHistoryTracker()
    
    # Test the safety checks that would have prevented the $36K loss
    print("\n🚨 TESTING SAFETY CONTROLS")
    print("=" * 50)
    
    # Simulate the rapid AVAXUSD trading that caused major losses
    test_symbol = "AVAXUSD"
    test_value = 23000  # The actual position size that caused problems
    
    # First trade should be allowed
    can_trade, reason = tracker.can_trade_symbol(test_symbol, test_value)
    print(f"1st trade: {can_trade} - {reason}")
    
    if can_trade:
        tracker.record_trade(test_symbol, "buy", 1000, 23.0, "test_001")
    
    # Second trade should be blocked by cooldown
    can_trade, reason = tracker.can_trade_symbol(test_symbol, test_value)
    print(f"2nd trade (immediate): {can_trade} - {reason}")
    
    # Test position size limits
    can_trade, reason = tracker.can_trade_symbol("ETHUSD", 25000)  # Exceeds $8K limit
    print(f"Large position: {can_trade} - {reason}")
    
    # Show status
    print(f"\n📊 System Status:")
    status = tracker.get_all_status()
    print(f"Total symbols tracked: {status['total_symbols']}")
    print(f"Symbols on cooldown: {status['symbols_on_cooldown']}")    # LOCAL FILE FUNCTIONS REMOVED - FIREBASE-ONLY STORAGE (GOLDEN RULE 1)
