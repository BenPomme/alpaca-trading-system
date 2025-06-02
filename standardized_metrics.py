#!/usr/bin/env python3
"""
Standardized Metrics Module

Provides consistent win rate and performance calculations across all components
of the trading system. Eliminates conflicting win rate reporting by establishing
a single source of truth for metric calculations.

Usage:
    from standardized_metrics import StandardizedMetrics
    
    metrics = StandardizedMetrics()
    report = metrics.calculate_performance_report(trades_data)
    print(f"Execution Rate: {report['execution_rate']['value']}%")
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class MetricType(Enum):
    """Types of performance metrics"""
    EXECUTION_RATE = "execution_rate"
    PROFITABILITY_RATE = "profitability_rate" 
    OVERALL_SUCCESS_RATE = "overall_success_rate"


@dataclass
class TradeData:
    """Standardized trade data structure"""
    symbol: str
    status: str  # 'executed', 'failed', 'pending'
    pnl: Optional[float] = None  # Profit/loss, None for open positions
    timestamp: Optional[datetime] = None
    trade_id: Optional[str] = None
    module: Optional[str] = None  # 'crypto', 'stocks', 'options'


@dataclass
class MetricDefinition:
    """Definition of a performance metric"""
    name: str
    description: str
    formula: str
    use_case: str
    calculation_method: str


class StandardizedMetrics:
    """
    Standardized metrics calculator for consistent win rate reporting.
    
    Provides three distinct metrics:
    1. Execution Rate: Orders successfully filled
    2. Profitability Rate: Completed trades that were profitable  
    3. Overall Success Rate: All trades that were profitable
    """
    
    def __init__(self):
        """Initialize standardized metrics calculator."""
        self.metric_definitions = self._initialize_metric_definitions()
    
    def _initialize_metric_definitions(self) -> Dict[str, MetricDefinition]:
        """Initialize metric definitions"""
        return {
            'execution_rate': MetricDefinition(
                name='Order Execution Rate',
                description='Percentage of orders successfully filled by broker',
                formula='executed_orders / total_orders * 100',
                use_case='Measure order execution reliability and broker performance',
                calculation_method='Count orders with status=executed vs total orders'
            ),
            'profitability_rate': MetricDefinition(
                name='Trade Profitability Rate',
                description='Percentage of completed trades that were profitable',
                formula='profitable_trades / completed_trades * 100',
                use_case='Measure strategy effectiveness among closed positions',
                calculation_method='Count trades with pnl>0 vs trades with pnl!=None'
            ),
            'overall_success_rate': MetricDefinition(
                name='Overall Success Rate',
                description='Percentage of all trades that were profitable',
                formula='profitable_trades / total_trades * 100',
                use_case='Measure complete system performance including open positions',
                calculation_method='Count trades with pnl>0 vs all trades'
            )
        }
    
    def normalize_trade_data(self, raw_data: List[Dict[str, Any]], source_format: str = 'auto') -> List[TradeData]:
        """
        Normalize trade data from different sources into standard format.
        
        Args:
            raw_data: Raw trade data from various sources
            source_format: Data source format ('firebase', 'sqlite', 'alpaca', 'auto')
            
        Returns:
            List of normalized TradeData objects
        """
        normalized_trades = []
        
        for trade in raw_data:
            try:
                if source_format == 'firebase' or 'trade_data' in trade:
                    # Firebase format: nested trade_data structure
                    trade_data = trade.get('trade_data', trade)
                    normalized_trade = TradeData(
                        symbol=trade_data.get('symbol', ''),
                        status=trade_data.get('status', 'unknown'),
                        pnl=trade_data.get('profit_loss'),
                        timestamp=self._parse_timestamp(trade_data.get('timestamp')),
                        trade_id=trade_data.get('trade_id'),
                        module=trade_data.get('module')
                    )
                    
                elif source_format == 'sqlite' or 'realized_pnl' in trade:
                    # SQLite format: flat structure with different field names
                    normalized_trade = TradeData(
                        symbol=trade.get('symbol', ''),
                        status=trade.get('trade_status', trade.get('status', 'unknown')),
                        pnl=trade.get('realized_pnl', trade.get('pnl')),
                        timestamp=self._parse_timestamp(trade.get('created_at', trade.get('timestamp'))),
                        trade_id=trade.get('id', trade.get('trade_id')),
                        module=trade.get('asset_class', trade.get('module'))
                    )
                    
                elif source_format == 'alpaca' or 'side' in trade:
                    # Alpaca API format: order structure
                    # Note: Alpaca orders don't have P&L until positions are closed
                    normalized_trade = TradeData(
                        symbol=trade.get('symbol', ''),
                        status='executed' if trade.get('status') == 'filled' else trade.get('status', 'unknown'),
                        pnl=None,  # P&L calculated separately from positions
                        timestamp=self._parse_timestamp(trade.get('filled_at', trade.get('created_at'))),
                        trade_id=trade.get('id'),
                        module='alpaca'
                    )
                    
                else:
                    # Auto-detect or generic format
                    normalized_trade = TradeData(
                        symbol=trade.get('symbol', ''),
                        status=trade.get('status', 'unknown'),
                        pnl=trade.get('pnl', trade.get('profit_loss')),
                        timestamp=self._parse_timestamp(trade.get('timestamp')),
                        trade_id=trade.get('trade_id', trade.get('id')),
                        module=trade.get('module')
                    )
                
                normalized_trades.append(normalized_trade)
                
            except Exception as e:
                # Log error but continue processing other trades
                print(f"Warning: Failed to normalize trade data: {e}")
                continue
        
        return normalized_trades
    
    def _parse_timestamp(self, timestamp: Any) -> Optional[datetime]:
        """Parse timestamp from various formats"""
        if timestamp is None:
            return None
        
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            try:
                # Try ISO format first
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                try:
                    # Try other common formats
                    return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                except:
                    return None
        
        return None
    
    def calculate_performance_metrics(self, trades: List[TradeData]) -> Dict[str, Any]:
        """
        Calculate standardized performance metrics.
        
        Args:
            trades: List of normalized trade data
            
        Returns:
            Dictionary with calculated metrics and raw counts
        """
        if not trades:
            return self._get_empty_metrics()
        
        # Count different trade categories
        total_trades = len(trades)
        executed_trades = [t for t in trades if t.status == 'executed']
        completed_trades = [t for t in trades if t.pnl is not None]
        profitable_trades = [t for t in completed_trades if t.pnl > 0]
        
        # Calculate rates
        execution_rate = len(executed_trades) / total_trades * 100 if total_trades > 0 else 0
        profitability_rate = len(profitable_trades) / len(completed_trades) * 100 if len(completed_trades) > 0 else 0
        overall_success_rate = len(profitable_trades) / total_trades * 100 if total_trades > 0 else 0
        
        return {
            'metrics': {
                'execution_rate': {
                    'value': round(execution_rate, 1),
                    'label': self.metric_definitions['execution_rate'].name,
                    'description': self.metric_definitions['execution_rate'].description,
                    'formula': self.metric_definitions['execution_rate'].formula
                },
                'profitability_rate': {
                    'value': round(profitability_rate, 1),
                    'label': self.metric_definitions['profitability_rate'].name,
                    'description': self.metric_definitions['profitability_rate'].description,
                    'formula': self.metric_definitions['profitability_rate'].formula
                },
                'overall_success_rate': {
                    'value': round(overall_success_rate, 1),
                    'label': self.metric_definitions['overall_success_rate'].name,
                    'description': self.metric_definitions['overall_success_rate'].description,
                    'formula': self.metric_definitions['overall_success_rate'].formula
                }
            },
            'raw_counts': {
                'total_trades': total_trades,
                'executed_trades': len(executed_trades),
                'completed_trades': len(completed_trades),
                'profitable_trades': len(profitable_trades),
                'failed_trades': total_trades - len(executed_trades),
                'open_trades': len(executed_trades) - len(completed_trades)
            },
            'calculated_at': datetime.now().isoformat(),
            'data_source': 'standardized_metrics'
        }
    
    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure when no data available"""
        return {
            'metrics': {
                'execution_rate': {'value': 0.0, 'label': 'No data', 'description': 'No trades available'},
                'profitability_rate': {'value': 0.0, 'label': 'No data', 'description': 'No completed trades'},
                'overall_success_rate': {'value': 0.0, 'label': 'No data', 'description': 'No trades available'}
            },
            'raw_counts': {
                'total_trades': 0,
                'executed_trades': 0,
                'completed_trades': 0,
                'profitable_trades': 0,
                'failed_trades': 0,
                'open_trades': 0
            },
            'calculated_at': datetime.now().isoformat(),
            'data_source': 'standardized_metrics'
        }
    
    def calculate_module_breakdown(self, trades: List[TradeData]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate metrics broken down by trading module.
        
        Args:
            trades: List of normalized trade data
            
        Returns:
            Dictionary with metrics for each module
        """
        module_breakdown = {}
        
        # Group trades by module
        trades_by_module = {}
        for trade in trades:
            module = trade.module or 'unknown'
            if module not in trades_by_module:
                trades_by_module[module] = []
            trades_by_module[module].append(trade)
        
        # Calculate metrics for each module
        for module, module_trades in trades_by_module.items():
            module_breakdown[module] = self.calculate_performance_metrics(module_trades)
        
        return module_breakdown
    
    def generate_performance_report(self, trades_data: List[Dict[str, Any]], 
                                  source_format: str = 'auto',
                                  include_module_breakdown: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive performance report with standardized metrics.
        
        Args:
            trades_data: Raw trade data from any source
            source_format: Source data format
            include_module_breakdown: Whether to include per-module metrics
            
        Returns:
            Complete performance report with standardized metrics
        """
        # Normalize trade data
        normalized_trades = self.normalize_trade_data(trades_data, source_format)
        
        # Calculate overall metrics
        overall_metrics = self.calculate_performance_metrics(normalized_trades)
        
        # Build report
        report = {
            'overall_performance': overall_metrics,
            'data_quality': {
                'total_trades_processed': len(trades_data),
                'successfully_normalized': len(normalized_trades),
                'normalization_success_rate': round(len(normalized_trades) / len(trades_data) * 100, 1) if trades_data else 0
            },
            'metric_definitions': {
                name: {
                    'name': defn.name,
                    'description': defn.description,
                    'formula': defn.formula,
                    'use_case': defn.use_case
                }
                for name, defn in self.metric_definitions.items()
            }
        }
        
        # Add module breakdown if requested
        if include_module_breakdown and normalized_trades:
            report['module_breakdown'] = self.calculate_module_breakdown(normalized_trades)
        
        return report
    
    def get_metric_explanation(self, metric_type: str) -> Dict[str, str]:
        """Get explanation for a specific metric type"""
        if metric_type in self.metric_definitions:
            defn = self.metric_definitions[metric_type]
            return {
                'name': defn.name,
                'description': defn.description,
                'formula': defn.formula,
                'use_case': defn.use_case,
                'calculation_method': defn.calculation_method
            }
        else:
            return {'error': f'Unknown metric type: {metric_type}'}
    
    def compare_data_sources(self, source1_data: List[Dict], source2_data: List[Dict],
                           source1_format: str = 'auto', source2_format: str = 'auto') -> Dict[str, Any]:
        """
        Compare metrics from two different data sources to identify inconsistencies.
        
        Args:
            source1_data: Trade data from first source
            source2_data: Trade data from second source
            source1_format: Format of first source
            source2_format: Format of second source
            
        Returns:
            Comparison report showing differences
        """
        # Calculate metrics for both sources
        source1_metrics = self.generate_performance_report(source1_data, source1_format, False)
        source2_metrics = self.generate_performance_report(source2_data, source2_format, False)
        
        # Compare metrics
        comparison = {
            'source1': {
                'metrics': source1_metrics['overall_performance']['metrics'],
                'counts': source1_metrics['overall_performance']['raw_counts']
            },
            'source2': {
                'metrics': source2_metrics['overall_performance']['metrics'],
                'counts': source2_metrics['overall_performance']['raw_counts']
            },
            'differences': {},
            'inconsistencies_found': False
        }
        
        # Calculate differences
        for metric_name in ['execution_rate', 'profitability_rate', 'overall_success_rate']:
            val1 = source1_metrics['overall_performance']['metrics'][metric_name]['value']
            val2 = source2_metrics['overall_performance']['metrics'][metric_name]['value']
            difference = abs(val1 - val2)
            
            comparison['differences'][metric_name] = {
                'source1_value': val1,
                'source2_value': val2,
                'absolute_difference': round(difference, 1),
                'percentage_difference': round(difference / max(val1, val2, 1) * 100, 1) if max(val1, val2) > 0 else 0
            }
            
            # Flag significant differences (>5%)
            if difference > 5.0:
                comparison['inconsistencies_found'] = True
        
        return comparison


# Convenience functions for easy integration
def calculate_win_rate(trades_data: List[Dict[str, Any]], 
                      metric_type: str = 'profitability_rate',
                      source_format: str = 'auto') -> float:
    """
    Calculate a specific win rate metric.
    
    Args:
        trades_data: Raw trade data
        metric_type: Type of metric to calculate ('execution_rate', 'profitability_rate', 'overall_success_rate')
        source_format: Source data format
        
    Returns:
        Win rate percentage
    """
    metrics_calc = StandardizedMetrics()
    report = metrics_calc.generate_performance_report(trades_data, source_format, False)
    return report['overall_performance']['metrics'][metric_type]['value']


def get_standardized_metrics_summary(trades_data: List[Dict[str, Any]]) -> str:
    """
    Get a human-readable summary of standardized metrics.
    
    Args:
        trades_data: Raw trade data
        
    Returns:
        Formatted metrics summary string
    """
    metrics_calc = StandardizedMetrics()
    report = metrics_calc.generate_performance_report(trades_data)
    
    metrics = report['overall_performance']['metrics']
    counts = report['overall_performance']['raw_counts']
    
    summary = f"""
📊 STANDARDIZED PERFORMANCE METRICS

✅ {metrics['execution_rate']['label']}: {metrics['execution_rate']['value']}%
   {metrics['execution_rate']['description']}
   ({counts['executed_trades']}/{counts['total_trades']} orders filled)

💰 {metrics['profitability_rate']['label']}: {metrics['profitability_rate']['value']}%
   {metrics['profitability_rate']['description']}
   ({counts['profitable_trades']}/{counts['completed_trades']} profitable)

🎯 {metrics['overall_success_rate']['label']}: {metrics['overall_success_rate']['value']}%
   {metrics['overall_success_rate']['description']}
   ({counts['profitable_trades']}/{counts['total_trades']} overall profitable)

📋 Raw Counts:
   Total Trades: {counts['total_trades']}
   Executed: {counts['executed_trades']}
   Completed: {counts['completed_trades']}
   Profitable: {counts['profitable_trades']}
   Failed: {counts['failed_trades']}
   Open: {counts['open_trades']}
"""
    
    return summary.strip()