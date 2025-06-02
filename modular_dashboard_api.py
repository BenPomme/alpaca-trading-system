#!/usr/bin/env python3
"""
Modular Trading Dashboard API with ML Optimization Monitoring

Enhanced dashboard API that connects to Firebase for real-time data from the 
modular trading architecture including ML parameter optimization monitoring.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import alpaca_trade_api as tradeapi

# Import modular components
from modular.firebase_interface import ModularFirebaseInterface
from firebase_database import FirebaseDatabase
from standardized_metrics import StandardizedMetrics, get_standardized_metrics_summary


class ModularDashboardAPI:
    """Enhanced dashboard API for modular trading architecture"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize Firebase connections
        self.firebase_db = FirebaseDatabase()
        self.modular_interface = ModularFirebaseInterface(self.firebase_db, self.logger)
        
        # Initialize standardized metrics calculator
        self.metrics_calculator = StandardizedMetrics()
        
        # Initialize Alpaca API for real-time account data
        api_key = os.getenv('ALPACA_PAPER_API_KEY')
        secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
        
        if api_key and secret_key:
            try:
                self.api = tradeapi.REST(
                    key_id=api_key,
                    secret_key=secret_key,
                    base_url='https://paper-api.alpaca.markets',
                    api_version='v2'
                )
                # Test connection
                account = self.api.get_account()
                self.logger.info(f"✅ Alpaca API connected: Portfolio Value: ${account.portfolio_value}")
            except Exception as e:
                self.logger.warning(f"⚠️ Alpaca API connection failed: {e}")
                self.api = None
        else:
            self.api = None
            self.logger.warning("⚠️ Alpaca API credentials not found")
    
    def generate_enhanced_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data for modular architecture"""
        try:
            self.logger.info("📊 Generating enhanced modular dashboard data...")
            
            dashboard_data = {
                # Core portfolio and trading data
                'portfolio': self.get_portfolio_data(),
                'positions': self.get_positions_data(),
                'trades': self.get_recent_trades(),
                'performance': self.calculate_performance_metrics(),
                
                # Module-specific performance
                'modules': self.get_module_performance(),
                'orchestrator': self.get_orchestrator_status(),
                
                # ML optimization data
                'ml_optimization': self.get_ml_optimization_data(),
                'parameter_effectiveness': self.get_parameter_effectiveness(),
                
                # Real-time system status
                'system_health': self.get_system_health(),
                'market_status': self.get_market_status(),
                
                # Strategy analysis
                'strategy_performance': self.get_strategy_performance(),
                
                # Metadata
                'generated_at': datetime.now().isoformat(),
                'data_source': 'modular_firebase' if self.firebase_db.is_connected() else 'fallback',
                'firebase_connected': self.firebase_db.is_connected(),
                'alpaca_connected': self.api is not None
            }
            
            self.logger.info(f"✅ Enhanced dashboard data generated successfully")
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"❌ Error generating dashboard data: {e}")
            return self.get_fallback_data()
    
    def get_portfolio_data(self) -> Dict[str, Any]:
        """Get portfolio data from Alpaca API"""
        try:
            if not self.api:
                return self.get_mock_portfolio_data()
            
            account = self.api.get_account()
            
            # Calculate additional metrics
            portfolio_value = float(account.portfolio_value)
            last_equity = float(account.last_equity)
            daily_pl = portfolio_value - last_equity
            daily_pl_pct = (daily_pl / last_equity) * 100 if last_equity > 0 else 0
            
            return {
                'value': portfolio_value,
                'cash': float(account.cash),
                'equity': float(account.equity),
                'buying_power': float(account.buying_power),
                'regt_buying_power': float(account.regt_buying_power),
                'daytrading_buying_power': float(getattr(account, 'daytrading_buying_power', 0)),
                'daily_pl': daily_pl,
                'daily_pl_percent': daily_pl_pct,
                'long_market_value': float(account.long_market_value),
                'short_market_value': float(account.short_market_value),
                'currency': account.currency,
                'account_blocked': account.account_blocked,
                'trading_blocked': account.trading_blocked,
                'transfers_blocked': account.transfers_blocked,
                'pattern_day_trader': account.pattern_day_trader,
                'sma': float(account.sma) if hasattr(account, 'sma') else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio data: {e}")
            return self.get_mock_portfolio_data()
    
    def get_positions_data(self) -> List[Dict[str, Any]]:
        """Get current positions with enhanced module classification"""
        try:
            if not self.api:
                return self.get_mock_positions_data()
            
            positions = self.api.list_positions()
            positions_data = []
            
            for pos in positions:
                symbol = pos.symbol
                
                # Enhanced position classification
                position_type, module = self._classify_position(symbol)
                
                # Calculate enhanced metrics
                entry_price = float(pos.avg_entry_price) if hasattr(pos, 'avg_entry_price') else 0
                current_price = float(pos.market_value) / float(pos.qty) if float(pos.qty) != 0 else 0
                unrealized_pl = float(pos.unrealized_pl)
                unrealized_pl_pct = float(pos.unrealized_plpc) * 100
                
                # Get hold time and strategy from modular data
                hold_time = self._get_position_hold_time(symbol)
                strategy = self._get_position_strategy(symbol)
                
                position_data = {
                    'symbol': symbol,
                    'quantity': float(pos.qty),
                    'side': 'long' if float(pos.qty) > 0 else 'short',
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'market_value': float(pos.market_value),
                    'unrealized_pl': unrealized_pl,
                    'unrealized_pl_percent': unrealized_pl_pct,
                    'hold_time': hold_time,
                    'strategy': strategy,
                    'type': position_type,
                    'module': module,
                    'cost_basis': float(pos.cost_basis),
                    'asset_class': pos.asset_class if hasattr(pos, 'asset_class') else 'unknown'
                }
                
                positions_data.append(position_data)
            
            return positions_data
            
        except Exception as e:
            self.logger.error(f"Error getting positions data: {e}")
            return self.get_mock_positions_data()
    
    def get_recent_trades(self) -> List[Dict[str, Any]]:
        """Get recent trades from modular Firebase data"""
        try:
            if not self.firebase_db.is_connected():
                return self.get_mock_trades_data()
            
            # Get recent trades from modular collections
            recent_trades = []
            
            # Try to get from modular trades collection
            try:
                modular_trades = self.firebase_db.db.collection('modular_trades').order_by(
                    'timestamp', direction='DESCENDING'
                ).limit(100).get()
                
                for trade_doc in modular_trades:
                    trade_data = trade_doc.to_dict()
                    
                    formatted_trade = {
                        'id': trade_doc.id,
                        'timestamp': trade_data.get('timestamp'),
                        'symbol': trade_data.get('symbol'),
                        'action': trade_data.get('action'),
                        'strategy': trade_data.get('strategy'),
                        'module_name': trade_data.get('module_name'),
                        'status': trade_data.get('status'),
                        'execution_price': trade_data.get('execution_price'),
                        'pnl': trade_data.get('pnl'),
                        'pnl_pct': trade_data.get('pnl_pct'),
                        'hold_duration': trade_data.get('hold_duration'),
                        'exit_reason': trade_data.get('exit_reason'),
                        'confidence': trade_data.get('confidence'),
                        'ml_enhanced': trade_data.get('ml_enhanced', False)
                    }
                    
                    recent_trades.append(formatted_trade)
                    
            except Exception as e:
                self.logger.warning(f"Could not get modular trades: {e}")
            
            # Fallback to regular trades collection
            if not recent_trades:
                regular_trades = self.firebase_db.get_recent_trades(limit=100)
                for trade in regular_trades:
                    formatted_trade = {
                        'timestamp': trade.get('timestamp'),
                        'symbol': trade.get('symbol'),
                        'action': trade.get('side', 'UNKNOWN'),
                        'strategy': trade.get('strategy'),
                        'module_name': 'legacy',
                        'execution_price': trade.get('price'),
                        'pnl': trade.get('profit_loss'),
                        'confidence': trade.get('confidence')
                    }
                    recent_trades.append(formatted_trade)
            
            return recent_trades[:50]  # Return last 50 trades
            
        except Exception as e:
            self.logger.error(f"Error getting recent trades: {e}")
            return self.get_mock_trades_data()
    
    def get_module_performance(self) -> Dict[str, Any]:
        """Get performance data for each trading module"""
        try:
            module_performance = {}
            
            if not self.firebase_db.is_connected():
                return self.get_mock_module_performance()
            
            # Get performance for each module
            modules = ['options', 'crypto', 'stocks']
            
            for module_name in modules:
                try:
                    # Get module performance data using modular interface
                    perf_data = self.modular_interface.get_module_performance_data(module_name, days_back=7)
                    
                    if perf_data:
                        module_performance[module_name] = {
                            'total_trades': perf_data.get('total_trades', 0),
                            'successful_trades': perf_data.get('successful_trades', 0),
                            'win_rate': perf_data.get('win_rate', 0) * 100,
                            'total_pnl': perf_data.get('total_pnl', 0),
                            'avg_pnl': perf_data.get('avg_pnl', 0),
                            'avg_hold_time_hours': perf_data.get('avg_hold_time_hours', 0),
                            'period_days': perf_data.get('period_days', 7),
                            'last_trade': self._get_last_trade_for_module(module_name)
                        }
                    else:
                        module_performance[module_name] = self._get_empty_module_performance()
                        
                except Exception as e:
                    self.logger.warning(f"Error getting performance for {module_name}: {e}")
                    module_performance[module_name] = self._get_empty_module_performance()
            
            return module_performance
            
        except Exception as e:
            self.logger.error(f"Error getting module performance: {e}")
            return self.get_mock_module_performance()
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status and metrics"""
        try:
            if not self.firebase_db.is_connected():
                return self.get_mock_orchestrator_status()
            
            # Get recent orchestrator cycles
            recent_cycles = self.firebase_db.db.collection('orchestrator_cycles').order_by(
                'timestamp', direction='DESCENDING'
            ).limit(10).get()
            
            if not recent_cycles:
                return self.get_mock_orchestrator_status()
            
            latest_cycle = recent_cycles[0].to_dict()
            
            # Calculate orchestrator metrics
            total_cycles = len(recent_cycles)
            successful_cycles = sum(1 for cycle in recent_cycles if cycle.to_dict().get('results', {}).get('success', False))
            success_rate = (successful_cycles / total_cycles) * 100 if total_cycles > 0 else 0
            
            # Get summary from latest cycle
            latest_results = latest_cycle.get('results', {})
            latest_summary = latest_results.get('summary', {})
            
            return {
                'last_cycle_time': latest_cycle.get('timestamp'),
                'cycle_number': latest_cycle.get('cycle_number', 0),
                'success_rate': success_rate,
                'total_cycles_analyzed': total_cycles,
                'last_cycle_successful': latest_results.get('success', False),
                'modules_in_last_cycle': len(latest_results.get('modules', {})),
                'total_opportunities_last_cycle': latest_summary.get('total_opportunities', 0),
                'total_trades_last_cycle': latest_summary.get('total_trades', 0),
                'successful_trades_last_cycle': latest_summary.get('successful_trades', 0),
                'orchestrator_version': latest_cycle.get('orchestrator_version', 'unknown'),
                'uptime_status': 'running' if datetime.now() - datetime.fromisoformat(latest_cycle.get('timestamp', '2020-01-01')) < timedelta(minutes=10) else 'stale'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting orchestrator status: {e}")
            return self.get_mock_orchestrator_status()
    
    def get_ml_optimization_data(self) -> Dict[str, Any]:
        """Get ML parameter optimization status and history"""
        try:
            if not self.firebase_db.is_connected():
                return self.get_mock_ml_optimization_data()
            
            ml_data = {
                'optimization_enabled': True,
                'recent_optimizations': [],
                'parameter_changes_today': 0,
                'optimization_effectiveness': {},
                'next_optimization_due': None,
                'models_status': {}
            }
            
            # Get recent ML optimization data
            try:
                ml_optimization_docs = self.firebase_db.db.collection('ml_optimization_data').order_by(
                    'timestamp', direction='DESCENDING'
                ).limit(20).get()
                
                for opt_doc in ml_optimization_docs:
                    opt_data = opt_doc.to_dict()
                    
                    optimization_record = {
                        'timestamp': opt_data.get('timestamp'),
                        'module_name': opt_data.get('module_name'),
                        'parameter_type': opt_data.get('parameter_type'),
                        'old_value': opt_data.get('old_value'),
                        'new_value': opt_data.get('new_value'),
                        'expected_improvement': opt_data.get('expected_improvement'),
                        'confidence': opt_data.get('confidence'),
                        'optimization_method': opt_data.get('optimization_method'),
                        'applied': opt_data.get('applied', False)
                    }
                    
                    ml_data['recent_optimizations'].append(optimization_record)
                
                # Count optimizations today
                today = datetime.now().date()
                ml_data['parameter_changes_today'] = sum(
                    1 for opt in ml_data['recent_optimizations']
                    if opt.get('applied') and 
                    datetime.fromisoformat(opt.get('timestamp', '2020-01-01')).date() == today
                )
                
            except Exception as e:
                self.logger.warning(f"Could not get ML optimization data: {e}")
            
            # Get ML learning events
            try:
                ml_events = self.firebase_db.db.collection('ml_learning_events').order_by(
                    'timestamp', direction='DESCENDING'
                ).limit(10).get()
                
                recent_events = []
                for event_doc in ml_events:
                    event_data = event_doc.to_dict()
                    recent_events.append({
                        'timestamp': event_data.get('timestamp'),
                        'model_name': event_data.get('model_name'),
                        'learning_event': event_data.get('learning_event'),
                        'performance_impact': event_data.get('performance_impact')
                    })
                
                ml_data['recent_learning_events'] = recent_events
                
            except Exception as e:
                self.logger.warning(f"Could not get ML learning events: {e}")
                ml_data['recent_learning_events'] = []
            
            return ml_data
            
        except Exception as e:
            self.logger.error(f"Error getting ML optimization data: {e}")
            return self.get_mock_ml_optimization_data()
    
    def get_parameter_effectiveness(self) -> Dict[str, Any]:
        """Get parameter effectiveness analysis"""
        try:
            if not self.firebase_db.is_connected():
                return self.get_mock_parameter_effectiveness()
            
            effectiveness_data = {
                'parameters_tracked': 0,
                'top_performing_parameters': [],
                'underperforming_parameters': [],
                'parameter_correlations': {},
                'optimization_candidates': []
            }
            
            # Get parameter effectiveness data
            try:
                param_docs = self.firebase_db.db.collection('parameter_effectiveness').order_by(
                    'timestamp', direction='DESCENDING'
                ).limit(100).get()
                
                effectiveness_data['parameters_tracked'] = len(param_docs)
                
                # Analyze parameter performance
                param_analysis = {}
                for param_doc in param_docs:
                    param_data = param_doc.to_dict()
                    
                    param_type = param_data.get('parameter_type')
                    success = param_data.get('success', False)
                    profit_loss = param_data.get('profit_loss', 0)
                    
                    if param_type not in param_analysis:
                        param_analysis[param_type] = {
                            'total_trades': 0,
                            'successful_trades': 0,
                            'total_pnl': 0,
                            'parameter_values': []
                        }
                    
                    param_analysis[param_type]['total_trades'] += 1
                    if success:
                        param_analysis[param_type]['successful_trades'] += 1
                    param_analysis[param_type]['total_pnl'] += profit_loss
                    param_analysis[param_type]['parameter_values'].append(param_data.get('parameter_value'))
                
                # Identify top and underperforming parameters
                for param_type, analysis in param_analysis.items():
                    win_rate = (analysis['successful_trades'] / analysis['total_trades']) * 100 if analysis['total_trades'] > 0 else 0
                    avg_pnl = analysis['total_pnl'] / analysis['total_trades'] if analysis['total_trades'] > 0 else 0
                    
                    param_summary = {
                        'parameter_type': param_type,
                        'win_rate': win_rate,
                        'avg_pnl': avg_pnl,
                        'total_trades': analysis['total_trades']
                    }
                    
                    if win_rate > 60 and avg_pnl > 0:
                        effectiveness_data['top_performing_parameters'].append(param_summary)
                    elif win_rate < 40 or avg_pnl < -5:
                        effectiveness_data['underperforming_parameters'].append(param_summary)
                
                # Sort by performance
                effectiveness_data['top_performing_parameters'].sort(key=lambda x: x['avg_pnl'], reverse=True)
                effectiveness_data['underperforming_parameters'].sort(key=lambda x: x['avg_pnl'])
                
            except Exception as e:
                self.logger.warning(f"Could not analyze parameter effectiveness: {e}")
            
            return effectiveness_data
            
        except Exception as e:
            self.logger.error(f"Error getting parameter effectiveness: {e}")
            return self.get_mock_parameter_effectiveness()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            health_status = {
                'overall_status': 'healthy',
                'firebase_connection': self.firebase_db.is_connected(),
                'alpaca_connection': self.api is not None,
                'modules_status': {},
                'last_activity': None,
                'error_rate': 0.0,
                'uptime_hours': 0.0
            }
            
            # Check Firebase connection health
            if not self.firebase_db.is_connected():
                health_status['overall_status'] = 'degraded'
            
            # Check recent activity
            try:
                recent_cycles = self.firebase_db.db.collection('orchestrator_cycles').order_by(
                    'timestamp', direction='DESCENDING'
                ).limit(1).get()
                
                if recent_cycles:
                    latest_cycle = recent_cycles[0].to_dict()
                    health_status['last_activity'] = latest_cycle.get('timestamp')
                    
                    # Check if activity is recent (within last 10 minutes)
                    last_activity_time = datetime.fromisoformat(latest_cycle.get('timestamp', '2020-01-01'))
                    if datetime.now() - last_activity_time > timedelta(minutes=10):
                        health_status['overall_status'] = 'stale'
                        
            except Exception as e:
                self.logger.warning(f"Could not check recent activity: {e}")
                health_status['overall_status'] = 'unknown'
            
            # Check module health from recent cycles
            try:
                modules = ['options', 'crypto', 'stocks']
                for module_name in modules:
                    # Get recent trades for this module to assess health
                    recent_module_activity = self.firebase_db.db.collection('modular_trades').where(
                        'module_name', '==', module_name
                    ).order_by('timestamp', direction='DESCENDING').limit(10).get()
                    
                    if recent_module_activity:
                        health_status['modules_status'][module_name] = 'active'
                    else:
                        health_status['modules_status'][module_name] = 'inactive'
                        
            except Exception as e:
                self.logger.warning(f"Could not check module health: {e}")
                for module_name in ['options', 'crypto', 'stocks']:
                    health_status['modules_status'][module_name] = 'unknown'
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            return {
                'overall_status': 'error',
                'firebase_connection': False,
                'alpaca_connection': False,
                'error': str(e)
            }
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status"""
        try:
            if not self.api:
                return {'is_open': False, 'next_open': 'Unknown', 'next_close': 'Unknown'}
            
            clock = self.api.get_clock()
            
            return {
                'is_open': clock.is_open,
                'next_open': clock.next_open.isoformat() if clock.next_open else 'Unknown',
                'next_close': clock.next_close.isoformat() if clock.next_close else 'Unknown',
                'timezone': 'America/New_York'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting market status: {e}")
            return {'is_open': False, 'next_open': 'Unknown', 'next_close': 'Unknown'}
    
    def get_strategy_performance(self) -> List[Dict[str, Any]]:
        """Get performance breakdown by strategy"""
        try:
            if not self.firebase_db.is_connected():
                return self.get_mock_strategy_performance()
            
            strategy_stats = {}
            
            # Get recent trades and group by strategy
            recent_trades = self.get_recent_trades()
            
            for trade in recent_trades:
                strategy = trade.get('strategy', 'unknown')
                
                if strategy not in strategy_stats:
                    strategy_stats[strategy] = {
                        'total_trades': 0,
                        'successful_trades': 0,
                        'total_pnl': 0,
                        'module_name': trade.get('module_name', 'unknown')
                    }
                
                strategy_stats[strategy]['total_trades'] += 1
                if trade.get('pnl', 0) > 0:
                    strategy_stats[strategy]['successful_trades'] += 1
                strategy_stats[strategy]['total_pnl'] += trade.get('pnl', 0)
            
            # Convert to list format
            strategy_performance = []
            for strategy_name, stats in strategy_stats.items():
                win_rate = (stats['successful_trades'] / stats['total_trades']) * 100 if stats['total_trades'] > 0 else 0
                avg_pnl = stats['total_pnl'] / stats['total_trades'] if stats['total_trades'] > 0 else 0
                
                strategy_performance.append({
                    'strategy': strategy_name,
                    'module': stats['module_name'],
                    'total_trades': stats['total_trades'],
                    'win_rate': win_rate,
                    'total_pnl': stats['total_pnl'],
                    'avg_pnl': avg_pnl
                })
            
            # Sort by total P&L
            strategy_performance.sort(key=lambda x: x['total_pnl'], reverse=True)
            
            return strategy_performance
            
        except Exception as e:
            self.logger.error(f"Error getting strategy performance: {e}")
            return self.get_mock_strategy_performance()
    
    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        try:
            metrics = {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_pnl_per_trade': 0.0,
                'best_trade': 0.0,
                'worst_trade': 0.0,
                'avg_hold_time_hours': 0.0,
                'daily_roi': 0.0,
                'weekly_roi': 0.0,
                'monthly_roi': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0
            }
            
            # Get recent trades for analysis
            recent_trades = self.get_recent_trades()
            
            if recent_trades:
                # STANDARDIZED METRICS CALCULATION - FIX FOR WIN RATE INCONSISTENCY
                self.logger.info(f"📊 Calculating standardized metrics for {len(recent_trades)} trades")
                
                try:
                    # Use standardized metrics calculator
                    standardized_report = self.metrics_calculator.generate_performance_report(
                        recent_trades, 
                        source_format='firebase',
                        include_module_breakdown=False
                    )
                    
                    # Extract standardized metrics
                    std_metrics = standardized_report['overall_performance']['metrics']
                    std_counts = standardized_report['overall_performance']['raw_counts']
                    
                    # Update metrics with standardized calculations
                    metrics['total_trades'] = std_counts['total_trades']
                    metrics['executed_trades'] = std_counts['executed_trades']
                    metrics['completed_trades'] = std_counts['completed_trades']
                    metrics['profitable_trades'] = std_counts['profitable_trades']
                    metrics['winning_trades'] = std_counts['profitable_trades']  # Legacy compatibility
                    metrics['losing_trades'] = std_counts['completed_trades'] - std_counts['profitable_trades']
                    
                    # CLEAR METRIC SEPARATION - NO MORE CONFUSION
                    metrics['execution_rate'] = std_metrics['execution_rate']['value']
                    metrics['execution_rate_label'] = std_metrics['execution_rate']['label']
                    
                    metrics['profitability_rate'] = std_metrics['profitability_rate']['value']
                    metrics['profitability_rate_label'] = std_metrics['profitability_rate']['label']
                    
                    metrics['overall_success_rate'] = std_metrics['overall_success_rate']['value']
                    metrics['overall_success_rate_label'] = std_metrics['overall_success_rate']['label']
                    
                    # For backward compatibility, use profitability_rate as default "win_rate"
                    metrics['win_rate'] = std_metrics['profitability_rate']['value']
                    metrics['win_rate_note'] = f"Profitability Rate: {std_metrics['profitability_rate']['description']}"
                    
                    # Calculate P&L statistics
                    pnl_values = [trade.get('pnl', 0) for trade in recent_trades if trade.get('pnl') is not None]
                    if pnl_values:
                        metrics['total_pnl'] = sum(pnl_values)
                        metrics['avg_pnl_per_trade'] = metrics['total_pnl'] / len(pnl_values)
                        metrics['best_trade'] = max(pnl_values)
                        metrics['worst_trade'] = min(pnl_values)
                    else:
                        metrics['total_pnl'] = 0
                        metrics['avg_pnl_per_trade'] = 0
                        metrics['best_trade'] = 0
                        metrics['worst_trade'] = 0
                    
                    # Add data quality information
                    metrics['data_quality'] = standardized_report['data_quality']
                    metrics['metric_source'] = 'standardized_metrics_v1.0'
                    
                    self.logger.info(f"✅ Standardized metrics calculated:")
                    self.logger.info(f"   Execution Rate: {metrics['execution_rate']}%")
                    self.logger.info(f"   Profitability Rate: {metrics['profitability_rate']}%")
                    self.logger.info(f"   Overall Success Rate: {metrics['overall_success_rate']}%")
                    
                except Exception as e:
                    self.logger.error(f"❌ Standardized metrics calculation failed: {e}")
                    # Fallback to legacy calculation
                    metrics['total_trades'] = len(recent_trades)
                    pnl_values = [trade.get('pnl', 0) for trade in recent_trades if trade.get('pnl') is not None]
                    if pnl_values:
                        metrics['winning_trades'] = sum(1 for pnl in pnl_values if pnl > 0)
                        metrics['losing_trades'] = sum(1 for pnl in pnl_values if pnl < 0)
                        metrics['win_rate'] = (metrics['winning_trades'] / len(pnl_values)) * 100
                        metrics['win_rate_note'] = "LEGACY CALCULATION - May be inconsistent"
                        metrics['total_pnl'] = sum(pnl_values)
                        metrics['avg_pnl_per_trade'] = metrics['total_pnl'] / len(pnl_values)
                        metrics['best_trade'] = max(pnl_values)
                        metrics['worst_trade'] = min(pnl_values)
                    metrics['metric_source'] = 'legacy_fallback'
            
            # Add portfolio-based metrics if Alpaca is available
            if self.api:
                try:
                    account = self.api.get_account()
                    portfolio_value = float(account.portfolio_value)
                    last_equity = float(account.last_equity)
                    
                    # Daily ROI
                    daily_pl = portfolio_value - last_equity
                    metrics['daily_roi'] = (daily_pl / last_equity) * 100 if last_equity > 0 else 0
                    
                    # Estimate weekly/monthly ROI (simplified)
                    metrics['weekly_roi'] = metrics['daily_roi'] * 5  # 5 trading days
                    metrics['monthly_roi'] = metrics['daily_roi'] * 22  # 22 trading days
                    
                except Exception as e:
                    self.logger.warning(f"Could not calculate portfolio-based metrics: {e}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return self.get_mock_performance_metrics()
    
    # Helper methods
    
    def _classify_position(self, symbol: str) -> tuple:
        """Classify position type and determine module"""
        if symbol.endswith('USD'):
            return 'crypto', 'crypto'
        elif len(symbol) > 6 or '/' in symbol:
            return 'option', 'options'
        elif symbol in ['TQQQ', 'UPRO', 'SOXL', 'FAS', 'UDOW']:
            return 'leveraged_etf', 'stocks'
        elif symbol in ['VXX', 'SVXY']:
            return 'volatility', 'stocks'
        else:
            return 'stock', 'stocks'
    
    def _get_position_hold_time(self, symbol: str) -> str:
        """Get hold time for a position from order history"""
        try:
            if not self.api:
                return "Unknown"
            
            orders = self.api.list_orders(status='filled', limit=50)
            symbol_orders = [order for order in orders if order.symbol == symbol and order.side == 'buy']
            
            if not symbol_orders:
                return "Unknown"
            
            latest_buy = max(symbol_orders, key=lambda x: x.filled_at if x.filled_at else datetime.min)
            
            if latest_buy.filled_at:
                hold_duration = datetime.now() - latest_buy.filled_at.replace(tzinfo=None)
                if hold_duration.days > 0:
                    return f"{hold_duration.days}d {hold_duration.seconds//3600}h"
                else:
                    hours = hold_duration.seconds // 3600
                    minutes = (hold_duration.seconds % 3600) // 60
                    return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            
            return "Unknown"
            
        except Exception:
            return "Unknown"
    
    def _get_position_strategy(self, symbol: str) -> str:
        """Get strategy for a position from modular data"""
        try:
            if not self.firebase_db.is_connected():
                return "unknown"
            
            # Look for recent trades with this symbol
            recent_trades = self.firebase_db.db.collection('modular_trades').where(
                'symbol', '==', symbol
            ).order_by('timestamp', direction='DESCENDING').limit(1).get()
            
            if recent_trades:
                trade_data = recent_trades[0].to_dict()
                return trade_data.get('strategy', 'unknown')
            
            # Fallback classification
            if symbol.endswith('USD'):
                return 'crypto_momentum'
            elif symbol in ['TQQQ', 'UPRO', 'SOXL']:
                return 'leveraged_etfs'
            else:
                return 'momentum'
                
        except Exception:
            return "unknown"
    
    def _get_last_trade_for_module(self, module_name: str) -> Optional[Dict]:
        """Get the last trade for a specific module"""
        try:
            recent_trades = self.firebase_db.db.collection('modular_trades').where(
                'module_name', '==', module_name
            ).order_by('timestamp', direction='DESCENDING').limit(1).get()
            
            if recent_trades:
                trade_data = recent_trades[0].to_dict()
                return {
                    'symbol': trade_data.get('symbol'),
                    'timestamp': trade_data.get('timestamp'),
                    'pnl': trade_data.get('pnl'),
                    'strategy': trade_data.get('strategy')
                }
            
            return None
            
        except Exception:
            return None
    
    def _get_empty_module_performance(self) -> Dict[str, Any]:
        """Return empty module performance structure"""
        return {
            'total_trades': 0,
            'successful_trades': 0,
            'win_rate': 0.0,
            'total_pnl': 0.0,
            'avg_pnl': 0.0,
            'avg_hold_time_hours': 0.0,
            'period_days': 7,
            'last_trade': None
        }
    
    # Mock data methods for fallback
    
    def get_fallback_data(self) -> Dict[str, Any]:
        """Return fallback data when real data is unavailable"""
        return {
            'portfolio': self.get_mock_portfolio_data(),
            'positions': self.get_mock_positions_data(),
            'trades': self.get_mock_trades_data(),
            'performance': self.get_mock_performance_metrics(),
            'modules': self.get_mock_module_performance(),
            'orchestrator': self.get_mock_orchestrator_status(),
            'ml_optimization': self.get_mock_ml_optimization_data(),
            'parameter_effectiveness': self.get_mock_parameter_effectiveness(),
            'system_health': {'overall_status': 'offline', 'firebase_connection': False},
            'market_status': {'is_open': False},
            'strategy_performance': self.get_mock_strategy_performance(),
            'generated_at': datetime.now().isoformat(),
            'data_source': 'fallback_mock',
            'firebase_connected': False,
            'alpaca_connected': False
        }
    
    def get_mock_portfolio_data(self) -> Dict[str, Any]:
        return {
            'value': 99500.00,
            'cash': 25000.00,
            'equity': 99500.00,
            'buying_power': 50000.00,
            'daily_pl': -500.00,
            'daily_pl_percent': -0.50
        }
    
    def get_mock_positions_data(self) -> List[Dict[str, Any]]:
        return [
            {
                'symbol': 'AAPL',
                'quantity': 15,
                'entry_price': 195.50,
                'current_price': 198.75,
                'unrealized_pl': 48.75,
                'unrealized_pl_percent': 1.66,
                'hold_time': '3h 25m',
                'strategy': 'momentum',
                'type': 'stock',
                'module': 'stocks'
            },
            {
                'symbol': 'BTCUSD',
                'quantity': 0.15,
                'entry_price': 45000.00,
                'current_price': 45850.00,
                'unrealized_pl': 127.50,
                'unrealized_pl_percent': 1.89,
                'hold_time': '1h 45m',
                'strategy': 'crypto_momentum',
                'type': 'crypto',
                'module': 'crypto'
            }
        ]
    
    def get_mock_trades_data(self) -> List[Dict[str, Any]]:
        return [
            {
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'symbol': 'SPY',
                'action': 'SELL',
                'strategy': 'momentum',
                'module_name': 'stocks',
                'pnl': 25.50,
                'confidence': 0.75
            }
        ]
    
    def get_mock_module_performance(self) -> Dict[str, Any]:
        return {
            'options': {'total_trades': 12, 'win_rate': 58.3, 'total_pnl': 125.50},
            'crypto': {'total_trades': 8, 'win_rate': 62.5, 'total_pnl': 89.25},
            'stocks': {'total_trades': 25, 'win_rate': 56.0, 'total_pnl': 234.75}
        }
    
    def get_mock_orchestrator_status(self) -> Dict[str, Any]:
        return {
            'last_cycle_time': (datetime.now() - timedelta(minutes=5)).isoformat(),
            'cycle_number': 1250,
            'success_rate': 87.5,
            'uptime_status': 'running'
        }
    
    def get_mock_ml_optimization_data(self) -> Dict[str, Any]:
        return {
            'optimization_enabled': True,
            'recent_optimizations': [
                {
                    'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                    'module_name': 'crypto',
                    'parameter_type': 'confidence_threshold',
                    'old_value': 0.6,
                    'new_value': 0.65,
                    'expected_improvement': 0.05,
                    'applied': True
                }
            ],
            'parameter_changes_today': 3
        }
    
    def get_mock_parameter_effectiveness(self) -> Dict[str, Any]:
        return {
            'parameters_tracked': 15,
            'top_performing_parameters': [
                {'parameter_type': 'confidence_threshold', 'win_rate': 68.5, 'avg_pnl': 12.50}
            ],
            'underperforming_parameters': []
        }
    
    def get_mock_performance_metrics(self) -> Dict[str, Any]:
        return {
            'total_trades': 45,
            'winning_trades': 26,
            'win_rate': 57.8,
            'total_pnl': 449.50,
            'daily_roi': 0.5,
            'weekly_roi': 2.5,
            'monthly_roi': 10.8
        }
    
    def get_mock_strategy_performance(self) -> List[Dict[str, Any]]:
        return [
            {'strategy': 'momentum', 'module': 'stocks', 'win_rate': 65.0, 'total_pnl': 234.50},
            {'strategy': 'crypto_momentum', 'module': 'crypto', 'win_rate': 58.0, 'total_pnl': 125.25}
        ]
    
    def save_to_file(self, data: Dict[str, Any], filename: str = "docs/api/modular-dashboard-data.json"):
        """Save enhanced dashboard data to JSON file"""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"✅ Enhanced dashboard data saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving dashboard data: {e}")


def main():
    """Generate enhanced modular dashboard data"""
    logging.basicConfig(level=logging.INFO)
    
    api = ModularDashboardAPI()
    data = api.generate_enhanced_dashboard_data()
    api.save_to_file(data)
    
    print(f"🎯 Enhanced Modular Dashboard Data Generated:")
    print(f"   Portfolio Value: ${data['portfolio']['value']:,.2f}")
    print(f"   Active Positions: {len(data['positions'])}")
    print(f"   Recent Trades: {len(data['trades'])}")
    print(f"   Modules Active: {len(data['modules'])}")
    print(f"   ML Optimizations Today: {data['ml_optimization']['parameter_changes_today']}")
    print(f"   Data Source: {data['data_source']}")
    print(f"   Firebase Connected: {data['firebase_connected']}")


if __name__ == "__main__":
    main()