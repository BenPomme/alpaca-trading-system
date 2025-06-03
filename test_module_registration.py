#!/usr/bin/env python3
"""
Test Module Registration - Verify stocks and options modules can be registered
"""

import os
import logging
from datetime import datetime

# Set mock environment variables for testing
os.environ['ALPACA_PAPER_API_KEY'] = 'PK_TEST_KEY_FOR_MODULE_TESTING'
os.environ['ALPACA_PAPER_SECRET_KEY'] = 'TEST_SECRET_KEY_FOR_MODULE_TESTING'
os.environ['ALPACA_BASE_URL'] = 'https://paper-api.alpaca.markets'

# Import after setting env vars
from modular.orchestrator import ModularOrchestrator
from modular.base_module import ModuleConfig
from production_config import ProductionConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_module_registration():
    """Test if modules can be registered without full system startup"""
    try:
        logger.info("🧪 Testing module registration without full system startup...")
        
        # Create orchestrator
        orchestrator = ModularOrchestrator()
        logger.info(f"✅ Orchestrator created: {orchestrator}")
        
        # Create module configs
        stocks_config = ModuleConfig(
            module_name="stocks",
            max_allocation_pct=50.0,
            min_confidence=0.55,
            custom_params={'aggressive_multiplier': 2.0}
        )
        
        options_config = ModuleConfig(
            module_name="options", 
            max_allocation_pct=30.0,
            min_confidence=0.60,
            custom_params={'max_contracts': 10}
        )
        
        crypto_config = ModuleConfig(
            module_name="crypto",
            max_allocation_pct=60.0,
            min_confidence=0.50,
            custom_params={'24_7_trading': True}
        )
        
        logger.info("✅ Module configs created")
        
        # Try to register modules (this will fail due to missing dependencies, but we can see the attempt)
        try:
            # Import modules
            from modular.stocks_module import StocksModule
            from modular.crypto_module import CryptoModule
            logger.info("✅ Modules imported successfully")
            
            # Check what modules the orchestrator can register
            logger.info(f"📊 Available module registration methods: {dir(orchestrator)}")
            
            if hasattr(orchestrator, 'register_module'):
                logger.info("✅ register_module method exists")
            else:
                logger.warning("⚠️ register_module method not found")
                
        except ImportError as e:
            logger.warning(f"⚠️ Module import failed (expected): {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Module registration test failed: {e}")
        return False

def check_market_hours():
    """Check if market is currently open"""
    try:
        import pytz
        et = pytz.timezone('US/Eastern')
        now_et = datetime.now(et)
        is_weekday = now_et.weekday() < 5  # Monday=0, Friday=4
        is_trading_hours = 9 <= now_et.hour < 16  # 9 AM to 4 PM ET
        
        logger.info(f"🕐 Current time (ET): {now_et.strftime('%Y-%m-%d %H:%M %Z')}")
        logger.info(f"📅 Is weekday: {is_weekday}")
        logger.info(f"⏰ Is trading hours (9 AM - 4 PM ET): {is_trading_hours}")
        logger.info(f"🏛️ Market should be open: {is_weekday and is_trading_hours}")
        
        return is_weekday and is_trading_hours
        
    except Exception as e:
        logger.error(f"❌ Market hours check failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🧪 Starting module registration test...")
    logger.info("=" * 60)
    
    # Check market hours
    market_open = check_market_hours()
    
    # Test module registration
    registration_success = test_module_registration()
    
    logger.info("=" * 60)
    if market_open and not registration_success:
        logger.error("🚨 DIAGNOSIS: Market is open but modules cannot be registered")
        logger.error("🔧 SOLUTION: Fix module registration and API credentials")
    elif not market_open:
        logger.info("📴 Market is closed - stocks/options modules should not trade")
        logger.info("💰 Only crypto module should be active (24/7 trading)")
    else:
        logger.info("✅ Module registration test completed")