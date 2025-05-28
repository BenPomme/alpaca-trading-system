#!/usr/bin/env python3
"""
Comprehensive Phase 1 Testing
Test all Phase 1 components working together
"""

import os
import sys
import time
from datetime import datetime
from test_system import TradingSystemTester
from enhanced_trader_v2 import EnhancedTraderV2
from performance_tracker import PerformanceTracker

class Phase1Tester:
    """Comprehensive Phase 1 testing framework"""
    
    def __init__(self):
        self.tester = TradingSystemTester()
        self.results = []
        print("🧪 PHASE 1 COMPREHENSIVE TESTING")
        print("=" * 50)
    
    def test_component(self, name, test_func):
        """Test individual component with error handling"""
        try:
            print(f"\n🔍 Testing {name}...")
            start_time = time.time()
            
            result = test_func()
            
            duration = time.time() - start_time
            status = "PASS" if result else "FAIL"
            
            self.tester.log_test(name, status, f"Duration: {duration:.2f}s")
            self.results.append({'name': name, 'status': status, 'duration': duration})
            
            return result
            
        except Exception as e:
            self.tester.log_test(name, "FAIL", f"Exception: {e}")
            self.results.append({'name': name, 'status': 'FAIL', 'error': str(e)})
            return False
    
    def test_database_integration(self):
        """Test database functionality"""
        try:
            from database_manager import TradingDatabase
            
            # Test database creation and operations
            db = TradingDatabase('data/test_phase1.db')
            
            # Test data storage
            db.store_market_quote('AAPL', 200.00, 200.05)
            cycle_id = db.store_trading_cycle({'regime': 'active', 'strategy': 'momentum'}, 1)
            trade_id = db.store_virtual_trade('AAPL', 'buy', 200.02, 'momentum', 'active', 0.8, cycle_id)
            
            # Test data retrieval
            quotes = db.get_recent_quotes('AAPL', 5)
            cycles = db.get_recent_cycles(5)
            trades = db.get_virtual_trades(limit=5)
            
            # Cleanup
            if os.path.exists('data/test_phase1.db'):
                os.remove('data/test_phase1.db')
            
            return len(quotes) > 0 and len(cycles) > 0 and len(trades) > 0
            
        except Exception as e:
            print(f"Database test error: {e}")
            return False
    
    def test_market_universe(self):
        """Test expanded market universe"""
        try:
            from market_universe import get_symbols_by_tier, validate_symbol_availability
            from enhanced_trader import EnhancedTrader
            
            # Test tier access
            tier1 = get_symbols_by_tier(1)
            tier2 = get_symbols_by_tier(2)
            
            # Test symbol validation
            trader = EnhancedTrader(use_database=False)
            validation = validate_symbol_availability(trader.api, tier1, max_test=3)
            
            return (len(tier1) >= 3 and len(tier2) > len(tier1) and 
                   validation['success_rate'] > 0.5)
            
        except Exception as e:
            print(f"Market universe test error: {e}")
            return False
    
    def test_enhanced_trader_v2(self):
        """Test enhanced trader v2 functionality"""
        try:
            trader = EnhancedTraderV2(use_database=True, market_tier=1)
            
            # Test single cycle
            cycle_data = trader.enhanced_run_cycle_v2()
            
            # Verify cycle data structure
            required_fields = ['regime', 'strategy', 'confidence', 'quotes_count', 'enhanced_v2']
            has_required = all(field in cycle_data for field in required_fields)
            
            return has_required and cycle_data.get('enhanced_v2', False)
            
        except Exception as e:
            print(f"Enhanced trader v2 test error: {e}")
            return False
    
    def test_performance_tracking(self):
        """Test performance tracking system"""
        try:
            tracker = PerformanceTracker()
            
            # Generate performance report
            report = tracker.generate_performance_report()
            
            # Check report structure
            required_sections = ['detailed_performance', 'strategy_comparison', 'regime_analysis', 'system_health_score']
            has_sections = all(section in report for section in required_sections)
            
            # Check health score
            health = report.get('system_health_score', {})
            has_health = 'score' in health and 'level' in health
            
            return has_sections and has_health
            
        except Exception as e:
            print(f"Performance tracking test error: {e}")
            return False
    
    def test_integration_workflow(self):
        """Test complete integration workflow"""
        try:
            print("   📊 Running integration workflow...")
            
            # Initialize enhanced trader
            trader = EnhancedTraderV2(use_database=True, market_tier=1)
            
            # Run multiple cycles
            for i in range(2):
                print(f"   🔄 Integration cycle {i+1}/2...")
                cycle_data = trader.enhanced_run_cycle_v2()
                time.sleep(1)  # Brief pause between cycles
            
            # Test performance analysis
            tracker = PerformanceTracker()
            report = tracker.generate_performance_report()
            
            # Verify integration
            has_trades = report.get('detailed_performance', {}).get('total_trades', 0) > 0
            has_cycles = report.get('regime_analysis', {}).get('total_cycles_analyzed', 0) > 0
            
            return has_trades and has_cycles
            
        except Exception as e:
            print(f"Integration workflow test error: {e}")
            return False
    
    def test_rollback_capability(self):
        """Test system rollback capability"""
        try:
            # Test file backup
            test_file = 'data/test_rollback.txt'
            with open(test_file, 'w') as f:
                f.write('original content')
            
            backup_path = self.tester.backup_file(test_file)
            
            # Modify file
            with open(test_file, 'w') as f:
                f.write('modified content')
            
            # Test rollback
            if backup_path and os.path.exists(backup_path):
                os.system(f"cp {backup_path} {test_file}")
                
                with open(test_file, 'r') as f:
                    content = f.read()
                
                # Cleanup
                os.remove(test_file)
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                
                return content == 'original content'
            
            return False
            
        except Exception as e:
            print(f"Rollback test error: {e}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all Phase 1 tests"""
        print("🚀 Starting comprehensive Phase 1 testing...")
        print()
        
        # Core component tests
        tests = [
            ("Database Integration", self.test_database_integration),
            ("Market Universe", self.test_market_universe),
            ("Enhanced Trader V2", self.test_enhanced_trader_v2),
            ("Performance Tracking", self.test_performance_tracking),
            ("Integration Workflow", self.test_integration_workflow),
            ("Rollback Capability", self.test_rollback_capability)
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            success = self.test_component(test_name, test_func)
            if not success:
                print(f"⚠️ {test_name} failed - reviewing...")
        
        # Generate comprehensive report
        return self.generate_phase1_report()
    
    def generate_phase1_report(self):
        """Generate comprehensive Phase 1 test report"""
        print("\n" + "=" * 60)
        print("📊 PHASE 1 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['status'] == 'PASS')
        failed_tests = total_tests - passed_tests
        
        print(f"📈 Test Summary:")
        print(f"   ✅ Passed: {passed_tests}/{total_tests}")
        print(f"   ❌ Failed: {failed_tests}/{total_tests}")
        print(f"   📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for result in self.results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            duration = result.get('duration', 0)
            print(f"   {status_icon} {result['name']}: {result['status']} ({duration:.2f}s)")
            if 'error' in result:
                print(f"      Error: {result['error']}")
        
        # Phase 1 readiness assessment
        print(f"\n🎯 Phase 1 Readiness Assessment:")
        if failed_tests == 0:
            readiness = "✅ READY FOR DEPLOYMENT"
            recommendations = [
                "All Phase 1 components tested successfully",
                "System ready for Railway deployment",
                "Can proceed to Phase 2 development"
            ]
        elif failed_tests <= 2:
            readiness = "⚠️ MOSTLY READY (minor issues)"
            recommendations = [
                "Address failed tests before deployment",
                "Consider partial deployment of working components",
                "Review failed components individually"
            ]
        else:
            readiness = "❌ NOT READY (major issues)"
            recommendations = [
                "Fix critical failures before proceeding",
                "Review system architecture",
                "Consider rollback to stable version"
            ]
        
        print(f"   Status: {readiness}")
        print(f"   Recommendations:")
        for rec in recommendations:
            print(f"   • {rec}")
        
        # Deployment readiness
        print(f"\n🚀 Deployment Checklist:")
        deployment_items = [
            ("Database layer", passed_tests > 0),
            ("Market data collection", any(r['name'] == 'Market Universe' and r['status'] == 'PASS' for r in self.results)),
            ("Enhanced trading logic", any(r['name'] == 'Enhanced Trader V2' and r['status'] == 'PASS' for r in self.results)),
            ("Performance tracking", any(r['name'] == 'Performance Tracking' and r['status'] == 'PASS' for r in self.results)),
            ("Integration testing", any(r['name'] == 'Integration Workflow' and r['status'] == 'PASS' for r in self.results)),
            ("Rollback capability", any(r['name'] == 'Rollback Capability' and r['status'] == 'PASS' for r in self.results))
        ]
        
        for item, status in deployment_items:
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {item}")
        
        deployment_ready = all(status for _, status in deployment_items)
        
        print(f"\n{'🎉' if deployment_ready else '⚠️'} PHASE 1 DEPLOYMENT: {'READY' if deployment_ready else 'NEEDS ATTENTION'}")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'deployment_ready': deployment_ready,
            'readiness_status': readiness,
            'recommendations': recommendations,
            'test_results': self.results
        }

def main():
    """Run comprehensive Phase 1 testing"""
    # Set environment variables
    os.environ['ALPACA_PAPER_API_KEY'] = os.environ.get('ALPACA_PAPER_API_KEY', 'PKOBXG3RWCRQTXH6ID0L')
    os.environ['ALPACA_PAPER_SECRET_KEY'] = os.environ.get('ALPACA_PAPER_SECRET_KEY', '8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn')
    
    # Run comprehensive tests
    phase1_tester = Phase1Tester()
    report = phase1_tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    if report['deployment_ready']:
        print("\n🚀 Phase 1 ready for deployment!")
        sys.exit(0)
    else:
        print("\n⚠️ Phase 1 needs attention before deployment")
        sys.exit(1)

if __name__ == "__main__":
    main()