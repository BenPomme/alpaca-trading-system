"""
Market Intelligence Module - OpenAI-Powered Market Analysis

This module provides AI-powered market intelligence using OpenAI's GPT models to analyze
market conditions, assess position risk, identify opportunities, and generate trading signals
that integrate with the existing modular trading architecture.
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import time

try:
    import openai
except ImportError:
    openai = None

from modular.base_module import (
    TradingModule, ModuleConfig, TradeOpportunity, TradeResult, 
    TradeAction, TradeStatus, ExitReason
)


@dataclass
class MarketIntelligenceSignal:
    """Represents a market intelligence signal"""
    signal_type: str  # market_regime, position_risk, opportunity, etc.
    symbol: Optional[str] = None  # None for market-wide signals
    value: float = 0.0  # Numeric signal value (0-1 for confidence scores)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0  # AI confidence in this signal
    reasoning: str = ""  # AI reasoning for the signal
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class DailyMarketIntelligence:
    """Daily market intelligence summary"""
    analysis_date: datetime
    pre_market_analysis: Dict[str, Any] = field(default_factory=dict)
    post_market_analysis: Dict[str, Any] = field(default_factory=dict)
    market_signals: List[MarketIntelligenceSignal] = field(default_factory=list)
    position_insights: Dict[str, Dict] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)


class OpenAIAnalyzer:
    """Core OpenAI integration for market analysis using latest API format"""
    
    def __init__(self, api_key: str, model: str = "o4-mini", web_search_model: str = "gpt-4o-mini-search-preview", logger=None, parent_module=None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.parent_module = parent_module  # Reference to parent module for metrics
        
        if not openai:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.web_search_model = web_search_model
        self.request_count = 0
        self.last_request_time = 0
        self.rate_limit_delay = 2  # Increased for reasoning models
        
        # Validate model choice for financial analysis - Updated for 2025 models
        recommended_models = ["o4-mini", "o3-mini", "o1-mini", "gpt-4o", "gpt-4-turbo"]
        if model not in recommended_models:
            self.logger.warning(f"Model {model} may not be optimal for financial analysis. Recommended: o4-mini")
        
        # Model-specific configuration
        self.is_reasoning_model = model.startswith(('o3', 'o4', 'o1'))
        if self.is_reasoning_model:
            self.rate_limit_delay = 3  # Reasoning models need more time
            self.logger.info(f"Using reasoning model {model} - enhanced for complex financial analysis")
        
        # Web search capability
        self.enable_web_search = web_search_model is not None
        if self.enable_web_search:
            self.logger.info(f"Web search enabled with model: {web_search_model}")
        
        self.logger.info(f"OpenAI Analyzer initialized with model: {model}")
    
    def _update_api_metrics(self, success: bool, duration: float, context: str, error_type: str = None):
        """Update API metrics via parent module if available"""
        if self.parent_module and hasattr(self.parent_module, '_update_api_metrics'):
            self.parent_module._update_api_metrics(success, duration, context, error_type)
    
    async def _rate_limited_request(self, messages: List[Dict], temperature: float = 0.1, debug_context: str = "unknown") -> str:
        """Make rate-limited OpenAI API request using latest Chat Completions API format"""
        request_start_time = time.time()
        
        try:
            # Debug logging
            self.logger.info(f"🤖 OPENAI REQUEST [{debug_context}]: Model={self.model}, Messages={len(messages)}")
            self.logger.debug(f"🤖 Request content preview: {str(messages)[:200]}...")
            
            # Rate limiting - more conservative for production
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - time_since_last
                self.logger.debug(f"🤖 Rate limiting: sleeping {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
            
            self.request_count += 1
            self.last_request_time = time.time()
            
            # Use latest OpenAI API format with reasoning model optimization
            api_params = {
                "model": self.model,
                "messages": messages,
            }
            
            # Add temperature only for non-reasoning models (o4-mini requires default temperature=1)
            if not self.is_reasoning_model:
                api_params["temperature"] = temperature
                self.logger.debug(f"🤖 Added temperature={temperature} for non-reasoning model")
            
            # Add parameters based on model type
            if self.is_reasoning_model:
                # o3/o4 models use max_completion_tokens instead of max_tokens
                api_params["max_completion_tokens"] = 6000
                self.logger.debug(f"🤖 Using reasoning model parameters: max_completion_tokens=6000")
            else:
                # Non-reasoning models use standard parameters
                api_params.update({
                    "max_tokens": 4000,
                    "top_p": 0.9,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0,
                    "response_format": {"type": "text"}
                })
                self.logger.debug(f"🤖 Using standard model parameters: max_tokens=4000")
            
            # Make API call
            self.logger.debug(f"🤖 Making API call to {self.model}...")
            response = self.client.chat.completions.create(**api_params)
            
            # Process response
            response_content = response.choices[0].message.content
            request_duration = time.time() - request_start_time
            
            # Success logging
            self.logger.info(f"✅ OPENAI SUCCESS [{debug_context}]: {len(response_content)} chars in {request_duration:.2f}s")
            self.logger.debug(f"✅ Response preview: {response_content[:200]}...")
            
            # Update metrics
            if hasattr(self, '_update_api_metrics'):
                self._update_api_metrics(True, request_duration, debug_context)
            
            return response_content
            
        except openai.RateLimitError as e:
            request_duration = time.time() - request_start_time
            self.logger.warning(f"⏱️ RATE LIMIT HIT [{debug_context}]: {e} (after {request_duration:.2f}s)")
            if hasattr(self, '_update_api_metrics'):
                self._update_api_metrics(False, request_duration, debug_context, 'rate_limit')
            await asyncio.sleep(60)
            return ""
        except openai.APIError as e:
            request_duration = time.time() - request_start_time
            self.logger.error(f"❌ OPENAI API ERROR [{debug_context}]: {e} (after {request_duration:.2f}s)")
            if hasattr(self, '_update_api_metrics'):
                self._update_api_metrics(False, request_duration, debug_context, 'api_error')
            return ""
        except Exception as e:
            request_duration = time.time() - request_start_time
            self.logger.error(f"💥 UNEXPECTED ERROR [{debug_context}]: {e} (after {request_duration:.2f}s)")
            if hasattr(self, '_update_api_metrics'):
                self._update_api_metrics(False, request_duration, debug_context, 'unexpected_error')
            return ""
    
    async def analyze_market_regime(self, market_data: Dict) -> Dict[str, Any]:
        """Analyze current market regime using AI"""
        try:
            prompt = f"""
            As a professional market analyst, analyze the current market regime based on this data:
            
            Market Data:
            {json.dumps(market_data, indent=2)}
            
            Provide analysis in this exact JSON format:
            {{
                "regime": "bull|bear|sideways",
                "confidence": 0.0-1.0,
                "volatility_forecast": "low|medium|high",
                "sector_rotation_signals": ["sector1", "sector2"],
                "risk_level": "low|medium|high",
                "key_factors": ["factor1", "factor2"],
                "reasoning": "detailed explanation"
            }}
            """
            
            messages = [
                {"role": "system", "content": "You are a professional quantitative market analyst. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self._rate_limited_request(messages, debug_context="market_regime")
            
            # Parse JSON response
            try:
                analysis = json.loads(response)
                self.logger.info(f"🎯 MARKET REGIME PARSED: {analysis.get('regime', 'unknown')} ({analysis.get('confidence', 0):.1%} confidence)")
                return analysis
            except json.JSONDecodeError:
                self.logger.warning(f"⚠️ JSON PARSE FAILED [market_regime]: Response was: {response[:100]}...")
                return self._get_default_market_analysis()
                
        except Exception as e:
            self.logger.error(f"Error in market regime analysis: {e}")
            return self._get_default_market_analysis()
    
    async def analyze_position_risk(self, position_data: Dict) -> Dict[str, Any]:
        """Analyze risk for a specific position"""
        try:
            prompt = f"""
            Analyze the risk profile for this trading position:
            
            Position Data:
            {json.dumps(position_data, indent=2)}
            
            Provide risk analysis in this exact JSON format:
            {{
                "risk_score": 0.0-1.0,
                "risk_factors": ["factor1", "factor2"],
                "exit_urgency": "low|medium|high",
                "recommended_action": "hold|reduce|exit",
                "time_horizon": "short|medium|long",
                "correlation_risk": 0.0-1.0,
                "reasoning": "detailed explanation"
            }}
            """
            
            messages = [
                {"role": "system", "content": "You are a professional risk analyst. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self._rate_limited_request(messages, debug_context="position_risk")
            
            try:
                analysis = json.loads(response)
                self.logger.info(f"⚠️ POSITION RISK PARSED: {position_data.get('symbol', 'unknown')} - {analysis.get('risk_score', 0):.1%} risk")
                return analysis
            except json.JSONDecodeError:
                self.logger.warning(f"⚠️ JSON PARSE FAILED [position_risk]: Response was: {response[:100]}...")
                return self._get_default_position_analysis()
                
        except Exception as e:
            self.logger.error(f"Error in position risk analysis: {e}")
            return self._get_default_position_analysis()
    
    async def identify_opportunities(self, market_context: Dict, existing_positions: List[Dict]) -> List[Dict]:
        """Identify new trading opportunities"""
        try:
            prompt = f"""
            Based on current market conditions and existing positions, identify new trading opportunities:
            
            Market Context:
            {json.dumps(market_context, indent=2)}
            
            Existing Positions:
            {json.dumps(existing_positions, indent=2)[:1000]}  # Truncate for token limits
            
            Identify up to 5 opportunities in this exact JSON format:
            {{
                "opportunities": [
                    {{
                        "symbol": "TICKER",
                        "action": "buy|sell",
                        "confidence": 0.0-1.0,
                        "strategy": "momentum|mean_reversion|breakout|etc",
                        "time_horizon": "intraday|swing|position",
                        "risk_reward_ratio": 0.0-10.0,
                        "reasoning": "explanation"
                    }}
                ]
            }}
            """
            
            messages = [
                {"role": "system", "content": "You are a professional trading strategist. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self._rate_limited_request(messages, debug_context="opportunities")
            
            try:
                analysis = json.loads(response)
                opportunities = analysis.get('opportunities', [])
                self.logger.info(f"💡 OPPORTUNITIES PARSED: {len(opportunities)} opportunities found")
                for i, opp in enumerate(opportunities[:3]):
                    symbol = opp.get('symbol', 'unknown')
                    confidence = opp.get('confidence', 0)
                    action = opp.get('action', 'unknown')
                    self.logger.debug(f"💡 Opportunity {i+1}: {symbol} {action} ({confidence:.1%})")
                return opportunities
            except json.JSONDecodeError:
                self.logger.warning(f"⚠️ JSON PARSE FAILED [opportunities]: Response was: {response[:100]}...")
                return []
                
        except Exception as e:
            self.logger.error(f"Error identifying opportunities: {e}")
            return []
    
    def _get_default_market_analysis(self) -> Dict[str, Any]:
        """Default market analysis when AI fails"""
        return {
            "regime": "sideways",
            "confidence": 0.3,
            "volatility_forecast": "medium",
            "sector_rotation_signals": [],
            "risk_level": "medium",
            "key_factors": ["ai_analysis_unavailable"],
            "reasoning": "Default analysis - AI service unavailable"
        }
    
    def _get_default_position_analysis(self) -> Dict[str, Any]:
        """Default position analysis when AI fails"""
        return {
            "risk_score": 0.5,
            "risk_factors": ["ai_analysis_unavailable"],
            "exit_urgency": "low",
            "recommended_action": "hold",
            "time_horizon": "medium",
            "correlation_risk": 0.5,
            "reasoning": "Default analysis - AI service unavailable"
        }
    
    async def search_market_news(self, symbols: List[str], query_context: str = "") -> Dict[str, Any]:
        """Search for recent market news and events using web search model"""
        try:
            if not self.enable_web_search:
                return {"news_summary": "Web search disabled", "market_events": []}
            
            symbols_str = ", ".join(symbols[:5])  # Limit to 5 symbols for API efficiency
            
            search_prompt = f"""
            Search for the latest financial news and market events related to: {symbols_str}
            
            Context: {query_context}
            
            Focus on:
            - Recent earnings reports or guidance changes
            - Regulatory announcements affecting these assets
            - Major market moving events in the last 24-48 hours
            - Sector-specific developments
            - Macroeconomic factors affecting these markets
            
            Provide analysis in this JSON format:
            {{
                "news_summary": "Brief summary of key market developments",
                "market_events": [
                    {{
                        "event": "Description of event",
                        "symbols_affected": ["SYMBOL"],
                        "impact": "positive|negative|neutral",
                        "significance": "high|medium|low"
                    }}
                ],
                "market_sentiment": "bullish|bearish|mixed",
                "key_risks": ["risk1", "risk2"],
                "opportunities": ["opportunity1", "opportunity2"]
            }}
            """
            
            messages = [
                {"role": "system", "content": "You are a financial news analyst. Always respond with valid JSON. Use web search to find current market information."},
                {"role": "user", "content": search_prompt}
            ]
            
            # Use web search model for current market information
            api_params = {
                "model": self.web_search_model,
                "messages": messages,
                "max_tokens": 3000
            }
            
            # Add temperature only if not a search model (search models may not support it)
            if "search" not in self.web_search_model:
                api_params["temperature"] = 0.3
            
            response = self.client.chat.completions.create(**api_params)
            result = response.choices[0].message.content
            
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse market news search as JSON")
                return {
                    "news_summary": "Market search completed but format invalid",
                    "market_events": [],
                    "market_sentiment": "mixed",
                    "key_risks": [],
                    "opportunities": []
                }
                
        except Exception as e:
            self.logger.error(f"Error in market news search: {e}")
            return {
                "news_summary": "Market search unavailable",
                "market_events": [],
                "market_sentiment": "unknown",
                "key_risks": ["search_unavailable"],
                "opportunities": []
            }


class MarketIntelligenceModule(TradingModule):
    """
    AI-powered market intelligence module that provides daily market analysis,
    position risk assessment, and trading opportunity identification.
    """
    
    def __init__(self, 
                 config: ModuleConfig,
                 firebase_db,
                 risk_manager,
                 order_executor,
                 openai_api_key: str,
                 openai_model: str = "gpt-4-turbo-preview",
                 logger: Optional[logging.Logger] = None):
        """Initialize Market Intelligence Module"""
        super().__init__(config, firebase_db, risk_manager, order_executor, logger)
        
        # Initialize OpenAI analyzer
        self.ai_analyzer = OpenAIAnalyzer(openai_api_key, openai_model, "gpt-4o-mini-search-preview", self.logger, parent_module=self)
        
        # Intelligence state
        self.current_signals: List[MarketIntelligenceSignal] = []
        self.daily_intelligence: Optional[DailyMarketIntelligence] = None
        self.last_analysis_time = None
        
        # Configuration
        self.intelligence_cycle_hours = int(os.getenv('INTELLIGENCE_CYCLE_HOURS', '6'))
        self.enable_pre_market_analysis = True
        self.enable_post_market_analysis = True
        self.enable_position_monitoring = True
        
        # Performance tracking with comprehensive debug metrics
        self._intelligence_metrics = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'signals_generated': 0,
            'opportunities_identified': 0,
            'api_requests_made': 0,
            'api_failures': 0,
            'api_success_rate': 0.0,
            'avg_analysis_time': 0.0,
            'last_analysis_time': None,
            'market_regime_calls': 0,
            'position_analysis_calls': 0,
            'opportunity_calls': 0,
            'web_search_calls': 0,
            'web_search_failures': 0,
            'json_parse_failures': 0,
            'fallback_activations': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Debug state tracking
        self._debug_state = {
            'last_openai_response': None,
            'last_market_data': None,
            'last_position_data': None,
            'last_error': None,
            'last_successful_analysis': None,
            'api_model_used': openai_model,
            'web_search_model_used': "gpt-4o-mini-search-preview",
            'module_version': '1.0.0',
            'deployment_env': os.getenv('RAILWAY_ENVIRONMENT', 'local')
        }
        
        self.logger.info(f"Market Intelligence Module initialized with {openai_model}")
    
    @property
    def module_name(self) -> str:
        return "market_intelligence"
    
    @property
    def supported_symbols(self) -> List[str]:
        # Intelligence module analyzes all symbols but doesn't trade directly
        return ["SPY", "QQQ", "IWM", "BTCUSD", "ETHUSD", "AAPPL", "MSFT", "GOOGL", "TSLA"]
    
    async def run_daily_intelligence_cycle(self) -> DailyMarketIntelligence:
        """Run complete daily intelligence cycle"""
        self.logger.info("🧠 Starting daily market intelligence cycle")
        
        try:
            intelligence = DailyMarketIntelligence(analysis_date=datetime.now())
            
            # 1. Market regime analysis with web search enhancement
            market_data = await self._gather_market_data()
            
            # 1a. Search for current market news and events
            current_symbols = list(self.supported_symbols)
            market_news = await self.ai_analyzer.search_market_news(
                current_symbols, 
                "Current market analysis for trading decisions"
            )
            
            # Enhance market data with web search results
            market_data['current_news'] = market_news
            
            regime_analysis = await self.ai_analyzer.analyze_market_regime(market_data)
            
            # QA Rule 4: Ensure complete data structure
            if not regime_analysis:
                regime_analysis = self.ai_analyzer._get_default_market_analysis()
            
            intelligence.pre_market_analysis['regime'] = regime_analysis
            intelligence.pre_market_analysis['market_news'] = market_news
            
            # 2. Position risk analysis
            positions = await self._get_current_positions()
            for symbol, position_data in positions.items():
                risk_analysis = await self.ai_analyzer.analyze_position_risk(position_data)
                
                # QA Rule 4: Ensure complete data structure
                if not risk_analysis:
                    risk_analysis = self.ai_analyzer._get_default_position_analysis()
                
                intelligence.position_insights[symbol] = risk_analysis
            
            # 3. Opportunity identification
            market_context = {
                'regime': regime_analysis,
                'market_data': market_data
            }
            opportunities = await self.ai_analyzer.identify_opportunities(market_context, list(positions.values()))
            
            # QA Rule 4: Ensure opportunities is always a list
            if not opportunities or not isinstance(opportunities, list):
                opportunities = []
            
            # 4. Generate signals
            signals = self._convert_analysis_to_signals(regime_analysis, intelligence.position_insights, opportunities)
            intelligence.market_signals = signals
            self.current_signals = signals
            
            # 5. Save to Firebase
            await self._save_intelligence_data(intelligence)
            
            # Update metrics - QA Rule 5: Defensive programming
            self._intelligence_metrics['total_analyses'] = self._intelligence_metrics.get('total_analyses', 0) + 1
            self._intelligence_metrics['successful_analyses'] = self._intelligence_metrics.get('successful_analyses', 0) + 1
            self._intelligence_metrics['signals_generated'] = self._intelligence_metrics.get('signals_generated', 0) + len(signals)
            self._intelligence_metrics['opportunities_identified'] = self._intelligence_metrics.get('opportunities_identified', 0) + len(opportunities)
            
            self.daily_intelligence = intelligence
            self.last_analysis_time = datetime.now()
            
            self.logger.info(f"✅ Intelligence cycle complete: {len(signals)} signals, {len(opportunities)} opportunities")
            return intelligence
            
        except Exception as e:
            self.logger.error(f"❌ Error in intelligence cycle: {e}")
            # QA Rule 5: Defensive programming for error case
            self._intelligence_metrics['total_analyses'] = self._intelligence_metrics.get('total_analyses', 0) + 1
            return DailyMarketIntelligence(analysis_date=datetime.now())
    
    def analyze_opportunities(self) -> List[TradeOpportunity]:
        """Convert AI opportunities to trading opportunities"""
        opportunities = []
        
        try:
            if not self.current_signals:
                return opportunities
            
            # Find opportunity signals
            for signal in self.current_signals:
                if signal.signal_type == "opportunity" and signal.confidence >= self.config.min_confidence:
                    # Convert intelligence signal to trade opportunity
                    opportunity = TradeOpportunity(
                        symbol=signal.symbol or "SPY",
                        action=TradeAction.BUY if signal.metadata.get('action') == 'buy' else TradeAction.SELL,
                        quantity=self._calculate_position_size(signal),
                        confidence=signal.confidence,
                        strategy=f"ai_intelligence_{signal.metadata.get('strategy', 'unknown')}",
                        metadata={
                            'intelligence_signal': True,
                            'ai_reasoning': signal.reasoning,
                            'risk_reward_ratio': signal.metadata.get('risk_reward_ratio', 1.0),
                            'time_horizon': signal.metadata.get('time_horizon', 'swing')
                        },
                        ml_score=signal.confidence,
                        profit_target_pct=0.15,  # Default targets
                        stop_loss_pct=0.08
                    )
                    opportunities.append(opportunity)
            
            self.logger.debug(f"Generated {len(opportunities)} AI-driven opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error analyzing opportunities: {e}")
            return opportunities
    
    def execute_trades(self, opportunities: List[TradeOpportunity]) -> List[TradeResult]:
        """Intelligence module doesn't execute trades directly"""
        # Intelligence module provides signals but doesn't execute
        # Trades are executed by other modules based on intelligence signals
        return []
    
    def monitor_positions(self) -> List[TradeResult]:
        """Monitor positions and provide intelligence-based exit signals"""
        exit_results = []
        
        try:
            if not self.current_signals:
                return exit_results
            
            # Find position risk signals
            for signal in self.current_signals:
                if signal.signal_type == "position_risk" and signal.symbol:
                    urgency = signal.metadata.get('exit_urgency', 'low')
                    
                    if urgency in ['high', 'medium']:
                        # Generate exit signal
                        exit_result = TradeResult(
                            opportunity=TradeOpportunity(
                                symbol=signal.symbol,
                                action=TradeAction.SELL,
                                quantity=0,  # Will be determined by position size
                                confidence=signal.confidence,
                                strategy="ai_risk_management"
                            ),
                            status=TradeStatus.PENDING,
                            exit_reason=ExitReason.RISK_MANAGEMENT if urgency == 'high' else ExitReason.ML_OPTIMIZATION
                        )
                        exit_results.append(exit_result)
            
            return exit_results
            
        except Exception as e:
            self.logger.error(f"Error monitoring positions: {e}")
            return exit_results
    
    def get_market_intelligence_signals(self) -> List[MarketIntelligenceSignal]:
        """Get current market intelligence signals for other modules"""
        return self.current_signals.copy()
    
    def get_position_risk_score(self, symbol: str) -> float:
        """Get AI risk score for a specific position"""
        try:
            for signal in self.current_signals:
                if signal.signal_type == "position_risk" and signal.symbol == symbol:
                    return signal.value
            return 0.5  # Default medium risk
        except Exception:
            return 0.5
    
    def should_run_intelligence_cycle(self) -> bool:
        """Check if intelligence cycle should run"""
        if not self.last_analysis_time:
            return True
        
        time_since_last = datetime.now() - self.last_analysis_time
        return time_since_last.total_seconds() >= (self.intelligence_cycle_hours * 3600)
    
    # Private helper methods
    
    async def _gather_market_data(self) -> Dict[str, Any]:
        """Gather current market data for analysis"""
        try:
            # Get data from risk manager and other sources
            market_data = {
                'timestamp': datetime.now().isoformat(),
                'market_hours': self._get_market_session(),
                'portfolio_value': 0,
                'positions_count': 0,
                'volatility_index': 0.2,  # Default
                'sector_performance': {}
            }
            
            # Add portfolio information if available - QA Rule 1: Check attribute existence
            if hasattr(self.risk_manager, 'get_portfolio_summary'):
                try:
                    portfolio = self.risk_manager.get_portfolio_summary()
                    if portfolio and isinstance(portfolio, dict):
                        market_data.update(portfolio)
                except Exception as e:
                    self.logger.debug(f"Could not get portfolio summary: {e}")
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error gathering market data: {e}")
            return {'timestamp': datetime.now().isoformat(), 'error': str(e)}
    
    async def _get_current_positions(self) -> Dict[str, Dict]:
        """Get current trading positions for analysis"""
        try:
            positions = {}
            
            # Get positions from risk manager - QA Rule 1: Check attribute existence  
            if hasattr(self.risk_manager, 'get_all_positions'):
                try:
                    risk_positions = self.risk_manager.get_all_positions()
                    if risk_positions and isinstance(risk_positions, dict):
                        for symbol, position in risk_positions.items():
                            # QA Rule 5: Defensive programming with .get() for all position fields
                            if position and isinstance(position, dict):
                                positions[symbol] = {
                                    'symbol': symbol,
                                    'quantity': position.get('quantity', 0),
                                    'market_value': position.get('market_value', 0),
                                    'unrealized_pnl': position.get('unrealized_pnl', 0),
                                    'entry_price': position.get('avg_entry_price', 0),
                                    'current_price': position.get('current_price', 0)
                                }
                except Exception as e:
                    self.logger.debug(f"Could not get positions from risk manager: {e}")
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Error getting current positions: {e}")
            return {}
    
    def _convert_analysis_to_signals(self, 
                                   regime_analysis: Dict,
                                   position_insights: Dict,
                                   opportunities: List[Dict]) -> List[MarketIntelligenceSignal]:
        """Convert AI analysis to standardized signals"""
        signals = []
        
        try:
            # QA Rule 4: Ensure regime_analysis is valid before processing
            if not regime_analysis or not isinstance(regime_analysis, dict):
                self.logger.warning("Invalid regime analysis data, using defaults")
                regime_analysis = {
                    'regime': 'sideways',
                    'confidence': 0.5,
                    'volatility_forecast': 'medium',
                    'risk_level': 'medium',
                    'reasoning': 'Default analysis - invalid data received'
                }
            
            # Market regime signal - QA Rule 5: All .get() calls with defaults
            regime_signal = MarketIntelligenceSignal(
                signal_type="market_regime",
                value=regime_analysis.get('confidence', 0.5),
                confidence=regime_analysis.get('confidence', 0.5),
                metadata={
                    'regime': regime_analysis.get('regime', 'sideways'),
                    'volatility_forecast': regime_analysis.get('volatility_forecast', 'medium'),
                    'risk_level': regime_analysis.get('risk_level', 'medium')
                },
                reasoning=regime_analysis.get('reasoning', ''),
                expires_at=datetime.now() + timedelta(hours=self.intelligence_cycle_hours)
            )
            signals.append(regime_signal)
            
            # Position risk signals - QA Rule 4: Validate data structure integrity
            if position_insights and isinstance(position_insights, dict):
                for symbol, insight in position_insights.items():
                    # QA Rule 5: Defensive programming - validate insight data
                    if not insight or not isinstance(insight, dict):
                        self.logger.warning(f"Invalid insight data for {symbol}, using defaults")
                        insight = {
                            'risk_score': 0.5,
                            'exit_urgency': 'low',
                            'recommended_action': 'hold',
                            'risk_factors': [],
                            'reasoning': 'Default analysis - invalid data received'
                        }
                    
                    risk_signal = MarketIntelligenceSignal(
                        signal_type="position_risk",
                        symbol=symbol,
                        value=insight.get('risk_score', 0.5),
                        confidence=0.8,  # High confidence in risk assessment
                        metadata={
                            'exit_urgency': insight.get('exit_urgency', 'low'),
                            'recommended_action': insight.get('recommended_action', 'hold'),
                            'risk_factors': insight.get('risk_factors', [])
                        },
                        reasoning=insight.get('reasoning', '')
                    )
                    signals.append(risk_signal)
            
            # Opportunity signals - QA Rule 4: Validate opportunities list
            if opportunities and isinstance(opportunities, list):
                for opp in opportunities:
                    # QA Rule 5: Defensive programming - validate opportunity data
                    if not opp or not isinstance(opp, dict):
                        self.logger.warning("Invalid opportunity data, skipping")
                        continue
                        
                    opp_signal = MarketIntelligenceSignal(
                        signal_type="opportunity",
                        symbol=opp.get('symbol'),
                        value=opp.get('confidence', 0.5),
                        confidence=opp.get('confidence', 0.5),
                        metadata={
                            'action': opp.get('action'),
                            'strategy': opp.get('strategy'),
                            'time_horizon': opp.get('time_horizon'),
                            'risk_reward_ratio': opp.get('risk_reward_ratio', 1.0)
                        },
                        reasoning=opp.get('reasoning', '')
                    )
                    signals.append(opp_signal)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error converting analysis to signals: {e}")
            return signals
    
    def _calculate_position_size(self, signal: MarketIntelligenceSignal) -> float:
        """Calculate position size based on signal strength"""
        try:
            base_size = 100  # Base position size
            confidence_multiplier = signal.confidence
            risk_reward = signal.metadata.get('risk_reward_ratio', 1.0)
            
            # Adjust size based on confidence and risk/reward
            size = base_size * confidence_multiplier * min(risk_reward, 2.0)
            return max(1, min(size, 1000))  # Cap between 1 and 1000
            
        except Exception:
            return 100  # Default size
    
    def _get_market_session(self) -> str:
        """Determine current market session"""
        now = datetime.now()
        hour = now.hour
        
        if 4 <= hour < 9:
            return "pre_market"
        elif 9 <= hour < 16:
            return "market_hours"
        elif 16 <= hour < 20:
            return "after_hours"
        else:
            return "closed"
    
    async def _save_intelligence_data(self, intelligence: DailyMarketIntelligence):
        """Save intelligence data to Firebase"""
        try:
            if self.firebase_db and self.firebase_db.is_connected():
                intelligence_data = {
                    'analysis_date': intelligence.analysis_date.isoformat(),
                    'pre_market_analysis': intelligence.pre_market_analysis,
                    'post_market_analysis': intelligence.post_market_analysis,
                    'signals_count': len(intelligence.market_signals),
                    'positions_analyzed': len(intelligence.position_insights),
                    'recommendations': intelligence.recommendations,
                    'module_version': '1.0',
                    'api_requests': self.ai_analyzer.request_count
                }
                
                self.firebase_db.save_market_intelligence(intelligence_data)
                self.logger.debug("Market intelligence data saved to Firebase")
            
        except Exception as e:
            self.logger.error(f"Error saving intelligence data: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get intelligence module performance summary with debug info"""
        base_summary = super().get_performance_summary()
        
        # Calculate uptime
        uptime_hours = (datetime.now() - datetime.fromisoformat(self._intelligence_metrics['start_time'])).total_seconds() / 3600
        
        # Calculate success rates
        total_requests = self._intelligence_metrics.get('api_requests_made', 0)
        api_success_rate = 0.0
        if total_requests > 0:
            failures = self._intelligence_metrics.get('api_failures', 0)
            api_success_rate = (total_requests - failures) / total_requests
        
        base_summary.update({
            'intelligence_metrics': self._intelligence_metrics.copy(),
            'debug_state': self._debug_state.copy(),
            'current_signals_count': len(self.current_signals),
            'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            'ai_model': self.ai_analyzer.model,
            'web_search_model': self.ai_analyzer.web_search_model,
            'api_requests_made': self.ai_analyzer.request_count,
            'uptime_hours': uptime_hours,
            'api_success_rate': api_success_rate,
            'health_status': self._get_health_status(),
            'last_cycle_should_run': self.should_run_intelligence_cycle(),
            'cycle_frequency_hours': self.intelligence_cycle_hours
        })
        return base_summary
    
    def _get_health_status(self) -> str:
        """Get current health status of the intelligence module"""
        try:
            # Check if we have recent successful analysis
            if not self.last_analysis_time:
                return "INITIALIZING"
            
            time_since_last = datetime.now() - self.last_analysis_time
            hours_since_last = time_since_last.total_seconds() / 3600
            
            # Check API success rate
            api_success_rate = self._intelligence_metrics.get('api_success_rate', 0.0)
            
            if hours_since_last > (self.intelligence_cycle_hours * 2):
                return "STALE"
            elif api_success_rate < 0.5:
                return "API_ISSUES"
            elif api_success_rate < 0.8:
                return "DEGRADED"
            else:
                return "HEALTHY"
                
        except Exception:
            return "ERROR"
    
    def _update_api_metrics(self, success: bool, duration: float, context: str, error_type: str = None):
        """Update API metrics for debugging"""
        try:
            self._intelligence_metrics['api_requests_made'] += 1
            
            if success:
                # Update success metrics
                current_avg = self._intelligence_metrics.get('avg_analysis_time', 0.0)
                total_requests = self._intelligence_metrics['api_requests_made']
                self._intelligence_metrics['avg_analysis_time'] = (
                    (current_avg * (total_requests - 1) + duration) / total_requests
                )
                
                # Store successful response for debugging
                self._debug_state['last_successful_analysis'] = {
                    'timestamp': datetime.now().isoformat(),
                    'context': context,
                    'duration': duration
                }
                
            else:
                # Update failure metrics
                self._intelligence_metrics['api_failures'] += 1
                
                # Store error for debugging
                self._debug_state['last_error'] = {
                    'timestamp': datetime.now().isoformat(),
                    'context': context,
                    'error_type': error_type,
                    'duration': duration
                }
                
                # Update specific failure counters
                if context == "web_search":
                    self._intelligence_metrics['web_search_failures'] += 1
                elif error_type == "json_parse":
                    self._intelligence_metrics['json_parse_failures'] += 1
                elif error_type in ['api_error', 'rate_limit', 'unexpected_error']:
                    self._intelligence_metrics['fallback_activations'] += 1
            
            # Update context-specific counters
            if context == "market_regime":
                self._intelligence_metrics['market_regime_calls'] += 1
            elif context == "position_risk":
                self._intelligence_metrics['position_analysis_calls'] += 1
            elif context == "opportunities":
                self._intelligence_metrics['opportunity_calls'] += 1
            elif context == "web_search":
                self._intelligence_metrics['web_search_calls'] += 1
            
            # Update success rate
            total_requests = self._intelligence_metrics['api_requests_made']
            failures = self._intelligence_metrics['api_failures']
            self._intelligence_metrics['api_success_rate'] = (total_requests - failures) / total_requests if total_requests > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error updating API metrics: {e}")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get detailed debug information for troubleshooting"""
        return {
            'module_info': {
                'name': self.module_name,
                'version': self._debug_state.get('module_version', '1.0.0'),
                'deployment_env': self._debug_state.get('deployment_env', 'unknown'),
                'ai_model': self._debug_state.get('api_model_used', 'unknown'),
                'web_search_model': self._debug_state.get('web_search_model_used', 'unknown'),
            },
            'performance_metrics': self._intelligence_metrics.copy(),
            'debug_state': self._debug_state.copy(),
            'health_status': self._get_health_status(),
            'current_time': datetime.now().isoformat(),
            'signals_summary': {
                'total_signals': len(self.current_signals),
                'signal_types': [s.signal_type for s in self.current_signals],
                'avg_confidence': sum(s.confidence for s in self.current_signals) / len(self.current_signals) if self.current_signals else 0.0
            },
            'configuration': {
                'cycle_hours': self.intelligence_cycle_hours,
                'min_confidence': self.config.min_confidence,
                'pre_market_enabled': self.enable_pre_market_analysis,
                'post_market_enabled': self.enable_post_market_analysis,
                'position_monitoring_enabled': self.enable_position_monitoring
            }
        }