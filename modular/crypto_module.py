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
        
        # Session-based trading configuration
        self.session_configs = {
            TradingSession.ASIA_PRIME: SessionConfig(
                strategy=CryptoStrategy.MOMENTUM,
                position_size_multiplier=1.2,
                min_confidence=0.45,
                symbol_focus='volatile'  # High volatility during Asia
            ),
            TradingSession.EUROPE_PRIME: SessionConfig(
                strategy=CryptoStrategy.BREAKOUT,
                position_size_multiplier=1.0,
                min_confidence=0.50,
                symbol_focus='defi'  # DeFi focus during Europe
            ),
            TradingSession.US_PRIME: SessionConfig(
                strategy=CryptoStrategy.REVERSAL,
                position_size_multiplier=1.1,
                min_confidence=0.40,
                symbol_focus='gaming'  # Gaming/metaverse during US
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
            
            # Get current session and active symbols
            current_session = self._get_current_trading_session()
            active_symbols = self._get_active_crypto_symbols(current_session)
            
            session_config = self.session_configs[current_session]
            self.logger.info(f"Analyzing {len(active_symbols)} cryptos for {current_session.value} session")
            
            # Analyze each active symbol
            for symbol in active_symbols:
                try:
                    analysis = self._analyze_crypto_symbol(symbol, current_session)
                    if analysis and analysis.is_tradeable:
                        # Check session-specific confidence threshold
                        if analysis.overall_confidence >= session_config.min_confidence:
                            opportunity = self._create_crypto_opportunity(analysis, session_config)
                            if opportunity:
                                opportunities.append(opportunity)
                
                except Exception as e:
                    self.logger.error(f"Error analyzing crypto {symbol}: {e}")
                    continue
            
            self.logger.info(f"Found {len(opportunities)} crypto opportunities in {current_session.value}")
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
    
    def _get_active_crypto_symbols(self, session: TradingSession) -> List[str]:
        """Get crypto symbols to trade based on current session"""
        # Always include major cryptocurrencies
        symbols = self.crypto_universe['major'].copy()
        
        # Add session-specific focus symbols
        session_config = self.session_configs[session]
        focus_category = session_config.symbol_focus
        
        if focus_category in self.crypto_universe:
            symbols.extend(self.crypto_universe[focus_category])
        
        return symbols
    
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
                                 session_config: SessionConfig) -> Optional[TradeOpportunity]:
        """Create a trade opportunity from crypto analysis"""
        try:
            # Determine trade direction based on strategy and analysis
            action = self._determine_crypto_action(analysis, session_config.strategy)
            
            # Calculate position size with session multiplier and leverage
            base_quantity = self._calculate_crypto_quantity(analysis.symbol, analysis.current_price)
            adjusted_quantity = base_quantity * session_config.position_size_multiplier * self.leverage_multiplier
            
            opportunity = TradeOpportunity(
                symbol=analysis.symbol,
                action=action,
                quantity=adjusted_quantity,
                confidence=analysis.overall_confidence,
                strategy=f"crypto_{analysis.strategy.value}",
                metadata={
                    'session': analysis.session.value,
                    'strategy': analysis.strategy.value,
                    'current_price': analysis.current_price,
                    'momentum_score': analysis.momentum_score,
                    'volatility_score': analysis.volatility_score,
                    'volume_score': analysis.volume_score,
                    'position_multiplier': session_config.position_size_multiplier,
                    'leverage': self.leverage_multiplier
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
        """Execute cryptocurrency trade"""
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
            
            if execution_result.get('success'):
                current_price = opportunity.metadata.get('current_price', 0)
                
                return TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.EXECUTED,
                    order_id=execution_result.get('order_id'),
                    execution_price=current_price,
                    execution_time=datetime.now()
                )
            else:
                return TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.FAILED,
                    error_message=execution_result.get('error', 'Unknown crypto execution error')
                )
                
        except Exception as e:
            return TradeResult(
                opportunity=opportunity,
                status=TradeStatus.FAILED,
                error_message=f"Crypto execution error: {e}"
            )
    
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
        """Execute crypto position exit"""
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
            
            # Execute exit
            result = self._execute_crypto_trade(exit_opportunity)
            
            if result.success:
                # Update with exit information
                result.pnl = position.get('unrealized_pl', 0)
                result.pnl_pct = position.get('unrealized_pl', 0) / max(abs(position.get('market_value', 1)), 1)
                result.exit_reason = self._get_exit_reason_enum(exit_reason)
                
                self.logger.info(f"Crypto exit: {symbol} {exit_reason} P&L: ${result.pnl:.2f} ({result.pnl_pct:.1%})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing crypto exit: {e}")
            return None
    
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