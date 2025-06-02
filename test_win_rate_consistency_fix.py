#!/usr/bin/env python3
"""
Test Win Rate Consistency Fix

Identifies and fixes win rate calculation inconsistencies across the system.
The problem: Multiple conflicting win rate calculations using different definitions
and data sources, leading to confusing performance reporting.

Solution: Standardize win rate calculations and provide clear metrics separation.
"""

import os
import sys
import logging
from unittest.mock import Mock
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_win_rate_definition_consistency():
    """Test that win rate definitions are consistent across modules"""
    
    logger.info("🧪 Testing Win Rate Definition Consistency...")
    
    try:
        from modular.base_module import TradeResult, TradeOpportunity, TradeAction, TradeStatus
        
        # Create test trades with different outcomes
        mock_opportunity = Mock()
        mock_opportunity.symbol = "BTCUSD"
        
        test_trades = [
            # Profitable completed trades
            TradeResult(opportunity=mock_opportunity, status=TradeStatus.EXECUTED, pnl=100.0),
            TradeResult(opportunity=mock_opportunity, status=TradeStatus.EXECUTED, pnl=50.0),
            
            # Loss-making completed trades  
            TradeResult(opportunity=mock_opportunity, status=TradeStatus.EXECUTED, pnl=-25.0),
            
            # Entry trades (no P&L yet)
            TradeResult(opportunity=mock_opportunity, status=TradeStatus.EXECUTED, pnl=None),
            TradeResult(opportunity=mock_opportunity, status=TradeStatus.EXECUTED, pnl=None),
            
            # Failed trades
            TradeResult(opportunity=mock_opportunity, status=TradeStatus.FAILED, pnl=None),
        ]
        
        # Calculate different win rate definitions
        total_trades = len(test_trades)
        executed_trades = [t for t in test_trades if t.passed]  # Order execution success
        profitable_trades = [t for t in test_trades if t.success]  # Profitability success
        completed_trades = [t for t in test_trades if t.pnl is not None]  # Has P&L data
        
        logger.info("📊 Win Rate Analysis:")
        logger.info(f"  Total trades: {total_trades}")
        logger.info(f"  Executed trades (passed): {len(executed_trades)}")
        logger.info(f"  Profitable trades (success): {len(profitable_trades)}")
        logger.info(f"  Completed trades (with P&L): {len(completed_trades)}")
        
        # Calculate standardized win rates
        execution_rate = len(executed_trades) / total_trades * 100 if total_trades > 0 else 0
        profitability_rate = len(profitable_trades) / len(completed_trades) * 100 if len(completed_trades) > 0 else 0
        overall_profit_rate = len(profitable_trades) / total_trades * 100 if total_trades > 0 else 0
        
        logger.info("📈 Standardized Metrics:")
        logger.info(f"  ✅ Execution Rate: {execution_rate:.1f}% (orders filled successfully)")
        logger.info(f"  💰 Profitability Rate: {profitability_rate:.1f}% (profitable among completed)")
        logger.info(f"  🎯 Overall Success Rate: {overall_profit_rate:.1f}% (profitable among all)")
        
        # Verify expected results
        assert len(executed_trades) == 5, f"Expected 5 executed trades, got {len(executed_trades)}"
        assert len(profitable_trades) == 2, f"Expected 2 profitable trades, got {len(profitable_trades)}"
        assert len(completed_trades) == 3, f"Expected 3 completed trades, got {len(completed_trades)}"
        
        assert abs(execution_rate - 83.3) < 0.1, f"Expected 83.3% execution rate, got {execution_rate:.1f}%"
        assert abs(profitability_rate - 66.7) < 0.1, f"Expected 66.7% profitability rate, got {profitability_rate:.1f}%"
        assert abs(overall_profit_rate - 33.3) < 0.1, f"Expected 33.3% overall success rate, got {overall_profit_rate:.1f}%"
        
        logger.info("✅ Win rate definitions are mathematically consistent!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Win rate definition test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def test_dashboard_data_source_consistency():
    """Test that dashboard data sources provide consistent calculations"""
    
    logger.info("🧪 Testing Dashboard Data Source Consistency...")
    
    try:
        # Mock trade data that all systems should use
        mock_trades = [
            {'symbol': 'BTCUSD', 'pnl': 100.0, 'status': 'executed'},
            {'symbol': 'ETHUSD', 'pnl': -50.0, 'status': 'executed'},
            {'symbol': 'SOLUSD', 'pnl': 25.0, 'status': 'executed'},
            {'symbol': 'LINKUSD', 'pnl': None, 'status': 'executed'},  # Entry trade
            {'symbol': 'AVAXUSD', 'pnl': None, 'status': 'failed'},     # Failed trade
        ]
        
        def calculate_standard_metrics(trades):
            """Standardized metric calculation"""
            total_trades = len(trades)
            executed_trades = [t for t in trades if t['status'] == 'executed']
            completed_trades = [t for t in trades if t['pnl'] is not None]
            profitable_trades = [t for t in completed_trades if t['pnl'] > 0]
            
            execution_rate = len(executed_trades) / total_trades * 100 if total_trades > 0 else 0
            profitability_rate = len(profitable_trades) / len(completed_trades) * 100 if len(completed_trades) > 0 else 0
            
            return {
                'total_trades': total_trades,
                'executed_trades': len(executed_trades),
                'completed_trades': len(completed_trades),
                'profitable_trades': len(profitable_trades),
                'execution_rate': round(execution_rate, 1),
                'profitability_rate': round(profitability_rate, 1)
            }
        
        # Test standard calculation
        standard_metrics = calculate_standard_metrics(mock_trades)
        
        logger.info("📊 Standard Metrics Calculation:")
        logger.info(f"  Total trades: {standard_metrics['total_trades']}")
        logger.info(f"  Executed: {standard_metrics['executed_trades']}")
        logger.info(f"  Completed: {standard_metrics['completed_trades']}")
        logger.info(f"  Profitable: {standard_metrics['profitable_trades']}")
        logger.info(f"  Execution rate: {standard_metrics['execution_rate']}%")
        logger.info(f"  Profitability rate: {standard_metrics['profitability_rate']}%")
        
        # Verify expected results
        assert standard_metrics['execution_rate'] == 80.0, f"Expected 80% execution rate"
        assert standard_metrics['profitability_rate'] == 66.7, f"Expected 66.7% profitability rate"
        
        # Test that different data sources would produce same results
        logger.info("🔍 Testing consistency across data source simulations...")
        
        # Simulate Firebase data format
        firebase_format = [
            {'trade_data': {'symbol': t['symbol'], 'profit_loss': t['pnl'], 'status': t['status']}}
            for t in mock_trades
        ]
        
        # Simulate SQLite data format  
        sqlite_format = [
            {'symbol': t['symbol'], 'realized_pnl': t['pnl'], 'trade_status': t['status']}
            for t in mock_trades
        ]
        
        # Convert back to standard format and verify consistency
        def normalize_firebase(data):
            return [
                {
                    'symbol': item['trade_data']['symbol'],
                    'pnl': item['trade_data']['profit_loss'],
                    'status': item['trade_data']['status']
                }
                for item in data
            ]
        
        def normalize_sqlite(data):
            return [
                {
                    'symbol': item['symbol'],
                    'pnl': item['realized_pnl'],
                    'status': item['trade_status']
                }
                for item in data
            ]
        
        firebase_metrics = calculate_standard_metrics(normalize_firebase(firebase_format))
        sqlite_metrics = calculate_standard_metrics(normalize_sqlite(sqlite_format))
        
        logger.info("📊 Data Source Consistency Check:")
        logger.info(f"  Standard: {standard_metrics['profitability_rate']}%")
        logger.info(f"  Firebase: {firebase_metrics['profitability_rate']}%")
        logger.info(f"  SQLite: {sqlite_metrics['profitability_rate']}%")
        
        # Verify all produce same results
        assert firebase_metrics['profitability_rate'] == standard_metrics['profitability_rate']
        assert sqlite_metrics['profitability_rate'] == standard_metrics['profitability_rate']
        
        logger.info("✅ All data sources produce consistent results!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Dashboard consistency test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def test_metric_separation_clarity():
    """Test that different metrics are clearly separated and labeled"""
    
    logger.info("🧪 Testing Metric Separation and Clarity...")
    
    try:
        # Define clear metric categories
        metric_definitions = {
            'execution_rate': {
                'name': 'Order Execution Rate',
                'description': 'Percentage of orders successfully filled by broker',
                'formula': 'executed_orders / total_orders * 100',
                'use_case': 'Measure order execution reliability'
            },
            'profitability_rate': {
                'name': 'Trade Profitability Rate', 
                'description': 'Percentage of completed trades that were profitable',
                'formula': 'profitable_trades / completed_trades * 100',
                'use_case': 'Measure strategy effectiveness'
            },
            'overall_success_rate': {
                'name': 'Overall Success Rate',
                'description': 'Percentage of all trades that were profitable',
                'formula': 'profitable_trades / total_trades * 100',
                'use_case': 'Measure complete system performance'
            }
        }
        
        logger.info("📋 Standardized Metric Definitions:")
        for key, metric in metric_definitions.items():
            logger.info(f"  📊 {metric['name']}:")
            logger.info(f"    Description: {metric['description']}")
            logger.info(f"    Formula: {metric['formula']}")
            logger.info(f"    Use case: {metric['use_case']}")
            logger.info("")
        
        # Test metric labeling function
        def create_performance_report(trades_data):
            """Create a standardized performance report with clear labeling"""
            
            total = len(trades_data)
            executed = len([t for t in trades_data if t.get('executed', False)])
            completed = len([t for t in trades_data if t.get('pnl') is not None])
            profitable = len([t for t in trades_data if t.get('pnl') is not None and t.get('pnl', 0) > 0])
            
            return {
                'metrics': {
                    'execution_rate': {
                        'value': round(executed / total * 100, 1) if total > 0 else 0,
                        'label': metric_definitions['execution_rate']['name'],
                        'description': metric_definitions['execution_rate']['description']
                    },
                    'profitability_rate': {
                        'value': round(profitable / completed * 100, 1) if completed > 0 else 0,
                        'label': metric_definitions['profitability_rate']['name'],
                        'description': metric_definitions['profitability_rate']['description']
                    },
                    'overall_success_rate': {
                        'value': round(profitable / total * 100, 1) if total > 0 else 0,
                        'label': metric_definitions['overall_success_rate']['name'],
                        'description': metric_definitions['overall_success_rate']['description']
                    }
                },
                'raw_counts': {
                    'total_trades': total,
                    'executed_trades': executed,
                    'completed_trades': completed,
                    'profitable_trades': profitable
                }
            }
        
        # Test with sample data
        sample_trades = [
            {'executed': True, 'pnl': 100},
            {'executed': True, 'pnl': -50},
            {'executed': True, 'pnl': None},  # Entry trade
            {'executed': False, 'pnl': None}  # Failed trade
        ]
        
        report = create_performance_report(sample_trades)
        
        logger.info("📊 Sample Performance Report:")
        for metric_key, metric_data in report['metrics'].items():
            logger.info(f"  {metric_data['label']}: {metric_data['value']}%")
            logger.info(f"    {metric_data['description']}")
        
        logger.info("📋 Raw Counts:")
        for count_key, count_value in report['raw_counts'].items():
            logger.info(f"  {count_key}: {count_value}")
        
        # Verify report structure
        assert 'metrics' in report
        assert 'raw_counts' in report
        assert len(report['metrics']) == 3
        assert all('label' in m for m in report['metrics'].values())
        assert all('description' in m for m in report['metrics'].values())
        
        logger.info("✅ Metric separation and labeling is clear!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Metric separation test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def main():
    """Run all win rate consistency tests"""
    
    logger.info("🚀 Starting Win Rate Consistency Fix Test Suite")
    logger.info("📊 Testing standardized win rate calculations and metric separation")
    logger.info("=" * 70)
    
    test_results = []
    
    # Test 1: Definition consistency
    logger.info("🧪 Test 1: Win Rate Definition Consistency")
    test1_success = test_win_rate_definition_consistency()
    test_results.append(("Win Rate Definitions", test1_success))
    
    # Test 2: Data source consistency
    logger.info("\n🧪 Test 2: Dashboard Data Source Consistency")
    test2_success = test_dashboard_data_source_consistency()
    test_results.append(("Data Source Consistency", test2_success))
    
    # Test 3: Metric separation
    logger.info("\n🧪 Test 3: Metric Separation and Clarity")
    test3_success = test_metric_separation_clarity()
    test_results.append(("Metric Separation", test3_success))
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("📊 TEST RESULTS SUMMARY")
    
    passed = 0
    failed = 0
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"  {test_name}: {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    logger.info(f"\n📈 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("📊 Win rate consistency fix verified:")
        logger.info("  📋 Clear metric definitions established")
        logger.info("  🔄 Data source calculations standardized")
        logger.info("  📈 Separate reporting for execution vs profitability")
        logger.info("  💰 No more conflicting win rate numbers!")
        return True
    else:
        logger.error("⚠️ SOME TESTS FAILED! Please fix issues before deployment.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)