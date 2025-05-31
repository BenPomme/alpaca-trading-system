"""
Test Framework for Modular Architecture

This script provides basic testing and validation for the modular trading framework
components before extracting individual trading modules.
"""

import sys
import os
import logging
from typing import Dict, Any, List
from datetime import datetime
import traceback

# Add modular directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modular'))

from modular.base_module import (
    TradingModule, ModuleConfig, TradeOpportunity, TradeResult, 
    TradeAction, TradeStatus, ModuleRegistry, ModuleHealthStatus
)
from modular.orchestrator import ModularOrchestrator
from modular.firebase_interface import ModularFirebaseInterface


class MockTradingModule(TradingModule):
    """Mock trading module for testing framework components"""
    
    @property
    def module_name(self) -> str:
        return "mock_test_module"
    
    @property
    def supported_symbols(self) -> List[str]:
        return ["AAPL", "MSFT", "GOOGL", "TSLA"]
    
    def analyze_opportunities(self) -> List[TradeOpportunity]:
        """Generate mock opportunities for testing"""
        opportunities = []
        
        for symbol in ["AAPL", "MSFT"]:
            opp = TradeOpportunity(
                symbol=symbol,
                action=TradeAction.BUY,
                quantity=100,
                confidence=0.75,
                strategy="mock_momentum",
                metadata={"test": True},
                technical_score=0.8,
                regime_score=0.7,
                pattern_score=0.6,
                ml_score=0.75
            )
            opportunities.append(opp)
        
        return opportunities
    
    def execute_trades(self, opportunities: List[TradeOpportunity]) -> List[TradeResult]:
        """Mock trade execution"""
        results = []
        
        for opp in opportunities:
            result = TradeResult(
                opportunity=opp,
                status=TradeStatus.EXECUTED,
                order_id=f"mock_order_{datetime.now().timestamp()}",
                execution_price=150.0,
                execution_time=datetime.now()
            )
            results.append(result)
        
        return results
    
    def monitor_positions(self) -> List[TradeResult]:
        """Mock position monitoring"""
        return []  # No exits for this test


class MockFirebaseCollection:
    """Mock Firebase collection for testing"""
    
    def __init__(self):
        self.documents = []
    
    def add(self, data):
        self.documents.append(data)
        return data
    
    def where(self, field, op, value):
        return self
    
    def order_by(self, field, direction='ASCENDING'):
        return self
    
    def limit(self, count):
        return self
    
    def get(self):
        return []


class MockFirebaseDB:
    """Mock Firebase database for testing without real Firebase connection"""
    
    def __init__(self):
        self.data = {}
        self.connected = True
        self.collections = {}
        # Create a mock db object with collection method
        self.db = self
    
    def collection(self, name):
        if name not in self.collections:
            self.collections[name] = MockFirebaseCollection()
        return self.collections[name]
    
    def is_connected(self):
        return self.connected


class MockRiskManager:
    """Mock risk manager for testing"""
    
    def validate_opportunity(self, module_name: str, opportunity: TradeOpportunity) -> bool:
        return opportunity.confidence > 0.6
    
    def get_module_allocation(self, module_name: str) -> float:
        return 15.0  # 15% allocation


class MockOrderExecutor:
    """Mock order executor for testing"""
    
    def execute_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'success': True,
            'order_id': f"mock_{datetime.now().timestamp()}"
        }


def test_base_module_functionality():
    """Test base module class functionality"""
    print("🧪 Testing base module functionality...")
    
    try:
        # Create mock dependencies
        config = ModuleConfig(
            module_name="test_module",
            max_allocation_pct=20.0,
            min_confidence=0.6
        )
        
        firebase_db = MockFirebaseDB()
        firebase_interface = ModularFirebaseInterface(firebase_db)
        risk_manager = MockRiskManager()
        order_executor = MockOrderExecutor()
        
        # Create mock module
        module = MockTradingModule(
            config=config,
            firebase_db=firebase_interface,
            risk_manager=risk_manager,
            order_executor=order_executor
        )
        
        # Test opportunity analysis
        opportunities = module.analyze_opportunities()
        assert len(opportunities) == 2, f"Expected 2 opportunities, got {len(opportunities)}"
        assert opportunities[0].symbol == "AAPL"
        assert opportunities[0].confidence == 0.75
        
        # Test opportunity validation
        valid_opps = [opp for opp in opportunities if module.validate_opportunity(opp)]
        assert len(valid_opps) == 2, "All opportunities should be valid"
        
        # Test trade execution
        results = module.execute_trades(valid_opps)
        assert len(results) == 2, f"Expected 2 trade results, got {len(results)}"
        assert all(result.success for result in results), "All trades should be successful"
        
        # Test performance summary
        performance = module.get_performance_summary()
        assert performance['module_name'] == "mock_test_module"
        assert performance['active_positions'] == 0
        
        print("✅ Base module functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Base module test failed: {e}")
        traceback.print_exc()
        return False


