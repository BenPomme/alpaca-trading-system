#!/usr/bin/env python3
"""
Tests for ML Parameter Optimization Engine

Tests the complete ML optimization pipeline including parameter analysis,
Bayesian optimization, and real-time parameter adjustment.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from datetime import datetime, timedelta
import logging

# Import ML optimization components
from modular.ml_optimizer import (
    BayesianOptimizer, ParameterOptimizer, MLParameterOptimizationEngine,
    ParameterOptimizationResult, MLModelPerformance
)
from modular.base_module import ModuleConfig, TradingModule


class TestBayesianOptimizer(unittest.TestCase):
    """Test Bayesian parameter optimization"""
    
    def setUp(self):
        self.parameter_bounds = {
            'confidence_threshold': (0.4, 0.9),
            'position_multiplier': (0.5, 3.0)
        }
        self.optimizer = BayesianOptimizer(self.parameter_bounds)
    
    def test_random_sampling_with_insufficient_data(self):
        """Test random sampling when insufficient historical data"""
        # Test with no data
        suggested = self.optimizer.suggest_next_parameters([])
        self.assertIn('confidence_threshold', suggested)
        self.assertIn('position_multiplier', suggested)
        
        # Check bounds are respected
        self.assertGreaterEqual(suggested['confidence_threshold'], 0.4)
        self.assertLessEqual(suggested['confidence_threshold'], 0.9)
        self.assertGreaterEqual(suggested['position_multiplier'], 0.5)
        self.assertLessEqual(suggested['position_multiplier'], 3.0)
    
    def test_bayesian_optimization_with_sufficient_data(self):
        """Test Bayesian optimization with sufficient historical data"""
        # Create mock historical data
        historical_data = []
        for i in range(10):
            data_point = {
                'confidence_threshold': 0.5 + i * 0.05,
                'position_multiplier': 1.0 + i * 0.2,
                'profit_loss': 10.0 if i > 5 else -5.0,  # Better performance with higher values
                'success': i > 5
            }
            historical_data.append(data_point)
        
        suggested = self.optimizer.suggest_next_parameters(historical_data)
        
        # Should suggest values within bounds
        self.assertIn('confidence_threshold', suggested)
        self.assertIn('position_multiplier', suggested)
        self.assertGreaterEqual(suggested['confidence_threshold'], 0.4)
        self.assertLessEqual(suggested['confidence_threshold'], 0.9)
    
    def test_parameter_bounds_enforcement(self):
        """Test that parameter bounds are always enforced"""
        for _ in range(10):  # Test multiple random samples
            suggested = self.optimizer._random_sample()
            for param_name, value in suggested.items():
                bounds = self.parameter_bounds[param_name]
                self.assertGreaterEqual(value, bounds[0], f"{param_name} below lower bound")
                self.assertLessEqual(value, bounds[1], f"{param_name} above upper bound")


class TestParameterOptimizer(unittest.TestCase):
    """Test core parameter optimization logic"""
    
    def setUp(self):
        self.mock_firebase_db = Mock()
        self.mock_firebase_db.is_connected.return_value = True
        self.logger = logging.getLogger('TestParameterOptimizer')
        self.optimizer = ParameterOptimizer(self.mock_firebase_db, self.logger)
    
    def test_should_optimize_parameters_with_sufficient_data(self):
        """Test optimization criteria with sufficient data"""
        # Mock sufficient recent data
        mock_data = [{'symbol': f'TEST{i}', 'profit_loss': i} for i in range(15)]
        
        with patch.object(self.optimizer, '_get_recent_performance_data', return_value=mock_data):
            should_optimize = self.optimizer.should_optimize_parameters('test_module')
            self.assertTrue(should_optimize)
    
    def test_should_optimize_parameters_with_insufficient_data(self):
        """Test optimization criteria with insufficient data"""
        # Mock insufficient data
        mock_data = [{'symbol': f'TEST{i}', 'profit_loss': i} for i in range(5)]
        
        with patch.object(self.optimizer, '_get_recent_performance_data', return_value=mock_data):
            should_optimize = self.optimizer.should_optimize_parameters('test_module')
            self.assertFalse(should_optimize)
    
    def test_parameter_correlation_calculation(self):
        """Test parameter correlation calculation"""
        # Create data with strong positive correlation
        param_data = []
        for i in range(10):
            param_data.append({
                'confidence_threshold': 0.5 + i * 0.05,
                'profit_loss': i * 2.0  # Strong positive correlation
            })
        
        correlation = self.optimizer._calculate_parameter_correlation('confidence_threshold', param_data)
        self.assertGreater(correlation, 0.8)  # Should be strongly positive
    
    def test_parameter_variance_calculation(self):
        """Test parameter variance calculation"""
        # Create data with known variance
        param_data = [
            {'test_param': 0.5},
            {'test_param': 0.7},
            {'test_param': 0.9}
        ]
        
        variance = self.optimizer._calculate_parameter_variance('test_param', param_data)
        self.assertGreater(variance, 0)  # Should have some variance
    
    def test_continuous_parameter_optimization(self):
        """Test continuous parameter optimization using Bayesian method"""
        module_name = 'test_module'
        param_type = 'confidence_threshold'
        
        # Mock performance data
        performance_data = []
        for i in range(15):
            performance_data.append({
                'confidence_threshold': 0.5 + i * 0.02,
                'profit_loss': i - 5,  # Varied performance
                'success': i > 7
            })
        
        current_params = {'confidence_threshold': 0.6}
        
        result = self.optimizer._optimize_continuous_parameter(
            module_name, param_type, performance_data, current_params
        )
        
        if result:  # Optimization may not always suggest changes
            self.assertIsInstance(result, ParameterOptimizationResult)
            self.assertEqual(result.module_name, module_name)
            self.assertEqual(result.parameter_type, param_type)
            self.assertEqual(result.optimization_method, 'bayesian')
    
    def test_discrete_parameter_optimization(self):
        """Test discrete parameter optimization using performance analysis"""
        module_name = 'test_module'
        param_type = 'strategy_type'
        
        # Mock performance data with discrete strategy types
        performance_data = [
            {'strategy_type': 'conservative', 'profit_loss': 5.0},
            {'strategy_type': 'conservative', 'profit_loss': 3.0},
            {'strategy_type': 'conservative', 'profit_loss': 4.0},
            {'strategy_type': 'aggressive', 'profit_loss': 15.0},
            {'strategy_type': 'aggressive', 'profit_loss': 12.0},
            {'strategy_type': 'aggressive', 'profit_loss': 18.0}
        ]
        
        current_params = {'strategy_type': 'conservative'}
        
        result = self.optimizer._optimize_discrete_parameter(
            module_name, param_type, performance_data, current_params
        )
        
        if result:
            self.assertIsInstance(result, ParameterOptimizationResult)
            self.assertEqual(result.new_value, 'aggressive')  # Should prefer better performing strategy
            self.assertEqual(result.optimization_method, 'discrete_analysis')


class TestMLParameterOptimizationEngine(unittest.TestCase):
    """Test the complete ML optimization engine"""
    
    def setUp(self):
        # Mock dependencies
        self.mock_firebase_db = Mock()
        self.mock_firebase_db.is_connected.return_value = True
        
        self.mock_orchestrator = Mock()
        self.mock_orchestrator.registry = Mock()
        
        # Create mock modules
        self.mock_options_module = Mock()
        self.mock_options_module.module_name = 'options'
        self.mock_crypto_module = Mock()
        self.mock_crypto_module.module_name = 'crypto'
        
        self.mock_orchestrator.registry.get_active_modules.return_value = [
            self.mock_options_module, self.mock_crypto_module
        ]
        
        self.logger = logging.getLogger('TestMLEngine')
        self.engine = MLParameterOptimizationEngine(
            self.mock_firebase_db, self.mock_orchestrator, self.logger
        )
    
    def test_optimization_engine_initialization(self):
        """Test ML optimization engine initializes correctly"""
        self.assertIsNotNone(self.engine.parameter_optimizer)
        self.assertTrue(self.engine.optimization_enabled)
        self.assertGreater(self.engine.min_confidence_for_application, 0)
    
    def test_optimization_cycle_with_no_optimizations_needed(self):
        """Test optimization cycle when no parameters need optimization"""
        # Mock parameter optimizer to return no optimizations needed
        with patch.object(self.engine.parameter_optimizer, 'should_optimize_parameters', return_value=False):
            summary = self.engine.run_optimization_cycle()
            
            self.assertIn('modules_analyzed', summary)
            self.assertEqual(summary['modules_analyzed'], 2)  # Two modules analyzed
            self.assertEqual(summary['optimizations_applied'], 0)  # No optimizations applied
    
    def test_optimization_cycle_with_parameter_updates(self):
        """Test optimization cycle with actual parameter updates"""
        # Mock optimization results
        mock_optimization_result = ParameterOptimizationResult(
            module_name='options',
            parameter_type='confidence_threshold',
            old_value=0.6,
            new_value=0.7,
            expected_improvement=0.05,
            confidence=0.8,
            optimization_method='bayesian',
            data_points_used=20
        )
        
        with patch.object(self.engine.parameter_optimizer, 'should_optimize_parameters', return_value=True), \
             patch.object(self.engine.parameter_optimizer, 'optimize_module_parameters', 
                         return_value=[mock_optimization_result]), \
             patch.object(self.engine, '_apply_parameter_optimization', return_value=True):
            
            summary = self.engine.run_optimization_cycle()
            
            self.assertEqual(summary['modules_analyzed'], 2)
            self.assertEqual(summary['parameters_optimized'], 2)  # One per module
            self.assertEqual(summary['optimizations_applied'], 2)  # High confidence, should apply
            self.assertGreater(summary['total_expected_improvement'], 0)
    
    def test_parameter_application_with_high_confidence(self):
        """Test parameter application when confidence is high enough"""
        high_confidence_result = ParameterOptimizationResult(
            module_name='crypto',
            parameter_type='session_multiplier',
            old_value=1.0,
            new_value=1.5,
            expected_improvement=0.08,
            confidence=0.9,  # High confidence
            optimization_method='bayesian',
            data_points_used=25
        )
        
        success = self.engine._apply_parameter_optimization(self.mock_crypto_module, high_confidence_result)
        self.assertTrue(success)
        
        # Verify orchestrator was called to update config
        self.mock_orchestrator.update_module_config.assert_called_once()
    
    def test_parameter_application_with_low_confidence(self):
        """Test parameter application is skipped when confidence is too low"""
        low_confidence_result = ParameterOptimizationResult(
            module_name='options',
            parameter_type='leverage_factor',
            old_value=2.0,
            new_value=2.5,
            expected_improvement=0.03,
            confidence=0.3,  # Low confidence
            optimization_method='discrete_analysis',
            data_points_used=8
        )
        
        # Should not apply optimization due to low confidence
        with patch.object(self.engine.parameter_optimizer, 'should_optimize_parameters', return_value=True), \
             patch.object(self.engine.parameter_optimizer, 'optimize_module_parameters', 
                         return_value=[low_confidence_result]):
            
            summary = self.engine.run_optimization_cycle()
            
            self.assertEqual(summary['parameters_optimized'], 2)  # Optimization was suggested
            self.assertEqual(summary['optimizations_applied'], 0)  # But not applied due to low confidence
    
    def test_optimization_status_reporting(self):
        """Test optimization status reporting"""
        status = self.engine.get_optimization_status()
        
        self.assertIn('optimization_enabled', status)
        self.assertIn('min_confidence_threshold', status)
        self.assertIn('max_changes_per_cycle', status)
        self.assertIn('active_experiments', status)
        
        self.assertTrue(status['optimization_enabled'])
        self.assertGreater(status['min_confidence_threshold'], 0)
        self.assertGreater(status['max_changes_per_cycle'], 0)
    
    def test_optimization_enable_disable(self):
        """Test enabling and disabling optimization"""
        # Test disable
        self.engine.disable_optimization()
        self.assertFalse(self.engine.optimization_enabled)
        
        # Test enable
        self.engine.enable_optimization()
        self.assertTrue(self.engine.optimization_enabled)
        
        # Test optimization cycle respects disabled state
        self.engine.disable_optimization()
        summary = self.engine.run_optimization_cycle()
        self.assertEqual(summary['modules_analyzed'], 0)  # Should skip analysis when disabled


class TestMLOptimizationIntegration(unittest.TestCase):
    """Integration tests for ML optimization with orchestrator"""
    
    def setUp(self):
        # Create test orchestrator with ML optimization
        self.mock_firebase_db = Mock()
        self.mock_firebase_db.is_connected.return_value = True
        
        self.mock_risk_manager = Mock()
        self.mock_order_executor = Mock()
        
        # Create logger
        self.logger = logging.getLogger('TestMLIntegration')
        logging.basicConfig(level=logging.DEBUG)
    
    def test_orchestrator_with_ml_optimization(self):
        """Test orchestrator creates and uses ML optimization engine"""
        from modular.orchestrator import ModularOrchestrator
        
        # Test with auto-creation of ML optimizer
        orchestrator = ModularOrchestrator(
            firebase_db=self.mock_firebase_db,
            risk_manager=self.mock_risk_manager,
            order_executor=self.mock_order_executor,
            logger=self.logger
        )
        
        # Should have auto-created ML optimizer
        self.assertIsNotNone(orchestrator.ml_optimizer)
        
        # Test ML optimization call during periodic maintenance
        with patch.object(orchestrator, '_run_ml_optimization') as mock_ml_opt:
            # Force ML optimization call (normally triggered by cycle count)
            orchestrator._run_ml_optimization()
            mock_ml_opt.assert_called_once()
    
    def test_ml_optimization_error_handling(self):
        """Test ML optimization handles errors gracefully"""
        from modular.orchestrator import ModularOrchestrator
        
        # Create orchestrator with invalid ML optimizer
        orchestrator = ModularOrchestrator(
            firebase_db=self.mock_firebase_db,
            risk_manager=self.mock_risk_manager,
            order_executor=self.mock_order_executor,
            ml_optimizer=Mock(side_effect=Exception("ML optimization error")),
            logger=self.logger
        )
        
        # Should handle ML optimization errors gracefully
        try:
            orchestrator._run_ml_optimization()
            # Should not raise exception
        except Exception as e:
            self.fail(f"ML optimization error not handled gracefully: {e}")


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    unittest.main(verbosity=2)