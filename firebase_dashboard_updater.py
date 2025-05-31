#!/usr/bin/env python3
"""
Firebase Dashboard Data Updater

This script runs continuously to update Firebase with real-time trading data
for the modular dashboard, ensuring the Firebase-hosted dashboard always 
has the latest information.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import alpaca_trade_api as tradeapi

# Import modular components
from modular.firebase_interface import ModularFirebaseInterface
from firebase_database import FirebaseDatabase
from modular_dashboard_api import ModularDashboardAPI


class FirebaseDashboardUpdater:
    """Updates Firebase with real-time dashboard data"""
    
    def __init__(self, update_interval: int = 30):
        """
        Initialize Firebase dashboard updater.
        
        Args:
            update_interval: Update interval in seconds (default: 30 seconds)
        """
        self.update_interval = update_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self.firebase_db = FirebaseDatabase()
        self.modular_interface = ModularFirebaseInterface(self.firebase_db, self.logger)
        self.dashboard_api = ModularDashboardAPI()
        
        # Track last update times
        self.last_portfolio_update = None
        self.last_performance_update = None
        self.last_health_check = None
        
        self.logger.info("Firebase Dashboard Updater initialized")
    
    def start_continuous_updates(self):
        """Start continuous dashboard data updates"""
        self.logger.info(f"Starting continuous Firebase dashboard updates (every {self.update_interval}s)")
        
        try:
            while True:
                cycle_start = time.time()
                
                # Update dashboard data
                self.update_dashboard_data()
                
                # Update system health
                self.update_system_health()
                
                # Calculate next update delay
                cycle_duration = time.time() - cycle_start
                sleep_time = max(0, self.update_interval - cycle_duration)
                
                self.logger.debug(f"Dashboard update cycle completed in {cycle_duration:.1f}s, "
                                f"next update in {sleep_time:.1f}s")
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            self.logger.info("Dashboard updater stopped by user")
        except Exception as e:
            self.logger.error(f"Error in dashboard update loop: {e}")
            raise
    
    def update_dashboard_data(self):
        """Update Firebase with current dashboard data"""
        try:
            # Generate complete dashboard data
            dashboard_data = self.dashboard_api.generate_enhanced_dashboard_data()
            
            # Update dashboard summary in Firebase
            self.update_dashboard_summary(dashboard_data)
            
            # Update specific collections with detailed data
            self.update_detailed_collections(dashboard_data)
            
            self.logger.debug("Dashboard data updated successfully")
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard data: {e}")
    
    def update_dashboard_summary(self, dashboard_data: Dict[str, Any]):
        """Update dashboard summary document in Firebase"""
        try:
            if not self.firebase_db.is_connected():
                return
            
            summary_data = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_value': dashboard_data['portfolio']['value'],
                'daily_pl': dashboard_data['portfolio']['daily_pl'],
                'daily_pl_percent': dashboard_data['portfolio']['daily_pl_percent'],
                'active_positions': len(dashboard_data['positions']),
                'win_rate': dashboard_data['performance']['win_rate'],
                'total_trades': dashboard_data['performance']['total_trades'],
                'ml_optimizations_today': dashboard_data['ml_optimization']['parameter_changes_today'],
                'firebase_connected': dashboard_data['firebase_connected'],
                'alpaca_connected': dashboard_data['alpaca_connected'],
                'system_status': dashboard_data['system_health']['overall_status'],
                'market_open': dashboard_data['market_status']['is_open'],
                'last_orchestrator_cycle': dashboard_data['orchestrator'].get('last_cycle_time'),
                'orchestrator_success_rate': dashboard_data['orchestrator'].get('success_rate', 0)
            }
            
            # Update dashboard summary collection
            self.firebase_db.db.collection('dashboard_summary').document('current').set(summary_data)
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard summary: {e}")
    
    def update_detailed_collections(self, dashboard_data: Dict[str, Any]):
        """Update detailed collections for dashboard consumption"""
        try:
            if not self.firebase_db.is_connected():
                return
            
            current_time = datetime.now()
            
            # Update module performance
            for module_name, performance in dashboard_data['modules'].items():
                module_doc = {
                    'timestamp': current_time.isoformat(),
                    'module_name': module_name,
                    **performance
                }
                
                self.firebase_db.db.collection('dashboard_module_performance').document(module_name).set(module_doc)
            
            # Update orchestrator status
            orchestrator_doc = {
                'timestamp': current_time.isoformat(),
                **dashboard_data['orchestrator']
            }
            
            self.firebase_db.db.collection('dashboard_orchestrator_status').document('current').set(orchestrator_doc)
            
            # Update ML optimization status
            ml_doc = {
                'timestamp': current_time.isoformat(),
                **dashboard_data['ml_optimization']
            }
            
            self.firebase_db.db.collection('dashboard_ml_status').document('current').set(ml_doc)
            
            # Update positions summary
            positions_summary = {
                'timestamp': current_time.isoformat(),
                'total_positions': len(dashboard_data['positions']),
                'positions_by_module': {},
                'positions_by_type': {},
                'total_unrealized_pl': 0
            }
            
            for position in dashboard_data['positions']:
                module = position.get('module', 'unknown')
                pos_type = position.get('type', 'unknown')
                
                positions_summary['positions_by_module'][module] = positions_summary['positions_by_module'].get(module, 0) + 1
                positions_summary['positions_by_type'][pos_type] = positions_summary['positions_by_type'].get(pos_type, 0) + 1
                positions_summary['total_unrealized_pl'] += position.get('unrealized_pl', 0)
            
            self.firebase_db.db.collection('dashboard_positions_summary').document('current').set(positions_summary)
            
        except Exception as e:
            self.logger.error(f"Error updating detailed collections: {e}")
    
    def update_system_health(self):
        """Update system health status"""
        try:
            if not self.firebase_db.is_connected():
                return
            
            current_time = datetime.now()
            
            # Check if health check is due (every 5 minutes)
            if (self.last_health_check is None or 
                current_time - self.last_health_check > timedelta(minutes=5)):
                
                health_status = self.dashboard_api.get_system_health()
                
                health_doc = {
                    'timestamp': current_time.isoformat(),
                    **health_status,
                    'updater_status': 'running',
                    'last_update_interval': self.update_interval
                }
                
                self.firebase_db.db.collection('dashboard_system_health').document('current').set(health_doc)
                
                self.last_health_check = current_time
                self.logger.debug("System health status updated")
                
        except Exception as e:
            self.logger.error(f"Error updating system health: {e}")
    
    def update_performance_charts_data(self):
        """Update data specifically for dashboard charts"""
        try:
            if not self.firebase_db.is_connected():
                return
            
            current_time = datetime.now()
            
            # Get recent trades for performance chart
            recent_trades = self.dashboard_api.get_recent_trades()
            
            if recent_trades:
                # Calculate cumulative P&L for chart
                cumulative_pnl = 0
                chart_data = []
                
                for trade in reversed(recent_trades[-20:]):  # Last 20 trades
                    cumulative_pnl += trade.get('pnl', 0)
                    chart_data.append({
                        'timestamp': trade.get('timestamp'),
                        'cumulative_pnl': cumulative_pnl,
                        'trade_pnl': trade.get('pnl', 0),
                        'symbol': trade.get('symbol'),
                        'module': trade.get('module_name')
                    })
                
                chart_doc = {
                    'timestamp': current_time.isoformat(),
                    'chart_data': chart_data,
                    'total_cumulative_pnl': cumulative_pnl
                }
                
                self.firebase_db.db.collection('dashboard_chart_data').document('performance').set(chart_doc)
            
        except Exception as e:
            self.logger.error(f"Error updating chart data: {e}")
    
    def cleanup_old_data(self):
        """Clean up old dashboard data to prevent Firebase bloat"""
        try:
            if not self.firebase_db.is_connected():
                return
            
            # Define cleanup thresholds
            old_threshold = datetime.now() - timedelta(days=7)
            
            # Collections to clean up
            cleanup_collections = [
                'dashboard_summary',
                'dashboard_system_health',
                'dashboard_chart_data'
            ]
            
            for collection_name in cleanup_collections:
                try:
                    # Get old documents
                    old_docs = self.firebase_db.db.collection(collection_name).where(
                        'timestamp', '<', old_threshold.isoformat()
                    ).limit(100).get()
                    
                    # Delete old documents
                    for doc in old_docs:
                        doc.reference.delete()
                    
                    if old_docs:
                        self.logger.info(f"Cleaned up {len(old_docs)} old documents from {collection_name}")
                        
                except Exception as e:
                    self.logger.warning(f"Error cleaning up {collection_name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error during data cleanup: {e}")
    
    def get_update_status(self) -> Dict[str, Any]:
        """Get current updater status"""
        return {
            'running': True,
            'update_interval': self.update_interval,
            'last_portfolio_update': self.last_portfolio_update.isoformat() if self.last_portfolio_update else None,
            'last_performance_update': self.last_performance_update.isoformat() if self.last_performance_update else None,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'firebase_connected': self.firebase_db.is_connected(),
            'uptime': (datetime.now() - datetime.now()).total_seconds()  # This would be calculated from start time
        }


class FirebaseDashboardService:
    """Service wrapper for Firebase dashboard updates"""
    
    def __init__(self):
        self.updater = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def start_service(self, update_interval: int = 30):
        """Start the Firebase dashboard update service"""
        try:
            self.logger.info("Starting Firebase Dashboard Update Service")
            
            self.updater = FirebaseDashboardUpdater(update_interval)
            self.updater.start_continuous_updates()
            
        except Exception as e:
            self.logger.error(f"Error starting dashboard service: {e}")
            raise
    
    def stop_service(self):
        """Stop the dashboard update service"""
        if self.updater:
            self.logger.info("Stopping Firebase Dashboard Update Service")
            # Service stops when updater loop exits
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        if self.updater:
            return self.updater.get_update_status()
        else:
            return {'running': False, 'error': 'Service not started'}


def main():
    """Run Firebase dashboard updater as standalone service"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get update interval from environment or use default
    update_interval = int(os.getenv('DASHBOARD_UPDATE_INTERVAL', 30))
    
    service = FirebaseDashboardService()
    
    try:
        print(f"🔥 Starting Firebase Dashboard Update Service")
        print(f"   Update interval: {update_interval} seconds")
        print(f"   Press Ctrl+C to stop")
        
        service.start_service(update_interval)
        
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except Exception as e:
        print(f"❌ Service error: {e}")
    finally:
        service.stop_service()


if __name__ == "__main__":
    main()