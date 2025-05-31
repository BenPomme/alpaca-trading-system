"""
Test suite for Stocks Trading Module

Tests the standalone stocks module functionality including enhanced strategies,
intelligence-driven analysis, real market data integration, and execution.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'modular'))

from modular.stocks_module import (
    StocksModule, StockStrategy, MarketRegime, StockAnalysis, SymbolTier
)
from modular.base_module import ModuleConfig, TradeOpportunity, TradeAction


class TestStocksModule(unittest.TestCase):
    """Test cases for Stocks Module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ModuleConfig(
            module_name="stocks",
            max_allocation_pct=50.0,
            min_confidence=0.55,
            custom_params={
                'aggressive_multiplier': 2.0,
                'market_tier': 2
            }
        )
        
        # Mock dependencies
        self.mock_firebase = Mock()
        self.mock_risk_manager = Mock()
        self.mock_order_executor = Mock()
        self.mock_api_client = Mock()
        self.mock_intelligence_systems = {
            'technical_indicators': Mock(),
            'market_regime_detector': Mock(),
            'pattern_recognition': Mock()
        }
        
        # Set up API client mocks
        self.mock_api_client.get_latest_quote.return_value = Mock(
            ask_price=150.0, bid_price=149.8, close=150.0
        )
        self.mock_api_client.get_account.return_value = Mock(
            portfolio_value=100000.0
        )
        self.mock_api_client.get_clock.return_value = Mock(
            is_open=True
        )
        self.mock_api_client.list_positions.return_value = []
        
        # Set up intelligence system mocks
        self.mock_intelligence_systems['technical_indicators'].analyze_symbol.return_value = {
            'composite_score': 0.7
        }
        self.mock_intelligence_systems['market_regime_detector'].analyze_symbol_regime.return_value = {
            'confidence': 0.6
        }
        self.mock_intelligence_systems['market_regime_detector'].get_current_regime.return_value = {
            'regime': 'bull'
        }
        self.mock_intelligence_systems['pattern_recognition'].analyze_patterns.return_value = {
            'strength': 0.5
        }
        
        # Create stocks module
        self.stocks_module = StocksModule(
            config=self.config,
            firebase_db=self.mock_firebase,
            risk_manager=self.mock_risk_manager,
            order_executor=self.mock_order_executor,
            api_client=self.mock_api_client,
            intelligence_systems=self.mock_intelligence_systems
        )
    
    def test_module_initialization(self):
        """Test module initializes correctly"""
        self.assertEqual(self.stocks_module.module_name, "stocks")
        self.assertEqual(self.stocks_module.max_stock_allocation, 0.50)
        self.assertEqual(self.stocks_module.aggressive_multiplier, 2.0)
        self.assertEqual(self.stocks_module.market_tier, 2)
        self.assertIsInstance(self.stocks_module.supported_symbols, list)
        self.assertIn('AAPL', self.stocks_module.supported_symbols)
        self.assertIn('SPY', self.stocks_module.supported_symbols)
    
    def test_stock_strategy_enum(self):
        """Test StockStrategy enum"""
        self.assertEqual(StockStrategy.LEVERAGED_ETFS.value, "leveraged_etfs")
        self.assertEqual(StockStrategy.SECTOR_ROTATION.value, "sector_rotation")
        self.assertEqual(StockStrategy.MOMENTUM_AMPLIFICATION.value, "momentum_amp")
        self.assertEqual(StockStrategy.VOLATILITY_TRADING.value, "volatility_trading")
        self.assertEqual(StockStrategy.CORE_EQUITY.value, "core_equity")
    
    def test_market_regime_enum(self):
        """Test MarketRegime enum"""
        self.assertEqual(MarketRegime.BULL.value, "bull")
        self.assertEqual(MarketRegime.BEAR.value, "bear")
        self.assertEqual(MarketRegime.SIDEWAYS.value, "sideways")
        self.assertEqual(MarketRegime.UNCERTAIN.value, "uncertain")
    
    def test_stock_analysis_creation(self):
        """Test StockAnalysis dataclass"""
        analysis = StockAnalysis(
            symbol="AAPL",
            current_price=150.0,
            technical_score=0.7,
            regime_score=0.6,
            pattern_score=0.5,
            combined_confidence=0.65,
            recommended_strategy=StockStrategy.CORE_EQUITY,
            position_multiplier=1.0
        )
        
        self.assertEqual(analysis.symbol, "AAPL")
        self.assertEqual(analysis.current_price, 150.0)
        self.assertTrue(analysis.is_tradeable)  # confidence > 0.55, price > 0, technical > 0.40
        
        # Test not tradeable
        low_analysis = StockAnalysis(
            symbol="AAPL", current_price=150.0, technical_score=0.3,  # Below 0.40
            regime_score=0.6, pattern_score=0.5, combined_confidence=0.65,
            recommended_strategy=StockStrategy.CORE_EQUITY, position_multiplier=1.0
        )
        self.assertFalse(low_analysis.is_tradeable)
    
    def test_symbol_tier_creation(self):
        """Test SymbolTier dataclass"""
        tier = SymbolTier(
            tier_name="test_tier",
            symbols=["AAPL", "MSFT"],
            priority=1,
            confidence_threshold=0.60
        )
        
        self.assertEqual(tier.tier_name, "test_tier")
        self.assertEqual(len(tier.symbols), 2)
        self.assertEqual(tier.priority, 1)
        self.assertEqual(tier.confidence_threshold, 0.60)
    
    def test_supported_symbols_by_tier(self):
        """Test symbol selection based on market tier"""
        # Tier 1 should include core ETFs
        self.assertIn('SPY', self.stocks_module.supported_symbols)
        self.assertIn('QQQ', self.stocks_module.supported_symbols)
        
        # Tier 2 should include liquid stocks and sector ETFs
        self.assertIn('AAPL', self.stocks_module.supported_symbols)
        self.assertIn('MSFT', self.stocks_module.supported_symbols)
        self.assertIn('XLK', self.stocks_module.supported_symbols)
    
    def test_get_real_stock_price_success(self):
        """Test real stock price retrieval success"""
        price = self.stocks_module._get_real_stock_price('AAPL')
        self.assertEqual(price, 150.0)
    
    def test_get_real_stock_price_failure(self):
        """Test real stock price retrieval failure"""
        self.mock_api_client.get_latest_quote.return_value = None
        
        price = self.stocks_module._get_real_stock_price('AAPL')
        self.assertEqual(price, 0.0)
    
    def test_is_market_open_true(self):
        """Test market open detection"""
        is_open = self.stocks_module._is_market_open()
        self.assertTrue(is_open)
    
    def test_is_market_open_false(self):
        """Test market closed detection"""
        self.mock_api_client.get_clock.return_value = Mock(is_open=False)
        
        is_open = self.stocks_module._is_market_open()
        self.assertFalse(is_open)
    
    def test_get_market_regime_with_intelligence(self):
        """Test market regime detection with intelligence system"""
        regime = self.stocks_module._get_market_regime()
        self.assertEqual(regime, "bull")
    
    def test_get_market_regime_fallback(self):
        """Test market regime fallback when intelligence unavailable"""
        # Remove intelligence system
        stocks_module = StocksModule(
            config=self.config,
            firebase_db=self.mock_firebase,
            risk_manager=self.mock_risk_manager,
            order_executor=self.mock_order_executor,
            api_client=self.mock_api_client,
            intelligence_systems={}
        )
        
        regime = stocks_module._get_market_regime()
        self.assertEqual(regime, "sideways")  # Default fallback
    
    def test_get_technical_analysis_with_intelligence(self):
        """Test technical analysis with intelligence system"""
        score = self.stocks_module._get_technical_analysis('AAPL', 150.0)
        self.assertEqual(score, 0.7)
    
    def test_get_technical_analysis_fallback(self):
        """Test technical analysis fallback"""
        # Mock intelligence system to return None
        self.mock_intelligence_systems['technical_indicators'].analyze_symbol.return_value = None
        
        score = self.stocks_module._get_technical_analysis('AAPL', 150.0)
        self.assertEqual(score, 0.5)  # Fallback to neutral
    
    def test_get_regime_analysis_with_intelligence(self):
        """Test regime analysis with intelligence system"""
        score = self.stocks_module._get_regime_analysis('AAPL', 'bull')
        self.assertEqual(score, 0.6)
    
    def test_get_regime_analysis_fallback(self):
        """Test regime analysis fallback"""
        # Remove intelligence system
        stocks_module = StocksModule(
            config=self.config,
            firebase_db=self.mock_firebase,
            risk_manager=self.mock_risk_manager,
            order_executor=self.mock_order_executor,
            api_client=self.mock_api_client,
            intelligence_systems={}
        )
        
        score = stocks_module._get_regime_analysis('AAPL', 'bull')
        self.assertEqual(score, 0.7)  # Bull regime score
    
    def test_get_pattern_analysis_with_intelligence(self):
        """Test pattern analysis with intelligence system"""
        score = self.stocks_module._get_pattern_analysis('AAPL', 150.0)
        self.assertEqual(score, 0.5)
    
    def test_select_stock_strategy_leveraged_etfs(self):
        """Test strategy selection for leveraged ETFs"""
        strategy, multiplier = self.stocks_module._select_stock_strategy('TQQQ', 0.75, 'bull')
        self.assertEqual(strategy, StockStrategy.LEVERAGED_ETFS)
        self.assertEqual(multiplier, 2.5)
    
    def test_select_stock_strategy_sector_rotation(self):
        """Test strategy selection for sector ETFs"""
        strategy, multiplier = self.stocks_module._select_stock_strategy('XLK', 0.65, 'bull')
        self.assertEqual(strategy, StockStrategy.SECTOR_ROTATION)
        self.assertEqual(multiplier, 1.5)
    
    def test_select_stock_strategy_momentum_amplification(self):
        """Test strategy selection for momentum stocks"""
        strategy, multiplier = self.stocks_module._select_stock_strategy('NVDA', 0.80, 'bull')
        self.assertEqual(strategy, StockStrategy.MOMENTUM_AMPLIFICATION)
        self.assertEqual(multiplier, 2.0)
    
    def test_select_stock_strategy_volatility_trading(self):
        """Test strategy selection for volatility symbols"""
        strategy, multiplier = self.stocks_module._select_stock_strategy('VXX', 0.60, 'uncertain')
        self.assertEqual(strategy, StockStrategy.VOLATILITY_TRADING)
        self.assertEqual(multiplier, 1.8)
    
    def test_select_stock_strategy_core_equity(self):
        """Test strategy selection for regular stocks"""
        strategy, multiplier = self.stocks_module._select_stock_strategy('AAPL', 0.60, 'bull')
        self.assertEqual(strategy, StockStrategy.CORE_EQUITY)
        self.assertEqual(multiplier, 1.0)
    
    def test_analyze_stock_symbol_success(self):
        """Test successful stock symbol analysis"""
        analysis = self.stocks_module._analyze_stock_symbol('AAPL', 'bull')
        
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.symbol, 'AAPL')
        self.assertEqual(analysis.current_price, 150.0)
        self.assertEqual(analysis.technical_score, 0.7)
        self.assertEqual(analysis.regime_score, 0.6)
        self.assertEqual(analysis.pattern_score, 0.5)
        
        # Combined confidence should be weighted average
        expected_confidence = 0.7 * 0.4 + 0.6 * 0.4 + 0.5 * 0.2
        self.assertAlmostEqual(analysis.combined_confidence, expected_confidence, places=2)
    
    def test_analyze_stock_symbol_no_price(self):
        """Test stock analysis with no price data"""
        self.mock_api_client.get_latest_quote.return_value = None
        
        analysis = self.stocks_module._analyze_stock_symbol('INVALID', 'bull')
        self.assertIsNone(analysis)
    
    def test_calculate_stock_quantity(self):
        """Test stock quantity calculation"""
        quantity = self.stocks_module._calculate_stock_quantity('AAPL', 150.0)
        
        # 1.5% of $100k * 2.0 aggressive multiplier = $3000, at $150 = 20 shares
        expected_quantity = int((100000 * 0.015 * 2.0) / 150.0)
        self.assertEqual(quantity, expected_quantity)
    
    def test_get_current_stock_allocation_zero(self):
        """Test stock allocation calculation with no positions"""
        allocation = self.stocks_module._get_current_stock_allocation()
        self.assertEqual(allocation, 0.0)
    
    def test_get_current_stock_allocation_with_positions(self):
        """Test stock allocation calculation with positions"""
        # Mock stock positions
        mock_positions = [
            Mock(symbol='AAPL', market_value=15000.0),
            Mock(symbol='MSFT', market_value=10000.0),
            Mock(symbol='BTCUSD', market_value=5000.0)  # Should be filtered out
        ]
        self.mock_api_client.list_positions.return_value = mock_positions
        
        allocation = self.stocks_module._get_current_stock_allocation()
        
        # Should be 25% (25k stock positions out of 100k portfolio)
        self.assertAlmostEqual(allocation, 0.25, places=2)
    
    def test_get_stock_positions(self):
        """Test getting stock positions (filtering out crypto and options)"""
        # Mock positions with mix of stocks, crypto, and options
        mock_positions = [
            Mock(symbol='AAPL', qty=100, market_value=15000.0, avg_entry_price=150.0, unrealized_pl=500.0),
            Mock(symbol='MSFT', qty=50, market_value=10000.0, avg_entry_price=200.0, unrealized_pl=-200.0),
            Mock(symbol='BTCUSD', qty=0.5, market_value=22500.0, avg_entry_price=45000.0, unrealized_pl=2500.0),  # Crypto
            Mock(symbol='AAPL240119C00150000', qty=2, market_value=1000.0, avg_entry_price=5.0, unrealized_pl=200.0)  # Option
        ]
        self.mock_api_client.list_positions.return_value = mock_positions
        
        stock_positions = self.stocks_module._get_stock_positions()
        
        # Should return only stock positions (AAPL, MSFT)
        self.assertEqual(len(stock_positions), 2)
        symbols = [pos['symbol'] for pos in stock_positions]
        self.assertIn('AAPL', symbols)
        self.assertIn('MSFT', symbols)
        self.assertNotIn('BTCUSD', symbols)
        self.assertNotIn('AAPL240119C00150000', symbols)
    
    def test_analyze_stock_exit_profit_target(self):
        """Test stock exit analysis for profit target"""
        position = {
            'symbol': 'AAPL',
            'qty': 100,
            'market_value': 15000.0,
            'unrealized_pl': 2250.0  # 15% profit
        }
        
        exit_signal = self.stocks_module._analyze_stock_exit(position)
        self.assertEqual(exit_signal, 'profit_target')
    
    def test_analyze_stock_exit_stop_loss(self):
        """Test stock exit analysis for stop loss"""
        position = {
            'symbol': 'AAPL',
            'qty': 100,
            'market_value': 15000.0,
            'unrealized_pl': -1200.0  # 8% loss
        }
        
        exit_signal = self.stocks_module._analyze_stock_exit(position)
        self.assertEqual(exit_signal, 'stop_loss')
    
    def test_analyze_stock_exit_leveraged_etf_profit(self):
        """Test stock exit analysis for leveraged ETF profit"""
        position = {
            'symbol': 'TQQQ',  # Leveraged ETF
            'qty': 100,
            'market_value': 15000.0,
            'unrealized_pl': 1800.0  # 12% profit (lower threshold for leveraged)
        }
        
        exit_signal = self.stocks_module._analyze_stock_exit(position)
        self.assertEqual(exit_signal, 'leveraged_profit')
    
    def test_analyze_stock_exit_leveraged_etf_stop(self):
        """Test stock exit analysis for leveraged ETF stop loss"""
        position = {
            'symbol': 'TQQQ',  # Leveraged ETF
            'qty': 100,
            'market_value': 15000.0,
            'unrealized_pl': -900.0  # 6% loss (lower threshold for leveraged)
        }
        
        exit_signal = self.stocks_module._analyze_stock_exit(position)
        self.assertEqual(exit_signal, 'leveraged_stop')
    
    def test_analyze_stock_exit_no_signal(self):
        """Test stock exit analysis with no exit signal"""
        position = {
            'symbol': 'AAPL',
            'qty': 100,
            'market_value': 15000.0,
            'unrealized_pl': 750.0  # 5% profit - not enough for exit
        }
        
        exit_signal = self.stocks_module._analyze_stock_exit(position)
        self.assertIsNone(exit_signal)
    
    def test_infer_position_strategy_leveraged_etfs(self):
        """Test strategy inference for leveraged ETFs"""
        strategy = self.stocks_module._infer_position_strategy('TQQQ')
        self.assertEqual(strategy, StockStrategy.LEVERAGED_ETFS)
    
    def test_infer_position_strategy_sector_etfs(self):
        """Test strategy inference for sector ETFs"""
        strategy = self.stocks_module._infer_position_strategy('XLK')
        self.assertEqual(strategy, StockStrategy.SECTOR_ROTATION)
    
    def test_infer_position_strategy_momentum_stocks(self):
        """Test strategy inference for momentum stocks"""
        strategy = self.stocks_module._infer_position_strategy('NVDA')
        self.assertEqual(strategy, StockStrategy.MOMENTUM_AMPLIFICATION)
    
    def test_infer_position_strategy_volatility_symbols(self):
        """Test strategy inference for volatility symbols"""
        strategy = self.stocks_module._infer_position_strategy('VXX')
        self.assertEqual(strategy, StockStrategy.VOLATILITY_TRADING)
    
    def test_infer_position_strategy_core_equity(self):
        """Test strategy inference for regular stocks"""
        # Use a symbol that's not in any enhanced strategy categories
        strategy = self.stocks_module._infer_position_strategy('KO')  # Coca-Cola, regular stock
        self.assertEqual(strategy, StockStrategy.CORE_EQUITY)
    
    def test_execute_stock_trade_success(self):
        """Test successful stock trade execution"""
        opportunity = TradeOpportunity(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=100,
            confidence=0.70,
            strategy="stock_core_equity",
            metadata={'current_price': 150.0}
        )
        
        # Mock successful execution
        self.mock_order_executor.execute_order.return_value = {
            'success': True,
            'order_id': 'stock_order_123'
        }
        
        result = self.stocks_module._execute_stock_trade(opportunity)
        
        self.assertTrue(result.success)
        self.assertEqual(result.order_id, 'stock_order_123')
        self.assertEqual(result.execution_price, 150.0)
    
    def test_execute_stock_trade_failure(self):
        """Test failed stock trade execution"""
        opportunity = TradeOpportunity(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=100,
            confidence=0.70,
            strategy="stock_core_equity",
            metadata={'current_price': 150.0}
        )
        
        # Mock failed execution
        self.mock_order_executor.execute_order.return_value = {
            'success': False,
            'error': 'Insufficient buying power'
        }
        
        result = self.stocks_module._execute_stock_trade(opportunity)
        
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, 'Insufficient buying power')
    
    def test_analyze_opportunities_market_closed(self):
        """Test opportunity analysis when market is closed"""
        self.mock_api_client.get_clock.return_value = Mock(is_open=False)
        
        opportunities = self.stocks_module.analyze_opportunities()
        self.assertEqual(len(opportunities), 0)
    
    def test_analyze_opportunities_allocation_limit(self):
        """Test opportunity analysis with allocation limit reached"""
        # Mock high allocation
        with patch.object(self.stocks_module, '_get_current_stock_allocation', return_value=0.55):
            opportunities = self.stocks_module.analyze_opportunities()
        
        # Should return empty list when allocation limit reached
        self.assertEqual(len(opportunities), 0)
    
    def test_validate_opportunity_basic(self):
        """Test basic opportunity validation"""
        opportunity = TradeOpportunity(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=100,
            confidence=0.70,
            strategy="stock_core_equity"
        )
        
        # Mock risk manager validation
        self.mock_risk_manager.validate_opportunity.return_value = True
        
        is_valid = self.stocks_module.validate_opportunity(opportunity)
        self.assertTrue(is_valid)
    
    def test_validate_opportunity_low_confidence(self):
        """Test opportunity validation with low confidence"""
        opportunity = TradeOpportunity(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=100,
            confidence=0.50,  # Below min_confidence of 0.55
            strategy="stock_core_equity"
        )
        
        is_valid = self.stocks_module.validate_opportunity(opportunity)
        self.assertFalse(is_valid)
    
    def test_validate_opportunity_unsupported_symbol(self):
        """Test opportunity validation with unsupported symbol"""
        opportunity = TradeOpportunity(
            symbol="UNSUPPORTED",
            action=TradeAction.BUY,
            quantity=100,
            confidence=0.70,
            strategy="stock_core_equity"
        )
        
        is_valid = self.stocks_module.validate_opportunity(opportunity)
        self.assertFalse(is_valid)
    
    def test_get_strategy_summary(self):
        """Test strategy summary information"""
        summary = self.stocks_module.get_strategy_summary()
        
        self.assertEqual(summary['module_name'], 'stocks')
        self.assertEqual(summary['market_tier'], 2)
        self.assertTrue(summary['market_open'])
        self.assertEqual(summary['current_regime'], 'bull')
        self.assertIn('enhanced_strategies', summary)
        self.assertIn('leveraged_etfs', summary['enhanced_strategies'])
        self.assertIn('strategy_performance', summary)


if __name__ == '__main__':
    unittest.main()