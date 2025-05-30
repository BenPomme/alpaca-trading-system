#!/usr/bin/env python3

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import random

class IntelligentExitManager:
    """
    Advanced exit management system that leverages:
    - Market regime detection
    - Technical indicators
    - ML confidence scoring
    - Pattern recognition
    - Partial profit taking
    - Smart trailing stops
    """
    
    def __init__(self, api, risk_manager, technical_indicators, regime_detector, pattern_recognition, ml_models=None):
        self.api = api
        self.risk_manager = risk_manager
        self.technical_indicators = technical_indicators
        self.regime_detector = regime_detector
        self.pattern_recognition = pattern_recognition
        self.ml_models = ml_models
        
        # Base exit parameters - MUCH MORE CONSERVATIVE after 13.2% win rate analysis
        self.base_stop_loss = 0.08  # 8% stop loss (was 5% - too tight!)
        self.base_take_profit = 0.15  # 15% take profit (was 12% - let winners run)
        self.base_quick_profit = 0.06  # 6% quick profit (was 4% - give trades time)
        
        # CRITICAL: Minimum hold time before intelligence exits (prevent immediate closures)
        self.min_hold_hours = 2  # Don't exit based on intelligence for first 2 hours
        
        # Intelligent exit parameters
        self.regime_multipliers = {
            'bullish': {'profit': 1.5, 'stop': 1.2, 'patience': 1.4},    # Let winners run in bull markets
            'bearish': {'profit': 0.6, 'stop': 0.8, 'patience': 0.7},   # Take profits fast in bear markets
            'neutral': {'profit': 1.0, 'stop': 1.0, 'patience': 1.0}    # Standard approach
        }
        
        # Technical indicator exit levels
        self.technical_exits = {
            'rsi_overbought': 75,      # Exit on extreme overbought
            'rsi_oversold': 25,        # Stop loss tightening
            'macd_divergence': True,   # Exit on MACD bearish divergence
            'bollinger_upper': True    # Exit near upper Bollinger Band
        }
        
        # ML confidence thresholds - MUCH MORE CONSERVATIVE
        self.ml_confidence_exits = {
            'high_confidence_hold': 0.80,    # Hold longer for high-confidence trades
            'low_confidence_exit': 0.25,     # Only exit on VERY low confidence (was 0.40)
            'reversal_signal': 0.85          # Only exit on VERY strong reversal (was 0.70)
        }
        
        # Partial exit strategy - More aggressive thresholds
        self.partial_exit_levels = [
            {'profit_pct': 0.06, 'exit_portion': 0.20},  # 20% at +6% (was 25% at +4%)
            {'profit_pct': 0.10, 'exit_portion': 0.30},  # 30% at +10% (was 35% at +6%)
            {'profit_pct': 0.15, 'exit_portion': 0.40}   # 40% at +15% (was 40% at +10%)
        ]
        
        print("🧠 Intelligent Exit Manager Initialized")
        print(f"   🎯 Regime-based exits: {len(self.regime_multipliers)} market conditions")
        print(f"   📊 Technical exits: {len(self.technical_exits)} indicators")
        print(f"   🤖 ML integration: {'✅ Enabled' if ml_models else '❌ Disabled'}")
        print(f"   📈 Partial exits: {len(self.partial_exit_levels)} levels")
    
    def analyze_exit_opportunity(self, symbol: str, position_info: Dict, market_data: Dict) -> Dict:
        """
        Comprehensive exit analysis combining all intelligence sources
        """
        try:
            entry_price = position_info.get('avg_entry_price', 0)
            current_price = market_data.get('current_price', 0)
            entry_time = position_info.get('entry_time', datetime.now())
            
            if not entry_price or not current_price:
                return {'action': 'hold', 'reason': 'insufficient_data'}
            
            # Calculate current P&L and hold time
            pl_pct = ((current_price - entry_price) / entry_price)
            hold_days = (datetime.now() - entry_time).days if isinstance(entry_time, datetime) else 0
            hold_hours = (datetime.now() - entry_time).total_seconds() / 3600 if isinstance(entry_time, datetime) else 24
            
            analysis = {
                'symbol': symbol,
                'pl_pct': pl_pct,
                'hold_days': hold_days,
                'hold_hours': hold_hours,
                'entry_price': entry_price,
                'current_price': current_price,
                'analysis_components': {}
            }
            
            # CRITICAL FIX: Prevent premature exits (main cause of 13.2% win rate)
            if hold_hours < self.min_hold_hours and pl_pct > -self.base_stop_loss:
                return {
                    'action': 'hold',
                    'reason': f'min_hold_period_{hold_hours:.1f}h_of_{self.min_hold_hours}h',
                    'confidence': 0.0,
                    'exit_signals': [],
                    'pl_pct': pl_pct,
                    'hold_hours': hold_hours
                }
            
            # 1. Market Regime Analysis
            regime_analysis = self._analyze_regime_exit(symbol, pl_pct, market_data)
            analysis['analysis_components']['regime'] = regime_analysis
            
            # 2. Technical Indicator Analysis
            technical_analysis = self._analyze_technical_exit(symbol, current_price, pl_pct)
            analysis['analysis_components']['technical'] = technical_analysis
            
            # 3. ML Model Analysis (if available)
            ml_analysis = self._analyze_ml_exit(symbol, market_data, position_info)
            analysis['analysis_components']['ml'] = ml_analysis
            
            # 4. Pattern Recognition Analysis
            pattern_analysis = self._analyze_pattern_exit(symbol, current_price, pl_pct)
            analysis['analysis_components']['pattern'] = pattern_analysis
            
            # 5. Time-based Analysis
            time_analysis = self._analyze_time_exit(hold_days, pl_pct)
            analysis['analysis_components']['time'] = time_analysis
            
            # 6. Combine all analyses for final decision
            final_decision = self._combine_exit_analyses(analysis)
            analysis.update(final_decision)
            
            return analysis
            
        except Exception as e:
            return {
                'action': 'hold',
                'reason': f'analysis_error: {e}',
                'confidence': 0.0
            }
    
    def _analyze_regime_exit(self, symbol: str, pl_pct: float, market_data: Dict) -> Dict:
        """Analyze exit based on market regime"""
        try:
            # Get current market regime
            regime_analysis = self.regime_detector.get_comprehensive_regime_analysis()
            overall_regime = regime_analysis.get('overall_assessment', {})
            regime_type = overall_regime.get('regime', 'neutral')
            regime_confidence = overall_regime.get('confidence', 0.5)
            
            multipliers = self.regime_multipliers.get(regime_type, self.regime_multipliers['neutral'])
            
            # Adjust profit targets based on regime
            adjusted_take_profit = self.base_take_profit * multipliers['profit']
            adjusted_stop_loss = self.base_stop_loss * multipliers['stop']
            patience_factor = multipliers['patience']
            
            # Regime-based exit signals
            exit_signals = []
            
            if regime_type == 'bearish' and pl_pct >= 0.03:  # Take profits fast in bear market
                exit_signals.append(f"bear_market_profit_protection")
            
            if regime_type == 'bullish' and pl_pct >= adjusted_take_profit:  # Let winners run in bull market
                exit_signals.append(f"bull_market_extended_target")
            
            # Regime change detection
            if hasattr(self, 'last_regime') and self.last_regime != regime_type:
                if pl_pct > 0.02:  # Protect profits on regime change
                    exit_signals.append(f"regime_change_protection")
            
            return {
                'regime_type': regime_type,
                'regime_confidence': regime_confidence,
                'adjusted_take_profit': adjusted_take_profit,
                'adjusted_stop_loss': adjusted_stop_loss,
                'patience_factor': patience_factor,
                'exit_signals': exit_signals,
                'recommendation': 'sell' if exit_signals else 'hold'
            }
            
        except Exception as e:
            return {'error': f'regime_analysis_failed: {e}', 'recommendation': 'hold'}
    
    def _analyze_technical_exit(self, symbol: str, current_price: float, pl_pct: float) -> Dict:
        """Analyze exit based on technical indicators"""
        try:
            # Get technical analysis for the symbol
            tech_analysis = self.technical_indicators.get_comprehensive_analysis(symbol)
            
            exit_signals = []
            technical_score = 0
            
            # RSI-based exits
            rsi_value = tech_analysis.get('rsi', {}).get('value', 50)
            if rsi_value >= self.technical_exits['rsi_overbought'] and pl_pct > 0.02:
                exit_signals.append(f"rsi_overbought_{rsi_value:.1f}")
                technical_score += 30
            elif rsi_value <= self.technical_exits['rsi_oversold'] and pl_pct < -0.01:
                exit_signals.append(f"rsi_oversold_stop_tighten")
                technical_score += 20
            
            # MACD-based exits
            macd_analysis = tech_analysis.get('macd', {})
            if macd_analysis.get('signal') == 'sell' and pl_pct > 0.02:
                exit_signals.append("macd_bearish_divergence")
                technical_score += 25
            
            # Bollinger Bands exits
            bb_analysis = tech_analysis.get('bollinger_bands', {})
            bb_position = bb_analysis.get('position', 'middle')
            if bb_position == 'upper' and pl_pct > 0.04:
                exit_signals.append("bollinger_upper_band_resistance")
                technical_score += 20
            
            # Moving Average Analysis
            ma_analysis = tech_analysis.get('moving_averages', {})
            if ma_analysis.get('trend') == 'bearish' and pl_pct > 0.01:
                exit_signals.append("moving_average_bearish_cross")
                technical_score += 15
            
            # Volume Analysis
            volume_analysis = tech_analysis.get('volume', {})
            if volume_analysis.get('trend') == 'declining' and pl_pct > 0.03:
                exit_signals.append("volume_decline_distribution")
                technical_score += 10
            
            recommendation = 'sell' if technical_score >= 40 else 'hold'
            
            return {
                'rsi_value': rsi_value,
                'macd_signal': macd_analysis.get('signal', 'neutral'),
                'bollinger_position': bb_position,
                'technical_score': technical_score,
                'exit_signals': exit_signals,
                'recommendation': recommendation
            }
            
        except Exception as e:
            return {'error': f'technical_analysis_failed: {e}', 'recommendation': 'hold'}
    
    def _analyze_ml_exit(self, symbol: str, market_data: Dict, position_info: Dict) -> Dict:
        """Analyze exit using ML models and confidence scoring"""
        try:
            if not self.ml_models:
                return {'ml_available': False, 'recommendation': 'hold'}
            
            exit_signals = []
            ml_confidence = 0.5
            
            # Get ML predictions for current market conditions
            try:
                # REAL ML INTEGRATION: Get actual ML predictions
                # Prepare market data for ML analysis
                ml_market_data = {
                    'technical': self.technical_indicators.get_comprehensive_analysis(symbol),
                    'regime': {
                        'type': self.regime_detector.detect_trend_regime(symbol).get('regime', 'neutral'),
                        'confidence': self.regime_detector.detect_trend_regime(symbol).get('confidence', 0.5)
                    },
                    'pattern': self.pattern_recognition.get_comprehensive_pattern_analysis(symbol)
                }
                
                # Get REAL ML strategy selection and confidence
                ml_strategy, current_confidence, ml_details = self.ml_models.strategy_selector.select_optimal_strategy(ml_market_data)
                
                # Get REAL ML risk prediction for reversal probability
                risk_analysis = self.ml_models.risk_predictor.predict_position_risk(
                    symbol=symbol,
                    position_size=position_info.get('quantity', 100),
                    entry_price=position_info.get('avg_entry_price', market_data['current_price']),
                    current_price=market_data['current_price']
                )
                reversal_probability = risk_analysis.get('risk_score', 0.5)
                
                # Get REAL trend strength from ML regime detector
                try:
                    regime_analysis = self.ml_models.strategy_selector.regime_detector.analyze_market_regime(
                        [market_data['current_price']]  # Simplified price input
                    )
                    trend_strength = regime_analysis.get('confidence', 0.5)
                except:
                    trend_strength = 0.5  # Fallback
                
                print(f"   🤖 ML Predictions: strategy={ml_strategy}, confidence={current_confidence:.2f}, reversal={reversal_probability:.2f}, trend={trend_strength:.2f}")
                
                # Original entry confidence vs current confidence
                entry_confidence = position_info.get('entry_confidence', 0.5)
                confidence_decay = entry_confidence - current_confidence
                
                if confidence_decay > 0.3:  # Significant confidence loss
                    exit_signals.append(f"ml_confidence_decay_{confidence_decay:.2f}")
                
                if reversal_probability > self.ml_confidence_exits['reversal_signal']:
                    exit_signals.append(f"ml_reversal_signal_{reversal_probability:.2f}")
                
                if current_confidence < self.ml_confidence_exits['low_confidence_exit']:
                    exit_signals.append(f"ml_low_confidence_{current_confidence:.2f}")
                
                # Hold longer for high-confidence trades
                if entry_confidence > self.ml_confidence_exits['high_confidence_hold']:
                    patience_multiplier = 1.5
                else:
                    patience_multiplier = 1.0
                
                ml_confidence = current_confidence
                
            except Exception as ml_error:
                return {'error': f'ml_model_error: {ml_error}', 'recommendation': 'hold'}
            
            recommendation = 'sell' if len(exit_signals) >= 2 else 'hold'
            
            return {
                'ml_available': True,
                'current_confidence': current_confidence,
                'entry_confidence': entry_confidence,
                'confidence_decay': confidence_decay,
                'reversal_probability': reversal_probability,
                'trend_strength': trend_strength,
                'patience_multiplier': patience_multiplier,
                'exit_signals': exit_signals,
                'recommendation': recommendation
            }
            
        except Exception as e:
            return {'error': f'ml_analysis_failed: {e}', 'recommendation': 'hold'}
    
    def _analyze_pattern_exit(self, symbol: str, current_price: float, pl_pct: float) -> Dict:
        """Analyze exit based on pattern recognition"""
        try:
            # Get pattern analysis
            pattern_analysis = self.pattern_recognition.analyze_patterns(symbol)
            
            exit_signals = []
            pattern_score = 0
            
            # Resistance level exits
            resistance_levels = pattern_analysis.get('resistance_levels', [])
            for resistance in resistance_levels:
                resistance_price = resistance.get('price', 0)
                if current_price >= resistance_price * 0.98:  # Within 2% of resistance
                    exit_signals.append(f"resistance_level_{resistance_price:.2f}")
                    pattern_score += 25
            
            # Pattern completion exits
            patterns = pattern_analysis.get('patterns', [])
            for pattern in patterns:
                if pattern.get('completion_probability', 0) > 0.7:
                    pattern_type = pattern.get('type', 'unknown')
                    if pattern_type in ['double_top', 'head_shoulders', 'rising_wedge']:
                        exit_signals.append(f"bearish_pattern_{pattern_type}")
                        pattern_score += 30
            
            # Breakout failure
            if pattern_analysis.get('recent_breakout', False):
                if pl_pct < -0.02:  # Breakout failed
                    exit_signals.append("breakout_failure")
                    pattern_score += 20
            
            recommendation = 'sell' if pattern_score >= 30 else 'hold'
            
            return {
                'resistance_levels': len(resistance_levels),
                'patterns_detected': len(patterns),
                'pattern_score': pattern_score,
                'exit_signals': exit_signals,
                'recommendation': recommendation
            }
            
        except Exception as e:
            return {'error': f'pattern_analysis_failed: {e}', 'recommendation': 'hold'}
    
    def _analyze_time_exit(self, hold_days: int, pl_pct: float) -> Dict:
        """Analyze time-based exit conditions"""
        try:
            exit_signals = []
            
            # Maximum hold period (from risk manager)
            max_hold_days = getattr(self.risk_manager, 'max_hold_days', 5)
            
            if hold_days >= max_hold_days:
                exit_signals.append(f"max_hold_period_{hold_days}d")
            
            # Quick profit acceleration (higher profits faster)
            if hold_days <= 1 and pl_pct >= self.base_quick_profit * 2:  # 6% in 1 day
                exit_signals.append(f"accelerated_profit_{pl_pct:.2%}")
            
            # Stagnant position (no movement)
            if hold_days >= 3 and abs(pl_pct) < 0.01:  # Flat for 3+ days
                exit_signals.append(f"stagnant_position_{hold_days}d")
            
            # Time decay for options (if applicable)
            if hold_days >= 2 and pl_pct > 0.05:  # Options profit protection
                exit_signals.append(f"time_decay_protection")
            
            recommendation = 'sell' if exit_signals else 'hold'
            
            return {
                'hold_days': hold_days,
                'max_hold_days': max_hold_days,
                'exit_signals': exit_signals,
                'recommendation': recommendation
            }
            
        except Exception as e:
            return {'error': f'time_analysis_failed: {e}', 'recommendation': 'hold'}
    
    def _combine_exit_analyses(self, analysis: Dict) -> Dict:
        """Combine all exit analyses for final intelligent decision"""
        try:
            components = analysis['analysis_components']
            pl_pct = analysis['pl_pct']
            
            # Collect all recommendations
            recommendations = []
            exit_signals = []
            confidence_scores = []
            
            for component_name, component_analysis in components.items():
                if isinstance(component_analysis, dict):
                    rec = component_analysis.get('recommendation', 'hold')
                    recommendations.append(rec)
                    
                    signals = component_analysis.get('exit_signals', [])
                    exit_signals.extend([f"{component_name}:{signal}" for signal in signals])
                    
                    # Calculate component confidence
                    if 'confidence' in component_analysis:
                        confidence_scores.append(component_analysis['confidence'])
                    elif rec == 'sell':
                        confidence_scores.append(0.7)
                    else:
                        confidence_scores.append(0.3)
            
            # Vote-based decision
            sell_votes = recommendations.count('sell')
            total_votes = len(recommendations)
            sell_confidence = sell_votes / total_votes if total_votes > 0 else 0
            
            # Override conditions
            final_action = 'hold'
            final_reason = 'insufficient_signals'
            exit_portion = 1.0  # Full exit by default
            
            # Emergency exits (always trigger)
            if pl_pct <= -self.base_stop_loss:  # Stop loss
                final_action = 'sell'
                final_reason = 'stop_loss_triggered'
                exit_portion = 1.0
            
            elif pl_pct >= self.base_take_profit * 2:  # Major profit (16%+)
                final_action = 'sell'
                final_reason = 'major_profit_protection'
                exit_portion = 0.7  # Partial exit
            
            # MUCH MORE CONSERVATIVE: Require profit OR very strong signals
            elif sell_confidence >= 0.8 and pl_pct > 0.02:  # 80%+ confidence AND +2% profit
                # Check for partial exit opportunities
                for level in self.partial_exit_levels:
                    if pl_pct >= level['profit_pct']:
                        final_action = 'sell'
                        final_reason = f"profitable_intelligent_exit_{len(exit_signals)}_signals"
                        exit_portion = level['exit_portion']
                        break
                
                if final_action == 'hold':  # No partial level matched but profitable
                    final_action = 'sell'
                    final_reason = f"profitable_high_confidence_exit_{sell_confidence:.1%}"
                    exit_portion = 0.5  # Only partial exit on intelligence
            
            elif len(exit_signals) >= 5 and pl_pct > -0.02:  # Need 5+ signals AND not losing much
                final_action = 'sell'
                final_reason = f"multiple_signals_{len(exit_signals)}"
                exit_portion = 0.3  # Very conservative partial exit
            
            # Calculate final confidence
            final_confidence = (
                sell_confidence * 0.4 +  # Vote weight
                (len(exit_signals) / 10) * 0.3 +  # Signal count weight
                (sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5) * 0.3
            )
            final_confidence = min(final_confidence, 1.0)
            
            return {
                'action': final_action,
                'reason': final_reason,
                'confidence': final_confidence,
                'exit_portion': exit_portion,
                'sell_votes': sell_votes,
                'total_votes': total_votes,
                'exit_signals': exit_signals,
                'analysis_summary': f"{sell_votes}/{total_votes} components recommend exit"
            }
            
        except Exception as e:
            return {
                'action': 'hold',
                'reason': f'analysis_combination_error: {e}',
                'confidence': 0.0,
                'exit_portion': 1.0
            }
    
    def execute_intelligent_exit(self, symbol: str, exit_analysis: Dict, order_manager) -> Dict:
        """Execute the intelligent exit decision with market hours awareness"""
        try:
            if exit_analysis.get('action') != 'sell':
                return {'status': 'no_action', 'reason': exit_analysis.get('reason', 'hold_decision')}
            
            # CRITICAL FIX: Check if US market is open before placing orders
            try:
                us_market_open = self.api.get_clock().is_open
                if not us_market_open:
                    # Check if this is crypto (can trade 24/7)
                    is_crypto = symbol.endswith('USD') and symbol.startswith(('BTC', 'ETH', 'ADA', 'SOL', 'MANA', 'SAND', 'AAVE', 'UNI', 'COMP', 'DOT', 'LINK', 'MATIC', 'AVAX'))
                    if not is_crypto:
                        print(f"   💤 SKIPPING EXIT ORDER: {symbol} - US market closed, order would queue until 10:00 PM")
                        print(f"   🎯 Exit recommendation recorded but no order placed during market closure")
                        return {
                            'status': 'market_closed', 
                            'reason': f'exit_deferred_market_closed_{exit_analysis.get("reason", "intelligent_exit")}',
                            'exit_portion': exit_analysis.get('exit_portion', 1.0),
                            'deferred_until_market_open': True
                        }
            except Exception as market_check_error:
                print(f"   ⚠️ Market hours check failed: {market_check_error}")
                # Continue with order placement if check fails
            
            exit_portion = exit_analysis.get('exit_portion', 1.0)
            reason = exit_analysis.get('reason', 'intelligent_exit')
            
            # Get current position
            positions = self.api.list_positions()
            position = None
            for pos in positions:
                if pos.symbol == symbol:
                    position = pos
                    break
            
            if not position:
                return {'status': 'error', 'reason': 'position_not_found'}
            
            current_qty = int(float(position.qty))
            exit_qty = max(1, int(current_qty * exit_portion))
            
            print(f"🧠 INTELLIGENT EXIT: {symbol}")
            print(f"   📊 Reason: {reason}")
            print(f"   💰 Exit Portion: {exit_portion:.0%} ({exit_qty}/{current_qty} shares)")
            print(f"   🎯 Confidence: {exit_analysis.get('confidence', 0):.1%}")
            print(f"   📈 Signals: {len(exit_analysis.get('exit_signals', []))}")
            
            # Execute the exit order
            if exit_portion >= 1.0:
                # Full exit
                result = order_manager.execute_sell_order(symbol, reason)
            else:
                # Partial exit - would need to implement partial sell in order_manager
                result = order_manager.execute_sell_order(symbol, f"partial_{reason}")
            
            if result.get('success', False):
                return {
                    'status': 'success',
                    'symbol': symbol,
                    'exit_qty': exit_qty,
                    'exit_portion': exit_portion,
                    'reason': reason,
                    'pl_pct': result.get('pl_pct', 0),
                    'analysis': exit_analysis
                }
            else:
                return {
                    'status': 'failed',
                    'reason': result.get('reason', 'execution_failed'),
                    'analysis': exit_analysis
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'reason': f'exit_execution_error: {e}',
                'analysis': exit_analysis
            }
    
    def get_exit_summary(self) -> Dict:
        """Get summary of intelligent exit capabilities"""
        return {
            'exit_manager': 'IntelligentExitManager',
            'capabilities': {
                'regime_based_exits': True,
                'technical_indicator_exits': True,
                'ml_confidence_exits': bool(self.ml_models),
                'pattern_recognition_exits': True,
                'partial_profit_taking': True,
                'time_based_exits': True
            },
            'exit_levels': self.partial_exit_levels,
            'regime_multipliers': self.regime_multipliers,
            'technical_thresholds': self.technical_exits
        }
    
    def record_exit_outcome(self, symbol: str, exit_reason: str, entry_info: Dict, exit_info: Dict):
        """
        Record exit outcome for ML learning and iterative improvement
        """
        try:
            if not self.ml_models:
                return
            
            # Prepare outcome data for ML learning
            outcome_data = {
                'symbol': symbol,
                'exit_reason': exit_reason,
                'entry_time': entry_info.get('entry_time', datetime.now()),
                'exit_time': datetime.now(),
                'entry_price': entry_info.get('avg_entry_price', 0),
                'exit_price': exit_info.get('exit_price', 0),
                'quantity': entry_info.get('quantity', 0),
                'profit_loss': exit_info.get('profit_loss', 0),
                'profit_pct': exit_info.get('profit_pct', 0),
                'hold_duration': (datetime.now() - entry_info.get('entry_time', datetime.now())).total_seconds() / 86400,  # days
                'entry_confidence': entry_info.get('entry_confidence', 0.5),
                'exit_confidence': exit_info.get('exit_confidence', 0.5)
            }
            
            # Record with ML framework for learning
            if hasattr(self.ml_models, 'strategy_selector'):
                self.ml_models.strategy_selector.update_strategy_performance(exit_reason, outcome_data)
                print(f"   🧠 ML Learning: Recorded exit outcome for {symbol} ({exit_reason})")
            
            # Update exit strategy performance
            self._update_exit_strategy_performance(exit_reason, outcome_data)
            
        except Exception as e:
            print(f"   ⚠️ Failed to record exit outcome: {e}")
    
    def _update_exit_strategy_performance(self, exit_reason: str, outcome_data: Dict):
        """
        Update performance tracking for different exit strategies
        """
        try:
            profit_pct = outcome_data.get('profit_pct', 0)
            
            # Initialize performance tracking if not exists
            if not hasattr(self, 'exit_performance'):
                self.exit_performance = {}
            
            if exit_reason not in self.exit_performance:
                self.exit_performance[exit_reason] = {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'total_profit': 0.0,
                    'avg_profit': 0.0,
                    'win_rate': 0.0
                }
            
            # Update performance metrics
            perf = self.exit_performance[exit_reason]
            perf['total_trades'] += 1
            perf['total_profit'] += profit_pct
            
            if profit_pct > 0:
                perf['winning_trades'] += 1
            
            perf['avg_profit'] = perf['total_profit'] / perf['total_trades']
            perf['win_rate'] = perf['winning_trades'] / perf['total_trades']
            
            print(f"   📊 Exit Strategy '{exit_reason}': {perf['win_rate']:.1%} win rate, {perf['avg_profit']:+.1f}% avg")
            
        except Exception as e:
            print(f"   ⚠️ Failed to update exit performance: {e}")
    
    def get_exit_strategy_recommendations(self) -> Dict:
        """
        Get recommendations for exit strategy improvements based on performance
        """
        try:
            if not hasattr(self, 'exit_performance'):
                return {'recommendations': ['Collect more exit data for analysis']}
            
            recommendations = []
            
            # Analyze performance by exit strategy
            for strategy, perf in self.exit_performance.items():
                if perf['total_trades'] >= 5:  # Minimum sample size
                    if perf['win_rate'] > 0.7:
                        recommendations.append(f"✅ '{strategy}' performing well ({perf['win_rate']:.1%} win rate)")
                    elif perf['win_rate'] < 0.4:
                        recommendations.append(f"⚠️ '{strategy}' underperforming ({perf['win_rate']:.1%} win rate) - consider adjusting")
                    
                    if perf['avg_profit'] < -2.0:
                        recommendations.append(f"📉 '{strategy}' avg loss {perf['avg_profit']:.1f}% - tighten stops")
            
            return {
                'performance_summary': self.exit_performance,
                'recommendations': recommendations,
                'total_strategies_tracked': len(self.exit_performance)
            }
            
        except Exception as e:
            return {'error': f'Failed to generate recommendations: {e}'}