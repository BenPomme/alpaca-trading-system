#!/usr/bin/env python3

import os
import sys
import time
import json
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

class Phase3Trader(Phase2Trader):
    """
    Phase 3: Intelligence Layer
    
    Inherits all Phase 2 execution capabilities and adds:
    - Technical indicators (RSI, MACD, Bollinger Bands)
    - Enhanced market regime detection (Bull/Bear/Sideways)
    - Pattern recognition (breakouts, support/resistance, mean reversion)
    - Sophisticated market analysis and decision making
    """
    
    def __init__(self, use_database=True, market_tier=2, global_trading=False):
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
        
        # Phase 3 specific settings
        self.intelligence_enabled = True
        self.min_technical_confidence = 0.6  # Minimum confidence from technical analysis
        self.regime_weight = 0.4  # Weight of regime analysis in final decision
        self.technical_weight = 0.4  # Weight of technical indicators
        self.pattern_weight = 0.2  # Weight of pattern recognition
        
        print("🧠 Phase 3 Intelligence Layer Initialized")
        print(f"   📊 Technical Indicators: {'✅ Enabled' if self.intelligence_enabled else '❌ Disabled'}")
        print(f"   🎯 Market Regime Detection: Enhanced")
        print(f"   🔍 Pattern Recognition: Active")
    
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
        
        # CRITICAL FIX: Match symbols to open markets only
        selected_symbols = []
        
        if us_market_open:
            # Trade US symbols during US hours
            from market_universe import get_symbols_by_tier
            us_symbols = get_symbols_by_tier(3)  # US stocks + ETFs
            selected_symbols.extend(us_symbols)
            print(f"🇺🇸 Trading US symbols: {len(us_symbols)} symbols")
            
        elif asian_market_open:
            # Trade Asian ADRs during Asian hours (these execute immediately)
            from market_universe import get_asian_symbols_by_region
            asian_adrs = get_asian_symbols_by_region()
            asian_symbols = []
            for region_symbols in asian_adrs.values():
                asian_symbols.extend(region_symbols)
            selected_symbols.extend(asian_symbols)
            print(f"🇯🇵 Trading Asian ADRs: {len(asian_symbols)} symbols")
            
        elif european_market_open:
            # Trade European ADRs during European hours (corrected tickers)
            european_symbols = ['ASML', 'SAP', 'NVO', 'UL', 'BP', 'RDS.A', 'SPOT', 'DEO']
            selected_symbols.extend(european_symbols)
            print(f"🇪🇺 Trading European ADRs: {len(european_symbols)} symbols")
            
        else:
            # No major markets open - minimal core symbols only
            selected_symbols = ['SPY', 'QQQ', 'VEA']  # Core ETFs only
            print(f"🌙 All markets closed, core ETFs only: {len(selected_symbols)} symbols")
        
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
            # CRITICAL: Cancel all pending orders to prevent market mismatch and duplicates
            print("🧹 EMERGENCY: Cleaning up all pending orders...")
            cancelled_count = self.order_manager.cancel_all_pending_orders()
            if cancelled_count > 0:
                print(f"🧹 EMERGENCY CLEANUP: Cancelled {cancelled_count} pending orders from wrong market/duplicates")
            else:
                print("🧹 No pending orders to cancel - account clean")
            
            # Get market data
            print("📈 Collecting market data...")
            quotes = self.get_market_quotes()
            
            if not quotes:
                print("❌ No market data available")
                return
            
            print(f"✅ Retrieved {len(quotes)} quotes")
            
            # Enhanced regime detection using intelligence
            print("🧠 Analyzing market intelligence...")
            
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