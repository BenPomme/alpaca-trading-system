"""
Stocks Trading Module - Modular Architecture

Standalone stocks trading module implementing enhanced stock strategies
with intelligence-driven analysis. Uses ONLY REAL MARKET DATA - no mock
or fake prices. Designed for aggressive 5-10% monthly returns through
leveraged ETFs, sector rotation, and momentum amplification.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time
import os

from modular.base_module import (
    TradingModule, ModuleConfig, TradeOpportunity, TradeResult,
    TradeAction, TradeStatus, ExitReason
)
from utils.pattern_recognition import PatternRecognition
from utils.news_sentiment import NewsSentimentAnalyzer # Example import


class StockStrategy(Enum):
    """Enhanced stock trading strategies"""
    LEVERAGED_ETFS = "leveraged_etfs"          # 3x ETFs for high confidence
    SECTOR_ROTATION = "sector_rotation"        # Sector-based momentum
    MOMENTUM_AMPLIFICATION = "momentum_amp"    # 2x sizing for conviction
    VOLATILITY_TRADING = "volatility_trading"  # VXX/SVXY based on regime
    CORE_EQUITY = "core_equity"               # Standard stock trading


class MarketRegime(Enum):
    """Market regime classifications"""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    UNCERTAIN = "uncertain"


@dataclass
class StockAnalysis:
    """Stock analysis results with intelligence components"""
    symbol: str
    current_price: float
    technical_score: float
    regime_score: float
    pattern_score: float
    combined_confidence: float
    recommended_strategy: StockStrategy
    position_multiplier: float
    
    @property
    def is_tradeable(self) -> bool:
        """Check if analysis meets minimum trading criteria - SIMPLIFIED"""
        return (self.combined_confidence > 0.30 and  # Much lower threshold
                self.current_price > 0 and
                self.technical_score > 0.20)  # Much lower threshold


@dataclass
class SymbolTier:
    """Symbol tier configuration"""
    tier_name: str
    symbols: List[str]
    priority: int
    confidence_threshold: float


class StocksModule(TradingModule):
    """
    Enhanced stocks trading module with intelligence-driven strategies.
    
    Features:
    - 4 enhanced strategies: Leveraged ETFs, Sector Rotation, Momentum, Volatility
    - Real market data integration with Alpaca API
    - Multi-factor intelligence analysis (technical + regime + pattern)
    - Tiered symbol universe with sector-aware selection
    - Market hours dependency for US equity trading
    - Aggressive position sizing for 5-10% monthly returns
    """
    
    def __init__(self,
                 config: ModuleConfig,
                 firebase_db,
                 risk_manager,
                 order_executor,
                 api_client,
                 intelligence_systems=None,
                 logger=None):
        super().__init__(config, firebase_db, risk_manager, order_executor, logger)
        
        self.api = api_client
        self.intelligence_systems = intelligence_systems or {}
        
        # INSTITUTIONAL STOCKS CONFIGURATION - Research-backed approach
        self.max_stock_allocation = 0.40  # REDUCED from 50% to 40% (better concentration)
        self.aggressive_multiplier = 1.5  # REDUCED from 2.0 to 1.5 (more conservative)
        self.market_tier = 2  # Focus on tier 1-2 only (core liquid stocks)
        
        # INSTITUTIONAL RISK MANAGEMENT
        self.stocks_stop_loss_pct = 0.08  # 8% stop loss (CRITICAL missing piece)
        self.stocks_profit_target_pct = 0.20  # Increased to 20% profit target for stocks
        self.monthly_rebalance_enabled = True  # Monthly momentum vs intraday scalping
        self.max_stock_positions = 25  # REDUCED from 40+ to 25 (institutional concentration)
        
        # Enhanced strategy symbols - ALL REAL SYMBOLS FOR LIVE TRADING
        self.strategy_symbols = {
            'leveraged_etfs': {
                'tech_3x': ['TQQQ'],        # 3x NASDAQ
                'broad_3x': ['UPRO'],       # 3x S&P 500
                'semi_3x': ['SOXL'],        # 3x Semiconductors
                'finance_3x': ['FAS'],      # 3x Financials
                'dow_3x': ['UDOW']          # 3x Dow Jones
            },
            'sector_etfs': {
                'technology': ['XLK'],      # Technology SPDR
                'healthcare': ['XLV'],      # Healthcare SPDR
                'financials': ['XLF'],      # Financials SPDR
                'energy': ['XLE'],          # Energy SPDR
                'consumer': ['XLY'],        # Consumer Discretionary SPDR
                'utilities': ['XLU'],       # Utilities SPDR
                'industrials': ['XLI'],     # Industrials SPDR
                'materials': ['XLB']        # Materials SPDR
            },
            'momentum_stocks': {
                'mega_cap': ['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
                'tech_growth': ['NVDA', 'TSLA', 'AMD', 'CRM'],
                'high_momentum': ['META', 'NFLX', 'ADBE', 'PYPL']
            },
            'volatility_symbols': {
                'vol_long': ['VXX'],        # Long volatility
                'vol_short': ['SVXY'],      # Short volatility
                'safe_haven': ['TLT', 'GLD']  # Bonds and Gold
            }
        }
        
        # INSTITUTIONAL SYMBOL UNIVERSE - Top 25 liquid stocks/ETFs only
        self.symbol_tiers = {
            1: SymbolTier("core_etfs", 
                         ['SPY', 'QQQ', 'IWM', 'XLK', 'XLV'], 1, 0.60),  # Core ETFs
            2: SymbolTier("mega_cap_stocks", 
                         ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 
                          'NFLX', 'AMD', 'CRM', 'V', 'MA', 'JPM', 'UNH', 'JNJ'], 2, 0.55)
            # REMOVED: Tiers 3 & 4 for concentration (was 40+ symbols, now 20)
            # Institutional focus: Quality over quantity, concentration over diversification
        }
        
        # Intelligence analysis weights
        self.intelligence_weights = {
            'technical': 0.40,    # RSI, MACD, Bollinger Bands
            'regime': 0.40,       # Bull/Bear/Sideways detection
            'pattern': 0.20       # Breakouts, support/resistance
        }
        
        # Strategy configuration - Optimized for intraday trading
        self.strategy_configs = {
            StockStrategy.LEVERAGED_ETFS: {
                'min_confidence': 0.65,  # Lowered for intraday opportunities
                'position_multiplier': 3.0,  # Increased for intraday leverage
                'max_allocation': 0.20,  # Increased for day trading
                'intraday_stop_loss': 0.03,  # Increased stop loss to 3% for intraday
                'intraday_profit_target': 0.04,  # Increased profit target to 4% for intraday
                'min_hold_minutes': 5  # Minimum 5 minute hold
            },
            StockStrategy.SECTOR_ROTATION: {
                'min_confidence': 0.55,  # Lowered for more opportunities
                'position_multiplier': 2.0,  # Increased for intraday
                'max_allocation': 0.30,  # Increased allocation
                'intraday_stop_loss': 0.035,  # Increased stop loss to 3.5%
                'intraday_profit_target': 0.05,  # Increased profit target to 5%
                'min_hold_minutes': 10
            },
            StockStrategy.MOMENTUM_AMPLIFICATION: {
                'min_confidence': 0.70,  # Slightly lowered
                'position_multiplier': 2.5,  # Increased for momentum
                'max_allocation': 0.25,  # Increased for momentum plays
                'intraday_stop_loss': 0.02,    # Increased stop loss to 2%
                'intraday_profit_target': 0.06,  # Increased profit target to 6%
                'min_hold_minutes': 3  # Very short hold for momentum
            },
            StockStrategy.VOLATILITY_TRADING: {
                'min_confidence': 0.50,  # Lowered for volatility opportunities
                'position_multiplier': 2.2,  # Increased for vol trading
                'max_allocation': 0.15,
                'intraday_stop_loss': 0.04,    # Increased stop loss to 4%
                'intraday_profit_target': 0.055,  # Increased profit target to 5.5%
                'min_hold_minutes': 8
            },
            StockStrategy.CORE_EQUITY: {
                'min_confidence': 0.50,  # Lowered for more opportunities
                'position_multiplier': 1.5,  # Increased for intraday
                'max_allocation': 0.35,  # Increased base allocation
                'intraday_stop_loss': 0.03,    # Increased stop loss to 3%
                'intraday_profit_target': 0.05,  # Increased profit target to 5%
                'min_hold_minutes': 8
            }
        }
        
        # INSTITUTIONAL TRADING CONFIGURATION - Monthly momentum approach
        self.institutional_config = {
            'cycle_frequency_seconds': 86400,  # DAILY cycles (vs 1-minute scalping)
            'max_monthly_rebalances': 4,  # Maximum 4 rebalances per month
            'momentum_period_months': 6,  # 6-month momentum (institutional standard)
            'monthly_loss_limit': 0.08,  # 8% monthly loss limit
            'position_hold_minimum_days': 7,  # Minimum 7-day hold period
            'concentration_limit': 25  # Maximum 25 positions (institutional standard)
        }
        
        # Time-of-day strategy matrix (Eastern Time)
        self.intraday_time_strategies = {
            (9.5, 10.5): {  # Opening hour (9:30-10:30 AM)
                'primary_strategy': StockStrategy.MOMENTUM_AMPLIFICATION,
                'confidence_adjustment': 0.05,  # Lower threshold for opening moves
                'volume_requirement': 1.5,  # 150% of average volume
                'position_multiplier': 1.3  # Larger positions for opening momentum
            },
            (10.5, 11.5): {  # Morning continuation (10:30-11:30 AM)
                'primary_strategy': StockStrategy.LEVERAGED_ETFS,
                'confidence_adjustment': 0.0,  # Standard confidence
                'volume_requirement': 1.2,
                'position_multiplier': 1.2
            },
            (11.5, 14.0): {  # Midday doldrums (11:30 AM-2:00 PM)
                'primary_strategy': StockStrategy.SECTOR_ROTATION,
                'confidence_adjustment': 0.1,  # Higher threshold for slower period
                'volume_requirement': 1.0,  # Normal volume OK
                'position_multiplier': 0.8  # Smaller positions in slow period
            },
            (14.0, 15.0): {  # Afternoon acceleration (2:00-3:00 PM)
                'primary_strategy': StockStrategy.MOMENTUM_AMPLIFICATION,
                'confidence_adjustment': 0.0,
                'volume_requirement': 1.3,
                'position_multiplier': 1.4  # Larger positions for afternoon moves
            },
            (15.0, 16.0): {  # Power hour (3:00-4:00 PM)
                'primary_strategy': StockStrategy.VOLATILITY_TRADING,
                'confidence_adjustment': -0.05,  # Lower threshold for power hour
                'volume_requirement': 1.8,  # High volume requirement
                'position_multiplier': 1.5  # Largest positions for power hour
            }
        }
        
        # Performance tracking
        self._strategy_performance = {strategy: {'trades': 0, 'wins': 0, 'total_pnl': 0.0} 
                                    for strategy in StockStrategy}
        self._daily_pnl = 0.0
        self._daily_trade_count = 0
        self._last_reset_date = datetime.now().date()
        
        total_symbols = sum(len(tier.symbols) for tier in self.symbol_tiers.values())
        self.logger.info(f"Stocks module initialized with {total_symbols} symbols across {len(self.symbol_tiers)} tiers")
        self.logger.info(f"Market tier: {self.market_tier}, Aggressive multiplier: {self.aggressive_multiplier}x")
        self.logger.info(f"Institutional trading: {self.institutional_config['cycle_frequency_seconds']}s cycles, "
                        f"Monthly momentum approach (vs intraday scalping)")
    
    @property
    def module_name(self) -> str:
        return "stocks"
    
    @property
    def supported_symbols(self) -> List[str]:
        """Get all supported stock symbols based on current tier"""
        symbols = []
        for tier_level in range(1, self.market_tier + 1):
            if tier_level in self.symbol_tiers:
                symbols.extend(self.symbol_tiers[tier_level].symbols)
        return list(set(symbols))  # Remove duplicates
    
    def analyze_opportunities(self) -> List[TradeOpportunity]:
        """
        Analyze stock opportunities using real market data and intelligence.
        Optimized for intraday trading with time-based strategy selection.
        
        Returns:
            List of stock trade opportunities
        """
        opportunities = []
        
        try:
            # Check if US market is open (stocks only trade during market hours)
            if not self._is_market_open():
                self.logger.info("US market closed - no stock opportunities")
                return opportunities
            
            # Reset daily counters if new trading day
            self._reset_daily_counters_if_needed()
            
            # Check daily limits for intraday trading
            if not self._check_intraday_trading_limits():
                return opportunities
            
            # Check current allocation
            current_allocation = self._get_current_stock_allocation()
            if current_allocation >= self.max_stock_allocation:
                self.logger.info(f"Stock allocation limit reached: {current_allocation:.1%} - SKIPPING NEW ENTRIES")
                self.logger.info("🚨 ALLOCATION LIMIT: Focusing on exit opportunities to free capital")
                return opportunities
            
            # Get intraday strategy and market regime
            intraday_strategy_info = self._get_intraday_strategy_for_current_time()
            market_regime = self._get_market_regime()
            
            # Get heat adjustment factor for position sizing
            heat_factor = self._get_heat_adjustment_factor()
            
            # Analyze symbols based on current tier and intraday strategy
            active_symbols = self._get_active_symbols()
            
            self.logger.info(f"Analyzing {len(active_symbols)} stocks for intraday opportunities "
                           f"(regime: {market_regime}, strategy: {intraday_strategy_info['primary_strategy'].value}, "
                           f"heat: {heat_factor:.2f})")
            
            for symbol in active_symbols:
                try:
                    analysis = self._analyze_stock_symbol_intraday(symbol, market_regime, intraday_strategy_info)
                    if analysis and analysis.is_tradeable:
                        # Apply intraday confidence threshold with time adjustment
                        adjusted_confidence_threshold = (
                            self.strategy_configs[analysis.recommended_strategy]['min_confidence'] - 
                            intraday_strategy_info['confidence_adjustment']
                        )
                        
                        if analysis.combined_confidence >= adjusted_confidence_threshold:
                            opportunity = self._create_intraday_stock_opportunity(analysis, heat_factor, intraday_strategy_info)
                            if opportunity:
                                opportunities.append(opportunity)
                
                except Exception as e:
                    self.logger.error(f"Error analyzing stock {symbol}: {e}")
                    continue
            
            self.logger.info(f"Found {len(opportunities)} intraday stock opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error in intraday stock opportunity analysis: {e}")
            return opportunities
    
    def execute_trades(self, opportunities: List[TradeOpportunity]) -> List[TradeResult]:
        """
        Execute validated stock trades using real market orders.
        
        Args:
            opportunities: List of validated stock opportunities
            
        Returns:
            List of trade execution results
        """
        results = []
        
        for opportunity in opportunities:
            try:
                # Verify market is still open before execution
                if not self._is_market_open():
                    result = TradeResult(
                        opportunity=opportunity,
                        status=TradeStatus.FAILED,
                        error_message="Market closed during execution"
                    )
                    results.append(result)
                    continue
                
                result = self._execute_stock_trade(opportunity)
                results.append(result)
                
                # Update strategy performance tracking
                strategy = StockStrategy(opportunity.strategy.replace('stock_', ''))
                self._strategy_performance[strategy]['trades'] += 1
                if result.success:
                    self._strategy_performance[strategy]['wins'] += 1
                
            except Exception as e:
                error_result = TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.FAILED,
                    error_message=f"Stock execution error: {e}"
                )
                results.append(error_result)
                self.logger.error(f"Failed to execute stock trade {opportunity.symbol}: {e}")
        
        return results
    
    def monitor_positions(self) -> List[TradeResult]:
        """
        Monitor existing stock positions for exit opportunities.
        Implements day trading logic - all positions closed before market close.
        
        Returns:
            List of exit trade results
        """
        exit_results = []
        
        try:
            # Get current stock positions
            positions = self._get_stock_positions()
            
            # Check if market is open
            if not self._is_market_open():
                return exit_results
            
            # Day Trading Logic: Check if we're near market close
            market_close_minutes = self._minutes_until_market_close()
            if market_close_minutes <= 30:  # Close all positions 30 minutes before market close
                self.logger.info(f"Day trading: Market closes in {market_close_minutes} minutes, closing all stock positions")
                for position in positions:
                    try:
                        # Force close position for day trading
                        exit_result = self._execute_stock_exit(position, {
                            'reason': ExitReason.END_OF_DAY,
                            'confidence': 1.0,
                            'exit_type': 'market_close'
                        })
                        if exit_result:
                            exit_results.append(exit_result)
                    except Exception as e:
                        self.logger.error(f"Error closing day trading position {position.get('symbol', 'unknown')}: {e}")
                return exit_results
            
            # Normal position monitoring during trading hours
            for position in positions:
                try:
                    exit_signal = self._analyze_stock_exit(position)
                    if exit_signal:
                        exit_result = self._execute_stock_exit(position, exit_signal)
                        if exit_result:
                            exit_results.append(exit_result)
                
                except Exception as e:
                    self.logger.error(f"Error monitoring stock position {position.get('symbol', 'unknown')}: {e}")
            
            # Log strategy performance periodically
            if len(positions) > 0:
                self._log_strategy_performance()
                
        except Exception as e:
            self.logger.error(f"Error monitoring stock positions: {e}")
        
        return exit_results
    
    # Stock analysis methods
    
    def _analyze_stock_symbol(self, symbol: str, market_regime: str) -> Optional[StockAnalysis]:
        """Analyze a stock symbol using real market data and intelligence"""
        try:
            # Get real current price - NO MOCK DATA
            current_price = self._get_real_stock_price(symbol)
            if not current_price or current_price <= 0:
                return None
            
            # Get intelligence scores from real analysis systems
            technical_score = self._get_technical_analysis(symbol, current_price)
            regime_score = self._get_regime_analysis(symbol, market_regime)
            pattern_score = self._get_pattern_analysis(symbol, current_price)
            
            # Calculate combined confidence using weighted scoring
            combined_confidence = (
                technical_score * self.intelligence_weights['technical'] +
                regime_score * self.intelligence_weights['regime'] +
                pattern_score * self.intelligence_weights['pattern']
            )
            
            # Determine best strategy for this symbol and confidence
            recommended_strategy, position_multiplier = self._select_stock_strategy(
                symbol, combined_confidence, market_regime
            )
            
            return StockAnalysis(
                symbol=symbol,
                current_price=current_price,
                technical_score=technical_score,
                regime_score=regime_score,
                pattern_score=pattern_score,
                combined_confidence=combined_confidence,
                recommended_strategy=recommended_strategy,
                position_multiplier=position_multiplier
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing stock symbol {symbol}: {e}")
            return None
    
    def _get_real_stock_price(self, symbol: str) -> float:
        """Get real current stock price from Alpaca API with data freshness validation"""
        try:
            quote = self.api.get_latest_quote(symbol)
            
            if quote:
                # Validate data freshness for minute-level trading
                if hasattr(quote, 'timestamp') and quote.timestamp:
                    from datetime import datetime, timezone
                    quote_time = quote.timestamp.replace(tzinfo=timezone.utc) if quote.timestamp.tzinfo is None else quote.timestamp
                    age_seconds = (datetime.now(timezone.utc) - quote_time).total_seconds()
                    
                    if age_seconds > 300:  # Warn if data is older than 5 minutes  
                        self.logger.warning(f"⚠️ {symbol}: Quote data is {age_seconds:.0f}s old (may impact trading accuracy)")
                    elif age_seconds > 60:  # Info if older than 1 minute
                        self.logger.info(f"🕐 {symbol}: Quote data is {age_seconds:.0f}s old")
                
                # Try different real price attributes
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
            self.logger.debug(f"Error getting real price for {symbol}: {e}")
            return 0.0
    
    def _get_technical_analysis(self, symbol: str, current_price: float) -> float:
        """Get technical analysis score from intelligence systems"""
        try:
            if 'technical_indicators' in self.intelligence_systems:
                # Use real technical analysis system
                technical_data = self.intelligence_systems['technical_indicators'].analyze_symbol(symbol)
                if technical_data:
                    return technical_data.get('composite_score', 0.5)
            
            # Fallback: basic technical analysis using real price data
            return self._calculate_basic_technical_score(symbol, current_price)
            
        except Exception as e:
            self.logger.debug(f"Error in technical analysis for {symbol}: {e}")
            return 0.5  # Neutral score
    
    def _get_regime_analysis(self, symbol: str, market_regime: str) -> float:
        """Get market regime analysis score"""
        try:
            if 'market_regime_detector' in self.intelligence_systems:
                # Use real regime detection system
                regime_data = self.intelligence_systems['market_regime_detector'].analyze_symbol_regime(symbol)
                if regime_data:
                    return regime_data.get('confidence', 0.5)
            
            # Fallback: regime-based scoring
            regime_scores = {
                'bull': 0.7,
                'sideways': 0.5,
                'bear': 0.3,
                'uncertain': 0.4
            }
            return regime_scores.get(market_regime, 0.5)
            
        except Exception as e:
            self.logger.debug(f"Error in regime analysis for {symbol}: {e}")
            return 0.5
    
    def _get_pattern_analysis(self, symbol: str, current_price: float) -> float:
        """Get pattern recognition analysis score"""
        try:
            if 'pattern_recognition' in self.intelligence_systems:
                # Use real pattern recognition system
                pattern_data = self.intelligence_systems['pattern_recognition'].analyze_patterns(symbol)
                if pattern_data:
                    return pattern_data.get('strength', 0.5)
            
            # Fallback: basic pattern analysis
            return self._calculate_basic_pattern_score(symbol, current_price)
            
        except Exception as e:
            self.logger.debug(f"Error in pattern analysis for {symbol}: {e}")
            return 0.5
    
    def _calculate_basic_technical_score(self, symbol: str, current_price: float) -> float:
        """Basic technical analysis using real market data"""
        try:
            # This would integrate with real technical indicators
            # For now, return neutral score - replace with actual technical analysis
            return 0.5
        except Exception:
            return 0.5
    
    def _calculate_basic_pattern_score(self, symbol: str, current_price: float) -> float:
        """Basic pattern analysis using real market data"""
        try:
            # This would integrate with real pattern recognition
            # For now, return neutral score - replace with actual pattern analysis
            return 0.5
        except Exception:
            return 0.5
    
    def _select_stock_strategy(self, symbol: str, confidence: float, 
                             market_regime: str) -> Tuple[StockStrategy, float]:
        """Select optimal stock strategy based on symbol and conditions"""
        try:
            # Check if symbol qualifies for enhanced strategies
            
            # Leveraged ETFs strategy for high confidence
            if (confidence >= 0.70 and 
                any(symbol in etfs for etfs in self.strategy_symbols['leveraged_etfs'].values())):
                return StockStrategy.LEVERAGED_ETFS, 2.5
            
            # Sector rotation for ETFs
            if (confidence >= 0.60 and 
                any(symbol in sectors for sectors in self.strategy_symbols['sector_etfs'].values())):
                return StockStrategy.SECTOR_ROTATION, 1.5
            
            # Momentum amplification for high-momentum stocks
            if (confidence >= 0.75 and 
                any(symbol in momentum for momentum in self.strategy_symbols['momentum_stocks'].values())):
                return StockStrategy.MOMENTUM_AMPLIFICATION, 2.0
            
            # Volatility trading for vol symbols
            if any(symbol in vol_symbols for vol_symbols in self.strategy_symbols['volatility_symbols'].values()):
                return StockStrategy.VOLATILITY_TRADING, 1.8
            
            # Default to core equity strategy
            return StockStrategy.CORE_EQUITY, 1.0
            
        except Exception as e:
            self.logger.debug(f"Error selecting strategy for {symbol}: {e}")
            return StockStrategy.CORE_EQUITY, 1.0
    
    def _create_stock_opportunity(self, analysis: StockAnalysis) -> Optional[TradeOpportunity]:
        """Create a trade opportunity from stock analysis"""
        try:
            # Determine trade direction based on combined analysis - SIMPLIFIED
            action = TradeAction.BUY if analysis.combined_confidence > 0.35 else TradeAction.SELL
            
            # Calculate position size with strategy multiplier
            base_quantity = self._calculate_stock_quantity(analysis.symbol, analysis.current_price)
            strategy_config = self.strategy_configs[analysis.recommended_strategy]
            adjusted_quantity = int(base_quantity * analysis.position_multiplier * strategy_config['position_multiplier'])
            
            if adjusted_quantity <= 0:
                return None
            
            opportunity = TradeOpportunity(
                symbol=analysis.symbol,
                action=action,
                quantity=adjusted_quantity,
                confidence=analysis.combined_confidence,
                strategy=f"stock_{analysis.recommended_strategy.value}",
                metadata={
                    'current_price': analysis.current_price,
                    'technical_score': analysis.technical_score,
                    'regime_score': analysis.regime_score,
                    'pattern_score': analysis.pattern_score,
                    'position_multiplier': analysis.position_multiplier,
                    'strategy': analysis.recommended_strategy.value,
                    'market_session': 'us_trading'
                },
                technical_score=analysis.technical_score,
                regime_score=analysis.regime_score,
                pattern_score=analysis.pattern_score,
                ml_score=analysis.combined_confidence,
                max_position_size=adjusted_quantity * analysis.current_price,
                stop_loss_pct=0.08,  # 8% stop loss for stocks
                profit_target_pct=0.15  # 15% profit target
            )
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error creating stock opportunity: {e}")
            return None
    
    # Trade execution methods
    
    def _execute_stock_trade(self, opportunity: TradeOpportunity) -> TradeResult:
        """Execute stock trade with ML-critical parameter data collection"""
        try:
            # Prepare order data for stock trading
            order_data = {
                'symbol': opportunity.symbol,
                'qty': int(opportunity.quantity), # Ensure quantity is an integer for stocks
                'side': 'buy' if opportunity.action == TradeAction.BUY else 'sell',
                'type': 'market',
                'time_in_force': 'day'  # Day orders for stocks
            }
            
            self.logger.info(f"Attempting stock trade for {opportunity.symbol}: {order_data['side']} {order_data['qty']} shares.")
            try:
                execution_result = self.order_executor.execute_order(order_data)
            except Exception as e:
                self.logger.error(f"Error executing stock order for {opportunity.symbol}: {e}")
                return None

            if not execution_result or not execution_result.get('success'):
                error_msg = execution_result.get('error', 'Unknown error during stock order submission')
                self.logger.error(f"Failed to submit stock order for {opportunity.symbol}: {error_msg}")
                return TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.FAILED,
                    order_id=None,
                    error_message=f"Order submission failed: {error_msg}"
                )

            order_id = execution_result.get('order_id')
            self.logger.info(f"Stock order {order_id} submitted for {opportunity.symbol}. Polling for fill...")

            # Poll for order status
            filled_avg_price = None
            actual_filled_qty = 0
            final_status = None
            max_retries = 60  # Poll for up to 60 seconds for stocks (market orders should fill quickly)
            retries = 0
            while retries < max_retries:
                time.sleep(1) # Wait 1 second between polls
                status_result = self.order_executor.get_order_status(order_id)
                if status_result and status_result.get('success'):
                    final_status = status_result.get('status')
                    if final_status == 'filled':
                        filled_avg_price = status_result.get('filled_avg_price')
                        actual_filled_qty = int(float(status_result.get('filled_qty', 0))) # Stocks are whole shares
                        self.logger.info(f"Stock order {order_id} for {opportunity.symbol} filled. Price: {filled_avg_price}, Qty: {actual_filled_qty}")
                        break
                    elif final_status in ['canceled', 'expired', 'rejected', 'done_for_day']:
                        self.logger.warning(f"Stock order {order_id} for {opportunity.symbol} did not fill. Final status: {final_status}")
                        break
                    # Add handling for partially_filled if necessary, though less common for market day orders for liquid stocks
                else:
                    self.logger.warning(f"Could not get status for stock order {order_id}. Retrying...")
                retries += 1
            
            result_status = TradeStatus.FAILED
            error_msg_result = None
            updated_opportunity = opportunity # Keep original opportunity by default

            if filled_avg_price and actual_filled_qty > 0:
                result_status = TradeStatus.EXECUTED
                # Update the opportunity within the result to reflect actual filled quantity
                updated_opportunity = dataclasses.replace(opportunity, quantity=actual_filled_qty)
            else:
                self.logger.error(f"Stock order {order_id} for {opportunity.symbol} did not fill adequately. Final status: {final_status}, Filled Qty: {actual_filled_qty}")
                error_msg_result = f"Order {order_id} failed to fill adequately. Status: {final_status}, Filled Qty: {actual_filled_qty}"

            # Create trade result
            # P&L is not calculated at the point of a single trade execution here; it's done on exit.
            # For entry trades, pnl should be None or 0. For exit trades handled by _execute_stock_exit, pnl will be calculated there.
            result = TradeResult(
                opportunity=updated_opportunity, # Use opportunity with actual filled qty
                status=result_status,
                order_id=order_id,
                execution_price=filled_avg_price if result_status == TradeStatus.EXECUTED else None,
                execution_time=datetime.now(), # Ideally, get execution time from order status if available
                error_message=error_msg_result,
                pnl=None, # P&L is handled by the calling exit function or remains None for entries
                pnl_pct=None
            )
            
            # 🧠 ML DATA COLLECTION: Save trade with enhanced parameter context
            # result.success checks (status == EXECUTED and pnl > 0). For entries, pnl is None, so result.success will be False here.
            # The ML data saving logic might need adjustment if it expects success on mere execution for entries.
            # However, _save_ml_enhanced_stock_trade already sets profit_loss=0.0 for entries, which is fine.
            if result.status == TradeStatus.EXECUTED: # Check for execution, not profitability, for saving entry trade ML data
                trade_id = self._save_ml_enhanced_stock_trade(updated_opportunity, result) # Pass updated_opportunity
                # Store trade_id in result metadata for position tracking
                if not hasattr(result, 'metadata'):
                    result.metadata = {}
                result.metadata['ml_trade_id'] = trade_id
            
            return result
                
        except Exception as e:
            self.logger.error(f"Stock execution error for {opportunity.symbol}: {e}", exc_info=True)
            return TradeResult(
                opportunity=opportunity,
                status=TradeStatus.ERROR, # Changed from FAILED to ERROR for clarity
                order_id=None,
                error_message=f"Stock execution error: {str(e)}"
            )
    
    def _save_ml_enhanced_stock_trade(self, opportunity: TradeOpportunity, result: TradeResult):
        """Save stock trade with ML-critical parameter data for optimization"""
        try:
            # Extract strategy information from opportunity metadata
            strategy_name = opportunity.metadata.get('strategy', 'unknown')
            regime_score = opportunity.metadata.get('regime_score', 0)
            technical_score = opportunity.metadata.get('technical_score', 0)
            pattern_score = opportunity.metadata.get('pattern_score', 0)
            position_multiplier = opportunity.metadata.get('position_multiplier', 1.0)
            current_price = opportunity.metadata.get('current_price', 0)
            
            # Get market regime information
            market_regime = self._get_market_regime()
            leverage_factor = self._get_strategy_leverage_factor(strategy_name)
            
            # Create entry parameters for ML learning
            entry_parameters = self.ml_data_collector.create_entry_parameters(
                confidence_threshold_used=opportunity.confidence,
                position_size_multiplier=position_multiplier,
                regime_confidence=regime_score,
                technical_confidence=technical_score,
                pattern_confidence=pattern_score,
                ml_strategy_selection=True,
                leverage_applied=leverage_factor,
                stock_strategy=strategy_name
            )
            
            # Create stocks-specific module parameters
            module_specific_params = self.ml_data_collector.create_stocks_module_params(
                regime_type=market_regime.get('type', 'neutral'),
                leverage_factor=leverage_factor,
                sector_momentum=self._get_sector_momentum(opportunity.symbol),
                intelligence_weights_used=self.intelligence_weights,
                strategy_specific_config=self._get_strategy_config(strategy_name),
                symbol_tier=self._get_symbol_tier(opportunity.symbol),
                market_session='us_trading',
                enhanced_strategy_applied=self._is_enhanced_strategy(strategy_name),
                confidence_threshold_for_strategy=self._get_strategy_confidence_threshold(strategy_name)
            )
            
            # Create market context
            market_context = self.ml_data_collector.create_market_context(
                us_market_open=self._is_market_open(),
                crypto_session=None,
                market_hours_type="stock_trading_hours"
            )
            
            # Create parameter performance context
            parameter_performance = self.ml_data_collector.create_parameter_performance(
                confidence_accuracy=opportunity.confidence,
                threshold_effectiveness=1.0 if opportunity.confidence >= self.config.min_confidence else 0.0,
                regime_multiplier_success=True,  # Strategy was selected
                alternative_outcomes={
                    'strategy_leveraged_etfs': 'would_have_triggered' if opportunity.confidence >= 0.70 else 'would_not_have_triggered',
                    'strategy_momentum_amp': 'would_have_triggered' if opportunity.confidence >= 0.75 else 'would_not_have_triggered',
                    'strategy_sector_rotation': 'would_have_triggered' if opportunity.confidence >= 0.60 else 'would_not_have_triggered',
                    'strategy_core_equity': 'would_have_triggered' if opportunity.confidence >= 0.55 else 'would_not_have_triggered'
                },
                parameter_attribution={
                    'technical_weight_contribution': self.intelligence_weights['technical'],
                    'regime_weight_contribution': self.intelligence_weights['regime'],
                    'pattern_weight_contribution': self.intelligence_weights['pattern'],
                    'position_multiplier_impact': position_multiplier,
                    'leverage_contribution': leverage_factor,
                    'strategy_confidence_requirement': self._get_strategy_confidence_threshold(strategy_name)
                }
            )
            
            # Create complete ML trade data
            ml_trade_data = self.ml_data_collector.create_ml_trade_data(
                symbol=opportunity.symbol,
                side='BUY' if opportunity.action == TradeAction.BUY else 'SELL',
                quantity=opportunity.quantity,
                price=result.execution_price or current_price,
                strategy=opportunity.strategy,
                confidence=opportunity.confidence,
                entry_parameters=entry_parameters,
                module_specific_params=module_specific_params,
                market_context=market_context,
                parameter_performance=parameter_performance,
                profit_loss=0.0,  # Will be updated on exit
                exit_reason=None  # Entry trade
            )
            
            # Add stocks-specific fields
            ml_trade_data_dict = ml_trade_data.to_dict()
            ml_trade_data_dict['asset_type'] = 'stock'
            ml_trade_data_dict['stock_strategy'] = strategy_name
            ml_trade_data_dict['market_regime'] = market_regime.get('type', 'neutral')
            ml_trade_data_dict['symbol_tier'] = self._get_symbol_tier(opportunity.symbol)
            
            # Save to Firebase with ML enhancements
            trade_id = self.save_ml_enhanced_trade(ml_trade_data_dict)
            
            # Record parameter effectiveness for ML optimization
            self.record_parameter_effectiveness(
                parameter_type='stock_strategy_selection',
                parameter_value=strategy_name,
                trade_outcome={
                    'symbol': opportunity.symbol,
                    'strategy': strategy_name,
                    'confidence': opportunity.confidence,
                    'executed': result.success,
                    'regime': market_regime.get('type', 'neutral')
                },
                success=result.success,
                profit_loss=0.0  # Will be updated on exit
            )
            
            # Record confidence threshold effectiveness
            self.record_parameter_effectiveness(
                parameter_type='stock_confidence_threshold',
                parameter_value=opportunity.confidence,
                trade_outcome={
                    'symbol': opportunity.symbol,
                    'strategy': strategy_name,
                    'leverage': leverage_factor,
                    'executed': result.success
                },
                success=result.success,
                profit_loss=0.0
            )
            
            # Record intelligence weights effectiveness
            self.record_parameter_effectiveness(
                parameter_type='intelligence_weights',
                parameter_value=self.intelligence_weights,
                trade_outcome={
                    'symbol': opportunity.symbol,
                    'technical_score': technical_score,
                    'regime_score': regime_score,
                    'pattern_score': pattern_score,
                    'executed': result.success
                },
                success=result.success,
                profit_loss=0.0
            )
            
            self.logger.info(f"💾 Stock ML data saved: {opportunity.symbol} ({strategy_name}) - {trade_id}")
            return trade_id
            
        except Exception as e:
            self.logger.error(f"Error saving ML stock trade data: {e}")
            return None
    
    def _get_strategy_leverage_factor(self, strategy_name: str) -> float:
        """Get leverage factor for a strategy"""
        try:
            if 'leveraged_etfs' in strategy_name:
                return 3.0  # 3x leveraged ETFs
            elif 'momentum_amp' in strategy_name:
                return 2.0  # 2x momentum amplification
            elif 'sector_rotation' in strategy_name:
                return 1.5  # 1.5x sector rotation
            elif 'volatility_trading' in strategy_name:
                return 1.8  # 1.8x volatility trading
            else:
                return 1.0  # Core equity
        except:
            return 1.0
    
    def _get_sector_momentum(self, symbol: str) -> float:
        """Get sector momentum for a symbol"""
        try:
            # Simplified sector momentum calculation
            if symbol in ['XLK', 'TQQQ', 'QQQ']:  # Tech
                return 0.75
            elif symbol in ['XLV', 'XLF']:  # Healthcare, Financial
                return 0.65
            elif symbol in ['XLE', 'XLY']:  # Energy, Consumer
                return 0.55
            else:
                return 0.60  # Default
        except:
            return 0.60
    
    def _get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """Get configuration for a strategy"""
        try:
            if 'leveraged_etfs' in strategy_name:
                return {'type': 'leveraged', 'target_symbols': ['TQQQ', 'UPRO', 'SOXL'], 'min_confidence': 0.70}
            elif 'momentum_amp' in strategy_name:
                return {'type': 'momentum', 'amplification': 2.0, 'min_confidence': 0.75}
            elif 'sector_rotation' in strategy_name:
                return {'type': 'sector', 'sectors': ['tech', 'healthcare', 'financial'], 'min_confidence': 0.60}
            elif 'volatility_trading' in strategy_name:
                return {'type': 'volatility', 'instruments': ['VXX', 'SVXY'], 'min_confidence': 0.55}
            else:
                return {'type': 'core_equity', 'min_confidence': 0.55}
        except:
            return {'type': 'unknown', 'min_confidence': 0.55}
    
    def _get_symbol_tier(self, symbol: str) -> int:
        """Get symbol tier for classification"""
        try:
            return self.symbol_tiers.get(symbol, 4)  # Default to tier 4
        except:
            return 4
    
    def _is_enhanced_strategy(self, strategy_name: str) -> bool:
        """Check if this is an enhanced strategy"""
        enhanced_strategies = ['leveraged_etfs', 'momentum_amp', 'volatility_trading']
        return any(enhanced in strategy_name for enhanced in enhanced_strategies)
    
    def _get_strategy_confidence_threshold(self, strategy_name: str) -> float:
        """Get confidence threshold for a strategy - SIMPLIFIED for more trading"""
        # SIMPLIFIED: Use same low threshold for all strategies to enable trading
        return 0.45  # Much lower threshold for all strategies
    
    # Position monitoring methods
    
    def _get_stock_positions(self) -> List[Dict]:
        """Get current stock positions (excluding crypto and options)"""
        try:
            positions = self.api.list_positions()
            stock_positions = []
            
            for position in positions:
                symbol = getattr(position, 'symbol', '')
                # Filter for stock symbols (exclude crypto USD pairs and long option symbols)
                if (symbol in self.supported_symbols and 
                    'USD' not in symbol and 
                    len(symbol) <= 6):  # Most stock symbols are <= 6 chars
                    
                    qty = getattr(position, 'qty', 0)
                    market_value = getattr(position, 'market_value', 0)
                    avg_entry_price = getattr(position, 'avg_entry_price', 0)
                    unrealized_pl = getattr(position, 'unrealized_pl', 0)
                    
                    stock_positions.append({
                        'symbol': symbol,
                        'qty': float(qty) if str(qty).replace('-', '').replace('.', '').isdigit() else 0.0,
                        'market_value': float(market_value) if str(market_value).replace('-', '').replace('.', '').isdigit() else 0.0,
                        'avg_entry_price': float(avg_entry_price) if str(avg_entry_price).replace('-', '').replace('.', '').isdigit() else 0.0,
                        'unrealized_pl': float(unrealized_pl) if str(unrealized_pl).replace('-', '').replace('.', '').isdigit() else 0.0
                    })
            
            return stock_positions
            
        except Exception as e:
            self.logger.error(f"Error getting stock positions: {e}")
            return []
    
    def _analyze_stock_exit(self, position: Dict) -> Optional[str]:
        """Analyze if stock position should be exited with intraday optimization"""
        try:
            unrealized_pl = position.get('unrealized_pl', 0)
            market_value = abs(position.get('market_value', 1))
            symbol = position.get('symbol', '')
            
            if market_value == 0:
                return None
            
            unrealized_pl_pct = unrealized_pl / market_value
            
            # Check if we're over allocation limit - be MORE aggressive with exits
            current_allocation = self._get_current_stock_allocation()
            over_allocation = current_allocation >= self.max_stock_allocation
            
            if over_allocation:
                # AGGRESSIVE EXIT MODE when over-allocated
                if unrealized_pl_pct >= 0.015:  # 1.5% profit when over-allocated (stocks move faster)
                    return 'over_allocation_profit'
                elif unrealized_pl_pct <= -0.025:  # 2.5% stop loss when over-allocated
                    return 'over_allocation_stop_loss'
                # When severely over-allocated, exit break-even positions
                elif abs(unrealized_pl_pct) <= 0.003:  # Within 0.3% of break-even
                    return 'over_allocation_rebalance'
            
            # Get position age (simplified - would track actual entry time)
            position_age_minutes = 30  # Estimate position age
            
            # Determine if this is an intraday position (all stocks are now intraday)
            is_intraday = True
            
            if is_intraday:
                # Use intraday exit parameters
                strategy = self._infer_position_strategy(symbol)
                strategy_config = self.strategy_configs.get(strategy)
                
                if strategy_config:
                    min_hold_minutes = strategy_config.get('min_hold_minutes', 8)
                    intraday_stop = strategy_config.get('intraday_stop_loss', 0.025)
                    intraday_target = strategy_config.get('intraday_profit_target', 0.03)
                    
                    # Check minimum hold time
                    if position_age_minutes < min_hold_minutes:
                        # Only exit on extreme moves before minimum hold
                        if unrealized_pl_pct <= -intraday_stop * 2:  # 2x stop loss
                            return 'emergency_stop'
                        elif unrealized_pl_pct >= intraday_target * 1.5:  # 1.5x target
                            return 'quick_profit'
                        return None
                    
                    # Normal intraday exits after minimum hold
                    if unrealized_pl_pct >= intraday_target:
                        return 'intraday_profit'
                    elif unrealized_pl_pct <= -intraday_stop:
                        return 'intraday_stop'
            
            # INSTITUTIONAL EXIT CONDITIONS - Research-backed risk management
            
            # 1. PROFIT TARGET - Take profits at 15%
            if unrealized_pl_pct >= self.stocks_profit_target_pct:  # 15% profit target
                self.logger.info(f"🎯 STOCKS PROFIT TARGET: {symbol} at {unrealized_pl_pct:.1%}")
                return 'institutional_profit_target'
            
            # 2. STOP LOSS - Limit losses at 8% (CRITICAL missing institutional control)
            elif unrealized_pl_pct <= -self.stocks_stop_loss_pct:  # 8% stop loss
                self.logger.warning(f"🚨 STOCKS STOP LOSS: {symbol} at {unrealized_pl_pct:.1%}")
                return 'institutional_stop_loss'
            
            # 3. MOMENTUM REVERSAL - Exit if 6-month momentum turns negative
            elif self._is_momentum_reversal(symbol, position):
                self.logger.info(f"📉 MOMENTUM REVERSAL: {symbol} - 6-month trend broken")
                return 'momentum_reversal'
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing intraday stock exit: {e}")
            return None
    
    def _execute_stock_exit(self, position: Dict, exit_reason: str) -> Optional[TradeResult]:
        """Execute stock position exit"""
        try:
            symbol = position.get('symbol')
            if not symbol:
                self.logger.error("Cannot execute stock exit: position symbol is missing.")
                return None

            # Original quantity from the position dict before attempting to close
            # This is primarily for creating the initial TradeOpportunity
            original_qty_from_position = abs(float(position.get('qty', 0)))
            
            if original_qty_from_position == 0:
                self.logger.warning(f"Attempting to exit stock position with zero quantity for {symbol}")
                return None
            
            # Determine side based on the position's quantity sign
            side_to_close = TradeAction.SELL if float(position.get('qty', 0)) > 0 else TradeAction.BUY

            # Create exit opportunity with the original quantity we intend to close
            exit_opportunity = TradeOpportunity(
                symbol=symbol,
                action=side_to_close,
                quantity=original_qty_from_position, # This is the target quantity to close
                confidence=0.6,  # Medium confidence for exits, can be refined
                strategy='stock_exit'
            )
            
            # Execute exit - _execute_stock_trade now handles polling and returns actual fill price
            # and updates opportunity.quantity in the result to actual_filled_qty.
            result = self._execute_stock_trade(exit_opportunity)
            
            # Check if the trade execution itself failed (e.g., order rejected, no fill)
            if not result or result.status != TradeStatus.EXECUTED:
                self.logger.error(f"Stock exit trade for {symbol} failed or was not executed. Status: {result.status if result else 'N/A'}")
                # Return the result from _execute_stock_trade, which contains error details
                return result 

            # At this point, result.status == TradeStatus.EXECUTED
            # result.execution_price is the actual average fill price
            # result.opportunity.quantity is the actual filled quantity

            actual_filled_qty = result.opportunity.quantity
            exit_fill_price = result.execution_price

            if actual_filled_qty == 0 or exit_fill_price is None:
                self.logger.error(f"Stock exit for {symbol} reported as EXECUTED but has zero filled quantity or no fill price.")
                # Update result to reflect this inconsistency if not already FAILED
                result.status = TradeStatus.FAILED
                result.error_message = result.error_message or "Executed with zero quantity or no fill price."
                return result

            # Calculate REAL P&L
            entry_price = float(position.get('avg_entry_price', 0))
            if entry_price == 0:
                self.logger.warning(f"avg_entry_price for stock {symbol} is 0. P&L calculation will be inaccurate.")

            # P&L = (exit_price - entry_price) * quantity_sold (for long)
            # P&L = (entry_price - exit_price) * quantity_bought_back (for short)
            if side_to_close == TradeAction.SELL: # Closing a long position
                realized_pnl = (exit_fill_price - entry_price) * actual_filled_qty
            else: # Closing a short position (buy to cover)
                realized_pnl = (entry_price - exit_fill_price) * actual_filled_qty
            
            cost_basis = entry_price * actual_filled_qty
            pnl_pct = (realized_pnl / cost_basis) * 100 if cost_basis != 0 else 0

            # Update the result object with the calculated P&L and correct exit reason
            result.pnl = realized_pnl
            result.pnl_pct = pnl_pct
            result.exit_reason = self._get_exit_reason_enum(exit_reason)
            
            # Now, result.success will correctly evaluate based on the new P&L
            if result.success: # This now checks pnl > 0
                self.logger.info(f"Profitable stock exit: {symbol} {exit_reason} P&L: ${result.pnl:.2f} ({result.pnl_pct:.1%})")
            else:
                self.logger.info(f"Stock exit (loss/breakeven): {symbol} {exit_reason} P&L: ${result.pnl:.2f} ({result.pnl_pct:.1%})")

            # Update daily P&L tracking for intraday trading
            # This uses the now-correct result.pnl_pct
            if result.pnl is not None: # Ensure pnl is calculated
                self._daily_pnl += result.pnl_pct # pnl_pct is already a percentage
                self._daily_trade_count += 1
            
            # Update strategy performance
            # This uses the now-correct result.pnl
            strategy_name_for_metrics = self._infer_position_strategy(symbol) 
            if strategy_name_for_metrics in self._strategy_performance:
                self._strategy_performance[strategy_name_for_metrics]['trades'] = self._strategy_performance[strategy_name_for_metrics].get('trades', 0) + 1
                if result.pnl is not None and result.pnl > 0:
                    self._strategy_performance[strategy_name_for_metrics]['wins'] = self._strategy_performance[strategy_name_for_metrics].get('wins', 0) + 1
                self._strategy_performance[strategy_name_for_metrics]['total_pnl'] = self._strategy_performance[strategy_name_for_metrics].get('total_pnl', 0) + (result.pnl or 0)
            
            self.logger.info(f"Stock exit processed: {symbol} {exit_reason} P&L: ${result.pnl:.2f} ({result.pnl_pct:.1%}) "
                           f"Daily P&L Sum (pct): {self._daily_pnl:.2f}% Trades: {self._daily_trade_count}")
            
            return result # This result now has accurate P&L
            
        except Exception as e:
            self.logger.error(f"Error executing stock exit for {position.get('symbol', 'UNKNOWN')}: {e}", exc_info=True)
            # Fallback if something unexpected happens
            symbol = position.get('symbol', 'UNKNOWN_STOCK')
            qty = abs(float(position.get('qty', 0)))
            action_on_error = TradeAction.SELL if float(position.get('qty', 0)) > 0 else TradeAction.BUY

            error_opportunity = TradeOpportunity(
                symbol=symbol,
                action=action_on_error,
                quantity=qty if qty > 0 else 1,
                confidence=0.0,
                strategy='stock_exit_error'
            )
            return TradeResult(
                opportunity=error_opportunity,
                status=TradeStatus.ERROR,
                order_id=None,
                error_message=str(e)
            )
    
    # Utility methods
    
    def _is_market_open(self) -> bool:
        """Check if US stock market is currently open"""
        try:
            if not self.api:
                # Fallback timezone check if no API
                import datetime
                import pytz
                et = pytz.timezone('US/Eastern')
                now_et = datetime.datetime.now(et)
                is_weekday = now_et.weekday() < 5  # Monday=0, Friday=4
                is_trading_hours = 9 <= now_et.hour < 16  # 9 AM to 4 PM ET
                self.logger.info(f"Market hours fallback: {now_et.strftime('%Y-%m-%d %H:%M %Z')}, weekday: {is_weekday}, hours: {is_trading_hours}")
                return is_weekday and is_trading_hours
            
            clock = self.api.get_clock()
            is_open = getattr(clock, 'is_open', False)
            self.logger.info(f"Market status from Alpaca: {is_open} (clock: {clock})")
            return is_open
        except Exception as e:
            self.logger.error(f"Error checking market hours: {e}")
            # Fallback to timezone calculation
            import datetime
            import pytz
            et = pytz.timezone('US/Eastern')
            now_et = datetime.datetime.now(et)
            is_weekday = now_et.weekday() < 5
            is_trading_hours = 9 <= now_et.hour < 16
            self.logger.warning(f"Using fallback market hours: {now_et.strftime('%Y-%m-%d %H:%M %Z')}, open: {is_weekday and is_trading_hours}")
            return is_weekday and is_trading_hours
    
    def _minutes_until_market_close(self) -> int:
        """Get minutes until market close for day trading logic"""
        try:
            clock = self.api.get_clock()
            if hasattr(clock, 'next_close'):
                from datetime import datetime
                import pytz
                
                # Convert to timezone-aware datetime
                now = datetime.now(pytz.timezone('America/New_York'))
                close_time = clock.next_close.replace(tzinfo=pytz.timezone('America/New_York'))
                
                time_diff = close_time - now
                minutes_until_close = int(time_diff.total_seconds() / 60)
                
                return max(0, minutes_until_close)
            return 240  # Default 4 hours if unable to determine
        except Exception as e:
            self.logger.debug(f"Error calculating time until market close: {e}")
            return 240  # Default to 4 hours
    
    def _get_market_regime(self) -> str:
        """Get current market regime"""
        try:
            if 'market_regime_detector' in self.intelligence_systems:
                regime_data = self.intelligence_systems['market_regime_detector'].get_current_regime()
                if regime_data:
                    return regime_data.get('regime', 'sideways')
            return 'sideways'  # Default regime
        except Exception:
            return 'sideways'
    
    def _get_active_symbols(self) -> List[str]:
        """Get active symbols based on current market tier"""
        try:
            symbols = []
            for tier_level in range(1, min(self.market_tier + 1, 5)):
                if tier_level in self.symbol_tiers:
                    symbols.extend(self.symbol_tiers[tier_level].symbols)
            
            # Remove duplicates and return
            return list(set(symbols))
        except Exception as e:
            self.logger.error(f"Error getting active symbols: {e}")
            return self.symbol_tiers[1].symbols  # Fallback to core ETFs
    
    def _calculate_stock_quantity(self, symbol: str, price: float) -> float:
        """Calculate stock quantity with day trading leverage"""
        try:
            account = self.api.get_account()
            
            # Use day trading buying power for leverage
            if hasattr(account, 'daytrading_buying_power'):
                buying_power = float(getattr(account, 'daytrading_buying_power', 0))
                self.logger.debug(f"Using day trading buying power: ${buying_power:,.2f}")
            elif hasattr(account, 'regt_buying_power'):
                buying_power = float(getattr(account, 'regt_buying_power', 0))
                self.logger.debug(f"Using RegT buying power: ${buying_power:,.2f}")
            else:
                portfolio_value = float(getattr(account, 'portfolio_value', 100000))
                buying_power = portfolio_value * 2.0  # Assume 2x leverage
                self.logger.debug(f"Using estimated buying power: ${buying_power:,.2f}")
            
            # Day trading allocation per trade (2.5% of buying power for aggressive leverage)
            leverage_allocation = 0.025
            max_position_value = buying_power * leverage_allocation * self.aggressive_multiplier
            
            # Calculate whole share quantity leveraging available buying power
            quantity = max_position_value / price if price > 0 else 0
            calculated_shares = int(quantity)
            
            self.logger.debug(f"Day trading calculation for {symbol}: buying_power=${buying_power:,.2f}, "
                            f"allocation={leverage_allocation:.1%}, position_value=${max_position_value:,.2f}, "
                            f"shares={calculated_shares}")
            
            return calculated_shares
            
        except Exception as e:
            self.logger.error(f"Error calculating leveraged stock quantity: {e}")
            return 0
    
    def _get_current_stock_allocation(self) -> float:
        """Get current stock allocation percentage"""
        try:
            account = self.api.get_account()
            portfolio_value = float(getattr(account, 'portfolio_value', 100000))
            
            stock_positions = self._get_stock_positions()
            stock_value = sum(abs(pos.get('market_value', 0)) for pos in stock_positions)
            
            return stock_value / portfolio_value if portfolio_value > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating stock allocation: {e}")
            return 0.0
    
    def _infer_position_strategy(self, symbol: str) -> StockStrategy:
        """Infer which strategy a position likely belongs to"""
        try:
            # Check enhanced strategy symbols with proper mapping
            strategy_mapping = {
                'leveraged_etfs': StockStrategy.LEVERAGED_ETFS,
                'sector_etfs': StockStrategy.SECTOR_ROTATION,
                'momentum_stocks': StockStrategy.MOMENTUM_AMPLIFICATION,
                'volatility_symbols': StockStrategy.VOLATILITY_TRADING
            }
            
            for strategy_name, symbol_groups in self.strategy_symbols.items():
                for group_symbols in symbol_groups.values():
                    if symbol in group_symbols:
                        return strategy_mapping.get(strategy_name, StockStrategy.CORE_EQUITY)
            
            return StockStrategy.CORE_EQUITY
        except Exception:
            return StockStrategy.CORE_EQUITY
    
    def _get_exit_reason_enum(self, exit_reason: str) -> ExitReason:
        """Convert exit reason string to enum"""
        mapping = {
            'profit_target': ExitReason.PROFIT_TARGET,
            'stop_loss': ExitReason.STOP_LOSS,
            'leveraged_profit': ExitReason.PROFIT_TARGET,
            'leveraged_stop': ExitReason.STOP_LOSS
        }
        return mapping.get(exit_reason, ExitReason.STRATEGY_SIGNAL)
    
    def _log_strategy_performance(self):
        """Log strategy-based performance metrics"""
        try:
            for strategy, stats in self._strategy_performance.items():
                if stats['trades'] > 0:
                    win_rate = stats['wins'] / stats['trades']
                    avg_pnl = stats['total_pnl'] / stats['trades']
                    self.logger.info(f"Strategy {strategy.value}: {stats['trades']} trades, "
                                   f"{win_rate:.1%} win rate, ${avg_pnl:.2f} avg P&L")
        except Exception as e:
            self.logger.debug(f"Error logging strategy performance: {e}")
    
    def get_strategy_summary(self) -> Dict[str, Any]:
        """Get current strategy performance and configuration"""
        return {
            'module_name': self.module_name,
            'market_tier': self.market_tier,
            'supported_symbols_count': len(self.supported_symbols),
            'max_allocation': self.max_stock_allocation,
            'aggressive_multiplier': self.aggressive_multiplier,
            'market_open': self._is_market_open(),
            'current_regime': self._get_market_regime(),
            'strategy_performance': dict(self._strategy_performance),
            'daily_pnl': self._daily_pnl,
            'daily_trade_count': self._daily_trade_count,
            'institutional_config': self.institutional_config,
            'enhanced_strategies': {
                'leveraged_etfs': len(sum(self.strategy_symbols['leveraged_etfs'].values(), [])),
                'sector_etfs': len(sum(self.strategy_symbols['sector_etfs'].values(), [])),
                'momentum_stocks': len(sum(self.strategy_symbols['momentum_stocks'].values(), [])),
                'volatility_symbols': len(sum(self.strategy_symbols['volatility_symbols'].values(), []))
            }
        }
    
    # Intraday Trading Optimization Methods
    
    def _reset_daily_counters_if_needed(self):
        """Reset daily counters if it's a new trading day"""
        try:
            current_date = datetime.now().date()
            if current_date != self._last_reset_date:
                self._daily_pnl = 0.0
                self._daily_trade_count = 0
                self._last_reset_date = current_date
                self.logger.info(f"🔄 Daily counters reset for {current_date}")
        except Exception as e:
            self.logger.error(f"Error resetting daily counters: {e}")
    
    def _check_intraday_trading_limits(self) -> bool:
        """Check if we can continue trading based on daily limits"""
        try:
            # NO DAILY TRADE LIMIT - Trade as much as profitable!
            # (was: daily trade limit check removed for unlimited profitable trading)
            
            # Check monthly loss limit (INSTITUTIONAL risk management)
            if self._daily_pnl <= -self.institutional_config['monthly_loss_limit']:
                self.logger.warning(f"Monthly loss limit reached: {self._daily_pnl:.1%} <= -{self.institutional_config['monthly_loss_limit']:.1%}")
                return False
            
            return True  # No artificial trade limits!
        except Exception as e:
            self.logger.error(f"Error checking intraday limits: {e}")
            return True  # Allow trading if check fails
    
    def _get_intraday_strategy_for_current_time(self) -> Dict[str, Any]:
        """Get optimal strategy based on current time of day"""
        try:
            import pytz
            
            # Get current ET time
            et_tz = pytz.timezone('America/New_York')
            current_et = datetime.now(et_tz)
            current_hour_decimal = current_et.hour + (current_et.minute / 60.0)
            
            # Find matching time strategy
            for (start_hour, end_hour), strategy_info in self.intraday_time_strategies.items():
                if start_hour <= current_hour_decimal < end_hour:
                    self.logger.debug(f"Using {strategy_info['primary_strategy'].value} strategy for time {current_hour_decimal:.1f}")
                    return strategy_info.copy()
            
            # Default to core equity during off-hours or edge cases
            return {
                'primary_strategy': StockStrategy.CORE_EQUITY,
                'confidence_adjustment': 0.1,  # Higher threshold during off-hours
                'volume_requirement': 1.0,
                'position_multiplier': 0.5  # Smaller positions during off-hours
            }
            
        except Exception as e:
            self.logger.error(f"Error getting intraday strategy: {e}")
            return {
                'primary_strategy': StockStrategy.CORE_EQUITY,
                'confidence_adjustment': 0.0,
                'volume_requirement': 1.0,
                'position_multiplier': 1.0
            }
    
    def _get_heat_adjustment_factor(self) -> float:
        """Get position sizing adjustment based on daily P&L performance"""
        try:
            # Institutional approach: Less heat adjustment, more consistent sizing
            return 1.0  # Simplified for institutional approach
            
            daily_pnl_pct = self._daily_pnl
            
            # Reduce size after losses
            if daily_pnl_pct <= -0.02:  # Down 2%
                return 0.5  # Half size
            elif daily_pnl_pct <= -0.01:  # Down 1%
                return 0.75  # 75% size
            # Increase size after wins (ride the hot hand)
            elif daily_pnl_pct >= 0.02:  # Up 2%
                return 1.5  # 150% size
            elif daily_pnl_pct >= 0.01:  # Up 1%
                return 1.25  # 125% size
            else:
                return 1.0  # Normal size
                
        except Exception as e:
            self.logger.error(f"Error calculating heat adjustment: {e}")
            return 1.0
    
    def _analyze_stock_symbol_intraday(self, symbol: str, market_regime: str, strategy_info: Dict[str, Any]) -> Optional[StockAnalysis]:
        """Analyze stock symbol with intraday optimizations"""
        try:
            # Get basic analysis first
            analysis = self._analyze_stock_symbol(symbol, market_regime)
            if not analysis:
                return None
            
            # Apply intraday strategy preference
            preferred_strategy = strategy_info['primary_strategy']
            if self._symbol_fits_strategy(symbol, preferred_strategy):
                analysis.recommended_strategy = preferred_strategy
                # Boost confidence for preferred strategy match
                analysis.combined_confidence = min(0.95, analysis.combined_confidence + 0.05)
            
            # Check volume requirement (simplified - would use real volume data)
            volume_requirement = strategy_info['volume_requirement']
            if volume_requirement > 1.0:
                # For now, assume all symbols meet volume requirements
                # In production, this would check actual volume vs average
                pass
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in intraday analysis for {symbol}: {e}")
            return None
    
    def _symbol_fits_strategy(self, symbol: str, strategy: StockStrategy) -> bool:
        """Check if symbol fits the given strategy - SIMPLIFIED to allow all symbols"""
        # SIMPLIFIED: Allow any symbol to use any strategy for maximum opportunities
        return True
    
    def _create_intraday_stock_opportunity(self, analysis: StockAnalysis, heat_factor: float, strategy_info: Dict[str, Any]) -> Optional[TradeOpportunity]:
        """Create intraday-optimized trade opportunity"""
        try:
            # Get base opportunity
            opportunity = self._create_stock_opportunity(analysis)
            if not opportunity:
                return None
            
            # Apply intraday adjustments
            strategy_config = self.strategy_configs[analysis.recommended_strategy]
            
            # Adjust position size with heat factor and time multiplier
            time_multiplier = strategy_info['position_multiplier']
            adjusted_quantity = int(opportunity.quantity * heat_factor * time_multiplier)
            opportunity.quantity = max(1, adjusted_quantity)  # At least 1 share
            
            # Use intraday stop loss and profit targets
            opportunity.stop_loss_pct = strategy_config.get('intraday_stop_loss', 0.025)
            opportunity.profit_target_pct = strategy_config.get('intraday_profit_target', 0.03)
            
            # Add intraday metadata
            opportunity.metadata.update({
                'intraday_trading': True,
                'heat_factor': heat_factor,
                'time_multiplier': time_multiplier,
                'min_hold_minutes': strategy_config.get('min_hold_minutes', 8),
                'strategy_confidence_threshold': strategy_config['min_confidence']
            })
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error creating intraday opportunity: {e}")
            return None
    
    def _is_momentum_reversal(self, symbol: str, position: Dict) -> bool:
        """INSTITUTIONAL MOMENTUM CHECK - Detect 6-month momentum reversal"""
        try:
            # In production, would check if 6-month momentum has turned negative
            # This is a placeholder for the institutional momentum reversal logic
            
            # Would implement:
            # 1. Get 6-month price performance 
            # 2. Check if recent momentum < historical momentum
            # 3. Return True if momentum has significantly deteriorated
            
            # For now, return False - would implement actual momentum calculation
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking momentum reversal for {symbol}: {e}")
            return False