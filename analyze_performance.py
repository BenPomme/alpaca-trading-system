#!/usr/bin/env python3
"""
System Performance Analysis
Check Firebase database and production logs for trading performance
"""

import os
import sys
from datetime import datetime, timedelta
import json

# Load environment variables manually from .env.local
def load_env_file():
    env_file = '.env.local'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"').strip("'")
                    os.environ[key] = value

# Load environment variables
load_env_file()

def analyze_firebase_trading_data():
    """Analyze Firebase trading performance data"""
    print("🔥 FIREBASE TRADING DATA ANALYSIS")
    print("=" * 50)
    
    try:
        # Import Firebase components
        from firebase_database import FirebaseDatabase
        
        print("🔗 Connecting to Firebase...")
        db = FirebaseDatabase()
        
        print("📊 Querying recent trading data...")
        
        # Get recent opportunities and results
        cutoff_time = datetime.now() - timedelta(hours=6)  # Last 6 hours
        
        print("\n📈 TRADE OPPORTUNITIES (Last 6 hours)")
        print("-" * 45)
        
        try:
            # Query opportunities
            opportunities_ref = db.db.collection('trade_opportunities')
            recent_opps = opportunities_ref.where('timestamp', '>=', cutoff_time).get()
            
            if recent_opps:
                opps = [doc.to_dict() for doc in recent_opps]
                print(f"✅ Found {len(opps)} opportunities")
                
                # Analyze by symbol and confidence
                symbol_counts = {}
                confidence_scores = []
                crypto_opps = 0
                stock_opps = 0
                options_opps = 0
                
                for opp in opps:
                    symbol = opp.get('symbol', 'unknown')
                    confidence = opp.get('confidence', 0)
                    
                    symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
                    confidence_scores.append(confidence)
                    
                    # Categorize by asset type
                    if 'USD' in symbol:
                        crypto_opps += 1
                    elif len(symbol) > 5:
                        options_opps += 1
                    else:
                        stock_opps += 1
                
                print(f"📊 Asset breakdown: {crypto_opps} crypto, {stock_opps} stocks, {options_opps} options")
                if confidence_scores:
                    avg_conf = sum(confidence_scores) / len(confidence_scores)
                    min_conf = min(confidence_scores)
                    max_conf = max(confidence_scores)
                    print(f"📊 Confidence: avg={avg_conf:.3f}, range={min_conf:.3f}-{max_conf:.3f}")
                
                print("\n🎯 Most active symbols:")
                for symbol, count in sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
                    print(f"   {symbol}: {count} opportunities")
            else:
                print("❌ No opportunities found in last 6 hours")
        except Exception as e:
            print(f"❌ Error querying opportunities: {e}")
        
        print("\n💰 TRADE RESULTS (Last 6 hours)")
        print("-" * 40)
        
        try:
            # Query trade results
            results_ref = db.db.collection('trade_results')
            recent_results = results_ref.where('timestamp', '>=', cutoff_time).get()
            
            if recent_results:
                results = [doc.to_dict() for doc in recent_results]
                print(f"✅ Found {len(results)} trade results")
                
                executed_count = 0
                failed_count = 0
                total_pnl = 0
                profitable_trades = 0
                
                for result in results:
                    status = result.get('status', 'unknown')
                    pnl = result.get('pnl', 0)
                    
                    if status in ['executed', 'EXECUTED']:
                        executed_count += 1
                        if pnl and isinstance(pnl, (int, float)) and pnl > 0:
                            profitable_trades += 1
                            total_pnl += float(pnl)
                        elif pnl and isinstance(pnl, (int, float)) and pnl < 0:
                            total_pnl += float(pnl)
                    elif status in ['failed', 'FAILED']:
                        failed_count += 1
                
                print(f"✅ Executed trades: {executed_count}")
                print(f"❌ Failed trades: {failed_count}")
                print(f"💰 Profitable trades: {profitable_trades}")
                print(f"💰 Total P&L: ${total_pnl:.2f}")
                
                if executed_count > 0:
                    success_rate = (executed_count / (executed_count + failed_count)) * 100 if (executed_count + failed_count) > 0 else 0
                    print(f"📊 Execution rate: {success_rate:.1f}%")
                    
                    if profitable_trades > 0:
                        win_rate = (profitable_trades / executed_count) * 100
                        print(f"📊 Win rate: {win_rate:.1f}%")
            else:
                print("❌ No trade results found in last 6 hours")
        except Exception as e:
            print(f"❌ Error querying trade results: {e}")
        
        print("\n🧠 ML LEARNING DATA (Recent)")
        print("-" * 35)
        
        try:
            # Query ML trades
            ml_ref = db.db.collection('ml_trades')
            recent_ml = ml_ref.order_by('timestamp', direction='DESCENDING').limit(10).get()
            
            if recent_ml:
                ml_trades = [doc.to_dict() for doc in recent_ml]
                print(f"✅ Found {len(ml_trades)} recent ML trades")
                
                entry_trades = 0
                exit_trades = 0
                
                for trade in ml_trades:
                    if trade.get('exit_reason'):
                        exit_trades += 1
                    else:
                        entry_trades += 1
                
                print(f"📊 Entry trades: {entry_trades}")
                print(f"📊 Exit trades: {exit_trades}")
                
                print("\n📝 Recent ML trade samples:")
                for i, trade in enumerate(ml_trades[:5], 1):
                    symbol = trade.get('symbol', 'unknown')
                    side = trade.get('side', 'unknown')
                    confidence = trade.get('confidence', 0)
                    timestamp = trade.get('timestamp', 'unknown')
                    exit_reason = trade.get('exit_reason', 'entry')
                    print(f"   {i}. {symbol} {side} conf={confidence:.3f} {exit_reason}")
            else:
                print("❌ No ML trading data found")
        except Exception as e:
            print(f"❌ Error querying ML data: {e}")
            
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        return False
    
    return True

