#!/usr/bin/env python3
"""
Production Health Monitoring

Provides comprehensive health checking and monitoring capabilities
for the modular trading system in production deployment.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
import threading

logger = logging.getLogger(__name__)


class ComponentHealthCheck:
    """Health check for individual system components."""
    
    def __init__(self, name: str, check_function: Callable, timeout: float = 10.0):
        """
        Initialize component health check.
        
        Args:
            name: Component name
            check_function: Function that returns True if healthy
            timeout: Health check timeout in seconds
        """
        self.name = name
        self.check_function = check_function
        self.timeout = timeout
        self.last_check = None
        self.last_result = None
        self.consecutive_failures = 0
        self.total_checks = 0
        self.total_failures = 0
    
    def check_health(self) -> Dict[str, Any]:
        """
        Perform health check on component.
        
        Returns:
            Health status dictionary
        """
        self.total_checks += 1
        check_start = time.time()
        
        try:
            # Run health check with timeout
            result = self._run_with_timeout(self.check_function, self.timeout)
            
            if result:
                self.consecutive_failures = 0
                status = 'healthy'
            else:
                self.consecutive_failures += 1
                self.total_failures += 1
                status = 'unhealthy'
            
            self.last_result = result
            
        except Exception as e:
            self.consecutive_failures += 1
            self.total_failures += 1
            status = 'error'
            result = False
            logger.error(f"Health check failed for {self.name}: {e}")
        
        check_duration = time.time() - check_start
        self.last_check = datetime.now()
        
        return {
            'component': self.name,
            'healthy': result,
            'status': status,
            'check_duration_ms': round(check_duration * 1000, 2),
            'consecutive_failures': self.consecutive_failures,
            'failure_rate': round(self.total_failures / self.total_checks, 3),
            'last_check': self.last_check.isoformat(),
            'total_checks': self.total_checks
        }
    
    def _run_with_timeout(self, func: Callable, timeout: float) -> bool:
        """Run function with timeout."""
        result = [False]
        exception = [None]
        
        def target():
            try:
                result[0] = func()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Health check timeout after {timeout}s")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]


class HealthMonitor:
    """
    Comprehensive health monitoring system for production deployment.
    
    Monitors all system components and provides health status endpoints
    for Railway and other deployment platforms.
    """
    
    def __init__(self):
        """Initialize the health monitor."""
        self.components: Dict[str, ComponentHealthCheck] = {}
        self.system_start_time = datetime.now()
        self.health_history: List[Dict[str, Any]] = []
        self.alert_callbacks: List[Callable] = []
        
        logger.info("🏥 Health monitor initialized")
    
    def register_component(self, name: str, component: Any, custom_check: Optional[Callable] = None):
        """
        Register a component for health monitoring.
        
        Args:
            name: Component name
            component: Component instance
            custom_check: Custom health check function
        """
        if custom_check:
            check_function = custom_check
        else:
            check_function = self._create_default_check(component)
        
        self.components[name] = ComponentHealthCheck(name, check_function)
        logger.info(f"✅ Registered health check for: {name}")
    
    def _create_default_check(self, component: Any) -> Callable:
        """Create default health check for component."""
        
        def default_check() -> bool:
            """Default health check implementation."""
            if component is None:
                return False
            
            # Check for common health methods
            if hasattr(component, 'is_healthy'):
                return component.is_healthy()
            elif hasattr(component, 'health_check'):
                return component.health_check()
            elif hasattr(component, 'is_connected'):
                return component.is_connected()
            elif hasattr(component, 'ping'):
                result = component.ping()
                return result is True or (hasattr(result, 'status_code') and result.status_code == 200)
            else:
                # For APIs, try a simple call
                if hasattr(component, 'get_account'):
                    try:
                        account = component.get_account()
                        return account is not None
                    except:
                        return False
                elif hasattr(component, 'get_clock'):
                    try:
                        clock = component.get_clock()
                        return clock is not None
                    except:
                        return False
                else:
                    # If no specific health check, assume healthy if object exists
                    return True
        
        return default_check
    
    def check_component(self, name: str) -> Optional[Dict[str, Any]]:
        """Check health of specific component."""
        if name not in self.components:
            return None
        
        return self.components[name].check_health()
    
    def check_all_components(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all registered components."""
        results = {}
        
        for name, component in self.components.items():
            try:
                results[name] = component.check_health()
            except Exception as e:
                results[name] = {
                    'component': name,
                    'healthy': False,
                    'status': 'error',
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }
        
        # Store in history
        self._store_health_history(results)
        
        return results
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary."""
        component_health = self.check_all_components()
        
        healthy_components = sum(1 for h in component_health.values() if h.get('healthy', False))
        total_components = len(component_health)
        
        overall_healthy = healthy_components == total_components
        health_percentage = (healthy_components / total_components * 100) if total_components > 0 else 0
        
        uptime = datetime.now() - self.system_start_time
        
        # Determine overall status
        if health_percentage >= 100:
            overall_status = 'healthy'
        elif health_percentage >= 75:
            overall_status = 'degraded'
        elif health_percentage >= 50:
            overall_status = 'warning'
        else:
            overall_status = 'critical'
        
        return {
            'overall_status': overall_status,
            'overall_healthy': overall_healthy,
            'health_percentage': round(health_percentage, 1),
            'healthy_components': healthy_components,
            'total_components': total_components,
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_hours': round(uptime.total_seconds() / 3600, 2),
            'timestamp': datetime.now().isoformat(),
            'components': component_health
        }
    
    def _store_health_history(self, health_results: Dict[str, Dict[str, Any]]):
        """Store health check results in history."""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'results': health_results
        }
        
        self.health_history.append(history_entry)
        
        # Keep only last 100 entries
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
    
    def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trends over specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_history = [
            entry for entry in self.health_history
            if datetime.fromisoformat(entry['timestamp']) >= cutoff_time
        ]
        
        if not recent_history:
            return {'error': 'No health history available'}
        
        trends = {}
        
        for component_name in self.components.keys():
            component_results = []
            for entry in recent_history:
                if component_name in entry['results']:
                    component_results.append(entry['results'][component_name])
            
            if component_results:
                healthy_count = sum(1 for r in component_results if r.get('healthy', False))
                total_count = len(component_results)
                
                trends[component_name] = {
                    'availability_percentage': round(healthy_count / total_count * 100, 2),
                    'total_checks': total_count,
                    'healthy_checks': healthy_count,
                    'avg_check_duration_ms': round(
                        sum(r.get('check_duration_ms', 0) for r in component_results) / total_count, 2
                    ),
                    'max_consecutive_failures': max(
                        (r.get('consecutive_failures', 0) for r in component_results), default=0
                    )
                }
        
        return {
            'period_hours': hours,
            'total_history_entries': len(recent_history),
            'trends': trends,
            'generated_at': datetime.now().isoformat()
        }
    
    def register_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Register callback for health alerts."""
        self.alert_callbacks.append(callback)
    
    def _trigger_alerts(self, component_name: str, health_result: Dict[str, Any]):
        """Trigger alerts for unhealthy components."""
        if not health_result.get('healthy', True):
            for callback in self.alert_callbacks:
                try:
                    callback(component_name, health_result)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
    
    def get_component_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed statistics for all components."""
        stats = {}
        
        for name, component in self.components.items():
            stats[name] = {
                'name': name,
                'total_checks': component.total_checks,
                'total_failures': component.total_failures,
                'consecutive_failures': component.consecutive_failures,
                'failure_rate': round(component.total_failures / max(component.total_checks, 1), 3),
                'last_check': component.last_check.isoformat() if component.last_check else None,
                'last_result': component.last_result
            }
        
        return stats
    
    def reset_component_stats(self, component_name: Optional[str] = None):
        """Reset statistics for component(s)."""
        if component_name:
            if component_name in self.components:
                component = self.components[component_name]
                component.total_checks = 0
                component.total_failures = 0
                component.consecutive_failures = 0
                logger.info(f"🔄 Reset stats for component: {component_name}")
        else:
            for component in self.components.values():
                component.total_checks = 0
                component.total_failures = 0
                component.consecutive_failures = 0
            logger.info("🔄 Reset stats for all components")


# Example health check functions for common components

def firebase_health_check(firebase_db) -> bool:
    """Health check for Firebase database."""
    try:
        return firebase_db.is_connected() if hasattr(firebase_db, 'is_connected') else True
    except:
        return False


def alpaca_health_check(alpaca_api) -> bool:
    """Health check for Alpaca API."""
    try:
        account = alpaca_api.get_account()
        return account is not None and hasattr(account, 'id')
    except:
        return False


def orchestrator_health_check(orchestrator) -> bool:
    """Health check for trading orchestrator."""
    try:
        if hasattr(orchestrator, 'is_healthy'):
            return orchestrator.is_healthy()
        elif hasattr(orchestrator, 'get_status'):
            status = orchestrator.get_status()
            return status.get('healthy', False)
        else:
            return orchestrator is not None
    except:
        return False