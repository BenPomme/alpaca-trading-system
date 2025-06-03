"""
Modular Trading Orchestrator

This module coordinates all trading modules (Options, Crypto, Stocks) and provides
centralized cycle management, performance monitoring, and ML optimization integration.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from modular.base_module import (
    TradingModule, ModuleRegistry, ModuleHealth, ModuleHealthStatus,
    TradeOpportunity, TradeResult, ModuleConfig
)
from modular.ml_optimizer import MLParameterOptimizationEngine


class ModularOrchestrator:
    """
    Orchestrates multiple trading modules with centralized coordination.
    
    Responsibilities:
    - Coordinate trading cycles across all modules
    - Monitor module health and performance
    - Integrate with ML optimization system
    - Handle Firebase data persistence
    - Provide unified logging and monitoring
    """
    
    def __init__(self, 
                 firebase_db,
                 risk_manager,
                 order_executor,
                 ml_optimizer=None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the modular orchestrator.
        
        Args:
            firebase_db: Firebase database interface
            risk_manager: Risk management service
            order_executor: Order execution service
            ml_optimizer: ML optimization service (optional)
            logger: Optional logger instance
        """
        self.firebase_db = firebase_db
        self.risk_manager = risk_manager
        self.order_executor = order_executor
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # Initialize ML optimizer if not provided
        if ml_optimizer is None and firebase_db:
            try:
                self.ml_optimizer = MLParameterOptimizationEngine(firebase_db, self, self.logger)
                self.logger.info("Auto-created ML optimization engine")
            except Exception as e:
                self.logger.warning(f"Could not create ML optimizer: {e}")
                self.ml_optimizer = None
        else:
            self.ml_optimizer = ml_optimizer
        
        # Initialize portfolio rebalancer for diversification
        try:
            from portfolio_rebalancer import PortfolioRebalancer
            self.portfolio_rebalancer = PortfolioRebalancer(
                orchestrator=self,
                firebase_db=firebase_db,
                logger=self.logger
            )
            self.logger.info("✅ Portfolio rebalancer initialized for diversification management")
        except Exception as e:
            self.logger.warning(f"⚠️ Portfolio rebalancer initialization failed: {e}")
            self.portfolio_rebalancer = None
        
        # Module management
        self.registry = ModuleRegistry()
        self._cycle_count = 0
        self._last_cycle_time = None
        self._cycle_delay = 120  # Default 2 minutes
        
        # Performance tracking
        self._orchestrator_metrics = {
            'total_cycles': 0,
            'total_opportunities': 0,
            'total_trades': 0,
            'successful_trades': 0,
            'start_time': datetime.now(),
            'uptime_hours': 0.0
        }
        
        # CRITICAL SAFETY: Emergency stop only (CIRCUIT BREAKER REMOVED per user request)
        self._emergency_stop = False
        
        # Configuration
        self._config = {
            'max_concurrent_modules': 3,
            'cycle_timeout_seconds': 300,  # 5 minutes
            'health_check_interval': 600,  # 10 minutes
            'optimization_interval': 1800,  # 30 minutes
            'enable_parallel_execution': True
        }
        
        self.logger.info("Modular Trading Orchestrator initialized")
    
    def register_module(self, module: TradingModule):
        """Register a trading module with the orchestrator"""
        self.registry.register_module(module)
        self.logger.info(f"Registered module: {module.module_name}")
    
    def start_trading_loop(self, cycle_delay: int = 120):
        """
        Start the main trading loop.
        
        Args:
            cycle_delay: Delay between cycles in seconds
        """
        self._cycle_delay = cycle_delay
        self.logger.info(f"Starting trading loop with {cycle_delay}s cycle delay")
        
        try:
            while True:
                cycle_start = time.time()
                
                # Run trading cycle
                self._run_trading_cycle()
                
                # Update metrics
                self._update_orchestrator_metrics()
                
                # Periodic maintenance
                self._run_periodic_maintenance()
                
                # Calculate next cycle delay
                cycle_duration = time.time() - cycle_start
                next_delay = max(0, self._cycle_delay - cycle_duration)
                
                self.logger.info(f"Cycle {self._cycle_count} completed in {cycle_duration:.1f}s, "
                               f"next cycle in {next_delay:.1f}s")
                
                if next_delay > 0:
                    time.sleep(next_delay)
                    
        except KeyboardInterrupt:
            self.logger.info("Trading loop interrupted by user")
        except Exception as e:
            self.logger.error(f"Trading loop error: {e}")
            raise
        finally:
            self._cleanup()
    
    def run_single_cycle(self) -> Dict[str, Any]:
        """
        Run a single trading cycle and return results.
        
        Returns:
            Dictionary with cycle results and metrics
        """
        cycle_start = time.time()
        self.logger.info(f"Starting trading cycle {self._cycle_count + 1}")
        
        try:
            results = self._run_trading_cycle()
            cycle_duration = time.time() - cycle_start
            
            # Update orchestrator metrics after cycle completion
            self._update_orchestrator_metrics()
            
            results['cycle_info'] = {
                'cycle_number': self._cycle_count,
                'duration_seconds': cycle_duration,
                'timestamp': datetime.now().isoformat()
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}")
            return {
                'success': False,
                'error': str(e),
                'cycle_info': {
                    'cycle_number': self._cycle_count,
                    'duration_seconds': time.time() - cycle_start,
                    'timestamp': datetime.now().isoformat()
                }
            }
    
    def _run_trading_cycle(self) -> Dict[str, Any]:
        """Execute a complete trading cycle across all modules"""
        self._cycle_count += 1
        
        # CRITICAL SAFETY: Check emergency stop only
        if self._check_emergency_stop():
            return {
                'success': False,
                'error': 'EMERGENCY STOP ACTIVE - Trading halted for safety',
                'modules': {},
                'summary': {
                    'total_opportunities': 0,
                    'total_trades': 0,
                    'trades_passed': 0,
                    'successful_trades': 0
                }
            }
        
        cycle_results = {
            'success': True,
            'modules': {},
            'summary': {
                'total_opportunities': 0,
                'total_trades': 0,
                'trades_passed': 0,      # Orders successfully executed
                'successful_trades': 0   # Profitable trades only
            }
        }
        
        # Get active modules
        active_modules = self.registry.get_active_modules()
        if not active_modules:
            self.logger.warning("No active modules found")
            return cycle_results
        
        try:
            # Execute modules in parallel or sequential
            if self._config['enable_parallel_execution']:
                module_results = self._run_modules_parallel(active_modules)
            else:
                module_results = self._run_modules_sequential(active_modules)
            
            # Process results
            for module_name, result in module_results.items():
                cycle_results['modules'][module_name] = result
                
                if result['success']:
                    cycle_results['summary']['total_opportunities'] += result['opportunities_count']
                    cycle_results['summary']['total_trades'] += result['trades_count']
                    cycle_results['summary']['trades_passed'] += result['trades_passed']
                    cycle_results['summary']['successful_trades'] += result['successful_trades']
                    
                    # CRITICAL SAFETY: Record trades for circuit breaker monitoring
                    if result['trades_count'] > 0:
                        # Estimate losses (trade failures and unprofitable trades)
                        failed_trades = result['trades_count'] - result['trades_passed']
                        unprofitable_trades = result['trades_passed'] - result['successful_trades']
                        estimated_losses = (failed_trades * 100) + (unprofitable_trades * 500)  # Rough estimate
                        
                        # Circuit breaker removed per user request - no trade recording
                else:
                    # Update module health on failure
                    self.registry.update_health(
                        module_name, 
                        ModuleHealthStatus.ERROR,
                        result.get('error', 'Unknown error')
                    )
            
            # Save cycle results to Firebase
            self._save_cycle_results(cycle_results)
            
            return cycle_results
            
        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}")
            cycle_results['success'] = False
            cycle_results['error'] = str(e)
            return cycle_results
    
    def _run_modules_parallel(self, modules: List[TradingModule]) -> Dict[str, Any]:
        """Run multiple modules in parallel"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=self._config['max_concurrent_modules']) as executor:
            # Submit all module tasks
            future_to_module = {
                executor.submit(self._run_single_module, module): module.module_name
                for module in modules
            }
            
            # Collect results with timeout
            for future in as_completed(future_to_module, timeout=self._config['cycle_timeout_seconds']):
                module_name = future_to_module[future]
                try:
                    results[module_name] = future.result()
                except Exception as e:
                    self.logger.error(f"Module {module_name} failed: {e}")
                    results[module_name] = {
                        'success': False,
                        'error': str(e),
                        'opportunities_count': 0,
                        'trades_count': 0,
                        'successful_trades': 0
                    }
        
        return results
    
    def _run_modules_sequential(self, modules: List[TradingModule]) -> Dict[str, Any]:
        """Run modules sequentially"""
        results = {}
        
        for module in modules:
            try:
                results[module.module_name] = self._run_single_module(module)
            except Exception as e:
                self.logger.error(f"Module {module.module_name} failed: {e}")
                results[module.module_name] = {
                    'success': False,
                    'error': str(e),
                    'opportunities_count': 0,
                    'trades_count': 0,
                    'successful_trades': 0
                }
        
        return results
    
    def _run_single_module(self, module: TradingModule) -> Dict[str, Any]:
        """Run a complete cycle for a single module"""
        module_start = time.time()
        result = {
            'success': False,
            'opportunities_count': 0,
            'trades_count': 0,
            'trades_passed': 0,        # Orders successfully executed
            'successful_trades': 0,    # Profitable trades only
            'exits_count': 0,
            'duration_seconds': 0.0
        }
        
        try:
            # EXPLICIT MODULE EXECUTION LOGGING
            self.logger.info(f"🔄 EXECUTING MODULE: {module.module_name}")
            
            # 1. Analyze opportunities
            self.logger.info(f"📊 {module.module_name}: Starting opportunity analysis...")
            opportunities = module.analyze_opportunities()
            result['opportunities_count'] = len(opportunities)
            self.logger.info(f"📊 {module.module_name}: Found {len(opportunities)} opportunities")
            
            # 2. Validate and filter opportunities
            valid_opportunities = [
                opp for opp in opportunities 
                if module.validate_opportunity(opp)
            ]
            
            # 3. Execute valid trades
            trade_results = []
            if valid_opportunities:
                self.logger.info(f"🚀 {module.module_name}: Executing {len(valid_opportunities)} valid trades...")
                trade_results = module.execute_trades(valid_opportunities)
                result['trades_count'] = len(trade_results)
                result['trades_passed'] = sum(1 for tr in trade_results if tr.passed)
                result['successful_trades'] = sum(1 for tr in trade_results if tr.success)
                self.logger.info(f"✅ {module.module_name}: {result['trades_passed']} passed, {result['successful_trades']} profitable")
            else:
                self.logger.info(f"⚠️ {module.module_name}: No valid opportunities to execute")
            
            # 4. Monitor existing positions for exits
            self.logger.info(f"👁️ {module.module_name}: Monitoring positions for exits...")
            exit_results = module.monitor_positions()
            result['exits_count'] = len(exit_results)
            self.logger.info(f"🚪 {module.module_name}: {len(exit_results)} exit actions taken")
            
            # Include exit results in trade counting
            if exit_results:
                all_trades = trade_results + exit_results
                result['trades_count'] = len(all_trades)
                result['trades_passed'] = sum(1 for tr in all_trades if tr.passed)
                result['successful_trades'] = sum(1 for tr in all_trades if tr.success)
            
            # 5. Save results
            for opp in opportunities:
                module.save_opportunity(opp)
            
            for trade_result in trade_results + exit_results:
                module.save_result(trade_result)
            
            # 6. Update module health
            self.registry.update_health(module.module_name, ModuleHealthStatus.HEALTHY)
            
            result['success'] = True
            result['duration_seconds'] = time.time() - module_start
            
            self.logger.info(f"📊 {module.module_name}: {result['opportunities_count']} opps, "
                            f"{result['trades_count']} trades ({result['trades_passed']} passed, "
                            f"{result['successful_trades']} profitable), {result['exits_count']} exits")
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            result['duration_seconds'] = time.time() - module_start
            self.logger.error(f"Error running {module.module_name}: {e}")
            return result
    
    def _save_cycle_results(self, cycle_results: Dict[str, Any]):
        """Save cycle results to Firebase"""
        try:
            cycle_data = {
                'timestamp': datetime.now().isoformat(),
                'cycle_number': self._cycle_count,
                'orchestrator_version': 'modular_v1',
                'results': cycle_results,
                'metrics': self._orchestrator_metrics.copy()
            }
            
            self.firebase_db.save_orchestrator_cycle(cycle_data)
            
        except Exception as e:
            self.logger.error(f"Error saving cycle results: {e}")
    
    def _update_orchestrator_metrics(self):
        """Update orchestrator performance metrics"""
        self._orchestrator_metrics['total_cycles'] = self._cycle_count
        self._orchestrator_metrics['uptime_hours'] = (
            (datetime.now() - self._orchestrator_metrics['start_time']).total_seconds() / 3600
        )
    
    def _run_periodic_maintenance(self):
        """Run periodic maintenance tasks"""
        now = datetime.now()
        
        # Health checks
        if (self._last_cycle_time is None or 
            (now - self._last_cycle_time).total_seconds() >= self._config['health_check_interval']):
            self._run_health_checks()
        
        # ML optimization
        if (self.ml_optimizer and 
            self._cycle_count % (self._config['optimization_interval'] // self._cycle_delay) == 0):
            self._run_ml_optimization()
        
        # Portfolio rebalancing (run every 10 cycles for diversification)
        if (self.portfolio_rebalancer and self._cycle_count % 10 == 0):
            self._run_portfolio_rebalancing()
        
        self._last_cycle_time = now
    
    def _run_health_checks(self):
        """Run health checks on all modules"""
        try:
            for module in self.registry._modules.values():
                # Check if module is responsive
                try:
                    performance = module.get_performance_summary()
                    if performance:
                        self.registry.update_health(module.module_name, ModuleHealthStatus.HEALTHY)
                    else:
                        self.registry.update_health(
                            module.module_name, 
                            ModuleHealthStatus.WARNING,
                            "No performance data available"
                        )
                except Exception as e:
                    self.registry.update_health(
                        module.module_name,
                        ModuleHealthStatus.ERROR, 
                        f"Health check failed: {e}"
                    )
        except Exception as e:
            self.logger.error(f"Error running health checks: {e}")
    
    def _run_ml_optimization(self):
        """Run ML optimization across all modules"""
        try:
            if not self.ml_optimizer:
                return
                
            self.logger.info("Running ML parameter optimization")
            
            # Run optimization cycle using new ML optimization engine
            optimization_summary = self.ml_optimizer.run_optimization_cycle()
            
            # Log optimization results
            if optimization_summary.get('optimizations_applied', 0) > 0:
                self.logger.info(f"ML Optimization Applied: {optimization_summary['optimizations_applied']} parameters updated, "
                               f"expected improvement: {optimization_summary.get('total_expected_improvement', 0):.1%}")
            else:
                self.logger.debug("ML Optimization: No parameter changes applied this cycle")
                    
        except Exception as e:
            self.logger.error(f"Error running ML optimization: {e}")
    
    def _run_portfolio_rebalancing(self):
        """Run portfolio rebalancing for diversification"""
        try:
            if not self.portfolio_rebalancer:
                return
            
            self.logger.info("🔄 Running portfolio rebalancing analysis...")
            
            # Get rebalancing recommendations
            recommendations = self.portfolio_rebalancer.get_rebalancing_recommendations()
            
            if recommendations.get('error'):
                self.logger.error(f"Portfolio analysis error: {recommendations['error']}")
                return
            
            portfolio_snapshot = recommendations.get('portfolio_snapshot', {})
            actions = recommendations.get('recommendations', [])
            
            # Log current portfolio state
            self.logger.info(f"📊 Portfolio: ${portfolio_snapshot.get('total_value', 0):,.0f}, "
                           f"{portfolio_snapshot.get('position_count', 0)} positions, "
                           f"largest: {portfolio_snapshot.get('largest_position_pct', 0):.1%}")
            
            # Execute high-priority rebalancing if needed
            critical_actions = [a for a in actions if a.get('urgency') in ['critical', 'high']]
            
            if critical_actions:
                self.logger.warning(f"🚨 Found {len(critical_actions)} critical rebalancing needs")
                
                # Convert back to RebalanceAction objects for execution
                from portfolio_rebalancer import RebalanceAction, RebalanceReason
                
                action_objects = []
                for action_dict in critical_actions[:3]:  # Limit to top 3
                    try:
                        action_obj = RebalanceAction(
                            symbol=action_dict['symbol'],
                            module=action_dict['module'],
                            current_weight=float(action_dict['current_weight'].replace('%', '')) / 100,
                            target_weight=float(action_dict['target_weight'].replace('%', '')) / 100,
                            action_type=action_dict['action'],
                            amount_usd=action_dict['amount_usd'],
                            reason=RebalanceReason(action_dict['reason']),
                            urgency=action_dict['urgency']
                        )
                        action_objects.append(action_obj)
                    except Exception as e:
                        self.logger.error(f"Error converting action: {e}")
                
                if action_objects:
                    execution_summary = self.portfolio_rebalancer.execute_rebalancing(action_objects)
                    
                    self.logger.info(f"✅ Rebalancing executed: {execution_summary.get('actions_executed', 0)} actions, "
                                   f"${execution_summary.get('total_value_rebalanced', 0):,.0f} rebalanced")
            else:
                diversification_score = portfolio_snapshot.get('diversification_score', 0)
                self.logger.info(f"✅ Portfolio balanced (diversification: {diversification_score:.2f})")
            
        except Exception as e:
            self.logger.error(f"Error in portfolio rebalancing: {e}")
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary for rebalancing analysis"""
        try:
            # Aggregate data from all modules
            all_positions = []
            total_value = 100000  # Default portfolio value
            
            # Get account value from risk manager or API
            if hasattr(self.risk_manager, 'get_portfolio_value'):
                total_value = self.risk_manager.get_portfolio_value()
            
            # Collect positions from all active modules
            for module in self.registry.get_active_modules():
                try:
                    if hasattr(module, '_get_positions'):
                        module_positions = module._get_positions()
                        for pos in module_positions:
                            pos['module'] = module.module_name
                            all_positions.append(pos)
                    elif hasattr(module, '_get_crypto_positions'):
                        crypto_positions = module._get_crypto_positions()
                        for pos in crypto_positions:
                            pos['module'] = module.module_name
                            all_positions.append(pos)
                    elif hasattr(module, '_get_stock_positions'):
                        stock_positions = module._get_stock_positions()
                        for pos in stock_positions:
                            pos['module'] = module.module_name
                            all_positions.append(pos)
                except Exception as e:
                    self.logger.debug(f"Could not get positions from {module.module_name}: {e}")
            
            return {
                'portfolio_value': total_value,
                'positions': all_positions,
                'position_count': len(all_positions),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return {
                'portfolio_value': 100000,
                'positions': [],
                'position_count': 0,
                'error': str(e)
            }
    
    def _cleanup(self):
        """Cleanup resources on shutdown"""
        self.logger.info("Shutting down modular orchestrator")
        
        # Attempt to save ML states via ml_optimizer
        if self.ml_optimizer:
            self.logger.info("Attempting to save final ML model states via ml_optimizer on cleanup...")
            # Check for a direct save method or a method to get the ML framework
            if hasattr(self.ml_optimizer, 'save_ml_states_to_firebase') and callable(self.ml_optimizer.save_ml_states_to_firebase):
                try:
                    self.ml_optimizer.save_ml_states_to_firebase()
                    self.logger.info("ML states saved via ml_optimizer.save_ml_states_to_firebase() on cleanup.")
                except Exception as e:
                    self.logger.error(f"Error saving ML states via ml_optimizer.save_ml_states_to_firebase() on cleanup: {e}")
            elif (hasattr(self.ml_optimizer, 'ml_adaptive_framework') and 
                  hasattr(self.ml_optimizer.ml_adaptive_framework, 'save_ml_states_to_firebase') and 
                  callable(self.ml_optimizer.ml_adaptive_framework.save_ml_states_to_firebase)):
                try:
                    self.ml_optimizer.ml_adaptive_framework.save_ml_states_to_firebase()
                    self.logger.info("ML states saved via ml_optimizer.ml_adaptive_framework.save_ml_states_to_firebase() on cleanup.")
                except Exception as e:
                    self.logger.error(f"Error saving ML states via ml_optimizer.ml_adaptive_framework.save_ml_states_to_firebase() on cleanup: {e}")
            elif hasattr(self.ml_optimizer, 'shutdown'): # Fallback if specific save method not found, assuming shutdown handles it
                self.logger.info("ML optimizer has a shutdown method, assuming it handles final state saving if necessary.")
            else:
                self.logger.warning("ml_optimizer does not have a recognized method to save ML states on cleanup.")

        # Save final metrics
        try:
            final_metrics = {
                'shutdown_time': datetime.now().isoformat(),
                'final_metrics': self._orchestrator_metrics.copy(),
                'module_health': self.registry.get_health_summary()
            }
            self.firebase_db.save_orchestrator_shutdown(final_metrics)
        except Exception as e:
            self.logger.error(f"Error saving shutdown metrics: {e}")
    
    # Public interface methods
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            'orchestrator_metrics': self._orchestrator_metrics.copy(),
            'module_health': self.registry.get_health_summary(),
            'active_modules': len(self.registry.get_active_modules()),
            'total_modules': len(self.registry._modules),
            'uptime_hours': self._orchestrator_metrics['uptime_hours'],
            'last_cycle': self._cycle_count
        }
    
    def enable_module(self, module_name: str):
        """Enable a trading module"""
        module = self.registry.get_module(module_name)
        if module:
            module.config.enabled = True
            self.logger.info(f"Enabled module: {module_name}")
        else:
            self.logger.warning(f"Module not found: {module_name}")
    
    def disable_module(self, module_name: str):
        """Disable a trading module"""
        module = self.registry.get_module(module_name)
        if module:
            module.config.enabled = False
            self.logger.info(f"Disabled module: {module_name}")
        else:
            self.logger.warning(f"Module not found: {module_name}")
    
    def update_module_config(self, module_name: str, config_updates: Dict[str, Any]):
        """Update configuration for a specific module"""
        module = self.registry.get_module(module_name)
        if module:
            for key, value in config_updates.items():
                if hasattr(module.config, key):
                    setattr(module.config, key, value)
                else:
                    module.config.custom_params[key] = value
            self.logger.info(f"Updated config for {module_name}: {config_updates}")
        else:
            self.logger.warning(f"Module not found: {module_name}")
    
    def get_module_performance(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get performance summary for a specific module"""
        module = self.registry.get_module(module_name)
        if module:
            return module.get_performance_summary()
        return None
    
    def _check_emergency_stop(self) -> bool:
        """Check if manual emergency stop is active (circuit breaker removed per user request)."""
        if self._emergency_stop:
            self.logger.error("🚨 EMERGENCY STOP: Manual halt active")
            return True
        
        return False
    
    def trigger_emergency_stop(self, reason: str):
        """Manually trigger emergency stop."""
        self._emergency_stop = True
        self.logger.critical(f"🚨 EMERGENCY STOP TRIGGERED: {reason}")
    
    def reset_emergency_stop(self):
        """Reset emergency stop."""
        self._emergency_stop = False
        self.logger.warning("⚠️ EMERGENCY STOP RESET - Trading resumed")
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety system status (circuit breaker removed per user request)."""
        return {
            'emergency_stop': self._emergency_stop,
            'circuit_breaker_removed': True,
            'status': 'Emergency stop only - circuit breaker disabled'
        }

    def shutdown(self):
        """Gracefully shutdown the orchestrator and all modules"""
        try:
            self.logger.info("🛑 Shutting down modular orchestrator...")
            
            # Stop any running cycles or background tasks
            if hasattr(self, '_running'):
                self._running = False
            
            # Shutdown all modules
            for module_name, module in self.registry._modules.items():
                try:
                    if hasattr(module, 'shutdown'):
                        module.shutdown()
                    self.logger.info(f"✅ Shutdown module: {module_name}")
                except Exception as e:
                    self.logger.error(f"❌ Error shutting down module {module_name}: {e}")
            
            # Shutdown ML optimizer
            if self.ml_optimizer and hasattr(self.ml_optimizer, 'shutdown'):
                try:
                    self.ml_optimizer.shutdown()
                    self.logger.info("✅ ML optimizer shutdown complete")
                except Exception as e:
                    self.logger.error(f"❌ ML optimizer shutdown error: {e}")
            
            self.logger.info("✅ Modular orchestrator shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Error during orchestrator shutdown: {e}")