#!/usr/bin/env python3
"""
Performance Tracking System
Advanced analytics for trading strategy performance
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database_manager import TradingDatabase

class PerformanceTracker:
    """Advanced performance tracking and analytics"""
    
    def __init__(self, db_path='data/trading_system.db'):
        self.db_path = db_path
        self.db = TradingDatabase(db_path)
        print("✅ Performance tracker initialized")
    
    def calculate_detailed_performance(self, days=30) -> Dict:
        """Calculate comprehensive performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get all virtual trades in period
            cursor.execute('''
                SELECT symbol, action, price, strategy, regime, confidence, timestamp, profit_loss
                FROM virtual_trades 
                WHERE timestamp > ?
                ORDER BY timestamp ASC
            ''', (cutoff_date,))
            
            trades = cursor.fetchall()
            
            if not trades:
                return {'error': 'No trades found in period', 'period_days': days}
            
            # Calculate comprehensive metrics
            total_trades = len(trades)
            strategies = {}
            regimes = {}
            symbols = {}
            daily_performance = {}
            
            for trade in trades:
                symbol, action, price, strategy, regime, confidence, timestamp, profit_loss = trade
                trade_date = timestamp[:10]  # YYYY-MM-DD
                
                # Strategy performance
                if strategy not in strategies:
                    strategies[strategy] = {
                        'trades': 0, 'total_confidence': 0, 'symbols': set()
                    }
                strategies[strategy]['trades'] += 1
                strategies[strategy]['total_confidence'] += confidence
                strategies[strategy]['symbols'].add(symbol)
                
                # Regime performance
                if regime not in regimes:
                    regimes[regime] = {'trades': 0, 'total_confidence': 0}
                regimes[regime]['trades'] += 1
                regimes[regime]['total_confidence'] += confidence
                
                # Symbol performance
                if symbol not in symbols:
                    symbols[symbol] = {'trades': 0, 'strategies': set()}
                symbols[symbol]['trades'] += 1
                symbols[symbol]['strategies'].add(strategy)
                
                # Daily performance
                if trade_date not in daily_performance:
                    daily_performance[trade_date] = {'trades': 0, 'avg_confidence': 0}
                daily_performance[trade_date]['trades'] += 1
            
            # Calculate averages and insights
            performance_summary = {
                'period_days': days,
                'total_trades': total_trades,
                'unique_symbols': len(symbols),
                'unique_strategies': len(strategies),
                'avg_daily_trades': total_trades / min(days, len(daily_performance)),
                'most_active_strategy': max(strategies.items(), key=lambda x: x[1]['trades'])[0],
                'most_active_regime': max(regimes.items(), key=lambda x: x[1]['trades'])[0],
                'strategy_breakdown': {
                    strategy: {
                        'trade_count': data['trades'],
                        'avg_confidence': data['total_confidence'] / data['trades'],
                        'unique_symbols': len(data['symbols']),
                        'percentage': (data['trades'] / total_trades) * 100
                    }
                    for strategy, data in strategies.items()
                },
                'regime_breakdown': {
                    regime: {
                        'trade_count': data['trades'],
                        'avg_confidence': data['total_confidence'] / data['trades'],
                        'percentage': (data['trades'] / total_trades) * 100
                    }
                    for regime, data in regimes.items()
                },
                'top_symbols': sorted(
                    [(symbol, data['trades']) for symbol, data in symbols.items()],
                    key=lambda x: x[1], reverse=True
                )[:10],
                'calculated_at': datetime.now().isoformat()
            }
            
            conn.close()
            return performance_summary
            
        except Exception as e:
            return {'error': f'Performance calculation failed: {e}'}
    
    def get_strategy_comparison(self) -> Dict:
        """Compare performance across different strategies"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get strategy performance over last 30 days
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            
            cursor.execute('''
                SELECT strategy, 
                       COUNT(*) as trade_count,
                       AVG(confidence) as avg_confidence,
                       COUNT(DISTINCT symbol) as unique_symbols,
                       MIN(timestamp) as first_trade,
                       MAX(timestamp) as last_trade
                FROM virtual_trades 
                WHERE timestamp > ?
                GROUP BY strategy
                ORDER BY trade_count DESC
            ''', (cutoff_date,))
            
            strategies = []
            for row in cursor.fetchall():
                strategy, count, avg_conf, symbols, first, last = row
                strategies.append({
                    'strategy': strategy,
                    'trade_count': count,
                    'avg_confidence': round(avg_conf, 3),
                    'unique_symbols': symbols,
                    'first_trade': first,
                    'last_trade': last,
                    'activity_span_days': (datetime.fromisoformat(last) - datetime.fromisoformat(first)).days + 1
                })
            
            conn.close()
            
            return {
                'strategy_comparison': strategies,
                'total_strategies': len(strategies),
                'comparison_period': '30 days',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Strategy comparison failed: {e}'}
    
    def get_market_regime_analysis(self) -> Dict:
        """Analyze performance across different market regimes"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get regime analysis from trading cycles
            cursor.execute('''
                SELECT regime, strategy, confidence, quotes_count, timestamp
                FROM trading_cycles 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 100
            ''', ((datetime.now() - timedelta(days=30)).isoformat(),))
            
            cycles = cursor.fetchall()
            
            if not cycles:
                return {'error': 'No cycle data available'}
            
            regime_analysis = {}
            for regime, strategy, confidence, quotes_count, timestamp in cycles:
                if regime not in regime_analysis:
                    regime_analysis[regime] = {
                        'cycles': 0,
                        'strategies': {},
                        'total_confidence': 0,
                        'total_quotes': 0
                    }
                
                regime_analysis[regime]['cycles'] += 1
                regime_analysis[regime]['total_confidence'] += confidence
                regime_analysis[regime]['total_quotes'] += quotes_count
                
                if strategy not in regime_analysis[regime]['strategies']:
                    regime_analysis[regime]['strategies'][strategy] = 0
                regime_analysis[regime]['strategies'][strategy] += 1
            
            # Calculate regime insights
            regime_insights = {}
            for regime, data in regime_analysis.items():
                regime_insights[regime] = {
                    'cycle_count': data['cycles'],
                    'avg_confidence': data['total_confidence'] / data['cycles'],
                    'avg_quotes_per_cycle': data['total_quotes'] / data['cycles'],
                    'preferred_strategy': max(data['strategies'].items(), key=lambda x: x[1])[0],
                    'strategy_distribution': data['strategies']
                }
            
            conn.close()
            
            return {
                'regime_analysis': regime_insights,
                'total_cycles_analyzed': sum(data['cycles'] for data in regime_analysis.values()),
                'analysis_period': '30 days (last 100 cycles)',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Regime analysis failed: {e}'}
    
    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        report = {
            'report_generated': datetime.now().isoformat(),
            'report_type': 'comprehensive_performance',
            'system_version': 'Enhanced Trader V2'
        }
        
        # Get all performance metrics
        report['detailed_performance'] = self.calculate_detailed_performance(30)
        report['strategy_comparison'] = self.get_strategy_comparison()
        report['regime_analysis'] = self.get_market_regime_analysis()
        
        # Calculate overall health score
        health_score = self.calculate_system_health_score(report)
        report['system_health_score'] = health_score
        
        return report
    
    def calculate_system_health_score(self, report: Dict) -> Dict:
        """Calculate overall system health score"""
        try:
            score = 100  # Start with perfect score
            issues = []
            
            detailed = report.get('detailed_performance', {})
            if 'error' in detailed:
                score -= 30
                issues.append('No trading data available')
            else:
                # Check trading activity
                if detailed.get('total_trades', 0) < 10:
                    score -= 20
                    issues.append('Low trading activity')
                
                # Check strategy diversity
                if detailed.get('unique_strategies', 0) < 2:
                    score -= 15
                    issues.append('Limited strategy diversity')
                
                # Check market coverage
                if detailed.get('unique_symbols', 0) < 5:
                    score -= 10
                    issues.append('Limited market coverage')
            
            # Check regime analysis
            regime = report.get('regime_analysis', {})
            if 'error' in regime:
                score -= 15
                issues.append('Regime analysis unavailable')
            
            # Determine health level
            if score >= 90:
                health_level = 'Excellent'
            elif score >= 75:
                health_level = 'Good'
            elif score >= 60:
                health_level = 'Fair'
            elif score >= 40:
                health_level = 'Poor'
            else:
                health_level = 'Critical'
            
            return {
                'score': max(0, score),
                'level': health_level,
                'issues': issues,
                'recommendations': self.get_health_recommendations(score, issues)
            }
            
        except Exception as e:
            return {
                'score': 0,
                'level': 'Unknown',
                'error': f'Health calculation failed: {e}'
            }
    
    def get_health_recommendations(self, score: int, issues: List[str]) -> List[str]:
        """Get recommendations based on health score"""
        recommendations = []
        
        if 'No trading data available' in issues:
            recommendations.append('Run system for longer to accumulate trading data')
        
        if 'Low trading activity' in issues:
            recommendations.append('Consider increasing market tier for more trading opportunities')
        
        if 'Limited strategy diversity' in issues:
            recommendations.append('Wait for system to develop multiple strategies based on market conditions')
        
        if 'Limited market coverage' in issues:
            recommendations.append('Increase market tier to monitor more symbols')
        
        if score < 60:
            recommendations.append('Review system configuration and ensure stable operation')
        
        if not recommendations:
            recommendations.append('System performing well - continue monitoring')
        
        return recommendations

def test_performance_tracker():
    """Test performance tracking functionality"""
    print("🧪 Testing Performance Tracker...")
    
    tracker = PerformanceTracker()
    
    # Test detailed performance
    detailed = tracker.calculate_detailed_performance(30)
    print(f"✅ Detailed performance: {detailed.get('total_trades', 0)} trades analyzed")
    
    # Test strategy comparison
    comparison = tracker.get_strategy_comparison()
    print(f"✅ Strategy comparison: {comparison.get('total_strategies', 0)} strategies found")
    
    # Test regime analysis
    regime = tracker.get_market_regime_analysis()
    print(f"✅ Regime analysis: {regime.get('total_cycles_analyzed', 0)} cycles analyzed")
    
    # Test comprehensive report
    report = tracker.generate_performance_report()
    health = report.get('system_health_score', {})
    print(f"✅ System health: {health.get('level', 'Unknown')} ({health.get('score', 0)}/100)")
    
    print("🎉 Performance tracker tests completed!")
    
    return report

if __name__ == "__main__":
    test_performance_tracker()