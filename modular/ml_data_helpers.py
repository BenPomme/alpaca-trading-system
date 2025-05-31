#!/usr/bin/env python3
"""
ML Data Collection Helpers for Trading Modules

Provides utilities for trading modules to capture ML-critical parameter data
that enables continuous parameter optimization.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class MLTradeData:
    """Complete ML-enhanced trade data structure"""
    
    # Basic trade data (existing fields)
    symbol: str
    side: str  # BUY/SELL
    quantity: float
    price: float
    strategy: str
    confidence: float
    profit_loss: float = 0.0
    exit_reason: str = None
    
    # ML-critical fields (new)
    entry_parameters: Dict[str, Any] = None
    module_specific_params: Dict[str, Any] = None
    exit_analysis: Dict[str, Any] = None
    market_context: Dict[str, Any] = None
    parameter_performance: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize empty dicts for ML fields if not provided"""
        if self.entry_parameters is None:
            self.entry_parameters = {}
        if self.module_specific_params is None:
            self.module_specific_params = {}
        if self.exit_analysis is None:
            self.exit_analysis = {}
        if self.market_context is None:
            self.market_context = {}
        if self.parameter_performance is None:
            self.parameter_performance = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firebase storage"""
        data = asdict(self)
        data['ml_data_version'] = "1.0"
        data['ml_enhanced'] = True
        data['timestamp'] = datetime.now()
        return data


class MLDataCollector:
    """Helper class for collecting ML-critical trading data"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.current_market_session = None
        self.us_market_open = None
    
    def create_entry_parameters(self,
                               confidence_threshold_used: float,
                               position_size_multiplier: float,
                               regime_confidence: float = None,
                               technical_confidence: float = None,
                               pattern_confidence: float = None,
                               ml_strategy_selection: bool = False,
                               **kwargs) -> Dict[str, Any]:
        """Create entry parameters data for ML learning"""
        entry_params = {
            'confidence_threshold_used': confidence_threshold_used,
            'position_size_multiplier': position_size_multiplier,
            'ml_strategy_selection': ml_strategy_selection
        }
        
        # Add intelligence scores if available
        if regime_confidence is not None:
            entry_params['regime_confidence'] = regime_confidence
        if technical_confidence is not None:
            entry_params['technical_confidence'] = technical_confidence
        if pattern_confidence is not None:
            entry_params['pattern_confidence'] = pattern_confidence
        
        # Add any additional parameters
        entry_params.update(kwargs)
        
        return entry_params
    
    def create_crypto_module_params(self,
                                  crypto_session: str,
                                  volatility_score: float,
                                  momentum_score: float,
                                  volume_score: float,
                                  session_multiplier: float,
                                  analysis_weights: Dict[str, float] = None,
                                  **kwargs) -> Dict[str, Any]:
        """Create crypto-specific module parameters"""
        crypto_params = {
            'crypto_session': crypto_session,
            'volatility_score': volatility_score,
            'momentum_score': momentum_score,
            'volume_score': volume_score,
            'session_multiplier': session_multiplier
        }
        
        if analysis_weights:
            crypto_params['analysis_weights'] = analysis_weights
        
        crypto_params.update(kwargs)
        return crypto_params
    
    def create_options_module_params(self,
                                   underlying_price: float,
                                   strike_selected: float,
                                   expiration_days: int,
                                   implied_volatility: float,
                                   option_strategy: str,
                                   contracts_multiplier: float = None,
                                   greeks: Dict[str, float] = None,
                                   **kwargs) -> Dict[str, Any]:
        """Create options-specific module parameters"""
        options_params = {
            'underlying_price': underlying_price,
            'strike_selected': strike_selected,
            'expiration_days': expiration_days,
            'implied_volatility': implied_volatility,
            'option_strategy': option_strategy
        }
        
        if contracts_multiplier is not None:
            options_params['contracts_multiplier'] = contracts_multiplier
        if greeks:
            options_params['greeks'] = greeks
        
        options_params.update(kwargs)
        return options_params
    
    def create_stocks_module_params(self,
                                  regime_type: str,
                                  leverage_factor: float = None,
                                  sector_momentum: float = None,
                                  intelligence_weights_used: Dict[str, float] = None,
                                  strategy_specific_config: Dict[str, Any] = None,
                                  **kwargs) -> Dict[str, Any]:
        """Create stocks-specific module parameters"""
        stocks_params = {
            'regime_type': regime_type
        }
        
        if leverage_factor is not None:
            stocks_params['leverage_factor'] = leverage_factor
        if sector_momentum is not None:
            stocks_params['sector_momentum'] = sector_momentum
        if intelligence_weights_used:
            stocks_params['intelligence_weights_used'] = intelligence_weights_used
        if strategy_specific_config:
            stocks_params['strategy_specific_config'] = strategy_specific_config
        
        stocks_params.update(kwargs)
        return stocks_params
    
    def create_exit_analysis(self,
                           hold_duration_hours: float,
                           exit_signals_count: int,
                           final_decision_reason: str,
                           ml_confidence_decay: float = None,
                           reversal_probability: float = None,
                           regime_adjusted_target: float = None,
                           exit_signals_details: List[str] = None,
                           **kwargs) -> Dict[str, Any]:
        """Create exit analysis data for ML learning"""
        exit_analysis = {
            'hold_duration_hours': hold_duration_hours,
            'exit_signals_count': exit_signals_count,
            'final_decision_reason': final_decision_reason
        }
        
        if ml_confidence_decay is not None:
            exit_analysis['ml_confidence_decay'] = ml_confidence_decay
        if reversal_probability is not None:
            exit_analysis['reversal_probability'] = reversal_probability
        if regime_adjusted_target is not None:
            exit_analysis['regime_adjusted_target'] = regime_adjusted_target
        if exit_signals_details:
            exit_analysis['exit_signals_details'] = exit_signals_details
        
        exit_analysis.update(kwargs)
        return exit_analysis
    
    def create_market_context(self,
                            us_market_open: bool = None,
                            crypto_session: str = None,
                            cycle_delay_used: int = None,
                            global_trading_active: bool = None,
                            market_hours_type: str = None,
                            **kwargs) -> Dict[str, Any]:
        """Create market context data"""
        market_context = {}
        
        if us_market_open is not None:
            market_context['us_market_open'] = us_market_open
        if crypto_session is not None:
            market_context['crypto_session'] = crypto_session
        if cycle_delay_used is not None:
            market_context['cycle_delay_used'] = cycle_delay_used
        if global_trading_active is not None:
            market_context['global_trading_active'] = global_trading_active
        if market_hours_type is not None:
            market_context['market_hours_type'] = market_hours_type
        
        market_context.update(kwargs)
        return market_context
    
    def create_parameter_performance(self,
                                   confidence_accuracy: float = None,
                                   threshold_effectiveness: float = None,
                                   regime_multiplier_success: bool = None,
                                   alternative_outcomes: Dict[str, str] = None,
                                   parameter_attribution: Dict[str, float] = None,
                                   **kwargs) -> Dict[str, Any]:
        """Create parameter performance data for ML analysis"""
        param_performance = {}
        
        if confidence_accuracy is not None:
            param_performance['confidence_accuracy'] = confidence_accuracy
        if threshold_effectiveness is not None:
            param_performance['threshold_effectiveness'] = threshold_effectiveness
        if regime_multiplier_success is not None:
            param_performance['regime_multiplier_success'] = regime_multiplier_success
        if alternative_outcomes:
            param_performance['alternative_outcomes'] = alternative_outcomes
        if parameter_attribution:
            param_performance['parameter_attribution'] = parameter_attribution
        
        param_performance.update(kwargs)
        return param_performance
    
    def create_ml_trade_data(self,
                           symbol: str,
                           side: str,
                           quantity: float,
                           price: float,
                           strategy: str,
                           confidence: float,
                           entry_parameters: Dict[str, Any],
                           module_specific_params: Dict[str, Any],
                           market_context: Dict[str, Any] = None,
                           exit_analysis: Dict[str, Any] = None,
                           parameter_performance: Dict[str, Any] = None,
                           profit_loss: float = 0.0,
                           exit_reason: str = None) -> MLTradeData:
        """Create complete ML trade data object"""
        
        if market_context is None:
            market_context = self.create_market_context()
        
        if parameter_performance is None:
            parameter_performance = self.create_parameter_performance()
        
        return MLTradeData(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            strategy=strategy,
            confidence=confidence,
            profit_loss=profit_loss,
            exit_reason=exit_reason,
            entry_parameters=entry_parameters,
            module_specific_params=module_specific_params,
            exit_analysis=exit_analysis or {},
            market_context=market_context,
            parameter_performance=parameter_performance
        )


