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

from .base_module import (
    TradingModule, ModuleConfig, TradeOpportunity, TradeResult,
    TradeAction, TradeStatus, ExitReason
)


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
        """Check if analysis meets minimum trading criteria"""
        return (self.combined_confidence > 0.55 and 
                self.current_price > 0 and
                self.technical_score > 0.40)


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
        
        # Stocks-specific configuration
        self.max_stock_allocation = config.custom_params.get('max_allocation_pct', 50.0) / 100  # 50% max for stocks
        self.aggressive_multiplier = config.custom_params.get('aggressive_multiplier', 2.0)
        self.market_tier = config.custom_params.get('market_tier', 2)
        
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
        
        # Symbol universe by tier (for market_tier configuration)
        self.symbol_tiers = {
            1: SymbolTier("core_etfs", ['SPY', 'QQQ', 'IWM'], 1, 0.60),
            2: SymbolTier("liquid_stocks", 
                         ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX'] + 
                         ['XLK', 'XLV', 'XLF', 'XLE', 'XLY'], 2, 0.55),
            3: SymbolTier("extended_universe",
                         ['AMD', 'CRM', 'ADBE', 'PYPL', 'BABA', 'DIS', 'V', 'MA', 'JPM', 'BAC'] +
                         ['TQQQ', 'UPRO', 'SOXL'], 3, 0.65),
            4: SymbolTier("global_symbols",
                         ['TSM', 'ASML', 'SAP', 'NVO', 'UNH', 'JNJ', 'PG', 'KO'] +
                         ['VXX', 'SVXY', 'TLT', 'GLD'], 4, 0.70)
        }
        
        # Intelligence analysis weights
        self.intelligence_weights = {
            'technical': 0.40,    # RSI, MACD, Bollinger Bands
            'regime': 0.40,       # Bull/Bear/Sideways detection
            'pattern': 0.20       # Breakouts, support/resistance
        }
        
        # Strategy configuration
        self.strategy_configs = {
            StockStrategy.LEVERAGED_ETFS: {
                'min_confidence': 0.70,
                'position_multiplier': 2.5,
                'max_allocation': 0.15  # 15% max in leveraged ETFs
            },
            StockStrategy.SECTOR_ROTATION: {
                'min_confidence': 0.60,
                'position_multiplier': 1.5,
                'max_allocation': 0.25
            },
            StockStrategy.MOMENTUM_AMPLIFICATION: {
                'min_confidence': 0.75,
                'position_multiplier': 2.0,
                'max_allocation': 0.20
            },
            StockStrategy.VOLATILITY_TRADING: {
                'min_confidence': 0.55,
                'position_multiplier': 1.8,
                'max_allocation': 0.10
            },
            StockStrategy.CORE_EQUITY: {
                'min_confidence': 0.55,
                'position_multiplier': 1.0,
                'max_allocation': 0.30
            }
        }
        
        # Performance tracking
        self._strategy_performance = {strategy: {'trades': 0, 'wins': 0, 'total_pnl': 0.0} 
                                    for strategy in StockStrategy}
        
        total_symbols = sum(len(tier.symbols) for tier in self.symbol_tiers.values())
        self.logger.info(f"Stocks module initialized with {total_symbols} symbols across {len(self.symbol_tiers)} tiers")
        self.logger.info(f"Market tier: {self.market_tier}, Aggressive multiplier: {self.aggressive_multiplier}x")
    
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
        
        Returns:
            List of stock trade opportunities
        """
        opportunities = []
        
        try:
            # Check if US market is open (stocks only trade during market hours)
            if not self._is_market_open():
                self.logger.info("US market closed - no stock opportunities")
                return opportunities
            
            # Check current allocation
            current_allocation = self._get_current_stock_allocation()
            if current_allocation >= self.max_stock_allocation:
                self.logger.info(f"Stock allocation limit reached: {current_allocation:.1%}")
                return opportunities
            
            # Get current market regime
            market_regime = self._get_market_regime()
            
            # Analyze symbols based on current tier
            active_symbols = self._get_active_symbols()
            
            self.logger.info(f"Analyzing {len(active_symbols)} stocks for opportunities (regime: {market_regime})")
            
            for symbol in active_symbols:
                try:
                    analysis = self._analyze_stock_symbol(symbol, market_regime)
                    if analysis and analysis.is_tradeable:
                        # Check strategy-specific confidence threshold
                        strategy_config = self.strategy_configs[analysis.recommended_strategy]
                        if analysis.combined_confidence >= strategy_config['min_confidence']:
                            opportunity = self._create_stock_opportunity(analysis)
                            if opportunity:
                                opportunities.append(opportunity)
                
                except Exception as e:
                    self.logger.error(f"Error analyzing stock {symbol}: {e}")
                    continue
            
            self.logger.info(f"Found {len(opportunities)} stock opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error in stock opportunity analysis: {e}")
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
        
        Returns:
            List of exit trade results
        """
        exit_results = []
        
        try:
            # Only monitor during market hours
            if not self._is_market_open():
                return exit_results
            
            # Get current stock positions
            positions = self._get_stock_positions()
            
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
        """Get real current stock price from Alpaca API - NO MOCK DATA"""
        try:
            quote = self.api.get_latest_quote(symbol)
            
            if quote:
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
            # Determine trade direction based on combined analysis
            action = TradeAction.BUY if analysis.combined_confidence > 0.55 else TradeAction.SELL
            
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
                'qty': int(opportunity.quantity),
                'side': 'buy' if opportunity.action == TradeAction.BUY else 'sell',
                'type': 'market',
                'time_in_force': 'day'  # Day orders for stocks
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
                    error_message=execution_result.get('error', 'Unknown stock execution error')
                )
            
            # 🧠 ML DATA COLLECTION: Save trade with enhanced parameter context
            if result.success:
                self._save_ml_enhanced_stock_trade(opportunity, result)
            
            return result
                
        except Exception as e:
            return TradeResult(
                opportunity=opportunity,
                status=TradeStatus.FAILED,
                error_message=f"Stock execution error: {e}"
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
            
        except Exception as e:
            self.logger.error(f"Error saving ML stock trade data: {e}")
    
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
        """Get confidence threshold for a strategy"""
        thresholds = {
            'leveraged_etfs': 0.70,
            'momentum_amp': 0.75,
            'sector_rotation': 0.60,
            'volatility_trading': 0.55,
            'core_equity': 0.55
        }
        
        for strategy, threshold in thresholds.items():
            if strategy in strategy_name:
                return threshold
        
        return 0.55  # Default
    
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
        """Analyze if stock position should be exited"""
        try:
            unrealized_pl = position.get('unrealized_pl', 0)
            market_value = abs(position.get('market_value', 1))
            
            if market_value == 0:
                return None
            
            unrealized_pl_pct = unrealized_pl / market_value
            
            # Stock-specific exit conditions
            if unrealized_pl_pct >= 0.15:  # 15% profit target
                return 'profit_target'
            elif unrealized_pl_pct <= -0.08:  # 8% stop loss
                return 'stop_loss'
            
            # Strategy-specific exits
            symbol = position.get('symbol', '')
            if symbol in sum(self.strategy_symbols['leveraged_etfs'].values(), []):
                # More aggressive exits for leveraged ETFs
                if unrealized_pl_pct >= 0.12:  # 12% profit for 3x ETFs
                    return 'leveraged_profit'
                elif unrealized_pl_pct <= -0.06:  # 6% stop loss for 3x ETFs
                    return 'leveraged_stop'
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing stock exit: {e}")
            return None
    
    def _execute_stock_exit(self, position: Dict, exit_reason: str) -> Optional[TradeResult]:
        """Execute stock position exit"""
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
                strategy='stock_exit'
            )
            
            # Execute exit
            result = self._execute_stock_trade(exit_opportunity)
            
            if result.success:
                # Update with exit information
                result.pnl = position.get('unrealized_pl', 0)
                result.pnl_pct = position.get('unrealized_pl', 0) / max(abs(position.get('market_value', 1)), 1)
                result.exit_reason = self._get_exit_reason_enum(exit_reason)
                
                # Update strategy performance
                strategy = self._infer_position_strategy(symbol)
                if strategy in self._strategy_performance:
                    if result.pnl and result.pnl > 0:
                        self._strategy_performance[strategy]['wins'] += 1
                    self._strategy_performance[strategy]['total_pnl'] += result.pnl or 0
                
                self.logger.info(f"Stock exit: {symbol} {exit_reason} P&L: ${result.pnl:.2f} ({result.pnl_pct:.1%})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing stock exit: {e}")
            return None
    
    # Utility methods
    
    def _is_market_open(self) -> bool:
        """Check if US stock market is currently open"""
        try:
            clock = self.api.get_clock()
            return getattr(clock, 'is_open', False)
        except Exception as e:
            self.logger.debug(f"Error checking market hours: {e}")
            return False  # Assume closed if unable to check
    
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
        """Calculate stock quantity based on portfolio allocation"""
        try:
            account = self.api.get_account()
            portfolio_value = float(getattr(account, 'portfolio_value', 100000))
            
            # Base allocation per stock trade (1.5% for stocks)
            base_allocation = 0.015
            max_position_value = portfolio_value * base_allocation * self.aggressive_multiplier
            
            # Calculate whole share quantity for stocks
            quantity = max_position_value / price if price > 0 else 0
            return int(quantity)  # Whole shares only for stocks
            
        except Exception as e:
            self.logger.error(f"Error calculating stock quantity: {e}")
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
            'enhanced_strategies': {
                'leveraged_etfs': len(sum(self.strategy_symbols['leveraged_etfs'].values(), [])),
                'sector_etfs': len(sum(self.strategy_symbols['sector_etfs'].values(), [])),
                'momentum_stocks': len(sum(self.strategy_symbols['momentum_stocks'].values(), [])),
                'volatility_symbols': len(sum(self.strategy_symbols['volatility_symbols'].values(), []))
            }
        }