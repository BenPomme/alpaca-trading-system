#!/usr/bin/env python3
"""
Performance Analysis Script
Check Firebase trading data and system performance after fixes
"""

import os
import sys
from datetime import datetime, timedelta
import json

# Set environment variables from the provided values
os.environ['ALPACA_PAPER_API_KEY'] = "PKIP9MZ4Q1WJ423JXOQU"
os.environ['ALPACA_PAPER_SECRET_KEY'] = "zjGO4D9sED7ATSv6J1UCKCl0xzOOep5hPHRRmRcc"
os.environ['EXECUTION_ENABLED'] = "true"
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

def analyze_firebase_performance():
    """Analyze recent Firebase trading data"""
    print("🔥 FIREBASE PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    try:
        print("📦 Importing Firebase...")
        from firebase_database import FirebaseDatabase
        
        print("🔗 Connecting to Firebase...")
        db = FirebaseDatabase()
        
        print("📊 Analyzing recent trade data...")
        
        # Get recent trades (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Analyze opportunities
        print("\n📈 TRADE OPPORTUNITIES ANALYSIS")
        print("-" * 40)
        
        opportunities = db.get_recent_opportunities(hours=24)
        if opportunities:
            print(f"✅ Total opportunities found: {len(opportunities)}")
            
            # Group by symbol
            symbol_counts = {}
            confidence_scores = []
            
            for opp in opportunities:
                symbol = opp.get('symbol', 'unknown')
                confidence = opp.get('confidence', 0)
                
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
                confidence_scores.append(confidence)
            
            print(f"📊 Unique symbols: {len(symbol_counts)}")
            print(f"📊 Average confidence: {sum(confidence_scores)/len(confidence_scores):.3f}")
            print(f"📊 Confidence range: {min(confidence_scores):.3f} - {max(confidence_scores):.3f}")
            
            print("\n🎯 Top symbols by opportunities:")
            for symbol, count in sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {symbol}: {count} opportunities")
        else:
            print("❌ No opportunities found in last 24 hours")
        
        # Analyze trade results
        print("\n💰 TRADE RESULTS ANALYSIS")
        print("-" * 40)
        
        results = db.get_recent_trade_results(hours=24)
        if results:
            print(f"✅ Total trade results: {len(results)}")
            
            successful_trades = 0
            failed_trades = 0
            total_pnl = 0
            executed_trades = []
            
            for result in results:
                status = result.get('status', 'unknown')
                pnl = result.get('pnl', 0)
                
                if status == 'executed':
                    successful_trades += 1
                    executed_trades.append(result)
                    if pnl:
                        total_pnl += float(pnl)
                elif status == 'failed':
                    failed_trades += 1
            
            print(f"✅ Successful trades: {successful_trades}")
            print(f"❌ Failed trades: {failed_trades}")
            print(f"💰 Total P&L: ${total_pnl:.2f}")
            
            if successful_trades > 0:
                success_rate = (successful_trades / (successful_trades + failed_trades)) * 100
                print(f"📊 Success rate: {success_rate:.1f}%")
                
                if executed_trades:
                    print(f"📊 Average P&L per trade: ${total_pnl/len(executed_trades):.2f}")
        else:
            print("❌ No trade results found in last 24 hours")
        
        # Recent activity summary
        print("\n🕐 RECENT ACTIVITY SUMMARY")
        print("-" * 40)
        
        recent_activity = db.get_recent_ml_trades(limit=10)
        if recent_activity:
            print(f"📝 Last {len(recent_activity)} ML trades:")
            for i, trade in enumerate(recent_activity[:5], 1):
                symbol = trade.get('symbol', 'unknown')
                side = trade.get('side', 'unknown')
                confidence = trade.get('confidence', 0)
                timestamp = trade.get('timestamp', 'unknown')
                print(f"   {i}. {symbol} {side} (conf: {confidence:.3f}) - {timestamp}")
        else:
            print("❌ No recent ML trade data found")
            
    except Exception as e:
        print(f"❌ Firebase analysis failed: {e}")
        return False
    
    return True

def analyze_recent_logs():
    """Analyze recent local log data"""
    print("\n📋 LOCAL LOG ANALYSIS")
    print("=" * 40)
    
    try:
        log_file = "/Users/benjamin.pommeraud/Desktop/Alpaca/production.log"
        if os.path.exists(log_file):
            print(f"📂 Analyzing {log_file}")
            
            # Get last 100 lines
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-100:]
            
            # Count key events
            opportunities_found = sum(1 for line in recent_lines if "opportunities" in line.lower())
            trades_executed = sum(1 for line in recent_lines if "✅ Order submitted successfully" in line)
            trades_failed = sum(1 for line in recent_lines if "ERROR" in line and "trade" in line.lower())
            confidence_logs = [line for line in recent_lines if "BUY_conf=" in line]
            
            print(f"📊 Opportunities mentioned: {opportunities_found}")
            print(f"📊 Orders submitted: {trades_executed}")
            print(f"📊 Trade errors: {trades_failed}")
            print(f"📊 Confidence calculations: {len(confidence_logs)}")
            
            if confidence_logs:
                print("\n🔍 Recent confidence scores:")
                for line in confidence_logs[-5:]:
                    # Extract confidence values
                    if "BUY_conf=" in line and "SELL_conf=" in line:
                        print(f"   {line.strip()}")
        else:
            print(f"❌ Log file not found: {log_file}")
            
    except Exception as e:
        print(f"❌ Log analysis failed: {e}")

if __name__ == "__main__":
    print("🚀 SYSTEM PERFORMANCE CHECK")
    print("=" * 60)
    print(f"📅 Analysis Time: {datetime.now()}")
    print()
    
    # Check Firebase performance
    firebase_success = analyze_firebase_performance()
    
    # Check local logs
    analyze_recent_logs()
    
    print(f"\n🏁 Analysis Complete")
    print("=" * 60)
    
    if firebase_success:
        print("✅ Firebase connection successful")
    else:
        print("❌ Firebase connection issues detected")