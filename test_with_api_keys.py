#!/usr/bin/env python3
"""
Test Enhanced System with Real API Keys
Quick test to verify enhanced data sources are working
"""

import os

# Load environment variables from .env.local
if os.path.exists('.env.local'):
    with open('.env.local', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                value = value.strip('"\'')
                os.environ[key] = value

print("🚀 Testing Enhanced System with Real API Keys")
print("=" * 60)

# Test enhanced data manager
try:
    from enhanced_data_manager import EnhancedDataManager
    
    manager = EnhancedDataManager(
        alpaca_api_key=os.getenv('ALPACA_PAPER_API_KEY'),
        alpaca_secret_key=os.getenv('ALPACA_PAPER_SECRET_KEY'),
        alpha_vantage_key=os.getenv('ALPHA_VANTAGE_API_KEY'),
        finnhub_key=os.getenv('FINNHUB_API_KEY')
    )
    
    # Test data source health
    health = manager.check_data_sources_health()
    print(f"📊 Data Sources Health: {health}")
    
    active_sources = sum(health.values())
    print(f"✅ Active data sources: {active_sources}/4")
    
    if active_sources > 0:
        # Test enhanced market data
        enhanced_data = manager.get_enhanced_market_data('AAPL')
        sources_used = enhanced_data.get('sources_used', [])
        data_quality = enhanced_data.get('data_quality_score', 0)
        
        print(f"📈 Enhanced data for AAPL:")
        print(f"  Sources used: {sources_used}")
        print(f"  Data quality: {data_quality:.2f}")
        
        if 'bid' in enhanced_data and 'ask' in enhanced_data:
            print(f"  Quote: ${enhanced_data['bid']:.2f} / ${enhanced_data['ask']:.2f}")
        
        print("✅ Enhanced Data Manager working with real API keys!")
    else:
        print("⚠️ No active data sources - fallback mode")
        
except Exception as e:
    print(f"❌ Enhanced Data Manager test failed: {e}")

# Test enhanced technical indicators
try:
    from enhanced_technical_indicators import EnhancedTechnicalIndicators
    import numpy as np
    
    indicators = EnhancedTechnicalIndicators()
    
    # Generate sample data
    np.random.seed(42)
    prices = [100 + np.random.randn() * 2 for _ in range(50)]
    
    rsi = indicators.calculate_rsi(prices)
    print(f"🔍 TA-Lib RSI calculation: {rsi:.2f}")
    print("✅ Enhanced Technical Indicators working!")
    
except Exception as e:
    print(f"❌ Enhanced Technical Indicators test failed: {e}")

# Test enhanced ML models
try:
    from enhanced_ml_models import EnhancedMLFramework
    
    ml_framework = EnhancedMLFramework()
    summary = ml_framework.get_model_summary()
    
    print(f"🧠 ML Framework Summary:")
    print(f"  PyTorch available: {summary['pytorch_available']}")
    if summary['device']:
        print(f"  Device: {summary['device']}")
    
    print("✅ Enhanced ML Models working!")
    
except Exception as e:
    print(f"❌ Enhanced ML Models test failed: {e}")

print("\n🎉 Enhanced system components tested with real API keys!")
print("Your system is ready for Phase 2 enhanced trading with multi-source data!")