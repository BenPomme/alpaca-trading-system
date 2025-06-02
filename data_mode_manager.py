#!/usr/bin/env python3
"""
Data Mode Manager - Dual Mode Architecture

Manages trading system behavior based on data subscription level:
- Free Account: Optimized for 15-minute delayed data
- Paid Account: Optimized for real-time data

Automatically adjusts strategies, cycle timing, and risk parameters
based on available data freshness.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum


class DataMode(Enum):
    """Available data modes"""
    DELAYED = "delayed"      # 15-minute delayed data (free account)
    REALTIME = "realtime"    # Real-time data (paid account)


class SubscriptionLevel(Enum):
    """Alpaca subscription levels"""
    FREE = "free"           # Basic plan - 15 minute delayed
    UNLIMITED = "unlimited"  # Paid plan - real-time data


class DataModeManager:
    """
    Manages trading system configuration based on data subscription level.
    
    Automatically optimizes strategies, timing, and risk parameters for
    either delayed data (free) or real-time data (paid) trading.
    """
    
    def __init__(self, subscription_level: str = "auto", logger=None):
        """
        Initialize data mode manager.
        
        Args:
            subscription_level: 'free', 'unlimited', or 'auto' to detect
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.subscription_level = self._determine_subscription_level(subscription_level)
        self.data_mode = self._determine_data_mode()
        
        # Configure system based on detected mode
        self.config = self._initialize_configuration()
        
        self.logger.info(f"🔧 Data Mode Manager initialized:")
        self.logger.info(f"   Subscription: {self.subscription_level.value}")
        self.logger.info(f"   Data Mode: {self.data_mode.value}")
        self.logger.info(f"   Cycle Delay: {self.config['cycle_delay']}s")
        
    def _determine_subscription_level(self, level: str) -> SubscriptionLevel:
        """Determine subscription level from environment or parameter"""
        
        if level != "auto":
            if level.lower() in ["free", "basic"]:
                return SubscriptionLevel.FREE
            elif level.lower() in ["unlimited", "paid", "pro"]:
                return SubscriptionLevel.UNLIMITED
        
        # Auto-detect from environment variables
        realtime_enabled = os.getenv('REALTIME_DATA_ENABLED', '').lower() == 'true'
        subscription_env = os.getenv('ALPACA_SUBSCRIPTION_LEVEL', 'free').lower()
        
        if realtime_enabled or subscription_env in ['unlimited', 'paid', 'pro']:
            return SubscriptionLevel.UNLIMITED
        else:
            return SubscriptionLevel.FREE
    
    def _determine_data_mode(self) -> DataMode:
        """Determine data mode based on subscription level"""
        if self.subscription_level == SubscriptionLevel.FREE:
            return DataMode.DELAYED
        else:
            return DataMode.REALTIME
    
    def _initialize_configuration(self) -> Dict[str, Any]:
        """Initialize configuration based on data mode"""
        
        if self.data_mode == DataMode.DELAYED:
            return self._get_delayed_data_config()
        else:
            return self._get_realtime_data_config()
    
    def _get_delayed_data_config(self) -> Dict[str, Any]:
        """Configuration optimized for 15-minute delayed data"""
        return {
            'cycle_delay': 900,  # 15 minutes - match data freshness
            'min_hold_time_hours': 4,  # Minimum 4-hour holds
            'max_daily_trades': 8,  # Fewer, higher-quality trades
            'position_size_multiplier': 0.8,  # 20% smaller positions for safety
            'stop_loss_buffer': 1.5,  # 50% wider stops for price gaps
            'profit_target_buffer': 1.3,  # 30% wider profit targets
            'quote_staleness_threshold': 1200,  # 20 minutes acceptable
            'preferred_timeframes': ['4H', '1D', '1W'],
            'strategy_focus': 'swing_trading',
            'risk_level': 'conservative',
            'data_warning_threshold': 1800,  # Warn if older than 30 minutes
            'execution_buffer_pct': 2.0,  # 2% execution buffer for delays
            'strategies': {
                'crypto': {
                    'enabled_strategies': ['daily_momentum', 'weekly_breakouts', 'end_of_day_analysis'],
                    'disabled_strategies': ['scalping', 'high_frequency', 'tick_analysis'],
                    'timeframes': ['4H', '1D'],
                    'confidence_threshold': 0.7,  # Higher confidence for delayed data
                    'min_profit_target': 0.08  # 8% minimum for longer holds
                },
                'stocks': {
                    'enabled_strategies': ['daily_trends', 'weekly_momentum', 'earnings_plays'],
                    'disabled_strategies': ['intraday_scalping', 'minute_breakouts'],
                    'timeframes': ['1D', '1W'],
                    'confidence_threshold': 0.75,
                    'min_profit_target': 0.06  # 6% minimum
                },
                'options': {
                    'enabled_strategies': ['daily_volatility', 'weekly_expiry', 'earnings_straddles'],
                    'disabled_strategies': ['intraday_gamma', 'scalping_theta'],
                    'timeframes': ['1D', '1W'],
                    'confidence_threshold': 0.8,
                    'min_profit_target': 0.15  # 15% minimum for options
                }
            }
        }
    
    def _get_realtime_data_config(self) -> Dict[str, Any]:
        """Configuration optimized for real-time data"""
        return {
            'cycle_delay': 60,  # 1 minute cycles
            'min_hold_time_hours': 0.25,  # 15-minute minimum holds
            'max_daily_trades': 50,  # More frequent trading
            'position_size_multiplier': 1.0,  # Full position sizing
            'stop_loss_buffer': 1.0,  # Normal stops
            'profit_target_buffer': 1.0,  # Normal targets
            'quote_staleness_threshold': 120,  # 2 minutes max staleness
            'preferred_timeframes': ['1m', '5m', '15m', '1H'],
            'strategy_focus': 'intraday_trading',
            'risk_level': 'aggressive',
            'data_warning_threshold': 300,  # Warn if older than 5 minutes
            'execution_buffer_pct': 0.5,  # 0.5% execution buffer
            'strategies': {
                'crypto': {
                    'enabled_strategies': ['momentum_scalping', 'breakout_trading', 'mean_reversion'],
                    'disabled_strategies': [],
                    'timeframes': ['1m', '5m', '15m'],
                    'confidence_threshold': 0.6,
                    'min_profit_target': 0.03  # 3% minimum for quick trades
                },
                'stocks': {
                    'enabled_strategies': ['intraday_momentum', 'breakout_scalping', 'gap_trading'],
                    'disabled_strategies': [],
                    'timeframes': ['1m', '5m', '15m'],
                    'confidence_threshold': 0.65,
                    'min_profit_target': 0.02  # 2% minimum
                },
                'options': {
                    'enabled_strategies': ['gamma_scalping', 'theta_decay', 'volatility_arbitrage'],
                    'disabled_strategies': [],
                    'timeframes': ['1m', '5m', '15m'],
                    'confidence_threshold': 0.7,
                    'min_profit_target': 0.10  # 10% minimum
                }
            }
        }
    
    def get_cycle_delay(self) -> int:
        """Get appropriate cycle delay for current data mode"""
        return self.config['cycle_delay']
    
    def get_strategy_config(self, module_name: str) -> Dict[str, Any]:
        """Get strategy configuration for specific module"""
        return self.config['strategies'].get(module_name, {})
    
    def is_strategy_enabled(self, module_name: str, strategy_name: str) -> bool:
        """Check if specific strategy is enabled for current data mode"""
        module_config = self.get_strategy_config(module_name)
        enabled = module_config.get('enabled_strategies', [])
        disabled = module_config.get('disabled_strategies', [])
        
        if strategy_name in disabled:
            return False
        if enabled and strategy_name not in enabled:
            return False
        return True
    
    def get_position_sizing_multiplier(self) -> float:
        """Get position sizing multiplier for current data mode"""
        return self.config['position_size_multiplier']
    
    def get_risk_parameters(self) -> Dict[str, float]:
        """Get risk parameters adjusted for current data mode"""
        return {
            'stop_loss_buffer': self.config['stop_loss_buffer'],
            'profit_target_buffer': self.config['profit_target_buffer'],
            'max_daily_trades': self.config['max_daily_trades'],
            'execution_buffer_pct': self.config['execution_buffer_pct']
        }
    
    def is_quote_acceptable(self, quote_age_seconds: float) -> bool:
        """Check if quote age is acceptable for current data mode"""
        threshold = self.config['quote_staleness_threshold']
        return quote_age_seconds <= threshold
    
    def should_warn_about_staleness(self, quote_age_seconds: float) -> bool:
        """Check if we should warn about quote staleness"""
        warning_threshold = self.config['data_warning_threshold']
        return quote_age_seconds > warning_threshold
    
    def get_acceptable_timeframes(self) -> List[str]:
        """Get list of acceptable timeframes for current data mode"""
        return self.config['preferred_timeframes']
    
    def format_data_mode_status(self) -> str:
        """Get formatted status string for logging"""
        status = f"""
📊 DATA MODE STATUS:
   Subscription: {self.subscription_level.value.upper()}
   Data Mode: {self.data_mode.value.upper()}
   Cycle Delay: {self.config['cycle_delay']}s
   Strategy Focus: {self.config['strategy_focus']}
   Risk Level: {self.config['risk_level']}
   Max Daily Trades: {self.config['max_daily_trades']}
   Min Hold Time: {self.config['min_hold_time_hours']}h
   Quote Staleness OK: <{self.config['quote_staleness_threshold']}s
        """
        return status.strip()
    
    def upgrade_to_realtime(self) -> bool:
        """
        Upgrade to real-time data mode.
        
        Returns:
            True if upgrade successful, False if already real-time
        """
        if self.data_mode == DataMode.REALTIME:
            self.logger.info("⚠️ Already in real-time data mode")
            return False
        
        self.logger.info("🚀 UPGRADING TO REAL-TIME DATA MODE")
        self.subscription_level = SubscriptionLevel.UNLIMITED
        self.data_mode = DataMode.REALTIME
        self.config = self._get_realtime_data_config()
        
        self.logger.info("✅ Upgrade complete - system now optimized for real-time data")
        self.logger.info(self.format_data_mode_status())
        return True
    
    def downgrade_to_delayed(self) -> bool:
        """
        Downgrade to delayed data mode.
        
        Returns:
            True if downgrade successful, False if already delayed
        """
        if self.data_mode == DataMode.DELAYED:
            self.logger.info("⚠️ Already in delayed data mode")
            return False
        
        self.logger.info("📉 DOWNGRADING TO DELAYED DATA MODE")
        self.subscription_level = SubscriptionLevel.FREE
        self.data_mode = DataMode.DELAYED
        self.config = self._get_delayed_data_config()
        
        self.logger.info("✅ Downgrade complete - system now optimized for delayed data")
        self.logger.info(self.format_data_mode_status())
        return True
    
    def get_upgrade_recommendation(self, monthly_profit: float) -> Dict[str, Any]:
        """
        Get recommendation on whether to upgrade based on profitability.
        
        Args:
            monthly_profit: Current monthly profit in dollars
            
        Returns:
            Dictionary with upgrade recommendation and analysis
        """
        upgrade_cost = 99  # Monthly cost for unlimited data
        
        if self.data_mode == DataMode.REALTIME:
            return {
                'recommended': False,
                'reason': 'Already using real-time data',
                'current_mode': 'realtime'
            }
        
        profit_after_cost = monthly_profit - upgrade_cost
        roi_improvement_estimate = 1.5  # Estimate 50% improvement with real-time
        estimated_new_profit = monthly_profit * roi_improvement_estimate
        estimated_profit_after_cost = estimated_new_profit - upgrade_cost
        
        # Recommend upgrade if estimated profit after cost > current profit and profit > minimum threshold
        should_upgrade = estimated_profit_after_cost > monthly_profit and monthly_profit > 120
        
        return {
            'recommended': should_upgrade,
            'current_monthly_profit': monthly_profit,
            'upgrade_cost_monthly': upgrade_cost,
            'estimated_new_profit': estimated_new_profit,
            'estimated_profit_after_cost': estimated_profit_after_cost,
            'break_even_profit': upgrade_cost / (roi_improvement_estimate - 1),
            'reason': self._get_upgrade_reason(should_upgrade, monthly_profit, upgrade_cost),
            'current_mode': 'delayed'
        }
    
    def _get_upgrade_reason(self, should_upgrade: bool, profit: float, cost: float) -> str:
        """Generate upgrade recommendation reason"""
        if should_upgrade:
            return f"Monthly profit ${profit:.0f} > break-even ${cost:.0f}. Real-time data should increase profits."
        elif profit < cost:
            return f"Monthly profit ${profit:.0f} < upgrade cost ${cost:.0f}. Build profitability first."
        else:
            return f"Marginal benefit. Consider upgrade when profit consistently > ${cost*1.5:.0f}/month."


# Convenience functions
def get_data_mode_manager(subscription_level: str = "auto") -> DataModeManager:
    """Get configured data mode manager instance"""
    return DataModeManager(subscription_level)


def is_delayed_data_mode() -> bool:
    """Check if system is currently in delayed data mode"""
    manager = get_data_mode_manager()
    return manager.data_mode == DataMode.DELAYED


def get_optimized_cycle_delay() -> int:
    """Get cycle delay optimized for current data mode"""
    manager = get_data_mode_manager()
    return manager.get_cycle_delay()


def should_enable_strategy(module_name: str, strategy_name: str) -> bool:
    """Check if strategy should be enabled for current data mode"""
    manager = get_data_mode_manager()
    return manager.is_strategy_enabled(module_name, strategy_name)