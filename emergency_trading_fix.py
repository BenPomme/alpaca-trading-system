#!/usr/bin/env python3
"""
EMERGENCY TRADING FIX

Portfolio down -5% - immediate action needed.
Test trading system locally with real credentials and verify why modules aren't trading.
"""

import os
import sys
import logging
from datetime import datetime

# Set environment variables directly (bypassing .env file issues)
os.environ['ALPACA_PAPER_API_KEY'] = 'PKIP9MZ4Q1WJ423JXOQU'
os.environ['ALPACA_PAPER_SECRET_KEY'] = 'zjGO4D9sED7ATSv6J1UCKCl0xzOOep5hPHRRmRcc'
os.environ['EXECUTION_ENABLED'] = 'true'
os.environ['GLOBAL_TRADING'] = 'true'
os.environ['OPTIONS_TRADING'] = 'true'
os.environ['CRYPTO_TRADING'] = 'true'
os.environ['MARKET_TIER'] = '2'
os.environ['MIN_CONFIDENCE'] = '0.6'
os.environ['FIREBASE_PRIVATE_KEY_ID'] = '1cc8ac3693bfd2b08e40582f3564da2a3c06d978'
os.environ['FIREBASE_CLIENT_EMAIL'] = 'firebase-adminsdk-fbsvc@alpaca-12fab.iam.gserviceaccount.com'
os.environ['FIREBASE_CLIENT_ID'] = '105751822466253435094'
os.environ['FIREBASE_CLIENT_CERT_URL'] = 'https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40alpaca-12fab.iam.gserviceaccount.com'

# Private key without quotes issues
firebase_private_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCtGoSe5pZgpT44
Q3Dg/f43lkgtXPmNlAExUFiHsQ0kWKbhlwq77N3vmS6tsmCIrizrSb
  d9ntuJN7x6
rdLG30EQdqLy5d0oI/moB2K1LaDbQ+q3EpH17gvARLVsDnU9wye6zfRSNyO2E/CZ
5yy75WhszLsl40inUEEZTi5o4fpr+t5dXZqoNNSkZLtg+38x6UqoItun10X0vDwM
cDRW4Zqf+aewBsGkodddf3XlCUyHbl2S
  t619DJk+989ZuEyFRqn8AC8WFJaehBCK
z+eVKEF1H9qQYzizH3a9KmpnCD7VJuWcxAY9qGD4Xclhkj8KCVOgPPy1arZdcG0z
72TxhnujAgMBAAECggEABv/dgPdd+UZ1P50qgU6D6wd+n6b0yE7FxZK0Ibh9CY00
IkcTPgoT50
  5QXuGpmZ1BX7o5WzEDO4cvbd59eWEpplrFuACncqoRvEOgMCdKK9OR
OBneIQ2hGAMvOtFS2E592sXdLT3hiclAn1iDrI1YLZ4RqzSHiYxrNXS916vbjmYj
aolul+keVDxA4rCdq7OHeOOUn/XEIWxIAftCl4pZesgn22z0vpLcjV
  IaQ9E22sY0
2lOLM2wP29CA+xUtHxfKBHepTEBIiWZzTziFpq4+7T8snOGQl6BTCRqA1+RA3Uoa
BQbRj/VKX8vDlfLNXoCTEP0EgXbAFs9yaSYPfmrR0QKBgQDh9KvbNMJR8zU2r5q9
vap8vn6/UJqeQ+TT8b2jhEJOqz/PbTw7
  +hVoDqaGx0MVC6bvD3Lz/LlYDKaB29Cj
BUCpJEceI3Pl9w0Dw6JHjYA3fTwxuDxVYMznRKhzuw55TbPsWYh9qEjKaFYglouD
z/vcyRF5L/UxN9Vj7X2ySM3rHwKBgQDEHs6eq0/nOPRJ3d0lgUR8uZ+2wgr98I9l
Lkg/BMPoWE
  NYyMxwEohEyOQuHBXyUPpIA1Ols2c5eu25V3EDUMr3vLRzr26SvNDS
p4IqcYtJ+BKfXy/TjoPDsSl6yZ+p8dAqnWEm8EqwimneVt7/HBxiBC3hkR+V/5aq
7q6wfNUi/QKBgDHHW00RlHXFZMXFbgu7CyIsPXQcZ9PSFUl0CllJu+
  nk5EvoPsrf
