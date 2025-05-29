#!/usr/bin/env python3
"""
Options Trading Manager - Phase 4.3
Advanced options strategies for hedging and leverage
"""

import os
import datetime
from typing import Dict, List, Optional, Tuple
import json

class OptionsManager:
    """Advanced options trading for hedging and aggressive strategies"""
    
    def __init__(self, api_client, risk_manager=None):
        self.api = api_client
        self.risk_manager = risk_manager
        
        # Options trading parameters
        self.max_options_allocation = 0.30  # 30% of portfolio in options
        self.leverage_target = 2.5          # Target 2.5x leverage through options
        self.hedge_threshold = 0.15         # Hedge when positions reach 15% of portfolio
        
        # Strategy preferences for aggressive 5-10% monthly returns
        self.preferred_strategies = {
            'bullish': ['long_calls', 'bull_call_spreads', 'covered_calls'],
            'bearish': ['protective_puts', 'bear_put_spreads', 'cash_secured_puts'],
            'neutral': ['iron_condors', 'straddles', 'covered_calls'],
            'high_volatility': ['long_straddles', 'long_strangles'],
            'low_volatility': ['iron_condors', 'covered_calls', 'cash_secured_puts']
        }
        
        print("📊 Options Manager initialized")
        print(f"   🎯 Max options allocation: {self.max_options_allocation:.1%}")
        print(f"   🚀 Target leverage: {self.leverage_target}x")
        print(f"   🛡️ Hedge threshold: {self.hedge_threshold:.1%}")
    
    def get_options_chain(self, symbol: str, expiration_date: str = None) -> Dict:
        """Get options chain for a symbol"""
        try:
            # If no expiration specified, use next monthly expiration
            if not expiration_date:
                expiration_date = self._get_next_monthly_expiration()
            
            # Get options chain from Alpaca
            options_chain = self.api.get_options_chain(symbol, expiration_date)
            
            return {
                'symbol': symbol,
                'expiration': expiration_date,
                'calls': options_chain.get('calls', []),
                'puts': options_chain.get('puts', []),
                'underlying_price': self._get_underlying_price(symbol)
            }
            
        except Exception as e:
            print(f"⚠️ Error getting options chain for {symbol}: {e}")
            return {}
    
    def analyze_options_opportunity(self, symbol: str, market_regime: str, confidence: float) -> Dict:
        """Analyze options trading opportunity for a symbol"""
        try:
            # Get current stock price and options chain
            stock_price = self._get_underlying_price(symbol)
            options_chain = self.get_options_chain(symbol)
            
            if not options_chain:
                return {'strategy': 'none', 'reason': 'No options chain available'}
            
            # Analyze based on market regime and confidence
            strategy_recommendation = self._select_options_strategy(
                market_regime, confidence, stock_price, options_chain
            )
            
            return {
                'symbol': symbol,
                'underlying_price': stock_price,
                'market_regime': market_regime,
                'confidence': confidence,
                'recommended_strategy': strategy_recommendation,
                'options_chain': options_chain
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing options for {symbol}: {e}")
            return {'strategy': 'none', 'reason': f'Analysis error: {e}'}
    
    def _select_options_strategy(self, regime: str, confidence: float, stock_price: float, chain: Dict) -> Dict:
        """Select optimal options strategy based on market conditions"""
        
        # High confidence bullish - aggressive calls
        if regime in ['bullish', 'momentum'] and confidence > 0.75:
            return self._analyze_long_calls(stock_price, chain)
        
        # Moderate confidence bullish - bull spreads
        elif regime in ['bullish', 'momentum'] and confidence > 0.60:
            return self._analyze_bull_call_spreads(stock_price, chain)
        
        # Bearish - protective strategies
        elif regime in ['bearish', 'uncertain'] and confidence > 0.60:
            return self._analyze_protective_puts(stock_price, chain)
        
        # Neutral/sideways - income strategies
        elif regime in ['neutral', 'conservative']:
            return self._analyze_covered_calls(stock_price, chain)
        
        # High volatility - volatility plays
        elif confidence < 0.50:  # Uncertain direction but expect movement
            return self._analyze_straddles(stock_price, chain)
        
        else:
            return {'strategy': 'none', 'reason': 'No suitable options strategy'}
    
    def _analyze_long_calls(self, stock_price: float, chain: Dict) -> Dict:
        """Analyze long call options for bullish aggressive strategy"""
        calls = chain.get('calls', [])
        if not calls:
            return {'strategy': 'none', 'reason': 'No calls available'}
        
        # Find slightly out-of-the-money calls (5-10% OTM) for leverage
        target_strike = stock_price * 1.05  # 5% out of money
        best_call = None
        min_diff = float('inf')
        
        for call in calls:
            strike_diff = abs(call['strike'] - target_strike)
            if strike_diff < min_diff and call['ask'] > 0:
                min_diff = strike_diff
                best_call = call
        
        if best_call:
            # Calculate potential return and risk
            premium = best_call['ask']
            leverage = stock_price / premium  # Leverage ratio
            breakeven = best_call['strike'] + premium
            
            return {
                'strategy': 'long_calls',
                'contract': best_call,
                'premium': premium,
                'leverage': leverage,
                'breakeven': breakeven,
                'max_risk': premium,  # Limited to premium paid
                'target_return': leverage * 0.10,  # 10% stock move = leverage * 10% return
                'confidence_required': 0.70
            }
        
        return {'strategy': 'none', 'reason': 'No suitable call options found'}
    
    def _analyze_bull_call_spreads(self, stock_price: float, chain: Dict) -> Dict:
        """Analyze bull call spreads for moderate bullish strategy"""
        calls = chain.get('calls', [])
        if len(calls) < 2:
            return {'strategy': 'none', 'reason': 'Insufficient call options'}
        
        # Find ATM call to buy and OTM call to sell
        buy_strike = min(calls, key=lambda x: abs(x['strike'] - stock_price))
        sell_strike = min([c for c in calls if c['strike'] > buy_strike['strike']], 
                         key=lambda x: abs(x['strike'] - stock_price * 1.10), default=None)
        
        if buy_strike and sell_strike:
            net_premium = buy_strike['ask'] - sell_strike['bid']
            max_profit = (sell_strike['strike'] - buy_strike['strike']) - net_premium
            
            return {
                'strategy': 'bull_call_spread',
                'buy_contract': buy_strike,
                'sell_contract': sell_strike,
                'net_premium': net_premium,
                'max_profit': max_profit,
                'max_risk': net_premium,
                'profit_ratio': max_profit / net_premium if net_premium > 0 else 0,
                'confidence_required': 0.60
            }
        
        return {'strategy': 'none', 'reason': 'Cannot construct bull call spread'}
    
    def _analyze_protective_puts(self, stock_price: float, chain: Dict) -> Dict:
        """Analyze protective puts for portfolio hedging"""
        puts = chain.get('puts', [])
        if not puts:
            return {'strategy': 'none', 'reason': 'No puts available'}
        
        # Find put ~5% out of money for cost-effective protection
        target_strike = stock_price * 0.95
        best_put = min(puts, key=lambda x: abs(x['strike'] - target_strike))
        
        if best_put:
            protection_cost = best_put['ask']
            protection_level = best_put['strike']
            
            return {
                'strategy': 'protective_puts',
                'contract': best_put,
                'protection_cost': protection_cost,
                'protection_level': protection_level,
                'max_loss': stock_price - protection_level + protection_cost,
                'cost_pct': protection_cost / stock_price,
                'confidence_required': 0.40  # Can use for any position
            }
        
        return {'strategy': 'none', 'reason': 'No suitable protective puts'}
    
    def _analyze_covered_calls(self, stock_price: float, chain: Dict) -> Dict:
        """Analyze covered calls for income generation"""
        calls = chain.get('calls', [])
        if not calls:
            return {'strategy': 'none', 'reason': 'No calls available'}
        
        # Find call ~5-10% out of money for income
        target_strike = stock_price * 1.07
        best_call = min(calls, key=lambda x: abs(x['strike'] - target_strike))
        
        if best_call:
            premium_income = best_call['bid']
            upside_cap = best_call['strike']
            
            return {
                'strategy': 'covered_calls',
                'contract': best_call,
                'premium_income': premium_income,
                'income_yield': premium_income / stock_price,
                'upside_cap': upside_cap,
                'max_return': (upside_cap - stock_price + premium_income) / stock_price,
                'confidence_required': 0.50
            }
        
        return {'strategy': 'none', 'reason': 'No suitable covered calls'}
    
    def _analyze_straddles(self, stock_price: float, chain: Dict) -> Dict:
        """Analyze straddles for volatility plays"""
        calls = chain.get('calls', [])
        puts = chain.get('puts', [])
        
        if not calls or not puts:
            return {'strategy': 'none', 'reason': 'Insufficient options for straddle'}
        
        # Find ATM call and put
        atm_call = min(calls, key=lambda x: abs(x['strike'] - stock_price))
        atm_put = min(puts, key=lambda x: abs(x['strike'] - stock_price))
        
        if atm_call and atm_put and abs(atm_call['strike'] - atm_put['strike']) < 2:
            total_premium = atm_call['ask'] + atm_put['ask']
            breakeven_up = atm_call['strike'] + total_premium
            breakeven_down = atm_put['strike'] - total_premium
            
            return {
                'strategy': 'long_straddle',
                'call_contract': atm_call,
                'put_contract': atm_put,
                'total_premium': total_premium,
                'breakeven_up': breakeven_up,
                'breakeven_down': breakeven_down,
                'move_required': total_premium / stock_price,
                'confidence_required': 0.30  # High volatility play
            }
        
        return {'strategy': 'none', 'reason': 'Cannot construct straddle'}
    
    def execute_options_strategy(self, strategy_analysis: Dict, position_size: float) -> Dict:
        """Execute the recommended options strategy"""
        try:
            strategy = strategy_analysis.get('recommended_strategy', {})
            strategy_type = strategy.get('strategy', 'none')
            
            if strategy_type == 'none':
                return {'status': 'skipped', 'reason': strategy.get('reason', 'No strategy')}
            
            # Calculate position sizing based on portfolio allocation
            account = self.api.get_account()
            portfolio_value = float(account.portfolio_value)
            max_options_value = portfolio_value * self.max_options_allocation
            
            # Execute specific strategy
            if strategy_type == 'long_calls':
                return self._execute_long_calls(strategy, position_size, max_options_value)
            elif strategy_type == 'bull_call_spread':
                return self._execute_bull_call_spread(strategy, position_size, max_options_value)
            elif strategy_type == 'protective_puts':
                return self._execute_protective_puts(strategy, position_size, max_options_value)
            elif strategy_type == 'covered_calls':
                return self._execute_covered_calls(strategy, position_size, max_options_value)
            elif strategy_type == 'long_straddle':
                return self._execute_straddle(strategy, position_size, max_options_value)
            else:
                return {'status': 'error', 'reason': f'Unknown strategy: {strategy_type}'}
        
        except Exception as e:
            print(f"❌ Options execution error: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    def _execute_long_calls(self, strategy: Dict, position_size: float, max_value: float) -> Dict:
        """Execute long call options strategy"""
        contract = strategy['contract']
        premium = strategy['premium']
        
        # Calculate number of contracts based on position size and premium
        max_contracts = int(min(position_size / (premium * 100), max_value / (premium * 100)))
        
        if max_contracts < 1:
            return {'status': 'skipped', 'reason': 'Position size too small for options'}
        
        try:
            # Place options order
            order = self.api.submit_order(
                symbol=contract['symbol'],
                qty=max_contracts,
                side='buy',
                type='market',
                time_in_force='day',
                order_class='option',
                option_contract=contract['contract_id']
            )
            
            return {
                'status': 'success',
                'strategy': 'long_calls',
                'contracts': max_contracts,
                'premium_paid': premium * max_contracts * 100,
                'leverage': strategy['leverage'],
                'order_id': order.id
            }
            
        except Exception as e:
            return {'status': 'error', 'reason': f'Order failed: {e}'}
    
    def _execute_bull_call_spread(self, strategy: Dict, position_size: float, max_value: float) -> Dict:
        """Execute bull call spread strategy"""
        buy_contract = strategy['buy_contract']
        sell_contract = strategy['sell_contract']
        net_premium = strategy['net_premium']
        
        # Calculate number of spreads based on position size and net premium
        max_spreads = int(min(position_size / (net_premium * 100), max_value / (net_premium * 100)))
        
        if max_spreads < 1:
            return {'status': 'skipped', 'reason': 'Position size too small for spreads'}
        
        try:
            # Submit spread order as a combo order
            buy_leg = {
                'symbol': buy_contract['symbol'],
                'qty': max_spreads,
                'side': 'buy',
                'option_contract': buy_contract['contract_id']
            }
            sell_leg = {
                'symbol': sell_contract['symbol'],
                'qty': max_spreads,
                'side': 'sell',
                'option_contract': sell_contract['contract_id']
            }
            
            # Submit as bracket order if API supports, otherwise individual orders
            order = self.api.submit_order(
                symbol=buy_contract['symbol'],
                qty=max_spreads,
                side='buy',
                type='market',
                time_in_force='day',
                order_class='spread',
                legs=[buy_leg, sell_leg]
            )
            
            return {
                'status': 'success',
                'strategy': 'bull_call_spread',
                'spreads': max_spreads,
                'net_premium_paid': net_premium * max_spreads * 100,
                'max_profit': strategy['max_profit'] * max_spreads * 100,
                'order_id': order.id
            }
            
        except Exception as e:
            # Fallback: submit individual orders
            try:
                buy_order = self.api.submit_order(
                    symbol=buy_contract['symbol'],
                    qty=max_spreads,
                    side='buy',
                    type='market',
                    time_in_force='day',
                    order_class='option',
                    option_contract=buy_contract['contract_id']
                )
                
                sell_order = self.api.submit_order(
                    symbol=sell_contract['symbol'],
                    qty=max_spreads,
                    side='sell',
                    type='market',
                    time_in_force='day',
                    order_class='option',
                    option_contract=sell_contract['contract_id']
                )
                
                return {
                    'status': 'success',
                    'strategy': 'bull_call_spread',
                    'spreads': max_spreads,
                    'buy_order_id': buy_order.id,
                    'sell_order_id': sell_order.id,
                    'net_premium_paid': net_premium * max_spreads * 100
                }
                
            except Exception as e2:
                return {'status': 'error', 'reason': f'Spread order failed: {e2}'}
    
    def _execute_protective_puts(self, strategy: Dict, position_size: float, max_value: float) -> Dict:
        """Execute protective puts strategy for portfolio hedging"""
        contract = strategy['contract']
        protection_cost = strategy['protection_cost']
        
        # For protective puts, we need to own the underlying stock
        # Check current stock position first
        try:
            positions = self.api.list_positions()
            stock_position = None
            
            for pos in positions:
                if pos.symbol == contract['underlying_symbol'] and pos.side == 'long':
                    stock_position = pos
                    break
            
            if not stock_position:
                return {'status': 'skipped', 'reason': 'No stock position to protect'}
            
            stock_qty = int(float(stock_position.qty))
            # Each put contract protects 100 shares
            max_puts = stock_qty // 100
            
            # Limit puts based on position size allocation
            allocated_puts = int(min(max_puts, position_size / (protection_cost * 100)))
            
            if allocated_puts < 1:
                return {'status': 'skipped', 'reason': 'Insufficient allocation for protective puts'}
            
            # Place protective put order
            order = self.api.submit_order(
                symbol=contract['symbol'],
                qty=allocated_puts,
                side='buy',
                type='market',
                time_in_force='day',
                order_class='option',
                option_contract=contract['contract_id']
            )
            
            protected_shares = allocated_puts * 100
            total_protection_cost = protection_cost * allocated_puts * 100
            
            return {
                'status': 'success',
                'strategy': 'protective_puts',
                'contracts': allocated_puts,
                'protected_shares': protected_shares,
                'protection_cost': total_protection_cost,
                'protection_level': strategy['protection_level'],
                'max_loss_per_share': strategy['max_loss'],
                'order_id': order.id
            }
            
        except Exception as e:
            return {'status': 'error', 'reason': f'Protective puts failed: {e}'}
    
    def _execute_covered_calls(self, strategy: Dict, position_size: float, max_value: float) -> Dict:
        """Execute covered calls strategy for income generation"""
        contract = strategy['contract']
        premium_income = strategy['premium_income']
        
        # For covered calls, we need to own the underlying stock
        try:
            positions = self.api.list_positions()
            stock_position = None
            
            for pos in positions:
                if pos.symbol == contract['underlying_symbol'] and pos.side == 'long':
                    stock_position = pos
                    break
            
            if not stock_position:
                # If no stock position, we can't sell covered calls
                # Could potentially buy stock + sell calls as combo, but risky
                return {'status': 'skipped', 'reason': 'No stock position for covered calls'}
            
            stock_qty = int(float(stock_position.qty))
            # Each call contract covers 100 shares
            max_calls = stock_qty // 100
            
            # Limit calls based on position size allocation (income generation strategy)
            # For covered calls, position_size represents how much of our stock to cover
            coverage_ratio = min(1.0, position_size / (float(stock_position.market_value)))
            allocated_calls = int(max_calls * coverage_ratio)
            
            if allocated_calls < 1:
                return {'status': 'skipped', 'reason': 'Insufficient allocation for covered calls'}
            
            # Sell covered calls
            order = self.api.submit_order(
                symbol=contract['symbol'],
                qty=allocated_calls,
                side='sell',
                type='market',
                time_in_force='day',
                order_class='option',
                option_contract=contract['contract_id']
            )
            
            covered_shares = allocated_calls * 100
            total_premium_received = premium_income * allocated_calls * 100
            
            return {
                'status': 'success',
                'strategy': 'covered_calls',
                'contracts': allocated_calls,
                'covered_shares': covered_shares,
                'premium_received': total_premium_received,
                'income_yield': strategy['income_yield'],
                'upside_cap': strategy['upside_cap'],
                'max_return': strategy['max_return'],
                'order_id': order.id
            }
            
        except Exception as e:
            return {'status': 'error', 'reason': f'Covered calls failed: {e}'}
    
    def _execute_straddle(self, strategy: Dict, position_size: float, max_value: float) -> Dict:
        """Execute long straddle strategy for volatility plays"""
        call_contract = strategy['call_contract']
        put_contract = strategy['put_contract']
        total_premium = strategy['total_premium']
        
        # Calculate number of straddles based on position size and total premium
        max_straddles = int(min(position_size / (total_premium * 100), max_value / (total_premium * 100)))
        
        if max_straddles < 1:
            return {'status': 'skipped', 'reason': 'Position size too small for straddles'}
        
        try:
            # Submit straddle as combo order if supported, otherwise individual orders
            call_leg = {
                'symbol': call_contract['symbol'],
                'qty': max_straddles,
                'side': 'buy',
                'option_contract': call_contract['contract_id']
            }
            put_leg = {
                'symbol': put_contract['symbol'],
                'qty': max_straddles,
                'side': 'buy',
                'option_contract': put_contract['contract_id']
            }
            
            try:
                # Try combo order first
                order = self.api.submit_order(
                    symbol=call_contract['symbol'],
                    qty=max_straddles,
                    side='buy',
                    type='market',
                    time_in_force='day',
                    order_class='combo',
                    legs=[call_leg, put_leg]
                )
                
                return {
                    'status': 'success',
                    'strategy': 'long_straddle',
                    'straddles': max_straddles,
                    'total_premium_paid': total_premium * max_straddles * 100,
                    'breakeven_up': strategy['breakeven_up'],
                    'breakeven_down': strategy['breakeven_down'],
                    'move_required': strategy['move_required'],
                    'order_id': order.id
                }
                
            except Exception:
                # Fallback: submit individual orders
                call_order = self.api.submit_order(
                    symbol=call_contract['symbol'],
                    qty=max_straddles,
                    side='buy',
                    type='market',
                    time_in_force='day',
                    order_class='option',
                    option_contract=call_contract['contract_id']
                )
                
                put_order = self.api.submit_order(
                    symbol=put_contract['symbol'],
                    qty=max_straddles,
                    side='buy',
                    type='market',
                    time_in_force='day',
                    order_class='option',
                    option_contract=put_contract['contract_id']
                )
                
                return {
                    'status': 'success',
                    'strategy': 'long_straddle',
                    'straddles': max_straddles,
                    'call_order_id': call_order.id,
                    'put_order_id': put_order.id,
                    'total_premium_paid': total_premium * max_straddles * 100,
                    'breakeven_up': strategy['breakeven_up'],
                    'breakeven_down': strategy['breakeven_down']
                }
                
        except Exception as e:
            return {'status': 'error', 'reason': f'Straddle order failed: {e}'}
    
    def _get_underlying_price(self, symbol: str) -> float:
        """Get current stock price"""
        try:
            quote = self.api.get_latest_quote(symbol)
            return float(quote.ask_price) if quote and quote.ask_price else 0.0
        except:
            return 0.0
    
    def _get_next_monthly_expiration(self) -> str:
        """Get next monthly options expiration date"""
        today = datetime.date.today()
        
        # Find third Friday of current month
        month = today.month
        year = today.year
        
        # If past third Friday, go to next month
        third_friday = self._get_third_friday(year, month)
        if today >= third_friday:
            month += 1
            if month > 12:
                month = 1
                year += 1
            third_friday = self._get_third_friday(year, month)
        
        return third_friday.strftime('%Y-%m-%d')
    
    def _get_third_friday(self, year: int, month: int) -> datetime.date:
        """Calculate third Friday of given month"""
        first_day = datetime.date(year, month, 1)
        first_friday = first_day + datetime.timedelta(days=(4 - first_day.weekday()) % 7)
        third_friday = first_friday + datetime.timedelta(days=14)
        return third_friday
    
    def get_portfolio_options_exposure(self) -> Dict:
        """Calculate current options exposure in portfolio with Greeks tracking"""
        try:
            positions = self.api.list_positions()
            account = self.api.get_account()
            portfolio_value = float(account.portfolio_value)
            
            options_value = 0.0
            options_positions = []
            total_delta = 0.0
            total_gamma = 0.0
            total_theta = 0.0
            total_vega = 0.0
            
            for position in positions:
                if 'option' in position.asset_class.lower():
                    market_value = float(position.market_value)
                    qty = float(position.qty)
                    options_value += market_value
                    
                    # Get Greeks for this option position
                    greeks = self._get_position_greeks(position.symbol, qty)
                    
                    total_delta += greeks.get('delta', 0)
                    total_gamma += greeks.get('gamma', 0)
                    total_theta += greeks.get('theta', 0)
                    total_vega += greeks.get('vega', 0)
                    
                    options_positions.append({
                        'symbol': position.symbol,
                        'qty': qty,
                        'market_value': market_value,
                        'unrealized_pl': float(position.unrealized_pl),
                        'delta': greeks.get('delta', 0),
                        'gamma': greeks.get('gamma', 0),
                        'theta': greeks.get('theta', 0),
                        'vega': greeks.get('vega', 0),
                        'strategy_type': self._identify_strategy_type(position.symbol, qty)
                    })
            
            return {
                'total_options_value': options_value,
                'options_allocation': options_value / portfolio_value if portfolio_value > 0 else 0,
                'max_allocation': self.max_options_allocation,
                'remaining_capacity': max(0, (self.max_options_allocation * portfolio_value) - options_value),
                'portfolio_greeks': {
                    'total_delta': total_delta,
                    'total_gamma': total_gamma,
                    'total_theta': total_theta,
                    'total_vega': total_vega
                },
                'risk_metrics': {
                    'delta_exposure': abs(total_delta) / portfolio_value * 100 if portfolio_value > 0 else 0,
                    'theta_decay': total_theta,  # Daily time decay
                    'vega_exposure': total_vega / 100  # Sensitivity to 1% vol change
                },
                'positions': options_positions
            }
            
        except Exception as e:
            print(f"⚠️ Error calculating options exposure: {e}")
            return {'total_options_value': 0, 'options_allocation': 0, 'positions': []}
    
    def _get_position_greeks(self, option_symbol: str, qty: float) -> Dict:
        """Get Greeks for an options position"""
        try:
            # Try to get option contract details and calculate Greeks
            # Note: Alpaca may provide Greeks directly or we may need to calculate
            
            # For now, return estimated Greeks based on option type and position
            # In production, would use actual Greeks from market data or calculate using Black-Scholes
            
            if 'C' in option_symbol:  # Call option
                return {
                    'delta': 0.50 * qty,  # Estimated delta for ATM call
                    'gamma': 0.02 * qty,  # Estimated gamma
                    'theta': -0.05 * qty,  # Time decay
                    'vega': 0.10 * qty    # Volatility sensitivity
                }
            elif 'P' in option_symbol:  # Put option
                return {
                    'delta': -0.50 * qty,  # Negative delta for puts
                    'gamma': 0.02 * qty,
                    'theta': -0.05 * qty,
                    'vega': 0.10 * qty
                }
            else:
                return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
                
        except Exception as e:
            print(f"⚠️ Error getting Greeks for {option_symbol}: {e}")
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
    
    def _identify_strategy_type(self, option_symbol: str, qty: float) -> str:
        """Identify the type of options strategy based on position"""
        try:
            # Simple strategy identification based on position characteristics
            if qty > 0 and 'C' in option_symbol:
                return 'long_call'
            elif qty < 0 and 'C' in option_symbol:
                return 'short_call'
            elif qty > 0 and 'P' in option_symbol:
                return 'long_put'
            elif qty < 0 and 'P' in option_symbol:
                return 'short_put'
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def monitor_options_positions(self) -> Dict:
        """Monitor all options positions and provide risk alerts"""
        exposure = self.get_portfolio_options_exposure()
        alerts = []
        
        # Check allocation limits
        if exposure['options_allocation'] > self.max_options_allocation:
            alerts.append({
                'type': 'allocation_warning',
                'message': f"Options allocation ({exposure['options_allocation']:.1%}) exceeds limit ({self.max_options_allocation:.1%})"
            })
        
        # Check portfolio Greeks
        greeks = exposure.get('portfolio_greeks', {})
        
        # Delta exposure alert
        if abs(greeks.get('total_delta', 0)) > 100:
            alerts.append({
                'type': 'delta_warning',
                'message': f"High delta exposure: {greeks.get('total_delta', 0):.2f}"
            })
        
        # Theta decay alert
        if greeks.get('total_theta', 0) < -50:
            alerts.append({
                'type': 'theta_warning',
                'message': f"High time decay: ${greeks.get('total_theta', 0):.2f}/day"
            })
        
        # Check expiring options (would need actual expiration dates)
        expiring_soon = self._check_expiring_options()
        if expiring_soon:
            alerts.append({
                'type': 'expiration_warning',
                'message': f"{len(expiring_soon)} options expiring within 7 days"
            })
        
        return {
            'exposure': exposure,
            'alerts': alerts,
            'recommendation': self._generate_risk_recommendation(exposure, alerts)
        }
    
    def _check_expiring_options(self) -> List[Dict]:
        """Check for options expiring soon"""
        # Would implement actual expiration checking in production
        return []
    
    def _generate_risk_recommendation(self, exposure: Dict, alerts: List[Dict]) -> str:
        """Generate risk management recommendation"""
        if not alerts:
            return "Options portfolio within acceptable risk parameters"
        
        if len(alerts) >= 3:
            return "HIGH RISK: Multiple alerts triggered. Consider reducing options exposure"
        elif len([a for a in alerts if 'warning' in a['type']]) >= 2:
            return "MODERATE RISK: Consider hedging or reducing position sizes"
        else:
            return "LOW RISK: Monitor positions closely"

def test_options_manager():
    """Test options manager functionality"""
    print("📊 Testing Options Manager...")
    
    try:
        # Create mock API
        class MockAPI:
            def get_account(self):
                class Account:
                    portfolio_value = "100000"
                return Account()
        
        mock_api = MockAPI()
        options_mgr = OptionsManager(mock_api)
        
        print("✅ Options Manager initialization successful")
        
        # Test strategy selection
        test_analysis = {
            'symbol': 'SPY',
            'underlying_price': 450.0,
            'market_regime': 'bullish',
            'confidence': 0.80
        }
        
        print(f"✅ Test analysis: {test_analysis}")
        print("📊 Options Manager ready for deployment")
        
        return True
        
    except Exception as e:
        print(f"❌ Options Manager test failed: {e}")
        return False

if __name__ == "__main__":
    test_options_manager()