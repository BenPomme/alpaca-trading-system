"""
Crypto Trading Module - Modular Architecture

Standalone cryptocurrency trading module implementing 24/7 session-aware
trading strategies for the modular trading architecture. Handles global
market coverage with aggressive strategies for 5-10% monthly returns.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .base_module import (
    TradingModule, ModuleConfig, TradeOpportunity, TradeResult,
    TradeAction, TradeStatus, ExitReason
)


class TradingSession(Enum):
    """Trading session types based on global market activity"""
    ASIA_PRIME = "asia_prime"      # 00:00-08:00 UTC
    EUROPE_PRIME = "europe_prime"  # 08:00-16:00 UTC
    US_PRIME = "us_prime"          # 16:00-24:00 UTC


class CryptoStrategy(Enum):
    """Crypto trading strategies by session"""
    MOMENTUM = "momentum"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"


@dataclass
class SessionConfig:
    """Configuration for a trading session"""
    strategy: CryptoStrategy
    position_size_multiplier: float
    min_confidence: float
    symbol_focus: str  # Category from crypto universe


@dataclass
class CryptoAnalysis:
    """Cryptocurrency analysis results"""
    symbol: str
    current_price: float
    momentum_score: float
    volatility_score: float
    volume_score: float
    overall_confidence: float
    session: TradingSession
    strategy: CryptoStrategy
    
    @property
    def is_tradeable(self) -> bool:
        """Check if analysis meets minimum trading criteria"""
        return self.overall_confidence > 0.35  # Base threshold


class CryptoModule(TradingModule):
    """
    24/7 Cryptocurrency trading module with session-aware strategies.
    
    Features:
    - True 24/7 trading across global time zones
    - Session-aware strategy selection (momentum/breakout/reversal)
    - Aggressive confidence thresholds for 5-10% monthly returns
    - Dynamic symbol selection based on trading session
    - Comprehensive crypto universe coverage
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
        
        # Crypto-specific configuration
        self.max_crypto_allocation = config.custom_params.get('max_allocation_pct', 30.0) / 100
        self.leverage_multiplier = config.custom_params.get('leverage_multiplier', 1.5)
        self.volatility_threshold = config.custom_params.get('volatility_threshold', 5.0) / 100
        
        # Cryptocurrency universe organized by categories
        self.crypto_universe = {
            'major': ['BTCUSD', 'ETHUSD', 'ADAUSD', 'SOLUSD'],
            'volatile': ['DOTUSD', 'LINKUSD', 'MATICUSD', 'AVAXUSD'],
            'defi': ['UNIUSD', 'AAVEUSD', 'COMPUSD'],
            'gaming': ['MANAUSD', 'SANDUSD']
        }
        
        # 24/7 Crypto Trading Configuration - No artificial session restrictions
        self.crypto_trading_config = {
            'min_confidence': 0.35,  # Aggressive threshold for 24/7 opportunities
            'position_size_multiplier': 1.2,  # Consistent aggressive sizing
            'strategy': CryptoStrategy.MOMENTUM,  # Best performing strategy for crypto
            'analyze_all_symbols': True,  # Always analyze entire universe
            'cycle_frequency_seconds': 120  # 2-minute cycles for crypto
        }
        
        # Keep session configs for legacy compatibility but don't use for restrictions
        self.session_configs = {
            TradingSession.ASIA_PRIME: SessionConfig(
                strategy=CryptoStrategy.MOMENTUM,
                position_size_multiplier=1.2,
                min_confidence=0.35,
                symbol_focus='all'
            ),
            TradingSession.EUROPE_PRIME: SessionConfig(
                strategy=CryptoStrategy.MOMENTUM,
                position_size_multiplier=1.2,
                min_confidence=0.35,
                symbol_focus='all'
            ),
            TradingSession.US_PRIME: SessionConfig(
                strategy=CryptoStrategy.MOMENTUM,
                position_size_multiplier=1.2,
                min_confidence=0.35,
                symbol_focus='all'
            )
        }
        
        # Analysis component weights
        self.analysis_weights = {
            'momentum': 0.40,
            'volatility': 0.30,
            'volume': 0.30
        }
        
        # Performance tracking
        self._crypto_positions = {}
        self._session_performance = {session: {'trades': 0, 'wins': 0} for session in TradingSession}
        
        total_cryptos = sum(len(symbols) for symbols in self.crypto_universe.values())
        self.logger.info(f"Crypto module initialized with {total_cryptos} cryptocurrencies")
        self.logger.info(f"Max allocation: {self.max_crypto_allocation:.1%}, Leverage: {self.leverage_multiplier}x")
    
    @property
    def module_name(self) -> str:
        return "crypto"
    
    @property
    def supported_symbols(self) -> List[str]:
        """Get all supported cryptocurrency symbols"""
        all_symbols = []
        for category_symbols in self.crypto_universe.values():
            all_symbols.extend(category_symbols)
        return all_symbols
    
    def analyze_opportunities(self) -> List[TradeOpportunity]:
        """
        Analyze crypto opportunities based on current trading session.
        
        Returns:
            List of crypto trade opportunities
        """
        opportunities = []
        
        try:
            # Check current allocation to avoid over-allocation
            current_allocation = self._get_current_crypto_allocation()
            if current_allocation >= self.max_crypto_allocation:
                self.logger.info(f"Crypto allocation limit reached: {current_allocation:.1%}")
                return opportunities
            
            # Get ALL crypto symbols for 24/7 analysis
            active_symbols = self._get_active_crypto_symbols()
            
            # Get current trading session for analysis (QA.md Rule 1: Define all required variables)
            current_session = self._get_current_trading_session()
            
            # Use unified 24/7 config instead of session-specific configs
            crypto_config = self.crypto_trading_config
            self.logger.info(f"Analyzing {len(active_symbols)} cryptos for 24/7 opportunities")
            
            # Analyze each active symbol
            for symbol in active_symbols:
                try:
                    analysis = self._analyze_crypto_symbol(symbol, current_session)
                    if analysis and analysis.is_tradeable:
                        # Check 24/7 confidence threshold (no session restrictions)
                        if analysis.overall_confidence >= crypto_config['min_confidence']:
                            opportunity = self._create_crypto_opportunity(analysis, crypto_config)
                            if opportunity:
                                opportunities.append(opportunity)
                
                except Exception as e:
                    self.logger.error(f"Error analyzing crypto {symbol}: {e}")
                    continue
            
            self.logger.info(f"Found {len(opportunities)} crypto opportunities (24/7 analysis)")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error in crypto opportunity analysis: {e}")
            return opportunities
    
    def execute_trades(self, opportunities: List[TradeOpportunity]) -> List[TradeResult]:
        """
        Execute validated crypto trades.
        
        Args:
            opportunities: List of validated crypto opportunities
            
        Returns:
            List of trade execution results
        """
        results = []
        
        for opportunity in opportunities:
            try:
                result = self._execute_crypto_trade(opportunity)
                results.append(result)
                
                # Update session performance tracking
                session = TradingSession(opportunity.metadata.get('session'))
                self._session_performance[session]['trades'] += 1
                if result.success:
                    self._session_performance[session]['wins'] += 1
                
            except Exception as e:
                error_result = TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.FAILED,
                    error_message=f"Crypto execution error: {e}"
                )
                results.append(error_result)
                self.logger.error(f"Failed to execute crypto trade {opportunity.symbol}: {e}")
        
        return results
    
    def monitor_positions(self) -> List[TradeResult]:
        """
        Monitor existing crypto positions for exit opportunities.
        
        Returns:
            List of exit trade results
        """
        exit_results = []
        
        try:
            # Get current crypto positions
            positions = self._get_crypto_positions()
            
            for position in positions:
                try:
                    exit_signal = self._analyze_crypto_exit(position)
                    if exit_signal:
                        exit_result = self._execute_crypto_exit(position, exit_signal)
                        if exit_result:
                            exit_results.append(exit_result)
                
                except Exception as e:
                    self.logger.error(f"Error monitoring crypto position {position.get('symbol', 'unknown')}: {e}")
            
            # Log session performance periodically
            if len(positions) > 0:
                self._log_session_performance()
                
        except Exception as e:
            self.logger.error(f"Error monitoring crypto positions: {e}")
        
        return exit_results
    
    # Session management methods
    
    def _get_current_trading_session(self) -> TradingSession:
        """Determine current trading session based on UTC time"""
        hour_utc = datetime.now(timezone.utc).hour
        
        if 0 <= hour_utc < 8:
            return TradingSession.ASIA_PRIME
        elif 8 <= hour_utc < 16:
            return TradingSession.EUROPE_PRIME
        else:
            return TradingSession.US_PRIME
    
    def _get_active_crypto_symbols(self, session: TradingSession = None) -> List[str]:
        """Get ALL crypto symbols for 24/7 trading - no artificial session restrictions"""
        # TRUE 24/7 CRYPTO TRADING: Always analyze ENTIRE universe
        symbols = []
        
        # Include ALL categories - crypto markets never close
        for category_symbols in self.crypto_universe.values():
            symbols.extend(category_symbols)
        
        # No session-based filtering - we want maximum opportunities 24/7
        # Sort by liquidity (major coins first for better execution)
        major_cryptos = self.crypto_universe['major']
        other_cryptos = [s for s in symbols if s not in major_cryptos]
        
        return major_cryptos + other_cryptos
    
    # Analysis methods
    
    def _analyze_crypto_symbol(self, symbol: str, session: TradingSession) -> Optional[CryptoAnalysis]:
        """Perform comprehensive analysis of a cryptocurrency"""
        try:
            # Get current price and market data
            current_price = self._get_crypto_price(symbol)
            if not current_price or current_price <= 0:
                return None
            
            # Get historical data for analysis (simplified - would integrate with real data)
            market_data = self._get_crypto_market_data(symbol)
            if not market_data:
                return None
            
            # Calculate analysis components
            momentum_score = self._calculate_crypto_momentum(symbol, market_data)
            volatility_score = self._calculate_crypto_volatility(symbol, market_data)
            volume_score = self._calculate_crypto_volume(symbol, market_data)
            
            # Calculate overall confidence using weighted scoring
            overall_confidence = (
                momentum_score * self.analysis_weights['momentum'] +
                volatility_score * self.analysis_weights['volatility'] +
                volume_score * self.analysis_weights['volume']
            )
            
            session_config = self.session_configs[session]
            
            return CryptoAnalysis(
                symbol=symbol,
                current_price=current_price,
                momentum_score=momentum_score,
                volatility_score=volatility_score,
                volume_score=volume_score,
                overall_confidence=overall_confidence,
                session=session,
                strategy=session_config.strategy
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing crypto symbol {symbol}: {e}")
            return None
    
    def _calculate_crypto_momentum(self, symbol: str, market_data: Dict) -> float:
        """Calculate momentum score for cryptocurrency"""
        try:
            # Simplified momentum calculation
            price_24h_ago = market_data.get('price_24h_ago', market_data.get('current_price', 0))
            current_price = market_data.get('current_price', 0)
            
            if price_24h_ago <= 0:
                return 0.5  # Neutral if no historical data
            
            price_change_pct = (current_price - price_24h_ago) / price_24h_ago
            
            # Convert to 0-1 score (0.5 = neutral, >0.5 = positive momentum)
            momentum_score = 0.5 + (price_change_pct * 5)  # Scale by 5 for sensitivity
            
            # Clamp to 0-1 range
            return max(0.0, min(1.0, momentum_score))
            
        except Exception as e:
            self.logger.debug(f"Error calculating momentum for {symbol}: {e}")
            return 0.5
    
    def _calculate_crypto_volatility(self, symbol: str, market_data: Dict) -> float:
        """Calculate volatility score for cryptocurrency"""
        try:
            # Simplified volatility calculation using daily range
            high_24h = market_data.get('high_24h', 0)
            low_24h = market_data.get('low_24h', 0)
            current_price = market_data.get('current_price', 0)
            
            if current_price <= 0 or high_24h <= low_24h:
                return 0.3  # Low volatility default
            
            daily_range = (high_24h - low_24h) / current_price
            
            # Score volatility (higher volatility = higher score up to threshold)
            volatility_score = min(daily_range / self.volatility_threshold, 1.0)
            
            return volatility_score
            
        except Exception as e:
            self.logger.debug(f"Error calculating volatility for {symbol}: {e}")
            return 0.3
    
    def _calculate_crypto_volume(self, symbol: str, market_data: Dict) -> float:
        """Calculate volume score for cryptocurrency"""
        try:
            # Simplified volume analysis
            volume_24h = market_data.get('volume_24h', 0)
            avg_volume = market_data.get('avg_volume_7d', volume_24h)
            
            if avg_volume <= 0:
                return 0.4  # Default volume score
            
            volume_ratio = volume_24h / avg_volume
            
            # Higher than average volume = higher score
            volume_score = min(volume_ratio, 2.0) / 2.0  # Normalize to 0-1
            
            return volume_score
            
        except Exception as e:
            self.logger.debug(f"Error calculating volume for {symbol}: {e}")
            return 0.4
    
    def _create_crypto_opportunity(self, analysis: CryptoAnalysis, 
                                 crypto_config: Dict[str, Any]) -> Optional[TradeOpportunity]:
        """Create a trade opportunity from crypto analysis"""
        try:
            # Determine trade direction - use momentum strategy for all crypto
            action = self._determine_crypto_action(analysis, crypto_config['strategy'])
            
            # Calculate position size with consistent 24/7 multiplier and leverage
            base_quantity = self._calculate_crypto_quantity(analysis.symbol, analysis.current_price)
            adjusted_quantity = base_quantity * crypto_config['position_size_multiplier'] * self.leverage_multiplier
            
            opportunity = TradeOpportunity(
                symbol=analysis.symbol,
                action=action,
                quantity=adjusted_quantity,
                confidence=analysis.overall_confidence,
                strategy=f"crypto_{analysis.strategy.value}",
                metadata={
                    'session': analysis.session.value,  # For logging only
                    'strategy': crypto_config['strategy'].value,
                    'current_price': analysis.current_price,
                    'momentum_score': analysis.momentum_score,
                    'volatility_score': analysis.volatility_score,
                    'volume_score': analysis.volume_score,
                    'position_multiplier': crypto_config['position_size_multiplier'],
                    'leverage': self.leverage_multiplier,
                    'trading_mode': '24_7_continuous'
                },
                technical_score=analysis.momentum_score,
                regime_score=analysis.volatility_score,
                pattern_score=analysis.volume_score,
                ml_score=analysis.overall_confidence,
                max_position_size=adjusted_quantity * analysis.current_price,
                stop_loss_pct=0.15,  # 15% stop loss for crypto
                profit_target_pct=0.25  # 25% profit target
            )
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error creating crypto opportunity: {e}")
            return None
    
    def _determine_crypto_action(self, analysis: CryptoAnalysis, strategy: CryptoStrategy) -> TradeAction:
        """Determine buy/sell action based on analysis and strategy"""
        if strategy == CryptoStrategy.MOMENTUM:
            # Momentum strategy: follow the trend
            return TradeAction.BUY if analysis.momentum_score > 0.5 else TradeAction.SELL
        
        elif strategy == CryptoStrategy.BREAKOUT:
            # Breakout strategy: high volatility + momentum
            if analysis.volatility_score > 0.6 and analysis.momentum_score > 0.55:
                return TradeAction.BUY
            else:
                return TradeAction.SELL
        
        elif strategy == CryptoStrategy.REVERSAL:
            # Reversal strategy: contrarian approach
            return TradeAction.SELL if analysis.momentum_score > 0.7 else TradeAction.BUY
        
        else:
            # Default to momentum
            return TradeAction.BUY if analysis.momentum_score > 0.5 else TradeAction.SELL
    
    # Execution methods
    
    def _execute_crypto_trade(self, opportunity: TradeOpportunity) -> TradeResult:
        """Execute cryptocurrency trade with ML-critical parameter data collection"""
        try:
            # Prepare order data for crypto
            order_data = {
                'symbol': opportunity.symbol,
                'qty': opportunity.quantity,
                'side': 'buy' if opportunity.action == TradeAction.BUY else 'sell',
                'type': 'market',
                'time_in_force': 'gtc'  # Good til cancelled for crypto
            }
            
            # Execute via injected order executor
            execution_result = self.order_executor.execute_order(order_data)
            
            # Create trade result
            result = None
            if execution_result.get('success'):
                current_price = opportunity.metadata.get('current_price', 0)
                
                result = TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.EXECUTED,
                    order_id=execution_result.get('order_id'),
                    execution_price=current_price,
                    execution_time=datetime.now()
                )
            else:
                result = TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.FAILED,
                    error_message=execution_result.get('error', 'Unknown crypto execution error')
                )
            
            # 🧠 ML DATA COLLECTION: Save trade with enhanced parameter context
            if result.success:
                self._save_ml_enhanced_crypto_trade(opportunity, result)
            
            return result
                
        except Exception as e:
            return TradeResult(
                opportunity=opportunity,
                status=TradeStatus.FAILED,
                error_message=f"Crypto execution error: {e}"
            )
    
    def _save_ml_enhanced_crypto_trade(self, opportunity: TradeOpportunity, result: TradeResult):
        """Save crypto trade with ML-critical parameter data for optimization"""
        try:
            # Get current session context for ML analysis
            current_session = self._get_current_trading_session()
            session_config = self.session_configs[current_session]
            
            # Create entry parameters for ML learning
            entry_parameters = self.ml_data_collector.create_entry_parameters(
                confidence_threshold_used=session_config.min_confidence,
                position_size_multiplier=session_config.position_size_multiplier * self.leverage_multiplier,
                regime_confidence=opportunity.regime_score,
                technical_confidence=opportunity.technical_score,
                pattern_confidence=opportunity.pattern_score,
                ml_strategy_selection=True,
                leverage_applied=self.leverage_multiplier,
                session_strategy=session_config.strategy.value
            )
            
            # Create crypto-specific module parameters
            module_specific_params = self.ml_data_collector.create_crypto_module_params(
                crypto_session=current_session.value,
                volatility_score=opportunity.metadata.get('volatility_score', 0),
                momentum_score=opportunity.metadata.get('momentum_score', 0),
                volume_score=opportunity.metadata.get('volume_score', 0),
                session_multiplier=session_config.position_size_multiplier,
                analysis_weights=self.analysis_weights,
                strategy_applied=session_config.strategy.value,
                focus_category=session_config.symbol_focus,
                base_allocation_pct=2.0,  # 2% base allocation
                max_crypto_allocation_pct=self.max_crypto_allocation * 100
            )
            
            # Create market context
            market_context = self.ml_data_collector.create_market_context(
                us_market_open=False,  # Crypto trades 24/7
                crypto_session=current_session.value,
                cycle_delay_used=600 if current_session != TradingSession.US_PRIME else 120,
                global_trading_active=True,
                market_hours_type="crypto_24_7"
            )
            
            # Create parameter performance context
            parameter_performance = self.ml_data_collector.create_parameter_performance(
                confidence_accuracy=opportunity.confidence,
                threshold_effectiveness=1.0 if opportunity.confidence >= session_config.min_confidence else 0.0,
                regime_multiplier_success=True,  # Session multiplier was applied
                alternative_outcomes={
                    'threshold_0_40': 'would_have_triggered' if opportunity.confidence >= 0.40 else 'would_not_have_triggered',
                    'threshold_0_50': 'would_have_triggered' if opportunity.confidence >= 0.50 else 'would_not_have_triggered',
                    'threshold_0_60': 'would_have_triggered' if opportunity.confidence >= 0.60 else 'would_not_have_triggered'
                },
                parameter_attribution={
                    'session_threshold_contribution': session_config.min_confidence,
                    'leverage_contribution': self.leverage_multiplier,
                    'momentum_weight_contribution': self.analysis_weights['momentum'],
                    'volatility_weight_contribution': self.analysis_weights['volatility'],
                    'volume_weight_contribution': self.analysis_weights['volume']
                }
            )
            
            # Create complete ML trade data
            ml_trade_data = self.ml_data_collector.create_ml_trade_data(
                symbol=opportunity.symbol,
                side='BUY' if opportunity.action == TradeAction.BUY else 'SELL',
                quantity=opportunity.quantity,
                price=result.execution_price or opportunity.metadata.get('current_price', 0),
                strategy=opportunity.strategy,
                confidence=opportunity.confidence,
                entry_parameters=entry_parameters,
                module_specific_params=module_specific_params,
                market_context=market_context,
                parameter_performance=parameter_performance,
                profit_loss=0.0,  # Will be updated on exit
                exit_reason=None  # Entry trade
            )
            
            # Save to Firebase with ML enhancements
            trade_id = self.save_ml_enhanced_trade(ml_trade_data.to_dict())
            
            # Record parameter effectiveness for ML optimization
            self.record_parameter_effectiveness(
                parameter_type='crypto_confidence_threshold',
                parameter_value=session_config.min_confidence,
                trade_outcome={
                    'symbol': opportunity.symbol,
                    'strategy': opportunity.strategy,
                    'session': current_session.value,
                    'executed': result.success
                },
                success=result.success,
                profit_loss=0.0  # Will be updated on exit
            )
            
            self.logger.info(f"💾 Crypto ML data saved: {opportunity.symbol} ({current_session.value}) - {trade_id}")
            
        except Exception as e:
            self.logger.error(f"Error saving ML crypto trade data: {e}")
    
    # Position monitoring methods
    
    def _get_crypto_positions(self) -> List[Dict]:
        """Get current cryptocurrency positions"""
        try:
            positions = self.api.list_positions()
            crypto_positions = []
            
            for position in positions:
                symbol = getattr(position, 'symbol', '')
                # Check if it's a crypto symbol (contains USD and is in our universe)
                if 'USD' in symbol and symbol in self.supported_symbols:
                    qty = getattr(position, 'qty', 0)
                    market_value = getattr(position, 'market_value', 0)
                    avg_entry_price = getattr(position, 'avg_entry_price', 0)
                    unrealized_pl = getattr(position, 'unrealized_pl', 0)
                    
                    crypto_positions.append({
                        'symbol': symbol,
                        'qty': float(qty) if str(qty).replace('-', '').replace('.', '').isdigit() else 0.0,
                        'market_value': float(market_value) if str(market_value).replace('-', '').replace('.', '').isdigit() else 0.0,
                        'avg_entry_price': float(avg_entry_price) if str(avg_entry_price).replace('-', '').replace('.', '').isdigit() else 0.0,
                        'unrealized_pl': float(unrealized_pl) if str(unrealized_pl).replace('-', '').replace('.', '').isdigit() else 0.0
                    })
            
            return crypto_positions
            
        except Exception as e:
            self.logger.error(f"Error getting crypto positions: {e}")
            return []
    
    def _analyze_crypto_exit(self, position: Dict) -> Optional[str]:
        """Analyze if crypto position should be exited"""
        try:
            unrealized_pl = position.get('unrealized_pl', 0)
            market_value = abs(position.get('market_value', 1))
            
            if market_value == 0:
                return None
            
            unrealized_pl_pct = unrealized_pl / market_value
            
            # Crypto-specific exit conditions (more aggressive than traditional assets)
            if unrealized_pl_pct >= 0.25:  # 25% profit target
                return 'profit_target'
            elif unrealized_pl_pct <= -0.15:  # 15% stop loss
                return 'stop_loss'
            
            # Session-based exits (simplified)
            current_session = self._get_current_trading_session()
            if current_session != self._infer_position_session(position):
                # Consider exit if session changed and position is profitable
                if unrealized_pl_pct > 0.10:  # 10% profit in different session
                    return 'session_change'
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing crypto exit: {e}")
            return None
    
    def _execute_crypto_exit(self, position: Dict, exit_reason: str) -> Optional[TradeResult]:
        """Execute crypto position exit with ML-enhanced exit analysis"""
        try:
            symbol = position.get('symbol', '')
            qty = abs(position.get('qty', 0))
            
            if qty == 0:
                return None
            
            # Create exit opportunity
            exit_opportunity = TradeOpportunity(
                symbol=symbol,
                action=TradeAction.SELL if position.get('qty', 0) > 0 else TradeAction.BUY,
                quantity=qty,
                confidence=0.6,  # Medium confidence for exits
                strategy='crypto_exit'
            )
            
            # Execute exit (without saving ML data for exit trades - handled separately)
            order_data = {
                'symbol': symbol,
                'qty': qty,
                'side': 'sell' if position.get('qty', 0) > 0 else 'buy',
                'type': 'market',
                'time_in_force': 'gtc'
            }
            
            execution_result = self.order_executor.execute_order(order_data)
            
            if execution_result.get('success'):
                # Create exit result with P&L information
                result = TradeResult(
                    opportunity=exit_opportunity,
                    status=TradeStatus.EXECUTED,
                    order_id=execution_result.get('order_id'),
                    execution_price=self._get_crypto_price(symbol),
                    execution_time=datetime.now(),
                    pnl=position.get('unrealized_pl', 0),
                    pnl_pct=position.get('unrealized_pl', 0) / max(abs(position.get('market_value', 1)), 1),
                    exit_reason=self._get_exit_reason_enum(exit_reason)
                )
                
                # 🧠 ML DATA COLLECTION: Save exit analysis for parameter optimization
                self._save_ml_enhanced_crypto_exit(position, result, exit_reason)
                
                self.logger.info(f"💰 Crypto exit: {symbol} {exit_reason} P&L: ${result.pnl:.2f} ({result.pnl_pct:.1%})")
                return result
            else:
                return TradeResult(
                    opportunity=exit_opportunity,
                    status=TradeStatus.FAILED,
                    error_message=execution_result.get('error', 'Exit execution failed')
                )
            
        except Exception as e:
            self.logger.error(f"Error executing crypto exit: {e}")
            return None
    
    def _save_ml_enhanced_crypto_exit(self, position: Dict, result: TradeResult, exit_reason: str):
        """Save crypto exit with ML-critical exit analysis data"""
        try:
            symbol = position.get('symbol', '')
            current_session = self._get_current_trading_session()
            
            # Calculate hold duration (simplified - would track entry time in production)
            hold_duration_hours = 4.0  # Estimated crypto hold time
            
            # Create exit analysis data
            exit_analysis = self.ml_data_collector.create_exit_analysis(
                hold_duration_hours=hold_duration_hours,
                exit_signals_count=1,  # Single exit signal for crypto
                final_decision_reason=exit_reason,
                ml_confidence_decay=None,  # Not applicable for crypto exits
                reversal_probability=0.5,  # Neutral for crypto
                regime_adjusted_target=0.25,  # 25% crypto profit target
                exit_signals_details=[f"crypto_{exit_reason}"]
            )
            
            # Get market context at exit time
            market_context = self.ml_data_collector.create_market_context(
                us_market_open=False,
                crypto_session=current_session.value,
                market_hours_type="crypto_24_7_exit"
            )
            
            # Create parameter performance assessment
            pnl_pct = result.pnl_pct or 0.0
            success = pnl_pct > 0.0
            
            parameter_performance = self.ml_data_collector.create_parameter_performance(
                confidence_accuracy=0.6,  # Exit confidence
                threshold_effectiveness=1.0 if success else 0.0,
                regime_multiplier_success=success,
                alternative_outcomes={
                    'exit_reason_effectiveness': exit_reason,
                    'would_profit_at_10pct': 'yes' if pnl_pct >= 0.10 else 'no',
                    'would_profit_at_15pct': 'yes' if pnl_pct >= 0.15 else 'no',
                    'would_profit_at_25pct': 'yes' if pnl_pct >= 0.25 else 'no'
                },
                parameter_attribution={
                    'exit_trigger_contribution': exit_reason,
                    'session_exit_timing': current_session.value,
                    'crypto_volatility_factor': 'high'
                }
            )
            
            # Create ML trade data for exit
            ml_exit_data = self.ml_data_collector.create_ml_trade_data(
                symbol=symbol,
                side='SELL' if position.get('qty', 0) > 0 else 'BUY',
                quantity=abs(position.get('qty', 0)),
                price=result.execution_price or 0,
                strategy='crypto_exit',
                confidence=0.6,
                entry_parameters={},  # Exit trade
                module_specific_params={
                    'exit_reason': exit_reason,
                    'session_at_exit': current_session.value,
                    'position_hold_duration': hold_duration_hours
                },
                market_context=market_context,
                exit_analysis=exit_analysis,
                parameter_performance=parameter_performance,
                profit_loss=result.pnl or 0.0,
                exit_reason=exit_reason
            )
            
            # Save to Firebase
            trade_id = self.save_ml_enhanced_trade(ml_exit_data.to_dict())
            
            # Record exit parameter effectiveness
            self.record_parameter_effectiveness(
                parameter_type='crypto_exit_threshold',
                parameter_value=exit_reason,
                trade_outcome={
                    'symbol': symbol,
                    'exit_reason': exit_reason,
                    'session': current_session.value,
                    'hold_hours': hold_duration_hours
                },
                success=success,
                profit_loss=result.pnl or 0.0
            )
            
            self.logger.info(f"💾 Crypto exit ML data saved: {symbol} ({exit_reason}) - {trade_id}")
            
        except Exception as e:
            self.logger.error(f"Error saving ML crypto exit data: {e}")
    
    # Utility methods
    
    def _get_crypto_price(self, symbol: str) -> float:
        """Get current cryptocurrency price with fallbacks"""
        try:
            # Use standard quote method for crypto (most APIs handle this uniformly)
            quote = self.api.get_latest_quote(symbol)
            
            if quote:
                # Try different price attributes
                for attr in ['ask_price', 'bid_price', 'close', 'price']:
                    if hasattr(quote, attr):
                        price_value = getattr(quote, attr)
                        try:
                            if price_value is not None:
                                price_float = float(price_value)
                                if price_float > 0:
                                    return price_float
                        except (ValueError, TypeError):
                            continue
            
            return 0.0
                
        except Exception as e:
            self.logger.debug(f"Error getting crypto price for {symbol}: {e}")
            return 0.0
    
    def _get_crypto_market_data(self, symbol: str) -> Optional[Dict]:
        """Get cryptocurrency market data for analysis"""
        try:
            current_price = self._get_crypto_price(symbol)
            if not current_price:
                return None
            
            # Simplified market data - in production would get real historical data
            return {
                'current_price': current_price,
                'price_24h_ago': current_price * 0.98,  # Simplified
                'high_24h': current_price * 1.05,
                'low_24h': current_price * 0.95,
                'volume_24h': 1000000,  # Simplified
                'avg_volume_7d': 800000  # Simplified
            }
            
        except Exception as e:
            self.logger.debug(f"Error getting market data for {symbol}: {e}")
            return None
    
    def _calculate_crypto_quantity(self, symbol: str, price: float) -> float:
        """Calculate crypto quantity based on portfolio allocation"""
        try:
            account = self.api.get_account()
            portfolio_value = float(getattr(account, 'portfolio_value', 100000))
            
            # Calculate position size as percentage of portfolio
            base_allocation = 0.02  # 2% base allocation per crypto trade
            max_position_value = portfolio_value * base_allocation
            
            # Calculate quantity (fractional for crypto)
            quantity = max_position_value / price if price > 0 else 0
            
            return quantity
            
        except Exception as e:
            self.logger.error(f"Error calculating crypto quantity: {e}")
            return 0.0
    
    def _get_current_crypto_allocation(self) -> float:
        """Get current cryptocurrency allocation percentage"""
        try:
            account = self.api.get_account()
            portfolio_value = float(getattr(account, 'portfolio_value', 100000))
            
            crypto_positions = self._get_crypto_positions()
            crypto_value = sum(abs(pos.get('market_value', 0)) for pos in crypto_positions)
            
            return crypto_value / portfolio_value if portfolio_value > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating crypto allocation: {e}")
            return 0.0
    
    def _infer_position_session(self, position: Dict) -> TradingSession:
        """Infer which session a position was likely opened in (simplified)"""
        # In production, would track this metadata
        return self._get_current_trading_session()
    
    def _get_exit_reason_enum(self, exit_reason: str) -> ExitReason:
        """Convert exit reason string to enum"""
        mapping = {
            'profit_target': ExitReason.PROFIT_TARGET,
            'stop_loss': ExitReason.STOP_LOSS,
            'session_change': ExitReason.STRATEGY_SIGNAL
        }
        return mapping.get(exit_reason, ExitReason.STRATEGY_SIGNAL)
    
    def _log_session_performance(self):
        """Log session-based performance metrics"""
        try:
            current_session = self._get_current_trading_session()
            session_stats = self._session_performance[current_session]
            
            if session_stats['trades'] > 0:
                win_rate = session_stats['wins'] / session_stats['trades']
                self.logger.info(f"Session {current_session.value}: {session_stats['trades']} trades, "
                               f"{win_rate:.1%} win rate")
                
        except Exception as e:
            self.logger.debug(f"Error logging session performance: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get current session information and performance"""
        current_session = self._get_current_trading_session()
        session_config = self.session_configs[current_session]
        active_symbols = self._get_active_crypto_symbols(current_session)
        
        return {
            'current_session': current_session.value,
            'strategy': session_config.strategy.value,
            'min_confidence': session_config.min_confidence,
            'position_multiplier': session_config.position_size_multiplier,
            'active_symbols': active_symbols,
            'symbol_count': len(active_symbols),
            'focus_category': session_config.symbol_focus,
            'session_performance': dict(self._session_performance)
        }