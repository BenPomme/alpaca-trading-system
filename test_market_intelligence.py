#!/usr/bin/env python3
"""
Test Market Intelligence Module

Tests the OpenAI-powered market intelligence module to ensure proper
integration with the modular trading system.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_market_intelligence_module():
    """Test the Market Intelligence Module functionality"""
    logger.info("🧠 Testing Market Intelligence Module...")
    
    try:
        # Import required components
        from modular.market_intelligence_module import MarketIntelligenceModule, OpenAIAnalyzer
        from modular.base_module import ModuleConfig
        from firebase_database import FirebaseDatabase
        
        # Mock risk manager and order executor for testing
        class MockRiskManager:
            def get_portfolio_summary(self):
                return {
                    'portfolio_value': 100000,
                    'positions_count': 5,
                    'available_cash': 50000
                }
            
            def get_all_positions(self):
                return {
                    'SPY': {
                        'quantity': 100,
                        'market_value': 45000,
                        'unrealized_pnl': 1500,
                        'avg_entry_price': 430.0,
                        'current_price': 450.0
                    },
                    'BTCUSD': {
                        'quantity': 0.5,
                        'market_value': 25000,
                        'unrealized_pnl': -500,
                        'avg_entry_price': 51000,
                        'current_price': 50000
                    }
                }
        
        class MockOrderExecutor:
            def __init__(self):
                pass
        
        # Check for OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            logger.error("❌ OPENAI_API_KEY environment variable not set")
            logger.info("Set it with: export OPENAI_API_KEY='your_key_here'")
            return False
        
        # Initialize Firebase (optional)
        try:
            firebase_db = FirebaseDatabase()
            logger.info("✅ Firebase connection established" if firebase_db.is_connected() else "⚠️ Firebase not connected")
        except Exception as e:
            logger.warning(f"Firebase not available: {e}")
            firebase_db = None
        
        # Test OpenAI Analyzer first
        logger.info("🔍 Testing OpenAI Analyzer...")
        analyzer = OpenAIAnalyzer(openai_key, model="o4-mini", logger=logger)
        
        # Test market regime analysis
        test_market_data = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_value': 100000,
            'positions_count': 5,
            'volatility_index': 0.25
        }
        
        regime_analysis = await analyzer.analyze_market_regime(test_market_data)
        logger.info(f"📊 Market Regime Analysis: {regime_analysis.get('regime')} "
                   f"(confidence: {regime_analysis.get('confidence', 0):.1%})")
        
        # Test position risk analysis
        test_position = {
            'symbol': 'SPY',
            'quantity': 100,
            'market_value': 45000,
            'unrealized_pnl': 1500,
            'entry_price': 430.0,
            'current_price': 450.0
        }
        
        risk_analysis = await analyzer.analyze_position_risk(test_position)
        logger.info(f"⚠️ Position Risk for SPY: {risk_analysis.get('risk_score', 0):.1%} "
                   f"({risk_analysis.get('exit_urgency', 'unknown')} urgency)")
        
        # Test opportunity identification
        opportunities = await analyzer.identify_opportunities(
            {'regime': regime_analysis}, 
            [test_position]
        )
        logger.info(f"💡 Opportunities Identified: {len(opportunities)}")
        
        # Test full Market Intelligence Module
        logger.info("🎯 Testing full Market Intelligence Module...")
        
        config = ModuleConfig(
            module_name="market_intelligence",
            enabled=True,
            min_confidence=0.6
        )
        
        intelligence_module = MarketIntelligenceModule(
            config=config,
            firebase_db=firebase_db,
            risk_manager=MockRiskManager(),
            order_executor=MockOrderExecutor(),
            openai_api_key=openai_key,
            openai_model="o4-mini",  # Use latest reasoning model for testing
            logger=logger
        )
        
        # Run daily intelligence cycle
        intelligence_result = await intelligence_module.run_daily_intelligence_cycle()
        
        logger.info(f"📈 Intelligence Cycle Complete:")
        logger.info(f"   - Market Signals: {len(intelligence_result.market_signals)}")
        logger.info(f"   - Position Insights: {len(intelligence_result.position_insights)}")
        logger.info(f"   - Analysis Date: {intelligence_result.analysis_date}")
        
        # Test signal generation
        trade_opportunities = intelligence_module.analyze_opportunities()
        logger.info(f"🎲 Trade Opportunities Generated: {len(trade_opportunities)}")
        
        # Test position monitoring
        exit_signals = intelligence_module.monitor_positions()
        logger.info(f"🚪 Exit Signals: {len(exit_signals)}")
        
        # Test performance summary
        performance = intelligence_module.get_performance_summary()
        logger.info(f"📊 Performance Metrics: {performance['intelligence_metrics']}")
        
        logger.info("✅ Market Intelligence Module test completed successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("Make sure to install required packages: pip install openai")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


async def test_integration_with_orchestrator():
    """Test integration with ModularOrchestrator"""
    logger.info("🎼 Testing integration with ModularOrchestrator...")
    
    try:
        from modular.orchestrator import ModularOrchestrator
        from modular.market_intelligence_module import MarketIntelligenceModule
        from modular.base_module import ModuleConfig
        from firebase_database import FirebaseDatabase
        
        # Mock components
        class MockRiskManager:
            def get_module_allocation(self, module_name):
                return 10.0  # 10% allocation
            
            def validate_opportunity(self, module_name, opportunity):
                return True
        
        class MockOrderExecutor:
            def set_execution_mode(self, enabled, dry_run):
                pass
        
        # Check API key
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            logger.warning("⚠️ OPENAI_API_KEY not set, skipping integration test")
            return True
        
        # Initialize components
        firebase_db = FirebaseDatabase() if os.getenv('FIREBASE_SERVICE_ACCOUNT') else None
        
        orchestrator = ModularOrchestrator(
            firebase_db=firebase_db,
            risk_manager=MockRiskManager(),
            order_executor=MockOrderExecutor(),
            logger=logger
        )
        
        # Create and register intelligence module
        config = ModuleConfig(
            module_name="market_intelligence",
            enabled=True,
            min_confidence=0.6
        )
        
        intelligence_module = MarketIntelligenceModule(
            config=config,
            firebase_db=firebase_db,
            risk_manager=orchestrator.risk_manager,
            order_executor=orchestrator.order_executor,
            openai_api_key=openai_key,
            openai_model="o4-mini",
            logger=logger
        )
        
        orchestrator.register_module(intelligence_module)
        
        # Test single cycle
        results = orchestrator.run_single_cycle()
        
        logger.info(f"🔄 Orchestrator Cycle Results:")
        logger.info(f"   - Success: {results.get('success', False)}")
        logger.info(f"   - Modules: {list(results.get('modules', {}).keys())}")
        logger.info(f"   - Summary: {results.get('summary', {})}")
        
        # Test status
        status = orchestrator.get_status()
        logger.info(f"📊 Orchestrator Status: {status['active_modules']} active modules")
        
        logger.info("✅ Orchestrator integration test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False


def main():
    """Run all Market Intelligence tests"""
    logger.info("🧪 Starting Market Intelligence Module Tests")
    
    async def run_tests():
        # Test 1: Core functionality
        test1_success = await test_market_intelligence_module()
        
        # Test 2: Integration
        test2_success = await test_integration_with_orchestrator()
        
        # Summary
        if test1_success and test2_success:
            logger.info("🎉 All Market Intelligence tests passed!")
            logger.info("Ready for production deployment!")
        else:
            logger.error("❌ Some tests failed. Check logs above.")
            
        return test1_success and test2_success
    
    # Run async tests
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()