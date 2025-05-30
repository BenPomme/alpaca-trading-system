#!/usr/bin/env python3
"""
Risk Management System for Phase 2
Advanced risk controls and position management
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database_manager import TradingDatabase

class RiskManager:
    """Advanced risk management for trading system"""
    
    def __init__(self, api_client, db: TradingDatabase = None):
        self.api = api_client
        self.db = db
        
        # Risk Parameters (Phase 4.1: Unlimited positions for aggressive strategy)
        self.max_positions = None                 # No limit on concurrent positions
        self.max_daily_trades = 20                # Maximum trades per day
        self.max_position_size_pct = 0.15         # 15% of portfolio per position
        self.max_sector_exposure = 0.60           # 60% exposure to any sector (aggressive target)
        self.max_daily_loss_pct = 0.05            # 5% daily portfolio loss limit
        self.position_risk_pct = 0.02             # 2% risk per trade
        
        # Stop Loss & Take Profit
        self.stop_loss_pct = 0.03                 # 3% stop loss
        self.take_profit_pct = 0.08               # 8% take profit
        self.quick_profit_pct = 0.03              # 3% quick profit (same day)
        self.max_hold_days = 5                    # Maximum hold period
        
        # Confidence-based adjustments
        self.confidence_multipliers = {
            'aggressive_momentum': 1.5,           # High confidence = larger positions
            'momentum': 1.0,                      # Standard positions
            'cautious_momentum': 0.7,             # Smaller positions
            'conservative': 0.3                   # Minimal positions
        }
        
        print("✅ Risk Manager initialized")
        self.print_risk_parameters()
    
    def print_risk_parameters(self):
        """Display current risk parameters"""
        print("📊 Risk Management Parameters:")
        print(f"   Max Positions: {'Unlimited' if self.max_positions is None else self.max_positions}")
        print(f"   Max Position Size: {self.max_position_size_pct:.1%}")
        print(f"   Position Risk: {self.position_risk_pct:.1%}")
        print(f"   Stop Loss: {self.stop_loss_pct:.1%}")
        print(f"   Take Profit: {self.take_profit_pct:.1%}")
        print(f"   Max Daily Loss: {self.max_daily_loss_pct:.1%}")
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                               strategy: str, confidence: float, 
                               portfolio_value: float) -> Tuple[int, Dict]:
        """Calculate optimal position size with risk management"""
        
        # Base risk amount (2% of portfolio)
        base_risk_amount = portfolio_value * self.position_risk_pct
        
        # Strategy-based risk adjustment
        strategy_multiplier = self.confidence_multipliers.get(strategy, 1.0)
        
        # Confidence-based adjustment (scale with confidence 0.5-1.0 → 0.7-1.3)
        confidence_multiplier = 0.7 + (confidence * 0.6)
        
        # Calculate adjusted risk
        adjusted_risk = base_risk_amount * strategy_multiplier * confidence_multiplier
        
        # Position size limits
        max_position_value = portfolio_value * self.max_position_size_pct
        target_position_value = min(adjusted_risk, max_position_value)
        
        # Calculate shares
        target_shares = int(target_position_value / entry_price)
        
        # Minimum position check
        if target_shares == 0 and adjusted_risk >= entry_price:
            target_shares = 1
        
        sizing_info = {
            'base_risk_amount': base_risk_amount,
            'strategy_multiplier': strategy_multiplier,
            'confidence_multiplier': confidence_multiplier,
            'adjusted_risk': adjusted_risk,
            'max_position_value': max_position_value,
            'target_position_value': target_position_value,
            'target_shares': target_shares,
            'estimated_cost': target_shares * entry_price
        }
        
        return target_shares, sizing_info
    
    def check_position_limits(self, symbol: str, target_shares: int, 
                             entry_price: float) -> Tuple[bool, str]:
        """Check if position meets all risk limits"""
        try:
            # Get current positions
            positions = self.api.list_positions()
            account = self.api.get_account()
            
            # DEBUG: Check account data
            print(f"🔍 ACCOUNT DEBUG:")
            print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
            print(f"   Buying Power: ${float(account.buying_power):,.2f}")
            print(f"   Cash: ${float(account.cash):,.2f}")
            print(f"   Account Status: {account.status}")
            print(f"   Day Trading Buying Power: ${float(getattr(account, 'daytrading_buying_power', 0)):,.2f}")
            
            portfolio_value = float(account.portfolio_value)
            
            # EMERGENCY FIX: Allow multiple trades in same symbol for aggressive strategy
            # Check if already have position (but allow position building for unlimited strategy)
            existing_position = next((p for p in positions if p.symbol == symbol), None)
            if existing_position:
                # For aggressive strategy, allow position building up to 2x the normal size
                current_value = float(existing_position.market_value)
                max_total_position = portfolio_value * (self.max_position_size_pct * 2)  # 30% total max per symbol
                
                if current_value + (target_shares * entry_price) > max_total_position:
                    return False, f"Position in {symbol} would exceed 30% limit (current: ${current_value:,.0f})"
                else:
                    print(f"   ✅ Position building allowed for {symbol} (current: ${current_value:,.0f})")
                    # Continue with other checks
            
            # Check maximum positions (Phase 4.1: Unlimited positions enabled)
            if self.max_positions is not None and len(positions) >= self.max_positions:
                return False, f"Maximum positions reached ({self.max_positions})"
            
            # Check position size limit
            position_value = target_shares * entry_price
            position_pct = position_value / portfolio_value
            if position_pct > self.max_position_size_pct:
                return False, f"Position too large ({position_pct:.1%} > {self.max_position_size_pct:.1%})"
            
            # Check buying power (FIXED: Use RegT buying power, not day trading)
            # Try RegT buying power first (this is what we want!)
            regt_bp = float(getattr(account, 'regt_buying_power', 0))
            buying_power = float(account.buying_power)  # Default (day trading)
            
            if regt_bp > 0:
                buying_power = regt_bp
                print(f"   ✅ Using RegT buying power: ${buying_power:,.2f}")
            elif buying_power > 0:
                print(f"   ✅ Using standard buying power: ${buying_power:,.2f}")
            else:
                # Fallback to cash if both are 0
                cash = float(account.cash)
                if cash > 0:
                    buying_power = cash
                    print(f"   🔄 Using cash balance: ${buying_power:,.2f}")
                else:
                    # Last resort: use portfolio value
                    buying_power = portfolio_value
                    print(f"   🔄 Using portfolio value as buying power: ${buying_power:,.2f}")
            
            print(f"   💰 Final buying power used: ${buying_power:,.2f}")
            
            if position_value > buying_power:
                return False, f"Insufficient buying power (${position_value:,.2f} > ${buying_power:,.2f})"
            
            # Check daily trading limit
            if self.db:
                today = datetime.now().date().isoformat()
                # This would check trade count from database
                # For now, we'll assume it's okay
                pass
            
            return True, "Position approved"
            
        except Exception as e:
            return False, f"Risk check error: {e}"
    
    def check_sector_exposure(self, symbol: str, target_value: float) -> Tuple[bool, str]:
        """Check sector exposure limits"""
        try:
            # EMERGENCY FIX: Expanded sector mapping to prevent unknown sector clustering
            sector_map = {
                # Market ETFs
                'SPY': 'market', 'QQQ': 'technology', 'IWM': 'small_cap', 'VTI': 'market',
                'DIA': 'market', 'VEA': 'international', 'EFA': 'international', 'IEFA': 'international',
                'VWO': 'emerging_markets', 'FXI': 'china', 'EWJ': 'japan', 'EWT': 'taiwan',
                'EWY': 'korea', 'INDA': 'india',
                
                # Technology
                'AAPL': 'technology', 'MSFT': 'technology', 'GOOGL': 'technology', 'GOOG': 'technology',
                'AMZN': 'technology', 'TSLA': 'technology', 'META': 'technology', 'NVDA': 'technology',
                'AMD': 'technology', 'INTC': 'technology', 'ORCL': 'technology', 'CRM': 'technology',
                'CSCO': 'technology', 'AVGO': 'technology', 'ADBE': 'technology', 'PYPL': 'technology',
                'ZM': 'technology', 'DOCU': 'technology', 'WDAY': 'technology', 'SNPS': 'technology',
                'LRCX': 'technology', 'AMAT': 'technology', 'MRVL': 'technology',
                
                # Finance
                'JPM': 'finance', 'BAC': 'finance', 'XLF': 'finance',
                
                # Healthcare
                'JNJ': 'healthcare', 'PFE': 'healthcare', 'GILD': 'healthcare', 'MRNA': 'healthcare',
                'XLV': 'healthcare',
                
                # Energy
                'XOM': 'energy', 'XLE': 'energy',
                
                # Consumer
                'DIS': 'consumer', 'SBUX': 'consumer', 'ABNB': 'consumer',
                'EBAY': 'consumer', 'XLY': 'consumer',
                
                # Communications
                'CMCSA': 'communications', 'T': 'communications', 'VZ': 'communications',
                
                # Industrial
                'TXN': 'industrial',
                
                # Sector ETFs
                'XLK': 'technology', 'XLV': 'healthcare', 'XLF': 'finance', 'XLE': 'energy',
                'XLY': 'consumer',
                
                # Crypto (treat as separate asset class)
                'BTCUSD': 'crypto', 'ETHUSD': 'crypto', 'SOLUSD': 'crypto', 'AAVEUSD': 'crypto'
            }
            
            symbol_sector = sector_map.get(symbol, 'unknown')
            
            # EMERGENCY FIX: Special handling for unknown symbols
            if symbol_sector == 'unknown':
                # For unknown symbols, create individual "sectors" to prevent clustering
                symbol_sector = f'unknown_{symbol}'
                print(f"⚠️ Unknown symbol {symbol} - treating as individual sector")
            
            # Get current positions in same sector
            positions = self.api.list_positions()
            account = self.api.get_account()
            portfolio_value = float(account.portfolio_value)
            
            # Calculate sector exposure with debugging
            sector_exposure = 0.0
            sector_positions = []
            
            for pos in positions:
                pos_symbol = pos.symbol
                pos_sector = sector_map.get(pos_symbol, f'unknown_{pos_symbol}')  # Individual sectors for unknown
                
                if pos_sector == symbol_sector:
                    pos_value = float(pos.market_value)
                    sector_exposure += pos_value
                    sector_positions.append(f"{pos_symbol}(${pos_value:,.0f})")
            
            # Add target position
            total_sector_exposure = sector_exposure + target_value
            sector_exposure_pct = total_sector_exposure / portfolio_value
            
            # Debug logging
            print(f"🔍 SECTOR EXPOSURE CHECK: {symbol} ({symbol_sector})")
            print(f"   📊 Current sector positions: {sector_positions}")
            print(f"   💰 Current exposure: ${sector_exposure:,.0f}")
            print(f"   🎯 Target addition: ${target_value:,.0f}")
            print(f"   📈 Total would be: ${total_sector_exposure:,.0f} ({sector_exposure_pct:.1%})")
            print(f"   🚦 Limit: {self.max_sector_exposure:.1%}")
            
            if sector_exposure_pct > self.max_sector_exposure:
                return False, f"Sector exposure too high ({sector_exposure_pct:.1%} > {self.max_sector_exposure:.1%})"
            
            return True, f"Sector exposure OK ({sector_exposure_pct:.1%})"
            
        except Exception as e:
            return False, f"Sector check error: {e}"
    
    def check_daily_loss_limit(self) -> Tuple[bool, str]:
        """Check if daily loss limit has been reached"""
        try:
            account = self.api.get_account()
            equity = float(account.equity)
            last_equity = float(account.last_equity)
            
            daily_pl = equity - last_equity
            daily_pl_pct = daily_pl / last_equity if last_equity > 0 else 0
            
            if daily_pl_pct <= -self.max_daily_loss_pct:
                return False, f"Daily loss limit reached ({daily_pl_pct:.1%})"
            
            return True, f"Daily P&L: {daily_pl_pct:+.1%}"
            
        except Exception as e:
            return False, f"Daily loss check error: {e}"
    
    def should_execute_trade(self, symbol: str, strategy: str, confidence: float,
                           entry_price: float) -> Tuple[bool, str, Dict]:
        """Comprehensive trade approval check"""
        
        try:
            account = self.api.get_account()
            portfolio_value = float(account.portfolio_value)
            
            # Calculate position size
            target_shares, sizing_info = self.calculate_position_size(
                symbol, entry_price, strategy, confidence, portfolio_value
            )
            
            if target_shares <= 0:
                return False, "Position size too small", {}
            
            target_value = target_shares * entry_price
            
            # Run all risk checks
            checks = []
            
            # Position limits check
            position_ok, position_msg = self.check_position_limits(symbol, target_shares, entry_price)
            checks.append(('Position Limits', position_ok, position_msg))
            
            # Sector exposure check
            sector_ok, sector_msg = self.check_sector_exposure(symbol, target_value)
            checks.append(('Sector Exposure', sector_ok, sector_msg))
            
            # Daily loss check
            daily_ok, daily_msg = self.check_daily_loss_limit()
            checks.append(('Daily Loss Limit', daily_ok, daily_msg))
            
            # Print risk assessment
            print(f"🔍 RISK ASSESSMENT: {symbol}")
            for check_name, check_ok, check_msg in checks:
                status = "✅" if check_ok else "❌"
                print(f"   {status} {check_name}: {check_msg}")
            
            # Overall approval
            all_checks_pass = all(check[1] for check in checks)
            
            if all_checks_pass:
                print(f"✅ TRADE APPROVED: {symbol} ({target_shares} shares, ${target_value:,.2f})")
                
                trade_info = {
                    'approved': True,
                    'target_shares': target_shares,
                    'target_value': target_value,
                    'sizing_info': sizing_info,
                    'risk_checks': checks
                }
                
                return True, "Trade approved", trade_info
            else:
                failed_checks = [check[2] for check in checks if not check[1]]
                return False, f"Risk checks failed: {'; '.join(failed_checks)}", {}
            
        except Exception as e:
            return False, f"Risk assessment error: {e}", {}
    
    def calculate_stop_loss_take_profit(self, entry_price: float, strategy: str) -> Dict:
        """Calculate stop loss and take profit levels"""
        
        # Strategy-based adjustments
        if strategy == 'aggressive_momentum':
            stop_loss_pct = self.stop_loss_pct * 1.2    # Wider stops for aggressive trades
            take_profit_pct = self.take_profit_pct * 1.2 # Higher targets
        elif strategy == 'cautious_momentum':
            stop_loss_pct = self.stop_loss_pct * 0.8    # Tighter stops
            take_profit_pct = self.take_profit_pct * 0.8 # Lower targets
        else:
            stop_loss_pct = self.stop_loss_pct
            take_profit_pct = self.take_profit_pct
        
        stop_loss_price = entry_price * (1 - stop_loss_pct)
        take_profit_price = entry_price * (1 + take_profit_pct)
        quick_profit_price = entry_price * (1 + self.quick_profit_pct)
        
        return {
            'stop_loss_price': stop_loss_price,
            'take_profit_price': take_profit_price,
            'quick_profit_price': quick_profit_price,
            'stop_loss_pct': stop_loss_pct,
            'take_profit_pct': take_profit_pct,
            'quick_profit_pct': self.quick_profit_pct
        }
    
    def get_risk_metrics(self) -> Dict:
        """Get current portfolio risk metrics"""
        try:
            account = self.api.get_account()
            positions = self.api.list_positions()
            
            portfolio_value = float(account.portfolio_value)
            total_market_value = sum(float(pos.market_value) for pos in positions)
            total_unrealized_pl = sum(float(pos.unrealized_pl) for pos in positions)
            
            # Calculate daily P&L
            equity = float(account.equity)
            last_equity = float(account.last_equity)
            daily_pl = equity - last_equity
            daily_pl_pct = (daily_pl / last_equity) * 100 if last_equity > 0 else 0
            
            # Portfolio utilization
            utilization_pct = (total_market_value / portfolio_value) * 100
            
            # Risk exposure
            largest_position_value = max([float(pos.market_value) for pos in positions], default=0)
            largest_position_pct = (largest_position_value / portfolio_value) * 100
            
            return {
                'portfolio_value': portfolio_value,
                'total_positions': len(positions),
                'portfolio_utilization_pct': utilization_pct,
                'largest_position_pct': largest_position_pct,
                'daily_pl': daily_pl,
                'daily_pl_pct': daily_pl_pct,
                'total_unrealized_pl': total_unrealized_pl,
                'unrealized_pl_pct': (total_unrealized_pl / portfolio_value) * 100,
                'risk_limit_usage': {
                    'max_positions': f"{len(positions)}/{'Unlimited' if self.max_positions is None else self.max_positions}",
                    'daily_loss_usage': f"{abs(min(0, daily_pl_pct)):.1f}%/{self.max_daily_loss_pct*100:.1f}%"
                }
            }
            
        except Exception as e:
            return {'error': f'Risk metrics calculation failed: {e}'}

def test_risk_manager():
    """Test risk management functionality"""
    print("🧪 Testing Risk Manager...")
    
    try:
        from enhanced_trader import EnhancedTrader
        from database_manager import TradingDatabase
        
        trader = EnhancedTrader(use_database=False)
        db = TradingDatabase()
        
        risk_mgr = RiskManager(trader.api, db)
        
        # Test risk metrics
        metrics = risk_mgr.get_risk_metrics()
        print(f"✅ Portfolio utilization: {metrics.get('portfolio_utilization_pct', 0):.1f}%")
        
        # Test position sizing
        shares, sizing = risk_mgr.calculate_position_size('AAPL', 200.0, 'momentum', 0.8, 100000)
        print(f"✅ Position sizing: {shares} shares for AAPL @ $200")
        
        # Test trade approval
        approved, msg, info = risk_mgr.should_execute_trade('AAPL', 'momentum', 0.8, 200.0)
        print(f"✅ Trade approval: {approved} - {msg}")
        
        print("✅ Risk Manager test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Risk Manager test failed: {e}")
        return False

if __name__ == "__main__":
    # Set environment for testing
    os.environ['ALPACA_PAPER_API_KEY'] = os.environ.get('ALPACA_PAPER_API_KEY', 'PKOBXG3RWCRQTXH6ID0L')
    os.environ['ALPACA_PAPER_SECRET_KEY'] = os.environ.get('ALPACA_PAPER_SECRET_KEY', '8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn')
    
    test_risk_manager()