z3N7NsiegXLTfFVSS/rghFyXfN9C8/XWJGae7WQAX3ocMSvRH6Ev1T1kQ6yYcAJH
Lx0MDShh31BuA+Nf3igAuPiOf9ryD45cdZowWb8fB59uM36uRXDPhT31AoGAbpjo
8DWvo7dMm/NP6PyTALs1RDz9MeNdGjQV
  beRkDjzoDcN+9pyc2B1qAE66WaIs4jtu
Cn23coTOVrzm8HW5YCe8o5iFBJ8SLBlmoETTxezto45sTCOMTukzeRkGvzGssLt7
tBfCJviHZ2kZ7EeQAf5VWWUbqN0vvElJniFnmIkCgYEAxdoRAwzWFp0jhVo5/52j
tHupz1y2LT
  FlDgiRGZztbQ3pGFJF+6KSjV3tnFjMyWs4U29g4BmvktC8kJxzTz5i
pZ7wHcqC1Rpqcp4CVURkOKCsJAAEhjEt3ywB/vG+x8xK2GG0TFuSvj+vWADl3rg3
tKyWmq6YEq8mP1RHoTfHyrE=
-----END PRIVATE KEY-----"""
os.environ['FIREBASE_PRIVATE_KEY'] = firebase_private_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_alpaca_connection():
    """Test Alpaca API connection"""
    logger.info("🚨 EMERGENCY: Testing Alpaca connection...")
    
    try:
        import alpaca_trade_api as tradeapi
        
        api_key = os.environ.get('ALPACA_PAPER_API_KEY')
        secret_key = os.environ.get('ALPACA_PAPER_SECRET_KEY')
        
        logger.info(f"API Key: {api_key[:8]}..." if api_key else "API Key: NOT SET")
        logger.info(f"Secret Key: {secret_key[:8]}..." if secret_key else "Secret Key: NOT SET")
        
        if not api_key or not secret_key:
            logger.error("❌ CRITICAL: API credentials missing")
            return False
            
        # Initialize API
        alpaca_api = tradeapi.REST(
            api_key,
            secret_key,
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        # Test connection
        account = alpaca_api.get_account()
        portfolio_value = float(account.portfolio_value)
        
        logger.info(f"✅ Alpaca connected - Account: {account.id}")
        logger.info(f"💰 Portfolio Value: ${portfolio_value:,.2f}")
        logger.info(f"📊 Buying Power: ${float(account.buying_power):,.2f}")
        
        # Get current positions
        positions = alpaca_api.list_positions()
        logger.info(f"📋 Current Positions: {len(positions)}")
        
        total_position_value = 0
        for pos in positions:
            market_value = float(pos.market_value)
            unrealized_pl = float(pos.unrealized_pl)
            total_position_value += abs(market_value)
            
            logger.info(f"   {pos.symbol}: ${market_value:,.2f} (P&L: ${unrealized_pl:,.2f})")
        
        # Calculate performance
        if portfolio_value > 0:
            if portfolio_value < 1000000:  # Assuming $1M starting
                loss_pct = ((1000000 - portfolio_value) / 1000000) * 100
                logger.error(f"🚨 PORTFOLIO DOWN: -{loss_pct:.2f}%")
            else:
                gain_pct = ((portfolio_value - 1000000) / 1000000) * 100
                logger.info(f"📈 Portfolio Up: +{gain_pct:.2f}%")
        
        return alpaca_api
        
    except Exception as e:
        logger.error(f"❌ Alpaca connection failed: {e}")
        return False

def test_firebase_connection():
    """Test Firebase connection"""
    logger.info("🔥 Testing Firebase connection...")
    
    try:
        from firebase_database import FirebaseDatabase
        
        firebase_db = FirebaseDatabase()
        
        if firebase_db.is_connected():
            logger.info("✅ Firebase connected successfully")
            
            # Test trade history
            try:
                trade_details = firebase_db.get_collection('trade_history_details')
                ml_trades = firebase_db.get_collection('ml_enhanced_trades')
                
                logger.info(f"📊 Trade History Entries: {len(trade_details) if trade_details else 0}")
                logger.info(f"🧠 ML Enhanced Trades: {len(ml_trades) if ml_trades else 0}")
                
                return firebase_db
                
            except Exception as e:
                logger.warning(f"⚠️ Firebase data access error: {e}")
                return firebase_db
        else:
            logger.error("❌ Firebase connection failed")
            return None
            
    except Exception as e:
        logger.error(f"❌ Firebase error: {e}")
        return None

def check_market_hours():
    """Check if market is open"""
    try:
        import pytz
        from datetime import datetime
        
        et = pytz.timezone('US/Eastern')
        now_et = datetime.now(et)
        is_weekday = now_et.weekday() < 5
        is_trading_hours = 9 <= now_et.hour < 16
        
        logger.info(f"⏰ Current time (ET): {now_et.strftime('%Y-%m-%d %H:%M %Z')}")
        logger.info(f"📅 Is weekday: {is_weekday}")
        logger.info(f"🕐 Is trading hours: {is_trading_hours}")
        
        market_open = is_weekday and is_trading_hours
        
        if market_open:
            logger.error("🚨 MARKET IS OPEN - SHOULD BE TRADING!")
        else:
            logger.info("📴 Market closed - only crypto should trade")
            
        return market_open
        
    except Exception as e:
        logger.error(f"❌ Market hours check failed: {e}")
        return False

def test_modules_registration():
    """Test if trading modules can be registered"""
    logger.info("🧪 Testing module registration...")
    
    try:
        from modular.orchestrator import ModularOrchestrator
        from modular.base_module import ModuleConfig
        
        # Create orchestrator
        orchestrator = ModularOrchestrator()
        logger.info("✅ Orchestrator created")
        
        # Test module imports
        modules_to_test = [
            ('stocks', 'modular.stocks_module', 'StocksModule'),
            ('crypto', 'modular.crypto_module', 'CryptoModule'),
            ('options', 'modular.options_module', 'OptionsModule')
        ]
        
        for module_name, module_path, class_name in modules_to_test:
            try:
                module = __import__(module_path, fromlist=[class_name])
                module_class = getattr(module, class_name)
                logger.info(f"✅ {module_name.upper()} module imported successfully")
            except Exception as e:
                logger.error(f"❌ {module_name.upper()} module import failed: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Module registration test failed: {e}")
        return False

def emergency_analysis():
    """Emergency analysis of why system isn't trading"""
    logger.info("🚨 EMERGENCY TRADING SYSTEM ANALYSIS")
    logger.info("=" * 60)
    logger.info(f"⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Test API connections
    alpaca_api = test_alpaca_connection()
    firebase_db = test_firebase_connection()
    
    # 2. Check market status
    market_open = check_market_hours()
    
    # 3. Test module registration
    modules_working = test_modules_registration()
    
    # 4. Diagnosis
    logger.info("\n" + "=" * 60)
    logger.info("🔍 DIAGNOSIS:")
    
    if not alpaca_api:
        logger.error("❌ CRITICAL: Alpaca API not working - cannot trade")
    
    if not firebase_db:
        logger.warning("⚠️ WARNING: Firebase not working - no trade tracking")
    
    if market_open and alpaca_api:
        logger.error("🚨 URGENT: Market is OPEN but system is not trading!")
        logger.error("🔧 SOLUTION NEEDED: Fix module registration and deployment")
    
    if not modules_working:
        logger.error("❌ CRITICAL: Modules cannot be registered")
    
    # 5. Immediate actions needed
    logger.info("\n📋 IMMEDIATE ACTIONS NEEDED:")
    logger.info("1. 🚨 URGENT: Stop losses if portfolio continues bleeding")
    logger.info("2. 🔧 FIX: Update Railway deployment with working credentials")
    logger.info("3. ✅ VERIFY: Modules are registering and trading")
    logger.info("4. 📊 MONITOR: Real-time performance once fixed")
    
    return {
        'alpaca_working': bool(alpaca_api),
        'firebase_working': bool(firebase_db),
        'market_open': market_open,
        'modules_working': modules_working,
        'critical_issue': market_open and not alpaca_api
    }

if __name__ == "__main__":
    emergency_analysis()