#!/usr/bin/env python3
"""
CRITICAL SYSTEM AUDIT - Live Data Analysis
Connect to real Alpaca account and Firebase to audit actual system state
"""

import os
import alpaca_trade_api as tradeapi
import json
from datetime import datetime, timedelta
import pandas as pd

# Set environment variables for connection
os.environ['ALPACA_PAPER_API_KEY'] = "PKOBXG3RWCRQTXH6ID0L"
os.environ['ALPACA_PAPER_SECRET_KEY'] = "8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn"
os.environ['ALPACA_BASE_URL'] = "https://paper-api.alpaca.markets"

def audit_alpaca_account():
    """Connect to Alpaca and get real account data"""
    print("🔍 CONNECTING TO ALPACA ACCOUNT...")
    
    try:
        api = tradeapi.REST(
            os.environ['ALPACA_PAPER_API_KEY'],
            os.environ['ALPACA_PAPER_SECRET_KEY'],
            os.environ['ALPACA_BASE_URL'],
            api_version='v2'
        )
        
        # Get account info
        account = api.get_account()
        print(f"✅ Connected to account: {account.id}")
        print(f"💰 Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"💵 Cash: ${float(account.cash):,.2f}")
        print(f"🏦 Buying Power: ${float(account.buying_power):,.2f}")
        print(f"📊 Day Trading Buying Power: ${float(account.daytrading_buying_power):,.2f}")
        print(f"📈 Equity: ${float(account.equity):,.2f}")
        print(f"📉 P&L Today: ${float(account.unrealized_pl):,.2f}")
        
        # Get positions
        positions = api.list_positions()
        print(f"\n📊 CURRENT POSITIONS ({len(positions)} total):")
        
        total_unrealized_pl = 0
        crypto_value = 0
        stock_value = 0
        
        position_data = []
        
        for pos in positions:
            unrealized_pl = float(pos.unrealized_pl)
            market_value = float(pos.market_value)
            total_unrealized_pl += unrealized_pl
            
            # Categorize positions
            if 'USD' in pos.symbol and len(pos.symbol) <= 7:  # Crypto symbols like BTCUSD
                crypto_value += market_value
            else:
                stock_value += market_value
            
            position_data.append({
                'symbol': pos.symbol,
                'qty': float(pos.qty),
                'market_value': market_value,
                'unrealized_pl': unrealized_pl,
                'unrealized_plpc': float(pos.unrealized_plpc) * 100,
                'avg_entry_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price)
            })
            
            print(f"  {pos.symbol}: {pos.qty} shares, ${market_value:,.2f} value, "
                  f"${unrealized_pl:+.2f} P&L ({float(pos.unrealized_plpc)*100:+.1f}%)")
        
        portfolio_value = float(account.portfolio_value)
        crypto_allocation = (crypto_value / portfolio_value) * 100 if portfolio_value > 0 else 0
        stock_allocation = (stock_value / portfolio_value) * 100 if portfolio_value > 0 else 0
        
        print(f"\n📊 ALLOCATION ANALYSIS:")
        print(f"  💰 Total Portfolio: ${portfolio_value:,.2f}")
        print(f"  ₿ Crypto Value: ${crypto_value:,.2f} ({crypto_allocation:.1f}%)")
        print(f"  📈 Stock Value: ${stock_value:,.2f} ({stock_allocation:.1f}%)")
        print(f"  💸 Total Unrealized P&L: ${total_unrealized_pl:+,.2f}")
        
        # Get recent orders
        print(f"\n📋 RECENT ORDERS (last 7 days):")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        try:
            orders = api.list_orders(
                status='all',
                after=start_date.isoformat(),
                limit=50
            )
            
            executed_orders = [o for o in orders if o.status == 'filled']
            pending_orders = [o for o in orders if o.status in ['new', 'partially_filled', 'pending_new']]
            rejected_orders = [o for o in orders if o.status in ['rejected', 'cancelled']]
            
            print(f"  ✅ Executed: {len(executed_orders)}")
            print(f"  ⏳ Pending: {len(pending_orders)}")
            print(f"  ❌ Rejected/Cancelled: {len(rejected_orders)}")
            
            # Show recent executed orders
            print(f"\n📈 LAST 10 EXECUTED ORDERS:")
            for order in executed_orders[:10]:
                print(f"  {order.submitted_at[:10]} {order.side} {order.qty} {order.symbol} @ ${float(order.filled_avg_price or 0):.2f}")
                
        except Exception as e:
            print(f"❌ Error getting orders: {e}")
        
        return {
            'account': account,
            'positions': position_data,
            'portfolio_value': portfolio_value,
            'crypto_allocation': crypto_allocation,
            'stock_allocation': stock_allocation,
            'total_unrealized_pl': total_unrealized_pl,
            'executed_orders_count': len(executed_orders) if 'executed_orders' in locals() else 0
        }
        
    except Exception as e:
        print(f"❌ ALPACA CONNECTION FAILED: {e}")
        return None

def analyze_performance_trends():
    """Analyze recent trading performance"""
    print("\n🔍 ANALYZING PERFORMANCE TRENDS...")
    
    try:
        # Try to read local performance data
        files_to_check = [
            'data/cloud_trading_data.json',
            'trading_data.json',
            'performance_data.json'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                print(f"📊 Reading {file_path}...")
                with open(file_path, 'r') as f:
                    data = json.load(f)
                print(f"  Found {len(data)} records")
                
                # Analyze data structure
                if isinstance(data, list) and len(data) > 0:
                    sample = data[0]
                    print(f"  Sample record keys: {list(sample.keys())}")
                    
                    # Look for profit/loss data
                    profit_fields = [k for k in sample.keys() if 'profit' in k.lower() or 'pnl' in k.lower() or 'pl' in k.lower()]
                    if profit_fields:
                        print(f"  Profit fields found: {profit_fields}")
                        
                        # Calculate basic stats
                        total_pnl = sum(float(record.get(profit_fields[0], 0)) for record in data)
                        profitable_trades = sum(1 for record in data if float(record.get(profit_fields[0], 0)) > 0)
                        total_trades = len(data)
                        win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0
                        
                        print(f"  📊 Total P&L: ${total_pnl:.2f}")
                        print(f"  🎯 Win Rate: {win_rate:.1f}% ({profitable_trades}/{total_trades})")
                    
                break
        else:
            print("❌ No local performance data found")
            
    except Exception as e:
        print(f"❌ Error analyzing performance: {e}")

def test_firebase_connection():
    """Test Firebase connection with provided credentials"""
    print("\n🔥 TESTING FIREBASE CONNECTION...")
    
    try:
        # Set Firebase environment variables
        os.environ['FIREBASE_PRIVATE_KEY_ID'] = "1cc8ac3693bfd2b08e40582f3564da2a3c06d978"
        os.environ['FIREBASE_PRIVATE_KEY'] = """-----BEGIN PRIVATE KEY-----
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
        os.environ['FIREBASE_CLIENT_EMAIL'] = "firebase-adminsdk-fbsvc@alpaca-12fab.iam.gserviceaccount.com"
        os.environ['FIREBASE_CLIENT_ID'] = "105751822466253435094"
        os.environ['FIREBASE_CLIENT_CERT_URL'] = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40alpaca-12fab.iam.gserviceaccount.com"
        
        # Try to connect
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            # Check if already initialized
            try:
                firebase_admin.get_app()
                print("✅ Firebase already initialized")
            except ValueError:
                # Initialize Firebase
                cred_dict = {
                    "type": "service_account",
                    "project_id": "alpaca-12fab",
                    "private_key_id": os.environ['FIREBASE_PRIVATE_KEY_ID'],
                    "private_key": os.environ['FIREBASE_PRIVATE_KEY'].replace('\\n', '\n'),
                    "client_email": os.environ['FIREBASE_CLIENT_EMAIL'],
                    "client_id": os.environ['FIREBASE_CLIENT_ID'],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.environ['FIREBASE_CLIENT_CERT_URL']
                }
                
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized successfully")
            
            # Test connection
            db = firestore.client()
            
            # Try to read some data
            collections = ['trades', 'performance', 'ml_data', 'trading_opportunities']
            for collection_name in collections:
                try:
                    collection_ref = db.collection(collection_name)
                    docs = list(collection_ref.limit(5).stream())
                    print(f"  📊 Collection '{collection_name}': {len(docs)} documents (showing first 5)")
                    
                    if docs:
                        # Show sample document structure
                        sample_doc = docs[0]
                        print(f"    Sample doc keys: {list(sample_doc.to_dict().keys())}")
                        
                except Exception as e:
                    print(f"  ❌ Error accessing '{collection_name}': {e}")
            
            return True
            
        except ImportError:
            print("❌ Firebase Admin SDK not installed")
            return False
        except Exception as e:
            print(f"❌ Firebase connection error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Firebase setup error: {e}")
        return False

def main():
    """Main audit function"""
    print("🚨 CRITICAL TRADING SYSTEM AUDIT - LIVE DATA ANALYSIS")
    print("=" * 60)
    
    # 1. Audit Alpaca account
    alpaca_data = audit_alpaca_account()
    
    # 2. Analyze performance trends
    analyze_performance_trends()
    
    # 3. Test Firebase connection
    firebase_connected = test_firebase_connection()
    
    # 4. Generate audit summary
    print("\n" + "=" * 60)
    print("📊 AUDIT SUMMARY")
    print("=" * 60)
    
    if alpaca_data:
        print(f"✅ Alpaca Connection: SUCCESSFUL")
        print(f"  💰 Portfolio Value: ${alpaca_data['portfolio_value']:,.2f}")
        print(f"  ₿ Crypto Allocation: {alpaca_data['crypto_allocation']:.1f}%")
        print(f"  📈 Stock Allocation: {alpaca_data['stock_allocation']:.1f}%")
        print(f"  💸 Unrealized P&L: ${alpaca_data['total_unrealized_pl']:+,.2f}")
        print(f"  📊 Total Positions: {len(alpaca_data['positions'])}")
        print(f"  📋 Recent Orders: {alpaca_data['executed_orders_count']}")
        
        # Identify critical issues
        issues = []
        if alpaca_data['crypto_allocation'] > 60:
            issues.append(f"🚨 CRYPTO OVER-ALLOCATION: {alpaca_data['crypto_allocation']:.1f}% (limit: 60%)")
        if alpaca_data['total_unrealized_pl'] < -1000:
            issues.append(f"🚨 MAJOR LOSSES: ${alpaca_data['total_unrealized_pl']:+,.2f} unrealized")
        if len(alpaca_data['positions']) > 30:
            issues.append(f"🚨 TOO MANY POSITIONS: {len(alpaca_data['positions'])} (target: <30)")
        
        if issues:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print(f"✅ No critical allocation issues detected")
    else:
        print(f"❌ Alpaca Connection: FAILED")
    
    print(f"🔥 Firebase Connection: {'✅ CONNECTED' if firebase_connected else '❌ FAILED'}")
    
    # Save audit results
    audit_results = {
        'timestamp': datetime.now().isoformat(),
        'alpaca_connected': alpaca_data is not None,
        'firebase_connected': firebase_connected,
        'alpaca_data': alpaca_data,
        'audit_status': 'completed'
    }
    
    with open('live_system_audit_results.json', 'w') as f:
        json.dump(audit_results, f, indent=2, default=str)
    
    print(f"\n📁 Audit results saved to: live_system_audit_results.json")

if __name__ == "__main__":
    main()