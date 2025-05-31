#!/usr/bin/env python3
"""
ML Parameter Optimization Demo

Demonstrates the complete ML parameter optimization pipeline including:
- Real-time parameter adjustment based on trading performance
- Bayesian optimization for continuous parameters
- Performance-based analysis for discrete parameters
- Integration with the modular trading orchestrator
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# Import modular components
from modular.orchestrator import ModularOrchestrator
from modular.firebase_interface import ModularFirebaseInterface
from modular.ml_optimizer import MLParameterOptimizationEngine
from modular.options_module import OptionsModule
from modular.crypto_module import CryptoModule
from modular.stocks_module import StocksModule
from modular.base_module import ModuleConfig


class MockApiClient:
    """Mock API client for demonstration"""
    
    def __init__(self):
        self.account_value = 100000
        self.positions = []
    
    def get_account(self):
        class MockAccount:
            portfolio_value = 100000
            regt_buying_power = 50000
        return MockAccount()
    
    def list_positions(self):
        return self.positions
    
    def get_clock(self):
        class MockClock:
            is_open = True
        return MockClock()
    
    def get_latest_quote(self, symbol):
        class MockQuote:
            ask_price = 450.0
            bid_price = 449.0
            close = 449.50
        return MockQuote()


class MockRiskManager:
    """Mock risk manager for demonstration"""
    
    def validate_opportunity(self, opportunity):
        return True
    
    def get_module_allocation(self, module_name):
        return 0.1  # 10% allocation


class MockOrderExecutor:
    """Mock order executor for demonstration"""
    
    def execute_order(self, order_data):
        return {
            'success': True,
            'order_id': f"demo_order_{int(time.time())}"
        }


class MockFirebaseDB:
    """Mock Firebase database for demonstration"""
    
    def __init__(self):
        self.ml_data = []
        self.parameter_data = []
        self.optimization_data = []
        self.connected = True
    
    def is_connected(self):
        return self.connected
    
    def save_trade(self, trade_data):
        self.ml_data.append(trade_data)
        return f"trade_{len(self.ml_data)}"
    
    def save_parameter_effectiveness(self, param_data):
        self.parameter_data.append(param_data)
        return f"param_{len(self.parameter_data)}"
    
    def save_ml_learning_event(self, event_data):
        return f"event_{int(time.time())}"
    
    def get_ml_optimization_data(self, module_name=None):
        # Generate mock historical performance data for optimization
        mock_data = []
        base_time = datetime.now() - timedelta(days=7)
        
        for i in range(50):  # 50 data points over 7 days
            timestamp = base_time + timedelta(hours=i * 3)
            
            # Simulate parameter variations and performance
            confidence_threshold = 0.5 + (i % 10) * 0.03
            position_multiplier = 1.0 + (i % 8) * 0.2
            
            # Simulate better performance with higher confidence
            profit_loss = -10 + (confidence_threshold - 0.5) * 50 + (i % 3 - 1) * 5
            
            mock_data.append({
                'module_name': module_name or 'demo',
                'confidence_threshold': confidence_threshold,
                'position_multiplier': position_multiplier,
                'profit_loss': profit_loss,
                'success': profit_loss > 0,
                'timestamp': timestamp.isoformat()
            })
        
        return mock_data
    
    def get_module_parameters(self, module_name):
        # Return current parameter values
        return {
            'confidence_threshold': 0.65,
            'position_multiplier': 1.5,
            'leverage_factor': 2.0
        }
    
    def save_ml_optimization_data(self, module_name, optimization_data):
        self.optimization_data.append(optimization_data)
        return f"opt_{len(self.optimization_data)}"
    
    def save_orchestrator_cycle(self, cycle_data):
        pass


def setup_logging():
    """Setup logging for the demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('MLOptimizationDemo')


def create_demo_modules(firebase_interface, api_client, risk_manager, order_executor, logger):
    """Create trading modules for demonstration"""
    
    # Options module configuration
    options_config = ModuleConfig(
        module_name="options",
        enabled=True,
        max_allocation_pct=30.0,
        min_confidence=0.60,
        custom_params={
            'max_allocation_pct': 30.0,
            'leverage_target': 2.5,
            'contracts_multiplier': 1.0
        }
    )
    
    # Crypto module configuration
    crypto_config = ModuleConfig(
        module_name="crypto",
        enabled=True,
        max_allocation_pct=20.0,
        min_confidence=0.45,
        custom_params={
            'max_allocation_pct': 20.0,
            'leverage_multiplier': 1.5,
            'session_multiplier': 1.2
        }
    )
    
    # Stocks module configuration
    stocks_config = ModuleConfig(
        module_name="stocks",
        enabled=True,
        max_allocation_pct=50.0,
        min_confidence=0.55,
        custom_params={
            'market_tier': 2,
            'aggressive_multiplier': 2.0
        }
    )
    
    # Create modules
    options_module = OptionsModule(
        config=options_config,
        firebase_db=firebase_interface,
        risk_manager=risk_manager,
        order_executor=order_executor,
        api_client=api_client,
        logger=logger
    )
    
    crypto_module = CryptoModule(
        config=crypto_config,
        firebase_db=firebase_interface,
        risk_manager=risk_manager,
        order_executor=order_executor,
        api_client=api_client,
        logger=logger
    )
    
    stocks_module = StocksModule(
        config=stocks_config,
        firebase_db=firebase_interface,
        risk_manager=risk_manager,
        order_executor=order_executor,
        api_client=api_client,
        logger=logger
    )
    
    return options_module, crypto_module, stocks_module