def test_module_registry():
    """Test module registry functionality"""
    print("🧪 Testing module registry...")
    
    try:
        registry = ModuleRegistry()
        
        # Create mock module
        config = ModuleConfig(module_name="test_module")
        firebase_db = MockFirebaseDB()
        firebase_interface = ModularFirebaseInterface(firebase_db)
        
        module = MockTradingModule(
            config=config,
            firebase_db=firebase_interface,
            risk_manager=MockRiskManager(),
            order_executor=MockOrderExecutor()
        )
        
        # Test registration
        registry.register_module(module)
        assert len(registry._modules) == 1
        
        # Test retrieval
        retrieved = registry.get_module("mock_test_module")
        assert retrieved is not None
        assert retrieved.module_name == "mock_test_module"
        
        # Test active modules
        active = registry.get_active_modules()
        assert len(active) == 1
        
        # Test health updates
        registry.update_health("mock_test_module", ModuleHealthStatus.WARNING, "Test warning")
        health_summary = registry.get_health_summary()
        assert "mock_test_module" in health_summary
        assert health_summary["mock_test_module"]["status"] == "warning"
        
        print("✅ Module registry tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Module registry test failed: {e}")
        traceback.print_exc()
        return False


def test_orchestrator_functionality():
    """Test orchestrator basic functionality"""
    print("🧪 Testing orchestrator functionality...")
    
    try:
        # Create mock dependencies
        firebase_db = MockFirebaseDB()
        firebase_interface = ModularFirebaseInterface(firebase_db)
        risk_manager = MockRiskManager()
        order_executor = MockOrderExecutor()
        
        # Create orchestrator
        orchestrator = ModularOrchestrator(
            firebase_db=firebase_interface,
            risk_manager=risk_manager,
            order_executor=order_executor
        )
        
        # Create and register mock modules with unique names
        class MockModule1(MockTradingModule):
            @property
            def module_name(self):
                return "mock_module_1"
        
        class MockModule2(MockTradingModule):
            @property  
            def module_name(self):
                return "mock_module_2"
        
        for i, module_class in enumerate([MockModule1, MockModule2]):
            config = ModuleConfig(module_name=f"mock_module_{i+1}")
            module = module_class(
                config=config,
                firebase_db=firebase_interface,
                risk_manager=risk_manager,
                order_executor=order_executor
            )
            orchestrator.register_module(module)
        
        # Test single cycle
        results = orchestrator.run_single_cycle()
        
        assert results['success'], "Cycle should be successful"
        assert 'modules' in results
        assert len(results['modules']) == 2, "Should have results from 2 modules"
        
        # Test status
        status = orchestrator.get_status()
        assert status['total_modules'] == 2
        assert status['active_modules'] == 2
        
        print("✅ Orchestrator functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        traceback.print_exc()
        return False


def test_firebase_interface():
    """Test Firebase interface functionality"""
    print("🧪 Testing Firebase interface...")
    
    try:
        firebase_db = MockFirebaseDB()
        interface = ModularFirebaseInterface(firebase_db)
        
        # Test connection check
        assert interface.is_connected(), "Should be connected to mock DB"
        
        # Test opportunity saving
        opp = TradeOpportunity(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=100,
            confidence=0.8,
            strategy="test_strategy"
        )
        
        interface.save_trade_opportunity("test_module", opp)
        # Check that opportunity was saved to the mock collection
        opportunities_collection = firebase_db.collections.get('modular_opportunities')
        assert opportunities_collection is not None, "Opportunities collection should exist"
        assert len(opportunities_collection.documents) == 1, "Should have 1 opportunity saved"
        
        # Test trade result saving
        result = TradeResult(
            opportunity=opp,
            status=TradeStatus.EXECUTED,
            order_id="test_123"
        )
        
        interface.save_trade_result("test_module", result)
        trades_collection = firebase_db.collections.get('modular_trades')
        assert trades_collection is not None, "Trades collection should exist"
        assert len(trades_collection.documents) == 1, "Should have 1 trade saved"
        
        # Test event publishing
        interface.publish_event("test_event", {"test": "data"})
        events_collection = firebase_db.collections.get('modular_events')
        assert events_collection is not None, "Events collection should exist"
        assert len(events_collection.documents) == 1, "Should have 1 event saved"
        
        # Test parameter retrieval (returns empty dict from mock)
        params = interface.get_module_parameters("test_module")
        assert isinstance(params, dict), "Should return a dictionary"
        
        print("✅ Firebase interface tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Firebase interface test failed: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Run complete test suite for modular framework"""
    print("🚀 Starting Modular Framework Test Suite")
    print("=" * 50)
    
    tests = [
        test_base_module_functionality,
        test_module_registry,
        test_orchestrator_functionality,
        test_firebase_interface
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Modular framework is ready for module extraction.")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before proceeding.")
        return False


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test suite
    success = run_all_tests()
    
    if success:
        print("\n✅ Framework validation complete - ready for module extraction!")
        print("\nNext steps:")
        print("1. Extract options trading module")
        print("2. Extract crypto trading module") 
        print("3. Extract stocks trading module")
        print("4. Create integration tests")
        print("5. Performance comparison with legacy system")
    else:
        print("\n❌ Framework validation failed - please fix issues first")
        sys.exit(1)