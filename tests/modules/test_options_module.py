"""
Test suite for Options Trading Module

Tests the standalone options module functionality including strategy analysis,
trade execution, and position monitoring.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'modular'))

from modular.options_module import OptionsModule, OptionsContract, OptionsStrategy
from modular.base_module import ModuleConfig, TradeOpportunity, TradeAction


class TestOptionsModule(unittest.TestCase):
    """Test cases for Options Module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ModuleConfig(
            module_name="options",
            max_allocation_pct=30.0,
            min_confidence=0.6,
            custom_params={
                'leverage_target': 2.5,
                'hedge_threshold': 15.0
            }
        )
        
        # Mock dependencies
        self.mock_firebase = Mock()
        self.mock_risk_manager = Mock()
        self.mock_order_executor = Mock()
        self.mock_api_client = Mock()
        
        # Set up API client mocks
        self.mock_api_client.get_latest_quote.return_value = Mock(
            ask_price=150.0, bid_price=149.8, close=150.0
        )
        self.mock_api_client.get_account.return_value = Mock(
            portfolio_value=100000.0
        )
        self.mock_api_client.list_positions.return_value = []
        
        # Create options module
        self.options_module = OptionsModule(
            config=self.config,
            firebase_db=self.mock_firebase,
            risk_manager=self.mock_risk_manager,
            order_executor=self.mock_order_executor,
            api_client=self.mock_api_client
        )
    
    def test_module_initialization(self):
        """Test module initializes correctly"""
        self.assertEqual(self.options_module.module_name, "options")
        self.assertEqual(self.options_module.max_options_allocation, 0.30)
        self.assertEqual(self.options_module.leverage_target, 2.5)
        self.assertIsInstance(self.options_module.supported_symbols, list)
        self.assertIn('AAPL', self.options_module.supported_symbols)
    
    def test_options_contract_creation(self):
        """Test OptionsContract dataclass"""
        contract = OptionsContract(
            symbol="AAPL240119C00150000",
            contract_id="test_id",
            underlying_symbol="AAPL",
            strike=150.0,
            expiration="2024-01-19",
            option_type="call",
            ask=5.0,
            bid=4.8
        )
        
        self.assertEqual(contract.mid_price, 4.9)
        self.assertEqual(contract.option_type, "call")
        self.assertEqual(contract.strike, 150.0)
    
    def test_options_strategy_creation(self):
        """Test OptionsStrategy dataclass"""
        contract = OptionsContract(
            symbol="AAPL240119C00150000",
            contract_id="test_id",
            underlying_symbol="AAPL",
            strike=150.0,
            expiration="2024-01-19",
            option_type="call",
            ask=5.0,
            bid=4.8
        )
        
        strategy = OptionsStrategy(
            name="long_calls",
            contracts=[contract],
            quantities=[1],
            net_premium=5.0,
            max_risk=5.0,
            max_reward=float('inf'),
            breakeven=155.0,
            leverage=30.0,
            confidence_required=0.75
        )
        
        self.assertEqual(strategy.name, "long_calls")
        self.assertEqual(len(strategy.contracts), 1)
        self.assertEqual(strategy.quantities[0], 1)
        self.assertEqual(strategy.max_risk, 5.0)
    
    @patch('modular.options_module.requests.get')
    def test_get_options_chain_success(self, mock_requests):
        """Test successful options chain retrieval"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'option_contracts': [
                {
                    'symbol': 'AAPL240119C00150000',
                    'id': 'test_id_1',
                    'underlying_symbol': 'AAPL',
                    'strike_price': '150.00',
                    'expiration_date': '2024-01-19',
                    'type': 'call'
                },
                {
                    'symbol': 'AAPL240119P00150000',
                    'id': 'test_id_2',
                    'underlying_symbol': 'AAPL',
                    'strike_price': '150.00',
                    'expiration_date': '2024-01-19',
                    'type': 'put'
                }
            ]
        }
        mock_requests.return_value = mock_response
        
        # Set environment variables
        with patch.dict(os.environ, {
            'ALPACA_PAPER_API_KEY': 'test_key',
            'ALPACA_PAPER_SECRET_KEY': 'test_secret'
        }):
            chain = self.options_module._get_options_chain('AAPL')
        
        self.assertEqual(chain['symbol'], 'AAPL')
        self.assertEqual(len(chain['calls']), 1)
        self.assertEqual(len(chain['puts']), 1)
        self.assertEqual(chain['calls'][0].strike, 150.0)
        self.assertEqual(chain['puts'][0].strike, 150.0)
    
    @patch('modular.options_module.requests.get')
    def test_get_options_chain_api_error(self, mock_requests):
        """Test options chain retrieval with API error"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_requests.return_value = mock_response
        
        with patch.dict(os.environ, {
            'ALPACA_PAPER_API_KEY': 'test_key',
            'ALPACA_PAPER_SECRET_KEY': 'test_secret'
        }):
            chain = self.options_module._get_options_chain('AAPL')
        
        self.assertEqual(chain, {})
    
    def test_get_options_chain_no_credentials(self):
        """Test options chain retrieval without API credentials"""
        with patch.dict(os.environ, {}, clear=True):
            chain = self.options_module._get_options_chain('AAPL')
        
        self.assertEqual(chain, {})
    
    def test_calculate_intrinsic_value_call(self):
        """Test intrinsic value calculation for call options"""
        call_contract = OptionsContract(
            symbol="AAPL240119C00150000",
            contract_id="test_id",
            underlying_symbol="AAPL",
            strike=150.0,
            expiration="2024-01-19",
            option_type="call",
            ask=5.0,
            bid=4.8
        )
        
        # In-the-money call
        intrinsic_itm = self.options_module._calculate_intrinsic_value(call_contract, 155.0)
        self.assertEqual(intrinsic_itm, 5.0)
        
        # Out-of-the-money call
        intrinsic_otm = self.options_module._calculate_intrinsic_value(call_contract, 145.0)
        self.assertEqual(intrinsic_otm, 0.0)
    
    def test_calculate_intrinsic_value_put(self):
        """Test intrinsic value calculation for put options"""
        put_contract = OptionsContract(
            symbol="AAPL240119P00150000",
            contract_id="test_id",
            underlying_symbol="AAPL",
            strike=150.0,
            expiration="2024-01-19",
            option_type="put",
            ask=5.0,
            bid=4.8
        )
        
        # In-the-money put
        intrinsic_itm = self.options_module._calculate_intrinsic_value(put_contract, 145.0)
        self.assertEqual(intrinsic_itm, 5.0)
        
        # Out-of-the-money put
        intrinsic_otm = self.options_module._calculate_intrinsic_value(put_contract, 155.0)
        self.assertEqual(intrinsic_otm, 0.0)
    
    def test_analyze_long_calls_strategy(self):
        """Test long calls strategy analysis"""
        # Create mock options chain
        call_contract = OptionsContract(
            symbol="AAPL240119C00155000",
            contract_id="test_id",
            underlying_symbol="AAPL",
            strike=155.0,
            expiration="2024-01-19",
            option_type="call",
            ask=3.0,
            bid=2.8
        )
        
        options_chain = {
            'calls': [call_contract],
            'puts': [],
            'underlying_price': 150.0
        }
        
        strategy = self.options_module._analyze_long_calls(options_chain)
        
        self.assertIsNotNone(strategy)
        self.assertEqual(strategy.name, 'long_calls')
        self.assertEqual(len(strategy.contracts), 1)
        self.assertEqual(strategy.quantities[0], 1)
        self.assertEqual(strategy.net_premium, 3.0)
        self.assertEqual(strategy.max_risk, 3.0)
        self.assertEqual(strategy.breakeven, 158.0)  # strike + premium
    
    def test_analyze_bull_call_spreads_strategy(self):
        """Test bull call spreads strategy analysis"""
        # Create mock options chain with multiple calls
        buy_call = OptionsContract(
            symbol="AAPL240119C00152000",
            contract_id="test_id_1",
            underlying_symbol="AAPL",
            strike=152.0,
            expiration="2024-01-19",
            option_type="call",
            ask=4.0,
            bid=3.8
        )
        
        sell_call = OptionsContract(
            symbol="AAPL240119C00158000",
            contract_id="test_id_2",
            underlying_symbol="AAPL",
            strike=158.0,
            expiration="2024-01-19",
            option_type="call",
            ask=2.0,
            bid=1.8
        )
        
        options_chain = {
            'calls': [buy_call, sell_call],
            'puts': [],
            'underlying_price': 150.0
        }
        
        strategy = self.options_module._analyze_bull_call_spreads(options_chain)
        
        self.assertIsNotNone(strategy)
        self.assertEqual(strategy.name, 'bull_call_spreads')
        self.assertEqual(len(strategy.contracts), 2)
        self.assertEqual(strategy.quantities, [1, -1])
        self.assertEqual(strategy.net_premium, 2.2)  # 4.0 - 1.8
        self.assertEqual(strategy.max_reward, 3.8)  # (158-152) - 2.2
    
    def test_get_next_monthly_expiration(self):
        """Test next monthly expiration calculation"""
        expiration = self.options_module._get_next_monthly_expiration()
        
        # Should return a valid date string
        self.assertIsInstance(expiration, str)
        self.assertEqual(len(expiration), 10)  # YYYY-MM-DD format
        
        # Should be a future date
        exp_date = datetime.strptime(expiration, '%Y-%m-%d')
        self.assertGreater(exp_date, datetime.now())
    
    def test_get_third_friday(self):
        """Test third Friday calculation"""
        third_friday = self.options_module._get_third_friday(2024, 1)
        
        # January 2024 third Friday should be January 19th
        self.assertEqual(third_friday.day, 19)
        self.assertEqual(third_friday.month, 1)
        self.assertEqual(third_friday.year, 2024)
        self.assertEqual(third_friday.weekday(), 4)  # Friday is 4
    
    def test_calculate_options_allocation(self):
        """Test options allocation calculation"""
        # Mock positions with options
        mock_positions = [
            Mock(symbol='AAPL240119C00150000', market_value=1000.0),
            Mock(symbol='AAPL', market_value=5000.0),  # Stock position
            Mock(symbol='SPY240119P00400000', market_value=500.0)
        ]
        self.mock_api_client.list_positions.return_value = mock_positions
        
        allocation = self.options_module._calculate_options_allocation()
        
        # Should be 1.5% (1500 options value / 100000 portfolio)
        self.assertAlmostEqual(allocation, 0.015, places=3)
    
    def test_analyze_opportunities_allocation_limit(self):
        """Test opportunity analysis with allocation limit reached"""
        # Mock high allocation
        with patch.object(self.options_module, '_calculate_options_allocation', return_value=0.35):
            opportunities = self.options_module.analyze_opportunities()
        
        # Should return empty list when allocation limit reached
        self.assertEqual(len(opportunities), 0)
    
    def test_validate_opportunity_basic(self):
        """Test basic opportunity validation"""
        opportunity = TradeOpportunity(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=1,
            confidence=0.75,
            strategy="long_calls"
        )
        
        # Mock risk manager validation
        self.mock_risk_manager.validate_opportunity.return_value = True
        
        is_valid = self.options_module.validate_opportunity(opportunity)
        self.assertTrue(is_valid)
    
    def test_validate_opportunity_low_confidence(self):
        """Test opportunity validation with low confidence"""
        opportunity = TradeOpportunity(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=1,
            confidence=0.50,  # Below min_confidence of 0.6
            strategy="long_calls"
        )
        
        is_valid = self.options_module.validate_opportunity(opportunity)
        self.assertFalse(is_valid)
    
    def test_validate_opportunity_unsupported_symbol(self):
        """Test opportunity validation with unsupported symbol"""
        opportunity = TradeOpportunity(
            symbol="UNSUPPORTED",
            action=TradeAction.BUY,
            quantity=1,
            confidence=0.75,
            strategy="long_calls"
        )
        
        is_valid = self.options_module.validate_opportunity(opportunity)
        self.assertFalse(is_valid)
    
    def test_execute_single_leg_order_success(self):
        """Test successful single leg order execution"""
        opportunity = TradeOpportunity(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=1,
            confidence=0.75,
            strategy="long_calls",
            metadata={
                'strategy_details': {
                    'contracts': ['AAPL240119C00150000'],
                    'net_premium': 5.0
                }
            }
        )
        
        # Mock successful execution
        self.mock_order_executor.execute_order.return_value = {
            'success': True,
            'order_id': 'test_order_123'
        }
        
        result = self.options_module._execute_single_leg_order(opportunity, opportunity.metadata['strategy_details'])
        
        self.assertTrue(result.success)
        self.assertEqual(result.order_id, 'test_order_123')
        self.assertEqual(result.execution_price, 5.0)
    
    def test_execute_single_leg_order_failure(self):
        """Test failed single leg order execution"""
        opportunity = TradeOpportunity(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=1,
            confidence=0.75,
            strategy="long_calls",
            metadata={
                'strategy_details': {
                    'contracts': ['AAPL240119C00150000'],
                    'net_premium': 5.0
                }
            }
        )
        
        # Mock failed execution
        self.mock_order_executor.execute_order.return_value = {
            'success': False,
            'error': 'Insufficient buying power'
        }
        
        result = self.options_module._execute_single_leg_order(opportunity, opportunity.metadata['strategy_details'])
        
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, 'Insufficient buying power')
    
    def test_get_options_positions(self):
        """Test getting current options positions"""
        # Mock positions with mix of stocks and options
        mock_positions = [
            Mock(symbol='AAPL', qty=100, market_value=15000.0, avg_entry_price=150.0, unrealized_pl=500.0),
            Mock(symbol='AAPL240119C00150000', qty=2, market_value=1000.0, avg_entry_price=5.0, unrealized_pl=200.0),
            Mock(symbol='SPY240119P00400000', qty=1, market_value=300.0, avg_entry_price=3.0, unrealized_pl=-50.0)
        ]
        self.mock_api_client.list_positions.return_value = mock_positions
        
        options_positions = self.options_module._get_options_positions()
        
        # Should return only options positions (symbols with dates/strikes)
        self.assertEqual(len(options_positions), 2)
        self.assertEqual(options_positions[0]['symbol'], 'AAPL240119C00150000')
        self.assertEqual(options_positions[1]['symbol'], 'SPY240119P00400000')
    
    def test_analyze_position_exit_profit_target(self):
        """Test position exit analysis for profit target"""
        position = {
            'symbol': 'AAPL240119C00150000',
            'qty': 1,
            'market_value': 1000.0,
            'unrealized_pl': 1000.0  # 100% profit
        }
        
        exit_signal = self.options_module._analyze_position_exit(position)
        self.assertEqual(exit_signal, 'profit_target')
    
    def test_analyze_position_exit_stop_loss(self):
        """Test position exit analysis for stop loss"""
        position = {
            'symbol': 'AAPL240119C00150000',
            'qty': 1,
            'market_value': 500.0,
            'unrealized_pl': -250.0  # 50% loss
        }
        
        exit_signal = self.options_module._analyze_position_exit(position)
        self.assertEqual(exit_signal, 'stop_loss')
    
    def test_analyze_position_exit_no_signal(self):
        """Test position exit analysis with no exit signal"""
        position = {
            'symbol': 'AAPL240119C00150000',
            'qty': 1,
            'market_value': 1000.0,
            'unrealized_pl': 200.0  # 20% profit - not enough for exit
        }
        
        exit_signal = self.options_module._analyze_position_exit(position)
        self.assertIsNone(exit_signal)


if __name__ == '__main__':
    unittest.main()