class ParameterEffectivenessTracker:
    """Tracks parameter effectiveness for ML optimization"""
    
    def __init__(self, firebase_db, module_name: str):
        self.firebase_db = firebase_db
        self.module_name = module_name
    
    def record_parameter_outcome(self,
                               parameter_type: str,
                               parameter_value: Any,
                               trade_outcome: Dict[str, Any],
                               success: bool,
                               profit_loss: float):
        """Record a parameter outcome for effectiveness tracking"""
        
        param_data = {
            'module_name': self.module_name,
            'parameter_type': parameter_type,
            'parameter_value': parameter_value,
            'success': success,
            'profit_loss': profit_loss,
            'trade_outcome': trade_outcome
        }
        
        if self.firebase_db and self.firebase_db.is_connected():
            self.firebase_db.save_parameter_effectiveness(param_data)
    
    def get_parameter_effectiveness(self, parameter_type: str = None) -> List[Dict[str, Any]]:
        """Get parameter effectiveness data for analysis"""
        if self.firebase_db and self.firebase_db.is_connected():
            return self.firebase_db.get_parameter_effectiveness(
                module_name=self.module_name,
                parameter_type=parameter_type
            )
        return []


class MLLearningEventLogger:
    """Logs ML learning events for audit trail"""
    
    def __init__(self, firebase_db, model_name: str):
        self.firebase_db = firebase_db
        self.model_name = model_name
    
    def log_parameter_change(self,
                           parameters_before: Dict[str, Any],
                           parameters_after: Dict[str, Any],
                           performance_impact: float = None,
                           confidence_change: float = None,
                           learning_trigger: str = None):
        """Log a parameter change event"""
        
        event_data = {
            'model_name': self.model_name,
            'learning_event': 'parameter_change',
            'parameters_before': parameters_before,
            'parameters_after': parameters_after,
            'performance_impact': performance_impact,
            'confidence_change': confidence_change,
            'learning_trigger': learning_trigger or 'performance_feedback'
        }
        
        if self.firebase_db and self.firebase_db.is_connected():
            self.firebase_db.save_ml_learning_event(event_data)
    
    def log_trade_outcome_processed(self,
                                  trade_data: Dict[str, Any],
                                  parameters_updated: Dict[str, Any] = None,
                                  learning_signal: str = None):
        """Log when a trade outcome is processed for ML learning"""
        
        event_data = {
            'model_name': self.model_name,
            'learning_event': 'trade_outcome_processed',
            'trade_symbol': trade_data.get('symbol'),
            'trade_success': trade_data.get('profit_loss', 0) > 0,
            'trade_confidence': trade_data.get('confidence'),
            'parameters_updated': parameters_updated or {},
            'learning_signal': learning_signal
        }
        
        if self.firebase_db and self.firebase_db.is_connected():
            self.firebase_db.save_ml_learning_event(event_data)