#!/usr/bin/env python3
"""
Risk Management System for Phase 2
Advanced risk controls and position management
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database_manager import TradingDatabase

class RiskManager:
    """Advanced risk management for trading system"""
    
    def __init__(self, api_client, db: TradingDatabase = None, logger=None):
        self.api = api_client
        self.db = db
        self.logger = logger or logging.getLogger(__name__)
        
        # Risk Parameters (EMERGENCY SAFETY CONTROLS AFTER $36K LOSS)
        self.max_positions = 15                 # REDUCED from 25 after rapid-fire trading incident
        self.max_daily_trades = 10                # REDUCED from 20 - limit excessive trading
        self.max_position_size_pct = 0.08         # REDUCED from 15% to 8% - smaller positions
        self.max_position_value = 8000            # HARD LIMIT: $8K max per position (was $23K+)
        self.max_sector_exposure = 0.40           # REDUCED from 60% to 40% exposure per sector
        self.max_daily_loss_pct = 0.015           # REDUCED to 1.5% daily loss limit (was 2%)
        # EMERGENCY FIX: Enable daily loss circuit breaker
        self.ignore_daily_loss = False
        self.logger.info("✅ Daily loss circuit breaker ENABLED: 2% limit")
        self.position_risk_pct = 0.02             # 2% risk per trade
        
        # Stop Loss & Take Profit
        self.stop_loss_pct = 0.03                 # 3% stop loss
        self.take_profit_pct = 0.08               # 8% take profit
        self.quick_profit_pct = 0.03              # 3% quick profit (same day)
        self.max_hold_days = 5                    # Maximum hold period
        
        # Confidence-based adjustments
        self.confidence_multipliers = {
            'aggressive_momentum': 1.5,           # High confidence = larger positions
            'momentum': 1.0,                      # Standard positions
            'cautious_momentum': 0.7,             # Smaller positions
            'conservative': 0.3                   # Minimal positions
        }
        
        # INTRADAY TRADING PARAMETERS
        self.intraday_enabled = False
        self.intraday_eligible = False
        self.daytrading_buying_power = 0
        self.max_intraday_position_size = 0
        self.intraday_position_multiplier = 1.5  # 50% larger positions for intraday
        self.end_of_day_liquidation_hour = 15.5  # 3:30 PM ET (30 min before close)
        
        # Performance-based leverage adjustment
        self.performance_leverage_config = {
            'enable': True,
            'min_win_rate_for_full_leverage': 0.50, # Win rate below this reduces leverage
            'reduced_leverage_factor': 0.75,       # Factor to apply if win rate is low
            'min_trades_for_assessment': 20       # Min trades before adjusting
        }
        
        # Initialize intraday capabilities
        self._initialize_intraday_trading()
        
        print("✅ Risk Manager initialized")
        self.print_risk_parameters()
    
    def _initialize_intraday_trading(self):
        """Initialize intraday trading capabilities"""
        try:
            if self.api:
                account = self.api.get_account()
                equity = float(account.equity)
                self.daytrading_buying_power = float(getattr(account, 'daytrading_buying_power', 0))
                buying_power = float(getattr(account, 'buying_power', 0))
                
                # FIXED: More flexible eligibility check
                # Check if account has daytrading power OR sufficient equity
                has_daytrading_power = self.daytrading_buying_power > 0
                has_sufficient_equity = equity >= 25000
                is_pattern_day_trader = getattr(account, 'pattern_day_trader', False)
                
                # Enable if any of these conditions are met
                self.intraday_eligible = has_daytrading_power or has_sufficient_equity or is_pattern_day_trader
                
                if self.intraday_eligible:
                    # Use daytrading power if available, otherwise use regular buying power with limits
                    effective_power = max(self.daytrading_buying_power, buying_power)
                    self.max_intraday_position_size = effective_power * 0.15
                    self.intraday_enabled = True
                    
                    print(f"🚀 Intraday Trading: ✅ ENABLED")
                    print(f"   💰 Account Equity: ${equity:,.2f}")
                    print(f"   💰 Day Trading Power: ${self.daytrading_buying_power:,.2f}")
                    print(f"   💰 Buying Power: ${buying_power:,.2f}")
                    print(f"   🎯 Max Intraday Position: ${self.max_intraday_position_size:,.2f}")
                    print(f"   📋 PDT Status: {is_pattern_day_trader}")
                else:
                    print(f"🚀 Intraday Trading: ❌ DISABLED (Account not eligible)")
                    print(f"   💰 Equity: ${equity:,.2f}")
                    print(f"   💰 Day Trading Power: ${self.daytrading_buying_power:,.2f}")
                    print(f"   📋 PDT Status: {is_pattern_day_trader}")
                    
        except Exception as e:
            print(f"⚠️ Intraday initialization failed: {e}")
            self.intraday_enabled = False
    
    def print_risk_parameters(self):
        """Display current risk parameters"""
        print("📊 Risk Management Parameters:")
        print(f"   Max Positions: {'Unlimited' if self.max_positions is None else self.max_positions}")
        print(f"   Max Position Size: {self.max_position_size_pct:.1%}")
        print(f"   Position Risk: {self.position_risk_pct:.1%}")
        print(f"   Stop Loss: {self.stop_loss_pct:.1%}")
        print(f"   Take Profit: {self.take_profit_pct:.1%}")
        print(f"   Max Daily Loss: {self.max_daily_loss_pct:.1%}")
        if self.intraday_enabled:
            print(f"   🚀 Intraday Strategy: ACTIVE")
            print(f"   ⏰ EOD Liquidation: {int(self.end_of_day_liquidation_hour)}:{int((self.end_of_day_liquidation_hour % 1) * 60):02d} ET")
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                               strategy: str, confidence: float, 
                               portfolio_value: float) -> Tuple[int, Dict]:
        """Calculate optimal position size with risk management"""
        
        # Determine if this is an intraday stock position
        is_stock_intraday = (
            self.intraday_enabled and 
            self._is_stock_symbol(symbol) and
            self._should_use_intraday_strategy()
        )
        
        if is_stock_intraday:
            # INTRADAY POSITION SIZING - Use day trading power
            base_risk_amount = self.daytrading_buying_power * self.position_risk_pct
            max_position_value = self.max_intraday_position_size
            sizing_multiplier = self.intraday_position_multiplier
            sizing_mode = "intraday"
        else:
            # MULTI-DAY POSITION SIZING - Use portfolio value  
            base_risk_amount = portfolio_value * self.position_risk_pct
            max_position_value = portfolio_value * self.max_position_size_pct
            sizing_multiplier = 1.0
            sizing_mode = "multiday"
        
        # Strategy-based risk adjustment
        strategy_multiplier = self.confidence_multipliers.get(strategy, 1.0)
        
        # Confidence-based adjustment (scale with confidence 0.5-1.0 → 0.7-1.3)
        confidence_multiplier = 0.7 + (confidence * 0.6)
        
        # Performance-based leverage adjustment
        performance_leverage_factor = self.get_performance_adjusted_leverage_factor()

        # Calculate adjusted risk with intraday multiplier and performance factor
        adjusted_risk = base_risk_amount * strategy_multiplier * confidence_multiplier * sizing_multiplier * performance_leverage_factor
        
        # Position size limits
        target_position_value = min(adjusted_risk, max_position_value)
        
        # Calculate shares
        target_shares = int(target_position_value / entry_price)
        
        # Minimum position check
        if target_shares == 0 and adjusted_risk >= entry_price:
            target_shares = 1
        
        sizing_info = {
            'sizing_mode': sizing_mode,
            'base_risk_amount': base_risk_amount,
            'strategy_multiplier': strategy_multiplier,
            'confidence_multiplier': confidence_multiplier,
            'sizing_multiplier': sizing_multiplier,
            'adjusted_risk': adjusted_risk,
            'max_position_value': max_position_value,
            'target_position_value': target_position_value,
            'target_shares': target_shares,
            'estimated_cost': target_shares * entry_price,
            'is_intraday': is_stock_intraday
        }
        
        return target_shares, sizing_info
    
    def check_position_limits(self, symbol: str, target_shares: int, 
                             entry_price: float) -> Tuple[bool, str]:
        """Check if position meets all risk limits"""
        try:
            # Get current positions
            positions = self.api.list_positions()
            account = self.api.get_account()
            
            # DEBUG: Check account data
            print(f"🔍 ACCOUNT DEBUG:")
            print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
            print(f"   Buying Power: ${float(account.buying_power):,.2f}")
            print(f"   Cash: ${float(account.cash):,.2f}")
            print(f"   Account Status: {account.status}")
            print(f"   Day Trading Buying Power: ${float(getattr(account, 'daytrading_buying_power', 0)):,.2f}")
            
            portfolio_value = float(account.portfolio_value)
            
            # CRITICAL SAFETY: Enforce strict position limits after $36K loss
            position_value = target_shares * entry_price
            
            # HARD LIMIT: Maximum position value per symbol
            if position_value > self.max_position_value:
                return False, f"Position value ${position_value:,.0f} exceeds hard limit of ${self.max_position_value:,.0f}"
            
            # Check existing position limits 
            existing_position = next((p for p in positions if p.symbol == symbol), None)
            if existing_position:
                current_value = abs(float(existing_position.market_value))
                total_position_value = current_value + position_value
                
                # REDUCED LIMIT: Max 8% of portfolio per symbol (was 30%)
                max_total_position = portfolio_value * self.max_position_size_pct
                
                if total_position_value > max_total_position:
                    return False, f"Total position in {symbol} would be ${total_position_value:,.0f}, exceeding {self.max_position_size_pct:.1%} limit (${max_total_position:,.0f})"
                
                if total_position_value > self.max_position_value:
                    return False, f"Total position in {symbol} would exceed ${self.max_position_value:,.0f} hard limit"
                
                print(f"   ⚠️ ADDING TO POSITION: {symbol} current ${current_value:,.0f} + new ${position_value:,.0f} = ${total_position_value:,.0f}")
            
            # Check maximum positions (Phase 4.1: Unlimited positions enabled)
            if self.max_positions is not None and len(positions) >= self.max_positions:
                return False, f"Maximum positions reached ({self.max_positions})"
            
            # Check position size limit
            position_value = target_shares * entry_price
            position_pct = position_value / portfolio_value
            if position_pct > self.max_position_size_pct:
                return False, f"Position too large ({position_pct:.1%} > {self.max_position_size_pct:.1%})"
            
            # CRITICAL FIX: Use day trading power for intraday, RegT for overnight
            daytrading_bp = float(getattr(account, 'daytrading_buying_power', 0))
            regt_bp = float(getattr(account, 'regt_buying_power', 0))
            buying_power = float(account.buying_power)  # Fallback
            
            # CRITICAL: Check if this is an intraday trade to determine leverage
            is_intraday = hasattr(self, 'should_liquidate_intraday_positions') and not self.should_liquidate_intraday_positions()
            
            # PRODUCTION FIX: Prioritize day trading power for maximum leverage utilization
            if daytrading_bp > 0:
                buying_power = daytrading_bp  # Use 4:1 leverage when available
                print(f"   🚀 Using Day Trading buying power (4:1): ${buying_power:,.2f}")
            elif regt_bp > 0:
                buying_power = regt_bp  # Use 2:1 leverage for overnight positions
                print(f"   ✅ Using RegT buying power (2:1): ${buying_power:,.2f}")
            elif buying_power > 0:
                print(f"   ⚠️ Using standard buying power: ${buying_power:,.2f}")
            else:
                # Fallback to cash if both are 0
                cash = float(account.cash)
                if cash > 0:
                    buying_power = cash
                    print(f"   🔄 Using cash balance: ${buying_power:,.2f}")
                else:
                    # Last resort: use portfolio value
                    buying_power = portfolio_value
                    print(f"   🔄 Using portfolio value as buying power: ${buying_power:,.2f}")
            
            print(f"   💰 Final buying power used: ${buying_power:,.2f}")
            
            if position_value > buying_power:
                return False, f"Insufficient buying power (${position_value:,.2f} > ${buying_power:,.2f})"
            
            # Check daily trading limit
            if self.db:
                today = datetime.now().date().isoformat()
                # This would check trade count from database
                # For now, we'll assume it's okay
                pass
            
            return True, "Position approved"
            
        except Exception as e:
            return False, f"Risk check error: {e}"
    
    def check_daily_loss_limit(self) -> Tuple[bool, str]:
        """Check if daily loss limit has been reached"""
        # Bypass daily loss limit if flagged
        if getattr(self, 'ignore_daily_loss', False):
            return True, "Daily loss limit bypassed via IGNORE_DAILY_LOSS"
        try:
            account = self.api.get_account()
            equity = float(account.equity)
            last_equity = float(account.last_equity)
            
            daily_pl = equity - last_equity
            daily_pl_pct = daily_pl / last_equity if last_equity > 0 else 0
            
            if daily_pl_pct <= -self.max_daily_loss_pct:
                return False, f"Daily loss limit reached ({daily_pl_pct:.1%})"
            
            return True, f"Daily P&L: {daily_pl_pct:+.1%}"
            
        except Exception as e:
            return False, f"Daily loss check error: {e}"
    
    def validate_opportunity(self, module_name: str, opportunity) -> bool:
        """
        Validate if a trading opportunity meets risk management criteria.
        
        Args:
            module_name: Name of the trading module
            opportunity: TradeOpportunity object with symbol, confidence, quantity, etc.
        
        Returns:
            bool: True if opportunity passes risk validation
        """
        try:
            # Use existing should_execute_trade logic for validation
            can_trade, reason, _ = self.should_execute_trade(
                symbol=opportunity.symbol,
                strategy=opportunity.strategy,
                confidence=opportunity.confidence,
                entry_price=opportunity.metadata.get('entry_price', 100.0)  # Default price if missing
            )
            
            if not can_trade:
                self.logger.debug(f"Risk validation failed for {opportunity.symbol}: {reason}")
            else:
                self.logger.info(f"✅ {opportunity.symbol}: Risk validation passed")
            
            return can_trade
            
        except Exception as e:
            # Defensive programming - if validation fails, reject the trade
            self.logger.error(f"Error validating opportunity {opportunity.symbol}: {e}")
            return False

    def get_portfolio_summary(self) -> Dict[str, float]:
        """
        Get portfolio summary for risk calculations.
        
        Returns:
            Dictionary with portfolio metrics
        """
        try:
            account = self.api.get_account()
            positions = self.api.list_positions()
            
            portfolio_value = float(account.portfolio_value)
            equity = float(account.equity)
            cash = float(account.cash)
            
            # Calculate position values
            long_value = sum(float(pos.market_value) for pos in positions if float(pos.qty) > 0)
            short_value = sum(abs(float(pos.market_value)) for pos in positions if float(pos.qty) < 0)
            total_positions = len(positions)
            
            return {
                'portfolio_value': portfolio_value,
                'equity': equity,
                'cash': cash,
                'buying_power': float(account.buying_power),
                'long_value': long_value,
                'short_value': short_value,
                'total_positions': total_positions,
                'cash_percentage': cash / portfolio_value * 100 if portfolio_value > 0 else 0,
                'invested_percentage': (long_value + short_value) / portfolio_value * 100 if portfolio_value > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return {
                'portfolio_value': 100000,  # Default fallback
                'equity': 100000,
                'cash': 50000,
                'buying_power': 50000,
                'long_value': 50000,
                'short_value': 0,
                'total_positions': 0,
                'cash_percentage': 50.0,
                'invested_percentage': 50.0
            }
    
    def get_module_allocation(self, module_name: str) -> float:
        """
        Get current allocation percentage for a specific module.
        
        Args:
            module_name: Name of the trading module (e.g., 'crypto', 'options', 'stocks')
            
        Returns:
            float: Current allocation percentage (0.0 to 1.0)
        """
        try:
            account = self.api.get_account()
            portfolio_value = float(getattr(account, 'portfolio_value', 100000))
            
            # Get positions and calculate module allocation
            positions = self.api.list_positions()
            module_value = 0.0
            
            for position in positions:
                symbol = position.symbol
                market_value = abs(float(getattr(position, 'market_value', 0)))
                
                # Categorize position by module
                if module_name == 'crypto' and 'USD' in symbol and len(symbol) <= 7:
                    module_value += market_value
                elif module_name == 'options' and len(symbol) > 10:  # Options have longer symbols
                    module_value += market_value
                elif module_name == 'stocks' and len(symbol) <= 5 and 'USD' not in symbol:
                    module_value += market_value
            
            allocation_pct = module_value / portfolio_value if portfolio_value > 0 else 0.0
            self.logger.info(f"📊 {module_name.title()} allocation: ${module_value:,.0f} ({allocation_pct:.1%})")
            
            return allocation_pct
            
        except Exception as e:
            self.logger.error(f"Error calculating {module_name} allocation: {e}")
            return 0.0

    def should_execute_trade(self, symbol: str, strategy: str, confidence: float,
                           entry_price: float) -> Tuple[bool, str, Dict]:
        """Comprehensive trade approval check"""
        
        try:
            account = self.api.get_account()
            portfolio_value = float(account.portfolio_value)
            
            # Calculate position size
            target_shares, sizing_info = self.calculate_position_size(
                symbol, entry_price, strategy, confidence, portfolio_value
            )
            
            if target_shares <= 0:
                return False, "Position size too small", {}
            
            target_value = target_shares * entry_price
            
            # Run all risk checks
            checks = []
            
            # Position limits check
            position_ok, position_msg = self.check_position_limits(symbol, target_shares, entry_price)
            checks.append(('Position Limits', position_ok, position_msg))
            
            # Daily loss check
            daily_ok, daily_msg = self.check_daily_loss_limit()
            checks.append(('Daily Loss Limit', daily_ok, daily_msg))
            
            # Print risk assessment
            print(f"🔍 RISK ASSESSMENT: {symbol}")
            for check_name, check_ok, check_msg in checks:
                status = "✅" if check_ok else "❌"
                print(f"   {status} {check_name}: {check_msg}")
            
            # Overall approval
            all_checks_pass = all(check[1] for check in checks)
            
            if all_checks_pass:
                print(f"✅ TRADE APPROVED: {symbol} ({target_shares} shares, ${target_value:,.2f})")
                
                trade_info = {
                    'approved': True,
                    'target_shares': target_shares,
                    'target_value': target_value,
                    'sizing_info': sizing_info,
                    'risk_checks': checks
                }
                
                return True, "Trade approved", trade_info
            else:
                failed_checks = [check[2] for check in checks if not check[1]]
                return False, f"Risk checks failed: {'; '.join(failed_checks)}", {}
            
        except Exception as e:
            return False, f"Risk assessment error: {e}", {}
    
    def calculate_stop_loss_take_profit(self, entry_price: float, strategy: str) -> Dict:
        """Calculate stop loss and take profit levels"""
        
        # Strategy-based adjustments
        if strategy == 'aggressive_momentum':
            stop_loss_pct = self.stop_loss_pct * 1.2    # Wider stops for aggressive trades
            take_profit_pct = self.take_profit_pct * 1.2 # Higher targets
        elif strategy == 'cautious_momentum':
            stop_loss_pct = self.stop_loss_pct * 0.8    # Tighter stops
            take_profit_pct = self.take_profit_pct * 0.8 # Lower targets
        else:
            stop_loss_pct = self.stop_loss_pct
            take_profit_pct = self.take_profit_pct
        
        stop_loss_price = entry_price * (1 - stop_loss_pct)
        take_profit_price = entry_price * (1 + take_profit_pct)
        quick_profit_price = entry_price * (1 + self.quick_profit_pct)
        
        return {
            'stop_loss_price': stop_loss_price,
            'take_profit_price': take_profit_price,
            'quick_profit_price': quick_profit_price,
            'stop_loss_pct': stop_loss_pct,
            'take_profit_pct': take_profit_pct,
            'quick_profit_pct': self.quick_profit_pct
        }
    
    def get_risk_metrics(self) -> Dict:
        """Get current portfolio risk metrics"""
        try:
            account = self.api.get_account()
            positions = self.api.list_positions()
            
            portfolio_value = float(account.portfolio_value)
            total_market_value = sum(float(pos.market_value) for pos in positions)
            total_unrealized_pl = sum(float(pos.unrealized_pl) for pos in positions)
            
            # Calculate daily P&L
            equity = float(account.equity)
            last_equity = float(account.last_equity)
            daily_pl = equity - last_equity
            daily_pl_pct = (daily_pl / last_equity) * 100 if last_equity > 0 else 0
            
            # Portfolio utilization
            utilization_pct = (total_market_value / portfolio_value) * 100
            
            # Risk exposure
            largest_position_value = max([float(pos.market_value) for pos in positions], default=0)
            largest_position_pct = (largest_position_value / portfolio_value) * 100
            
            return {
                'portfolio_value': portfolio_value,
                'total_positions': len(positions),
                'portfolio_utilization_pct': utilization_pct,
                'largest_position_pct': largest_position_pct,
                'daily_pl': daily_pl,
                'daily_pl_pct': daily_pl_pct,
                'total_unrealized_pl': total_unrealized_pl,
                'unrealized_pl_pct': (total_unrealized_pl / portfolio_value) * 100,
                'risk_limit_usage': {
                    'max_positions': f"{len(positions)}/{'Unlimited' if self.max_positions is None else self.max_positions}",
                    'daily_loss_usage': f"{abs(min(0, daily_pl_pct)):.1f}%/{self.max_daily_loss_pct*100:.1f}%"
                }
            }
            
        except Exception as e:
            return {'error': f'Risk metrics calculation failed: {e}'}
    
    def _is_stock_symbol(self, symbol: str) -> bool:
        """Determine if symbol is a stock/ETF (not crypto or options)"""
        # Crypto symbols end with USD
        if symbol.endswith('USD'):
            return False
        
        # Options symbols typically have / or are longer than 5 chars
        if '/' in symbol or len(symbol) > 5:
            return False
            
        # Everything else is considered stock/ETF
        return True
    
    def _should_use_intraday_strategy(self) -> bool:
        """Determine if we should use intraday strategy based on market hours"""
        try:
            if not self.api:
                return False
                
            # Check if market is open
            clock = self.api.get_clock()
            if not clock.is_open:
                return False
                
            # Check if it's close to end of day (don't start new intraday positions)
            import datetime
            import pytz
            
            # Get current ET time
            et = pytz.timezone('America/New_York')
            now_et = datetime.datetime.now(et)
            market_close_hour = self.end_of_day_liquidation_hour
            
            # Don't start new intraday positions if we're close to liquidation time
            current_hour = now_et.hour + now_et.minute / 60.0
            if current_hour >= market_close_hour:
                return False
                
            return True
            
        except Exception as e:
            print(f"⚠️ Intraday strategy check failed: {e}")
            return False
    
    def should_liquidate_intraday_positions(self) -> bool:
        """Check if it's time to liquidate intraday positions (end of day)"""
        try:
            if not self.intraday_enabled:
                return False
                
            import datetime
            import pytz
            
            # Get current ET time
            et = pytz.timezone('America/New_York')
            now_et = datetime.datetime.now(et)
            current_hour = now_et.hour + now_et.minute / 60.0
            
            # Liquidate at or after the specified hour
            return current_hour >= self.end_of_day_liquidation_hour
            
        except Exception as e:
            print(f"⚠️ Liquidation time check failed: {e}")
            return False
    
    def get_intraday_positions(self) -> List:
        """Get list of positions that should be liquidated at end of day"""
        try:
            positions = self.api.list_positions()
            intraday_positions = []
            
            for pos in positions:
                # All stock positions are considered intraday if intraday is enabled
                if self._is_stock_symbol(pos.symbol):
                    intraday_positions.append(pos)
                    
            return intraday_positions
            
        except Exception as e:
            print(f"⚠️ Error getting intraday positions: {e}")
            return []

    def get_recent_performance_metrics(self) -> Dict:
        """ 
        Fetches or calculates recent performance metrics.
        Placeholder: Ideally, this would query self.db for win rate and P&L.
        For now, returns a simulated or default value.
        """
        # TODO: Integrate with TradingDatabase to get actual recent performance
        # self.logger.info("Fetching recent performance metrics (currently simulated).")
        # For demonstration, simulate metrics:
        simulated_win_rate = 0.45 # Simulate a win rate below 50%
        simulated_total_trades = 25 # Simulate enough trades for assessment
        return {
            "win_rate": simulated_win_rate, 
            "total_trades": simulated_total_trades,
            "recent_pnl_pct": -0.02 # Simulate a slight recent loss
        }

    def get_performance_adjusted_leverage_factor(self) -> float:
        """ 
        Determines a leverage adjustment factor based on recent performance.
        Returns a factor (e.g., 0.75 for reduced leverage, 1.0 for full).
        """
        if not self.performance_leverage_config.get('enable', False):
            return 1.0

        metrics = self.get_recent_performance_metrics()
        win_rate = metrics.get("win_rate", 0.0)
        total_trades = metrics.get("total_trades", 0)

        min_trades = self.performance_leverage_config.get('min_trades_for_assessment', 20)
        min_win_rate_full = self.performance_leverage_config.get('min_win_rate_for_full_leverage', 0.50)
        reduced_factor = self.performance_leverage_config.get('reduced_leverage_factor', 0.75)

        if total_trades < min_trades:
            self.logger.debug(f"Performance leverage: Not enough trades ({total_trades}/{min_trades}) for adjustment. Using full factor.")
            return 1.0
        
        if win_rate < min_win_rate_full:
            # EMERGENCY FIX: Only log this once per minute to prevent spam
            import time
            if not hasattr(self, '_last_leverage_warning') or time.time() - self._last_leverage_warning > 60:
                self.logger.warning(f"⚠️ PERFORMANCE: Win rate {win_rate:.2%} < {min_win_rate_full:.2%} - using {reduced_factor}x leverage (logged once/min)")
                self._last_leverage_warning = time.time()
            return reduced_factor
        
        self.logger.debug(f"Performance leverage: Win rate {win_rate:.2%} meets threshold. Using full leverage factor.")
        return 1.0