def demonstrate_ml_optimization():
    """Demonstrate ML parameter optimization in action"""
    
    logger = setup_logging()
    logger.info("🧠 Starting ML Parameter Optimization Demo")
    
    # Create mock dependencies
    mock_firebase_db = MockFirebaseDB()
    firebase_interface = ModularFirebaseInterface(mock_firebase_db, logger)
    api_client = MockApiClient()
    risk_manager = MockRiskManager()
    order_executor = MockOrderExecutor()
    
    # Create orchestrator with ML optimization
    logger.info("🚀 Creating modular orchestrator with ML optimization")
    orchestrator = ModularOrchestrator(
        firebase_db=firebase_interface,
        risk_manager=risk_manager,
        order_executor=order_executor,
        logger=logger
    )
    
    # Verify ML optimizer was created
    if orchestrator.ml_optimizer:
        logger.info("✅ ML Parameter Optimization Engine created successfully")
    else:
        logger.error("❌ Failed to create ML optimization engine")
        return
    
    # Create and register trading modules
    logger.info("📊 Creating and registering trading modules")
    options_module, crypto_module, stocks_module = create_demo_modules(
        firebase_interface, api_client, risk_manager, order_executor, logger
    )
    
    orchestrator.register_module(options_module)
    orchestrator.register_module(crypto_module)
    orchestrator.register_module(stocks_module)
    
    logger.info(f"📈 Registered {len(orchestrator.registry.get_active_modules())} trading modules")
    
    # Demonstrate ML optimization analysis
    logger.info("\n🔍 ANALYZING PARAMETER OPTIMIZATION OPPORTUNITIES")
    
    ml_engine = orchestrator.ml_optimizer
    
    for module in orchestrator.registry.get_active_modules():
        module_name = module.module_name
        logger.info(f"\n📊 Module: {module_name.upper()}")
        
        # Check if optimization is needed
        should_optimize = ml_engine.parameter_optimizer.should_optimize_parameters(module_name)
        logger.info(f"   Optimization needed: {'✅ YES' if should_optimize else '❌ NO'}")
        
        if should_optimize:
            # Show current parameters
            current_params = ml_engine.parameter_optimizer._get_current_module_parameters(module_name)
            logger.info(f"   Current parameters: {current_params}")
            
            # Get recent performance data
            performance_data = ml_engine.parameter_optimizer._get_recent_performance_data(module_name)
            logger.info(f"   Performance data points: {len(performance_data)}")
            
            if len(performance_data) > 0:
                avg_performance = sum(d.get('profit_loss', 0) for d in performance_data) / len(performance_data)
                win_rate = sum(1 for d in performance_data if d.get('profit_loss', 0) > 0) / len(performance_data)
                logger.info(f"   Average P&L: ${avg_performance:.2f}")
                logger.info(f"   Win rate: {win_rate:.1%}")
    
    # Run optimization cycle
    logger.info("\n🧠 RUNNING ML PARAMETER OPTIMIZATION CYCLE")
    optimization_summary = ml_engine.run_optimization_cycle()
    
    logger.info("📈 Optimization Results:")
    logger.info(f"   Modules analyzed: {optimization_summary['modules_analyzed']}")
    logger.info(f"   Parameters optimized: {optimization_summary['parameters_optimized']}")
    logger.info(f"   Optimizations applied: {optimization_summary['optimizations_applied']}")
    logger.info(f"   Expected improvement: {optimization_summary['total_expected_improvement']:.1%}")
    
    # Show optimization status
    logger.info("\n⚙️ ML OPTIMIZATION ENGINE STATUS")
    status = ml_engine.get_optimization_status()
    for key, value in status.items():
        logger.info(f"   {key}: {value}")
    
    # Demonstrate parameter updates
    logger.info("\n🔧 DEMONSTRATING MANUAL PARAMETER UPDATES")
    
    # Show how parameters can be updated through orchestrator
    logger.info("   Updating crypto module session_multiplier...")
    orchestrator.update_module_config('crypto', {'session_multiplier': 1.8})
    
    logger.info("   Updating options module confidence threshold...")
    orchestrator.update_module_config('options', {'min_confidence': 0.7})
    
    logger.info("   Updating stocks module aggressive multiplier...")
    orchestrator.update_module_config('stocks', {'aggressive_multiplier': 2.5})
    
    # Show final module configurations
    logger.info("\n📋 FINAL MODULE CONFIGURATIONS")
    for module in orchestrator.registry.get_active_modules():
        logger.info(f"\n   {module.module_name.upper()} Module:")
        logger.info(f"     Enabled: {module.config.enabled}")
        logger.info(f"     Min confidence: {module.config.min_confidence}")
        logger.info(f"     Max allocation: {module.config.max_allocation_pct}%")
        logger.info(f"     Custom params: {module.config.custom_params}")
    
    # Demonstrate optimization data storage
    logger.info(f"\n💾 DATA STORAGE SUMMARY")
    logger.info(f"   ML trade data points: {len(mock_firebase_db.ml_data)}")
    logger.info(f"   Parameter effectiveness records: {len(mock_firebase_db.parameter_data)}")
    logger.info(f"   Optimization results: {len(mock_firebase_db.optimization_data)}")
    
    logger.info("\n✅ ML Parameter Optimization Demo Complete!")
    logger.info("\n🎯 KEY ACHIEVEMENTS:")
    logger.info("   ✅ Real-time parameter optimization based on trading performance")
    logger.info("   ✅ Bayesian optimization for continuous parameters")
    logger.info("   ✅ Performance analysis for discrete parameters")
    logger.info("   ✅ Integration with modular trading orchestrator")
    logger.info("   ✅ Comprehensive ML data collection and storage")
    logger.info("   ✅ Automated parameter adjustment with confidence thresholds")


if __name__ == '__main__':
    demonstrate_ml_optimization()