#!/usr/bin/env python3
"""
ML Parameter Optimization Engine for Modular Trading Architecture

This module implements real-time parameter optimization using machine learning
techniques to continuously improve trading module performance based on
historical data and live performance feedback.
"""

import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from modular.ml_data_helpers import MLLearningEventLogger


@dataclass
class ParameterOptimizationResult:
    """Result of parameter optimization"""
    module_name: str
    parameter_type: str
    old_value: Any
    new_value: Any
    expected_improvement: float
    confidence: float
    optimization_method: str
    data_points_used: int


@dataclass
class MLModelPerformance:
    """ML model performance metrics"""
    model_name: str
    accuracy_score: float
    feature_importance: Dict[str, float]
    cross_validation_score: float
    training_data_points: int
    last_updated: datetime


class BayesianOptimizer:
    """Bayesian optimization for continuous parameters"""
    
    def __init__(self, parameter_bounds: Dict[str, Tuple[float, float]]):
        self.parameter_bounds = parameter_bounds
        self.acquisition_data = []
        self.gp_model = None
    
    def suggest_next_parameters(self, historical_data: List[Dict]) -> Dict[str, float]:
        """Suggest next parameter values using Bayesian optimization"""
        if len(historical_data) < 3:
            # Not enough data for Bayesian optimization, return random sample
            return self._random_sample()
        
        try:
            # Prepare data for Gaussian Process
            X, y = self._prepare_data(historical_data)
            
            if len(X) == 0:
                return self._random_sample()
            
            # Use Random Forest as GP surrogate for simplicity and robustness
            self.gp_model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.gp_model.fit(X, y)
            
            # Find optimal parameters using acquisition function
            best_params = self._optimize_acquisition_function()
            
            return best_params
            
        except Exception as e:
            logging.warning(f"Bayesian optimization failed: {e}, falling back to random sampling")
            return self._random_sample()
    
    def _prepare_data(self, historical_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for optimization"""
        X = []
        y = []
        
        for data_point in historical_data:
            # Extract parameter values
            param_values = []
            for param_name in self.parameter_bounds.keys():
                if param_name in data_point:
                    param_values.append(float(data_point[param_name]))
                else:
                    # Skip this data point if missing parameters
                    break
            
            if len(param_values) == len(self.parameter_bounds):
                X.append(param_values)
                # Use profit/loss or success rate as target
                target = data_point.get('profit_loss', 0.0)
                if target == 0.0:
                    target = 1.0 if data_point.get('success', False) else -1.0
                y.append(target)
        
        return np.array(X), np.array(y)
    
    def _random_sample(self) -> Dict[str, float]:
        """Sample random parameter values within bounds"""
        return {
            param_name: np.random.uniform(bounds[0], bounds[1])
            for param_name, bounds in self.parameter_bounds.items()
        }
    
    def _optimize_acquisition_function(self) -> Dict[str, float]:
        """Optimize acquisition function to find next best parameters"""
        try:
            def negative_acquisition(x):
                # Expected improvement acquisition function
                x_reshaped = x.reshape(1, -1)
                mean_pred = self.gp_model.predict(x_reshaped)[0]
                return -mean_pred  # Negative because we minimize
            
            # Random starting point
            x0 = np.array([
                np.random.uniform(bounds[0], bounds[1])
                for bounds in self.parameter_bounds.values()
            ])
            
            # Bounds for optimization
            bounds = list(self.parameter_bounds.values())
            
            # Optimize
            result = minimize(negative_acquisition, x0, bounds=bounds, method='L-BFGS-B')
            
            if result.success:
                optimized_values = result.x
                return {
                    param_name: float(value)
                    for param_name, value in zip(self.parameter_bounds.keys(), optimized_values)
                }
            else:
                return self._random_sample()
                
        except Exception:
            return self._random_sample()


class ParameterOptimizer:
    """Core parameter optimization engine"""
    
    def __init__(self, firebase_db, logger: Optional[logging.Logger] = None):
        self.firebase_db = firebase_db
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # Parameter boundaries for different parameter types
        self.parameter_bounds = {
            'confidence_threshold': (0.4, 0.9),
            'position_multiplier': (0.5, 3.0),
            'leverage_factor': (1.0, 3.0),
            'session_multiplier': (0.8, 2.0),
            'volatility_threshold': (0.1, 0.8),
            'momentum_threshold': (0.3, 0.9),
            'regime_confidence_weight': (0.2, 0.6),
            'technical_confidence_weight': (0.2, 0.6),
            'pattern_confidence_weight': (0.1, 0.4)
        }
        
        # Module-specific optimizers
        self.bayesian_optimizers = {}
        self.performance_trackers = {}
        
        # Minimum data requirements
        self.min_data_points = 10
        self.optimization_frequency = timedelta(hours=6)  # Optimize every 6 hours
        self.last_optimization = {}
        
        self.logger.info("ML Parameter Optimizer initialized")
    
    def should_optimize_parameters(self, module_name: str) -> bool:
        """Check if parameters should be optimized for a module"""
        try:
            # Check if enough time has passed
            if module_name in self.last_optimization:
                time_since_last = datetime.now() - self.last_optimization[module_name]
                if time_since_last < self.optimization_frequency:
                    return False
            
            # Check if we have enough data
            recent_data = self._get_recent_performance_data(module_name)
            return len(recent_data) >= self.min_data_points
            
        except Exception as e:
            self.logger.error(f"Error checking optimization criteria for {module_name}: {e}")
            return False
    
    def optimize_module_parameters(self, module_name: str) -> List[ParameterOptimizationResult]:
        """Optimize parameters for a specific module with enhanced profit-based learning"""
        optimization_results = []
        
        try:
            self.logger.info(f"Starting enhanced parameter optimization for {module_name}")
            
            # Get recent performance data with profit focus
            performance_data = self._get_recent_performance_data(module_name)
            if len(performance_data) < self.min_data_points:
                self.logger.warning(f"Insufficient data for {module_name}: {len(performance_data)} points")
                return optimization_results
            
            # Enhanced profitability analysis
            profit_analysis = self._analyze_profitability_patterns(module_name, performance_data)
            self.logger.info(f"Profitability analysis for {module_name}: {profit_analysis}")
            
            # Get current module parameters
            current_params = self._get_current_module_parameters(module_name)
            
            # Analyze parameter effectiveness with profit weighting
            param_analysis = self._analyze_parameter_effectiveness_with_profit(module_name, performance_data)
            
            # Optimize parameters based on profitability patterns
            for param_type, effectiveness in param_analysis.items():
                if effectiveness.get('should_optimize', False):
                    result = self._optimize_single_parameter_for_profit(
                        module_name, param_type, performance_data, current_params, profit_analysis
                    )
                    if result:
                        optimization_results.append(result)
            
            # Update last optimization time
            self.last_optimization[module_name] = datetime.now()
            
            self.logger.info(f"Enhanced optimization for {module_name}: {len(optimization_results)} parameters updated")
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Error in enhanced optimization for {module_name}: {e}")
            return optimization_results
    
    def _get_recent_performance_data(self, module_name: str, days_back: int = 7) -> List[Dict]:
        """Get recent performance data for a module"""
        try:
            if not self.firebase_db or not self.firebase_db.is_connected():
                return []
            
            # Get performance data from Firebase
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # This would use Firebase query - simplified for now
            all_data = self.firebase_db.get_ml_optimization_data(module_name)
            
            # Filter recent data
            recent_data = [
                data for data in all_data
                if self._parse_timestamp(data.get('timestamp')) >= cutoff_date
            ]
            
            return recent_data
            
        except Exception as e:
            self.logger.error(f"Error getting performance data for {module_name}: {e}")
            return []
    
    def _get_current_module_parameters(self, module_name: str) -> Dict[str, Any]:
        """Get current parameters for a module"""
        try:
            if self.firebase_db and self.firebase_db.is_connected():
                return self.firebase_db.get_module_parameters(module_name)
            return {}
        except Exception as e:
            self.logger.error(f"Error getting current parameters for {module_name}: {e}")
            return {}
    
    def _analyze_parameter_effectiveness(self, module_name: str, 
                                       performance_data: List[Dict]) -> Dict[str, Dict]:
        """Analyze which parameters should be optimized"""
        analysis = {}
        
        try:
            # Group data by parameter types
            param_groups = self._group_data_by_parameters(performance_data)
            
            for param_type, param_data in param_groups.items():
                if len(param_data) < 5:  # Need minimum data for analysis
                    continue
                
                # Calculate performance correlation
                correlation = self._calculate_parameter_correlation(param_type, param_data)
                variance = self._calculate_parameter_variance(param_type, param_data)
                
                # Determine if optimization is needed
                should_optimize = (
                    abs(correlation) > 0.1 and  # Some correlation with performance
                    variance > 0.01 and        # Some variance in parameter values
                    len(param_data) >= 5       # Sufficient data points
                )
                
                analysis[param_type] = {
                    'correlation': correlation,
                    'variance': variance,
                    'data_points': len(param_data),
                    'should_optimize': should_optimize
                }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing parameter effectiveness: {e}")
            return {}
    
    def _optimize_single_parameter(self, module_name: str, param_type: str,
                                 performance_data: List[Dict],
                                 current_params: Dict[str, Any]) -> Optional[ParameterOptimizationResult]:
        """Optimize a single parameter using appropriate method"""
        try:
            # Check if parameter has bounds (continuous optimization)
            if param_type in self.parameter_bounds:
                return self._optimize_continuous_parameter(
                    module_name, param_type, performance_data, current_params
                )
            else:
                return self._optimize_discrete_parameter(
                    module_name, param_type, performance_data, current_params
                )
                
        except Exception as e:
            self.logger.error(f"Error optimizing parameter {param_type}: {e}")
            return None
    
    def _optimize_continuous_parameter(self, module_name: str, param_type: str,
                                     performance_data: List[Dict],
                                     current_params: Dict[str, Any]) -> Optional[ParameterOptimizationResult]:
        """Optimize continuous parameter using Bayesian optimization"""
        try:
            # Get or create Bayesian optimizer for this parameter
            optimizer_key = f"{module_name}_{param_type}"
            if optimizer_key not in self.bayesian_optimizers:
                bounds = {param_type: self.parameter_bounds[param_type]}
                self.bayesian_optimizers[optimizer_key] = BayesianOptimizer(bounds)
            
            optimizer = self.bayesian_optimizers[optimizer_key]
            
            # Suggest new parameter value
            suggested_params = optimizer.suggest_next_parameters(performance_data)
            new_value = suggested_params.get(param_type)
            
            if new_value is None:
                return None
            
            current_value = current_params.get(param_type, 0.5)
            
            # Calculate expected improvement
            expected_improvement = self._estimate_improvement(
                param_type, current_value, new_value, performance_data
            )
            
            # Only suggest change if improvement is significant
            if abs(new_value - current_value) < 0.05 or expected_improvement < 0.02:
                return None
            
            return ParameterOptimizationResult(
                module_name=module_name,
                parameter_type=param_type,
                old_value=current_value,
                new_value=new_value,
                expected_improvement=expected_improvement,
                confidence=min(0.8, len(performance_data) / 50),  # Higher confidence with more data
                optimization_method="bayesian",
                data_points_used=len(performance_data)
            )
            
        except Exception as e:
            self.logger.error(f"Error in continuous parameter optimization: {e}")
            return None
    
    def _optimize_discrete_parameter(self, module_name: str, param_type: str,
                                   performance_data: List[Dict],
                                   current_params: Dict[str, Any]) -> Optional[ParameterOptimizationResult]:
        """Optimize discrete parameter using performance analysis"""
        try:
            # Analyze performance by parameter value
            value_performance = {}
            
            for data_point in performance_data:
                param_value = data_point.get(param_type)
                if param_value is not None:
                    if param_value not in value_performance:
                        value_performance[param_value] = []
                    
                    profit_loss = data_point.get('profit_loss', 0.0)
                    if profit_loss == 0.0:
                        profit_loss = 1.0 if data_point.get('success', False) else -1.0
                    
                    value_performance[param_value].append(profit_loss)
            
            # Find best performing value
            best_value = None
            best_performance = float('-inf')
            
            for value, performances in value_performance.items():
                if len(performances) >= 3:  # Need minimum samples
                    avg_performance = np.mean(performances)
                    if avg_performance > best_performance:
                        best_performance = avg_performance
                        best_value = value
            
            current_value = current_params.get(param_type)
            
            if best_value is None or best_value == current_value:
                return None
            
            return ParameterOptimizationResult(
                module_name=module_name,
                parameter_type=param_type,
                old_value=current_value,
                new_value=best_value,
                expected_improvement=best_performance,
                confidence=0.6,
                optimization_method="discrete_analysis",
                data_points_used=len(performance_data)
            )
            
        except Exception as e:
            self.logger.error(f"Error in discrete parameter optimization: {e}")
            return None
    
    def _group_data_by_parameters(self, performance_data: List[Dict]) -> Dict[str, List[Dict]]:
        """Group performance data by parameter types"""
        param_groups = {}
        
        for data_point in performance_data:
            # Extract parameter information from the data point
            for key in data_point.keys():
                if any(param_key in key.lower() for param_key in 
                      ['confidence', 'threshold', 'multiplier', 'weight', 'factor']):
                    if key not in param_groups:
                        param_groups[key] = []
                    param_groups[key].append(data_point)
        
        return param_groups
    
    def _calculate_parameter_correlation(self, param_type: str, param_data: List[Dict]) -> float:
        """Calculate correlation between parameter value and performance"""
        try:
            param_values = []
            performance_values = []
            
            for data_point in param_data:
                param_val = data_point.get(param_type)
                perf_val = data_point.get('profit_loss', 0.0)
                
                if param_val is not None and isinstance(param_val, (int, float)):
                    param_values.append(float(param_val))
                    performance_values.append(perf_val)
            
            if len(param_values) < 3:
                return 0.0
            
            correlation = np.corrcoef(param_values, performance_values)[0, 1]
            return correlation if not np.isnan(correlation) else 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_parameter_variance(self, param_type: str, param_data: List[Dict]) -> float:
        """Calculate variance in parameter values"""
        try:
            param_values = []
            
            for data_point in param_data:
                param_val = data_point.get(param_type)
                if param_val is not None and isinstance(param_val, (int, float)):
                    param_values.append(float(param_val))
            
            if len(param_values) < 2:
                return 0.0
            
            return np.var(param_values)
            
        except Exception:
            return 0.0
    
    def _estimate_improvement(self, param_type: str, current_value: float,
                            new_value: float, performance_data: List[Dict]) -> float:
        """Estimate performance improvement from parameter change"""
        try:
            # Simple linear extrapolation based on historical correlation
            correlation = self._calculate_parameter_correlation(param_type, performance_data)
            value_change = new_value - current_value
            
            # Estimate improvement as correlation * change magnitude
            estimated_improvement = abs(correlation * value_change * 0.1)  # Conservative estimate
            
            return min(estimated_improvement, 0.2)  # Cap at 20% improvement
            
        except Exception:
            return 0.01  # Small positive default
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime"""
        try:
            if isinstance(timestamp_str, datetime):
                return timestamp_str
            # Handle ISO format timestamps
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except Exception:
            return datetime.now() - timedelta(days=30)  # Very old timestamp as fallback


class MLParameterOptimizationEngine:
    """Main ML Parameter Optimization Engine"""
    
    def __init__(self, firebase_db, orchestrator, logger: Optional[logging.Logger] = None):
        self.firebase_db = firebase_db
        self.orchestrator = orchestrator
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # Core components
        self.parameter_optimizer = ParameterOptimizer(firebase_db, logger)
        self.active_experiments = {}
        
        # Optimization settings
        self.optimization_enabled = True
        self.min_confidence_for_application = 0.6
        self.max_parameter_changes_per_cycle = 3
        
        self.logger.info("ML Parameter Optimization Engine initialized")
    
    def run_optimization_cycle(self) -> Dict[str, Any]:
        """Run a complete parameter optimization cycle"""
        optimization_summary = {
            'timestamp': datetime.now().isoformat(),
            'modules_analyzed': 0,
            'parameters_optimized': 0,
            'optimizations_applied': 0,
            'total_expected_improvement': 0.0
        }
        
        if not self.optimization_enabled:
            self.logger.info("Parameter optimization is disabled")
            return optimization_summary
        
        try:
            self.logger.info("Starting ML parameter optimization cycle")
            
            # Get all active modules from orchestrator
            active_modules = self.orchestrator.registry.get_active_modules()
            
            for module in active_modules:
                module_name = module.module_name
                optimization_summary['modules_analyzed'] += 1
                
                # Check if optimization is needed
                if self.parameter_optimizer.should_optimize_parameters(module_name):
                    # Run optimization for this module
                    results = self.parameter_optimizer.optimize_module_parameters(module_name)
                    
                    for result in results:
                        optimization_summary['parameters_optimized'] += 1
                        optimization_summary['total_expected_improvement'] += result.expected_improvement
                        
                        # Apply optimization if confidence is high enough
                        if (result.confidence >= self.min_confidence_for_application and
                            optimization_summary['optimizations_applied'] < self.max_parameter_changes_per_cycle):
                            
                            success = self._apply_parameter_optimization(module, result)
                            if success:
                                optimization_summary['optimizations_applied'] += 1
                                
                                # Log the optimization
                                self._log_optimization_applied(result)
            
            self.logger.info(f"Optimization cycle complete: {optimization_summary}")
            return optimization_summary
            
        except Exception as e:
            self.logger.error(f"Error in optimization cycle: {e}")
            optimization_summary['error'] = str(e)
            return optimization_summary
    
    def _apply_parameter_optimization(self, module, result: ParameterOptimizationResult) -> bool:
        """Apply parameter optimization to a module"""
        try:
            self.logger.info(f"Applying optimization: {result.module_name}.{result.parameter_type} "
                           f"{result.old_value} -> {result.new_value} "
                           f"(expected improvement: {result.expected_improvement:.1%})")
            
            # Update module configuration
            config_update = {result.parameter_type: result.new_value}
            self.orchestrator.update_module_config(result.module_name, config_update)
            
            # Save optimization to Firebase
            self._save_optimization_result(result)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying optimization: {e}")
            return False
    
    def _save_optimization_result(self, result: ParameterOptimizationResult):
        """Save optimization result to Firebase"""
        try:
            if self.firebase_db and self.firebase_db.is_connected():
                optimization_data = {
                    'module_name': result.module_name,
                    'parameter_type': result.parameter_type,
                    'old_value': result.old_value,
                    'new_value': result.new_value,
                    'expected_improvement': result.expected_improvement,
                    'confidence': result.confidence,
                    'optimization_method': result.optimization_method,
                    'data_points_used': result.data_points_used,
                    'timestamp': datetime.now().isoformat(),
                    'applied': True
                }
                
                self.firebase_db.save_ml_optimization_data(result.module_name, optimization_data)
                
        except Exception as e:
            self.logger.error(f"Error saving optimization result: {e}")
    
    def _log_optimization_applied(self, result: ParameterOptimizationResult):
        """Log optimization application for audit trail"""
        try:
            event_logger = MLLearningEventLogger(self.firebase_db, "parameter_optimizer")
            event_logger.log_parameter_change(
                parameters_before={result.parameter_type: result.old_value},
                parameters_after={result.parameter_type: result.new_value},
                performance_impact=result.expected_improvement,
                confidence_change=result.confidence,
                learning_trigger=f"{result.optimization_method}_optimization"
            )
            
        except Exception as e:
            self.logger.error(f"Error logging optimization: {e}")
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status"""
        return {
            'optimization_enabled': self.optimization_enabled,
            'min_confidence_threshold': self.min_confidence_for_application,
            'max_changes_per_cycle': self.max_parameter_changes_per_cycle,
            'active_experiments': len(self.active_experiments),
            'last_optimization_cycle': getattr(self, 'last_cycle_time', None)
        }
    
    def enable_optimization(self):
        """Enable parameter optimization"""
        self.optimization_enabled = True
        self.logger.info("Parameter optimization enabled")
    
    def disable_optimization(self):
        """Disable parameter optimization"""
        self.optimization_enabled = False
        self.logger.info("Parameter optimization disabled")
    
    def _analyze_profitability_patterns(self, module_name: str, performance_data: List[Dict]) -> Dict[str, Any]:
        """Analyze profitability patterns to guide optimization"""
        try:
            profitable_trades = [d for d in performance_data if d.get('profit_loss', 0) > 0]
            losing_trades = [d for d in performance_data if d.get('profit_loss', 0) < 0]
            
            total_trades = len(performance_data)
            win_rate = len(profitable_trades) / total_trades if total_trades > 0 else 0
            
            avg_profit = np.mean([d.get('profit_loss', 0) for d in profitable_trades]) if profitable_trades else 0
            avg_loss = np.mean([d.get('profit_loss', 0) for d in losing_trades]) if losing_trades else 0
            
            # Analyze confidence thresholds of profitable vs losing trades
            profitable_confidence = np.mean([d.get('confidence', 0.5) for d in profitable_trades]) if profitable_trades else 0.5
            losing_confidence = np.mean([d.get('confidence', 0.5) for d in losing_trades]) if losing_trades else 0.5
            
            return {
                'win_rate': win_rate,
                'avg_profit': avg_profit,
                'avg_loss': avg_loss,
                'profit_factor': abs(avg_profit / avg_loss) if avg_loss != 0 else 1.0,
                'profitable_confidence_avg': profitable_confidence,
                'losing_confidence_avg': losing_confidence,
                'confidence_effectiveness': profitable_confidence - losing_confidence,
                'total_pnl': sum(d.get('profit_loss', 0) for d in performance_data)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing profitability patterns: {e}")
            return {}
    
    def _analyze_parameter_effectiveness_with_profit(self, module_name: str, 
                                                   performance_data: List[Dict]) -> Dict[str, Dict]:
        """Enhanced parameter analysis weighted by profitability"""
        analysis = {}
        
        try:
            # Group data by parameter types with profit weighting
            param_groups = self._group_data_by_parameters(performance_data)
            
            for param_type, param_data in param_groups.items():
                if len(param_data) < 5:
                    continue
                
                # Calculate profit-weighted correlation
                profit_correlation = self._calculate_profit_weighted_correlation(param_type, param_data)
                variance = self._calculate_parameter_variance(param_type, param_data)
                
                # Calculate parameter impact on win rate
                win_rate_impact = self._calculate_win_rate_impact(param_type, param_data)
                
                # Determine optimization priority based on profit impact
                should_optimize = (
                    abs(profit_correlation) > 0.15 or  # Strong profit correlation
                    abs(win_rate_impact) > 0.1 or     # Significant win rate impact
                    (variance > 0.02 and len(param_data) >= 10)  # High variance with sufficient data
                )
                
                analysis[param_type] = {
                    'profit_correlation': profit_correlation,
                    'win_rate_impact': win_rate_impact,
                    'variance': variance,
                    'data_points': len(param_data),
                    'should_optimize': should_optimize,
                    'optimization_priority': abs(profit_correlation) + abs(win_rate_impact)
                }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in enhanced parameter analysis: {e}")
            return {}
    
    def _calculate_profit_weighted_correlation(self, param_type: str, param_data: List[Dict]) -> float:
        """Calculate correlation between parameter and profit with profit weighting"""
        try:
            param_values = []
            profit_values = []
            profit_weights = []
            
            for data_point in param_data:
                param_val = data_point.get(param_type)
                profit_val = data_point.get('profit_loss', 0.0)
                
                if param_val is not None and isinstance(param_val, (int, float)):
                    param_values.append(float(param_val))
                    profit_values.append(profit_val)
                    # Weight profitable trades more heavily
                    weight = 2.0 if profit_val > 0 else 1.0
                    profit_weights.append(weight)
            
            if len(param_values) < 3:
                return 0.0
            
            # Calculate weighted correlation
            weighted_param = np.average(param_values, weights=profit_weights)
            weighted_profit = np.average(profit_values, weights=profit_weights)
            
            # Calculate weighted covariance and standard deviations
            param_deviations = [(p - weighted_param) * w for p, w in zip(param_values, profit_weights)]
            profit_deviations = [(p - weighted_profit) * w for p, w in zip(profit_values, profit_weights)]
            
            covariance = np.mean([pd * pfd for pd, pfd in zip(param_deviations, profit_deviations)])
            param_std = np.sqrt(np.mean([pd ** 2 for pd in param_deviations]))
            profit_std = np.sqrt(np.mean([pfd ** 2 for pfd in profit_deviations]))
            
            if param_std == 0 or profit_std == 0:
                return 0.0
            
            correlation = covariance / (param_std * profit_std)
            return correlation if not np.isnan(correlation) else 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_win_rate_impact(self, param_type: str, param_data: List[Dict]) -> float:
        """Calculate how parameter values impact win rate"""
        try:
            # Split data into high/low parameter value groups
            param_values = [d.get(param_type) for d in param_data if d.get(param_type) is not None]
            if len(param_values) < 6:
                return 0.0
            
            median_param = np.median(param_values)
            
            high_param_data = [d for d in param_data if d.get(param_type, 0) >= median_param]
            low_param_data = [d for d in param_data if d.get(param_type, 0) < median_param]
            
            if len(high_param_data) < 3 or len(low_param_data) < 3:
                return 0.0
            
            # Calculate win rates for each group
            high_wins = sum(1 for d in high_param_data if d.get('profit_loss', 0) > 0)
            high_win_rate = high_wins / len(high_param_data)
            
            low_wins = sum(1 for d in low_param_data if d.get('profit_loss', 0) > 0)
            low_win_rate = low_wins / len(low_param_data)
            
            # Return difference in win rates
            return high_win_rate - low_win_rate
            
        except Exception:
            return 0.0
    
    def _optimize_single_parameter_for_profit(self, module_name: str, param_type: str,
                                            performance_data: List[Dict],
                                            current_params: Dict[str, Any],
                                            profit_analysis: Dict[str, Any]) -> Optional[ParameterOptimizationResult]:
        """Optimize parameter specifically for profitability"""
        try:
            # Use existing optimization but weight by profitability
            if param_type in self.parameter_bounds:
                result = self._optimize_continuous_parameter_for_profit(
                    module_name, param_type, performance_data, current_params, profit_analysis
                )
            else:
                result = self._optimize_discrete_parameter_for_profit(
                    module_name, param_type, performance_data, current_params, profit_analysis
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error optimizing parameter {param_type} for profit: {e}")
            return None
    
    def _optimize_continuous_parameter_for_profit(self, module_name: str, param_type: str,
                                                performance_data: List[Dict],
                                                current_params: Dict[str, Any],
                                                profit_analysis: Dict[str, Any]) -> Optional[ParameterOptimizationResult]:
        """Optimize continuous parameter with profit weighting"""
        try:
            # Filter to only profitable trades for parameter suggestions
            profitable_data = [d for d in performance_data if d.get('profit_loss', 0) > 0]
            
            if len(profitable_data) < 3:
                # Fall back to regular optimization if insufficient profitable trades
                return self._optimize_continuous_parameter(module_name, param_type, performance_data, current_params)
            
            # Get optimal parameter values from profitable trades
            profitable_param_values = [d.get(param_type) for d in profitable_data if d.get(param_type) is not None]
            
            if not profitable_param_values:
                return None
            
            # Calculate optimal value as weighted average of profitable parameters
            weights = [d.get('profit_loss', 1.0) for d in profitable_data if d.get(param_type) is not None]
            optimal_value = np.average(profitable_param_values, weights=weights)
            
            # Ensure within bounds
            bounds = self.parameter_bounds[param_type]
            optimal_value = max(bounds[0], min(bounds[1], optimal_value))
            
            current_value = current_params.get(param_type, 0.5)
            
            # Only suggest change if improvement is significant
            if abs(optimal_value - current_value) < 0.03:
                return None
            
            # Estimate improvement based on profit analysis
            expected_improvement = min(0.15, profit_analysis.get('profit_factor', 1.0) * 0.05)
            
            return ParameterOptimizationResult(
                module_name=module_name,
                parameter_type=param_type,
                old_value=current_value,
                new_value=optimal_value,
                expected_improvement=expected_improvement,
                confidence=min(0.85, len(profitable_data) / 20),
                optimization_method="profit_weighted_continuous",
                data_points_used=len(profitable_data)
            )
            
        except Exception as e:
            self.logger.error(f"Error in profit-weighted continuous optimization: {e}")
            return None
    
    def _optimize_discrete_parameter_for_profit(self, module_name: str, param_type: str,
                                              performance_data: List[Dict],
                                              current_params: Dict[str, Any],
                                              profit_analysis: Dict[str, Any]) -> Optional[ParameterOptimizationResult]:
        """Optimize discrete parameter based on profitability"""
        try:
            # Group by parameter value and calculate profit metrics
            value_performance = {}
            
            for data_point in performance_data:
                param_value = data_point.get(param_type)
                if param_value is not None:
                    if param_value not in value_performance:
                        value_performance[param_value] = {'profits': [], 'total_pnl': 0.0, 'win_rate': 0.0}
                    
                    profit_loss = data_point.get('profit_loss', 0.0)
                    value_performance[param_value]['profits'].append(profit_loss)
                    value_performance[param_value]['total_pnl'] += profit_loss
            
            # Calculate win rates and average profits for each value
            best_value = None
            best_score = float('-inf')
            
            for value, perf in value_performance.items():
                if len(perf['profits']) >= 3:
                    wins = sum(1 for p in perf['profits'] if p > 0)
                    win_rate = wins / len(perf['profits'])
                    avg_profit = perf['total_pnl'] / len(perf['profits'])
                    
                    # Combined score: win rate + average profit
                    score = win_rate * 0.6 + (avg_profit / 100) * 0.4  # Normalize profit impact
                    
                    if score > best_score:
                        best_score = score
                        best_value = value
            
            current_value = current_params.get(param_type)
            
            if best_value is None or best_value == current_value:
                return None
            
            return ParameterOptimizationResult(
                module_name=module_name,
                parameter_type=param_type,
                old_value=current_value,
                new_value=best_value,
                expected_improvement=best_score,
                confidence=0.7,
                optimization_method="profit_weighted_discrete",
                data_points_used=len(performance_data)
            )
            
        except Exception as e:
            self.logger.error(f"Error in profit-weighted discrete optimization: {e}")
            return None