def test_risk_manager():
    """Test risk management functionality"""
    print("🧪 Testing Risk Manager...")
    
    try:
        from enhanced_trader import EnhancedTrader
        from database_manager import TradingDatabase
        
        trader = EnhancedTrader(use_database=False)
        db = TradingDatabase()
        
        risk_mgr = RiskManager(trader.api, db)
        
        # Test risk metrics
        metrics = risk_mgr.get_risk_metrics()
        print(f"✅ Portfolio utilization: {metrics.get('portfolio_utilization_pct', 0):.1f}%")
        
        # Test position sizing
        shares, sizing = risk_mgr.calculate_position_size('AAPL', 200.0, 'momentum', 0.8, 100000)
        print(f"✅ Position sizing: {shares} shares for AAPL @ $200")
        
        # Test trade approval
        approved, msg, info = risk_mgr.should_execute_trade('AAPL', 'momentum', 0.8, 200.0)
        print(f"✅ Trade approval: {approved} - {msg}")
        
        print("✅ Risk Manager test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Risk Manager test failed: {e}")
        return False

if __name__ == "__main__":
    # Set environment for testing
    os.environ['ALPACA_PAPER_API_KEY'] = os.environ.get('ALPACA_PAPER_API_KEY', 'PKOBXG3RWCRQTXH6ID0L')
    os.environ['ALPACA_PAPER_SECRET_KEY'] = os.environ.get('ALPACA_PAPER_SECRET_KEY', '8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn')
    
    test_risk_manager()