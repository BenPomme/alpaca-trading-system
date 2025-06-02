"""
Base Trading Module Interface and Data Structures

This module defines the core interfaces and data structures for the modular trading architecture.
All trading modules (Options, Crypto, Stocks) inherit from TradingModule and implement the
common interface for analysis, execution, and monitoring.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging
from enum import Enum

# Import ML data collection helpers
from .ml_data_helpers import MLDataCollector, ParameterEffectivenessTracker, MLLearningEventLogger


class TradeAction(Enum):
    BUY = "buy"
    SELL = "sell"


class TradeStatus(Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExitReason(Enum):
    PROFIT_TARGET = "profit_target"
    STOP_LOSS = "stop_loss"
    TIME_LIMIT = "time_limit"
    STRATEGY_SIGNAL = "strategy_signal"
    RISK_MANAGEMENT = "risk_management"
    ML_OPTIMIZATION = "ml_optimization"
    END_OF_DAY = "end_of_day"


@dataclass
class TradeOpportunity:
    """Represents a potential trading opportunity identified by a module"""
    symbol: str
    action: TradeAction
    quantity: float
    confidence: float
    strategy: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Analysis components
    technical_score: float = 0.0
    regime_score: float = 0.0
    pattern_score: float = 0.0
    ml_score: float = 0.0
    
    # Risk parameters
    max_position_size: float = 0.0
    stop_loss_pct: float = 0.0
    profit_target_pct: float = 0.0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class TradeResult:
    """Result of executing a trade opportunity"""
    opportunity: TradeOpportunity
    status: TradeStatus
    order_id: Optional[str] = None
    execution_price: Optional[float] = None
    execution_time: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Performance tracking
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    hold_duration: Optional[float] = None  # hours
    exit_reason: Optional[ExitReason] = None
    
    @property
    def passed(self) -> bool:
        """
        A trade passed if the order was successfully executed (filled).
        This counts all successful order executions regardless of profitability.
        """
        return self.status == TradeStatus.EXECUTED
    
    @property
    def success(self) -> bool:
        """
        A trade is successful (profitable) only if:
        1. Order was executed AND
        2. Trade generated profit (pnl > 0)
        
        For entry trades without P&L data yet, success is False until exit.
        """
        return (self.status == TradeStatus.EXECUTED and 
                self.pnl is not None and 
                self.pnl > 0)


@dataclass
class ModuleConfig:
    """Configuration for a trading module"""
    module_name: str
    enabled: bool = True
    max_allocation_pct: float = 0.0  # 0 = no limit
    min_confidence: float = 0.6
    max_positions: int = 0  # 0 = no limit
    
    # Risk parameters
    default_stop_loss_pct: float = 0.08  # 8%
    default_profit_target_pct: float = 0.15  # 15%
    min_hold_time_hours: float = 2.0
    max_hold_time_hours: float = 168.0  # 1 week
    
    # Module-specific parameters
    custom_params: Dict[str, Any] = field(default_factory=dict)



def calculate_optimal_position_size(self, opportunity, portfolio_value):
    """
    Calculate optimal position size based on:
    - 1-2% risk per trade (research best practice)
    - Portfolio allocation limits
    - Confidence-based sizing
    """
    # Maximum risk per trade: 1.5% of portfolio
    max_risk_per_trade = portfolio_value * 0.015
    
    # Base position size: 2% of portfolio for high confidence trades
    base_position_pct = 0.02 if opportunity.confidence > 0.7 else 0.01
    base_position_size = portfolio_value * base_position_pct
    
    # Adjust for volatility (reduce size for volatile assets)
    if hasattr(opportunity, 'volatility') and opportunity.volatility:
        volatility_adjustment = min(1.5, max(0.5, 1.0 / opportunity.volatility))
        base_position_size *= volatility_adjustment
    
    # Ensure we don't exceed risk limits
    position_size = min(base_position_size, max_risk_per_trade)
    
    # Additional safety: never more than 5% of portfolio in single position
    max_position = portfolio_value * 0.05
    position_size = min(position_size, max_position)
    
    return position_size



def implement_automatic_stop_loss(self, symbol, entry_price, quantity, stop_loss_pct=0.15):
    """
    Implement automatic stop loss for position
    - Default 15% stop loss (research recommended)
    - Trailing stop option for profitable positions
    """
    try:
        stop_price = entry_price * (1 - stop_loss_pct)
        
        # Submit stop loss order
        if hasattr(self, 'api') and self.api:
            time_in_force = 'gtc' if 'USD' in symbol else 'day'
            
            order = self.api.submit_order(
                symbol=symbol,
                qty=abs(quantity),
                side='sell',
                type='stop',
                stop_price=round(stop_price, 2),
                time_in_force=time_in_force
            )
            
            self.logger.info(f"🛡️ Stop loss set for {symbol}: ${stop_price:.2f} ({stop_loss_pct*100:.1f}%)")
            return order.id
        
    except Exception as e:
        self.logger.error(f"❌ Failed to set stop loss for {symbol}: {e}")
        return None

def update_trailing_stop(self, symbol, current_price, entry_price, stop_loss_order_id):
    """
    Update trailing stop loss as position becomes profitable
    """
    try:
        profit_pct = (current_price - entry_price) / entry_price
        
        # If position is 10%+ profitable, tighten stop to break-even
        if profit_pct >= 0.10:
            new_stop_price = entry_price * 1.02  # 2% above entry (small profit)
            
            # Cancel old stop and create new one
            self.api.cancel_order(stop_loss_order_id)
            
            new_order = self.api.submit_order(
                symbol=symbol,
                qty=abs(quantity),
                side='sell', 
                type='stop',
                stop_price=round(new_stop_price, 2),
                time_in_force='gtc' if 'USD' in symbol else 'day'
            )
            
            self.logger.info(f"🎯 Trailing stop updated for {symbol}: ${new_stop_price:.2f}")
            return new_order.id
            
    except Exception as e:
        self.logger.error(f"❌ Failed to update trailing stop for {symbol}: {e}")
    
    return stop_loss_order_id



def implement_profit_taking_strategy(self, position_data):
    """
    Implement systematic profit taking based on research:
    - Take 25% profits at 15% gain
    - Take 50% profits at 25% gain  
    - Take 75% profits at 40% gain
    - Let 25% run with trailing stop
    """
    try:
        symbol = position_data['symbol']
        current_price = position_data['current_price']
        entry_price = position_data['avg_entry_price']
        quantity = abs(position_data['qty'])
        
        profit_pct = (current_price - entry_price) / entry_price
        
        if profit_pct >= 0.40:  # 40% gain - take 75% profits
            sell_qty = quantity * 0.75
            self._execute_partial_profit_taking(symbol, sell_qty, "75% at 40% gain")
            
        elif profit_pct >= 0.25:  # 25% gain - take 50% profits
            sell_qty = quantity * 0.50
            self._execute_partial_profit_taking(symbol, sell_qty, "50% at 25% gain")
            
        elif profit_pct >= 0.15:  # 15% gain - take 25% profits
            sell_qty = quantity * 0.25
            self._execute_partial_profit_taking(symbol, sell_qty, "25% at 15% gain")
        
        return profit_pct
        
    except Exception as e:
        self.logger.error(f"❌ Error in profit taking for {symbol}: {e}")
        return 0

def _execute_partial_profit_taking(self, symbol, quantity, reason):
    """Execute partial profit taking order"""
    try:
        if hasattr(self, 'api') and self.api and quantity > 0:
            time_in_force = 'gtc' if 'USD' in symbol else 'day'
            
            order = self.api.submit_order(
                symbol=symbol,
                qty=quantity,
                side='sell',
                type='market',
                time_in_force=time_in_force
            )
            
            self.logger.info(f"💰 Profit taking executed for {symbol}: {quantity} shares ({reason})")
            return order.id
            
    except Exception as e:
        self.logger.error(f"❌ Failed profit taking for {symbol}: {e}")
        return None


class TradingModule(ABC):
    """
    Abstract base class for all trading modules.
    
    Provides common functionality and enforces consistent interface across
    Options, Crypto, and Stocks modules.
    """
    
    def __init__(self, 
                 config: ModuleConfig,
                 firebase_db,
                 risk_manager,
                 order_executor,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize trading module with injected dependencies.
        
        Args:
            config: Module configuration
            firebase_db: Firebase database interface
            risk_manager: Risk management service
            order_executor: Order execution service  
            logger: Optional logger instance
        """
        self.config = config
        self.firebase_db = firebase_db
        self.risk_manager = risk_manager
        self.order_executor = order_executor
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # Module state
        self._active_positions: Dict[str, Dict] = {}
        self._pending_opportunities: List[TradeOpportunity] = []
        self._performance_metrics: Dict[str, Any] = {}
        
        # ML data collection tools
        self.ml_data_collector = MLDataCollector(self.module_name)
        self.parameter_tracker = ParameterEffectivenessTracker(firebase_db, self.module_name)
        self.ml_event_logger = MLLearningEventLogger(firebase_db, f"{self.module_name}_module")
        
        self.logger.info(f"Initialized {self.module_name} module with ML data collection enabled")
    
    @property
    @abstractmethod
    def module_name(self) -> str:
        """Unique identifier for this module"""
        pass
    
    @property
    @abstractmethod
    def supported_symbols(self) -> List[str]:
        """List of symbols this module can trade"""
        pass
    
    @abstractmethod
    def analyze_opportunities(self) -> List[TradeOpportunity]:
        """
        Analyze market conditions and identify trade opportunities.
        
        Returns:
            List of trade opportunities meeting module criteria
        """
        pass
    
    @abstractmethod
    def execute_trades(self, opportunities: List[TradeOpportunity]) -> List[TradeResult]:
        """
        Execute validated trade opportunities.
        
        Args:
            opportunities: List of opportunities to execute
            
        Returns:
            List of trade results
        """
        pass
    
    @abstractmethod
    def monitor_positions(self) -> List[TradeResult]:
        """
        Monitor existing positions for exit opportunities.
        
        Returns:
            List of exit trade results
        """
        pass
    
    # Common functionality implementations
    
    def validate_opportunity(self, opportunity: TradeOpportunity) -> bool:
        """
        Validate if opportunity meets module and risk criteria.
        
        Args:
            opportunity: Trade opportunity to validate
            
        Returns:
            True if opportunity is valid
        """
        try:
            # Basic validation
            if opportunity.confidence < self.config.min_confidence:
                self.logger.debug(f"Opportunity rejected: confidence {opportunity.confidence} < {self.config.min_confidence}")
                return False
            
            if opportunity.symbol not in self.supported_symbols:
                self.logger.debug(f"Opportunity rejected: {opportunity.symbol} not in supported symbols")
                return False
            
            # Risk management validation
            if not self.risk_manager.validate_opportunity(self.module_name, opportunity):
                self.logger.debug(f"Opportunity rejected by risk manager: {opportunity.symbol}")
                return False
            
            # Portfolio allocation check
            if self.config.max_allocation_pct > 0:
                try:
                    current_allocation = self._calculate_current_allocation()
                    if current_allocation >= self.config.max_allocation_pct:
                        self.logger.debug(f"Opportunity rejected: allocation limit {current_allocation}% >= {self.config.max_allocation_pct}%")
                        return False
                except Exception as e:
                    self.logger.debug(f"Error checking allocation limit: {e}")
                    # Continue validation if allocation check fails
            
            # Position limit check  
            if self.config.max_positions > 0:
                if len(self._active_positions) >= self.config.max_positions:
                    self.logger.debug(f"Opportunity rejected: position limit {len(self._active_positions)} >= {self.config.max_positions}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating opportunity {opportunity.symbol}: {e}")
            return False
    
    def save_opportunity(self, opportunity: TradeOpportunity):
        """Save opportunity to Firebase for ML analysis"""
        try:
            self.firebase_db.save_trade_opportunity(self.module_name, opportunity)
        except Exception as e:
            self.logger.error(f"Error saving opportunity to Firebase: {e}")
    
    def save_result(self, result: TradeResult):
        """Save trade result to Firebase for performance tracking"""
        try:
            self.firebase_db.save_trade_result(self.module_name, result)
            self._update_performance_metrics(result)
        except Exception as e:
            self.logger.error(f"Error saving result to Firebase: {e}")
    
    def get_optimized_parameters(self) -> Dict[str, Any]:
        """Get ML-optimized parameters for this module"""
        try:
            return self.firebase_db.get_module_parameters(self.module_name)
        except Exception as e:
            self.logger.error(f"Error getting optimized parameters: {e}")
            return {}
    
    def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event for other modules or systems to consume"""
        try:
            event_data = {
                'module': self.module_name,
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            self.firebase_db.publish_event(event_type, event_data)
        except Exception as e:
            self.logger.error(f"Error publishing event {event_type}: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for this module"""
        return {
            'module_name': self.module_name,
            'active_positions': len(self._active_positions),
            'pending_opportunities': len(self._pending_opportunities),
            'performance_metrics': self._performance_metrics.copy()
        }
    
    # Private helper methods
    
    def _calculate_current_allocation(self) -> float:
        """Calculate current portfolio allocation percentage for this module"""
        try:
            return self.risk_manager.get_module_allocation(self.module_name)
        except Exception as e:
            self.logger.error(f"Error calculating allocation: {e}")
            return 0.0
    
    def _update_performance_metrics(self, result: TradeResult):
        """Update internal performance metrics with trade result"""
        if 'total_trades' not in self._performance_metrics:
            self._performance_metrics = {
                'total_trades': 0,
                'successful_trades': 0,
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'avg_hold_time': 0.0
            }
        
        self._performance_metrics['total_trades'] += 1
        
        if result.success and result.pnl is not None:
            if result.pnl > 0:
                self._performance_metrics['successful_trades'] += 1
            self._performance_metrics['total_pnl'] += result.pnl
            
            # Update win rate
            self._performance_metrics['win_rate'] = (
                self._performance_metrics['successful_trades'] / 
                self._performance_metrics['total_trades']
            )
            
            # Update average hold time
            if result.hold_duration is not None:
                current_avg = self._performance_metrics['avg_hold_time']
                total_trades = self._performance_metrics['total_trades']
                self._performance_metrics['avg_hold_time'] = (
                    (current_avg * (total_trades - 1) + result.hold_duration) / total_trades
                )
    
    # ML Data Collection Helper Methods
    
    def save_ml_enhanced_trade(self, trade_data: Dict[str, Any]) -> str:
        """Save trade with ML-critical data to Firebase"""
        try:
            if self.firebase_db and self.firebase_db.is_connected():
                trade_id = self.firebase_db.save_trade(trade_data)
                self.logger.debug(f"Saved ML-enhanced trade: {trade_data.get('symbol')} - {trade_id}")
                return trade_id
            else:
                self.logger.warning("Firebase not connected - ML data not saved")
                return "no_firebase"
        except Exception as e:
            self.logger.error(f"Error saving ML trade data: {e}")
            return "error"
    
    def update_ml_trade_outcome(self, trade_id: str, outcome_data: Dict[str, Any]):
        """Update existing trade with final profit/loss outcome - CRITICAL FOR ML LEARNING"""
        try:
            if self.firebase_db and self.firebase_db.is_connected():
                success = self.firebase_db.update_trade_outcome(trade_id, outcome_data)
                if success:
                    self.logger.debug(f"✅ Trade {trade_id} outcome updated with P&L: ${outcome_data.get('profit_loss', 0):.2f}")
                else:
                    self.logger.warning(f"Failed to update trade {trade_id} outcome")
            else:
                self.logger.warning("Firebase not available for trade outcome update")
        except Exception as e:
            self.logger.error(f"Error updating trade outcome {trade_id}: {e}")
    
    def record_parameter_effectiveness(self, 
                                     parameter_type: str,
                                     parameter_value: Any,
                                     trade_outcome: Dict[str, Any],
                                     success: bool,
                                     profit_loss: float):
        """Record parameter effectiveness for ML optimization"""
        try:
            self.parameter_tracker.record_parameter_outcome(
                parameter_type=parameter_type,
                parameter_value=parameter_value,
                trade_outcome=trade_outcome,
                success=success,
                profit_loss=profit_loss
            )
            self.logger.debug(f"Recorded parameter effectiveness: {parameter_type}={parameter_value}, success={success}")
        except Exception as e:
            self.logger.error(f"Error recording parameter effectiveness: {e}")
    
    def log_ml_parameter_change(self,
                              parameters_before: Dict[str, Any],
                              parameters_after: Dict[str, Any],
                              performance_impact: float = None,
                              learning_trigger: str = None):
        """Log ML parameter changes for audit trail"""
        try:
            self.ml_event_logger.log_parameter_change(
                parameters_before=parameters_before,
                parameters_after=parameters_after,
                performance_impact=performance_impact,
                learning_trigger=learning_trigger
            )
            self.logger.info(f"Logged ML parameter change: {len(parameters_after)} parameters updated")
        except Exception as e:
            self.logger.error(f"Error logging ML parameter change: {e}")
    
    def get_ml_optimized_parameters(self) -> Dict[str, Any]:
        """Get ML-optimized parameters from Firebase"""
        try:
            if self.firebase_db and self.firebase_db.is_connected():
                optimization_data = self.firebase_db.get_ml_optimization_data(self.module_name)
                if optimization_data:
                    return optimization_data[0].get('optimized_parameters', {})
            return {}
        except Exception as e:
            self.logger.error(f"Error getting ML optimized parameters: {e}")
            return {}
    
    def update_ml_optimized_parameters(self, optimized_parameters: Dict[str, Any]):
        """Update ML-optimized parameters in Firebase"""
        try:
            if self.firebase_db and self.firebase_db.is_connected():
                optimization_data = {
                    'optimized_parameters': optimized_parameters,
                    'optimization_generation': getattr(self, '_optimization_generation', 0) + 1,
                    'last_optimization': datetime.now(),
                    'module_version': "1.0"
                }
                self.firebase_db.save_ml_optimization_data(self.module_name, optimization_data)
                self._optimization_generation = optimization_data['optimization_generation']
                self.logger.info(f"Updated ML parameters for {self.module_name}: generation {self._optimization_generation}")
        except Exception as e:
            self.logger.error(f"Error updating ML parameters: {e}")


class ModuleHealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class ModuleHealth:
    """Health status for a trading module"""
    module_name: str
    status: ModuleHealthStatus
    last_update: datetime
    error_count: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def is_healthy(self) -> bool:
        return self.status == ModuleHealthStatus.HEALTHY


class ModuleRegistry:
    """Registry for managing trading modules"""
    
    def __init__(self):
        self._modules: Dict[str, TradingModule] = {}
        self._health_status: Dict[str, ModuleHealth] = {}
    
    def register_module(self, module: TradingModule):
        """Register a trading module"""
        self._modules[module.module_name] = module
        self._health_status[module.module_name] = ModuleHealth(
            module_name=module.module_name,
            status=ModuleHealthStatus.HEALTHY,
            last_update=datetime.now()
        )
    
    def get_module(self, module_name: str) -> Optional[TradingModule]:
        """Get a module by name"""
        return self._modules.get(module_name)
    
    def get_active_modules(self) -> List[TradingModule]:
        """Get all active (healthy and enabled) modules"""
        return [
            module for module in self._modules.values()
            if (module.config.enabled and 
                self._health_status[module.module_name].is_healthy)
        ]
    
    def update_health(self, module_name: str, status: ModuleHealthStatus, 
                     message: str = ""):
        """Update health status for a module"""
        if module_name in self._health_status:
            health = self._health_status[module_name]
            health.status = status
            health.last_update = datetime.now()
            
            if status == ModuleHealthStatus.ERROR:
                health.error_count += 1
                health.errors.append(f"{datetime.now()}: {message}")
            elif status == ModuleHealthStatus.WARNING:
                health.warnings.append(f"{datetime.now()}: {message}")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for all modules"""
        return {
            name: {
                'status': health.status.value,
                'last_update': health.last_update.isoformat(),
                'error_count': health.error_count,
                'enabled': self._modules[name].config.enabled
            }
            for name, health in self._health_status.items()
        }