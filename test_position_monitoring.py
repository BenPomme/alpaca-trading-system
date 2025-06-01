#!/usr/bin/env python3
"""
Quick test to check position monitoring functionality and current positions
"""

import os
import sys
import logging
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_test_environment():
    """Setup test environment with API client"""
    try:
        import alpaca_trade_api as tradeapi
        
        # Get API credentials
        api_key = os.getenv('ALPACA_PAPER_API_KEY')
        secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
        base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not api_key or not secret_key:
            print("❌ Missing Alpaca API credentials")
            return None
        
        # Create API client
        api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
        return api
        
    except Exception as e:
        print(f"❌ Error setting up API client: {e}")
        return None

def test_current_positions(api):
    """Test getting current positions from Alpaca"""
    print("\n" + "="*60)
    print("📊 TESTING CURRENT POSITIONS")
    print("="*60)
    
    try:
        # Get all positions
        positions = api.list_positions()
        
        print(f"📈 Total positions found: {len(positions)}")
        
        if not positions:
            print("💡 No current positions in Alpaca Paper Trading account")
            return []
        
        # Analyze each position
        crypto_positions = []
        options_positions = []
        stock_positions = []
        
        for i, position in enumerate(positions):
            try:
                symbol = getattr(position, 'symbol', 'UNKNOWN')
                qty = getattr(position, 'qty', '0')
                market_value = getattr(position, 'market_value', '0')
                unrealized_pl = getattr(position, 'unrealized_pl', '0')
                
                # Try to get avg_entry_price safely (QA Rule 9)
                avg_entry_price = None
                if hasattr(position, 'avg_entry_price') and position.avg_entry_price:
                    avg_entry_price = float(position.avg_entry_price)
                elif hasattr(position, 'cost_basis') and position.cost_basis:
                    avg_entry_price = float(position.cost_basis)
                else:
                    # Calculate fallback
                    try:
                        avg_entry_price = float(market_value) / float(qty) if float(qty) != 0 else 0.0
                    except:
                        avg_entry_price = 0.0
                
                position_data = {
                    'symbol': symbol,
                    'qty': float(qty) if str(qty).replace('-', '').replace('.', '').isdigit() else 0.0,
                    'market_value': float(market_value) if str(market_value).replace('-', '').replace('.', '').isdigit() else 0.0,
                    'avg_entry_price': avg_entry_price,
                    'unrealized_pl': float(unrealized_pl) if str(unrealized_pl).replace('-', '').replace('.', '').isdigit() else 0.0,
                    'unrealized_pl_pct': 0.0
                }
                
                # Calculate P&L percentage
                if position_data['market_value'] != 0:
                    position_data['unrealized_pl_pct'] = position_data['unrealized_pl'] / abs(position_data['market_value'])
                
                # Categorize position
                if 'USD' in symbol and symbol.endswith('USD'):
                    crypto_positions.append(position_data)
                    category = "CRYPTO"
                elif len(symbol) > 10 and any(char.isdigit() for char in symbol[-8:]):
                    options_positions.append(position_data)
                    category = "OPTIONS"
                else:
                    stock_positions.append(position_data)
                    category = "STOCK/ETF"
                
                print(f"\n📍 Position {i+1}: {symbol} ({category})")
                print(f"   Quantity: {position_data['qty']}")
                print(f"   Market Value: ${position_data['market_value']:.2f}")
                print(f"   Entry Price: ${position_data['avg_entry_price']:.2f}")
                print(f"   Unrealized P&L: ${position_data['unrealized_pl']:.2f} ({position_data['unrealized_pl_pct']:.1%})")
                
            except Exception as e:
                print(f"❌ Error processing position {i+1}: {e}")
                continue
        
        print(f"\n📊 POSITION SUMMARY:")
        print(f"   Crypto Positions: {len(crypto_positions)}")
        print(f"   Options Positions: {len(options_positions)}")
        print(f"   Stock/ETF Positions: {len(stock_positions)}")
        
        return {
            'crypto': crypto_positions,
            'options': options_positions,
            'stocks': stock_positions
        }
        
    except Exception as e:
        print(f"❌ Error getting positions: {e}")
        return []

