"""
Enhanced Crypto Trading Module - Phase 2 Data Integration
Integrates enhanced data sources and professional technical indicators
Maintains compatibility with existing modular architecture
Preserves Firebase + Railway deployment
"""

import os
import logging
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Import base modular architecture (PRESERVE)
from modular.base_module import (
    TradingModule, ModuleConfig, TradeOpportunity, TradeResult,
    TradeAction, TradeStatus, ExitReason
)

# Enhanced data integration (NEW - Phase 2)
try:
    from enhanced_data_manager import get_enhanced_data_manager
    ENHANCED_DATA_AVAILABLE = True
except ImportError:
    print("⚠️ Enhanced data manager not available - using fallback")
    ENHANCED_DATA_AVAILABLE = False

# Enhanced technical indicators (NEW - Phase 2)
try:
    from enhanced_technical_indicators import get_enhanced_technical_indicators
    ENHANCED_INDICATORS_AVAILABLE = True
except ImportError:
    print("⚠️ Enhanced technical indicators not available - using fallback")
    ENHANCED_INDICATORS_AVAILABLE = False

# Enhanced ML models (NEW - Phase 2)
try:
    from enhanced_ml_models import get_enhanced_ml_framework
    ENHANCED_ML_AVAILABLE = True
except ImportError:
    print("⚠️ Enhanced ML models not available - using fallback")
    ENHANCED_ML_AVAILABLE = False

# Fallback to existing components
try:
    from utils.technical_indicators import TechnicalIndicators
    from utils.pattern_recognition import PatternRecognition
    FALLBACK_AVAILABLE = True
except ImportError:
    print("⚠️ Fallback components not available")
    FALLBACK_AVAILABLE = False


class TradingSession(Enum):
    """Trading session types based on global market activity"""
    ASIA_PRIME = "asia_prime"      # 00:00-08:00 UTC
    EUROPE_PRIME = "europe_prime"  # 08:00-16:00 UTC
    US_PRIME = "us_prime"          # 16:00-24:00 UTC


class CryptoStrategy(Enum):
    """Enhanced crypto trading strategies"""
    MOMENTUM = "momentum"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"
    ML_ENSEMBLE = "ml_ensemble"    # NEW - AI-powered strategy
    FUNDAMENTAL = "fundamental"    # NEW - News/sentiment based


@dataclass
class EnhancedCryptoAnalysis:
    """Enhanced cryptocurrency analysis with multi-source data"""
    symbol: str
    current_price: float
    timestamp: datetime
    
    # Technical analysis (enhanced)
    technical_confidence: float
    technical_signals: Dict[str, Any]
    
    # Fundamental analysis (NEW)
    fundamental_confidence: Optional[float] = None
    news_sentiment: Optional[float] = None
    market_sentiment: Optional[str] = None
    
    # ML predictions (NEW)
    ml_confidence: Optional[float] = None
    ml_prediction: Optional[str] = None
    ml_probabilities: Optional[Dict[str, float]] = None
    
    # Data quality metrics
    data_sources_used: List[str] = None
    data_quality_score: float = 1.0
    
    # Combined analysis
    overall_confidence: float = 0.0
    recommended_action: TradeAction = TradeAction.HOLD
    risk_score: float = 0.5


