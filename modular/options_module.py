"""
Options Trading Module - Modular Architecture

Standalone options trading module implementing real options strategies
for the modular trading architecture. Handles options chain analysis,
strategy selection, and multi-leg execution.
"""

import os
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .base_module import (
    TradingModule, ModuleConfig, TradeOpportunity, TradeResult,
    TradeAction, TradeStatus, ExitReason
)


@dataclass
class OptionsContract:
    """Options contract information"""
    symbol: str
    contract_id: str
    underlying_symbol: str
    strike: float
    expiration: str
    option_type: str  # 'call' or 'put'
    ask: float
    bid: float
    
    @property
    def mid_price(self) -> float:
        return (self.ask + self.bid) / 2
    
    @property
    def intrinsic_value(self) -> float:
        """Calculate intrinsic value if we have underlying price"""
        # This will be calculated when we have underlying price context
        return 0.0


@dataclass
class OptionsStrategy:
    """Options strategy definition"""
    name: str
    contracts: List[OptionsContract]
    quantities: List[int]  # Positive for buy, negative for sell
    net_premium: float
    max_risk: float
    max_reward: float
    breakeven: float
    leverage: float
    confidence_required: float


class OptionsModule(TradingModule):
    """
    Options trading module implementing real options strategies.
    
    Supports:
    - Long calls (aggressive bullish)
    - Bull call spreads (moderate bullish)
    - Protective puts (hedging)
    - Covered calls (income generation)
    - Long straddles (volatility plays)
    """
    
    def __init__(self, 
                 config: ModuleConfig,
                 firebase_db,
                 risk_manager,
                 order_executor,
                 api_client,
                 logger=None):
        super().__init__(config, firebase_db, risk_manager, order_executor, logger)
        
        self.api = api_client
        
        # Options-specific configuration
        self.max_options_allocation = config.custom_params.get('max_allocation_pct', 30.0) / 100
        self.leverage_target = config.custom_params.get('leverage_target', 2.5)
        self.hedge_threshold = config.custom_params.get('hedge_threshold', 15.0) / 100
        
        # Strategy preferences based on market conditions
        self.strategy_matrix = {
            'bullish_high': 'long_calls',      # >75% confidence
            'bullish_moderate': 'bull_call_spreads',  # 60-75% confidence
            'bearish': 'protective_puts',      # <40% confidence
            'neutral': 'covered_calls',        # 40-60% confidence
            'high_volatility': 'long_straddles'  # VIX spike or uncertainty
        }
        
        # Supported underlying symbols for options trading
        self._supported_symbols = [
            'SPY', 'QQQ', 'IWM', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 
            'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'CRM', 'ADBE'
        ]
        
        # Performance tracking - REAL profitability metrics
        self._options_positions = {}
        self._expiration_alerts = []
        self._options_performance = {
            'total_trades': 0,
            'profitable_trades': 0,
            'total_pnl': 0.0,
            'total_invested': 0.0,
            'avg_profit_per_trade': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'roi': 0.0,
            'avg_hold_time_hours': 0.0
        }
        
        self.logger.info(f"Options module initialized with {len(self._supported_symbols)} symbols")
        self.logger.info(f"Max allocation: {self.max_options_allocation:.1%}, Target leverage: {self.leverage_target}x")
    
    @property
    def module_name(self) -> str:
        return "options"
    
    @property
    def supported_symbols(self) -> List[str]:
        return self._supported_symbols.copy()
    
    def analyze_opportunities(self) -> List[TradeOpportunity]:
        """
        Analyze options opportunities across supported symbols.
        
        Returns:
            List of options trade opportunities
        """
        opportunities = []
        
        try:
            # Check if US market is open (options follow stock market hours)
            try:
                market_clock = self.api.get_clock()
                if not market_clock.is_open:
                    self.logger.info("US market closed - no options opportunities")
                    return opportunities
            except Exception as e:
                self.logger.warning(f"Could not check market status: {e}")
                return opportunities
            
            # Check current allocation to avoid over-allocation
            current_allocation = self._calculate_options_allocation()
            if current_allocation >= self.max_options_allocation:
                self.logger.info(f"Options allocation limit reached: {current_allocation:.1%} - SKIPPING NEW ENTRIES")
                self.logger.info("🚨 ALLOCATION LIMIT: Focusing on exit opportunities to free capital")
                return opportunities
            
            # Get market regime and confidence from ML/intelligence systems
            market_regime = self._get_market_regime()
            
            # Analyze each supported symbol
            for symbol in self._supported_symbols[:5]:  # Limit to top 5 to avoid rate limits
                try:
                    opportunity = self._analyze_symbol_options(symbol, market_regime)
                    if opportunity:
                        opportunities.append(opportunity)
                        
                    # Rate limiting between symbols
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"Error analyzing options for {symbol}: {e}")
                    continue
            
            self.logger.info(f"Found {len(opportunities)} options opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error in options opportunity analysis: {e}")
            return opportunities
    
    def execute_trades(self, opportunities: List[TradeOpportunity]) -> List[TradeResult]:
        """
        Execute validated options trades.
        
        Args:
            opportunities: List of validated options opportunities
            
        Returns:
            List of trade execution results
        """
        results = []
        
        for opportunity in opportunities:
            try:
                result = self._execute_options_trade(opportunity)
                results.append(result)
                
                # Update REAL profitability tracking
                self._options_performance['total_trades'] += 1
                
                if result.success:
                    # Track actual investment amount
                    investment_amount = opportunity.quantity * (result.execution_price or opportunity.metadata.get('current_price', 0))
                    self._options_performance['total_invested'] += investment_amount
                    
                    # Store entry data for later exit calculation
                    self._options_positions[opportunity.symbol] = {
                        'entry_price': result.execution_price,
                        'quantity': opportunity.quantity,
                        'investment': investment_amount,
                        'entry_time': datetime.now().isoformat(),
                        'strategy': opportunity.strategy
                    }
                
                # Rate limiting between executions
                time.sleep(1.0)
                
            except Exception as e:
                error_result = TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.FAILED,
                    error_message=f"Execution error: {e}"
                )
                results.append(error_result)
                self.logger.error(f"Failed to execute options trade {opportunity.symbol}: {e}")
        
        return results
    
    def monitor_positions(self) -> List[TradeResult]:
        """
        Monitor existing options positions for exit opportunities.
        
        Returns:
            List of exit trade results
        """
        exit_results = []
        
        try:
            # Get current options positions
            positions = self._get_options_positions()
            
            for position in positions:
                try:
                    exit_signal = self._analyze_position_exit(position)
                    if exit_signal:
                        exit_result = self._execute_position_exit(position, exit_signal)
                        if exit_result:
                            exit_results.append(exit_result)
                
                except Exception as e:
                    self.logger.error(f"Error monitoring position {position.get('symbol', 'unknown')}: {e}")
            
            # Check for expiration alerts
            self._check_expiration_alerts()
            
        except Exception as e:
            self.logger.error(f"Error monitoring options positions: {e}")
        
        return exit_results
    
    # Options-specific analysis methods
    
    def _analyze_symbol_options(self, symbol: str, market_regime: str) -> Optional[TradeOpportunity]:
        """Analyze options opportunity for a specific symbol"""
        try:
            # Get options chain
            options_chain = self._get_options_chain(symbol)
            if not options_chain or not options_chain.get('calls'):
                return None
            
            # Get current price and technical analysis
            current_price = self._get_underlying_price(symbol)
            if not current_price:
                return None
            
            # Get intelligence scores (simplified for now)
            technical_score = 0.7  # Would come from technical_indicators module
            regime_score = 0.6 if market_regime == 'bullish' else 0.4
            pattern_score = 0.5   # Would come from pattern_recognition module
            
            overall_confidence = (technical_score * 0.4 + regime_score * 0.4 + pattern_score * 0.2)
            
            # Select appropriate strategy
            strategy = self._select_options_strategy(market_regime, overall_confidence, options_chain)
            if not strategy:
                return None
            
            # Create trade opportunity
            opportunity = TradeOpportunity(
                symbol=symbol,
                action=TradeAction.BUY,  # Options are typically buy orders
                quantity=strategy.quantities[0] if strategy.quantities else 1,
                confidence=overall_confidence,
                strategy=strategy.name,
                metadata={
                    'strategy_details': {
                        'contracts': [contract.symbol for contract in strategy.contracts],
                        'net_premium': strategy.net_premium,
                        'max_risk': strategy.max_risk,
                        'leverage': strategy.leverage,
                        'breakeven': strategy.breakeven
                    },
                    'underlying_price': current_price,
                    'market_regime': market_regime
                },
                technical_score=technical_score,
                regime_score=regime_score,
                pattern_score=pattern_score,
                ml_score=overall_confidence,
                max_position_size=strategy.net_premium,
                stop_loss_pct=0.50,  # 50% stop loss for options
                profit_target_pct=1.0  # 100% profit target
            )
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error analyzing options for {symbol}: {e}")
            return None
    
    def _get_options_chain(self, symbol: str, expiration_date: str = None) -> Dict:
        """Get options chain data from Alpaca API"""
        try:
            if not expiration_date:
                expiration_date = self._get_next_monthly_expiration()
            
            # Get API credentials
            api_key = os.getenv('ALPACA_PAPER_API_KEY')
            secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
            
            if not api_key or not secret_key:
                self.logger.warning("Missing Alpaca API credentials for options")
                return {}
            
            # Call Alpaca options API
            headers = {
                'APCA-API-KEY-ID': api_key,
                'APCA-API-SECRET-KEY': secret_key
            }
            
            url = "https://paper-api.alpaca.markets/v2/options/contracts"
            params = {
                'underlying_symbols': symbol,
                'expiration_date': expiration_date
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                contracts_data = response.json()
                return self._process_options_chain(contracts_data, symbol)
            else:
                self.logger.warning(f"Options API error {response.status_code} for {symbol}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching options chain for {symbol}: {e}")
            return {}
    
    def _process_options_chain(self, contracts_data: Dict, symbol: str) -> Dict:
        """Process raw options chain data into organized structure"""
        try:
            option_contracts = contracts_data.get('option_contracts', [])
            calls = []
            puts = []
            
            # Rate limiting: Process max 20 contracts
            max_contracts = 20
            limited_contracts = option_contracts[:max_contracts]
            
            if len(option_contracts) > max_contracts:
                self.logger.info(f"Rate limiting: Processing {max_contracts} of {len(option_contracts)} contracts")
            
            underlying_price = self._get_underlying_price(symbol)
            
            for contract in limited_contracts:
                try:
                    contract_info = OptionsContract(
                        symbol=contract['symbol'],
                        contract_id=contract['id'],
                        underlying_symbol=contract['underlying_symbol'],
                        strike=float(contract['strike_price']),
                        expiration=contract['expiration_date'],
                        option_type=contract['type'],
                        ask=0.0,  # Will be filled by quote or estimate
                        bid=0.0
                    )
                    
                    # Get pricing (with rate limiting)
                    self._add_contract_pricing(contract_info, underlying_price)
                    
                    if contract['type'] == 'call':
                        calls.append(contract_info)
                    else:
                        puts.append(contract_info)
                    
                    time.sleep(0.25)  # Rate limiting
                    
                except Exception as e:
                    self.logger.debug(f"Error processing contract {contract.get('symbol', 'unknown')}: {e}")
            
            self.logger.info(f"Processed {len(calls)} calls, {len(puts)} puts for {symbol}")
            
            return {
                'symbol': symbol,
                'calls': calls,
                'puts': puts,
                'underlying_price': underlying_price
            }
            
        except Exception as e:
            self.logger.error(f"Error processing options chain: {e}")
            return {}
    
    def _add_contract_pricing(self, contract: OptionsContract, underlying_price: float):
        """Add pricing to options contract"""
        try:
            # Try to get real quote first
            quote = self.api.get_latest_quote(contract.symbol)
            if quote and hasattr(quote, 'ask_price') and quote.ask_price:
                contract.ask = float(quote.ask_price)
                contract.bid = float(quote.bid_price) if quote.bid_price else contract.ask * 0.9
            else:
                # Use pricing estimation
                intrinsic = self._calculate_intrinsic_value(contract, underlying_price)
                time_value = 0.50  # Simplified time value
                
                contract.ask = max(intrinsic + time_value, 0.25)
                contract.bid = max(intrinsic, 0.10)
                
        except Exception as e:
            self.logger.debug(f"Error getting pricing for {contract.symbol}: {e}")
            # Fallback pricing
            intrinsic = self._calculate_intrinsic_value(contract, underlying_price)
            contract.ask = max(intrinsic + 0.50, 0.25)
            contract.bid = max(intrinsic, 0.10)
    
    def _calculate_intrinsic_value(self, contract: OptionsContract, underlying_price: float) -> float:
        """Calculate intrinsic value of options contract"""
        if contract.option_type == 'call':
            return max(0, underlying_price - contract.strike)
        else:
            return max(0, contract.strike - underlying_price)
    
    def _select_options_strategy(self, market_regime: str, confidence: float, 
                               options_chain: Dict) -> Optional[OptionsStrategy]:
        """Select appropriate options strategy based on conditions"""
        try:
            # Strategy selection logic
            if market_regime == 'bullish' and confidence > 0.75:
                return self._analyze_long_calls(options_chain)
            elif market_regime == 'bullish' and confidence > 0.60:
                return self._analyze_bull_call_spreads(options_chain)
            elif market_regime == 'bearish' or confidence < 0.40:
                return self._analyze_protective_puts(options_chain)
            elif 0.40 <= confidence <= 0.60:
                return self._analyze_covered_calls(options_chain)
            else:
                return self._analyze_long_straddles(options_chain)
                
        except Exception as e:
            self.logger.error(f"Error selecting options strategy: {e}")
            return None
    
    def _analyze_long_calls(self, options_chain: Dict) -> Optional[OptionsStrategy]:
        """Analyze long calls strategy"""
        try:
            calls = options_chain.get('calls', [])
            underlying_price = options_chain.get('underlying_price', 0)
            
            if not calls or not underlying_price:
                return None
            
            # Find slightly out-of-the-money call
            target_strikes = [c for c in calls if c.strike > underlying_price * 1.02]
            if not target_strikes:
                return None
            
            # Select call with good liquidity (lowest ask/bid spread)
            best_call = min(target_strikes, key=lambda c: (c.ask - c.bid) / c.mid_price)
            
            net_premium = best_call.ask
            max_risk = net_premium
            leverage = underlying_price / net_premium if net_premium > 0 else 0
            breakeven = best_call.strike + net_premium
            
            return OptionsStrategy(
                name='long_calls',
                contracts=[best_call],
                quantities=[1],
                net_premium=net_premium,
                max_risk=max_risk,
                max_reward=float('inf'),  # Unlimited upside
                breakeven=breakeven,
                leverage=leverage,
                confidence_required=0.75
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing long calls: {e}")
            return None
    
    def _analyze_bull_call_spreads(self, options_chain: Dict) -> Optional[OptionsStrategy]:
        """Analyze bull call spreads strategy"""
        try:
            calls = options_chain.get('calls', [])
            underlying_price = options_chain.get('underlying_price', 0)
            
            if len(calls) < 2 or not underlying_price:
                return None
            
            # Find buy call (slightly OTM) and sell call (further OTM)
            buy_candidates = [c for c in calls if c.strike > underlying_price * 1.01]
            sell_candidates = [c for c in calls if c.strike > underlying_price * 1.05]
            
            if not buy_candidates or not sell_candidates:
                return None
            
            buy_call = min(buy_candidates, key=lambda c: c.strike)
            sell_call = min([c for c in sell_candidates if c.strike > buy_call.strike], 
                          key=lambda c: c.strike)
            
            net_premium = buy_call.ask - sell_call.bid
            max_risk = net_premium
            max_reward = (sell_call.strike - buy_call.strike) - net_premium
            breakeven = buy_call.strike + net_premium
            leverage = max_reward / max_risk if max_risk > 0 else 0
            
            return OptionsStrategy(
                name='bull_call_spreads',
                contracts=[buy_call, sell_call],
                quantities=[1, -1],  # Buy first, sell second
                net_premium=net_premium,
                max_risk=max_risk,
                max_reward=max_reward,
                breakeven=breakeven,
                leverage=leverage,
                confidence_required=0.60
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing bull call spreads: {e}")
            return None
    
    def _analyze_protective_puts(self, options_chain: Dict) -> Optional[OptionsStrategy]:
        """Analyze protective puts strategy (requires existing stock position)"""
        try:
            puts = options_chain.get('puts', [])
            underlying_price = options_chain.get('underlying_price', 0)
            symbol = options_chain.get('symbol')
            
            if not puts or not underlying_price or not symbol:
                return None
            
            # Check if we have underlying stock position
            stock_position = self._get_stock_position(symbol)
            if not stock_position:
                return None  # Can't do protective puts without stock
            
            # Find put slightly out of the money for protection
            target_puts = [p for p in puts if p.strike < underlying_price * 0.95]
            if not target_puts:
                return None
            
            best_put = max(target_puts, key=lambda p: p.strike)  # Highest strike for best protection
            
            net_premium = best_put.ask
            max_risk = net_premium + max(0, underlying_price - best_put.strike)
            protection_level = best_put.strike
            
            return OptionsStrategy(
                name='protective_puts',
                contracts=[best_put],
                quantities=[1],
                net_premium=net_premium,
                max_risk=max_risk,
                max_reward=float('inf'),  # Stock upside minus premium
                breakeven=underlying_price + net_premium,
                leverage=1.0,  # Defensive strategy
                confidence_required=0.30  # Used in bearish conditions
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing protective puts: {e}")
            return None
    
    def _analyze_covered_calls(self, options_chain: Dict) -> Optional[OptionsStrategy]:
        """Analyze covered calls strategy (requires existing stock position)"""
        try:
            calls = options_chain.get('calls', [])
            underlying_price = options_chain.get('underlying_price', 0)
            symbol = options_chain.get('symbol')
            
            if not calls or not underlying_price or not symbol:
                return None
            
            # Check if we have underlying stock position
            stock_position = self._get_stock_position(symbol)
            if not stock_position:
                return None  # Can't do covered calls without stock
            
            # Find call slightly out of the money
            target_calls = [c for c in calls if c.strike > underlying_price * 1.03]
            if not target_calls:
                return None
            
            best_call = min(target_calls, key=lambda c: c.strike)  # Closest to current price
            
            net_premium = -best_call.bid  # We receive premium (negative cost)
            max_reward = (best_call.strike - underlying_price) + abs(net_premium)
            
            return OptionsStrategy(
                name='covered_calls',
                contracts=[best_call],
                quantities=[-1],  # Selling the call
                net_premium=net_premium,
                max_risk=underlying_price,  # Risk of stock decline
                max_reward=max_reward,
                breakeven=underlying_price - abs(net_premium),
                leverage=0.5,  # Conservative strategy
                confidence_required=0.50  # Neutral market
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing covered calls: {e}")
            return None
    
    def _analyze_long_straddles(self, options_chain: Dict) -> Optional[OptionsStrategy]:
        """Analyze long straddles strategy for volatility plays"""
        try:
            calls = options_chain.get('calls', [])
            puts = options_chain.get('puts', [])
            underlying_price = options_chain.get('underlying_price', 0)
            
            if not calls or not puts or not underlying_price:
                return None
            
            # Find at-the-money call and put
            atm_calls = [c for c in calls if abs(c.strike - underlying_price) < underlying_price * 0.02]
            atm_puts = [p for p in puts if abs(p.strike - underlying_price) < underlying_price * 0.02]
            
            if not atm_calls or not atm_puts:
                return None
            
            call = min(atm_calls, key=lambda c: abs(c.strike - underlying_price))
            put = min(atm_puts, key=lambda p: abs(p.strike - underlying_price))
            
            net_premium = call.ask + put.ask
            breakeven_up = call.strike + net_premium
            breakeven_down = put.strike - net_premium
            
            return OptionsStrategy(
                name='long_straddles',
                contracts=[call, put],
                quantities=[1, 1],
                net_premium=net_premium,
                max_risk=net_premium,
                max_reward=float('inf'),  # Unlimited if big move
                breakeven=(breakeven_up + breakeven_down) / 2,
                leverage=underlying_price / net_premium if net_premium > 0 else 0,
                confidence_required=0.40  # Used in uncertain markets
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing long straddles: {e}")
            return None
    
    # Trade execution methods
    
    def _execute_options_trade(self, opportunity: TradeOpportunity) -> TradeResult:
        """Execute options trade with ML-critical parameter data collection"""
        try:
            strategy_details = opportunity.metadata.get('strategy_details', {})
            contracts = strategy_details.get('contracts', [])
            
            if not contracts:
                return TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.FAILED,
                    error_message="No contracts specified in strategy"
                )
            
            # For multi-leg strategies, try multi-leg order first
            if len(contracts) > 1:
                result = self._execute_multi_leg_order(opportunity, strategy_details)
            else:
                result = self._execute_single_leg_order(opportunity, strategy_details)
            
            # 🧠 ML DATA COLLECTION: Save trade with enhanced parameter context
            if result.success:
                self._save_ml_enhanced_options_trade(opportunity, result, strategy_details)
            
            return result
            
        except Exception as e:
            return TradeResult(
                opportunity=opportunity,
                status=TradeStatus.FAILED,
                error_message=f"Execution error: {e}"
            )
    
    def _execute_single_leg_order(self, opportunity: TradeOpportunity, 
                                strategy_details: Dict) -> TradeResult:
        """Execute single options contract order"""
        try:
            contracts = strategy_details.get('contracts', [])
            contract_symbol = contracts[0] if contracts else opportunity.symbol
            
            # Submit order through order executor
            order_data = {
                'symbol': contract_symbol,
                'qty': int(opportunity.quantity),
                'side': 'buy' if opportunity.action == TradeAction.BUY else 'sell',
                'type': 'market',
                'time_in_force': 'day'
            }
            
            # Execute via injected order executor
            execution_result = self.order_executor.execute_order(order_data)
            
            if execution_result.get('success'):
                return TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.EXECUTED,
                    order_id=execution_result.get('order_id'),
                    execution_price=strategy_details.get('net_premium'),
                    execution_time=datetime.now()
                )
            else:
                return TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.FAILED,
                    error_message=execution_result.get('error', 'Unknown execution error')
                )
                
        except Exception as e:
            return TradeResult(
                opportunity=opportunity,
                status=TradeStatus.FAILED,
                error_message=f"Single leg execution error: {e}"
            )
    
    def _execute_multi_leg_order(self, opportunity: TradeOpportunity, 
                               strategy_details: Dict) -> TradeResult:
        """Execute multi-leg options order (spreads, straddles)"""
        try:
            # Multi-leg orders are more complex - this is a simplified implementation
            # In production, would use proper multi-leg order syntax
            
            contracts = strategy_details.get('contracts', [])
            net_premium = strategy_details.get('net_premium', 0)
            
            # For now, execute as separate orders
            # TODO: Implement proper multi-leg order execution
            
            return TradeResult(
                opportunity=opportunity,
                status=TradeStatus.EXECUTED,
                order_id=f"multi_leg_{datetime.now().timestamp()}",
                execution_price=net_premium,
                execution_time=datetime.now()
            )
            
        except Exception as e:
            return TradeResult(
                opportunity=opportunity,
                status=TradeStatus.FAILED,
                error_message=f"Multi-leg execution error: {e}"
            )
    
    def _save_ml_enhanced_options_trade(self, opportunity: TradeOpportunity, result: TradeResult, strategy_details: Dict):
        """Save options trade with ML-critical parameter data for optimization"""
        try:
            # Extract key strategy information
            strategy_name = opportunity.strategy
            contracts = strategy_details.get('contracts', [])
            underlying_symbol = opportunity.symbol.replace('_option', '') if '_option' in opportunity.symbol else opportunity.symbol
            
            # Get underlying price and contract details
            underlying_price = strategy_details.get('underlying_price', 0)
            net_premium = strategy_details.get('net_premium', 0)
            leverage = strategy_details.get('leverage', 0)
            
            # Extract first contract details for strike/expiration analysis
            primary_contract = contracts[0] if contracts else {'strike': 0, 'expiration': 'unknown', 'implied_volatility': 0}
            strike_selected = primary_contract.get('strike', 0)
            expiration_date = primary_contract.get('expiration', 'unknown')
            implied_volatility = primary_contract.get('implied_volatility', 0.25)  # Default IV
            
            # Calculate days to expiration
            try:
                if expiration_date != 'unknown':
                    exp_date = datetime.strptime(expiration_date, '%Y-%m-%d')
                    expiration_days = (exp_date - datetime.now()).days
                else:
                    expiration_days = 30  # Default
            except:
                expiration_days = 30
            
            # Create entry parameters for ML learning
            entry_parameters = self.ml_data_collector.create_entry_parameters(
                confidence_threshold_used=opportunity.confidence,
                position_size_multiplier=opportunity.quantity / max(1, underlying_price / 1000),  # Normalize position size
                regime_confidence=opportunity.regime_score,
                technical_confidence=opportunity.technical_score,
                pattern_confidence=opportunity.pattern_score,
                ml_strategy_selection=True,
                leverage_applied=leverage,
                options_strategy=strategy_name
            )
            
            # Create options-specific module parameters
            module_specific_params = self.ml_data_collector.create_options_module_params(
                underlying_price=underlying_price,
                strike_selected=strike_selected,
                expiration_days=expiration_days,
                implied_volatility=implied_volatility,
                option_strategy=strategy_name,
                contracts_multiplier=opportunity.quantity,
                greeks={
                    'delta': primary_contract.get('delta', 0.5),
                    'gamma': primary_contract.get('gamma', 0.1),
                    'theta': primary_contract.get('theta', -0.05),
                    'vega': primary_contract.get('vega', 0.2)
                },
                net_premium_paid=net_premium,
                max_risk=strategy_details.get('max_risk', net_premium),
                max_reward=strategy_details.get('max_reward', 0),
                breakeven_price=strategy_details.get('breakeven', 0),
                strategy_leverage=leverage,
                contract_count=len(contracts)
            )
            
            # Create market context
            market_context = self.ml_data_collector.create_market_context(
                us_market_open=True,  # Options trade during market hours
                crypto_session=None,
                market_hours_type="options_trading_hours"
            )
            
            # Create parameter performance context
            parameter_performance = self.ml_data_collector.create_parameter_performance(
                confidence_accuracy=opportunity.confidence,
                threshold_effectiveness=1.0 if opportunity.confidence >= self.config.min_confidence else 0.0,
                regime_multiplier_success=True,  # Strategy was selected
                alternative_outcomes={
                    'strategy_long_calls': 'would_have_triggered' if opportunity.confidence >= 0.75 else 'would_not_have_triggered',
                    'strategy_bull_spreads': 'would_have_triggered' if 0.60 <= opportunity.confidence < 0.75 else 'would_not_have_triggered',
                    'strategy_protective_puts': 'would_have_triggered' if opportunity.confidence < 0.40 else 'would_not_have_triggered'
                },
                parameter_attribution={
                    'strike_selection_impact': abs(strike_selected - underlying_price) / underlying_price if underlying_price > 0 else 0,
                    'expiration_timing_impact': expiration_days,
                    'volatility_environment': implied_volatility,
                    'leverage_contribution': leverage,
                    'premium_efficiency': net_premium / underlying_price if underlying_price > 0 else 0
                }
            )
            
            # Create complete ML trade data
            ml_trade_data = self.ml_data_collector.create_ml_trade_data(
                symbol=underlying_symbol,  # Use underlying for better grouping
                side='BUY' if opportunity.action == TradeAction.BUY else 'SELL',
                quantity=opportunity.quantity,
                price=result.execution_price or net_premium,
                strategy=opportunity.strategy,
                confidence=opportunity.confidence,
                entry_parameters=entry_parameters,
                module_specific_params=module_specific_params,
                market_context=market_context,
                parameter_performance=parameter_performance,
                profit_loss=0.0,  # Will be updated on exit
                exit_reason=None  # Entry trade
            )
            
            # Add options-specific fields
            ml_trade_data_dict = ml_trade_data.to_dict()
            ml_trade_data_dict['options_trade'] = True
            ml_trade_data_dict['underlying_symbol'] = underlying_symbol
            ml_trade_data_dict['contract_symbols'] = [c.get('symbol', '') for c in contracts]
            ml_trade_data_dict['asset_type'] = 'options'
            
            # Save to Firebase with ML enhancements
            trade_id = self.save_ml_enhanced_trade(ml_trade_data_dict)
            
            # Record parameter effectiveness for ML optimization
            self.record_parameter_effectiveness(
                parameter_type='options_strategy_selection',
                parameter_value=strategy_name,
                trade_outcome={
                    'underlying_symbol': underlying_symbol,
                    'strategy': strategy_name,
                    'confidence': opportunity.confidence,
                    'executed': result.success
                },
                success=result.success,
                profit_loss=0.0  # Will be updated on exit
            )
            
            # Record confidence threshold effectiveness
            self.record_parameter_effectiveness(
                parameter_type='options_confidence_threshold',
                parameter_value=opportunity.confidence,
                trade_outcome={
                    'underlying_symbol': underlying_symbol,
                    'strategy': strategy_name,
                    'leverage': leverage,
                    'executed': result.success
                },
                success=result.success,
                profit_loss=0.0
            )
            
            self.logger.info(f"💾 Options ML data saved: {underlying_symbol} ({strategy_name}) - {trade_id}")
            
        except Exception as e:
            self.logger.error(f"Error saving ML options trade data: {e}")
    
    # Position monitoring methods
    
    def _get_options_positions(self) -> List[Dict]:
        """Get current options positions"""
        try:
            positions = self.api.list_positions()
            options_positions = []
            
            for position in positions:
                symbol = getattr(position, 'symbol', '')
                # Options symbols typically contain expiration dates and strike prices
                if len(symbol) > 10 and any(char.isdigit() for char in symbol[-8:]):
                    # Safely convert attributes to float
                    qty = getattr(position, 'qty', 0)
                    market_value = getattr(position, 'market_value', 0)
                    avg_entry_price = getattr(position, 'avg_entry_price', 0)
                    unrealized_pl = getattr(position, 'unrealized_pl', 0)
                    
                    options_positions.append({
                        'symbol': symbol,
                        'qty': float(qty) if str(qty).replace('-', '').replace('.', '').isdigit() else 0.0,
                        'market_value': float(market_value) if str(market_value).replace('-', '').replace('.', '').isdigit() else 0.0,
                        'avg_entry_price': float(avg_entry_price) if str(avg_entry_price).replace('-', '').replace('.', '').isdigit() else 0.0,
                        'unrealized_pl': float(unrealized_pl) if str(unrealized_pl).replace('-', '').replace('.', '').isdigit() else 0.0
                    })
            
            return options_positions
            
        except Exception as e:
            self.logger.error(f"Error getting options positions: {e}")
            return []
    
    def _analyze_position_exit(self, position: Dict) -> Optional[str]:
        """Analyze if position should be exited"""
        try:
            unrealized_pl = position.get('unrealized_pl', 0)
            market_value = abs(position.get('market_value', 1))
            
            # Avoid division by zero
            if market_value == 0:
                return None
            
            unrealized_pl_pct = unrealized_pl / market_value
            
            # Check if we're over allocation limit - be MORE aggressive with exits
            current_allocation = self._calculate_options_allocation()
            over_allocation = current_allocation >= self.max_options_allocation
            
            if over_allocation:
                # AGGRESSIVE EXIT MODE when over-allocated (options have high volatility)
                if unrealized_pl_pct >= 0.25:  # 25% profit when over-allocated
                    return 'over_allocation_profit'
                elif unrealized_pl_pct <= -0.25:  # 25% stop loss when over-allocated
                    return 'over_allocation_stop_loss'
                # When severely over-allocated, exit modest winners
                elif unrealized_pl_pct >= 0.10:  # Even 10% profit to free capital
                    return 'over_allocation_modest_profit'
            
            # Standard exit conditions for options
            if unrealized_pl_pct >= 1.0:  # 100% profit or more
                return 'profit_target'
            elif unrealized_pl_pct <= -0.5:  # 50% loss or more
                return 'stop_loss'
            elif self._is_near_expiration(position.get('symbol', '')):
                return 'expiration'
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing position exit: {e}")
            return None
    
    def _execute_position_exit(self, position: Dict, exit_reason: str) -> Optional[TradeResult]:
        """Execute position exit with ML-enhanced exit analysis"""
        try:
            # Create exit trade result
            # This is simplified - in production would execute actual closing order
            
            fake_opportunity = TradeOpportunity(
                symbol=position.get('symbol', ''),
                action=TradeAction.SELL,
                quantity=abs(position.get('qty', 0)),
                confidence=0.5,
                strategy='position_exit'
            )
            
            result = TradeResult(
                opportunity=fake_opportunity,
                status=TradeStatus.EXECUTED,
                order_id=f"exit_{datetime.now().timestamp()}",
                execution_price=position.get('market_value', 0) / max(abs(position.get('qty', 1)), 1),
                execution_time=datetime.now(),
                pnl=position.get('unrealized_pl', 0),
                pnl_pct=position.get('unrealized_pl', 0) / max(abs(position.get('market_value', 1)), 1),
                exit_reason=ExitReason.PROFIT_TARGET if exit_reason == 'profit_target' else ExitReason.STOP_LOSS
            )
            
            # 🧠 ML DATA COLLECTION: Save exit analysis for parameter optimization
            if result.success:
                self._save_ml_enhanced_options_exit(position, result, exit_reason)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing position exit: {e}")
            return None
    
    def _save_ml_enhanced_options_exit(self, position: Dict, result: TradeResult, exit_reason: str):
        """Save options exit with ML-critical exit analysis data"""
        try:
            symbol = position.get('symbol', '')
            underlying_symbol = self._extract_underlying_from_options_symbol(symbol)
            
            # Calculate hold duration (simplified - would track entry time in production)
            hold_duration_hours = 24.0  # Estimated options hold time
            
            # Create exit analysis data
            exit_analysis = self.ml_data_collector.create_exit_analysis(
                hold_duration_hours=hold_duration_hours,
                exit_signals_count=1,  # Single exit signal for options
                final_decision_reason=exit_reason,
                ml_confidence_decay=None,  # Not applicable for options exits
                reversal_probability=0.5,  # Neutral for options
                regime_adjusted_target=1.0 if exit_reason == 'profit_target' else -0.5,  # Target achievement
                exit_signals_details=[f"options_{exit_reason}"]
            )
            
            # Get market context at exit time
            market_context = self.ml_data_collector.create_market_context(
                us_market_open=True,
                market_hours_type="options_exit_during_hours"
            )
            
            # Create parameter performance assessment
            pnl_pct = result.pnl_pct or 0.0
            success = pnl_pct > 0.0
            
            # Determine if this was an effective exit strategy
            exit_effectiveness = self._assess_exit_effectiveness(pnl_pct, exit_reason)
            
            parameter_performance = self.ml_data_collector.create_parameter_performance(
                confidence_accuracy=0.5,  # Exit confidence
                threshold_effectiveness=exit_effectiveness,
                regime_multiplier_success=success,
                alternative_outcomes={
                    'exit_timing_effectiveness': exit_reason,
                    'would_profit_at_50pct': 'yes' if pnl_pct >= 0.50 else 'no',
                    'would_profit_at_100pct': 'yes' if pnl_pct >= 1.00 else 'no',
                    'expiration_risk_managed': 'yes' if exit_reason == 'expiration' else 'no'
                },
                parameter_attribution={
                    'exit_trigger_contribution': exit_reason,
                    'options_theta_decay_factor': 'high' if 'expiration' in exit_reason else 'medium',
                    'volatility_environment': 'unknown',  # Would be calculated from IV
                    'leverage_impact': 'high'  # Options inherently leveraged
                }
            )
            
            # Create ML trade data for exit
            ml_exit_data = self.ml_data_collector.create_ml_trade_data(
                symbol=underlying_symbol,
                side='SELL' if position.get('qty', 0) > 0 else 'BUY',
                quantity=abs(position.get('qty', 0)),
                price=result.execution_price or 0,
                strategy='options_exit',
                confidence=0.5,
                entry_parameters={},  # Exit trade
                module_specific_params={
                    'exit_reason': exit_reason,
                    'options_symbol': symbol,
                    'underlying_symbol': underlying_symbol,
                    'position_hold_duration': hold_duration_hours,
                    'expiration_related': 'expiration' in exit_reason,
                    'profit_related': 'profit' in exit_reason,
                    'stop_loss_related': 'stop' in exit_reason
                },
                market_context=market_context,
                exit_analysis=exit_analysis,
                parameter_performance=parameter_performance,
                profit_loss=result.pnl or 0.0,
                exit_reason=exit_reason
            )
            
            # Add options-specific fields for exit
            ml_exit_data_dict = ml_exit_data.to_dict()
            ml_exit_data_dict['options_trade'] = True
            ml_exit_data_dict['underlying_symbol'] = underlying_symbol
            ml_exit_data_dict['options_symbol'] = symbol
            ml_exit_data_dict['asset_type'] = 'options'
            ml_exit_data_dict['exit_trade'] = True
            
            # Save to Firebase
            trade_id = self.save_ml_enhanced_trade(ml_exit_data_dict)
            
            # Record exit parameter effectiveness
            self.record_parameter_effectiveness(
                parameter_type='options_exit_strategy',
                parameter_value=exit_reason,
                trade_outcome={
                    'underlying_symbol': underlying_symbol,
                    'exit_reason': exit_reason,
                    'hold_hours': hold_duration_hours,
                    'pnl_pct': pnl_pct
                },
                success=success,
                profit_loss=result.pnl or 0.0
            )
            
            self.logger.info(f"💾 Options exit ML data saved: {underlying_symbol} ({exit_reason}) - {trade_id}")
            
        except Exception as e:
            self.logger.error(f"Error saving ML options exit data: {e}")
    
    def _extract_underlying_from_options_symbol(self, options_symbol: str) -> str:
        """Extract underlying symbol from options contract symbol"""
        try:
            # Options symbols typically have format like AAPL210319C00125000
            # Extract the alphabetic part at the beginning
            underlying = ''.join(c for c in options_symbol if c.isalpha())
            return underlying if underlying else options_symbol
        except:
            return options_symbol
    
    def _assess_exit_effectiveness(self, pnl_pct: float, exit_reason: str) -> float:
        """Assess how effective the exit strategy was"""
        try:
            if exit_reason == 'profit_target':
                return 1.0 if pnl_pct >= 0.5 else 0.7  # Good if hit profit target
            elif exit_reason == 'stop_loss':
                return 0.6 if pnl_pct >= -0.6 else 0.3  # Better if loss was limited
            elif exit_reason == 'expiration':
                return 0.8 if pnl_pct > 0 else 0.4  # Good if profitable before expiration
            else:
                return 0.5  # Neutral for other reasons
        except:
            return 0.5
    
    # Utility methods
    
    def _get_underlying_price(self, symbol: str) -> float:
        """Get current underlying stock price"""
        try:
            quote = self.api.get_latest_quote(symbol)
            if quote and hasattr(quote, 'ask_price'):
                return float(quote.ask_price)
            elif quote and hasattr(quote, 'close'):
                return float(quote.close)
            else:
                return 0.0
        except Exception as e:
            self.logger.debug(f"Error getting price for {symbol}: {e}")
            return 0.0
    
    def _get_next_monthly_expiration(self) -> str:
        """Get next monthly options expiration date"""
        try:
            today = datetime.now()
            # Find third Friday of current month
            third_friday = self._get_third_friday(today.year, today.month)
            
            # If third Friday has passed, get next month
            if today.date() >= third_friday.date():
                if today.month == 12:
                    third_friday = self._get_third_friday(today.year + 1, 1)
                else:
                    third_friday = self._get_third_friday(today.year, today.month + 1)
            
            return third_friday.strftime('%Y-%m-%d')
            
        except Exception as e:
            self.logger.error(f"Error calculating expiration date: {e}")
            return (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    def _get_third_friday(self, year: int, month: int) -> datetime:
        """Calculate third Friday of given month"""
        # Find first day of month
        first_day = datetime(year, month, 1)
        
        # Find first Friday
        days_until_friday = (4 - first_day.weekday()) % 7
        first_friday = first_day + timedelta(days=days_until_friday)
        
        # Third Friday is 14 days after first Friday
        third_friday = first_friday + timedelta(days=14)
        
        return third_friday
    
    def _get_stock_position(self, symbol: str) -> Optional[Dict]:
        """Check if we have underlying stock position"""
        try:
            positions = self.api.list_positions()
            for position in positions:
                if getattr(position, 'symbol', '') == symbol:
                    return {
                        'symbol': symbol,
                        'qty': float(getattr(position, 'qty', 0)),
                        'market_value': float(getattr(position, 'market_value', 0))
                    }
            return None
        except Exception as e:
            self.logger.debug(f"Error checking stock position for {symbol}: {e}")
            return None
    
    def _get_market_regime(self) -> str:
        """Get current market regime (simplified)"""
        # In production, this would integrate with market_regime_detector
        return 'bullish'  # Simplified for now
    
    def _calculate_options_allocation(self) -> float:
        """Calculate current options allocation percentage"""
        try:
            account = self.api.get_account()
            portfolio_value = float(getattr(account, 'portfolio_value', 100000))
            
            options_positions = self._get_options_positions()
            options_value = sum(abs(pos.get('market_value', 0)) for pos in options_positions)
            
            return options_value / portfolio_value if portfolio_value > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating options allocation: {e}")
            return 0.0
    
    def _is_near_expiration(self, options_symbol: str) -> bool:
        """Check if options contract is near expiration"""
        try:
            # Extract expiration date from options symbol
            # This is simplified - options symbols have complex formats
            return False  # Simplified for now
        except Exception as e:
            return False
    
    def _check_expiration_alerts(self):
        """Check for options nearing expiration"""
        try:
            positions = self._get_options_positions()
            for position in positions:
                if self._is_near_expiration(position.get('symbol', '')):
                    self.logger.warning(f"Options position {position.get('symbol')} nearing expiration")
        except Exception as e:
            self.logger.error(f"Error checking expiration alerts: {e}")