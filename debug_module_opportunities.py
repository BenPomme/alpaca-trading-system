#!/usr/bin/env python3
"""
DEBUG MODULE OPPORTUNITIES - Find out why only UNIUSD is trading
"""

import os
import logging
from modular.crypto_module import CryptoModule
from modular.stocks_module import StocksModule
from modular.base_module import ModuleConfig
import alpaca_trade_api as tradeapi

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set API credentials
api_key = 'PKIP9MZ4Q1WJ423JXOQU'
secret_key = 'zjGO4D9sED7ATSv6J1UCKCl0xzOOep5hPHRRmRcc'

print("🔍 DEBUGGING MODULE OPPORTUNITIES")
print("=" * 50)

try:
    # Initialize Alpaca API
    api = tradeapi.REST(api_key, secret_key, 'https://paper-api.alpaca.markets')
    
    print("✅ Alpaca API connected")
    
    # Test Crypto Module
    print("\n₿ CRYPTO MODULE DEBUG:")
    print("-" * 30)
    
    crypto_config = ModuleConfig(
        module_name="crypto",
        enabled=True,
        max_allocation_pct=60.0,
        min_confidence=0.35,  # This should be low enough
        max_positions=15
    )
    
    crypto_module = CryptoModule(
        config=crypto_config,
        firebase_db=None,  # Mock
        risk_manager=None,  # Mock
        order_executor=None,  # Mock
        api_client=api,
        logger=logger
    )
    
    print(f"Crypto Universe: {crypto_module.supported_symbols}")
    print(f"Min Confidence: {crypto_config.min_confidence}")
    
    # Test crypto opportunities
    crypto_opportunities = crypto_module.analyze_opportunities()
    print(f"\nCrypto Opportunities Found: {len(crypto_opportunities)}")
    
    for i, opp in enumerate(crypto_opportunities):
        print(f"  {i+1}. {opp.symbol}: confidence={opp.confidence:.3f}, strategy={opp.strategy}")
        print(f"      action={opp.action}, qty={opp.quantity}, max_pos_size=${opp.max_position_size:.2f}")
        print(f"      technical={opp.technical_score:.2f}, stop_loss={opp.stop_loss_pct:.1%}")
    
    # Now test if crypto module can EXECUTE these opportunities
    print(f"\n🔍 CRYPTO EXECUTION TEST:")
    if crypto_opportunities:
        print(f"  Testing execution of first opportunity: {crypto_opportunities[0].symbol}")
        try:
            # Test if the opportunity passes validation
            first_opp = crypto_opportunities[0]
            validates = crypto_module.validate_opportunity(first_opp)
            print(f"  Validation result: {validates}")
            
            # Test what happens during execution
            if validates:
                print(f"  ✅ Opportunity would pass validation")
            else:
                print(f"  ❌ Opportunity fails validation")
        except Exception as e:
            print(f"  ❌ Validation error: {e}")
    
    # Test Stocks Module
    print("\n📈 STOCKS MODULE DEBUG:")
    print("-" * 30)
    
    stocks_config = ModuleConfig(
        module_name="stocks",
        enabled=True,
        max_allocation_pct=70.0,
        min_confidence=0.30,  # Very low threshold
        max_positions=30
    )
    
    stocks_module = StocksModule(
        config=stocks_config,
        firebase_db=None,  # Mock
        risk_manager=None,  # Mock
        order_executor=None,  # Mock
        api_client=api,
        logger=logger
    )
    
    print(f"Stocks Universe Size: {len(stocks_module.supported_symbols)}")
    print(f"Min Confidence: {stocks_config.min_confidence}")
    print(f"First 10 stocks: {stocks_module.supported_symbols[:10]}")
    
    # Test stock opportunities
    stock_opportunities = stocks_module.analyze_opportunities()
    print(f"\nStock Opportunities Found: {len(stock_opportunities)}")
    
    for i, opp in enumerate(stock_opportunities[:5]):  # Show first 5
        print(f"  {i+1}. {opp.symbol}: confidence={opp.confidence:.3f}, strategy={opp.strategy}")
        print(f"      action={opp.action}, qty={opp.quantity}, max_pos_size=${opp.max_position_size:.2f}")
        print(f"      technical={opp.technical_score:.2f}, stop_loss={opp.stop_loss_pct:.1%}")
    
    # Analysis Summary
    print(f"\n🎯 ANALYSIS SUMMARY:")
    print(f"  Crypto opportunities: {len(crypto_opportunities)}")
    print(f"  Stock opportunities: {len(stock_opportunities)}")
    print(f"  Total opportunities: {len(crypto_opportunities) + len(stock_opportunities)}")
    
    if len(crypto_opportunities) == 1 and crypto_opportunities[0].symbol == 'UNIUSD':
        print(f"  ❌ PROBLEM: Only UNIUSD crypto opportunity found!")
        
    if len(stock_opportunities) == 0:
        print(f"  ❌ PROBLEM: No stock opportunities found!")
        
    # Check individual crypto symbols
    print(f"\n🔍 INDIVIDUAL CRYPTO ANALYSIS:")
    for symbol in crypto_module.supported_symbols[:5]:  # Test first 5
        try:
            price = crypto_module._get_crypto_price(symbol)
            print(f"  {symbol}: price=${price:.2f}" if price else f"  {symbol}: price=N/A")
        except Exception as e:
            print(f"  {symbol}: ERROR - {e}")

except Exception as e:
    print(f"❌ Debug failed: {e}")
    import traceback
    traceback.print_exc()