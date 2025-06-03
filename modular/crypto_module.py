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
        """Check if analysis meets minimum trading criteria - LOWERED"""
        return self.overall_confidence > 0.25  # LOWERED for more opportunities


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
        
        # Initialize Enhanced Data Manager for real-time crypto data
        try:
            import os
            from enhanced_data_manager import EnhancedDataManager
            
            alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            finnhub_key = os.getenv('FINNHUB_API_KEY')
            
            self.enhanced_data_manager = EnhancedDataManager(
                api_client=api_client,
                alpha_vantage_key=alpha_vantage_key,
                finnhub_key=finnhub_key,
                logger=logger
            )
            self.logger.info("✅ Enhanced data manager with real-time APIs initialized for crypto module")
        except Exception as e:
            self.logger.warning(f"⚠️ Enhanced data manager initialization failed: {e} - using basic Alpaca data")
            self.enhanced_data_manager = None
        
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
            'min_confidence': 0.35,  # LOWERED: Increase opportunities while maintaining quality
            'position_size_multiplier': 1.2,  # INCREASED: More aggressive sizing for recovery
            'strategy': CryptoStrategy.MOMENTUM,  # Momentum strategy for crypto entries
            'analyze_all_symbols': True,  # CHANGED: Analyze all symbols for maximum opportunities
            'cycle_frequency_seconds': 3600,  # Hourly cycles (not intraday scalping)
            'stop_loss_pct': 0.07,  # 7% stop loss (tighter risk control)
            'profit_target_pct': 0.20,  # ADJUSTED: 20% profit target for better hit rate
            'oversold_threshold': -0.15,  # ADJUSTED: Buy on 15%+ dips for more opportunities
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
            
            # AGGRESSIVE RECOVERY MODE: Only limit at extreme over-allocation
            extreme_limit = smart_allocation_limit * 2.0  # INCREASED: 2x buffer for aggressive recovery
            
            if current_allocation >= extreme_limit:
                self.logger.warning(f"🚨 EXTREME OVER-ALLOCATION: {current_allocation:.1%} > {extreme_limit:.1%} - Pausing for risk management")
                return opportunities
            elif current_allocation >= smart_allocation_limit:
                self.logger.info(f"🎯 ABOVE TARGET: {current_allocation:.1%} > {smart_allocation_limit:.1%} - Seeking high-conviction opportunities only")
                # Continue trading but be more selective (higher confidence threshold applied later)
            
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
        """Perform comprehensive analysis of a cryptocurrency using research-backed multi-indicator approach."""
        try:
            # Get current price and market data
            current_price = self._get_crypto_price(symbol)
            if not current_price or current_price <= 0:
                return None
            
            # Get historical data for analysis
            market_data = self._get_crypto_market_data(symbol)
            if not market_data:
                return None
            
            # RESEARCH-BACKED APPROACH: Multiple technical indicators with directional bias
            rsi_analysis = self._calculate_rsi_signals(symbol, market_data)
            macd_analysis = self._calculate_macd_signals(symbol, market_data)
            bollinger_analysis = self._calculate_bollinger_signals(symbol, market_data)
            volume_analysis = self._calculate_volume_confirmation(symbol, market_data)
            
            # RESILIENT ANALYSIS: Log failed indicators but continue with available data
            failed_indicators = []
            if rsi_analysis is None:
                failed_indicators.append("RSI")
            if macd_analysis is None:
                failed_indicators.append("MACD")
            if bollinger_analysis is None:
                failed_indicators.append("Bollinger")
            if volume_analysis is None:
                failed_indicators.append("Volume")
            
            # If ALL indicators fail, abort analysis
            successful_indicators = [rsi_analysis, macd_analysis, bollinger_analysis, volume_analysis]
            successful_count = sum(1 for indicator in successful_indicators if indicator is not None)
            
            if successful_count == 0:
                self.logger.error(f"❌ {symbol}: All indicators FAILED - cannot perform analysis")
                return None
            elif failed_indicators:
                self.logger.warning(f"⚠️ {symbol}: Partial indicators failed: {failed_indicators} - continuing with {successful_count}/4 indicators")
            
            # RESEARCH-BASED CONFIDENCE: Separate BUY and SELL confidence scores
            buy_confidence = self._calculate_directional_confidence('BUY', rsi_analysis, macd_analysis, bollinger_analysis, volume_analysis)
            sell_confidence = self._calculate_directional_confidence('SELL', rsi_analysis, macd_analysis, bollinger_analysis, volume_analysis)
            
            # Use the higher confidence score and determine action
            if buy_confidence > sell_confidence:
                technical_confidence = buy_confidence
                primary_action = 'BUY'
                momentum_score = buy_confidence  # For compatibility
            else:
                technical_confidence = sell_confidence
                primary_action = 'SELL'
                momentum_score = sell_confidence  # For compatibility
            
            # For compatibility with existing code structure - handle None safely
            volatility_score = bollinger_analysis.get('volatility_score', 0.5) if bollinger_analysis else 0.5
            volume_score = volume_analysis.get('volume_score', 0.5) if volume_analysis else 0.5
            
            # DEBUG: Log comprehensive analysis for troubleshooting - handle None safely
            rsi_value = rsi_analysis.get('rsi_value', 0) if rsi_analysis else 0
            macd_signal = macd_analysis.get('macd_signal', 'neutral') if macd_analysis else 'None'
            bollinger_position = bollinger_analysis.get('position', 'neutral') if bollinger_analysis else 'None'
            volume_confirmation = volume_analysis.get('confirmation', 'neutral') if volume_analysis else 'None'
            
            self.logger.info(f"🔍 {symbol}: BUY_conf={buy_confidence:.2f}, SELL_conf={sell_confidence:.2f}, Action={primary_action}, RSI={rsi_value:.1f}")
            self.logger.debug(f"📊 {symbol}: MACD={macd_signal}, Bollinger={bollinger_position}, Volume={volume_confirmation}")
            
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
                self.logger.info(f"📊 {symbol}: Technical confidence={overall_confidence:.2f} (momentum={momentum_score:.2f}, vol={volatility_score:.2f}, volume={volume_score:.2f})")
            
            session_config = self.session_configs[session]
            
            # Store the primary action in metadata for use in opportunity creation
            analysis_result = CryptoAnalysis(
                symbol=symbol,
                current_price=current_price,
                momentum_score=momentum_score,
                volatility_score=volatility_score,
                volume_score=volume_score,
                overall_confidence=overall_confidence,
                session=session,
                strategy=session_config.strategy
            )
            
            # Add primary action as an attribute for the opportunity creation
            analysis_result.primary_action = primary_action
            
            return analysis_result
        except Exception as e:
            self.logger.error(f"Error analyzing crypto symbol {symbol}: {e}")
            return None
    
    # RESEARCH-BACKED TECHNICAL INDICATORS (Based on 2024 crypto trading research)
    
    def _calculate_rsi_signals(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """Calculate RSI-based buy/sell signals with mean reversion using real market data"""
        try:
            prices = market_data.get('price_history', [])
            if len(prices) < 14:
                return None
            
            # Calculate RSI (14-period standard) with proper real data
            price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            gains = [change if change > 0 else 0 for change in price_changes]
            losses = [-change if change < 0 else 0 for change in price_changes]
            
            # Calculate average gains and losses
            avg_gain = sum(gains[-14:]) / 14
            avg_loss = sum(losses[-14:]) / 14
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            # MEAN REVERSION STRATEGY: Calculate deviation from moving average
            ma_period = self.crypto_trading_config['moving_average_period']
            if len(prices) >= ma_period:
                moving_average = sum(prices[-ma_period:]) / ma_period
                current_price = prices[-1]
                deviation_pct = (current_price - moving_average) / moving_average
                
                # Mean reversion logic: favor opposite direction of deviation
                if deviation_pct <= self.crypto_trading_config['oversold_threshold']:
                    # Price significantly below MA - STRONG BUY signal
                    mean_reversion_buy_boost = 0.3
                    mean_reversion_sell_penalty = -0.3
                    signal_context = f"mean_reversion_oversold_{deviation_pct:.1%}"
                elif deviation_pct >= -self.crypto_trading_config['oversold_threshold']:
                    # Price significantly above MA - SELL signal
                    mean_reversion_buy_boost = -0.2
                    mean_reversion_sell_penalty = 0.2
                    signal_context = f"mean_reversion_overbought_{deviation_pct:.1%}"
                else:
                    # Price near MA - neutral
                    mean_reversion_buy_boost = 0.0
                    mean_reversion_sell_penalty = 0.0
                    signal_context = f"mean_reversion_neutral_{deviation_pct:.1%}"
            else:
                # Not enough data for mean reversion
                mean_reversion_buy_boost = 0.0
                mean_reversion_sell_penalty = 0.0
                signal_context = "insufficient_data_for_mean_reversion"
            
            # Combine RSI with mean reversion
            if rsi <= 30:
                # Strong oversold RSI + mean reversion
                buy_strength = min(0.95, 0.85 + mean_reversion_buy_boost)
                sell_strength = max(0.05, 0.15 + mean_reversion_sell_penalty)
                signal = 'strong_buy'
            elif rsi <= 45:
                # Moderate oversold + mean reversion
                buy_strength = min(0.85, 0.70 + mean_reversion_buy_boost)
                sell_strength = max(0.15, 0.30 + mean_reversion_sell_penalty)
                signal = 'buy'
            elif rsi <= 55:
                # Neutral RSI - let mean reversion dominate
                buy_strength = max(0.30, min(0.70, 0.50 + mean_reversion_buy_boost))
                sell_strength = max(0.30, min(0.70, 0.50 + mean_reversion_sell_penalty))
                signal = 'neutral'
            elif rsi <= 70:
                # Moderate overbought + mean reversion
                buy_strength = max(0.15, 0.40 + mean_reversion_buy_boost)
                sell_strength = min(0.85, 0.60 + mean_reversion_sell_penalty)
                signal = 'weak_sell'
            else:
                # Strong overbought RSI + mean reversion
                buy_strength = max(0.05, 0.25 + mean_reversion_buy_boost)
                sell_strength = min(0.95, 0.75 + mean_reversion_sell_penalty)
                signal = 'sell'
            
            return {
                'rsi_value': rsi,
                'signal': signal,
                'buy_strength': buy_strength,
                'sell_strength': sell_strength,
                'mean_reversion_context': signal_context,
                'ma_deviation': deviation_pct if len(prices) >= ma_period else None
            }
            
        except Exception as e:
            self.logger.error(f"❌ {symbol}: RSI+MeanReversion calculation failed: {e}")
            return None
    
    def _calculate_macd_signals(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """Calculate MACD signals for trend confirmation"""
        try:
            prices = market_data.get('price_history', [])
            if len(prices) < 26:
                # FALLBACK: Use shorter EMA periods if insufficient data for standard MACD
                if len(prices) >= 21:
                    self.logger.warning(f"MACD fallback: Using EMA-9/21 instead of EMA-12/26 (have {len(prices)} bars)")
                    ema_9 = self._calculate_ema(prices, 9)
                    ema_21 = self._calculate_ema(prices, 21)
                    if ema_9 and ema_21:
                        macd_line = ema_9 - ema_21
                        signal = 'bullish' if macd_line > 0 else 'bearish'
                        strength = 0.6 if macd_line > 0 else 0.4  # Reduced confidence for fallback
                        return {
                            'macd_line': macd_line,
                            'macd_signal': signal,
                            'buy_strength': strength if signal == 'bullish' else 1 - strength,
                            'sell_strength': 1 - strength if signal == 'bullish' else strength,
                            'confidence': 0.5,  # Lower confidence for fallback method
                            'fallback_method': True
                        }
                return None
            
            # Calculate EMAs
            ema_12 = self._calculate_ema(prices, 12)
            ema_26 = self._calculate_ema(prices, 26)
            
            if ema_12 is None or ema_26 is None:
                return None
            
            # MACD line
            macd_line = ema_12 - ema_26
            
            # DYNAMIC MACD interpretation based on actual MACD value
            # Convert MACD line to strength based on magnitude relative to current price
            current_price = market_data.get('current_price', 1)
            macd_percentage = (macd_line / current_price) * 100  # Convert to percentage
            
            # Scale MACD strength based on percentage magnitude
            # Strong signals when MACD is >1% or <-1% of price
            abs_macd_pct = abs(macd_percentage)
            
            if macd_line > 0:
                # Bullish MACD - stronger signal with higher positive values
                signal = 'bullish'
                # Scale from 0.5 (barely positive) to 0.9 (strongly positive >2%)
                buy_strength = 0.5 + min(abs_macd_pct / 2.0, 0.4)  # 0.5 -> 0.9
                sell_strength = 1 - buy_strength
            else:
                # Bearish MACD - stronger signal with higher negative values
                signal = 'bearish'
                # Scale from 0.5 (barely negative) to 0.9 (strongly negative <-2%)
                sell_strength = 0.5 + min(abs_macd_pct / 2.0, 0.4)  # 0.5 -> 0.9
                buy_strength = 1 - sell_strength
            
            return {
                'macd_line': macd_line,
                'macd_signal': signal,
                'buy_strength': buy_strength,
                'sell_strength': sell_strength
            }
            
        except Exception as e:
            self.logger.error(f"❌ {symbol}: MACD calculation failed: {e}")
            return None
    
    def _calculate_bollinger_signals(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """Calculate Bollinger Bands signals for volatility breakouts"""
        try:
            prices = market_data.get('price_history', [])
            current_price = market_data.get('current_price', 0)
            
            if len(prices) < 20 or current_price <= 0:
                return None
            
            # Calculate 20-period SMA and standard deviation
            sma_20 = sum(prices[-20:]) / 20
            variance = sum([(price - sma_20) ** 2 for price in prices[-20:]]) / 20
            std_dev = variance ** 0.5
            
            # Bollinger Bands
            upper_band = sma_20 + (2 * std_dev)
            lower_band = sma_20 - (2 * std_dev)
            
            # DYNAMIC Bollinger Bands interpretation based on exact price position
            # Calculate where price sits within the bands (0 = lower band, 1 = upper band)
            band_range = upper_band - lower_band
            if band_range > 0:
                # Price position within bands (0.0 = at lower band, 1.0 = at upper band)
                band_position = (current_price - lower_band) / band_range
                
                if current_price > upper_band:
                    # Above upper band - overbought territory
                    excess_pct = (current_price - upper_band) / upper_band
                    position = 'above_upper'
                    buy_strength = max(0.1, 0.3 - min(excess_pct * 2, 0.2))  # 0.1-0.3 range
                    sell_strength = 1 - buy_strength
                elif current_price < lower_band:
                    # Below lower band - oversold territory  
                    deficit_pct = (lower_band - current_price) / lower_band
                    position = 'below_lower'
                    buy_strength = min(0.9, 0.7 + min(deficit_pct * 2, 0.2))  # 0.7-0.9 range
                    sell_strength = 1 - buy_strength
                else:
                    # Within bands - proportional to position
                    position = 'within_bands'
                    # Linear scale with peak buy strength near lower band
                    if band_position <= 0.5:
                        # Lower half - increasing buy strength as we approach lower band
                        buy_strength = 0.5 + (0.5 - band_position) * 0.6  # 0.5 -> 0.8
                    else:
                        # Upper half - decreasing buy strength as we approach upper band
                        buy_strength = 0.5 - (band_position - 0.5) * 0.6  # 0.5 -> 0.2
                    
                    sell_strength = 1 - buy_strength
            else:
                # Fallback if band calculation fails
                position = 'neutral'
                buy_strength = 0.5
                sell_strength = 0.5
            
            # Volatility score for compatibility
            band_width = (upper_band - lower_band) / sma_20
            volatility_score = min(band_width / 0.1, 1.0)  # Normalize to 0-1
            
            return {
                'position': position,
                'upper_band': upper_band,
                'lower_band': lower_band,
                'sma_20': sma_20,
                'buy_strength': buy_strength,
                'sell_strength': sell_strength,
                'volatility_score': volatility_score
            }
            
        except Exception as e:
            self.logger.error(f"❌ {symbol}: Bollinger Bands calculation failed: {e}")
            return None
    
    def _calculate_volume_confirmation(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """Calculate volume-based confirmation signals"""
        try:
            volume_24h = market_data.get('volume_24h', 0)
            avg_volume = market_data.get('avg_volume_7d', volume_24h)
            
            if avg_volume <= 0:
                return None
            
            volume_ratio = volume_24h / avg_volume
            
            # Research-backed volume interpretation
            if volume_ratio >= 2.0:
                confirmation = 'strong'
                strength_multiplier = 1.2
            elif volume_ratio >= 1.5:
                confirmation = 'moderate'
                strength_multiplier = 1.1
            elif volume_ratio >= 0.8:
                confirmation = 'neutral'
                strength_multiplier = 1.0
            else:
                confirmation = 'weak'
                strength_multiplier = 0.8
            
            volume_score = min(volume_ratio / 2.0, 1.0)  # Normalize
            
            return {
                'volume_ratio': volume_ratio,
                'confirmation': confirmation,
                'strength_multiplier': strength_multiplier,
                'volume_score': volume_score
            }
            
        except Exception as e:
            self.logger.error(f"❌ {symbol}: Volume confirmation calculation failed: {e}")
            return None
    
    def _calculate_directional_confidence(self, direction: str, rsi_analysis: Optional[Dict], macd_analysis: Optional[Dict], bollinger_analysis: Optional[Dict], volume_analysis: Optional[Dict]) -> float:
        """Calculate directional confidence using research-backed multi-indicator approach with fallback handling"""
        try:
            # Handle None indicators gracefully with neutral defaults
            if direction == 'BUY':
                # Combine buy strengths from available indicators
                rsi_strength = rsi_analysis.get('buy_strength', 0.5) if rsi_analysis else 0.5
                macd_strength = macd_analysis.get('buy_strength', 0.5) if macd_analysis else 0.5
                bollinger_strength = bollinger_analysis.get('buy_strength', 0.5) if bollinger_analysis else 0.5
            else:  # SELL
                # Combine sell strengths from available indicators
                rsi_strength = rsi_analysis.get('sell_strength', 0.5) if rsi_analysis else 0.5
                macd_strength = macd_analysis.get('sell_strength', 0.5) if macd_analysis else 0.5
                bollinger_strength = bollinger_analysis.get('sell_strength', 0.5) if bollinger_analysis else 0.5
            
            # Dynamic weights based on available indicators
            available_indicators = []
            if rsi_analysis is not None:
                available_indicators.append(('rsi', rsi_strength, 0.4))
            if macd_analysis is not None:
                available_indicators.append(('macd', macd_strength, 0.3))
            if bollinger_analysis is not None:
                available_indicators.append(('bollinger', bollinger_strength, 0.3))
            
            if available_indicators:
                # Normalize weights for available indicators
                total_weight = sum(weight for _, _, weight in available_indicators)
                normalized_weights = [(name, strength, weight/total_weight) for name, strength, weight in available_indicators]
                
                weighted_confidence = sum(strength * norm_weight for _, strength, norm_weight in normalized_weights)
            else:
                # Fallback if no indicators available
                weighted_confidence = 0.5
            
            # Volume confirmation multiplier
            volume_multiplier = volume_analysis.get('strength_multiplier', 1.0) if volume_analysis else 1.0
            final_confidence = weighted_confidence * volume_multiplier
            
            # Cap at 1.0 and ensure minimum threshold
            return max(0.1, min(final_confidence, 1.0))
            
        except Exception as e:
            self.logger.error(f"Error calculating directional confidence: {e}")
            return 0.5
    
    def _calculate_ema(self, prices: List[float], period: int) -> Optional[float]:
        """Calculate Exponential Moving Average"""
        try:
            if len(prices) < period:
                return None
            
            multiplier = 2 / (period + 1)
            ema = prices[0]
            
            for price in prices[1:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))
            
            return ema
            
        except Exception:
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
            self.logger.debug(f"🎯 {analysis.symbol}: Action determined = {action.value} (strategy={crypto_config['strategy'].value})")
            
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
                self.logger.warning(f"⚠️ {analysis.symbol}: Invalid quantity {adjusted_quantity} - cannot create opportunity"
                                  f" (base={base_quantity:.6f}, multiplier={crypto_config['position_size_multiplier']:.2f}, leverage={session_leverage:.2f})")
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
        """Determine buy/sell action based on RESEARCH-BACKED directional confidence"""
        # Use the pre-determined action from the comprehensive analysis
        if hasattr(analysis, 'primary_action'):
            return TradeAction.BUY if analysis.primary_action == 'BUY' else TradeAction.SELL
        
        # Fallback to momentum-based decision (should not be reached with new analysis)
        return TradeAction.BUY if analysis.momentum_score > 0.5 else TradeAction.SELL
    
    # Execution methods
    
    def _execute_crypto_trade(self, opportunity: TradeOpportunity) -> TradeResult:
        """Execute cryptocurrency trade with ML-critical parameter data collection"""
        try:
            # CRITICAL FIX: Validate before ALL order submissions (BUY and SELL)
            if opportunity.action == TradeAction.BUY:
                entry_price = opportunity.metadata.get('current_price', 0)
                is_valid, error_msg, _ = self.risk_manager.should_execute_trade(
                    opportunity.symbol, 
                    opportunity.strategy, 
                    opportunity.confidence,
                    entry_price
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
            
            # DEBUG: Log all positions to understand the filtering issue
            all_position_symbols = [getattr(pos, 'symbol', 'unknown') for pos in positions]
            self.logger.debug(f"📊 ALL POSITIONS: {all_position_symbols}")
            self.logger.debug(f"📊 SUPPORTED CRYPTO: {self.supported_symbols}")
            
            for position in positions:
                symbol = getattr(position, 'symbol', '')
                # FIXED: Be more inclusive in crypto position detection
                # Check if it's a crypto symbol (contains USD and matches common crypto patterns)
                is_crypto = ('USD' in symbol and 
                           (symbol in self.supported_symbols or 
                            any(crypto in symbol for crypto in ['BTC', 'ETH', 'SOL', 'DOT', 'LINK', 'MATIC', 'AVAX', 'UNI', 'AAVE'])))
                
                if is_crypto:
                    qty = getattr(position, 'qty', 0)
                    market_value = getattr(position, 'market_value', 0)
                    avg_entry_price = getattr(position, 'avg_entry_price', 0)
                    unrealized_pl = getattr(position, 'unrealized_pl', 0)
                    
                    # DEBUG: Log position detection
                    self.logger.debug(f"✅ CRYPTO POSITION FOUND: {symbol} - Value: ${market_value}")
                    
                    crypto_positions.append({
                        'symbol': symbol,
                        'qty': float(qty) if str(qty).replace('-', '').replace('.', '').isdigit() else 0.0,
                        'market_value': float(market_value) if str(market_value).replace('-', '').replace('.', '').isdigit() else 0.0,
                        'avg_entry_price': float(avg_entry_price) if str(avg_entry_price).replace('-', '').replace('.', '').isdigit() else 0.0,
                        'unrealized_pl': float(unrealized_pl) if str(unrealized_pl).replace('-', '').replace('.', '').isdigit() else 0.0
                    })
                else:
                    self.logger.debug(f"❌ FILTERED OUT: {symbol} (not crypto or not supported)")
            
            self.logger.info(f"📊 CRYPTO POSITIONS FOUND: {len(crypto_positions)} positions, Total Value: ${sum(pos['market_value'] for pos in crypto_positions):,.0f}")
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
        """Get cryptocurrency market data using enhanced real-time data sources"""
        try:
            # PRIMARY: Use enhanced data manager for real-time data if available
            if hasattr(self, 'enhanced_data_manager') and self.enhanced_data_manager:
                enhanced_data = self.enhanced_data_manager.get_enhanced_quote_data(symbol, include_fundamentals=False)
                if enhanced_data:
                    self.logger.debug(f"📊 {symbol}: Using enhanced real-time data from {enhanced_data.get('source')}")
                    return {
                        'price_history': enhanced_data.get('price_history', []),
                        'volume_history': enhanced_data.get('volume_history', []),
                        'high_history': enhanced_data.get('high_history', []),
                        'low_history': enhanced_data.get('low_history', []),
                        'current_price': enhanced_data['current_price'],
                        'real_time': enhanced_data.get('real_time', False),
                        'source': enhanced_data.get('source', 'enhanced_data_manager')
                    }
            
            # FALLBACK: Use Alpaca API for basic data
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
                
                # FIXED: Get 30h of hourly bars to ensure 26+ data points for MACD
                # MACD requires 26 periods minimum, so request extra hours to handle gaps
                start_time = datetime.now(timezone.utc) - timedelta(hours=30)  # 30 hours for safety
                start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')  # RFC3339 format
                
                bars = self.api.get_crypto_bars(
                    formatted_symbol,
                    start=start_time_str,
                    timeframe='1Hour',
                    limit=30  # Request 30 bars explicitly to ensure we get enough data
                )
                
                if bars and len(bars) > 0:
                    # Calculate real 24h metrics from bars
                    prices = [float(bar.c) for bar in bars]  # Close prices
                    volumes = [float(bar.v) for bar in bars]  # Volumes
                    
                    # COMPREHENSIVE ANALYSIS: Require sufficient data or use fallback methods
                    if not prices:
                        self.logger.error(f"❌ {symbol}: No price data available from API")
                        return None
                    elif len(prices) < 21:  # Minimum for any technical analysis
                        self.logger.error(f"❌ {symbol}: Insufficient price history ({len(prices)}/21+ bars needed) - skipping analysis")
                        return None
                    elif len(prices) < 26:  # Log warning but continue with fallback
                        self.logger.warning(f"⚠️ {symbol}: Limited price history ({len(prices)}/26 bars) - using fallback MACD calculation")
                    
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
                    
                    self.logger.info(f"📊 {symbol}: Real data from {len(prices)} bars - High: ${high_24h:.4f}, Low: ${low_24h:.4f}, Vol: {volume_24h:.0f}")
                    
                    # Return market data with calculated values
                    return {
                        'current_price': current_price,
                        'price_24h_ago': price_24h_ago,
                        'high_24h': high_24h,
                        'low_24h': low_24h,
                        'volume_24h': volume_24h,
                        'avg_volume_7d': avg_volume,  # Use real calculated average
                        'ma_20': ma_20,  # 20-day moving average for mean reversion
                        'volume_ratio': volume_ratio,  # Volume ratio for mean reversion
                        'price_history': prices  # Full price history for technical indicators
                    }
                else:
                    # NEVER USE SIMULATED DATA - return None for missing data
                    self.logger.error(f"❌ {symbol}: No real market data available from Alpaca API")
                    return None
                
            except Exception as api_error:
                self.logger.error(f"❌ {symbol}: Crypto bars API failed: {api_error}")
                return None
            
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
        """DISABLED: No forced pre-market closures for aggressive recovery strategy"""
        # FIXED: Portfolio down -2.55% - forced closures just caused -$657 and -$184 losses
        # Crypto is 24/7 and should run independently of stock market timing
        # Let winning positions run and only exit based on technical/profit criteria
        return False  # NEVER force close profitable crypto positions
    
    # Smart Allocation Methods for 5% Monthly ROI Target
    
    def _get_smart_allocation_limit(self) -> float:
        """Get smart allocation limit based on performance for 5% monthly ROI target"""
        try:
            if not self.smart_allocation_enabled:
                return 0.90  # Use 90% of buying power when smart allocation disabled
            
            # Get current performance metrics first
            current_win_rate = self._calculate_current_win_rate()
            monthly_performance = self._calculate_monthly_performance()
            
            self.logger.info(f"🎯 SMART ALLOCATION: Win rate: {current_win_rate:.1%}, Monthly: {monthly_performance:.1%}")
            
            # AGGRESSIVE BUY-THE-DIP MODE: When portfolio is down, be MORE aggressive, not less
            # Current portfolio: -2.55% needs aggressive recovery strategy
            if monthly_performance < -0.02:  # Down more than 2%
                if monthly_performance < -0.05:  # Down more than 5%
                    self.logger.warning(f"🔥 AGGRESSIVE RECOVERY MODE: Monthly loss {monthly_performance:.1%} - INCREASING to 60% allocation")
                    return 0.60  # AGGRESSIVE: 60% crypto for recovery
                else:
                    self.logger.warning(f"🔥 BUY-THE-DIP MODE: Monthly loss {monthly_performance:.1%} - INCREASING to 50% allocation")
                    return 0.50  # BUY-THE-DIP: 50% crypto when down 2-5%
            
            # MARKET HOURS: Allow reasonable crypto allocation (not emergency mode)
            if self._is_stock_market_open():
                # Check if we have profitable crypto positions
                crypto_positions = self._get_crypto_positions()
                profitable_positions = sum(1 for pos in crypto_positions if pos.get('unrealized_pl', 0) > 0)
                
                if profitable_positions > 0:
                    self.logger.info(f"💡 MARKET HOURS: {profitable_positions} profitable crypto positions - allowing 40% allocation")
                    return 0.40  # Allow higher allocation when crypto is profitable
                else:
                    self.logger.info("💡 MARKET HOURS: Standard 30% crypto allocation")
                    return 0.30  # Standard allocation during market hours
            
            # PERFORMANCE-BASED ALLOCATION TIERS (AFTER HOURS)
            if current_win_rate < 0.45:
                # Learning phase: Moderate allocation for learning
                return 0.35  # 35% max allocation (increased from 25%)
            elif current_win_rate < 0.60:
                # Stable phase: Target allocation for balanced growth
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