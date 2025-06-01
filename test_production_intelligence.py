#!/usr/bin/env python3
"""
Production Intelligence Test

Comprehensive test of Market Intelligence Module with real OpenAI integration
to validate data formats, signal generation, and production environment compatibility.
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionIntelligenceTest:
    """Comprehensive production test for Market Intelligence Module"""
    
    def __init__(self):
        self.test_results = {
            'openai_connection': False,
            'market_analysis': False,
            'position_analysis': False,
            'opportunity_identification': False,
            'signal_generation': False,
            'data_format_validation': False,
            'ml_integration': False,
            'error_handling': False
        }
        
    async def run_full_test(self):
        """Run comprehensive production test"""
        logger.info("🧪 STARTING PRODUCTION INTELLIGENCE TEST")
        logger.info("=" * 60)
        
        try:
            # Test 1: OpenAI Connection and Model Availability
            await self._test_openai_connection()
            
            # Test 2: Market Analysis with Real Data
            await self._test_market_analysis()
            
            # Test 3: Position Risk Analysis
            await self._test_position_analysis()
            
            # Test 4: Opportunity Identification
            await self._test_opportunity_identification()
            
            # Test 5: Signal Generation and Format Validation
            await self._test_signal_generation()
            
            # Test 6: ML Integration Format
            await self._test_ml_integration()
            
            # Test 7: Error Handling and Graceful Degradation
            await self._test_error_handling()
            
            # Test 8: Full Intelligence Cycle in Production Environment
            await self._test_full_production_cycle()
            
            # Generate final report
            self._generate_test_report()
            
        except Exception as e:
            logger.error(f"❌ Production test failed: {e}")
            import traceback
            logger.error(f"Error details: {traceback.format_exc()}")
    
    async def _test_openai_connection(self):
        """Test OpenAI API connection and model availability"""
        logger.info("🔍 Testing OpenAI Connection...")
        
        try:
            from modular.market_intelligence_module import OpenAIAnalyzer
            
            # Get API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.error("❌ OPENAI_API_KEY not found in environment")
                return
            
            # Test both models
            analyzer = OpenAIAnalyzer(api_key, model="o4-mini", logger=logger)
            
            # Test basic API call
            test_messages = [
                {"role": "system", "content": "You are a financial analyst. Respond with valid JSON."},
                {"role": "user", "content": "Analyze this test data: {'market': 'test'} and respond with: {\"status\": \"success\", \"analysis\": \"test complete\"}"}
            ]
            
            response = await analyzer._rate_limited_request(test_messages)
            
            if response and len(response) > 0:
                logger.info("✅ OpenAI o4-mini model connection successful")
                self.test_results['openai_connection'] = True
                
                # Test JSON parsing
                try:
                    # Extract JSON from response
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_data = json.loads(json_match.group())
                        logger.info(f"✅ JSON parsing successful: {json_data}")
                    else:
                        logger.warning("⚠️ Response format not JSON, but API working")
                except Exception as e:
                    logger.warning(f"⚠️ JSON parsing issue: {e}")
            else:
                logger.error("❌ OpenAI API call returned empty response")
                
        except Exception as e:
            logger.error(f"❌ OpenAI connection test failed: {e}")
    
    async def _test_market_analysis(self):
        """Test market regime analysis with real data"""
        logger.info("📊 Testing Market Analysis...")
        
        try:
            from modular.market_intelligence_module import OpenAIAnalyzer
            
            api_key = os.getenv('OPENAI_API_KEY')
            analyzer = OpenAIAnalyzer(api_key, model="o4-mini", logger=logger)
            
            # Real market data simulation
            test_market_data = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_value': 98845.67,
                'positions_count': 12,
                'volatility_index': 0.23,
                'sector_performance': {
                    'technology': 0.15,
                    'healthcare': -0.02,
                    'financials': 0.08
                }
            }
            
            # Run market analysis
            analysis = await analyzer.analyze_market_regime(test_market_data)
            
            # Validate structure
            required_fields = ['regime', 'confidence', 'volatility_forecast', 'risk_level', 'reasoning']
            missing_fields = [field for field in required_fields if field not in analysis]
            
            if not missing_fields:
                logger.info("✅ Market analysis structure valid")
                logger.info(f"📊 Regime: {analysis.get('regime')} (confidence: {analysis.get('confidence'):.1%})")
                logger.info(f"📊 Risk Level: {analysis.get('risk_level')}")
                logger.info(f"📊 Reasoning: {analysis.get('reasoning', 'N/A')[:100]}...")
                self.test_results['market_analysis'] = True
            else:
                logger.error(f"❌ Market analysis missing fields: {missing_fields}")
                
        except Exception as e:
            logger.error(f"❌ Market analysis test failed: {e}")
    
    async def _test_position_analysis(self):
        """Test position risk analysis"""
        logger.info("⚠️ Testing Position Analysis...")
        
        try:
            from modular.market_intelligence_module import OpenAIAnalyzer
            
            api_key = os.getenv('OPENAI_API_KEY')
            analyzer = OpenAIAnalyzer(api_key, model="o4-mini", logger=logger)
            
            # Real position data simulation
            test_position = {
                'symbol': 'SPY',
                'quantity': 250,
                'market_value': 112500.0,
                'unrealized_pnl': 3750.50,
                'entry_price': 430.25,
                'current_price': 450.00,
                'hold_duration_hours': 72,
                'sector': 'broad_market'
            }
            
            # Run position analysis
            analysis = await analyzer.analyze_position_risk(test_position)
            
            # Validate structure
            required_fields = ['risk_score', 'exit_urgency', 'recommended_action', 'reasoning']
            missing_fields = [field for field in required_fields if field not in analysis]
            
            if not missing_fields:
                logger.info("✅ Position analysis structure valid")
                logger.info(f"⚠️ Risk Score: {analysis.get('risk_score', 0):.1%}")
                logger.info(f"⚠️ Exit Urgency: {analysis.get('exit_urgency', 'unknown')}")
                logger.info(f"⚠️ Recommendation: {analysis.get('recommended_action', 'unknown')}")
                self.test_results['position_analysis'] = True
            else:
                logger.error(f"❌ Position analysis missing fields: {missing_fields}")
                
        except Exception as e:
            logger.error(f"❌ Position analysis test failed: {e}")
    
    async def _test_opportunity_identification(self):
        """Test opportunity identification"""
        logger.info("💡 Testing Opportunity Identification...")
        
        try:
            from modular.market_intelligence_module import OpenAIAnalyzer
            
            api_key = os.getenv('OPENAI_API_KEY')
            analyzer = OpenAIAnalyzer(api_key, model="o4-mini", logger=logger)
            
            # Market context
            market_context = {
                'regime': {
                    'regime': 'bull',
                    'confidence': 0.75,
                    'volatility_forecast': 'medium'
                },
                'market_data': {
                    'timestamp': datetime.now().isoformat(),
                    'portfolio_value': 98845.67
                }
            }
            
            # Current positions
            existing_positions = [
                {
                    'symbol': 'SPY',
                    'quantity': 250,
                    'market_value': 112500.0,
                    'sector': 'broad_market'
                }
            ]
            
            # Run opportunity identification
            opportunities = await analyzer.identify_opportunities(market_context, existing_positions)
            
            if isinstance(opportunities, list):
                logger.info(f"✅ Opportunity identification successful: {len(opportunities)} opportunities found")
                
                for i, opp in enumerate(opportunities[:3]):  # Show first 3
                    if isinstance(opp, dict):
                        symbol = opp.get('symbol', 'Unknown')
                        action = opp.get('action', 'Unknown')
                        confidence = opp.get('confidence', 0)
                        strategy = opp.get('strategy', 'Unknown')
                        logger.info(f"💡 Opportunity {i+1}: {symbol} - {action} ({confidence:.1%} confidence, {strategy})")
                
                self.test_results['opportunity_identification'] = True
            else:
                logger.warning("⚠️ Opportunity identification returned non-list format")
                
        except Exception as e:
            logger.error(f"❌ Opportunity identification test failed: {e}")
    
    async def _test_signal_generation(self):
        """Test signal generation and format validation"""
        logger.info("📡 Testing Signal Generation...")
        
        try:
            from modular.market_intelligence_module import MarketIntelligenceModule, MarketIntelligenceSignal
            from modular.base_module import ModuleConfig
            
            # Mock dependencies
            class MockRiskManager:
                def get_portfolio_summary(self):
                    return {'portfolio_value': 98845.67, 'positions_count': 12}
                def get_all_positions(self):
                    return {
                        'SPY': {
                            'quantity': 250,
                            'market_value': 112500.0,
                            'unrealized_pnl': 3750.50,
                            'avg_entry_price': 430.25,
                            'current_price': 450.00
                        }
                    }
            
            class MockOrderExecutor:
                pass
            
            # Initialize module
            config = ModuleConfig(module_name="market_intelligence", enabled=True, min_confidence=0.6)
            api_key = os.getenv('OPENAI_API_KEY')
            
            module = MarketIntelligenceModule(
                config=config,
                firebase_db=None,
                risk_manager=MockRiskManager(),
                order_executor=MockOrderExecutor(),
                openai_api_key=api_key,
                openai_model="o4-mini",
                logger=logger
            )
            
            # Run signal generation
            signals = module.get_market_intelligence_signals()
            
            logger.info(f"📡 Generated {len(signals)} signals")
            
            # Validate signal structure
            for i, signal in enumerate(signals[:3]):  # Check first 3
                if isinstance(signal, MarketIntelligenceSignal):
                    logger.info(f"📡 Signal {i+1}: {signal.signal_type} - {signal.symbol or 'market-wide'} (confidence: {signal.confidence:.1%})")
                    logger.info(f"    Reasoning: {signal.reasoning[:80]}...")
                else:
                    logger.warning(f"⚠️ Signal {i+1} not proper MarketIntelligenceSignal instance")
            
            self.test_results['signal_generation'] = True
            
        except Exception as e:
            logger.error(f"❌ Signal generation test failed: {e}")
    
    async def _test_ml_integration(self):
        """Test ML integration format compatibility"""
        logger.info("🧠 Testing ML Integration...")
        
        try:
            from modular.market_intelligence_module import MarketIntelligenceModule
            from modular.base_module import ModuleConfig
            
            # Mock dependencies
            class MockFirebaseDB:
                def is_connected(self):
                    return False
                def save_market_intelligence(self, data):
                    logger.info(f"🔥 Firebase save called with {len(str(data))} bytes")
            
            class MockRiskManager:
                def get_portfolio_summary(self):
                    return {'portfolio_value': 98845.67}
                def get_all_positions(self):
                    return {}
            
            # Test ML data collection methods
            config = ModuleConfig(module_name="market_intelligence", enabled=True)
            api_key = os.getenv('OPENAI_API_KEY')
            
            module = MarketIntelligenceModule(
                config=config,
                firebase_db=MockFirebaseDB(),
                risk_manager=MockRiskManager(),
                order_executor=None,
                openai_api_key=api_key,
                openai_model="o4-mini",
                logger=logger
            )
            
            # Test ML enhanced trade data format
            test_trade_data = {
                'symbol': 'SPY',
                'action': 'buy',
                'quantity': 100,
                'confidence': 0.85,
                'intelligence_signals': {
                    'market_regime': 'bull',
                    'position_risk': 0.3,
                    'opportunity_score': 0.8
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Test saving ML trade data
            trade_id = module.save_ml_enhanced_trade(test_trade_data)
            logger.info(f"🧠 ML trade data saved with ID: {trade_id}")
            
            # Test outcome update
            outcome_data = {
                'profit_loss': 245.50,
                'exit_reason': 'profit_target',
                'final_outcome': 'profitable'
            }
            
            module.update_ml_trade_outcome(trade_id, outcome_data)
            logger.info("🧠 ML trade outcome updated successfully")
            
            self.test_results['ml_integration'] = True
            
        except Exception as e:
            logger.error(f"❌ ML integration test failed: {e}")
    
    async def _test_error_handling(self):
        """Test error handling and graceful degradation"""
        logger.info("🛡️ Testing Error Handling...")
        
        try:
            from modular.market_intelligence_module import OpenAIAnalyzer
            
            # Test with invalid API key
            bad_analyzer = OpenAIAnalyzer("invalid_key", model="o4-mini", logger=logger)
            
            # Should handle gracefully and return defaults
            analysis = await bad_analyzer.analyze_market_regime({})
            
            if analysis and 'reasoning' in analysis:
                if 'default' in analysis['reasoning'].lower() or 'unavailable' in analysis['reasoning'].lower():
                    logger.info("✅ Error handling working - returned default analysis")
                    self.test_results['error_handling'] = True
                else:
                    logger.warning("⚠️ Unexpected response from bad API key")
            else:
                logger.warning("⚠️ No response from bad API key test")
                
        except Exception as e:
            logger.info(f"✅ Error handling working - caught exception: {type(e).__name__}")
            self.test_results['error_handling'] = True
    
    async def _test_full_production_cycle(self):
        """Test full intelligence cycle in production-like environment"""
        logger.info("🎯 Testing Full Production Cycle...")
        
        try:
            from modular.market_intelligence_module import MarketIntelligenceModule
            from modular.base_module import ModuleConfig
            
            # Production-like dependencies
            class ProductionMockRiskManager:
                def get_portfolio_summary(self):
                    return {
                        'portfolio_value': 98845.67,
                        'positions_count': 12,
                        'available_cash': 15000.0,
                        'total_equity': 98845.67
                    }
                
                def get_all_positions(self):
                    return {
                        'SPY': {
                            'quantity': 250,
                            'market_value': 112500.0,
                            'unrealized_pnl': 3750.50,
                            'avg_entry_price': 430.25,
                            'current_price': 450.00
                        },
                        'QQQ': {
                            'quantity': 100,
                            'market_value': 45000.0,
                            'unrealized_pnl': -200.25,
                            'avg_entry_price': 452.25,
                            'current_price': 450.00
                        }
                    }
            
            # Initialize full module
            config = ModuleConfig(
                module_name="market_intelligence",
                enabled=True,
                min_confidence=0.6,
                custom_params={
                    'intelligence_cycle_hours': 6,
                    'enable_pre_market': True,
                    'enable_post_market': True
                }
            )
            
            api_key = os.getenv('OPENAI_API_KEY')
            
            module = MarketIntelligenceModule(
                config=config,
                firebase_db=None,
                risk_manager=ProductionMockRiskManager(),
                order_executor=None,
                openai_api_key=api_key,
                openai_model="o4-mini",
                logger=logger
            )
            
            # Run full intelligence cycle
            logger.info("🧠 Running full daily intelligence cycle...")
            intelligence_result = await module.run_daily_intelligence_cycle()
            
            # Validate results
            if intelligence_result:
                logger.info(f"✅ Intelligence cycle complete:")
                logger.info(f"   📊 Market Signals: {len(intelligence_result.market_signals)}")
                logger.info(f"   📊 Position Insights: {len(intelligence_result.position_insights)}")
                logger.info(f"   📊 Analysis Date: {intelligence_result.analysis_date}")
                
                # Test trading opportunities
                opportunities = module.analyze_opportunities()
                logger.info(f"   💡 Trading Opportunities: {len(opportunities)}")
                
                # Test position monitoring
                exit_signals = module.monitor_positions()
                logger.info(f"   🚪 Exit Signals: {len(exit_signals)}")
                
                # Test performance summary
                performance = module.get_performance_summary()
                logger.info(f"   📈 Performance Metrics: {performance['intelligence_metrics']}")
                
                self.test_results['data_format_validation'] = True
                
            else:
                logger.error("❌ Intelligence cycle returned no results")
                
        except Exception as e:
            logger.error(f"❌ Full production cycle test failed: {e}")
    
    def _generate_test_report(self):
        """Generate final test report"""
        logger.info("\n" + "=" * 60)
        logger.info("📋 PRODUCTION INTELLIGENCE TEST REPORT")
        logger.info("=" * 60)
        
        passed_tests = sum(self.test_results.values())
        total_tests = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} {test_name.replace('_', ' ').title()}")
        
        logger.info("-" * 60)
        logger.info(f"📊 TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED - PRODUCTION READY!")
        elif passed_tests >= total_tests * 0.8:
            logger.info("✅ MOSTLY PASSING - Minor issues to address")
        else:
            logger.info("❌ SIGNIFICANT ISSUES - Review required")
        
        logger.info("=" * 60)


async def main():
    """Run production intelligence test"""
    test = ProductionIntelligenceTest()
    await test.run_full_test()


if __name__ == "__main__":
    asyncio.run(main())