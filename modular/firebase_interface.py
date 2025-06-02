"""
Firebase Interface for Modular Architecture

This module provides a Firebase-first data layer interface specifically designed
for the modular trading architecture. It extends the existing firebase_database.py
with additional methods for module coordination and ML optimization.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging

from modular.base_module import TradeOpportunity, TradeResult, ModuleConfig


class ModularFirebaseInterface:
    """
    Firebase interface specifically designed for modular architecture.
    
    Provides methods for:
    - Module-specific data storage
    - Event-driven communication
    - ML optimization data
    - Performance analytics
    - Real-time parameter updates
    """
    
    def __init__(self, firebase_db, logger: Optional[logging.Logger] = None):
        """
        Initialize with existing Firebase database instance.
        
        Args:
            firebase_db: Existing FirebaseDatabase instance
            logger: Optional logger instance
        """
        self.firebase_db = firebase_db
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # Collection names for modular architecture
        self.collections = {
            'module_opportunities': 'modular_opportunities',
            'module_trades': 'modular_trades', 
            'module_configs': 'modular_configs',
            'module_events': 'modular_events',
            'orchestrator_cycles': 'orchestrator_cycles',
            'ml_parameters': 'ml_parameters',
            'performance_analytics': 'performance_analytics'
        }
        
        self.logger.info("Modular Firebase interface initialized")
    
    def is_connected(self) -> bool:
        """Check if Firebase connection is available"""
        try:
            return self.firebase_db.is_connected() if self.firebase_db else False
        except Exception as e:
            self.logger.error(f"Error checking Firebase connection: {e}")
            return False
    
    # Module data persistence methods
    
    def save_trade_opportunity(self, module_name: str, opportunity: TradeOpportunity):
        """
        Save trade opportunity for ML analysis and tracking.
        
        Args:
            module_name: Name of the module that generated the opportunity
            opportunity: TradeOpportunity instance
        """
        try:
            if not self.is_connected():
                self.logger.warning("Firebase not connected, skipping opportunity save")
                return
            
            doc_data = {
                'module_name': module_name,
                'symbol': opportunity.symbol,
                'action': opportunity.action.value,
                'quantity': opportunity.quantity,
                'confidence': opportunity.confidence,
                'strategy': opportunity.strategy,
                'metadata': opportunity.metadata,
                'technical_score': opportunity.technical_score,
                'regime_score': opportunity.regime_score,
                'pattern_score': opportunity.pattern_score,
                'ml_score': opportunity.ml_score,
                'max_position_size': opportunity.max_position_size,
                'stop_loss_pct': opportunity.stop_loss_pct,
                'profit_target_pct': opportunity.profit_target_pct,
                'created_at': opportunity.created_at.isoformat(),
                'expires_at': opportunity.expires_at.isoformat() if opportunity.expires_at else None,
                'timestamp': datetime.now().isoformat()
            }
            
            self.firebase_db.db.collection(self.collections['module_opportunities']).add(doc_data)
            
        except Exception as e:
            self.logger.error(f"Error saving opportunity to Firebase: {e}")
    
    def save_trade_result(self, module_name: str, result: TradeResult):
        """
        Save trade execution result for performance tracking.
        
        Args:
            module_name: Name of the module that executed the trade
            result: TradeResult instance
        """
        try:
            if not self.is_connected():
                self.logger.warning("Firebase not connected, skipping trade result save")
                return
            
            doc_data = {
                'module_name': module_name,
                'symbol': result.opportunity.symbol,
                'action': result.opportunity.action.value,
                'strategy': result.opportunity.strategy,
                'status': result.status.value,
                'order_id': result.order_id,
                'execution_price': result.execution_price,
                'execution_time': result.execution_time.isoformat() if result.execution_time else None,
                'error_message': result.error_message,
                'pnl': result.pnl,
                'pnl_pct': result.pnl_pct,
                'hold_duration': result.hold_duration,
                'exit_reason': result.exit_reason.value if result.exit_reason else None,
                'confidence': result.opportunity.confidence,
                'timestamp': datetime.now().isoformat()
            }
            
            self.firebase_db.db.collection(self.collections['module_trades']).add(doc_data)
            
        except Exception as e:
            self.logger.error(f"Error saving trade result to Firebase: {e}")
    
    def save_orchestrator_cycle(self, cycle_data: Dict[str, Any]):
        """
        Save orchestrator cycle results.
        
        Args:
            cycle_data: Complete cycle data from orchestrator
        """
        try:
            if not self.is_connected():
                self.logger.warning("Firebase not connected, skipping cycle save")
                return
            
            self.firebase_db.db.collection(self.collections['orchestrator_cycles']).add(cycle_data)
            
        except Exception as e:
            self.logger.error(f"Error saving orchestrator cycle: {e}")
    
    def save_orchestrator_shutdown(self, shutdown_data: Dict[str, Any]):
        """Save orchestrator shutdown metrics"""
        try:
            if not self.is_connected():
                return
            
            self.firebase_db.db.collection('orchestrator_shutdowns').add(shutdown_data)
            
        except Exception as e:
            self.logger.error(f"Error saving shutdown data: {e}")
    
    # Module configuration methods
    
    def get_module_parameters(self, module_name: str) -> Dict[str, Any]:
        """
        Get ML-optimized parameters for a module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Dictionary of optimized parameters
        """
        try:
            if not self.is_connected():
                return {}
            
            docs = (self.firebase_db.db
                   .collection(self.collections['ml_parameters'])
                   .where('module_name', '==', module_name)
                   .order_by('timestamp', direction='DESCENDING')
                   .limit(1)
                   .get())
            
            if docs:
                return docs[0].to_dict().get('parameters', {})
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting module parameters: {e}")
            return {}
    
    def save_module_parameters(self, module_name: str, parameters: Dict[str, Any]):
        """
        Save ML-optimized parameters for a module.
        
        Args:
            module_name: Name of the module
            parameters: Optimized parameters dictionary
        """
        try:
            if not self.is_connected():
                return
            
            doc_data = {
                'module_name': module_name,
                'parameters': parameters,
                'timestamp': datetime.now().isoformat(),
                'optimization_version': 'v1'
            }
            
            self.firebase_db.db.collection(self.collections['ml_parameters']).add(doc_data)
            
        except Exception as e:
            self.logger.error(f"Error saving module parameters: {e}")
    
    # Event-driven communication methods
    
    def publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Publish event for inter-module communication.
        
        Args:
            event_type: Type of event (e.g., 'trade_executed', 'market_regime_change')
            event_data: Event data dictionary
        """
        try:
            if not self.is_connected():
                return
            
            doc_data = {
                'event_type': event_type,
                'data': event_data,
                'timestamp': datetime.now().isoformat()
            }
            
            self.firebase_db.db.collection(self.collections['module_events']).add(doc_data)
            
        except Exception as e:
            self.logger.error(f"Error publishing event: {e}")
    
    def get_recent_events(self, event_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent events for module coordination.
        
        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        try:
            if not self.is_connected():
                return []
            
            query = self.firebase_db.db.collection(self.collections['module_events'])
            
            if event_type:
                query = query.where('event_type', '==', event_type)
            
            docs = query.order_by('timestamp', direction='DESCENDING').limit(limit).get()
            
            return [doc.to_dict() for doc in docs]
            
        except Exception as e:
            self.logger.error(f"Error getting recent events: {e}")
            return []
    
    # Performance analytics methods
    
    def get_module_performance_data(self, module_name: str, 
                                  days_back: int = 7) -> Dict[str, Any]:
        """
        Get performance analytics for a module.
        
        Args:
            module_name: Name of the module
            days_back: Number of days of data to retrieve
            
        Returns:
            Performance data dictionary
        """
        try:
            if not self.is_connected():
                return {}
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Get trade results
            trades = (self.firebase_db.db
                     .collection(self.collections['module_trades'])
                     .where('module_name', '==', module_name)
                     .where('timestamp', '>=', cutoff_date.isoformat())
                     .get())
            
            trade_data = [doc.to_dict() for doc in trades]
            
            # Calculate metrics
            total_trades = len(trade_data)
            successful_trades = sum(1 for t in trade_data if t.get('pnl', 0) > 0)
            total_pnl = sum(t.get('pnl', 0) for t in trade_data if t.get('pnl') is not None)
            avg_hold_time = sum(t.get('hold_duration', 0) for t in trade_data) / max(1, total_trades)
            
            return {
                'module_name': module_name,
                'period_days': days_back,
                'total_trades': total_trades,
                'successful_trades': successful_trades,
                'win_rate': successful_trades / max(1, total_trades),
                'total_pnl': total_pnl,
                'avg_pnl': total_pnl / max(1, total_trades),
                'avg_hold_time_hours': avg_hold_time,
                'trade_data': trade_data
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance data: {e}")
            return {}
    
    def save_performance_analytics(self, analytics_data: Dict[str, Any]):
        """
        Save calculated performance analytics.
        
        Args:
            analytics_data: Performance analytics dictionary
        """
        try:
            if not self.is_connected():
                return
            
            doc_data = {
                **analytics_data,
                'timestamp': datetime.now().isoformat()
            }
            
            self.firebase_db.db.collection(self.collections['performance_analytics']).add(doc_data)
            
        except Exception as e:
            self.logger.error(f"Error saving performance analytics: {e}")
    
    # Dashboard data methods
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive data for real-time dashboard.
        
        Returns:
            Dashboard data dictionary
        """
        try:
            if not self.is_connected():
                return {'connected': False}
            
            # Get recent orchestrator cycles
            recent_cycles = (self.firebase_db.db
                           .collection(self.collections['orchestrator_cycles'])
                           .order_by('timestamp', direction='DESCENDING')
                           .limit(5)
                           .get())
            
            # Get recent trades by module
            recent_trades = (self.firebase_db.db
                           .collection(self.collections['module_trades'])
                           .order_by('timestamp', direction='DESCENDING')
                           .limit(20)
                           .get())
            
            # Get module performance summaries
            modules = ['options', 'crypto', 'stocks']  # Known modules
            module_performance = {}
            
            for module in modules:
                module_performance[module] = self.get_module_performance_data(module, days_back=1)
            
            return {
                'connected': True,
                'timestamp': datetime.now().isoformat(),
                'recent_cycles': [doc.to_dict() for doc in recent_cycles],
                'recent_trades': [doc.to_dict() for doc in recent_trades],
                'module_performance': module_performance
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {'connected': False, 'error': str(e)}
    
    # Migration and compatibility methods
    
    def migrate_legacy_data(self):
        """
        Migrate data from legacy SQLite/Firebase structure to modular structure.
        
        This method helps transition from the current Phase 5 system to the new
        modular architecture without losing historical data.
        """
        try:
            if not self.is_connected():
                self.logger.warning("Cannot migrate data - Firebase not connected")
                return
            
            self.logger.info("Starting legacy data migration to modular structure")
            
            # Get existing trading cycles from Phase 5
            legacy_cycles = self.firebase_db.get_recent_trading_cycles(limit=100)
            
            migration_stats = {
                'cycles_migrated': 0,
                'trades_migrated': 0,
                'errors': []
            }
            
            for cycle in legacy_cycles:
                try:
                    # Convert legacy cycle to modular format
                    modular_cycle = self._convert_legacy_cycle(cycle)
                    
                    # Save as orchestrator cycle
                    self.firebase_db.db.collection(self.collections['orchestrator_cycles']).add(modular_cycle)
                    migration_stats['cycles_migrated'] += 1
                    
                except Exception as e:
                    migration_stats['errors'].append(f"Cycle migration error: {e}")
            
            # Get existing trades
            legacy_trades = self.firebase_db.get_recent_trades(limit=500)
            
            for trade in legacy_trades:
                try:
                    # Convert legacy trade to modular format
                    modular_trade = self._convert_legacy_trade(trade)
                    
                    # Save as module trade
                    self.firebase_db.db.collection(self.collections['module_trades']).add(modular_trade)
                    migration_stats['trades_migrated'] += 1
                    
                except Exception as e:
                    migration_stats['errors'].append(f"Trade migration error: {e}")
            
            self.logger.info(f"Migration completed: {migration_stats}")
            
            # Save migration log
            migration_log = {
                'timestamp': datetime.now().isoformat(),
                'stats': migration_stats,
                'migration_version': 'v1'
            }
            self.firebase_db.db.collection('migration_logs').add(migration_log)
            
        except Exception as e:
            self.logger.error(f"Error during data migration: {e}")
    
    def _convert_legacy_cycle(self, legacy_cycle: Dict[str, Any]) -> Dict[str, Any]:
        """Convert legacy trading cycle to modular format"""
        return {
            'timestamp': legacy_cycle.get('timestamp'),
            'cycle_number': legacy_cycle.get('cycle_id', 0),
            'orchestrator_version': 'legacy_migration',
            'results': {
                'success': True,
                'modules': {
                    'legacy': {
                        'success': True,
                        'opportunities_count': legacy_cycle.get('opportunities_analyzed', 0),
                        'trades_count': legacy_cycle.get('trades_executed', 0),
                        'successful_trades': legacy_cycle.get('successful_trades', 0)
                    }
                },
                'summary': {
                    'total_opportunities': legacy_cycle.get('opportunities_analyzed', 0),
                    'total_trades': legacy_cycle.get('trades_executed', 0),
                    'successful_trades': legacy_cycle.get('successful_trades', 0)
                }
            },
            'migrated_from': 'legacy_phase5'
        }
    
    def _convert_legacy_trade(self, legacy_trade: Dict[str, Any]) -> Dict[str, Any]:
        """Convert legacy trade to modular format"""
        # Determine module based on symbol or strategy
        module_name = 'legacy'
        symbol = legacy_trade.get('symbol', '')
        
        if any(crypto in symbol for crypto in ['BTC', 'ETH', 'ADA', 'SOL']):
            module_name = 'crypto'
        elif 'C' in symbol or 'P' in symbol:  # Options symbols often contain C/P
            module_name = 'options'
        else:
            module_name = 'stocks'
        
        return {
            'module_name': module_name,
            'symbol': symbol,
            'action': legacy_trade.get('action', 'buy'),
            'strategy': legacy_trade.get('strategy', 'unknown'),
            'status': 'executed' if legacy_trade.get('success') else 'failed',
            'order_id': legacy_trade.get('order_id'),
            'execution_price': legacy_trade.get('execution_price'),
            'execution_time': legacy_trade.get('timestamp'),
            'pnl': legacy_trade.get('pnl'),
            'pnl_pct': legacy_trade.get('pnl_percentage'),
            'confidence': legacy_trade.get('confidence', 0.5),
            'timestamp': legacy_trade.get('timestamp'),
            'migrated_from': 'legacy_phase5'
        }
    
    # ML Data Collection Methods (for compatibility with enhanced modules)
    
    def save_trade(self, trade_data: Dict[str, Any]) -> str:
        """Save ML-enhanced trade data to Firebase"""
        try:
            if not self.is_connected():
                return "mock_trade_id"
            
            return self.firebase_db.save_trade(trade_data)
            
        except Exception as e:
            self.logger.error(f"Error saving ML trade data: {e}")
            return "error_trade_id"
    
    def update_trade_outcome(self, trade_id: str, outcome_data: Dict[str, Any]) -> bool:
        """Update existing trade with final profit/loss outcome - CRITICAL FOR ML LEARNING"""
        try:
            if not self.is_connected():
                self.logger.warning(f"Firebase not connected - cannot update trade {trade_id}")
                return False
            
            return self.firebase_db.update_trade_outcome(trade_id, outcome_data)
            
        except Exception as e:
            self.logger.error(f"Error updating trade outcome {trade_id}: {e}")
            return False
    
    def save_parameter_effectiveness(self, param_data: Dict[str, Any]) -> str:
        """Save parameter effectiveness data for ML optimization"""
        try:
            if not self.is_connected():
                return "mock_param_id"
            
            return self.firebase_db.save_parameter_effectiveness(param_data)
            
        except Exception as e:
            self.logger.error(f"Error saving parameter effectiveness: {e}")
            return "error_param_id"
    
    def save_ml_learning_event(self, event_data: Dict[str, Any]) -> str:
        """Save ML learning event for audit trail"""
        try:
            if not self.is_connected():
                return "mock_event_id"
            
            return self.firebase_db.save_ml_learning_event(event_data)
            
        except Exception as e:
            self.logger.error(f"Error saving ML learning event: {e}")
            return "error_event_id"
    
    def get_ml_optimization_data(self, module_name: str = None) -> List[Dict[str, Any]]:
        """Get ML optimization data"""
        try:
            if not self.is_connected():
                return []
            
            return self.firebase_db.get_ml_optimization_data(module_name)
            
        except Exception as e:
            self.logger.error(f"Error getting ML optimization data: {e}")
            return []
    
    def save_ml_optimization_data(self, module_name: str, optimization_data: Dict[str, Any]) -> str:
        """Save ML optimization data for a module"""
        try:
            if not self.is_connected():
                return "mock_optimization_id"
            
            return self.firebase_db.save_ml_optimization_data(module_name, optimization_data)
            
        except Exception as e:
            self.logger.error(f"Error saving ML optimization data: {e}")
            return "error_optimization_id"