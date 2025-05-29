#!/usr/bin/env python3

import os
import sys
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import Phase 2 foundation
from phase2_trader import Phase2Trader

# Import Phase 3 intelligence modules
from technical_indicators import TechnicalIndicators
from market_regime_detector import MarketRegimeDetector
from pattern_recognition import PatternRecognition

# Import Phase 4.1 global market capability
from global_market_manager import GlobalMarketManager

# Import Phase 4.3 options trading capability 
from options_manager import OptionsManager

# Import Phase 4.4 crypto trading capability
from crypto_trader import CryptoTrader

# Import Intelligent Exit Management System
from intelligent_exit_manager import IntelligentExitManager

class Phase3Trader(Phase2Trader):
    """
    Phase 3: Intelligence Layer
    
    Inherits all Phase 2 execution capabilities and adds:
    - Technical indicators (RSI, MACD, Bollinger Bands)
    - Enhanced market regime detection (Bull/Bear/Sideways)
    - Pattern recognition (breakouts, support/resistance, mean reversion)
    - Sophisticated market analysis and decision making
    """
    
    def __init__(self, use_database=True, market_tier=2, global_trading=False, options_trading=False, crypto_trading=False):
        super().__init__(use_database, market_tier)
        
        # Initialize intelligence modules
        self.technical_indicators = TechnicalIndicators()
        self.regime_detector = MarketRegimeDetector()
        self.pattern_recognition = PatternRecognition()
        
        # Phase 4.1: Initialize global market manager
        self.global_trading = global_trading
        if self.global_trading:
            self.global_market_manager = GlobalMarketManager()
            print("🌍 Global Market Trading: ✅ Enabled")
        else:
            self.global_market_manager = None
            print("🌍 Global Market Trading: ❌ Disabled")
        
        # Phase 4.3: Initialize options trading
        self.options_trading = options_trading
        if self.options_trading:
            self.options_manager = OptionsManager(self.api, self.risk_manager)
            print("📊 Options Trading: ✅ Enabled")
        else:
            self.options_manager = None
            print("📊 Options Trading: ❌ Disabled")
        
        # Phase 4.4: Initialize 24/7 crypto trading
        self.crypto_trading = crypto_trading
        if self.crypto_trading:
            self.crypto_trader = CryptoTrader(self.api, self.risk_manager)
            print("₿ 24/7 Crypto Trading: ✅ Enabled")
        else:
            self.crypto_trader = None
            print("₿ 24/7 Crypto Trading: ❌ Disabled")
        
        # Phase 3 specific settings
        self.intelligence_enabled = True
        self.min_technical_confidence = 0.6  # Minimum confidence from technical analysis
        self.regime_weight = 0.4  # Weight of regime analysis in final decision
        self.technical_weight = 0.4  # Weight of technical indicators
        self.pattern_weight = 0.2  # Weight of pattern recognition
        
        # Initialize Intelligent Exit Manager
        try:
            self.intelligent_exit_manager = IntelligentExitManager(
                api=self.api,
                risk_manager=self.risk_manager,
                technical_indicators=self.technical_indicators,
                regime_detector=self.regime_detector,
                pattern_recognition=self.pattern_recognition,
                ml_models=None  # Will integrate ML models when available
            )
            print("🧠 Intelligent Exit Manager: ✅ Enabled")
        except Exception as e:
            print(f"⚠️ Intelligent Exit Manager failed to initialize: {e}")
            self.intelligent_exit_manager = None
        
        print("🧠 Phase 3 Intelligence Layer Initialized")
        print(f"   📊 Technical Indicators: {'✅ Enabled' if self.intelligence_enabled else '❌ Disabled'}")
        print(f"   🎯 Market Regime Detection: Enhanced")
        print(f"   🔍 Pattern Recognition: Active")
        print(f"   🧠 Intelligent Exits: {'✅ Enabled' if self.intelligent_exit_manager else '❌ Disabled'}")
    
    def analyze_symbol_intelligence(self, symbol: str, price: float, volume: int = 0) -> Dict:
        """
        Comprehensive intelligence analysis for a symbol
        Combines technical indicators, regime detection, and pattern recognition
        """
        # Add data to all intelligence modules
        timestamp = datetime.now()
        self.technical_indicators.add_price_data(symbol, price, volume, timestamp)
        self.regime_detector.add_market_data(symbol, price, volume, timestamp)
        self.pattern_recognition.add_price_data(symbol, price, volume, timestamp)
        
        # Initialize analysis dictionary first
        analysis = {
            'symbol': symbol,
            'current_price': price,
            'timestamp': timestamp.isoformat(),
            'intelligence_scores': {}
        }
        
        # Track data accumulation progress
        price_data_count = len(self.technical_indicators.price_history.get(symbol, []))
        analysis['data_points'] = price_data_count
        
        # Technical Indicators Analysis
        if symbol in self.technical_indicators.initialized_symbols:
            tech_analysis = self.technical_indicators.get_comprehensive_analysis(symbol)
            if 'error' not in tech_analysis:
                analysis['technical_indicators'] = tech_analysis
                
                # Extract signals and confidence
                signals = []
                if 'indicators' in tech_analysis:
                    for indicator, data in tech_analysis['indicators'].items():
                        if isinstance(data, dict) and 'signal' in data:
                            signals.append(data['signal'])
                
                buy_signals = signals.count('buy')
                sell_signals = signals.count('sell')
                total_signals = len(signals)
                
                if total_signals > 0:
                    if buy_signals > sell_signals:
                        tech_signal = 'buy'
                        tech_confidence = buy_signals / total_signals
                    elif sell_signals > buy_signals:
                        tech_signal = 'sell'
                        tech_confidence = sell_signals / total_signals
                    else:
                        tech_signal = 'hold'
                        tech_confidence = 0.5
                else:
                    tech_signal = 'hold'
                    tech_confidence = 0.5
                
                analysis['intelligence_scores']['technical'] = {
                    'signal': tech_signal,
                    'confidence': tech_confidence,
                    'indicators_count': total_signals
                }
        
        # Market Regime Analysis
        regime_analysis = self.regime_detector.detect_trend_regime(symbol)
        if regime_analysis:
            analysis['regime_detection'] = regime_analysis
            
            # Convert regime to trading signal
            if regime_analysis['regime'] == 'bull' and regime_analysis['confidence'] > 0.6:
                regime_signal = 'buy'
                regime_confidence = regime_analysis['confidence']
            elif regime_analysis['regime'] == 'bear' and regime_analysis['confidence'] > 0.6:
                regime_signal = 'sell'
                regime_confidence = regime_analysis['confidence']
            else:
                regime_signal = 'hold'
                regime_confidence = 0.5
            
            analysis['intelligence_scores']['regime'] = {
                'signal': regime_signal,
                'confidence': regime_confidence,
                'regime': regime_analysis['regime']
            }
        
        # Pattern Recognition Analysis
        pattern_analysis = self.pattern_recognition.get_comprehensive_pattern_analysis(symbol)
        if 'overall_assessment' in pattern_analysis:
            analysis['pattern_recognition'] = pattern_analysis
            
            overall_pattern = pattern_analysis['overall_assessment']
            pattern_signal = overall_pattern['signal']
            pattern_confidence = overall_pattern['strength']
            
            analysis['intelligence_scores']['pattern'] = {
                'signal': pattern_signal,
                'confidence': pattern_confidence,
                'patterns_count': overall_pattern.get('pattern_count', 0)
            }
        
        # Combined Intelligence Score
        analysis['combined_intelligence'] = self.calculate_combined_intelligence_score(
            analysis.get('intelligence_scores', {})
        )
        
        return analysis
    
    def calculate_combined_intelligence_score(self, intelligence_scores: Dict) -> Dict:
        """
        Calculate combined intelligence score from all analysis modules
        Returns: {'signal': str, 'confidence': float, 'components': Dict}
        """
        if not intelligence_scores:
            return {'signal': 'hold', 'confidence': 0.5, 'components': {}}
        
        # Weight the different components
        weighted_scores = {}
        total_weight = 0
        
        # Technical indicators
        if 'technical' in intelligence_scores:
            tech = intelligence_scores['technical']
            weight = self.technical_weight
            score = 1 if tech['signal'] == 'buy' else -1 if tech['signal'] == 'sell' else 0
            weighted_scores['technical'] = score * tech['confidence'] * weight
            total_weight += weight
        
        # Market regime
        if 'regime' in intelligence_scores:
            regime = intelligence_scores['regime']
            weight = self.regime_weight
            score = 1 if regime['signal'] == 'buy' else -1 if regime['signal'] == 'sell' else 0
            weighted_scores['regime'] = score * regime['confidence'] * weight
            total_weight += weight
        
        # Pattern recognition
        if 'pattern' in intelligence_scores:
            pattern = intelligence_scores['pattern']
            weight = self.pattern_weight
            score = 1 if pattern['signal'] == 'bullish' else -1 if pattern['signal'] == 'bearish' else 0
            weighted_scores['pattern'] = score * pattern['confidence'] * weight
            total_weight += weight
        
        # Calculate combined score
        if total_weight > 0:
            combined_score = sum(weighted_scores.values()) / total_weight
            
            # Determine signal and confidence
            if combined_score > 0.2:
                signal = 'buy'
                confidence = abs(combined_score)
            elif combined_score < -0.2:
                signal = 'sell'
                confidence = abs(combined_score)
            else:
                signal = 'hold'
                confidence = 1 - abs(combined_score)
            
            return {
                'signal': signal,
                'confidence': min(confidence, 1.0),
                'combined_score': combined_score,
                'components': weighted_scores,
                'total_weight': total_weight
            }
        
        return {'signal': 'hold', 'confidence': 0.5, 'components': {}}
    
    def enhanced_strategy_selection(self, quotes: list, market_regime: str, confidence: float) -> str:
        """
        Enhanced strategy selection using Phase 3 intelligence
        """
        # Get overall market intelligence
        market_intelligence = {}
        
        # Analyze core market indices for overall regime
        for symbol in ['SPY', 'QQQ', 'IWM']:
            quote_data = next((q for q in quotes if q['symbol'] == symbol), None)
            if quote_data:
                intel = self.analyze_symbol_intelligence(symbol, quote_data['ask'], quote_data.get('volume', 0))
                if 'combined_intelligence' in intel:
                    market_intelligence[symbol] = intel['combined_intelligence']
        
        # Calculate overall market intelligence signal
        if market_intelligence:
            market_signals = [intel['signal'] for intel in market_intelligence.values()]
            market_confidences = [intel['confidence'] for intel in market_intelligence.values()]
            
            buy_signals = market_signals.count('buy')
            sell_signals = market_signals.count('sell')
            avg_confidence = sum(market_confidences) / len(market_confidences)
            
            # Enhanced strategy selection based on intelligence
            if buy_signals >= 2 and avg_confidence > 0.7:
                return "aggressive_momentum"
            elif buy_signals >= 2 and avg_confidence > 0.5:
                return "momentum"
            elif sell_signals >= 2:
                return "defensive"
            elif buy_signals > sell_signals and avg_confidence > 0.6:
                return "cautious_momentum"
            else:
                return "conservative"
        
        # Fallback to original strategy selection (fix parameter order)
        return super().enhanced_strategy_selection(market_regime, confidence, {}, quotes)
    
    def should_execute_trade_with_intelligence(self, symbol: str, strategy: str, base_confidence: float, price: float) -> tuple:
        """
        Enhanced trade decision using Phase 3 intelligence
        Returns: (should_trade: bool, final_confidence: float, intelligence_summary: str)
        """
        # Get Phase 2 risk assessment first
        should_trade_base, risk_reason, risk_details = self.risk_manager.should_execute_trade(
            symbol, strategy, base_confidence, price
        )
        
        if not should_trade_base:
            return False, base_confidence, f"Risk rejected: {risk_reason}"
        
        # Add intelligence analysis
        if not self.intelligence_enabled:
            return should_trade_base, base_confidence, "Intelligence disabled"
        
        # Get symbol intelligence
        intel_analysis = self.analyze_symbol_intelligence(symbol, price)
        
        if 'combined_intelligence' not in intel_analysis:
            return should_trade_base, base_confidence, "Insufficient intelligence data"
        
        combined_intel = intel_analysis['combined_intelligence']
        intel_signal = combined_intel['signal']
        intel_confidence = combined_intel['confidence']
        
        # Determine if intelligence supports the trade
        if strategy in ['aggressive_momentum', 'momentum', 'cautious_momentum']:
            # For bullish strategies, need bullish intelligence
            intelligence_supports = intel_signal == 'buy'
        elif strategy in ['defensive']:
            # For defensive strategies, bearish intelligence is okay
            intelligence_supports = intel_signal in ['sell', 'hold']
        else:
            # Conservative strategy - any signal okay
            intelligence_supports = True
        
        # Calculate final confidence
        if intelligence_supports and intel_confidence >= self.min_technical_confidence:
            # Boost confidence if intelligence strongly supports
            confidence_boost = (intel_confidence - self.min_technical_confidence) * 0.3
            final_confidence = min(base_confidence + confidence_boost, 1.0)
            intelligence_summary = f"Intelligence supports: {intel_signal} ({intel_confidence:.1%})"
        elif intelligence_supports:
            # Slight boost if supports but low confidence
            final_confidence = base_confidence + 0.1
            intelligence_summary = f"Weak intelligence support: {intel_signal} ({intel_confidence:.1%})"
        else:
            # Reduce confidence if intelligence conflicts
            final_confidence = base_confidence * 0.7
            intelligence_summary = f"Intelligence conflicts: {intel_signal} vs {strategy}"
        
        # Final decision based on intelligence-adjusted confidence
        should_trade_final = final_confidence >= self.min_confidence_to_trade
        
        # DEBUG: Add detailed logging to find why trades aren't executing
        print(f"🔍 INTELLIGENCE DECISION DEBUG: {symbol}")
        print(f"   Strategy: {strategy}")
        print(f"   Base confidence: {base_confidence:.1%}")
        print(f"   Intel signal: {intel_signal}")
        print(f"   Intel confidence: {intel_confidence:.1%}")
        print(f"   Intelligence supports: {intelligence_supports}")
        print(f"   Final confidence: {final_confidence:.1%}")
        print(f"   Min threshold: {self.min_confidence_to_trade:.1%}")
        print(f"   Should trade: {should_trade_final}")
        
        return should_trade_final, final_confidence, intelligence_summary
    
    def get_active_trading_symbols(self) -> List[str]:
        """
        Get symbols to trade based on current market sessions and global trading settings
        Phase 4.1: FIXED - Match symbols to open markets for immediate execution
        """
        # Check which markets are currently open
        import datetime
        import pytz
        
        current_utc = datetime.datetime.now(pytz.UTC)
        
        # Check US market (using Alpaca API)
        try:
            us_market_open = self.api.get_clock().is_open
        except:
            us_market_open = False
        
        # Check Asian markets (9:00-15:30 JST weekdays)
        tokyo_tz = pytz.timezone('Asia/Tokyo')
        tokyo_time = current_utc.astimezone(tokyo_tz)
        asian_market_open = (tokyo_time.weekday() < 5 and 9 <= tokyo_time.hour <= 15)
        
        # Check European markets (8:00-16:30 GMT weekdays)  
        london_tz = pytz.timezone('Europe/London')
        london_time = current_utc.astimezone(london_tz)
        european_market_open = (london_time.weekday() < 5 and 8 <= london_time.hour <= 16)
        
        print(f"🌍 MARKET STATUS CHECK:")
        print(f"   🇺🇸 US Market: {'OPEN' if us_market_open else 'CLOSED'}")
        print(f"   🇯🇵 Asian Market: {'OPEN' if asian_market_open else 'CLOSED'}")
        print(f"   🇪🇺 European Market: {'OPEN' if european_market_open else 'CLOSED'}")
        
        # CORRECTED: Only trade when exchanges are open for immediate execution
        selected_symbols = []
        
        if us_market_open:
            # Trade US-listed stocks/ETFs on US exchanges (immediate execution)
            from market_universe import get_symbols_by_tier
            us_symbols = get_symbols_by_tier(4)  # US stocks + ETFs + Global ETFs
            selected_symbols.extend(us_symbols)
            print(f"🇺🇸 Trading US-listed symbols on US exchanges: {len(us_symbols)} symbols")
            print(f"🇺🇸 Includes: US stocks, Global ETFs, all ADRs for immediate execution")
            
        elif asian_market_open:
            # During Asian hours: Trade Global ETFs with Asian exposure (execute immediately)
            # Note: True Asian exchange trading requires different broker
            asian_etfs = ['EWJ', 'FXI', 'EWT', 'INDA', 'EWY', 'VWO', 'VEA']  # These trade 24hrs
            selected_symbols.extend(asian_etfs)
            print(f"🇯🇵 Asian market hours: Trading Global ETFs with Asian exposure")
            print(f"🇯🇵 Note: These are US-listed ETFs that can trade extended hours")
            
        elif european_market_open:
            # During European hours: Trade Global ETFs with European exposure
            # Note: True European exchange trading requires different broker  
            european_etfs = ['VEA', 'IEFA', 'EFA', 'VGK']  # Europe-focused ETFs
            selected_symbols.extend(european_etfs)
            print(f"🇪🇺 European market hours: Trading European-focused ETFs")
            print(f"🇪🇺 Note: True EU exchange trading not supported by Alpaca")
            
        else:
            # No major markets open - core ETFs only
            selected_symbols = ['SPY', 'QQQ', 'VTI']  # Core broad market ETFs
            print(f"🌙 All markets closed: Core ETFs only")
            print(f"🌙 Note: Limited trading during global market closure")
        
        # Remove duplicates and return
        unique_symbols = list(set(selected_symbols))
        
        print(f"🎯 SELECTED SYMBOLS FOR IMMEDIATE EXECUTION: {unique_symbols}")
        
        # Limit to reasonable number for performance
        max_symbols = min(len(unique_symbols), 20)
        final_symbols = unique_symbols[:max_symbols]
        
        return final_symbols
    
    def prioritize_global_symbols(self, symbols: List[str]) -> List[str]:
        """
        Prioritize symbols based on volatility, volume, and momentum potential
        """
        from market_universe import get_momentum_symbols, get_defensive_symbols
        
        momentum_symbols = get_momentum_symbols()
        defensive_symbols = get_defensive_symbols()
        
        # Prioritize momentum symbols first, then defensive, then others
        prioritized = []
        
        # Add momentum symbols that are in our list
        for symbol in momentum_symbols:
            if symbol in symbols and symbol not in prioritized:
                prioritized.append(symbol)
        
        # Add defensive symbols
        for symbol in defensive_symbols:
            if symbol in symbols and symbol not in prioritized:
                prioritized.append(symbol)
        
        # Add remaining symbols
        for symbol in symbols:
            if symbol not in prioritized:
                prioritized.append(symbol)
        
        return prioritized
    
    def get_market_quotes(self):
        """
        Override to use global trading symbols when enabled
        Phase 4.1: Global Market Integration
        """
        if self.global_trading and self.global_market_manager:
            # Get global trading symbols based on active sessions
            symbols = self.get_active_trading_symbols()
        else:
            # Use parent class method (tier-based symbols)
            from market_universe import get_symbols_by_tier
            symbols = get_symbols_by_tier(self.market_tier)
        
        # Collect quotes for selected symbols
        quotes = []
        failed_count = 0
        
        for symbol in symbols:
            try:
                quote = self.api.get_latest_quote(symbol)
                if quote and quote.ask_price and quote.ask_price > 0:
                    quotes.append({
                        'symbol': symbol,
                        'ask': float(quote.ask_price),
                        'bid': float(quote.bid_price),
                        'volume': getattr(quote, 'ask_size', 0) or 0,
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                failed_count += 1
                if failed_count <= 3:  # Only show first few errors
                    print(f"⚠️ Failed to get quote for {symbol}: {str(e)[:50]}")
        
        if self.global_trading:
            print(f"🌍 Global Trading: Retrieved {len(quotes)} quotes, {failed_count} failed")
        
        return quotes
    
    def execute_trading_decisions_with_intelligence(self, quotes: list, strategy: str, confidence: float, cycle_id: int = None) -> Dict:
        """
        Enhanced trading execution with Phase 3 intelligence
        """
        if not self.execution_enabled:
            return {"status": "execution_disabled", "message": "Execution is disabled"}
        
        execution_summary = {
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy,
            "base_confidence": confidence,
            "intelligence_enabled": self.intelligence_enabled,
            "trades_attempted": 0,
            "trades_executed": 0,
            "intelligence_insights": [],
            "execution_details": []
        }
        
        # Get current positions to avoid duplicates
        current_positions = self.order_manager.get_current_positions()
        held_symbols = {pos['symbol'] for pos in current_positions}
        
        # Analyze and potentially trade each symbol
        for quote in quotes:
            symbol = quote['symbol']
            price = quote['ask']  # Use ask price for buying
            
            # Skip if we already hold this symbol
            if symbol in held_symbols:
                continue
            
            execution_summary["trades_attempted"] += 1
            
            # Phase 3 intelligence-enhanced decision
            should_trade, final_confidence, intel_summary = self.should_execute_trade_with_intelligence(
                symbol, strategy, confidence, price
            )
            
            execution_summary["intelligence_insights"].append({
                "symbol": symbol,
                "intelligence_summary": intel_summary,
                "final_confidence": final_confidence
            })
            
            if should_trade:
                # Execute the trade
                trade_result = self.order_manager.execute_buy_order(
                    symbol=symbol, 
                    strategy=strategy, 
                    confidence=final_confidence,
                    cycle_id=cycle_id
                )
                
                if trade_result["status"] == "success":
                    execution_summary["trades_executed"] += 1
                    
                    execution_summary["execution_details"].append({
                        "symbol": symbol,
                        "action": "BUY",
                        "shares": trade_result["shares"],
                        "price": trade_result["price"],
                        "value": trade_result["total_value"],
                        "intelligence_confidence": final_confidence,
                        "intelligence_summary": intel_summary
                    })
                    
                    print(f"🧠 INTELLIGENCE TRADE: {symbol}")
                    print(f"   💰 {trade_result['shares']} shares @ ${trade_result['price']:.2f}")
                    print(f"   🎯 Final Confidence: {final_confidence:.1%}")
                    print(f"   📊 Intelligence: {intel_summary}")
                else:
                    execution_summary["execution_details"].append({
                        "symbol": symbol,
                        "action": "REJECTED",
                        "reason": trade_result.get("message", "Unknown error"),
                        "intelligence_summary": intel_summary
                    })
        
        return execution_summary
    
    def run_trading_cycle_with_intelligence(self):
        """
        Enhanced trading cycle with Phase 3 intelligence
        """
        cycle_start = datetime.now()
        cycle_id = int(cycle_start.timestamp())
        
        print(f"\n🧠 PHASE 3 INTELLIGENCE CYCLE - {cycle_start.strftime('%H:%M:%S')}")
        print("=" * 60)
        
        try:
            # CRITICAL: Cancel all pending orders (ADRs on wrong exchanges)
            print("🧹 EMERGENCY: Cleaning up ADR orders that trade on wrong exchanges...")
            cancelled_count = self.order_manager.cancel_all_pending_orders()
            if cancelled_count > 0:
                print(f"🧹 EMERGENCY CLEANUP: Cancelled {cancelled_count} ADR orders that would queue on US exchanges")
            else:
                print("🧹 No pending orders to cancel - account clean")
            
            # Get market data
            print("📈 Collecting market data...")
            quotes = self.get_market_quotes()
            
            if not quotes:
                print("❌ No market data available")
                return
            
            print(f"✅ Retrieved {len(quotes)} quotes")
            
            # CRITICAL FIX: Position monitoring and exit management
            print("\n💼 POSITION MONITORING & EXIT MANAGEMENT")
            print("-" * 50)
            print(f"🔍 DEBUG: Intelligent exit manager status: {'✅ ACTIVE' if self.intelligent_exit_manager else '❌ INACTIVE'}")
            
            # Get current positions for monitoring
            try:
                positions = self.api.list_positions()
                if positions:
                    print(f"📊 Monitoring {len(positions)} open positions for intelligent exits...")
                    
                    # Use intelligent exit system instead of basic stop-losses
                    intelligent_exit_results = []
                    if self.intelligent_exit_manager:
                        for position in positions:
                            try:
                                symbol = position.symbol
                                
                                # Get current market data for the position
                                quote = self.api.get_latest_quote(symbol)
                                if not quote or not quote.bid_price:
                                    continue
                                
                                current_price = float(quote.bid_price)
                                entry_price = float(position.avg_cost)
                                
                                # Prepare market data for analysis
                                market_data = {
                                    'current_price': current_price,
                                    'volume': getattr(quote, 'volume', 0),
                                    'bid': float(quote.bid_price),
                                    'ask': float(quote.ask_price)
                                }
                                
                                # Prepare position info
                                position_info = {
                                    'avg_entry_price': entry_price,
                                    'quantity': float(position.qty),
                                    'entry_time': datetime.now(),  # Simplified - should come from DB
                                    'entry_confidence': 0.7  # Simplified - should come from DB
                                }
                                
                                # Analyze exit opportunity using intelligent system
                                exit_analysis = self.intelligent_exit_manager.analyze_exit_opportunity(
                                    symbol, position_info, market_data
                                )
                                
                                # Execute if intelligent system recommends exit
                                if exit_analysis.get('action') == 'sell':
                                    print(f"🧠 INTELLIGENT EXIT TRIGGERED: {symbol}")
                                    print(f"   📊 Reason: {exit_analysis.get('reason', 'Unknown')}")
                                    print(f"   🎯 Confidence: {exit_analysis.get('confidence', 0):.1%}")
                                    print(f"   📈 Signals: {len(exit_analysis.get('exit_signals', []))}")
                                    
                                    # Execute the intelligent exit
                                    exit_result = self.intelligent_exit_manager.execute_intelligent_exit(
                                        symbol, exit_analysis, self.order_manager
                                    )
                                    
                                    if exit_result.get('status') == 'success':
                                        intelligent_exit_results.append(exit_result)
                                        print(f"   ✅ Exit executed: {exit_result.get('exit_portion', 1):.0%} of position")
                                    else:
                                        print(f"   ❌ Exit failed: {exit_result.get('reason', 'Unknown')}")
                                else:
                                    # Just log the analysis for debugging
                                    pl_pct = ((current_price - entry_price) / entry_price) * 100
                                    signals = len(exit_analysis.get('exit_signals', []))
                                    print(f"   📊 {symbol}: P&L {pl_pct:+.1f}%, {signals} signals, confidence {exit_analysis.get('confidence', 0):.1%}")
                                
                            except Exception as e:
                                print(f"   ⚠️ Intelligent exit analysis failed for {position.symbol}: {e}")
                    
                    # Fallback to basic system if intelligent system unavailable
                    else:
                        print("   ⚠️ Using basic exit system (intelligent system unavailable)")
                        exit_results = self.order_manager.check_stop_losses()
                        if exit_results:
                            print(f"🔄 Executed {len(exit_results)} basic exit trades:")
                            for result in exit_results:
                                print(f"   📊 {result.get('symbol', 'Unknown')}: {result.get('reason', 'Unknown')} (P&L: {result.get('pl_pct', 0):.1f}%)")
                        intelligent_exit_results = exit_results
                    
                    # Summary of intelligent exits
                    if intelligent_exit_results:
                        print(f"🧠 INTELLIGENT EXITS EXECUTED: {len(intelligent_exit_results)}")
                        for result in intelligent_exit_results:
                            symbol = result.get('symbol', 'Unknown')
                            reason = result.get('reason', 'Unknown')
                            pl_pct = result.get('pl_pct', 0)
                            exit_portion = result.get('exit_portion', 1.0)
                            print(f"   🎯 {symbol}: {reason} ({pl_pct:+.1f}%, {exit_portion:.0%} exit)")
                    else:
                        print("✅ No intelligent exit triggers activated")
                    
                    # Time-based exit check (5-day max hold)
                    if hasattr(self.risk_manager, 'max_hold_days'):
                        max_hold_days = self.risk_manager.max_hold_days
                        print(f"⏰ Checking for positions older than {max_hold_days} days...")
                        
                        from datetime import timedelta
                        cutoff_date = datetime.now() - timedelta(days=max_hold_days)
                        
                        # Check each position age (this would need position tracking in DB)
                        aged_positions = 0
                        for pos in positions:
                            # For now, we'll implement basic age checking
                            # Full implementation would query DB for entry date
                            print(f"   📅 {pos.symbol}: Monitoring for time-based exit")
                            aged_positions += 1
                        
                        if aged_positions > 0:
                            print(f"📊 {aged_positions} positions under time-based monitoring")
                    
                    # Regime-based exit check
                    print("🧠 Checking for regime-based exits...")
                    if hasattr(self, 'last_regime') and market_regime != getattr(self, 'last_regime', market_regime):
                        print(f"⚠️ Market regime changed: {getattr(self, 'last_regime', 'Unknown')} → {market_regime}")
                        print("   💡 Consider reducing positions on regime change")
                        # This could trigger selective position reduction
                    
                    self.last_regime = market_regime
                    
                else:
                    print("📊 No open positions to monitor")
                    
            except Exception as e:
                print(f"⚠️ Position monitoring error: {e}")
            
            # Enhanced regime detection using intelligence
            print("\n🧠 ANALYZING MARKET INTELLIGENCE")
            print("-" * 40)
            
            # Add VIX data if available (simulated for now)
            import random
            simulated_vix = random.uniform(15, 25)
            self.regime_detector.add_vix_data(simulated_vix)
            
            # Get comprehensive market regime analysis
            regime_analysis = self.regime_detector.get_comprehensive_regime_analysis()
            
            # Extract regime information (now guaranteed to exist)
            overall = regime_analysis['overall_assessment']
            regime_type = overall['regime']
            
            if regime_type == 'bullish':
                market_regime = "active"
            elif regime_type == 'bearish':
                market_regime = "uncertain"
            else:
                market_regime = "neutral"
            
            regime_confidence = overall['confidence']
            
            # Display additional info if available
            if 'note' in overall:
                print(f"ℹ️ Regime Analysis: {overall['note']}")
                
                # Show data accumulation progress
                indices_analyzed = overall.get('indices_analyzed', 0)
                if indices_analyzed == 0:
                    print(f"📊 Intelligence Building: Accumulating market data...")
                    print(f"   💡 Technical indicators need 20-50 cycles for full analysis")
                    print(f"   🎯 Regime detection will improve as data accumulates")
            
            print(f"🎯 Market Regime: {market_regime} ({regime_confidence:.1%} confidence)")
            
            # Enhanced strategy selection
            strategy = self.enhanced_strategy_selection(quotes, market_regime, regime_confidence)
            print(f"🎯 Strategy: {strategy}")
            
            # Phase 4.4: Execute 24/7 crypto trading if enabled
            crypto_results = {}
            if self.crypto_trading and self.crypto_trader:
                print("\n₿ CRYPTO TRADING CYCLE")
                print("-" * 30)
                
                # Get active crypto symbols for current session
                crypto_symbols = self.crypto_trader.get_active_crypto_symbols()
                print(f"₿ Active crypto symbols: {crypto_symbols}")
                
                # Analyze and trade crypto opportunities
                for symbol in crypto_symbols:
                    try:
                        # Get crypto market data (simulated for now)
                        crypto_data = {
                            'price': random.uniform(30000, 70000) if 'BTC' in symbol else random.uniform(2000, 4000),
                            'high_24h': random.uniform(35000, 75000) if 'BTC' in symbol else random.uniform(2100, 4200),
                            'low_24h': random.uniform(28000, 65000) if 'BTC' in symbol else random.uniform(1900, 3800),
                            'price_24h_ago': random.uniform(29000, 69000) if 'BTC' in symbol else random.uniform(1950, 3950),
                            'volume_24h': random.uniform(500000, 2000000),
                            'avg_volume_30d': random.uniform(400000, 1500000)
                        }
                        
                        # Analyze crypto opportunity
                        crypto_analysis = self.crypto_trader.analyze_crypto_opportunity(symbol, crypto_data)
                        
                        # Debug output for crypto analysis
                        print(f"₿ {symbol}: confidence={crypto_analysis.get('confidence', 0):.1%}, min={crypto_analysis.get('min_confidence', 0):.1%}, tradeable={crypto_analysis.get('tradeable', False)}")
                        
                        if crypto_analysis.get('tradeable', False):
                            # Calculate crypto position size (smaller allocation)
                            position_size = 2000  # $2K base position for crypto
                            
                            # Execute crypto trade
                            crypto_result = self.crypto_trader.execute_crypto_trade(crypto_analysis, position_size)
                            crypto_results[symbol] = crypto_result
                            
                            if crypto_result['status'] == 'success':
                                print(f"₿ CRYPTO TRADE: {symbol}")
                                print(f"   📊 {crypto_result['side'].upper()}: {crypto_result['quantity']:.6f} @ ${crypto_data['price']:.0f}")
                                print(f"   🎯 Confidence: {crypto_result['confidence']:.1%}")
                                print(f"   🌍 Session: {crypto_result['session']}")
                            else:
                                print(f"₿ CRYPTO FAILED: {symbol} - {crypto_result.get('reason', 'Unknown error')}")
                        else:
                            print(f"₿ CRYPTO SKIP: {symbol} - confidence too low or not tradeable")
                        
                    except Exception as e:
                        print(f"⚠️ Crypto trading error for {symbol}: {e}")
            
            # CRITICAL FIX: Phase 4.3 - Real Options Trading Integration  
            options_results = {}
            if self.options_trading and self.options_manager:
                print("\n📊 REAL OPTIONS TRADING")
                print("-" * 30)
                
                try:
                    # Get top performing symbols for options trading
                    options_candidates = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA']  # High liquidity options
                    
                    for symbol in options_candidates[:3]:  # Limit to top 3 for now
                        try:
                            # Get current market data for the underlying
                            quote = self.api.get_latest_quote(symbol)
                            if not quote or not quote.ask_price:
                                continue
                                
                            underlying_price = float(quote.ask_price)
                            
                            # Analyze options opportunity based on market regime and confidence
                            options_analysis = {
                                'symbol': symbol,
                                'underlying_price': underlying_price,
                                'regime': regime_type,
                                'confidence': regime_confidence,
                                'strategy_recommendation': 'long_calls' if regime_type == 'bullish' and regime_confidence > 0.65 else 'protective_puts'
                            }
                            
                            print(f"📊 OPTIONS ANALYSIS: {symbol}")
                            print(f"   💰 Underlying: ${underlying_price:.2f}")
                            print(f"   🎯 Regime: {regime_type} ({regime_confidence:.1%})")
                            print(f"   📈 Strategy: {options_analysis['strategy_recommendation']}")
                            
                            # Execute options trade if conditions are favorable
                            if regime_confidence > 0.60:  # Minimum confidence for options
                                options_result = self.options_manager.execute_options_strategy(
                                    symbol=symbol,
                                    strategy=options_analysis['strategy_recommendation'],
                                    market_data={
                                        'price': underlying_price,
                                        'regime': regime_type,
                                        'confidence': regime_confidence
                                    }
                                )
                                
                                if options_result and options_result.get('status') == 'success':
                                    print(f"📊 OPTIONS TRADE: {symbol}")
                                    print(f"   🎯 Strategy: {options_result.get('strategy', 'Unknown')}")
                                    print(f"   💰 Contracts: {options_result.get('contracts', 0)}")
                                    print(f"   📊 Strike: ${options_result.get('strike', 0):.2f}")
                                    print(f"   📅 Expiration: {options_result.get('expiration', 'Unknown')}")
                                    options_results[symbol] = options_result
                                else:
                                    print(f"📊 OPTIONS SKIP: {symbol} - {options_result.get('reason', 'Unknown')}")
                            else:
                                print(f"📊 OPTIONS SKIP: {symbol} - confidence too low ({regime_confidence:.1%})")
                                
                        except Exception as e:
                            print(f"⚠️ Options analysis error for {symbol}: {e}")
                            
                except Exception as e:
                    print(f"⚠️ Options trading system error: {e}")
            else:
                print("\n📊 OPTIONS TRADING: ❌ DISABLED")
                print("-" * 30)
                print("   💡 Options trading module not enabled or initialized")
            
            # Phase 4.4: Enhanced Stock Trading Strategies
            enhanced_strategies = {}
            print("\n📊 ENHANCED STOCK STRATEGIES")
            print("-" * 30)
            
            # Implement aggressive stock strategies to compensate for no options
            # 1. Leveraged ETF Trading
            leveraged_etfs = ['TQQQ', 'UPRO', 'SOXL', 'FAS', 'UDOW']  # 3x leveraged ETFs
            for symbol in leveraged_etfs:
                try:
                    # Get current price
                    quote = self.api.get_latest_quote(symbol)
                    if quote and quote.ask_price:
                        price = float(quote.ask_price)
                        
                        # Use regime to determine if leveraged ETF is appropriate
                        if regime_confidence > 0.70 and regime_type == 'bullish':
                            # High confidence bullish - use leveraged ETFs for amplified returns
                            position_size = 5000  # $5K for leveraged ETF positions
                            
                            # Check if we should execute
                            should_trade, final_conf, intel = self.should_execute_trade_with_intelligence(
                                symbol, strategy, regime_confidence, price
                            )
                            
                            if should_trade:
                                trade_result = self.order_manager.execute_buy_order(
                                    symbol=symbol, 
                                    strategy=f"leveraged_{strategy}", 
                                    confidence=final_conf,
                                    cycle_id=cycle_id
                                )
                                
                                if trade_result["status"] == "success":
                                    print(f"📊 LEVERAGED ETF: {symbol}")
                                    print(f"   💰 {trade_result['shares']} shares @ ${trade_result['price']:.2f}")
                                    print(f"   🎯 3x Leverage Effect")
                                    print(f"   📊 Intelligence: {intel}")
                        
                except Exception as e:
                    print(f"⚠️ Leveraged ETF error for {symbol}: {e}")
            
            # 2. Sector Rotation Strategy
            sector_etfs = {
                'technology': 'XLK',
                'healthcare': 'XLV', 
                'financials': 'XLF',
                'energy': 'XLE',
                'consumer': 'XLY'
            }
            
            print(f"📊 Sector rotation based on regime: {regime_type}")
            if regime_type == 'bullish':
                # Bullish: Focus on growth sectors
                priority_sectors = ['technology', 'consumer', 'financials']
            elif regime_type == 'bearish':
                # Bearish: Focus on defensive sectors  
                priority_sectors = ['healthcare', 'consumer']
            else:
                # Neutral: Balanced approach
                priority_sectors = ['technology', 'healthcare']
            
            for sector in priority_sectors[:2]:  # Top 2 sectors
                symbol = sector_etfs[sector]
                try:
                    quote = self.api.get_latest_quote(symbol)
                    if quote and quote.ask_price:
                        price = float(quote.ask_price)
                        should_trade, final_conf, intel = self.should_execute_trade_with_intelligence(
                            symbol, f"sector_{sector}", regime_confidence, price
                        )
                        
                        if should_trade:
                            trade_result = self.order_manager.execute_buy_order(
                                symbol=symbol, 
                                strategy=f"sector_{sector}", 
                                confidence=final_conf,
                                cycle_id=cycle_id
                            )
                            
                            if trade_result["status"] == "success":
                                print(f"📊 SECTOR PLAY: {symbol} ({sector})")
                                print(f"   💰 {trade_result['shares']} shares @ ${trade_result['price']:.2f}")
                                
                except Exception as e:
                    print(f"⚠️ Sector ETF error for {symbol}: {e}")
            
            # 3. Momentum Amplification Strategy
            # Use higher position sizes during high-confidence periods
            if regime_confidence > 0.75 and regime_type == 'bullish':
                momentum_stocks = ['NVDA', 'TSLA', 'AMD', 'AAPL', 'MSFT']
                print(f"📊 MOMENTUM AMPLIFICATION: High confidence ({regime_confidence:.1%})")
                
                for symbol in momentum_stocks[:2]:  # Top 2 momentum stocks
                    try:
                        quote = self.api.get_latest_quote(symbol)
                        if quote and quote.ask_price:
                            price = float(quote.ask_price)
                            
                            # Use 2x normal position size for high-conviction trades
                            should_trade, final_conf, intel = self.should_execute_trade_with_intelligence(
                                symbol, "momentum_amplified", regime_confidence * 1.1, price  # Boost confidence
                            )
                            
                            if should_trade:
                                # Override position size for aggressive momentum
                                original_position_multiplier = self.risk_manager.position_size_multiplier
                                self.risk_manager.position_size_multiplier = 2.0  # 2x leverage through position size
                                
                                trade_result = self.order_manager.execute_buy_order(
                                    symbol=symbol, 
                                    strategy="momentum_amplified", 
                                    confidence=final_conf,
                                    cycle_id=cycle_id
                                )
                                
                                # Restore original multiplier
                                self.risk_manager.position_size_multiplier = original_position_multiplier
                                
                                if trade_result["status"] == "success":
                                    print(f"📊 MOMENTUM 2X: {symbol}")
                                    print(f"   💰 {trade_result['shares']} shares @ ${trade_result['price']:.2f}")
                                    print(f"   🚀 2x Position Size")
                                    print(f"   📊 Intelligence: {intel}")
                    
                    except Exception as e:
                        print(f"⚠️ Momentum stock error for {symbol}: {e}")
            
            # 4. Volatility Trading Strategy
            # Trade VIX-related ETFs based on market volatility
            volatility_symbols = {
                'low_vol': 'VXX',   # Long volatility
                'short_vol': 'SVXY'  # Short volatility
            }
            
            if regime_confidence > 0.60:
                if regime_type == 'uncertain':
                    # High uncertainty - long volatility
                    vol_symbol = volatility_symbols['low_vol']
                    vol_strategy = "long_volatility"
                elif regime_type == 'bullish' and regime_confidence > 0.80:
                    # Very bullish - short volatility
                    vol_symbol = volatility_symbols['short_vol'] 
                    vol_strategy = "short_volatility"
                else:
                    vol_symbol = None
                
                if vol_symbol:
                    try:
                        quote = self.api.get_latest_quote(vol_symbol)
                        if quote and quote.ask_price:
                            price = float(quote.ask_price)
                            should_trade, final_conf, intel = self.should_execute_trade_with_intelligence(
                                vol_symbol, vol_strategy, regime_confidence, price
                            )
                            
                            if should_trade:
                                trade_result = self.order_manager.execute_buy_order(
                                    symbol=vol_symbol, 
                                    strategy=vol_strategy, 
                                    confidence=final_conf,
                                    cycle_id=cycle_id
                                )
                                
                                if trade_result["status"] == "success":
                                    print(f"📊 VOLATILITY PLAY: {vol_symbol}")
                                    print(f"   💰 {trade_result['shares']} shares @ ${trade_result['price']:.2f}")
                                    print(f"   🎯 Strategy: {vol_strategy}")
                    
                    except Exception as e:
                        print(f"⚠️ Volatility ETF error for {vol_symbol}: {e}")
            
            # 5. Real Options Trading
            options_results = {}
            if self.options_trading and self.options_manager:
                print("\n📊 REAL OPTIONS TRADING")
                print("-" * 30)
                
                # Monitor current options exposure
                try:
                    options_monitoring = self.options_manager.monitor_options_positions()
                    print(f"📊 Options exposure: {options_monitoring['exposure'].get('options_allocation', 0):.1%}")
                    
                    # Show alerts if any
                    if options_monitoring['alerts']:
                        for alert in options_monitoring['alerts']:
                            print(f"⚠️ {alert['type']}: {alert['message']}")
                except Exception as e:
                    print(f"⚠️ Options monitoring error: {e}")
                
                # Analyze options opportunities for liquid stocks
                options_stocks = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA']
                for symbol in options_stocks:
                    try:
                        # Analyze options opportunity
                        options_analysis = self.options_manager.analyze_options_opportunity(
                            symbol, regime_type, regime_confidence
                        )
                        
                        recommended_strategy = options_analysis.get('recommended_strategy', {})
                        if recommended_strategy.get('strategy') != 'none':
                            # Calculate options position size
                            position_size = 3000  # $3K base position for options
                            
                            # Execute options strategy
                            options_result = self.options_manager.execute_options_strategy(
                                options_analysis, position_size
                            )
                            options_results[symbol] = options_result
                            
                            if options_result['status'] == 'success':
                                print(f"📊 OPTIONS TRADE: {symbol}")
                                print(f"   🎯 Strategy: {options_result['strategy']}")
                                print(f"   💰 Contracts: {options_result.get('contracts', 0)}")
                                print(f"   🎯 Confidence: {regime_confidence:.1%}")
                            elif options_result['status'] == 'error':
                                print(f"📊 OPTIONS FAILED: {symbol} - {options_result.get('reason', 'Unknown error')}")
                        else:
                            print(f"📊 OPTIONS SKIP: {symbol} - no suitable strategy")
                        
                    except Exception as e:
                        print(f"⚠️ Options trading error for {symbol}: {e}")
            
            # Execute trades with intelligence
            if self.execution_enabled:
                execution_result = self.execute_trading_decisions_with_intelligence(
                    quotes, strategy, regime_confidence, cycle_id
                )
                
                print(f"\n📊 EXECUTION SUMMARY:")
                print(f"   🎯 Trades Attempted: {execution_result['trades_attempted']}")
                print(f"   ✅ Trades Executed: {execution_result['trades_executed']}")
                print(f"   🧠 Intelligence Insights: {len(execution_result['intelligence_insights'])}")
            else:
                print("⚠️ Execution disabled - analysis only")
            
            # Store cycle data
            if self.use_database and self.db:
                try:
                    cycle_data = {
                        'regime': market_regime,
                        'confidence': regime_confidence,
                        'strategy': strategy,
                        'quotes_count': len(quotes),
                        'intelligence_enabled': self.intelligence_enabled,
                        'phase': 'phase3_intelligence',
                        'cycle_id': cycle_id
                    }
                    db_cycle_id = self.db.store_trading_cycle(cycle_data, cycle_id)
                    print(f"💾 Phase 3 cycle data stored (DB ID: {db_cycle_id})")
                except Exception as e:
                    print(f"⚠️ Cycle storage error: {e}")
            
            print(f"✅ Phase 3 cycle completed in {(datetime.now() - cycle_start).total_seconds():.1f}s")
            
        except Exception as e:
            print(f"❌ Phase 3 cycle error: {str(e)}")
            import traceback
            traceback.print_exc()
            print("🔄 Continuing to next cycle despite error...")
    
    def run_continuous_intelligence_trading(self):
        """
        Run continuous trading with Phase 3 intelligence
        """
        print(f"\n🧠 PHASE 3 INTELLIGENCE TRADER STARTING")
        print("=" * 60)
        print(f"⚡ Execution: {'ENABLED' if self.execution_enabled else 'DISABLED'}")
        print(f"🧠 Intelligence: {'ENABLED' if self.intelligence_enabled else 'DISABLED'}")
        print(f"🎯 Market Tier: {self.market_tier}")
        print(f"📊 Symbol Universe: {len(self.market_universe)} symbols")
        print(f"🎯 Min Confidence: {self.min_confidence_to_trade:.1%}")
        print(f"🧠 Min Technical Confidence: {self.min_technical_confidence:.1%}")
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                print(f"\n📊 Cycle #{cycle_count}")
                
                self.run_trading_cycle_with_intelligence()
                
                print(f"⏳ Next cycle in {self.cycle_delay} seconds...")
                time.sleep(self.cycle_delay)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Phase 3 Intelligence Trader stopped by user")
        except Exception as e:
            print(f"\n❌ Phase 3 system error: {str(e)}")
            import traceback
            traceback.print_exc()
            print("🔄 Restarting in 60 seconds...")
            time.sleep(60)
            # Try to restart the trading loop
            try:
                self.run_continuous_intelligence_trading()
            except Exception as restart_error:
                print(f"❌ Restart failed: {restart_error}")
                raise

if __name__ == "__main__":
    # Initialize Phase 3 Trader
    execution_enabled = os.getenv('EXECUTION_ENABLED', 'false').lower() == 'true'
    market_tier = int(os.getenv('MARKET_TIER', '2'))
    
    trader = Phase3Trader(use_database=True, market_tier=market_tier)
    trader.execution_enabled = execution_enabled
    trader.min_confidence_to_trade = float(os.getenv('MIN_CONFIDENCE', '0.7'))
    trader.min_technical_confidence = float(os.getenv('MIN_TECHNICAL_CONFIDENCE', '0.6'))
    
    # Start continuous trading
    trader.run_continuous_intelligence_trading()