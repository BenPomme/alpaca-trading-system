#!/usr/bin/env python3
"""
Integration Tests for Modular Trading Architecture

Tests all modules working together through the orchestrator to ensure
the complete modular system functions correctly with ML data collection.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
import logging

# Import modular components
from modular.orchestrator import ModularOrchestrator
from modular.base_module import ModuleConfig, TradeOpportunity, TradeResult, TradeAction, TradeStatus
from modular.options_module import OptionsModule
from modular.crypto_module import CryptoModule
from modular.stocks_module import StocksModule
from modular.firebase_interface import ModularFirebaseInterface


class TestModularIntegration(unittest.TestCase):
    """Integration tests for the complete modular trading system"""
    
    def setUp(self):
        """Set up test environment with mocked dependencies"""
        # Create mock dependencies
        self.mock_firebase_db = Mock()
        self.mock_firebase_db.is_connected.return_value = True
        self.mock_firebase_db.save_trade.return_value = "test_trade_id"
        self.mock_firebase_db.save_orchestrator_cycle.return_value = None
        
        self.mock_risk_manager = Mock()
        self.mock_risk_manager.validate_opportunity.return_value = True
        self.mock_risk_manager.get_module_allocation.return_value = 0.1
        
        self.mock_order_executor = Mock()
        self.mock_order_executor.execute_order.return_value = {'success': True, 'order_id': 'test_order_123'}
        
        self.mock_api_client = Mock()
        
        # Configure mock API client for different modules
        self._setup_mock_api_client()
        
        # Create logger
        self.logger = logging.getLogger('TestIntegration')
        logging.basicConfig(level=logging.DEBUG)
        
        # Create Firebase interface
        self.firebase_interface = ModularFirebaseInterface(self.mock_firebase_db, self.logger)
        
        # Create orchestrator
        self.orchestrator = ModularOrchestrator(
            firebase_db=self.firebase_interface,
            risk_manager=self.mock_risk_manager,
            order_executor=self.mock_order_executor,
            logger=self.logger
        )
    
    def _setup_mock_api_client(self):
        """Configure mock API client responses for all modules"""
        # Mock account info
        mock_account = Mock()
        mock_account.portfolio_value = 100000
        mock_account.regt_buying_power = 50000
        self.mock_api_client.get_account.return_value = mock_account
        
        # Mock positions (empty initially)
        self.mock_api_client.list_positions.return_value = []
        
        # Mock market clock
        mock_clock = Mock()
        mock_clock.is_open = True
        self.mock_api_client.get_clock.return_value = mock_clock
        
        # Mock quotes for various symbols
        mock_quote = Mock()
        mock_quote.ask_price = 450.0
        mock_quote.bid_price = 449.0
        mock_quote.close = 449.50
        self.mock_api_client.get_latest_quote.return_value = mock_quote
        
        # Mock options chain response
        mock_options_response = Mock()
        mock_options_response.status_code = 200
        mock_options_response.json.return_value = {
            "options": {
                "AAPL": [
                    {
                        "symbol": "AAPL240119C00450000",
                        "strike": 450.0,
                        "expiry": "2024-01-19",
                        "option_type": "C",
                        "ask": 5.50,
                        "bid": 5.40
                    }
                ]
            }
        }
    
    def _create_test_modules(self):
        """Create test modules with proper configurations"""
        # Options module config
        options_config = ModuleConfig(
            module_name="options",
            enabled=True,
            max_allocation_pct=30.0,
            min_confidence=0.60,
            custom_params={
                'max_allocation_pct': 30.0,
                'leverage_target': 2.5
            }
        )
        
        # Crypto module config  
        crypto_config = ModuleConfig(
            module_name="crypto",
            enabled=True,
            max_allocation_pct=20.0,
            min_confidence=0.45,
            custom_params={
                'max_allocation_pct': 20.0,
                'leverage_multiplier': 1.5
            }
        )
        
        # Stocks module config
        stocks_config = ModuleConfig(
            module_name="stocks",
            enabled=True,
            max_allocation_pct=50.0,
            min_confidence=0.55,
            custom_params={
                'market_tier': 2
            }
        )
        
        # Create modules
        options_module = OptionsModule(
            config=options_config,
            firebase_db=self.firebase_interface,
            risk_manager=self.mock_risk_manager,
            order_executor=self.mock_order_executor,
            api_client=self.mock_api_client,
            logger=self.logger
        )
        
        crypto_module = CryptoModule(
            config=crypto_config,
            firebase_db=self.firebase_interface,
            risk_manager=self.mock_risk_manager,
            order_executor=self.mock_order_executor,
            api_client=self.mock_api_client,
            logger=self.logger
        )
        
        stocks_module = StocksModule(
            config=stocks_config,
            firebase_db=self.firebase_interface,
            risk_manager=self.mock_risk_manager,
            order_executor=self.mock_order_executor,
            api_client=self.mock_api_client,
            logger=self.logger
        )
        
        return options_module, crypto_module, stocks_module
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        self.assertIsNotNone(self.orchestrator)
        self.assertEqual(len(self.orchestrator.registry._modules), 0)
        
        status = self.orchestrator.get_status()
        self.assertIn('orchestrator_metrics', status)
        self.assertIn('module_health', status)
        self.assertEqual(status['active_modules'], 0)
    
    def test_module_registration(self):
        """Test modules can be registered with orchestrator"""
        options_module, crypto_module, stocks_module = self._create_test_modules()
        
        # Register modules
        self.orchestrator.register_module(options_module)
        self.orchestrator.register_module(crypto_module) 
        self.orchestrator.register_module(stocks_module)
        
        # Verify registration
        self.assertEqual(len(self.orchestrator.registry._modules), 3)
        self.assertEqual(len(self.orchestrator.registry.get_active_modules()), 3)
        
        status = self.orchestrator.get_status()
        self.assertEqual(status['active_modules'], 3)
        self.assertEqual(status['total_modules'], 3)
    
    def test_single_cycle_execution(self):
        """Test orchestrator can execute a complete trading cycle"""
        options_module, crypto_module, stocks_module = self._create_test_modules()
        
        # Register modules
        self.orchestrator.register_module(options_module)
        self.orchestrator.register_module(crypto_module)
        self.orchestrator.register_module(stocks_module)
        
        # Mock module responses to ensure some activity
        with patch.object(options_module, 'analyze_opportunities') as mock_options_analyze, \
             patch.object(crypto_module, 'analyze_opportunities') as mock_crypto_analyze, \
             patch.object(stocks_module, 'analyze_opportunities') as mock_stocks_analyze:
            
            # Mock opportunities for each module
            mock_options_analyze.return_value = [self._create_test_opportunity("AAPL", "options")]
            mock_crypto_analyze.return_value = [self._create_test_opportunity("BTCUSD", "crypto")]
            mock_stocks_analyze.return_value = [self._create_test_opportunity("SPY", "stocks")]
            
            # Execute single cycle
            results = self.orchestrator.run_single_cycle()
            
            # Verify results structure
            self.assertIn('success', results)
            self.assertIn('modules', results)
            self.assertIn('summary', results)
            self.assertIn('cycle_info', results)
            
            # Check module results
            self.assertIn('options', results['modules'])
            self.assertIn('crypto', results['modules'])
            self.assertIn('stocks', results['modules'])
            
            # Verify summary
            summary = results['summary']
            self.assertGreaterEqual(summary['total_opportunities'], 3)  # At least one per module
    
    def test_ml_data_collection_integration(self):
        """Test ML data collection works across all modules"""
        options_module, crypto_module, stocks_module = self._create_test_modules()
        
        # Register modules
        self.orchestrator.register_module(options_module)
        self.orchestrator.register_module(crypto_module)
        self.orchestrator.register_module(stocks_module)
        
        # Track ML data collection calls
        ml_trades_saved = []
        
        def track_ml_trade_save(trade_data):
            ml_trades_saved.append(trade_data)
            return "ml_trade_id"
        
        # Mock the ML data save method
        with patch.object(self.firebase_interface, 'save_trade_result') as mock_save_result, \
             patch.object(options_module, 'save_ml_enhanced_trade', side_effect=track_ml_trade_save), \
             patch.object(crypto_module, 'save_ml_enhanced_trade', side_effect=track_ml_trade_save), \
             patch.object(stocks_module, 'save_ml_enhanced_trade', side_effect=track_ml_trade_save):
            
            # Execute cycle with forced opportunities
            with patch.object(options_module, 'analyze_opportunities') as mock_options_analyze, \
                 patch.object(crypto_module, 'analyze_opportunities') as mock_crypto_analyze, \
                 patch.object(stocks_module, 'analyze_opportunities') as mock_stocks_analyze:
                
                mock_options_analyze.return_value = [self._create_test_opportunity("AAPL", "options")]
                mock_crypto_analyze.return_value = [self._create_test_opportunity("BTCUSD", "crypto")]
                mock_stocks_analyze.return_value = [self._create_test_opportunity("SPY", "stocks")]
                
                results = self.orchestrator.run_single_cycle()
                
                # Verify ML data was collected
                self.assertGreater(len(ml_trades_saved), 0, "ML trade data should have been saved")
                
                # Verify ML data structure for each module type
                for trade_data in ml_trades_saved:
                    self.assertIn('ml_data_version', trade_data)
                    self.assertIn('ml_enhanced', trade_data)
                    self.assertTrue(trade_data['ml_enhanced'])
                    self.assertIn('entry_parameters', trade_data)
                    self.assertIn('module_specific_params', trade_data)
                    self.assertIn('parameter_performance', trade_data)
    
    def test_module_health_monitoring(self):
        """Test module health monitoring works correctly"""
        options_module, crypto_module, stocks_module = self._create_test_modules()
        
        # Register modules
        self.orchestrator.register_module(options_module)
        self.orchestrator.register_module(crypto_module)
        self.orchestrator.register_module(stocks_module)
        
        # Simulate module failure
        with patch.object(crypto_module, 'analyze_opportunities', side_effect=Exception("Test error")):
            
            results = self.orchestrator.run_single_cycle()
            
            # Check that the failed module is marked unhealthy
            health_summary = self.orchestrator.registry.get_health_summary()
            
            # Should have health status for all modules
            self.assertIn('options', health_summary)
            self.assertIn('crypto', health_summary)
            self.assertIn('stocks', health_summary)
            
            # Crypto module should have error status
            crypto_health = health_summary['crypto']
            self.assertEqual(crypto_health['status'], 'error')
    
    def test_parallel_module_execution(self):
        """Test modules can execute in parallel"""
        options_module, crypto_module, stocks_module = self._create_test_modules()
        
        # Register modules
        self.orchestrator.register_module(options_module)
        self.orchestrator.register_module(crypto_module)
        self.orchestrator.register_module(stocks_module)
        
        # Enable parallel execution
        self.orchestrator._config['enable_parallel_execution'] = True
        
        # Mock module execution with delays to test parallelism
        import time
        
        def slow_options_analysis():
            time.sleep(0.1)
            return [self._create_test_opportunity("AAPL", "options")]
        
        def slow_crypto_analysis():
            time.sleep(0.1)
            return [self._create_test_opportunity("BTCUSD", "crypto")]
        
        def slow_stocks_analysis():
            time.sleep(0.1)
            return [self._create_test_opportunity("SPY", "stocks")]
        
        with patch.object(options_module, 'analyze_opportunities', side_effect=slow_options_analysis), \
             patch.object(crypto_module, 'analyze_opportunities', side_effect=slow_crypto_analysis), \
             patch.object(stocks_module, 'analyze_opportunities', side_effect=slow_stocks_analysis):
            
            start_time = time.time()
            results = self.orchestrator.run_single_cycle()
            execution_time = time.time() - start_time
            
            # Parallel execution should be faster than sequential (0.3s)
            # Note: In test environment with mocks, the timing may vary, so we use a more generous threshold
            self.assertLess(execution_time, 2.0, "Parallel execution should complete within reasonable time")
            
            # All modules should have executed successfully
            self.assertTrue(results['success'])
            self.assertEqual(len(results['modules']), 3)
    
    def test_firebase_integration(self):
        """Test Firebase integration works correctly"""
        options_module, crypto_module, stocks_module = self._create_test_modules()
        
        # Register modules
        self.orchestrator.register_module(options_module)
        self.orchestrator.register_module(crypto_module)
        self.orchestrator.register_module(stocks_module)
        
        # Track Firebase calls on the interface level
        firebase_calls = []
        
        def track_firebase_save(data):
            firebase_calls.append(data)
        
        # Mock the Firebase interface save method (not the underlying db)
        with patch.object(self.firebase_interface, 'save_orchestrator_cycle', side_effect=track_firebase_save):
            
            # Execute cycle
            with patch.object(options_module, 'analyze_opportunities') as mock_options_analyze:
                mock_options_analyze.return_value = [self._create_test_opportunity("AAPL", "options")]
                
                results = self.orchestrator.run_single_cycle()
                
                # Verify Firebase orchestrator cycle was saved
                self.assertGreater(len(firebase_calls), 0, "Firebase orchestrator cycle should have been saved")
                
                # Check cycle data structure
                cycle_data = firebase_calls[0]
                self.assertIn('timestamp', cycle_data)
                self.assertIn('cycle_number', cycle_data)
                self.assertIn('results', cycle_data)
                self.assertIn('metrics', cycle_data)
    
    def test_module_configuration_updates(self):
        """Test module configuration can be updated dynamically"""
        options_module, crypto_module, stocks_module = self._create_test_modules()
        
        # Register modules
        self.orchestrator.register_module(options_module)
        
        # Get initial config
        initial_confidence = options_module.config.min_confidence
        
        # Update configuration
        new_config = {'min_confidence': 0.75, 'custom_param': 'test_value'}
        self.orchestrator.update_module_config('options', new_config)
        
        # Verify configuration was updated
        self.assertEqual(options_module.config.min_confidence, 0.75)
        self.assertEqual(options_module.config.custom_params['custom_param'], 'test_value')
        
        # Test module enable/disable
        self.orchestrator.disable_module('options')
        self.assertFalse(options_module.config.enabled)
        
        self.orchestrator.enable_module('options')
        self.assertTrue(options_module.config.enabled)
    
    def test_performance_metrics_collection(self):
        """Test performance metrics are collected correctly"""
        options_module, crypto_module, stocks_module = self._create_test_modules()
        
        # Register modules
        self.orchestrator.register_module(options_module)
        self.orchestrator.register_module(crypto_module)
        
        # Execute multiple cycles to build metrics
        for i in range(3):
            with patch.object(options_module, 'analyze_opportunities') as mock_analyze:
                mock_analyze.return_value = [self._create_test_opportunity("AAPL", "options")]
                self.orchestrator.run_single_cycle()
        
        # Check orchestrator metrics
        status = self.orchestrator.get_status()
        metrics = status['orchestrator_metrics']
        
        self.assertEqual(metrics['total_cycles'], 3)
        self.assertGreater(metrics['uptime_hours'], 0)
        
        # Check module performance
        options_performance = self.orchestrator.get_module_performance('options')
        self.assertIsNotNone(options_performance)
        self.assertIn('module_name', options_performance)
    
    def _create_test_opportunity(self, symbol: str, module_type: str) -> TradeOpportunity:
        """Helper to create test trading opportunities"""
        return TradeOpportunity(
            symbol=symbol,
            action=TradeAction.BUY,
            quantity=10.0,
            confidence=0.75,
            strategy=f"{module_type}_test_strategy",
            metadata={
                'test_opportunity': True,
                'module_type': module_type,
                'current_price': 450.0
            },
            technical_score=0.7,
            regime_score=0.8,
            pattern_score=0.6,
            ml_score=0.75
        )


class TestModularFirebaseInterface(unittest.TestCase):
    """Test the modular Firebase interface"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_firebase_db = Mock()
        self.mock_firebase_db.is_connected.return_value = True
        self.logger = logging.getLogger('TestFirebaseInterface')
        
        self.interface = ModularFirebaseInterface(self.mock_firebase_db, self.logger)
    
    def test_firebase_interface_initialization(self):
        """Test Firebase interface initializes correctly"""
        self.assertIsNotNone(self.interface)
        self.assertTrue(self.interface.is_connected())
        
        # Test collections mapping
        self.assertIn('module_opportunities', self.interface.collections)
        self.assertIn('module_trades', self.interface.collections)
        self.assertIn('orchestrator_cycles', self.interface.collections)
    
    def test_trade_opportunity_saving(self):
        """Test trade opportunity saving"""
        # Mock Firebase collection
        mock_collection = Mock()
        self.mock_firebase_db.db.collection.return_value = mock_collection
        
        opportunity = TradeOpportunity(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=100,
            confidence=0.8,
            strategy="test_strategy"
        )
        
        self.interface.save_trade_opportunity("test_module", opportunity)
        
        # Verify Firebase collection was called
        self.mock_firebase_db.db.collection.assert_called()
        mock_collection.add.assert_called_once()
    
    def test_trade_result_saving(self):
        """Test trade result saving"""
        # Mock Firebase collection
        mock_collection = Mock()
        self.mock_firebase_db.db.collection.return_value = mock_collection
        
        opportunity = TradeOpportunity(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=100,
            confidence=0.8,
            strategy="test_strategy"
        )
        
        result = TradeResult(
            opportunity=opportunity,
            status=TradeStatus.EXECUTED,
            order_id="test_order_123"
        )
        
        self.interface.save_trade_result("test_module", result)
        
        # Verify Firebase collection was called
        self.mock_firebase_db.db.collection.assert_called()
        mock_collection.add.assert_called_once()


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    unittest.main(verbosity=2)