class EnhancedCryptoModule(TradingModule):
    """
    Enhanced cryptocurrency trading module with multi-source data integration
    Maintains backward compatibility with existing modular architecture
    """
    
    def __init__(self, config: ModuleConfig, api_client=None, firebase_db=None, 
                 risk_manager=None, order_executor=None, trade_history_tracker=None,
                 market_intelligence=None, logger: logging.Logger = None):
        
        # Initialize base module (PRESERVE existing functionality)
        super().__init__(config, firebase_db, risk_manager, order_executor, logger)
        
        # Store additional components
        self.api_client = api_client
        self.trade_history_tracker = trade_history_tracker
        self.market_intelligence = market_intelligence
        
        # Initialize enhanced data sources
        self.enhanced_data_manager = None
        self.enhanced_indicators = None
        self.enhanced_ml_framework = None
        
        # Initialize enhanced components if available
        if ENHANCED_DATA_AVAILABLE:
            try:
                self.enhanced_data_manager = get_enhanced_data_manager(
                    alpaca_api_key=os.getenv('ALPACA_PAPER_API_KEY'),
                    alpaca_secret_key=os.getenv('ALPACA_PAPER_SECRET_KEY'),
                    alpha_vantage_key=os.getenv('ALPHA_VANTAGE_API_KEY'),
                    finnhub_key=os.getenv('FINNHUB_API_KEY'),
                    logger=self.logger
                )
                self.logger.info("✅ Enhanced data manager initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Enhanced data manager initialization failed: {e}")
        
        if ENHANCED_INDICATORS_AVAILABLE:
            try:
                self.enhanced_indicators = get_enhanced_technical_indicators(logger=self.logger)
                self.logger.info("✅ Enhanced technical indicators initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Enhanced indicators initialization failed: {e}")
        
        if ENHANCED_ML_AVAILABLE:
            try:
                self.enhanced_ml_framework = get_enhanced_ml_framework(logger=self.logger)
                self.logger.info("✅ Enhanced ML framework initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Enhanced ML framework initialization failed: {e}")
        
        # Fallback to existing components
        if not self.enhanced_indicators and FALLBACK_AVAILABLE:
            self.technical_indicators = TechnicalIndicators()
            self.pattern_recognition = PatternRecognition()
            self.logger.info("✅ Fallback indicators initialized")
        
        # Enhanced crypto universe (expanded from Reddit recommendations)
        self.enhanced_crypto_universe = {
            'BTCUSD': {'tier': 1, 'volatility': 'medium', 'liquidity': 'high'},
            'ETHUSD': {'tier': 1, 'volatility': 'medium', 'liquidity': 'high'},
            'SOLUSD': {'tier': 2, 'volatility': 'high', 'liquidity': 'medium'},
            'AVAXUSD': {'tier': 2, 'volatility': 'high', 'liquidity': 'medium'},
            'ADAUSD': {'tier': 2, 'volatility': 'high', 'liquidity': 'medium'},
            'DOTUSD': {'tier': 2, 'volatility': 'high', 'liquidity': 'medium'},
            'LINKUSD': {'tier': 2, 'volatility': 'high', 'liquidity': 'medium'},
            'UNIUSD': {'tier': 3, 'volatility': 'very_high', 'liquidity': 'low'},
            'AAVEUSD': {'tier': 3, 'volatility': 'very_high', 'liquidity': 'low'},
        }
        
        # Session configurations with enhanced strategies
        self.enhanced_session_configs = {
            TradingSession.ASIA_PRIME: {
                'strategy': CryptoStrategy.ML_ENSEMBLE,
                'position_size_multiplier': 0.8,
                'min_confidence': 0.65,
                'symbol_focus': 'tier_1'
            },
            TradingSession.EUROPE_PRIME: {
                'strategy': CryptoStrategy.FUNDAMENTAL,
                'position_size_multiplier': 1.0,
                'min_confidence': 0.60,
                'symbol_focus': 'tier_2'
            },
            TradingSession.US_PRIME: {
                'strategy': CryptoStrategy.MOMENTUM,
                'position_size_multiplier': 1.2,
                'min_confidence': 0.55,
                'symbol_focus': 'all_tiers'
            }
        }
        
        self.logger.info("🚀 Enhanced Crypto Module initialized with multi-source data")
    
    @property
    def module_name(self) -> str:
        """Unique identifier for this module"""
        return "enhanced_crypto"
    
    @property
    def supported_symbols(self) -> List[str]:
        """List of symbols this module can trade"""
        return list(self.enhanced_crypto_universe.keys())
    
    def execute_trades(self, opportunities: List[TradeOpportunity]) -> List[TradeResult]:
        """Execute validated trade opportunities"""
        results = []
        for opportunity in opportunities:
            try:
                # Mock implementation for testing
                result = TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.EXECUTED,
                    order_id=f"mock_{opportunity.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    execution_price=50000.0,  # Mock price
                    execution_time=datetime.now()
                )
                results.append(result)
                self.logger.info(f"✅ Mock execution: {opportunity.symbol} - {opportunity.action.value}")
            except Exception as e:
                error_result = TradeResult(
                    opportunity=opportunity,
                    status=TradeStatus.FAILED,
                    error_message=str(e)
                )
                results.append(error_result)
                self.logger.error(f"❌ Mock execution failed: {opportunity.symbol} - {e}")
        return results
    
    def monitor_positions(self) -> List[TradeResult]:
        """Monitor existing positions for exit opportunities"""
        # Mock implementation for testing
        return []
    
    def analyze_opportunities(self) -> List[TradeOpportunity]:
        """
        Enhanced opportunity analysis using multiple data sources
        """
        opportunities = []
        current_session = self._get_current_session()
        session_config = self.enhanced_session_configs[current_session]
        
        self.logger.info(f"🔍 Analyzing crypto opportunities - Session: {current_session.value}")
        
        for symbol, crypto_info in self.enhanced_crypto_universe.items():
            try:
                # Enhanced analysis with multiple data sources
                analysis = self._analyze_crypto_enhanced(symbol, crypto_info, session_config)
                
                if analysis and analysis.overall_confidence >= session_config['min_confidence']:
                    opportunity = TradeOpportunity(
                        symbol=symbol,
                        action=analysis.recommended_action,
                        quantity=self._calculate_position_size(symbol, analysis),
                        confidence=analysis.overall_confidence,
                        reasoning=self._generate_reasoning(analysis),
                        metadata={
                            'session': current_session.value,
                            'strategy': session_config['strategy'].value,
                            'data_sources': analysis.data_sources_used,
                            'data_quality': analysis.data_quality_score,
                            'technical_confidence': analysis.technical_confidence,
                            'fundamental_confidence': analysis.fundamental_confidence,
                            'ml_confidence': analysis.ml_confidence,
                            'risk_score': analysis.risk_score
                        }
                    )
                    opportunities.append(opportunity)
                    self.logger.info(f"✅ Opportunity found: {symbol} - {analysis.recommended_action.value} "
                                   f"(confidence: {analysis.overall_confidence:.2f})")
                
            except Exception as e:
                self.logger.error(f"❌ Analysis failed for {symbol}: {e}")
                continue
        
        self.logger.info(f"📊 Enhanced analysis complete: {len(opportunities)} opportunities found")
        return opportunities
    
    def _analyze_crypto_enhanced(self, symbol: str, crypto_info: Dict, 
                               session_config: Dict) -> Optional[EnhancedCryptoAnalysis]:
        """
        Enhanced cryptocurrency analysis with multi-source data
        """
        try:
            # Get enhanced market data
            if self.enhanced_data_manager:
                market_data = self.enhanced_data_manager.get_enhanced_market_data(symbol)
                if not market_data or 'bid' not in market_data:
                    self.logger.warning(f"⚠️ No market data available for {symbol}")
                    return None
                
                current_price = (market_data['bid'] + market_data['ask']) / 2
                data_sources = market_data.get('sources_used', ['unknown'])
                data_quality = market_data.get('data_quality_score', 0.5)
            else:
                # Fallback to basic price (maintain compatibility)
                current_price = self._get_fallback_price(symbol)
                if not current_price:
                    return None
                data_sources = ['fallback']
                data_quality = 0.3
            
            # Technical analysis (enhanced or fallback)
            technical_analysis = self._perform_technical_analysis(symbol, market_data if self.enhanced_data_manager else None)
            
            # Fundamental analysis (NEW - if enhanced data available)
            fundamental_analysis = self._perform_fundamental_analysis(symbol, market_data if self.enhanced_data_manager else None)
            
            # ML analysis (NEW - if enhanced ML available)
            ml_analysis = self._perform_ml_analysis(symbol, technical_analysis, fundamental_analysis)
            
            # Combine all analyses
            overall_confidence, recommended_action, risk_score = self._combine_analyses(
                technical_analysis, fundamental_analysis, ml_analysis, session_config
            )
            
            return EnhancedCryptoAnalysis(
                symbol=symbol,
                current_price=current_price,
                timestamp=datetime.now(timezone.utc),
                technical_confidence=technical_analysis.get('confidence', 0.0),
                technical_signals=technical_analysis.get('signals', {}),
                fundamental_confidence=fundamental_analysis.get('confidence') if fundamental_analysis else None,
                news_sentiment=fundamental_analysis.get('sentiment_score') if fundamental_analysis else None,
                market_sentiment=fundamental_analysis.get('market_sentiment') if fundamental_analysis else None,
                ml_confidence=ml_analysis.get('confidence') if ml_analysis else None,
                ml_prediction=ml_analysis.get('prediction') if ml_analysis else None,
                ml_probabilities=ml_analysis.get('probabilities') if ml_analysis else None,
                data_sources_used=data_sources,
                data_quality_score=data_quality,
                overall_confidence=overall_confidence,
                recommended_action=recommended_action,
                risk_score=risk_score
            )
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced analysis failed for {symbol}: {e}")
            return None
    
    def _perform_technical_analysis(self, symbol: str, market_data: Dict = None) -> Dict[str, Any]:
        """
        Enhanced technical analysis using TA-Lib or fallback indicators
        """
        try:
            if self.enhanced_indicators and market_data:
                # Use enhanced indicators with real historical data
                historical_data = self.enhanced_data_manager.get_historical_data(symbol, period="1mo", interval="1h")
                
                if historical_data is not None and not historical_data.empty:
                    # Extract OHLCV data
                    high_prices = historical_data['high'].values
                    low_prices = historical_data['low'].values
                    close_prices = historical_data['close'].values
                    volumes = historical_data['volume'].values if 'volume' in historical_data.columns else None
                    
                    # Get comprehensive analysis
                    analysis = self.enhanced_indicators.get_comprehensive_analysis(
                        high_prices.tolist(), low_prices.tolist(), close_prices.tolist(),
                        volumes.tolist() if volumes is not None else None
                    )
                    
                    return {
                        'confidence': self._calculate_technical_confidence(analysis),
                        'signals': analysis['signals'],
                        'indicators': analysis['indicators'],
                        'strength': analysis['strength'],
                        'source': 'enhanced_talib'
                    }
            
            # Fallback to existing technical indicators
            if hasattr(self, 'technical_indicators'):
                # Use existing fallback method
                return self._fallback_technical_analysis(symbol)
            
            return {'confidence': 0.5, 'signals': {}, 'source': 'none'}
            
        except Exception as e:
            self.logger.warning(f"⚠️ Technical analysis failed for {symbol}: {e}")
            return {'confidence': 0.3, 'signals': {}, 'source': 'error'}
    
    def _perform_fundamental_analysis(self, symbol: str, market_data: Dict = None) -> Optional[Dict[str, Any]]:
        """
        Fundamental analysis using news sentiment and market data (NEW)
        """
        if not self.enhanced_data_manager:
            return None
        
        try:
            fundamental_data = {}
            
            # Get fundamental data if available
            fundamentals = self.enhanced_data_manager.get_fundamental_data(symbol)
            if fundamentals:
                fundamental_data.update(fundamentals)
            
            # Get news sentiment
            news = self.enhanced_data_manager.get_news_sentiment(symbol, limit=10)
            if news:
                # Calculate sentiment score
                sentiment_score = self._calculate_news_sentiment(news)
                fundamental_data.update({
                    'news_items': len(news),
                    'sentiment_score': sentiment_score,
                    'market_sentiment': 'bullish' if sentiment_score > 0.1 else 'bearish' if sentiment_score < -0.1 else 'neutral'
                })
            
            # Calculate fundamental confidence
            confidence = self._calculate_fundamental_confidence(fundamental_data)
            
            return {
                'confidence': confidence,
                'sentiment_score': fundamental_data.get('sentiment_score', 0.0),
                'market_sentiment': fundamental_data.get('market_sentiment', 'neutral'),
                'data': fundamental_data,
                'source': 'enhanced_fundamental'
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Fundamental analysis failed for {symbol}: {e}")
            return None
    
    def _perform_ml_analysis(self, symbol: str, technical_analysis: Dict, 
                           fundamental_analysis: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """
        ML-based analysis using enhanced models (NEW)
        """
        if not self.enhanced_ml_framework:
            return None
        
        try:
            # Prepare features from technical and fundamental analysis
            features = self._prepare_ml_features(technical_analysis, fundamental_analysis)
            
            if features is None:
                return None
            
            # Get available models
            model_summary = self.enhanced_ml_framework.get_model_summary()
            
            if model_summary['total_models'] == 0:
                return None
            
            # Use the first available model for prediction
            model_ids = list(model_summary['models'].keys())
            if not model_ids:
                return None
            
            model_id = model_ids[0]  # Use first available model
            
            # Make prediction
            prediction, probabilities = self.enhanced_ml_framework.predict(model_id, features)
            
            if prediction is not None:
                # Convert prediction to trading action
                action_map = {0: 'sell', 1: 'hold', 2: 'buy'}
                predicted_action = action_map.get(prediction, 'hold')
                
                # Calculate confidence from probabilities
                confidence = max(probabilities) if probabilities is not None else 0.5
                
                return {
                    'confidence': confidence,
                    'prediction': predicted_action,
                    'probabilities': {
                        'sell': probabilities[0] if probabilities is not None else 0.33,
                        'hold': probabilities[1] if probabilities is not None else 0.34,
                        'buy': probabilities[2] if probabilities is not None else 0.33
                    },
                    'model_id': model_id,
                    'source': 'enhanced_ml'
                }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ ML analysis failed for {symbol}: {e}")
            return None
    
    def _combine_analyses(self, technical: Dict, fundamental: Optional[Dict], 
                         ml: Optional[Dict], session_config: Dict) -> Tuple[float, TradeAction, float]:
        """
        Combine all analyses to determine overall confidence and action
        """
        # Weights based on session strategy
        strategy = session_config['strategy']
        
        if strategy == CryptoStrategy.ML_ENSEMBLE:
            weights = {'technical': 0.3, 'fundamental': 0.2, 'ml': 0.5}
        elif strategy == CryptoStrategy.FUNDAMENTAL:
            weights = {'technical': 0.4, 'fundamental': 0.4, 'ml': 0.2}
        else:  # MOMENTUM, BREAKOUT, REVERSAL
            weights = {'technical': 0.6, 'fundamental': 0.2, 'ml': 0.2}
        
        # Calculate weighted confidence
        total_confidence = 0.0
        total_weight = 0.0
        
        # Technical analysis (always available)
        tech_confidence = technical.get('confidence', 0.0)
        total_confidence += tech_confidence * weights['technical']
        total_weight += weights['technical']
        
        # Fundamental analysis (if available)
        if fundamental:
            fund_confidence = fundamental.get('confidence', 0.0)
            total_confidence += fund_confidence * weights['fundamental']
            total_weight += weights['fundamental']
        
        # ML analysis (if available)
        if ml:
            ml_confidence = ml.get('confidence', 0.0)
            total_confidence += ml_confidence * weights['ml']
            total_weight += weights['ml']
        
        # Normalize confidence
        overall_confidence = total_confidence / total_weight if total_weight > 0 else 0.0
        
        # Determine action based on combined signals
        recommended_action = self._determine_action(technical, fundamental, ml, overall_confidence)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(technical, fundamental, ml)
        
        return overall_confidence, recommended_action, risk_score
    
    def _determine_action(self, technical: Dict, fundamental: Optional[Dict], 
                         ml: Optional[Dict], confidence: float) -> TradeAction:
        """
        Determine trading action based on combined analysis
        """
        buy_signals = 0
        sell_signals = 0
        total_signals = 0
        
        # Technical signals
        tech_strength = technical.get('strength', 'neutral')
        if tech_strength == 'bullish':
            buy_signals += 1
        elif tech_strength == 'bearish':
            sell_signals += 1
        total_signals += 1
        
        # Fundamental signals
        if fundamental:
            market_sentiment = fundamental.get('market_sentiment', 'neutral')
            if market_sentiment == 'bullish':
                buy_signals += 1
            elif market_sentiment == 'bearish':
                sell_signals += 1
            total_signals += 1
        
        # ML signals
        if ml:
            ml_prediction = ml.get('prediction', 'hold')
            if ml_prediction == 'buy':
                buy_signals += 1
            elif ml_prediction == 'sell':
                sell_signals += 1
            total_signals += 1
        
        # Decision logic
        if confidence < 0.5:
            return TradeAction.HOLD
        
        buy_ratio = buy_signals / total_signals if total_signals > 0 else 0
        sell_ratio = sell_signals / total_signals if total_signals > 0 else 0
        
        if buy_ratio > 0.5 and confidence > 0.6:
            return TradeAction.BUY
        elif sell_ratio > 0.5 and confidence > 0.6:
            return TradeAction.SELL
        else:
            return TradeAction.HOLD
    
    def _calculate_technical_confidence(self, analysis: Dict) -> float:
        """Calculate confidence from enhanced technical analysis"""
        signals = analysis.get('signals', {})
        strength = analysis.get('strength', 'neutral')
        
        # Base confidence from signal consensus
        signal_values = list(signals.values())
        if not signal_values:
            return 0.5
        
        consensus_signals = sum(1 for s in signal_values if s != 'neutral')
        consensus_ratio = consensus_signals / len(signal_values)
        
        # Boost for strong directional bias
        strength_boost = 0.2 if strength in ['bullish', 'bearish'] else 0.0
        
        return min(0.5 + (consensus_ratio * 0.3) + strength_boost, 1.0)
    
    def _calculate_fundamental_confidence(self, fundamental_data: Dict) -> float:
        """Calculate confidence from fundamental analysis"""
        confidence = 0.5  # Base confidence
        
        # News sentiment contribution
        sentiment_score = fundamental_data.get('sentiment_score', 0.0)
        confidence += abs(sentiment_score) * 0.3
        
        # News volume contribution
        news_items = fundamental_data.get('news_items', 0)
        if news_items > 5:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_news_sentiment(self, news: List[Dict]) -> float:
        """Calculate sentiment score from news items"""
        if not news:
            return 0.0
        
        # Simple sentiment calculation (could be enhanced with NLP)
        positive_keywords = ['bullish', 'rise', 'surge', 'breakout', 'buy', 'positive', 'growth']
        negative_keywords = ['bearish', 'fall', 'crash', 'sell', 'negative', 'decline', 'loss']
        
        total_sentiment = 0.0
        for item in news:
            headline = item.get('headline', '').lower()
            summary = item.get('summary', '').lower()
            text = headline + ' ' + summary
            
            positive_count = sum(1 for word in positive_keywords if word in text)
            negative_count = sum(1 for word in negative_keywords if word in text)
            
            if positive_count > negative_count:
                total_sentiment += 0.1
            elif negative_count > positive_count:
                total_sentiment -= 0.1
        
        return total_sentiment / len(news)
    
    def _prepare_ml_features(self, technical: Dict, fundamental: Optional[Dict]) -> Optional[np.ndarray]:
        """Prepare feature vector for ML model"""
        import numpy as np
        
        features = []
        
        # Technical features
        tech_confidence = technical.get('confidence', 0.0)
        features.append(tech_confidence)
        
        # Extract key technical indicators
        indicators = technical.get('indicators', {})
        features.extend([
            indicators.get('rsi', 50.0) / 100.0,  # Normalize RSI
            float(indicators.get('moving_averages', {}).get(20, 0) > 0),  # MA signal
            float(technical.get('strength') == 'bullish') - float(technical.get('strength') == 'bearish'),
        ])
        
        # Fundamental features
        if fundamental:
            features.extend([
                fundamental.get('confidence', 0.0),
                fundamental.get('sentiment_score', 0.0),
                float(fundamental.get('market_sentiment') == 'bullish') - float(fundamental.get('market_sentiment') == 'bearish'),
            ])
        else:
            features.extend([0.0, 0.0, 0.0])  # Padding
        
        # Pad to minimum required features (10 for example)
        while len(features) < 10:
            features.append(0.0)
        
        return np.array(features[:10]).reshape(1, -1)  # Ensure 10 features
    
    def _calculate_risk_score(self, technical: Dict, fundamental: Optional[Dict], 
                            ml: Optional[Dict]) -> float:
        """Calculate overall risk score"""
        risk_factors = []
        
        # Technical risk
        tech_confidence = technical.get('confidence', 0.0)
        risk_factors.append(1.0 - tech_confidence)  # Lower confidence = higher risk
        
        # Fundamental risk
        if fundamental:
            fund_confidence = fundamental.get('confidence', 0.0)
            risk_factors.append(1.0 - fund_confidence)
        
        # ML uncertainty risk
        if ml and 'probabilities' in ml:
            probs = list(ml['probabilities'].values())
            uncertainty = 1.0 - max(probs)  # High uncertainty = high risk
            risk_factors.append(uncertainty)
        
        return sum(risk_factors) / len(risk_factors) if risk_factors else 0.5
    
    def _get_current_session(self) -> TradingSession:
        """Determine current trading session based on UTC time"""
        current_hour = datetime.now(timezone.utc).hour
        
        if 0 <= current_hour < 8:
            return TradingSession.ASIA_PRIME
        elif 8 <= current_hour < 16:
            return TradingSession.EUROPE_PRIME
        else:
            return TradingSession.US_PRIME
    
    def _get_fallback_price(self, symbol: str) -> Optional[float]:
        """Fallback price retrieval for compatibility"""
        try:
            # Implement basic price retrieval (placeholder)
            return 50000.0  # Placeholder price
        except Exception:
            return None
    
    def _fallback_technical_analysis(self, symbol: str) -> Dict[str, Any]:
        """Fallback technical analysis using existing indicators"""
        return {
            'confidence': 0.6,
            'signals': {'momentum': 'bullish'},
            'strength': 'neutral',
            'source': 'fallback'
        }
    
    def _generate_reasoning(self, analysis: EnhancedCryptoAnalysis) -> str:
        """Generate human-readable reasoning for the trade opportunity"""
        reasoning_parts = []
        
        # Data quality
        reasoning_parts.append(f"Data quality: {analysis.data_quality_score:.1f}/1.0 from {len(analysis.data_sources_used)} sources")
        
        # Technical analysis
        reasoning_parts.append(f"Technical confidence: {analysis.technical_confidence:.2f}")
        
        # Fundamental analysis
        if analysis.fundamental_confidence is not None:
            reasoning_parts.append(f"Fundamental confidence: {analysis.fundamental_confidence:.2f}")
            if analysis.market_sentiment:
                reasoning_parts.append(f"Market sentiment: {analysis.market_sentiment}")
        
        # ML analysis
        if analysis.ml_confidence is not None:
            reasoning_parts.append(f"ML confidence: {analysis.ml_confidence:.2f}")
            if analysis.ml_prediction:
                reasoning_parts.append(f"ML prediction: {analysis.ml_prediction}")
        
        # Risk assessment
        reasoning_parts.append(f"Risk score: {analysis.risk_score:.2f}")
        
        return " | ".join(reasoning_parts)
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get enhanced module information"""
        base_info = {
            'module_name': self.module_name,
            'supported_symbols': self.supported_symbols,
            'config': {
                'enabled': self.config.enabled,
                'max_positions': self.config.max_positions,
                'min_confidence': self.config.min_confidence
            }
        }
        
        # Add enhanced capabilities information
        enhanced_info = {
            'enhanced_data_available': ENHANCED_DATA_AVAILABLE,
            'enhanced_indicators_available': ENHANCED_INDICATORS_AVAILABLE,
            'enhanced_ml_available': ENHANCED_ML_AVAILABLE,
            'data_sources': [],
            'crypto_universe_size': len(self.enhanced_crypto_universe)
        }
        
        # Check data source health
        if self.enhanced_data_manager:
            health = self.enhanced_data_manager.check_data_sources_health()
            enhanced_info['data_sources'] = [source for source, available in health.items() if available]
        
        base_info.update(enhanced_info)
        return base_info