def test_crypto_position_monitoring(api, crypto_positions):
    """Test crypto position monitoring methods"""
    print("\n" + "="*60)
    print("₿ TESTING CRYPTO POSITION MONITORING")
    print("="*60)
    
    if not crypto_positions:
        print("💡 No crypto positions to monitor")
        return
    
    try:
        # Test individual crypto position analysis
        for position in crypto_positions:
            symbol = position['symbol']
            unrealized_pl_pct = position['unrealized_pl_pct']
            
            print(f"\n🔍 Analyzing {symbol}:")
            print(f"   Current P&L: {unrealized_pl_pct:.1%}")
            
            # Simulate exit analysis logic from crypto module
            exit_signal = None
            
            if unrealized_pl_pct >= 0.25:  # 25% profit target
                exit_signal = 'profit_target'
            elif unrealized_pl_pct <= -0.15:  # 15% stop loss
                exit_signal = 'stop_loss'
            elif unrealized_pl_pct >= 0.05:  # 5% modest profit
                exit_signal = 'modest_profit'
            
            if exit_signal:
                print(f"   🚨 EXIT SIGNAL: {exit_signal}")
            else:
                print(f"   ✅ HOLD: No exit conditions met")
        
    except Exception as e:
        print(f"❌ Error in crypto position monitoring test: {e}")

def test_options_position_monitoring(api, options_positions):
    """Test options position monitoring methods"""
    print("\n" + "="*60)
    print("📈 TESTING OPTIONS POSITION MONITORING")
    print("="*60)
    
    if not options_positions:
        print("💡 No options positions to monitor")
        return
    
    try:
        # Test individual options position analysis
        for position in options_positions:
            symbol = position['symbol']
            unrealized_pl_pct = position['unrealized_pl_pct']
            
            print(f"\n🔍 Analyzing {symbol}:")
            print(f"   Current P&L: {unrealized_pl_pct:.1%}")
            
            # Simulate exit analysis logic from options module
            exit_signal = None
            
            if unrealized_pl_pct >= 1.0:  # 100% profit target for options
                exit_signal = 'profit_target'
            elif unrealized_pl_pct <= -0.5:  # 50% stop loss for options
                exit_signal = 'stop_loss'
            # Note: Would also check expiration date in real implementation
            
            if exit_signal:
                print(f"   🚨 EXIT SIGNAL: {exit_signal}")
            else:
                print(f"   ✅ HOLD: No exit conditions met")
        
    except Exception as e:
        print(f"❌ Error in options position monitoring test: {e}")

def test_portfolio_allocation(api, position_data):
    """Test portfolio allocation calculations"""
    print("\n" + "="*60)
    print("💼 TESTING PORTFOLIO ALLOCATION")
    print("="*60)
    
    try:
        # Get account information
        account = api.get_account()
        portfolio_value = float(getattr(account, 'portfolio_value', 100000))
        
        print(f"💰 Total Portfolio Value: ${portfolio_value:,.2f}")
        
        # Calculate allocations
        crypto_value = sum(abs(pos['market_value']) for pos in position_data.get('crypto', []))
        options_value = sum(abs(pos['market_value']) for pos in position_data.get('options', []))
        stocks_value = sum(abs(pos['market_value']) for pos in position_data.get('stocks', []))
        
        crypto_allocation = crypto_value / portfolio_value if portfolio_value > 0 else 0
        options_allocation = options_value / portfolio_value if portfolio_value > 0 else 0
        stocks_allocation = stocks_value / portfolio_value if portfolio_value > 0 else 0
        
        print(f"\n📊 ALLOCATION BREAKDOWN:")
        print(f"   Crypto: ${crypto_value:,.2f} ({crypto_allocation:.1%})")
        print(f"   Options: ${options_value:,.2f} ({options_allocation:.1%})")
        print(f"   Stocks/ETFs: ${stocks_value:,.2f} ({stocks_allocation:.1%})")
        
        # Check against limits
        print(f"\n🚨 ALLOCATION LIMITS CHECK:")
        print(f"   Crypto limit (30%): {crypto_allocation:.1%} {'✅ OK' if crypto_allocation <= 0.30 else '❌ OVER LIMIT'}")
        print(f"   Options limit (30%): {options_allocation:.1%} {'✅ OK' if options_allocation <= 0.30 else '❌ OVER LIMIT'}")
        
    except Exception as e:
        print(f"❌ Error testing portfolio allocation: {e}")

