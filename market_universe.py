#!/usr/bin/env python3
"""
Market Universe Definition
Expanded stock universe for enhanced trading analysis
"""

# NASDAQ-100 Top 50 Components (by market cap)
NASDAQ_TOP_50 = [
    # Mega-cap Technology
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA',
    
    # Large-cap Technology  
    'NFLX', 'ADBE', 'CRM', 'ORCL', 'AVGO', 'CSCO', 'INTC', 'AMD',
    'QCOM', 'TXN', 'INTU', 'AMAT', 'ADI', 'LRCX', 'KLAC', 'MRVL',
    
    # Consumer & Services
    'COST', 'SBUX', 'ABNB', 'BKNG', 'EBAY', 'PYPL', 'ZM', 'DOCU',
    
    # Healthcare & Biotech
    'JNJ', 'PFE', 'MRNA', 'GILD', 'AMGN', 'BIIB', 'REGN', 'VRTX',
    
    # Communication & Media
    'CMCSA', 'T', 'VZ', 'CHTR', 'NFLX', 'DIS',
    
    # Other Sectors
    'TSLA', 'PANW', 'SNPS', 'CDNS', 'FTNT', 'WDAY'
]

# Core ETFs for market regime detection
CORE_ETFS = [
    'SPY',   # S&P 500
    'QQQ',   # NASDAQ-100
    'IWM',   # Russell 2000 (Small Cap)
    'DIA',   # Dow Jones
    'VTI',   # Total Stock Market
    'XLK',   # Technology Sector
    'XLF',   # Financial Sector
    'XLE',   # Energy Sector
    'XLV',   # Healthcare Sector
    'XLP'    # Consumer Staples
]

# High-volume, liquid stocks for reliable data
HIGH_VOLUME_STOCKS = [
    'SPY', 'QQQ', 'IWM',  # ETFs
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',  # Mega-cap
    'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'QCOM',    # Large-cap tech
    'JPM', 'BAC', 'WFC', 'C',                                  # Banks
    'JNJ', 'PFE', 'UNH', 'CVX', 'XOM',                       # Diversified sectors
    'DIS', 'KO', 'PEP', 'WMT', 'HD'                          # Consumer
]

# Complete trading universe (prioritized list)
TRADING_UNIVERSE = {
    'tier_1_core': CORE_ETFS[:3],                    # SPY, QQQ, IWM - always monitor
    'tier_2_liquid': HIGH_VOLUME_STOCKS[:15],        # Most liquid stocks
    'tier_3_nasdaq': NASDAQ_TOP_50[:25],             # Top NASDAQ stocks
    'tier_4_extended': NASDAQ_TOP_50[25:] + ['VTI', 'DIA', 'XLK', 'XLF']  # Extended universe
}

def get_symbols_by_tier(tier_level=1):
    """Get symbols by tier level (1=most important, 4=extended)"""
    if tier_level == 1:
        return TRADING_UNIVERSE['tier_1_core']
    elif tier_level == 2:
        return TRADING_UNIVERSE['tier_1_core'] + TRADING_UNIVERSE['tier_2_liquid']
    elif tier_level == 3:
        return (TRADING_UNIVERSE['tier_1_core'] + 
                TRADING_UNIVERSE['tier_2_liquid'] + 
                TRADING_UNIVERSE['tier_3_nasdaq'])
    elif tier_level == 4:
        # All symbols combined (remove duplicates)
        all_symbols = []
        for tier in TRADING_UNIVERSE.values():
            all_symbols.extend(tier)
        return list(set(all_symbols))  # Remove duplicates
    else:
        return TRADING_UNIVERSE['tier_1_core']

def get_sector_symbols():
    """Get symbols organized by sector"""
    return {
        'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM', 'ORCL'],
        'finance': ['JPM', 'BAC', 'WFC', 'C', 'XLF'],
        'healthcare': ['JNJ', 'PFE', 'UNH', 'XLV'],
        'energy': ['CVX', 'XOM', 'XLE'],
        'consumer': ['DIS', 'KO', 'PEP', 'WMT', 'HD', 'XLP'],
        'etfs': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI']
    }

def validate_symbol_availability(api_client, symbols, max_test=10):
    """Test symbol availability and data quality"""
    available_symbols = []
    failed_symbols = []
    
    # Test up to max_test symbols
    test_symbols = symbols[:max_test]
    
    for symbol in test_symbols:
        try:
            quote = api_client.get_latest_quote(symbol)
            if quote and quote.ask_price and quote.ask_price > 0:
                available_symbols.append(symbol)
            else:
                failed_symbols.append(symbol)
        except Exception as e:
            failed_symbols.append(symbol)
    
    success_rate = len(available_symbols) / len(test_symbols) if test_symbols else 0
    
    return {
        'available_symbols': available_symbols,
        'failed_symbols': failed_symbols,
        'success_rate': success_rate,
        'total_tested': len(test_symbols)
    }

# Test the market universe
def test_market_universe():
    """Test market universe functionality"""
    print("🧪 Testing Market Universe...")
    
    # Test tier access
    tier1 = get_symbols_by_tier(1)
    tier2 = get_symbols_by_tier(2)
    tier3 = get_symbols_by_tier(3)
    tier4 = get_symbols_by_tier(4)
    
    print(f"✅ Tier 1 (Core): {len(tier1)} symbols - {tier1}")
    print(f"✅ Tier 2 (Liquid): {len(tier2)} symbols")
    print(f"✅ Tier 3 (NASDAQ): {len(tier3)} symbols")
    print(f"✅ Tier 4 (All): {len(tier4)} symbols")
    
    # Test sector organization
    sectors = get_sector_symbols()
    print(f"✅ Sectors: {list(sectors.keys())}")
    
    # Verify no duplicates in tier 4
    tier4_unique = list(set(tier4))
    print(f"✅ Tier 4 unique check: {len(tier4)} -> {len(tier4_unique)} symbols")
    
    print("🎉 Market universe tests completed!")
    
    return tier1, tier2, tier3, tier4

if __name__ == "__main__":
    test_market_universe()