def analyze_production_logs():
    """Analyze recent production logs"""
    print("\n📋 PRODUCTION LOG ANALYSIS")
    print("=" * 40)
    
    try:
        log_file = "/Users/benjamin.pommeraud/Desktop/Alpaca/production.log"
        if os.path.exists(log_file):
            print(f"📂 Reading {log_file}")
            
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Get last 200 lines (recent activity)
            recent_lines = lines[-200:]
            
            # Count significant events
            opportunities_created = sum(1 for line in recent_lines if "OPPORTUNITY CREATED" in line)
            orders_submitted = sum(1 for line in recent_lines if "Order submitted successfully" in line)
            trade_errors = sum(1 for line in recent_lines if "ERROR" in line and ("trade" in line.lower() or "execute" in line.lower()))
            confidence_calculations = sum(1 for line in recent_lines if "BUY_conf=" in line)
            risk_validations = sum(1 for line in recent_lines if "Risk validation passed" in line)
            
            print(f"📊 Opportunities created: {opportunities_created}")
            print(f"📊 Orders submitted: {orders_submitted}")
            print(f"📊 Risk validations passed: {risk_validations}")
            print(f"📊 Confidence calculations: {confidence_calculations}")
            print(f"📊 Trade errors: {trade_errors}")
            
            # Extract recent confidence scores
            confidence_lines = [line for line in recent_lines if "BUY_conf=" in line and "SELL_conf=" in line]
            if confidence_lines:
                print(f"\n🔍 Recent confidence scores (last {min(len(confidence_lines), 5)}):")
                for line in confidence_lines[-5:]:
                    if "INFO" in line:
                        # Extract timestamp and confidence info
                        parts = line.strip().split(" - ")
                        if len(parts) >= 3:
                            timestamp = parts[0].split(",")[0]
                            message = parts[-1]
                            print(f"   {timestamp}: {message}")
            
            # Check for recent successful order flows
            successful_flows = []
            for i, line in enumerate(recent_lines):
                if "TRADE APPROVED" in line and i + 5 < len(recent_lines):
                    # Look for order submission in next few lines
                    for j in range(i+1, min(i+5, len(recent_lines))):
                        if "Order submitted successfully" in recent_lines[j]:
                            successful_flows.append(line.strip())
                            break
            
            if successful_flows:
                print(f"\n✅ Recent successful trade flows: {len(successful_flows)}")
                for flow in successful_flows[-3:]:
                    # Extract symbol from approval message
                    if "TRADE APPROVED:" in flow:
                        parts = flow.split("TRADE APPROVED:")
                        if len(parts) > 1:
                            print(f"   {parts[1].strip()}")
            
        else:
            print(f"❌ Log file not found: {log_file}")
            
    except Exception as e:
        print(f"❌ Log analysis error: {e}")

def analyze_alpaca_account():
    """Check current Alpaca account status"""
    print("\n📈 ALPACA ACCOUNT STATUS")
    print("=" * 35)
    
    try:
        import alpaca_trade_api as tradeapi
        
        api = tradeapi.REST(
            os.getenv('ALPACA_PAPER_API_KEY'),
            os.getenv('ALPACA_PAPER_SECRET_KEY'),
            base_url='https://paper-api.alpaca.markets'
        )
        
        account = api.get_account()
        positions = api.list_positions()
        
        print(f"💰 Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"💰 Buying Power: ${float(account.buying_power):,.2f}")
        print(f"💰 Cash: ${float(account.cash):,.2f}")
        print(f"📊 Day Trading Power: ${float(getattr(account, 'daytrading_buying_power', 0)):,.2f}")
        print(f"📊 Total Positions: {len(positions)}")
        
        if positions:
            print(f"\n📍 Current Positions:")
            total_value = 0
            crypto_value = 0
            stock_value = 0
            
            for pos in positions[:10]:  # Show first 10
                symbol = pos.symbol
                qty = float(pos.qty)
                market_value = float(pos.market_value)
                unrealized_pl = float(pos.unrealized_pl)
                
                total_value += abs(market_value)
                if 'USD' in symbol:
                    crypto_value += abs(market_value)
                else:
                    stock_value += abs(market_value)
                
                print(f"   {symbol}: {qty:,.4f} shares, ${market_value:,.2f} (P&L: ${unrealized_pl:,.2f})")
            
            print(f"\n📊 Allocation: ${crypto_value:,.0f} crypto, ${stock_value:,.0f} stocks")
            
    except Exception as e:
        print(f"❌ Alpaca API error: {e}")

if __name__ == "__main__":
    print("🚀 TRADING SYSTEM PERFORMANCE ANALYSIS")
    print("=" * 60)
    print(f"📅 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check environment
    if not os.getenv('FIREBASE_PRIVATE_KEY_ID'):
        print("❌ Environment variables not loaded properly")
        sys.exit(1)
    
    # Run analyses
    firebase_success = analyze_firebase_trading_data()
    analyze_production_logs()
    analyze_alpaca_account()
    
    print(f"\n🏁 ANALYSIS COMPLETE")
    print("=" * 60)
    
    if firebase_success:
        print("✅ Firebase analysis successful - check data above")
    else:
        print("❌ Firebase analysis had issues")
    
    print("📋 Check the sections above for performance insights")