def test_real_time_quotes(api):
    """Test getting real-time quote data for analysis"""
    print("\n" + "="*60)
    print("📡 TESTING REAL-TIME QUOTE DATA")
    print("="*60)
    
    test_symbols = ['SPY', 'BTC/USD', 'ETH/USD']
    
    for symbol in test_symbols:
        try:
            print(f"\n🔍 Testing quotes for {symbol}:")
            
            if '/' in symbol:
                # Crypto symbol
                try:
                    bars = api.get_latest_crypto_bars(symbol)
                    if bars and symbol in bars:
                        bar = bars[symbol]
                        price = float(bar.c) if hasattr(bar, 'c') else 0.0
                        print(f"   Real crypto price from bars: ${price}")
                    else:
                        print(f"   ❌ No crypto bars data for {symbol}")
                        
                    quotes = api.get_latest_crypto_quotes(symbol)
                    if quotes and symbol in quotes:
                        quote = quotes[symbol]
                        ask = float(quote.ap) if hasattr(quote, 'ap') and quote.ap else 0.0
                        bid = float(quote.bp) if hasattr(quote, 'bp') and quote.bp else 0.0
                        print(f"   Real crypto quotes: Bid=${bid}, Ask=${ask}")
                    else:
                        print(f"   ❌ No crypto quotes data for {symbol}")
                        
                except Exception as e:
                    print(f"   ❌ Crypto API error: {e}")
            else:
                # Stock symbol
                try:
                    quote = api.get_latest_quote(symbol)
                    if quote:
                        ask = float(quote.ask_price) if hasattr(quote, 'ask_price') and quote.ask_price else 0.0
                        bid = float(quote.bid_price) if hasattr(quote, 'bid_price') and quote.bid_price else 0.0
                        print(f"   Real stock quotes: Bid=${bid}, Ask=${ask}")
                    else:
                        print(f"   ❌ No stock quote data for {symbol}")
                except Exception as e:
                    print(f"   ❌ Stock API error: {e}")
                    
        except Exception as e:
            print(f"❌ Error testing {symbol}: {e}")

def main():
    """Main test function"""
    print("🚀 ALPACA POSITION MONITORING TEST")
    print(f"⏰ Test started at: {datetime.now()}")
    
    # Setup API client
    api = setup_test_environment()
    if not api:
        print("❌ Failed to setup API client - exiting")
        return
    
    # Test current positions
    position_data = test_current_positions(api)
    
    if position_data:
        # Test position monitoring for each asset type
        test_crypto_position_monitoring(api, position_data.get('crypto', []))
        test_options_position_monitoring(api, position_data.get('options', []))
        
        # Test portfolio allocation
        test_portfolio_allocation(api, position_data)
    
    # Test real-time data retrieval
    test_real_time_quotes(api)
    
    print(f"\n✅ Test completed at: {datetime.now()}")
    print("\n" + "="*60)
    print("📋 SUMMARY:")
    print("This test examined:")
    print("1. Current positions in Alpaca Paper Trading account")
    print("2. Position monitoring logic for exits")
    print("3. Portfolio allocation calculations")
    print("4. Real-time price data retrieval")
    print("5. Unrealized P&L calculations")
    print("="*60)

if __name__ == "__main__":
    main()