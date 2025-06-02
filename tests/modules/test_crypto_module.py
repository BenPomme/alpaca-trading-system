"""
Test suite for Crypto Trading Module

Tests the standalone crypto module functionality including 24/7 session-aware
trading, analysis, execution, and position monitoring.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'modular'))

from modular.crypto_module import (
    CryptoModule, TradingSession, CryptoStrategy, SessionConfig, CryptoAnalysis
)
from modular.base_module import ModuleConfig, TradeOpportunity, TradeAction


class TestCryptoModule(unittest.TestCase):
    """Test cases for Crypto Module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ModuleConfig(
            module_name="crypto",
            max_allocation_pct=30.0,
            min_confidence=0.4,
            custom_params={
                'leverage_multiplier': 1.5,
                'volatility_threshold': 5.0
            }
        )
        
        # Mock dependencies
        self.mock_firebase = Mock()
        self.mock_risk_manager = Mock()
        self.mock_order_executor = Mock()
        self.mock_api_client = Mock()
        
        # Set up API client mocks
        self.mock_api_client.get_latest_quote.return_value = Mock(
            ask_price=45000.0, bid_price=44950.0, close=45000.0
        )
        self.mock_api_client.get_account.return_value = Mock(
            portfolio_value=100000.0
        )
        self.mock_api_client.list_positions.return_value = []
        
        # Create crypto module
        self.crypto_module = CryptoModule(
            config=self.config,
            firebase_db=self.mock_firebase,
            risk_manager=self.mock_risk_manager,
            order_executor=self.mock_order_executor,
            api_client=self.mock_api_client
        )
    
    def test_module_initialization(self):
        """Test module initializes correctly"""
        self.assertEqual(self.crypto_module.module_name, "crypto")
        self.assertEqual(self.crypto_module.max_crypto_allocation, 0.30)
        self.assertEqual(self.crypto_module.leverage_multiplier, 1.5)
        self.assertIsInstance(self.crypto_module.supported_symbols, list)
        self.assertIn('BTCUSD', self.crypto_module.supported_symbols)
        self.assertIn('ETHUSD', self.crypto_module.supported_symbols)
    
    def test_trading_session_enum(self):
        """Test TradingSession enum"""
        self.assertEqual(TradingSession.ASIA_PRIME.value, "asia_prime")
        self.assertEqual(TradingSession.EUROPE_PRIME.value, "europe_prime")
        self.assertEqual(TradingSession.US_PRIME.value, "us_prime")
    
    def test_crypto_strategy_enum(self):
        """Test CryptoStrategy enum"""
        self.assertEqual(CryptoStrategy.MOMENTUM.value, "momentum")
        self.assertEqual(CryptoStrategy.BREAKOUT.value, "breakout")
        self.assertEqual(CryptoStrategy.REVERSAL.value, "reversal")
    
    def test_session_config_creation(self):
        """Test SessionConfig dataclass"""
        config = SessionConfig(
            strategy=CryptoStrategy.MOMENTUM,
            position_size_multiplier=1.2,
            min_confidence=0.45,
            symbol_focus='volatile'
        )
        
        self.assertEqual(config.strategy, CryptoStrategy.MOMENTUM)
        self.assertEqual(config.position_size_multiplier, 1.2)
        self.assertEqual(config.min_confidence, 0.45)
        self.assertEqual(config.symbol_focus, 'volatile')
    
    def test_crypto_analysis_creation(self):
        """Test CryptoAnalysis dataclass"""
        analysis = CryptoAnalysis(
            symbol="BTCUSD",
            current_price=45000.0,
            momentum_score=0.7,
            volatility_score=0.6,
            volume_score=0.5,
            overall_confidence=0.65,
            session=TradingSession.ASIA_PRIME,
            strategy=CryptoStrategy.MOMENTUM
        )
        
        self.assertEqual(analysis.symbol, "BTCUSD")
        self.assertEqual(analysis.current_price, 45000.0)
        self.assertTrue(analysis.is_tradeable)  # confidence > 0.35
        
        # Test not tradeable
        low_confidence_analysis = CryptoAnalysis(
            symbol="BTCUSD", current_price=45000.0, momentum_score=0.3,
            volatility_score=0.3, volume_score=0.3, overall_confidence=0.3,
            session=TradingSession.ASIA_PRIME, strategy=CryptoStrategy.MOMENTUM
        )
        self.assertFalse(low_confidence_analysis.is_tradeable)
    
    @patch('modular.crypto_module.datetime')
    def test_get_current_trading_session_asia(self, mock_datetime):
        """Test session detection for Asia prime time"""
        # Mock UTC time at 4:00 (Asia prime)
        mock_datetime.now.return_value = Mock()
        mock_datetime.now.return_value.hour = 4
        
        session = self.crypto_module._get_current_trading_session()
        self.assertEqual(session, TradingSession.ASIA_PRIME)
    
    @patch('modular.crypto_module.datetime')
    def test_get_current_trading_session_europe(self, mock_datetime):
        """Test session detection for Europe prime time"""
        # Mock UTC time at 12:00 (Europe prime)
        mock_datetime.now.return_value = Mock()
        mock_datetime.now.return_value.hour = 12
        
        session = self.crypto_module._get_current_trading_session()
        self.assertEqual(session, TradingSession.EUROPE_PRIME)
    
    @patch('modular.crypto_module.datetime')
    def test_get_current_trading_session_us(self, mock_datetime):
        """Test session detection for US prime time"""
        # Mock UTC time at 20:00 (US prime)
        mock_datetime.now.return_value = Mock()
        mock_datetime.now.return_value.hour = 20
        
        session = self.crypto_module._get_current_trading_session()
        self.assertEqual(session, TradingSession.US_PRIME)
    
    def test_get_active_crypto_symbols_asia(self):
        """Test symbol selection during Asia session"""
        symbols = self.crypto_module._get_active_crypto_symbols(TradingSession.ASIA_PRIME)
        
        # Should include major + volatile
        self.assertIn('BTCUSD', symbols)  # major
        self.assertIn('ETHUSD', symbols)  # major
        self.assertIn('DOTUSD', symbols)  # volatile (Asia focus)
        self.assertIn('LINKUSD', symbols)  # volatile (Asia focus)
    
    def test_get_active_crypto_symbols_europe(self):
        """Test symbol selection during Europe session"""
        symbols = self.crypto_module._get_active_crypto_symbols(TradingSession.EUROPE_PRIME)
        
        # Should include major + defi
        self.assertIn('BTCUSD', symbols)  # major
        self.assertIn('ETHUSD', symbols)  # major
        self.assertIn('UNIUSD', symbols)  # defi (Europe focus)
        self.assertIn('AAVEUSD', symbols)  # defi (Europe focus)
    
    def test_get_active_crypto_symbols_us(self):
        """Test symbol selection during US session"""
        symbols = self.crypto_module._get_active_crypto_symbols(TradingSession.US_PRIME)
        
        # Should include major + gaming
        self.assertIn('BTCUSD', symbols)  # major
        self.assertIn('ETHUSD', symbols)  # major
        self.assertIn('MANAUSD', symbols)  # gaming (US focus)
        self.assertIn('SANDUSD', symbols)  # gaming (US focus)
    
    def test_calculate_crypto_mean_reversion_oversold(self):
        """Test mean reversion calculation for oversold condition"""
        market_data = {
            'current_price': 40000.0,
            'ma_20': 50000.0,  # 20% below MA (oversold)
            'volume_ratio': 1.5
        }
        
        score = self.crypto_module._calculate_crypto_mean_reversion_score('BTCUSD', market_data)
        
        # Oversold condition should result in high score
        self.assertGreater(score, 0.7)
        self.assertLessEqual(score, 1.0)
    
    def test_calculate_crypto_mean_reversion_overbought(self):
        """Test mean reversion calculation for overbought condition"""
        market_data = {
            'current_price': 60000.0,
            'ma_20': 50000.0,  # 20% above MA (overbought)
            'volume_ratio': 1.0
        }
        
        score = self.crypto_module._calculate_crypto_mean_reversion_score('BTCUSD', market_data)
        
        # Overbought condition should result in low score
        self.assertLessEqual(score, 0.2)
        self.assertGreaterEqual(score, 0.0)
    
    def test_calculate_crypto_mean_reversion_neutral(self):
        """Test mean reversion calculation for neutral zone"""
        market_data = {
            'current_price': 50000.0,
            'ma_20': 50000.0,  # At MA (neutral)
            'volume_ratio': 1.0
        }
        
        score = self.crypto_module._calculate_crypto_mean_reversion_score('BTCUSD', market_data)
        
        # Neutral zone should return moderate score
        self.assertAlmostEqual(score, 0.4, places=1)
    
    def test_calculate_crypto_volatility_high(self):
        """Test volatility calculation with high volatility"""
        market_data = {
            'current_price': 45000.0,
            'high_24h': 48000.0,
            'low_24h': 42000.0
        }
        
        volatility = self.crypto_module._calculate_crypto_volatility('BTCUSD', market_data)
        
        # 13.3% daily range should result in high volatility score
        self.assertGreater(volatility, 0.5)
    
    def test_calculate_crypto_volatility_low(self):
        """Test volatility calculation with low volatility"""
        market_data = {
            'current_price': 45000.0,
            'high_24h': 45500.0,
            'low_24h': 44500.0
        }
        
        volatility = self.crypto_module._calculate_crypto_volatility('BTCUSD', market_data)
        
        # 2.2% daily range should result in low volatility score
        self.assertLess(volatility, 0.5)
    
    def test_calculate_crypto_volume_high(self):
        """Test volume calculation with high volume"""
        market_data = {
            'volume_24h': 2000000,
            'avg_volume_7d': 1000000
        }
        
        volume = self.crypto_module._calculate_crypto_volume('BTCUSD', market_data)
        
        # 2x average volume should result in high volume score
        self.assertGreater(volume, 0.5)
    
    def test_calculate_crypto_volume_low(self):
        """Test volume calculation with low volume"""
        market_data = {
            'volume_24h': 500000,
            'avg_volume_7d': 1000000
        }
        
        volume = self.crypto_module._calculate_crypto_volume('BTCUSD', market_data)
        
        # 0.5x average volume should result in low volume score
        self.assertLess(volume, 0.5)
    
    def test_determine_crypto_action_momentum_buy(self):
        """Test action determination for momentum strategy - buy signal"""
        analysis = CryptoAnalysis(
            symbol="BTCUSD", current_price=45000.0, momentum_score=0.7,
            volatility_score=0.5, volume_score=0.5, overall_confidence=0.6,
            session=TradingSession.ASIA_PRIME, strategy=CryptoStrategy.MOMENTUM
        )
        
        action = self.crypto_module._determine_crypto_action(analysis, CryptoStrategy.MOMENTUM)
        self.assertEqual(action, TradeAction.BUY)
    
    def test_determine_crypto_action_momentum_sell(self):
        """Test action determination for momentum strategy - sell signal"""
        analysis = CryptoAnalysis(
            symbol="BTCUSD", current_price=45000.0, momentum_score=0.3,
            volatility_score=0.5, volume_score=0.5, overall_confidence=0.4,
            session=TradingSession.ASIA_PRIME, strategy=CryptoStrategy.MOMENTUM
        )
        
        action = self.crypto_module._determine_crypto_action(analysis, CryptoStrategy.MOMENTUM)
        self.assertEqual(action, TradeAction.SELL)
    
    def test_determine_crypto_action_breakout_buy(self):
        """Test action determination for breakout strategy - buy signal"""
        analysis = CryptoAnalysis(
            symbol="BTCUSD", current_price=45000.0, momentum_score=0.6,
            volatility_score=0.7, volume_score=0.5, overall_confidence=0.6,
            session=TradingSession.EUROPE_PRIME, strategy=CryptoStrategy.BREAKOUT
        )
        
        action = self.crypto_module._determine_crypto_action(analysis, CryptoStrategy.BREAKOUT)
        self.assertEqual(action, TradeAction.BUY)
    
    def test_determine_crypto_action_breakout_sell(self):
        """Test action determination for breakout strategy - sell signal"""
        analysis = CryptoAnalysis(
            symbol="BTCUSD", current_price=45000.0, momentum_score=0.5,
            volatility_score=0.4, volume_score=0.5, overall_confidence=0.5,
            session=TradingSession.EUROPE_PRIME, strategy=CryptoStrategy.BREAKOUT
        )
        
        action = self.crypto_module._determine_crypto_action(analysis, CryptoStrategy.BREAKOUT)
        self.assertEqual(action, TradeAction.SELL)
    
    def test_determine_crypto_action_reversal_buy(self):
        """Test action determination for reversal strategy - buy signal"""
        analysis = CryptoAnalysis(
            symbol="BTCUSD", current_price=45000.0, momentum_score=0.6,  # Not high enough for sell
            volatility_score=0.5, volume_score=0.5, overall_confidence=0.5,
            session=TradingSession.US_PRIME, strategy=CryptoStrategy.REVERSAL
        )
        
        action = self.crypto_module._determine_crypto_action(analysis, CryptoStrategy.REVERSAL)
        self.assertEqual(action, TradeAction.BUY)
    
    def test_determine_crypto_action_reversal_sell(self):
        """Test action determination for reversal strategy - sell signal"""
        analysis = CryptoAnalysis(
            symbol="BTCUSD", current_price=45000.0, momentum_score=0.8,  # High momentum = sell in reversal
            volatility_score=0.5, volume_score=0.5, overall_confidence=0.6,
            session=TradingSession.US_PRIME, strategy=CryptoStrategy.REVERSAL
        )
        
        action = self.crypto_module._determine_crypto_action(analysis, CryptoStrategy.REVERSAL)
        self.assertEqual(action, TradeAction.SELL)
    
    def test_get_crypto_price_success(self):
        """Test crypto price retrieval success"""            
        price = self.crypto_module._get_crypto_price('BTCUSD')
        self.assertEqual(price, 45000.0)
    
    def test_get_crypto_price_failure(self):
        """Test crypto price retrieval failure"""
        self.mock_api_client.get_latest_quote.return_value = None
        
        price = self.crypto_module._get_crypto_price('BTCUSD')
        self.assertEqual(price, 0.0)
    
    def test_get_crypto_market_data(self):
        """Test crypto market data retrieval"""
        market_data = self.crypto_module._get_crypto_market_data('BTCUSD')
        
        self.assertIsNotNone(market_data)
        self.assertIn('current_price', market_data)
        self.assertIn('price_24h_ago', market_data)
        self.assertIn('high_24h', market_data)
        self.assertIn('low_24h', market_data)
        self.assertEqual(market_data['current_price'], 45000.0)
    
    def test_calculate_crypto_quantity(self):
        """Test crypto quantity calculation"""
        quantity = self.crypto_module._calculate_crypto_quantity('BTCUSD', 45000.0)
        
        # 2% of $100k portfolio = $2000, at $45k = ~0.044 BTC
        expected_quantity = 2000.0 / 45000.0
        self.assertAlmostEqual(quantity, expected_quantity, places=6)
    
    def test_get_current_crypto_allocation_zero(self):
        """Test crypto allocation calculation with no positions"""
        allocation = self.crypto_module._get_current_crypto_allocation()
        self.assertEqual(allocation, 0.0)
    
    def test_get_current_crypto_allocation_with_positions(self):
        """Test crypto allocation calculation with positions"""
        # Mock crypto positions
        mock_positions = [
            Mock(symbol='BTCUSD', market_value=15000.0),
            Mock(symbol='ETHUSD', market_value=5000.0),
            Mock(symbol='AAPL', market_value=10000.0)  # Not crypto
        ]
        self.mock_api_client.list_positions.return_value = mock_positions
        
        allocation = self.crypto_module._get_current_crypto_allocation()
        
        # Should be 20% (20k crypto out of 100k portfolio)
        self.assertAlmostEqual(allocation, 0.20, places=2)
    
    def test_get_crypto_positions(self):
        """Test getting crypto positions"""
        # Mock positions with mix of crypto and stocks
        mock_positions = [
            Mock(symbol='BTCUSD', qty=0.5, market_value=22500.0, avg_entry_price=45000.0, unrealized_pl=2500.0),
            Mock(symbol='ETHUSD', qty=10.0, market_value=30000.0, avg_entry_price=3000.0, unrealized_pl=-1000.0),
            Mock(symbol='AAPL', qty=100, market_value=15000.0, avg_entry_price=150.0, unrealized_pl=500.0)  # Not crypto
        ]
        self.mock_api_client.list_positions.return_value = mock_positions
        
        crypto_positions = self.crypto_module._get_crypto_positions()
        
        # Should return only crypto positions
        self.assertEqual(len(crypto_positions), 2)
        self.assertEqual(crypto_positions[0]['symbol'], 'BTCUSD')
        self.assertEqual(crypto_positions[1]['symbol'], 'ETHUSD')
    
    def test_analyze_crypto_exit_profit_target(self):
        """Test crypto exit analysis for profit target"""
        position = {
            'symbol': 'BTCUSD',
            'qty': 0.5,
            'market_value': 22500.0,
            'unrealized_pl': 5625.0  # 25% profit
        }
        
        exit_signal = self.crypto_module._analyze_crypto_exit(position)
        self.assertEqual(exit_signal, 'profit_target')
    
    def test_analyze_crypto_exit_stop_loss(self):
        """Test crypto exit analysis for stop loss"""
        position = {
            'symbol': 'BTCUSD',
            'qty': 0.5,
            'market_value': 18000.0,
            'unrealized_pl': -2700.0  # 15% loss
        }
        
        exit_signal = self.crypto_module._analyze_crypto_exit(position)
        self.assertEqual(exit_signal, 'stop_loss')
    
    def test_analyze_crypto_exit_no_signal(self):
        """Test crypto exit analysis with no exit signal"""
        position = {
            'symbol': 'BTCUSD',
            'qty': 0.5,
            'market_value': 22500.0,
            'unrealized_pl': 2250.0  # 10% profit - not enough for exit
        }
        
        exit_signal = self.crypto_module._analyze_crypto_exit(position)
        self.assertIsNone(exit_signal)
    
    def test_execute_crypto_trade_success(self):
        """Test successful crypto trade execution"""
        opportunity = TradeOpportunity(
            symbol="BTCUSD",
            action=TradeAction.BUY,
            quantity=0.1,
            confidence=0.65,
            strategy="crypto_momentum",
            metadata={'current_price': 45000.0}
        )
        
        # Mock successful execution
        self.mock_order_executor.execute_order.return_value = {
            'success': True,
            'order_id': 'crypto_order_123'
        }
        
        result = self.crypto_module._execute_crypto_trade(opportunity)
        
        self.assertTrue(result.success)
        self.assertEqual(result.order_id, 'crypto_order_123')
        self.assertEqual(result.execution_price, 45000.0)
    
    def test_execute_crypto_trade_failure(self):
        """Test failed crypto trade execution"""
        opportunity = TradeOpportunity(
            symbol="BTCUSD",
            action=TradeAction.BUY,
            quantity=0.1,
            confidence=0.65,
            strategy="crypto_momentum",
            metadata={'current_price': 45000.0}
        )
        
        # Mock failed execution
        self.mock_order_executor.execute_order.return_value = {
            'success': False,
            'error': 'Insufficient buying power'
        }
        
        result = self.crypto_module._execute_crypto_trade(opportunity)
        
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, 'Insufficient buying power')
    
    def test_analyze_opportunities_allocation_limit(self):
        """Test opportunity analysis with allocation limit reached"""
        # Mock high allocation
        with patch.object(self.crypto_module, '_get_current_crypto_allocation', return_value=0.35):
            opportunities = self.crypto_module.analyze_opportunities()
        
        # Should return empty list when allocation limit reached
        self.assertEqual(len(opportunities), 0)
    
    def test_validate_opportunity_basic(self):
        """Test basic opportunity validation"""
        opportunity = TradeOpportunity(
            symbol="BTCUSD",
            action=TradeAction.BUY,
            quantity=0.1,
            confidence=0.65,
            strategy="crypto_momentum"
        )
        
        # Mock risk manager validation
        self.mock_risk_manager.validate_opportunity.return_value = True
        
        is_valid = self.crypto_module.validate_opportunity(opportunity)
        self.assertTrue(is_valid)
    
    def test_validate_opportunity_low_confidence(self):
        """Test opportunity validation with low confidence"""
        opportunity = TradeOpportunity(
            symbol="BTCUSD",
            action=TradeAction.BUY,
            quantity=0.1,
            confidence=0.30,  # Below min_confidence of 0.4
            strategy="crypto_momentum"
        )
        
        is_valid = self.crypto_module.validate_opportunity(opportunity)
        self.assertFalse(is_valid)
    
    def test_validate_opportunity_unsupported_symbol(self):
        """Test opportunity validation with unsupported symbol"""
        opportunity = TradeOpportunity(
            symbol="UNSUPPORTED",
            action=TradeAction.BUY,
            quantity=0.1,
            confidence=0.65,
            strategy="crypto_momentum"
        )
        
        is_valid = self.crypto_module.validate_opportunity(opportunity)
        self.assertFalse(is_valid)
    
    def test_get_session_summary(self):
        """Test session summary information"""
        with patch.object(self.crypto_module, '_get_current_trading_session', 
                         return_value=TradingSession.ASIA_PRIME):
            summary = self.crypto_module.get_session_summary()
        
        self.assertEqual(summary['current_session'], 'asia_prime')
        self.assertEqual(summary['strategy'], 'momentum')
        self.assertEqual(summary['min_confidence'], 0.45)
        self.assertEqual(summary['focus_category'], 'volatile')
        self.assertIn('BTCUSD', summary['active_symbols'])
        self.assertIn('DOTUSD', summary['active_symbols'])  # volatile category


if __name__ == '__main__':
    unittest.main()