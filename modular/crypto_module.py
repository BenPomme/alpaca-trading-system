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
import time
import dataclasses

from modular.base_module import (
    TradingModule, ModuleConfig, TradeOpportunity, TradeResult,
    TradeAction, TradeStatus, ExitReason
)
from utils.technical_indicators import TechnicalIndicators
from utils.pattern_recognition import PatternRecognition


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
        
        # SMART LEVERAGE SYSTEM FOR 5% MONTHLY ROI
        self.base_crypto_allocation = 0.40  # Target 40% for 5% monthly ROI (balanced performance)
        self.emergency_allocation = 0.20    # Emergency mode if losing money
        self.max_profitable_allocation = 0.60  # Maximum when performing well
        self.leverage_multiplier = 2.0      # Smart leverage for 5% monthly target
        self.smart_allocation_enabled = True
        self.volatility_threshold = config.custom_params.get('volatility_threshold', 5.0) / 100
        
        # Cryptocurrency universe organized by categories (only Alpaca-supported cryptos)
        self.crypto_universe = {
            'major': ['BTCUSD', 'ETHUSD', 'SOLUSD'],  # Removed ADAUSD (not supported)
            'volatile': ['DOTUSD', 'LINKUSD', 'MATICUSD', 'AVAXUSD'],
            'defi': ['UNIUSD', 'AAVEUSD'],  # Removed COMPUSD (not supported)
            # Removed 'gaming' category (MANAUSD, SANDUSD not supported by Alpaca Paper API)
        }
        
        # INSTITUTIONAL CRYPTO STRATEGY - Research-backed mean reversion
        self.crypto_trading_config = {
            'min_confidence': 0.60,  # Higher threshold based on research
            'position_size_multiplier': 0.8,  # Conservative sizing with proper risk management
            'strategy': CryptoStrategy.MOMENTUM,  # Momentum strategy for crypto entries
            'analyze_all_symbols': False,  # Focus on top 3 cryptos for concentration
            'cycle_frequency_seconds': 3600,  # Hourly cycles (not intraday scalping)
            'stop_loss_pct': 0.07,  # 7% stop loss (tighter risk control)
            'profit_target_pct': 0.25,  # Increased to 25% profit target for larger mean reversion captures
            'oversold_threshold': -0.20,  # Buy on 20%+ dips from moving average
            'moving_average_period': 20  # 20-day MA for mean reversion reference
        }
        
        # Keep session configs for legacy compatibility but don't use for restrictions
        self.session_configs = {
            TradingSession.ASIA_PRIME: SessionConfig(
                strategy=CryptoStrategy.REVERSAL,
                position_size_multiplier=1.2,
                min_confidence=0.35,
                symbol_focus='all'
            ),
            TradingSession.EUROPE_PRIME: SessionConfig(
                strategy=CryptoStrategy.REVERSAL,
                position_size_multiplier=1.2,
                min_confidence=0.35,
                symbol_focus='all'
            ),
            TradingSession.US_PRIME: SessionConfig(
                strategy=CryptoStrategy.REVERSAL,
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
        
        # Performance tracking - REAL profitability metrics
        self._crypto_positions = {}
        # EMERGENCY FIX: Clear any stale position data on initialization
        self._clear_stale_position_data()
        self._session_performance = {
            session: {
                'total_trades': 0,
                'profitable_trades': 0,
                'total_pnl': 0.0,
                'total_invested': 0.0,
                'avg_profit_per_trade': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'roi': 0.0
            } for session in TradingSession
        }
        
        # Define missing attributes for compatibility
        self.max_crypto_allocation = self.base_crypto_allocation  # Default to base allocation
        self.after_hours_max_allocation = 0.90  # 90% for after hours aggressive trading
        self.after_hours_leverage = 1.5  # EMERGENCY FIX: Reduced from 3.5x to 1.5x to limit losses
        
        total_cryptos = sum(len(symbols) for symbols in self.crypto_universe.values())
        self.logger.info(f"Crypto module initialized with {total_cryptos} cryptocurrencies")
        self.logger.info(f"Smart allocation range: {self.emergency_allocation:.1%}-{self.max_profitable_allocation:.1%}, Leverage: {self.leverage_multiplier}x")
    
    def _clear_stale_position_data(self):
        """EMERGENCY FIX: Clear all stale internal position tracking data"""
        try:
            self._crypto_positions.clear()
            self.logger.info("🧹 EMERGENCY: Cleared all stale internal position data")
            
            # Also clear any file-based position tracking if it exists
            import os
            stale_files = ['data/crypto_positions.json', 'crypto_positions.db', 'positions.cache']
            for filename in stale_files:
                if os.path.exists(filename):
                    os.remove(filename)
                    self.logger.info(f"🧹 EMERGENCY: Removed stale position file: {filename}")
                    
        except Exception as e:
            self.logger.error(f"Error clearing stale position data: {e}")
    
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
            # SMART ALLOCATION CONTROL FOR 5% MONTHLY ROI TARGET
            current_allocation = self._get_current_crypto_allocation()
            session_type = "AFTER-HOURS" if not self._is_stock_market_open() else "MARKET HOURS"
            
            # Get smart allocation limit based on performance
            smart_allocation_limit = self._get_smart_allocation_limit()
            
            # Check current allocation vs smart limit
            portfolio_summary = self.risk_manager.get_portfolio_summary() if self.risk_manager else {}
            portfolio_value = portfolio_summary.get('portfolio_value', 100000)
            current_crypto_value = current_allocation * portfolio_value
            
            if current_allocation >= smart_allocation_limit:
                self.logger.warning(f"🎯 SMART ALLOCATION LIMIT: {current_allocation:.1%} >= {smart_allocation_limit:.1%} - optimizing for 5% monthly ROI")
                self.logger.info(f"💡 PERFORMANCE MODE: Current allocation ${current_crypto_value:,.0f} optimized for risk-adjusted returns")
                
                # Don't completely stop - allow high-confidence opportunities for rebalancing
                if current_allocation >= smart_allocation_limit * 1.2:  # 20% buffer
                    self.logger.warning(f"🚨 ALLOCATION EXCEEDED: {current_allocation:.1%} > {smart_allocation_limit*1.2:.1%} - PAUSING new entries")
                    return opportunities
            
            # Log current status without arbitrary limits
            self.logger.info(f"💰 CRYPTO STATUS ({session_type}): {current_allocation:.1%} allocation, "
                           f"${current_crypto_value:,.0f} exposure - Looking for quality opportunities")
            
            # Get ALL crypto symbols for 24/7 analysis
            active_symbols = self._get_active_crypto_symbols()
            
            # Get current trading session for analysis (QA.md Rule 1: Define all required variables)
            current_session = self._get_current_trading_session()
            
            # Use unified 24/7 config instead of session-specific configs
            crypto_config = self.crypto_trading_config
            self.logger.info(f"Analyzing {len(active_symbols)} cryptos for 24/7 opportunities")
            self.logger.info(f"🎯 Confidence threshold: {crypto_config['min_confidence']:.2f}, Session: {current_session.value}")
            
            # Analyze each active symbol
            for symbol in active_symbols:
                try:
                    # Add stale data check before analysis
                    if self._is_quote_data_stale(symbol):
                        self.logger.warning(f"⚠️ {symbol}: Skipping due to stale quote data")
                        continue

                    analysis = self._analyze_crypto_symbol(symbol, current_session)
                    
                    if analysis:
                        # Log detailed analysis results for debugging
                        self.logger.info(f"📊 {symbol}: confidence={analysis.overall_confidence:.2f}, "
                                       f"tradeable={analysis.is_tradeable}, "
                                       f"momentum={analysis.momentum_score:.2f}, "
                                       f"volatility={analysis.volatility_score:.2f}")
                        
                        if analysis.is_tradeable:
                            # Check 24/7 confidence threshold (no session restrictions)
                            if analysis.overall_confidence >= crypto_config['min_confidence']:
                                opportunity = self._create_crypto_opportunity(analysis, crypto_config)
                                if opportunity:
                                    opportunities.append(opportunity)
                                    self.logger.info(f"✅ {symbol}: OPPORTUNITY CREATED (confidence={analysis.overall_confidence:.2f})")
                                else:
                                    self.logger.info(f"⚠️ {symbol}: opportunity creation failed despite good confidence")
                            else:
                                self.logger.info(f"❌ {symbol}: confidence {analysis.overall_confidence:.2f} < threshold {crypto_config['min_confidence']}")
                        else:
                            self.logger.debug(f"❌ {symbol}: not tradeable (confidence={analysis.overall_confidence:.2f})")
                    else:
                        self.logger.warning(f"❌ {symbol}: analysis returned None - check market data quality")
                
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
                
                # Update session performance tracking with REAL metrics
                session = TradingSession(opportunity.metadata.get('session'))
                session_stats = self._session_performance[session]
                session_stats['total_trades'] += 1
                
                if result.success:
                    # Track actual investment amount
                    investment_amount = opportunity.quantity * (result.execution_price or opportunity.metadata.get('current_price', 0))
                    session_stats['total_invested'] += investment_amount
                    
                    # Store entry data for later exit calculation
                    ml_trade_id = getattr(result, 'metadata', {}).get('ml_trade_id', None)
                    self._crypto_positions[opportunity.symbol] = {
                        'entry_price': result.execution_price,
                        'quantity': opportunity.quantity,
                        'investment': investment_amount,
                        'session': session.value,
                        'entry_time': datetime.now().isoformat(),
                        'entry_trade_id': ml_trade_id  # Link to ML entry trade for profit updates
                    }
                
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
            
            # Check if we should close positions before market opens (CRITICAL for strategy)
            if self._should_close_positions_before_market_open() and positions:
                self.logger.warning(f"🚨 PRE-MARKET CLOSURE: Closing {len(positions)} crypto positions before market opens")
                for position in positions:
                    symbol = position.get('symbol', 'unknown')
                    self.logger.info(f"⏰ FORCED CLOSURE: {symbol} - preparing for stock market session")
                    exit_result = self._execute_crypto_exit(position, "pre_market_closure")
                    if exit_result:
                        exit_results.append(exit_result)
                return exit_results
            
            if len(positions) > 0:
                allocation = self._get_current_crypto_allocation()
                max_allocation = self._get_max_allocation_for_current_session()
                # Automatically trim worst positions if allocation far above smart limit
                smart_limit = self._get_smart_allocation_limit()
                if allocation > smart_limit * 1.2:
                    self.logger.warning(f"🚨 OVER-ALLOCATION: {allocation:.1%} > {smart_limit*1.2:.1%} – commencing auto-rebalancing exits")
                    # Sort by unrealised P&L (worst first) and close until within limit
                    try:
                        sorted_positions = sorted(positions, key=lambda p: p.get('unrealized_pl', 0))
                        for pos in sorted_positions:
                            if self._get_current_crypto_allocation() <= smart_limit:
                                break
                            sym = pos.get('symbol', 'unknown')
                            self.logger.info(f"🔻 REBALANCE EXIT: {sym} UPL {pos.get('unrealized_pl',0):.2f}")
                            try:
                                reb_res = self._execute_crypto_exit(pos, 'over_allocation_rebalance')
                                if reb_res:
                                    exit_results.append(reb_res)
                            except Exception as ex:
                                self.logger.error(f"Rebalance exit failed for {sym}: {ex}")
                    except Exception as ex_outer:
                        self.logger.error(f"Error during auto-rebalancing: {ex_outer}")
                session_type = "AFTER-HOURS" if not self._is_stock_market_open() else "MARKET HOURS"
                self.logger.info(f"📊 Monitoring {len(positions)} crypto positions for exits ({session_type}: {allocation:.1%}/{max_allocation:.1%})")
                
                for position in positions:
                    try:
                        symbol = position.get('symbol', 'unknown')
                        pnl = position.get('unrealized_pl', 0)
                        pnl_pct = pnl / max(abs(position.get('market_value', 1)), 1)
                        
                        self.logger.info(f"💰 {symbol}: ${pnl:.2f} P&L ({pnl_pct:.1%}) - checking exit signals")
                        
                        exit_signal = self._analyze_crypto_exit(position)
                        if exit_signal:
                            self.logger.info(f"🚨 EXIT SIGNAL: {symbol} - {exit_signal}")
                            exit_result = self._execute_crypto_exit(position, exit_signal)
                            if exit_result:
                                exit_results.append(exit_result)
                        else:
                            self.logger.debug(f"✅ {symbol}: No exit signal - holding position")
                    except Exception as e:
                        self.logger.error(f"Error monitoring position {position.get('symbol', 'unknown')}: {e}")
            else:
                self.logger.debug("No crypto positions found to monitor")
            
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
        """Perform comprehensive analysis of a cryptocurrency, now including market intelligence/ML confidence."""
        try:
            # Get current price and market data
            current_price = self._get_crypto_price(symbol)
            if not current_price or current_price <= 0:
                return None
            
            # Get historical data for analysis (simplified - would integrate with real data)
            market_data = self._get_crypto_market_data(symbol)
            if not market_data:
                return None
            
            # Calculate analysis components using institutional mean reversion approach
            momentum_score = self._calculate_crypto_mean_reversion_score(symbol, market_data)
            volatility_score = self._calculate_crypto_volatility(symbol, market_data)
            volume_score = self._calculate_crypto_volume(symbol, market_data)
            
            # NEVER USE FALLBACKS: If any calculation failed, abort analysis
            if momentum_score is None or volatility_score is None or volume_score is None:
                self.logger.error(f"❌ {symbol}: Analysis FAILED - momentum={momentum_score}, volatility={volatility_score}, volume={volume_score}")
                return None
            
            # Calculate technical confidence using weighted scoring
            technical_confidence = (
                momentum_score * self.analysis_weights['momentum'] +
                volatility_score * self.analysis_weights['volatility'] +
                volume_score * self.analysis_weights['volume']
            )
            
            # DEBUG: Log individual components for troubleshooting
            self.logger.debug(f"🔍 {symbol}: momentum={momentum_score:.2f}, volatility={volatility_score:.2f}, volume={volume_score:.2f}")
            
            # Integrate Market Intelligence/ML confidence if available
            intelligence_confidence = None
            if hasattr(self, 'market_intelligence') and self.market_intelligence:
                try:
                    intelligence_confidence = self.market_intelligence.get_position_risk_score(symbol)
                    self.logger.debug(f"🤖 {symbol}: Market Intelligence confidence={intelligence_confidence:.2f}")
                except Exception as e:
                    self.logger.debug(f"⚠️ {symbol}: Market Intelligence unavailable: {e}")
                    intelligence_confidence = None
            
            # Combine technical and intelligence confidence (if available)
            if intelligence_confidence is not None:
                overall_confidence = 0.5 * technical_confidence + 0.5 * intelligence_confidence
                self.logger.info(f"📊 {symbol}: Tech={technical_confidence:.2f} + AI={intelligence_confidence:.2f} = Overall={overall_confidence:.2f}")
            else:
                overall_confidence = technical_confidence
                self.logger.info(f"📊 {symbol}: Technical-only confidence={overall_confidence:.2f} (momentum={momentum_score:.2f}, vol={volatility_score:.2f}, volume={volume_score:.2f})")
            
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
    
    def _calculate_crypto_mean_reversion_score(self, symbol: str, market_data: Dict) -> float:
        """Calculate mean reversion score for cryptocurrency (INSTITUTIONAL APPROACH)"""
        try:
            # Get data for mean reversion analysis
            current_price = market_data.get('current_price', 0)
            ma_20 = market_data.get('ma_20', None)  # NEVER USE CURRENT PRICE AS FALLBACK
            volume_ratio = market_data.get('volume_ratio', None)
            
            # NEVER USE FALLBACKS - require real market data
            if ma_20 is None or volume_ratio is None:
                self.logger.error(f"❌ {symbol}: Missing critical market data - ma_20={ma_20}, volume_ratio={volume_ratio}")
                return None
            
            if ma_20 <= 0:
                self.logger.error(f"❌ {symbol}: Invalid ma_20={ma_20} for mean reversion calculation")
                return None
            
            # Calculate distance from moving average (key mean reversion metric)
            distance_from_ma = (current_price - ma_20) / ma_20
            
            # INSTITUTIONAL LOGIC: Buy when oversold (below MA), sell when overbought (above MA)
            oversold_threshold = self.crypto_trading_config['oversold_threshold']  # -20%
            
            if distance_from_ma <= oversold_threshold:
                # Oversold condition - higher score for bigger discounts
                # More oversold = higher confidence for mean reversion
                oversold_magnitude = abs(distance_from_ma) / abs(oversold_threshold)
                base_score = min(oversold_magnitude, 1.0)
                
                # Volume confirmation increases confidence
                volume_boost = min((volume_ratio - 1.0) * 0.3, 0.3)  # Up to 30% boost
                
                final_score = min(base_score + volume_boost, 1.0)
                
                self.logger.info(f"📉 {symbol}: OVERSOLD SIGNAL - Distance from MA: {distance_from_ma:.1%}, Score: {final_score:.2f}")
                return final_score
            
            elif distance_from_ma >= 0.20:  # Overbought (20% above MA)
                # Overbought - low score (don't buy, prepare to sell)
                return 0.1
            
            else:
                # Neutral zone - more conservative scoring to prevent overconfidence
                # Map distance to score: 0% distance = 0.5 score, 20% distance = 0.1 score
                neutrality_score = 0.5 - (abs(distance_from_ma) / 0.20) * 0.4  # More conservative scaling
                final_score = max(neutrality_score, 0.1)
                
                self.logger.debug(f"📊 {symbol}: NEUTRAL ZONE - Distance from MA: {distance_from_ma:.1%}, Score: {final_score:.2f}")
                return final_score
            
        except Exception as e:
            self.logger.error(f"❌ {symbol}: Mean reversion calculation FAILED: {e}")
            return None  # NEVER fallback - let caller handle failure
    
    def _calculate_crypto_volatility(self, symbol: str, market_data: Dict) -> float:
        """Calculate volatility score for cryptocurrency"""
        try:
            # Simplified volatility calculation using daily range
            high_24h = market_data.get('high_24h', 0)
            low_24h = market_data.get('low_24h', 0)
            current_price = market_data.get('current_price', 0)
            
            if current_price <= 0:
                self.logger.error(f"❌ {symbol}: Invalid current_price={current_price} for volatility calculation")
                return None
            
            if high_24h <= low_24h:
                self.logger.error(f"❌ {symbol}: Invalid 24h range (high={high_24h}, low={low_24h}) for volatility calculation")
                return None
            
            daily_range = (high_24h - low_24h) / current_price
            
            # Score volatility (higher volatility = higher score up to threshold)
            # Cap volatility score to prevent artificially high confidence
            raw_volatility_score = daily_range / self.volatility_threshold
            volatility_score = min(raw_volatility_score, 1.0)
            
            # Additional dampening to prevent overconfidence in volatile markets
            if raw_volatility_score > 2.0:  # Very high volatility
                volatility_score = volatility_score * 0.7  # Reduce score for extreme volatility
            
            self.logger.debug(f"📊 {symbol}: Volatility - daily_range={daily_range:.3f}, threshold={self.volatility_threshold:.3f}, score={volatility_score:.2f}")
            return volatility_score
            
        except Exception as e:
            self.logger.error(f"❌ {symbol}: Volatility calculation FAILED: {e}")
            return None  # NEVER fallback - let caller handle failure
    
    def _calculate_crypto_volume(self, symbol: str, market_data: Dict) -> float:
        """Calculate volume score for cryptocurrency"""
        try:
            # Simplified volume analysis
            volume_24h = market_data.get('volume_24h', 0)
            avg_volume = market_data.get('avg_volume_7d', volume_24h)
            
            if avg_volume <= 0:
                self.logger.error(f"❌ {symbol}: Invalid avg_volume={avg_volume} for volume calculation")
                return None
            
            volume_ratio = volume_24h / avg_volume
            
            # Higher than average volume = higher score, but with realistic caps
            # Cap at 3x average volume to prevent artificial confidence spikes
            capped_ratio = min(volume_ratio, 3.0)
            volume_score = capped_ratio / 3.0  # Normalize to 0-1
            
            # Additional dampening for extremely high volume (may indicate manipulation)
            if volume_ratio > 5.0:
                volume_score = volume_score * 0.8  # Reduce confidence for suspicious volume
            
            self.logger.debug(f"📊 {symbol}: Volume - 24h={volume_24h:.0f}, avg={avg_volume:.0f}, ratio={volume_ratio:.2f}, score={volume_score:.2f}")
            return volume_score
            
        except Exception as e:
            self.logger.error(f"❌ {symbol}: Volume calculation FAILED: {e}")
            return None  # NEVER fallback - let caller handle failure
    
    def _create_crypto_opportunity(self, analysis: CryptoAnalysis, 
                                 crypto_config: Dict[str, Any]) -> Optional[TradeOpportunity]:
        """Create a trade opportunity from crypto analysis"""
        try:
            # Determine trade direction - use momentum strategy for all crypto
            action = self._determine_crypto_action(analysis, crypto_config['strategy'])
            
            # CRITICAL FIX: Prevent SELL opportunities when no position exists
            if action == TradeAction.SELL:
                # Check if we actually have a position to sell
                current_positions = self._get_crypto_positions()
                has_position = any(pos.get('symbol') == analysis.symbol and float(pos.get('qty', 0)) > 0 
                                 for pos in current_positions)
                
                if not has_position:
                    self.logger.debug(f"🚫 {analysis.symbol}: Blocking SELL opportunity - no position exists")
                    return None  # Don't create phantom sell opportunities
                else:
                    self.logger.info(f"✅ {analysis.symbol}: SELL opportunity valid - position exists")
            
            # Calculate position size with session-aware leverage (AGGRESSIVE after hours)
            base_quantity = self._calculate_crypto_quantity(analysis.symbol, analysis.current_price)
            session_leverage = self._get_leverage_for_current_session()
            adjusted_quantity = base_quantity * crypto_config['position_size_multiplier'] * session_leverage
            
            # Debug: Log quantity calculation details
            self.logger.debug(f"🔢 {analysis.symbol}: Quantity calc - base={base_quantity:.4f}, session_leverage={session_leverage:.2f}, multiplier={crypto_config['position_size_multiplier']:.2f}, final={adjusted_quantity:.4f}")
            
            # Check for invalid quantities
            if adjusted_quantity <= 0:
                self.logger.warning(f"⚠️ {analysis.symbol}: Invalid quantity {adjusted_quantity} - cannot create opportunity")
                return None
            
            # Log aggressive positioning when market is closed
            if not self._is_stock_market_open():
                self.logger.info(f"🚀 AFTER-HOURS AGGRESSIVE: {analysis.symbol} using {session_leverage}x leverage (vs {self.leverage_multiplier}x normal)")
            
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
            # CRITICAL FIX: Validate before ALL order submissions (BUY and SELL)
            if opportunity.action == TradeAction.BUY:
                trade_value = float(opportunity.quantity) * opportunity.entry_price
                is_valid, error_msg = self.risk_manager.validate_position(
                    opportunity.symbol, 
                    trade_value, # Use trade value for crypto instead of shares
                    1.0  # Price = 1 since we're passing trade value as quantity
                )
                if not is_valid:
                    self.logger.warning(f"🚫 Crypto trade blocked for {opportunity.symbol}: {error_msg}")
                    return TradeResult(
                        opportunity=opportunity,
                        status=TradeStatus.FAILED,
                        order_id=None,
                        error_message=f"Risk validation failed: {error_msg}"
                    )
            elif opportunity.action == TradeAction.SELL:
                # EMERGENCY FIX: Validate position exists before selling
                positions = self._get_crypto_positions()
                position_exists = any(pos.symbol == opportunity.symbol for pos in positions)
                if not position_exists:
                    self.logger.error(f"🚫 PHANTOM SELL BLOCKED: {opportunity.symbol} - position does not exist!")
                    return TradeResult(
                        opportunity=opportunity,
                        status=TradeStatus.FAILED,
                        order_id=None,
                        error_message=f"Cannot sell {opportunity.symbol}: position does not exist"
                    )
                
                # Validate sufficient quantity
                available_qty = 0.0
                for pos in positions:
                    if pos.symbol == opportunity.symbol:
                        available_qty = float(pos.qty)
                        break
                
                if float(opportunity.quantity) > available_qty:
                    self.logger.error(f"🚫 INSUFFICIENT QUANTITY: {opportunity.symbol} - requested: {opportunity.quantity}, available: {available_qty}")
                    return TradeResult(
                        opportunity=opportunity,
                        status=TradeStatus.FAILED,
                        order_id=None,
                        error_message=f"Insufficient quantity for {opportunity.symbol}: requested {opportunity.quantity}, available {available_qty}"
                    )
            
            # Prepare order data for crypto
            order_data = {
                'symbol': opportunity.symbol,
                'qty': opportunity.quantity, # Crypto quantities can be fractional
                'side': 'buy' if opportunity.action == TradeAction.BUY else 'sell',
                'type': 'market',
                'time_in_force': 'gtc'  # Good til cancelled for crypto
            }
            
            self.logger.info(f"Attempting crypto trade for {opportunity.symbol}: {order_data['side']} {order_data['qty']} units.")
            execution_result = self.order_executor.execute_order(order_data)
            
            if not execution_result or not execution_result.get('success'):
                error_msg = execution_result.get('error', 'Unknown error during crypto order submission')
                self.logger.error(f"Failed to submit crypto order for {opportunity.symbol}: {error_msg}")
                return TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.FAILED,
                    order_id=None,
                    error_message=f"Order submission failed: {error_msg}"
                )

            order_id = execution_result.get('order_id')
            self.logger.info(f"Crypto order {order_id} submitted for {opportunity.symbol}. Polling for fill...")

            # Poll for order status
            filled_avg_price = None
            actual_filled_qty = 0.0
            final_status = None
            max_retries = 120  # Poll for up to 120 seconds for crypto
            retries = 0
            while retries < max_retries:
                time.sleep(1) # Wait 1 second between polls
                status_result = self.order_executor.get_order_status(order_id)
                if status_result and status_result.get('success'):
                    final_status = status_result.get('status')
                    if final_status == 'filled':
                        filled_avg_price = status_result.get('filled_avg_price')
                        actual_filled_qty = float(status_result.get('filled_qty', 0.0))
                        self.logger.info(f"Crypto order {order_id} for {opportunity.symbol} filled. Price: {filled_avg_price}, Qty: {actual_filled_qty}")
                        break
                    elif final_status in ['canceled', 'expired', 'rejected', 'done_for_day']:
                        self.logger.warning(f"Crypto order {order_id} for {opportunity.symbol} did not fill. Final status: {final_status}")
                        break
                    elif final_status == 'partially_filled':
                        current_filled_qty = float(status_result.get('filled_qty', 0.0))
                        self.logger.info(f"Crypto order {order_id} for {opportunity.symbol} is partially_filled with {current_filled_qty}. Continuing to poll.")
                else:
                    self.logger.warning(f"Could not get status for crypto order {order_id}. Retrying...")
                retries += 1

            result_status = TradeStatus.FAILED
            error_msg_result = None
            updated_opportunity = opportunity # Keep original opportunity by default

            if filled_avg_price and actual_filled_qty > 0:
                result_status = TradeStatus.EXECUTED
                updated_opportunity = dataclasses.replace(opportunity, quantity=actual_filled_qty)
            else:
                self.logger.error(f"Crypto order {order_id} for {opportunity.symbol} did not fill adequately. Final status: {final_status}, Filled Qty: {actual_filled_qty}")
                error_msg_result = f"Order {order_id} failed to fill adequately. Status: {final_status}, Filled Qty: {actual_filled_qty}"

            # Create trade result. P&L is None for entry trades.
            result = TradeResult(
                opportunity=updated_opportunity,
                status=result_status,
                order_id=order_id,
                execution_price=filled_avg_price if result_status == TradeStatus.EXECUTED else None,
                execution_time=datetime.now(), # Ideally, get execution time from order status
                error_message=error_msg_result,
                pnl=None, # P&L is handled by _execute_crypto_exit for exits
                pnl_pct=None
            )
            
            # 🧠 ML DATA COLLECTION: Save trade with enhanced parameter context
            # result.success checks pnl > 0, which is false for entries. Check status directly.
            if result.status == TradeStatus.EXECUTED:
                trade_id = self._save_ml_enhanced_crypto_trade(updated_opportunity, result) # Pass updated_opportunity
                if not hasattr(result, 'metadata'): # Ensure metadata attribute exists
                    result.metadata = {}
                result.metadata['ml_trade_id'] = trade_id
            
            return result
                
        except Exception as e:
            self.logger.error(f"Crypto execution error for {opportunity.symbol}: {e}", exc_info=True)
            return TradeResult(
                opportunity=opportunity,
                status=TradeStatus.FAILED,
                order_id=None,
                error_message=f"Crypto execution error: {str(e)}"
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
            return trade_id
            
        except Exception as e:
            self.logger.error(f"Error saving ML crypto trade data: {e}")
            return None
    
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
            
            # INSTITUTIONAL EXIT LOGIC - Research-backed risk management
            
            # 1. EMERGENCY STOP LOSS - Protect capital (MOST CRITICAL FIX)
            stop_loss_pct = self.crypto_trading_config.get('stop_loss_pct', 0.10)
            if unrealized_pl_pct <= -stop_loss_pct:  # 10% stop loss (DOWN from 15%)
                self.logger.warning(f"🚨 EMERGENCY STOP LOSS: {position.get('symbol')} at {unrealized_pl_pct:.1%} loss")
                return 'emergency_stop_loss'
            
            # 2. INSTITUTIONAL PROFIT TARGET - Mean reversion complete
            profit_target_pct = self.crypto_trading_config.get('profit_target_pct', 0.25)
            if unrealized_pl_pct >= profit_target_pct:  # 25% profit target (DOWN from 25%)
                self.logger.info(f"🎯 PROFIT TARGET HIT: {position.get('symbol')} at {unrealized_pl_pct:.1%} gain")
                return 'institutional_profit_target'
            
            # 3. MEAN REVERSION OVERBOUGHT EXIT - Exit if too far above MA
            if unrealized_pl_pct >= 0.30:  # 30%+ gains may be due for reversal
                self.logger.info(f"🔄 MEAN REVERSION EXIT: {position.get('symbol')} at {unrealized_pl_pct:.1%} - overbought")
                return 'mean_reversion_overbought'
            
            # 4. TRAILING STOP LOGIC - Protect profits once we're doing well
            if unrealized_pl_pct >= 0.20:  # If we're at 20%+ profit
                # Use trailing stop to protect 75% of gains (5% trailing stop from peak)
                # This is a simplified version - in production we'd track peak value
                trailing_stop_threshold = 0.15  # Exit if profit drops to 15% (from 20%+)
                if unrealized_pl_pct <= trailing_stop_threshold:
                    return 'trailing_stop'
            
            # 5. TECHNICAL ANALYSIS EXIT - Exit if momentum turns against us
            try:
                current_price = position.get('current_price', 0)
                if current_price > 0:
                    # Get recent price action for momentum analysis
                    quotes = self._get_quotes([symbol])
                    if quotes and symbol in quotes:
                        quote = quotes[symbol]
                        # Simple momentum check: if current price is significantly below recent quote
                        if hasattr(quote, 'ap') and quote.ap:
                            recent_price = float(quote.ap)
                            price_decline = (recent_price - current_price) / current_price
                            
                            # If we're profitable but price declining rapidly, exit to protect gains
                            if unrealized_pl_pct > 0.05 and price_decline < -0.03:  # 3% price decline
                                return 'momentum_reversal'
            except Exception:
                pass  # Skip technical analysis if data unavailable
            
            # 6. PRE-MARKET CLOSURE - Only exit if market opening soon (already implemented elsewhere)
            if self._should_close_positions_before_market_open():
                return 'pre_market_closure'
            
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing crypto exit: {e}")
            return None
    
    def _execute_crypto_exit(self, position: Dict, exit_reason: str) -> Optional[TradeResult]:
        """Execute crypto position exit with ML-enhanced exit analysis"""
        try:
            symbol = position.get('symbol')
            if not symbol:
                self.logger.error("Cannot execute crypto exit: position symbol is missing.")
                return None

            position_qty = float(position.get('qty', 0))
            if position_qty == 0:
                self.logger.warning(f"Attempting to exit crypto position with zero quantity for {symbol}")
                return None

            side_to_close = 'sell' if position_qty > 0 else 'buy'
            qty_to_close = abs(position_qty)
            
            # Create exit opportunity (used for TradeResult regardless of execution outcome)
            exit_opportunity = TradeOpportunity(
                symbol=symbol,
                action=TradeAction.SELL if side_to_close == 'sell' else TradeAction.BUY,
                quantity=qty_to_close,
                confidence=0.6,  # Medium confidence for exits, can be refined
                strategy='crypto_exit'
            )
            
            # Prepare order data for crypto exit
            order_data = {
                'symbol': symbol,
                'qty': qty_to_close,
                'side': side_to_close,
                'type': 'market',
                'time_in_force': 'gtc'  # Good til cancelled for crypto
            }
            
            self.logger.info(f"Attempting to close crypto position {symbol}: {side_to_close} {qty_to_close} units.")
            execution_result = self.order_executor.execute_order(order_data)
            
            if not execution_result or not execution_result.get('success'):
                error_msg = execution_result.get('error', 'Unknown error during crypto order submission')
                self.logger.error(f"Failed to submit closing crypto order for {symbol}: {error_msg}")
                return TradeResult(
                    opportunity=exit_opportunity,
                    status=TradeStatus.FAILED,
                    order_id=None,
                    error_message=f"Order submission failed: {error_msg}"
                )

            order_id = execution_result.get('order_id')
            self.logger.info(f"Closing crypto order {order_id} submitted for {symbol}. Polling for fill...")

            # Poll for order status
            filled_avg_price = None
            actual_filled_qty = 0
            final_status = None
            # Crypto orders might take longer or have partial fills, adjust polling as needed
            max_retries = 120  # Poll for up to 120 seconds for crypto
            retries = 0
            while retries < max_retries:
                time.sleep(1) # Wait 1 second between polls
                status_result = self.order_executor.get_order_status(order_id)
                if status_result and status_result.get('success'):
                    final_status = status_result.get('status')
                    # For crypto, partial fills might occur. We need to handle 'filled' or 'partially_filled' and then check qty.
                    # However, Alpaca API usually transitions from partially_filled to filled once complete for market orders.
                    # We will consider 'filled' as the primary success state.
                    if final_status == 'filled':
                        filled_avg_price = status_result.get('filled_avg_price')
                        actual_filled_qty = float(status_result.get('filled_qty', 0))
                        self.logger.info(f"Crypto order {order_id} for {symbol} filled. Price: {filled_avg_price}, Qty: {actual_filled_qty}")
                        break
                    elif final_status in ['canceled', 'expired', 'rejected', 'done_for_day']:
                        self.logger.warning(f"Crypto order {order_id} for {symbol} did not fill. Final status: {final_status}")
                        break
                    elif final_status == 'partially_filled':
                        # Log partial fill and continue polling, or decide to act on it
                        current_filled_qty = float(status_result.get('filled_qty', 0))
                        self.logger.info(f"Crypto order {order_id} for {symbol} is partially_filled with {current_filled_qty}. Continuing to poll.")
                        # Potentially update filled_avg_price and actual_filled_qty if we were to accept partial fills here
                else:
                    self.logger.warning(f"Could not get status for crypto order {order_id}. Retrying...")
                retries += 1
            
            if not filled_avg_price or actual_filled_qty == 0:
                self.logger.error(f"Closing crypto order {order_id} for {symbol} did not achieve full fill with valid price/qty. Final status: {final_status}")
                return TradeResult(
                    opportunity=exit_opportunity,
                    status=TradeStatus.FAILED, # Or a more specific status
                    order_id=order_id,
                    error_message=f"Order {order_id} failed to fill adequately. Status: {final_status}, Filled Qty: {actual_filled_qty}"
                )

            # Calculate REAL P&L using actual fill price and entry price from position
            entry_price = float(position.get('avg_entry_price', 0))
            if entry_price == 0:
                 self.logger.warning(f"avg_entry_price for crypto {symbol} is 0. P&L calculation will be inaccurate.")

            if side_to_close == 'sell': # Closing a long position
                realized_pnl = (filled_avg_price - entry_price) * actual_filled_qty
            else: # Closing a short position (buy to cover)
                realized_pnl = (entry_price - filled_avg_price) * actual_filled_qty
            
            cost_basis = entry_price * actual_filled_qty
            pnl_pct = (realized_pnl / cost_basis) * 100 if cost_basis != 0 else 0

            self.logger.info(f"Crypto Exit P&L for {symbol}: Entry: {entry_price}, Exit Fill: {filled_avg_price}, Qty: {actual_filled_qty}, P&L: {realized_pnl:.2f} ({pnl_pct:.2f}%)")

            # Create exit result with P&L information
            result = TradeResult(
                opportunity=exit_opportunity, # Original opportunity for context
                status=TradeStatus.EXECUTED if final_status == 'filled' and actual_filled_qty > 0 else TradeStatus.FAILED,
                order_id=order_id,
                execution_price=filled_avg_price,
                execution_time=datetime.now(), # Ideally, get execution time from order status
                pnl=realized_pnl,
                pnl_pct=pnl_pct,
                exit_reason=self._get_exit_reason_enum(exit_reason)
            )
            
            # UPDATE REAL PROFITABILITY METRICS
            self._update_exit_performance_metrics(symbol, realized_pnl) # Use the new accurate P&L
            
            # 🧠 ML DATA COLLECTION: Save exit analysis for parameter optimization
            # This call should now use the `result` object with correct P&L
            self._save_ml_enhanced_crypto_exit(position, result, exit_reason)
            
            self.logger.info(f"💰 Crypto exit processed: {symbol} {exit_reason} P&L: ${realized_pnl:.2f} ({pnl_pct:.1%})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing crypto exit for {position.get('symbol', 'UNKNOWN')}: {e}", exc_info=True)
            symbol = position.get('symbol', 'UNKNOWN_CRYPTO')
            qty = abs(float(position.get('qty', 0)))
            action_on_error = TradeAction.SELL if float(position.get('qty', 0)) > 0 else TradeAction.BUY

            error_opportunity = TradeOpportunity(
                symbol=symbol,
                action=action_on_error,
                quantity=qty if qty > 0 else 0.001, # Avoid zero quantity for crypto
                confidence=0.0,
                strategy='crypto_exit_error'
            )
            return TradeResult(
                opportunity=error_opportunity,
                status=TradeStatus.FAILED,
                order_id=None,
                error_message=str(e)
            )
    
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
            
            # UPDATE ENTRY TRADE WITH FINAL PROFIT/LOSS (CRITICAL FOR ML LEARNING)
            entry_data = self._crypto_positions.get(symbol, {})
            entry_trade_id = entry_data.get('entry_trade_id')
            if entry_trade_id:
                try:
                    # Update the original entry trade with final profit outcome
                    entry_update_data = {
                        'profit_loss': result.pnl or 0.0,
                        'exit_reason': exit_reason,
                        'final_outcome': 'profitable' if (result.pnl or 0.0) > 0 else 'loss',
                        'hold_duration_hours': hold_duration_hours,
                        'exit_trade_id': trade_id,
                        'updated_at': datetime.now().isoformat()
                    }
                    self.update_ml_trade_outcome(entry_trade_id, entry_update_data)
                    self.logger.info(f"🔗 Updated entry trade {entry_trade_id} with final P&L: ${result.pnl:.2f}")
                except Exception as e:
                    self.logger.error(f"Failed to update entry trade profit: {e}")
            
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
        """Get current cryptocurrency price using correct Alpaca API methods"""
        try:
            # Convert symbol format: BTCUSD -> BTC/USD (Alpaca crypto format)
            if '/' not in symbol and 'USD' in symbol:
                base_symbol = symbol.replace('USD', '')
                formatted_symbol = f"{base_symbol}/USD"
            else:
                formatted_symbol = symbol
            
            self.logger.info(f"🔍 {symbol}: Trying formatted symbol: {formatted_symbol}")
            
            # First try: get_latest_crypto_bars (documented method)
            try:
                bars = self.api.get_latest_crypto_bars(formatted_symbol)
                if bars and formatted_symbol in bars:
                    bar = bars[formatted_symbol]
                    if hasattr(bar, 'c') and hasattr(bar, 't'):  # 'c' is close price, 't' is timestamp
                        price = float(bar.c)
                        
                        # Validate data freshness based on subscription level
                        if hasattr(bar, 't') and bar.t:
                            from datetime import datetime, timezone
                            from data_mode_manager import get_data_mode_manager
                            
                            bar_time = bar.t.replace(tzinfo=timezone.utc) if bar.t.tzinfo is None else bar.t
                            age_seconds = (datetime.now(timezone.utc) - bar_time).total_seconds()
                            
                            # Use data mode manager to determine acceptable staleness
                            data_manager = get_data_mode_manager()
                            
                            if not data_manager.is_quote_acceptable(age_seconds):
                                if data_manager.should_warn_about_staleness(age_seconds):
                                    self.logger.warning(f"⚠️ {symbol}: Quote data is {age_seconds:.0f}s old (exceeds {data_manager.config['data_warning_threshold']}s threshold)")
                                else:
                                    self.logger.debug(f"🕐 {symbol}: Quote data is {age_seconds:.0f}s old (acceptable for {data_manager.data_mode.value} mode)")
                            else:
                                self.logger.debug(f"✅ {symbol}: Quote data is {age_seconds:.0f}s old (fresh for {data_manager.data_mode.value} mode)")
                        
                        if price > 0:
                            self.logger.info(f"✅ {symbol}: Real-time price from crypto bars: ${price}")
                            return price
                self.logger.error(f"❌ {symbol}: get_latest_crypto_bars returned no valid data")
            except Exception as e:
                self.logger.error(f"❌ {symbol}: get_latest_crypto_bars failed: {e}")
            
            # Second try: get_latest_crypto_trades (documented method)
            try:
                trades = self.api.get_latest_crypto_trades(formatted_symbol)
                if trades and formatted_symbol in trades:
                    trade = trades[formatted_symbol]
                    if hasattr(trade, 'p'):  # 'p' is trade price
                        price = float(trade.p)
                        if price > 0:
                            self.logger.info(f"✅ {symbol}: Real price from crypto trades: ${price}")
                            return price
                self.logger.error(f"❌ {symbol}: get_latest_crypto_trades returned no valid data")
            except Exception as e:
                self.logger.error(f"❌ {symbol}: get_latest_crypto_trades failed: {e}")
            
            # Third try: get_latest_crypto_quotes (documented method)
            try:
                quotes = self.api.get_latest_crypto_quotes(formatted_symbol)
                if quotes and formatted_symbol in quotes:
                    quote = quotes[formatted_symbol]
                    # Try ask price first, then bid
                    for attr in ['ap', 'bp']:  # ap = ask price, bp = bid price
                        if hasattr(quote, attr):
                            price_value = getattr(quote, attr)
                            try:
                                if price_value is not None:
                                    price_float = float(price_value)
                                    if price_float > 0:
                                        self.logger.info(f"✅ {symbol}: Real price from crypto quotes: ${price_float}")
                                        return price_float
                            except (ValueError, TypeError):
                                continue
                self.logger.error(f"❌ {symbol}: get_latest_crypto_quotes returned no valid data")
            except Exception as e:
                self.logger.error(f"❌ {symbol}: get_latest_crypto_quotes failed: {e}")
            
            # NO FALLBACK TO SIMULATED PRICES - Real data only
            self.logger.error(f"❌ {symbol}: No real crypto price available from Alpaca API")
            return 0.0
                
        except Exception as e:
            self.logger.error(f"❌ {symbol}: All real crypto price methods failed: {e}")
            return 0.0
    
    def _get_crypto_market_data(self, symbol: str) -> Optional[Dict]:
        """Get cryptocurrency market data for analysis using real Alpaca data"""
        try:
            current_price = self._get_crypto_price(symbol)
            if not current_price:
                return None
            
            # Convert symbol format for API calls
            if '/' not in symbol and 'USD' in symbol:
                base_symbol = symbol.replace('USD', '')
                formatted_symbol = f"{base_symbol}/USD"
            else:
                formatted_symbol = symbol
            
            # Get real historical bars for 24h data
            try:
                from datetime import datetime, timedelta, timezone
                
                # Get 24h of hourly bars with proper RFC3339 timestamp
                start_time = datetime.now(timezone.utc) - timedelta(days=1)
                start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')  # RFC3339 format
                
                bars = self.api.get_crypto_bars(
                    formatted_symbol,
                    start=start_time_str,
                    timeframe='1Hour'
                )
                
                if bars and len(bars) > 0:
                    # Calculate real 24h metrics from bars
                    prices = [float(bar.c) for bar in bars]  # Close prices
                    volumes = [float(bar.v) for bar in bars]  # Volumes
                    
                    # NEVER USE FALLBACKS - require real data
                    if not prices or len(prices) < 20:
                        self.logger.error(f"❌ {symbol}: Insufficient price history ({len(prices) if prices else 0}/20 bars)")
                        return None
                    
                    if not volumes:
                        self.logger.error(f"❌ {symbol}: No volume data available")
                        return None
                    
                    price_24h_ago = prices[0]
                    high_24h = max(float(bar.h) for bar in bars)
                    low_24h = min(float(bar.l) for bar in bars)
                    volume_24h = sum(volumes)
                    
                    # Calculate mean reversion metrics ONLY from real data
                    ma_20 = sum(prices[-20:]) / 20  # Exactly 20 periods
                    avg_volume = sum(volumes) / len(volumes)
                    volume_ratio = volume_24h / avg_volume
                    
                    self.logger.info(f"📊 {symbol}: Real 24h data - High: ${high_24h:.4f}, Low: ${low_24h:.4f}, Vol: {volume_24h:.0f}")
                    
                else:
                    # NEVER USE SIMULATED DATA - return None for missing data
                    self.logger.error(f"❌ {symbol}: No real market data available from Alpaca API")
                    return None
                
            except Exception as api_error:
                self.logger.error(f"❌ {symbol}: Crypto bars API failed: {api_error}")
                return None
            
            # ma_20 and volume_ratio are now calculated in each data path above
            
            return {
                'current_price': current_price,
                'price_24h_ago': price_24h_ago,
                'high_24h': high_24h,
                'low_24h': low_24h,
                'volume_24h': volume_24h,
                'avg_volume_7d': avg_volume,  # Use real calculated average
                'ma_20': ma_20,  # 20-day moving average for mean reversion
                'volume_ratio': volume_ratio  # Volume ratio for mean reversion
            }
            
        except Exception as e:
            self.logger.error(f"❌ {symbol}: Error getting market data: {e}")
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
            
            # Debug logging
            self.logger.debug(f"💰 {symbol}: Quantity calc - portfolio=${portfolio_value:,.2f}, allocation={base_allocation:.1%}, max_value=${max_position_value:.2f}, price=${price:.4f}, quantity={quantity:.6f}")
            
            return quantity
            
        except Exception as e:
            self.logger.error(f"Error calculating crypto quantity for {symbol}: {e}")
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
    
    def _update_exit_performance_metrics(self, symbol: str, pnl: float):
        """Update real profitability metrics when position is exited"""
        try:
            # Get the entry session from our tracked positions
            entry_data = self._crypto_positions.get(symbol, {})
            entry_session_name = entry_data.get('session', self._get_current_trading_session().value)
            
            # Find the session enum
            entry_session = None
            for session in TradingSession:
                if session.value == entry_session_name:
                    entry_session = session
                    break
            
            if entry_session:
                session_stats = self._session_performance[entry_session]
                
                # Update P&L metrics
                session_stats['total_pnl'] += pnl
                if pnl > 0:
                    session_stats['profitable_trades'] += 1
                
                # Recalculate derived metrics
                if session_stats['total_trades'] > 0:
                    session_stats['win_rate'] = session_stats['profitable_trades'] / session_stats['total_trades']
                    session_stats['avg_profit_per_trade'] = session_stats['total_pnl'] / session_stats['total_trades']
                
                if session_stats['total_invested'] > 0:
                    session_stats['roi'] = session_stats['total_pnl'] / session_stats['total_invested']
                
                # Remove from tracked positions
                if symbol in self._crypto_positions:
                    del self._crypto_positions[symbol]
                    
        except Exception as e:
            self.logger.error(f"Error updating exit performance metrics: {e}")
    
    def _log_session_performance(self):
        """Log session-based REAL profitability metrics"""
        try:
            current_session = self._get_current_trading_session()
            session_stats = self._session_performance[current_session]
            
            if session_stats['total_trades'] > 0:
                self.logger.info(f"Session {current_session.value}: {session_stats['total_trades']} trades, "
                               f"{session_stats['win_rate']:.1%} WIN RATE (execution success), "
                               f"Total P&L: ${session_stats['total_pnl']:.2f}, "
                               f"ROI: {session_stats['roi']:.1%}")
                               
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
    
    def _is_stock_market_open(self) -> bool:
        """Check if US stock market is currently open"""
        try:
            clock = self.api.get_clock()
            return getattr(clock, 'is_open', False)
        except Exception as e:
            self.logger.debug(f"Error checking market hours: {e}")
            return False  # Assume closed if unable to check
    
    def _get_max_allocation_for_current_session(self) -> float:
        """Get maximum crypto allocation based on market session"""
        if self._is_stock_market_open():
            # Market hours: Conservative allocation to save room for stock trades
            return self.max_crypto_allocation  # 30%
        else:
            # After hours: AGGRESSIVE allocation - use almost all buying power for crypto
            return self.after_hours_max_allocation  # 90%
    
    def _get_leverage_for_current_session(self) -> float:
        """Get leverage multiplier based on market session"""
        if self._is_stock_market_open():
            # Market hours: Standard leverage
            return self.leverage_multiplier  # 1.5x
        else:
            # After hours: MAXIMUM leverage for crypto opportunities
            return self.after_hours_leverage  # 1.5x (emergency fix)
    
    def _should_close_positions_before_market_open(self) -> bool:
        """Check if we should close positions before market opens"""
        try:
            clock = self.api.get_clock()
            if hasattr(clock, 'next_open'):
                from datetime import datetime, timedelta
                next_open = clock.next_open
                current_time = datetime.now(next_open.tzinfo)
                time_until_open = (next_open - current_time).total_seconds() / 60  # minutes
                
                # Close positions 30 minutes before market opens
                return time_until_open <= 30 and time_until_open > 0
            return False
        except Exception as e:
            self.logger.debug(f"Error checking time until market open: {e}")
            return False
    
    # Smart Allocation Methods for 5% Monthly ROI Target
    
    def _get_smart_allocation_limit(self) -> float:
        """Get smart allocation limit based on performance for 5% monthly ROI target"""
        try:
            if not self.smart_allocation_enabled:
                return 0.90  # Use 90% of buying power when smart allocation disabled
            
            # MARKET HOURS: EMERGENCY LIMIT - Crypto should be MINIMAL during bullish stock market
            if self._is_stock_market_open():
                self.logger.warning("🚨 EMERGENCY: Limiting crypto to 20% during bullish stock market hours")
                return 0.20  # EMERGENCY: Only 20% crypto during market hours
            
            # Get current performance metrics
            current_win_rate = self._calculate_current_win_rate()
            monthly_performance = self._calculate_monthly_performance()
            
            self.logger.info(f"🎯 SMART ALLOCATION: Win rate: {current_win_rate:.1%}, Monthly: {monthly_performance:.1%}")
            
            # EMERGENCY MODE: If losing 5%+ this month, drastically reduce allocation
            if monthly_performance < -0.05:
                self.logger.warning(f"🚨 EMERGENCY MODE: Monthly loss {monthly_performance:.1%} - reducing to {self.emergency_allocation:.1%}")
                return self.emergency_allocation  # 20%
            
            # PERFORMANCE-BASED ALLOCATION TIERS (AFTER HOURS)
            if current_win_rate < 0.45:
                # Learning phase: Conservative allocation while system learns
                return 0.25  # 25% max allocation
            elif current_win_rate < 0.60:
                # Stable phase: Moderate allocation for balanced growth
                return self.base_crypto_allocation  # 40% target allocation
            else:
                # Profitable phase: Maximum allocation for 5% monthly target
                return self.max_profitable_allocation  # 60% max allocation
                
        except Exception as e:
            self.logger.error(f"Error calculating smart allocation limit: {e}")
            return self.base_crypto_allocation  # Fallback to 40%
    
    def _calculate_current_win_rate(self) -> float:
        """Calculate current win rate across all sessions"""
        try:
            total_trades = 0
            profitable_trades = 0
            
            for session_stats in self._session_performance.values():
                total_trades += session_stats.get('total_trades', 0)
                profitable_trades += session_stats.get('profitable_trades', 0)
            
            if total_trades == 0:
                return 0.50  # Neutral starting point
            
            win_rate = profitable_trades / total_trades
            return win_rate
            
        except Exception as e:
            self.logger.error(f"Error calculating win rate: {e}")
            return 0.50  # Conservative default
    
    def _calculate_monthly_performance(self) -> float:
        """Calculate monthly performance for smart allocation decisions"""
        try:
            # Get daily P&L for last 30 days (simplified version)
            daily_pnl = self._get_daily_pnl()
            
            if not daily_pnl:
                return 0.0  # No performance data yet
            
            # Calculate portfolio base value (for percentage calculation)
            account = self.api.get_account()
            portfolio_value = float(getattr(account, 'portfolio_value', 100000))
            
            # Sum recent P&L and calculate percentage
            recent_pnl = sum(daily_pnl[-30:])  # Last 30 days
            monthly_performance = recent_pnl / portfolio_value if portfolio_value > 0 else 0.0
            
            return monthly_performance
            
        except Exception as e:
            self.logger.error(f"Error calculating monthly performance: {e}")
            return 0.0  # Conservative default
    
    def _get_daily_pnl(self) -> List[float]:
        # Placeholder - replace with actual implementation
        return []

    def _is_quote_data_stale(self, symbol: str) -> bool:
        """Checks if the last quote data for a symbol is older than a threshold (e.g., 30 minutes)."""
        try:
            # Format symbol for Alpaca API (e.g., BTCUSD -> BTC/USD)
            if '/' not in symbol and 'USD' in symbol:
                base_symbol = symbol.replace('USD', '')
                formatted_symbol = f"{base_symbol}/USD"
            else:
                formatted_symbol = symbol

            latest_quotes_dict = self.api.get_latest_crypto_quotes([formatted_symbol])
            
            if not latest_quotes_dict or formatted_symbol not in latest_quotes_dict:
                self.logger.warning(f"No quote data returned for {formatted_symbol} from get_latest_crypto_quotes.")
                return True # Treat as stale if no data

            quote = latest_quotes_dict[formatted_symbol]
            
            if not quote or not hasattr(quote, 'timestamp'):
                self.logger.warning(f"No valid quote object or timestamp for {formatted_symbol}.")
                return True # Treat as stale if no valid quote object or timestamp

            quote_time = quote.timestamp
            # Alpaca SDK's CryptoQuote timestamp should be a timezone-aware datetime object (UTC)
            if quote_time.tzinfo is None:
                # If somehow it's naive, assume UTC as Alpaca operates in UTC
                quote_time = quote_time.replace(tzinfo=timezone.utc)
            
            now_utc = datetime.now(timezone.utc)
            age_seconds = (now_utc - quote_time).total_seconds()

            if age_seconds > 1800:  # 30 minutes threshold
                self.logger.warning(f"Stale data for {formatted_symbol}: quote is {age_seconds:.0f}s old (older than 30 minutes).")
                return True
            
            self.logger.debug(f"Quote for {formatted_symbol} is fresh: {age_seconds:.0f}s old.")
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking quote staleness for {symbol} (formatted: {formatted_symbol if 'formatted_symbol' in locals() else 'N/A'}): {e}")
            return True # Treat as stale on error