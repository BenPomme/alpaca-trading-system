#!/usr/bin/env python3
"""
CRITICAL TRADING AUDIT - WHY ONLY UNIUSD?
Comprehensive audit of why the system is failing to diversify
"""

import os
import logging
from datetime import datetime, timedelta
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderStatus, OrderSide
from modular.orchestrator import ModularOrchestrator
from modular.crypto_module import CryptoModule  
from modular.stocks_module import StocksModule

# Set up API credentials
api_key = os.getenv('ALPACA_PAPER_API_KEY', 'PKIP9MZ4Q1WJ423JXOQU')
secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY', 'zjGO4D9sED7ATSv6J1UCKCl0xzOOep5hPHRRmRcc')

print("🚨 CRITICAL TRADING SYSTEM AUDIT")
print("=" * 60)
print(f"⏰ Audit Time: {datetime.now()}")
print("")

try:
    # Initialize Alpaca client
    client = TradingClient(api_key, secret_key, paper=True)
    account = client.get_account()
    
    print("💰 ACCOUNT STATUS:")
    print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"  Buying Power: ${float(account.buying_power):,.2f}")
    print(f"  Day Trading Power: ${float(account.daytrading_buying_power):,.2f}")
    print("")
    
    # Get current positions
    positions = client.get_all_positions()
    print(f"📊 CURRENT POSITIONS ({len(positions)} total):")
    if positions:
        total_exposure = 0
        for pos in positions:
            market_val = float(pos.market_value)
            pnl = float(pos.unrealized_pl)
            pct_of_portfolio = (market_val / float(account.portfolio_value)) * 100
            total_exposure += market_val
            print(f"  {pos.symbol}: ${market_val:,.2f} ({pct_of_portfolio:.1f}% of portfolio)")
            print(f"    Qty: {pos.qty}, P&L: ${pnl:,.2f}")
        
        print(f"\n💸 RISK ANALYSIS:")
        print(f"  Total Exposure: ${total_exposure:,.2f}")
        print(f"  Portfolio Concentration: {(total_exposure / float(account.portfolio_value)) * 100:.1f}%")
        if len(positions) == 1:
            print("  ❌ CRITICAL: Single position concentration risk!")
    else:
        print("  No positions")
    
    print("")
    
    # Get recent orders
    print("📋 RECENT TRADING ACTIVITY (Last 20 orders):")
    recent_orders = client.get_orders(limit=20)
    
    if recent_orders:
        symbol_counts = {}
        filled_orders = []
        
        for order in recent_orders:
            symbol = order.symbol
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
            
            if order.status == OrderStatus.FILLED:
                filled_orders.append(order)
            
            print(f"  {order.created_at.strftime('%m-%d %H:%M')} {order.symbol} {order.side} {order.qty}")
            print(f"    Status: {order.status}, Filled: ${order.filled_avg_price or 'N/A'}")
        
        print(f"\n🎯 TRADING PATTERNS:")
        print(f"  Symbols traded: {list(symbol_counts.keys())}")
        print(f"  Order distribution: {symbol_counts}")
        print(f"  Filled orders: {len(filled_orders)}/{len(recent_orders)}")
        
        if len(symbol_counts) == 1:
            print("  ❌ CRITICAL: Trading only ONE symbol!")
    else:
        print("  No recent orders")
    
    print("")
    
    # Test module opportunity detection
    print("🔍 MODULE ANALYSIS:")
    print("-" * 40)
    
    # Test crypto module
    print("₿ CRYPTO MODULE AUDIT:")
    try:
        crypto_module = CryptoModule(api_client=client)
        crypto_opportunities = crypto_module.analyze_opportunities()
        print(f"  Opportunities found: {len(crypto_opportunities)}")
        
        if crypto_opportunities:
            print("  Top opportunities:")
            for i, opp in enumerate(crypto_opportunities[:3]):
                print(f"    {i+1}. {opp.symbol}: confidence {opp.confidence:.3f}")
        else:
            print("  ❌ NO CRYPTO OPPORTUNITIES DETECTED")
            
        # Check crypto universe
        print(f"  Crypto universe: {crypto_module.crypto_universe}")
        
    except Exception as e:
        print(f"  ❌ Crypto module error: {e}")
    
    print("")
    
    # Test stocks module  
    print("📈 STOCKS MODULE AUDIT:")
    try:
        stocks_module = StocksModule(api_client=client)
        stock_opportunities = stocks_module.analyze_opportunities()
        print(f"  Opportunities found: {len(stock_opportunities)}")
        
        if stock_opportunities:
            print("  Top opportunities:")
            for i, opp in enumerate(stock_opportunities[:3]):
                print(f"    {i+1}. {opp.symbol}: confidence {opp.confidence:.3f}")
        else:
            print("  ❌ NO STOCK OPPORTUNITIES DETECTED")
            
        # Check stock universe
        print(f"  Stock universe size: {len(stocks_module.stock_universe)}")
        print(f"  First 10 stocks: {stocks_module.stock_universe[:10]}")
        
    except Exception as e:
        print(f"  ❌ Stocks module error: {e}")
    
    print("")
    
    # Check system configuration
    print("⚙️ SYSTEM CONFIGURATION AUDIT:")
    print(f"  EXECUTION_ENABLED: {os.getenv('EXECUTION_ENABLED', 'Not set')}")
    print(f"  GLOBAL_TRADING: {os.getenv('GLOBAL_TRADING', 'Not set')}")
    print(f"  CRYPTO_TRADING: {os.getenv('CRYPTO_TRADING', 'Not set')}")
    print(f"  OPTIONS_TRADING: {os.getenv('OPTIONS_TRADING', 'Not set')}")
    print(f"  MIN_CONFIDENCE: {os.getenv('MIN_CONFIDENCE', 'Not set')}")
    print(f"  MARKET_TIER: {os.getenv('MARKET_TIER', 'Not set')}")
    
except Exception as e:
    print(f"❌ AUDIT FAILED: {e}")
    import traceback
    traceback.print_exc()

print("")
print("🏁 AUDIT COMPLETE")