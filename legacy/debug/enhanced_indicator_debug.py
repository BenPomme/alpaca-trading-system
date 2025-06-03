#!/usr/bin/env python3
"""Enhanced debugging for technical indicators with detailed logging"""

import logging

def debug_indicator_requirements():
    """Debug what data requirements each indicator has"""
    
    print("📊 TECHNICAL INDICATOR DATA REQUIREMENTS")
    print("="*60)
    
    requirements = {
        'RSI': {
            'min_periods': 14,
            'calculation': '14-period gains/losses average',
            'formula': 'RSI = 100 - (100 / (1 + RS))',
            'typical_timeframe': '14 hours for hourly data'
        },
        'MACD': {
            'min_periods': 26,
            'fallback_periods': 21,
            'calculation': 'EMA(12) - EMA(26)',
            'formula': 'MACD Line = EMA(12) - EMA(26)',
            'typical_timeframe': '26 hours for hourly data'
        },
        'Bollinger Bands': {
            'min_periods': 20,
            'calculation': '20-period SMA ± 2*StdDev',
            'formula': 'Upper = SMA(20) + 2*σ, Lower = SMA(20) - 2*σ',
            'typical_timeframe': '20 hours for hourly data'
        },
        'Volume': {
            'min_periods': 1,
            'calculation': 'Current volume vs historical average',
            'formula': 'Volume Ratio = Current / Average',
            'typical_timeframe': 'Any period with volume data'
        }
    }
    
    for indicator, req in requirements.items():
        print(f"\n{indicator}:")
        print(f"  Minimum periods: {req['min_periods']}")
        if 'fallback_periods' in req:
            print(f"  Fallback periods: {req['fallback_periods']}")
        print(f"  Calculation: {req['calculation']}")
        print(f"  Formula: {req['formula']}")
        print(f"  Timeframe: {req['typical_timeframe']}")

def debug_potential_failure_modes():
    """Debug potential reasons why indicators might fail"""
    
    print(f"\n📋 POTENTIAL FAILURE MODES")
    print("="*60)
    
    failure_modes = [
        {
            'category': 'Insufficient Data',
            'issues': [
                'API returns less than required bars (e.g., only 10 instead of 26)',
                'Market closed periods reduce available data',
                'Weekend gaps in crypto data',
                'New trading pairs with limited history'
            ]
        },
        {
            'category': 'Data Quality Issues',
            'issues': [
                'Bars with zero volume',
                'Missing close prices',
                'Invalid price values (negative, NaN)',
                'Timestamp inconsistencies'
            ]
        },
        {
            'category': 'API Response Issues',
            'issues': [
                'Network timeouts during data fetch',
                'Rate limiting from Alpaca API',
                'Authentication failures',
                'Malformed response data'
            ]
        },
        {
            'category': 'Code Logic Issues',
            'issues': [
                'Exception in calculation logic',
                'Division by zero in RSI/MACD',
                'Math domain errors (sqrt of negative)',
                'Type conversion failures'
            ]
        }
    ]
    
    for mode in failure_modes:
        print(f"\n{mode['category']}:")
        for issue in mode['issues']:
            print(f"  • {issue}")

def debug_logging_recommendations():
    """Provide recommendations for better debugging"""
    
    print(f"\n🔧 DEBUGGING RECOMMENDATIONS")
    print("="*60)
    
    recommendations = [
        "Add data quantity logging: 'Retrieved X bars for Y symbol'",
        "Log price data ranges: 'Prices: $X.XX - $X.XX over N periods'",
        "Log volume data quality: 'Volume range: X - X over N periods'",
        "Add timing logs: 'API call took X.Xs, returned Y bars'",
        "Log intermediate calculations: 'EMA(12)=X, EMA(26)=Y, MACD=Z'",
        "Add exception logging in each indicator method",
        "Log data age: 'Oldest bar: X hours ago, newest: Y hours ago'",
        "Add calculation step logging for failed indicators"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

def debug_enhanced_logging_code():
    """Provide enhanced logging code suggestions"""
    
    print(f"\n💻 ENHANCED LOGGING CODE SUGGESTIONS")
    print("="*60)
    
    suggestions = """
# Enhanced market data logging
def _get_crypto_market_data_with_debug(self, symbol: str) -> Optional[Dict]:
    try:
        # Log API request
        self.logger.info(f"🔍 {symbol}: Requesting 30 hours of data...")
        
        bars = self.api.get_crypto_bars(...)
        
        if bars and len(bars) > 0:
            prices = [float(bar.c) for bar in bars]
            volumes = [float(bar.v) for bar in bars]
            
            # ENHANCED LOGGING
            self.logger.info(f"📊 {symbol}: Retrieved {len(bars)} bars")
            self.logger.info(f"💰 {symbol}: Price range ${min(prices):.4f} - ${max(prices):.4f}")
            self.logger.info(f"📈 {symbol}: Volume range {min(volumes):,.0f} - {max(volumes):,.0f}")
            
            # Check requirements
            if len(prices) < 14:
                self.logger.error(f"❌ {symbol}: RSI requires 14+ bars, got {len(prices)}")
            if len(prices) < 20:
                self.logger.error(f"❌ {symbol}: Bollinger requires 20+ bars, got {len(prices)}")
            if len(prices) < 26:
                self.logger.warning(f"⚠️ {symbol}: MACD requires 26+ bars, got {len(prices)} (fallback available)")
                
        return market_data
        
    except Exception as e:
        self.logger.error(f"❌ {symbol}: Market data fetch failed: {e}")
        return None

# Enhanced indicator logging
def _calculate_rsi_signals_with_debug(self, symbol: str, market_data: Dict) -> Optional[Dict]:
    try:
        prices = market_data.get('price_history', [])
        self.logger.debug(f"🔍 {symbol}: RSI calculation with {len(prices)} prices")
        
        if len(prices) < 14:
            self.logger.error(f"❌ {symbol}: RSI needs 14+ prices, got {len(prices)}")
            return None
            
        # Log calculation steps
        price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [change if change > 0 else 0 for change in price_changes]
        losses = [-change if change < 0 else 0 for change in price_changes]
        
        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14
        
        self.logger.debug(f"📊 {symbol}: RSI avg_gain={avg_gain:.4f}, avg_loss={avg_loss:.4f}")
        
        if avg_loss == 0:
            rsi = 100
            self.logger.debug(f"📊 {symbol}: RSI=100 (no losses)")
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            self.logger.debug(f"📊 {symbol}: RSI={rsi:.2f} (RS={rs:.4f})")
            
        return {'rsi_value': rsi, ...}
        
    except Exception as e:
        self.logger.error(f"❌ {symbol}: RSI calculation failed: {e}")
        import traceback
        self.logger.error(f"❌ {symbol}: RSI traceback: {traceback.format_exc()}")
        return None
"""
    
    print(suggestions)

if __name__ == '__main__':
    debug_indicator_requirements()
    debug_potential_failure_modes()
    debug_logging_recommendations()
    debug_enhanced_logging_code()
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Deploy the fixes for technical_confidence variable")
    print("2. Add enhanced logging to identify root cause of None indicators")
    print("3. Monitor production logs for specific data/calculation failures")
    print("4. Run system with DEBUG level logging to capture detailed flow")
    print("="*60)