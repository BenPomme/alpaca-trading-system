#!/usr/bin/env python3
"""
Live Performance Analysis Report

Comprehensive analysis of current trading system performance based on:
1. Firebase trade history data
2. Alpaca account status
3. ROI calculations and projections
"""

import os
import json
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
import logging

# Set precision for financial calculations
getcontext().prec = 28

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check that required environment variables are set"""
    required_vars = [
        'ALPACA_PAPER_API_KEY',
        'ALPACA_PAPER_SECRET_KEY',
        'FIREBASE_PRIVATE_KEY_ID',
        'FIREBASE_CLIENT_EMAIL'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables found")
    return True

def analyze_current_performance():
    """Analyze current trading system performance"""
    
    if not check_environment():
        return
    
    print("📊 LIVE TRADING SYSTEM PERFORMANCE ANALYSIS")
    print("=" * 70)
    print(f"📅 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize connections
    try:
        from firebase_database import FirebaseDatabase
        firebase_db = FirebaseDatabase()
        logger.info("🔥 Firebase connected")
    except Exception as e:
        logger.error(f"❌ Firebase failed: {e}")
        return
    
    try:
        import alpaca_trade_api as tradeapi
        alpaca_api = tradeapi.REST(
            os.getenv('ALPACA_PAPER_API_KEY'),
            os.getenv('ALPACA_PAPER_SECRET_KEY'),
            base_url='https://paper-api.alpaca.markets'
        )
        logger.info("📈 Alpaca connected")
    except Exception as e:
        logger.error(f"❌ Alpaca failed: {e}")
        return
    
    # 1. CURRENT ACCOUNT STATUS
    print("💰 CURRENT ACCOUNT STATUS")
    print("-" * 50)
    
    account = alpaca_api.get_account()
    positions = alpaca_api.list_positions()
    
    portfolio_value = float(account.portfolio_value)
    equity = float(account.equity)
    buying_power = float(account.buying_power)
    initial_capital = 1000000  # $1M baseline
    
    total_return = portfolio_value - initial_capital
    return_pct = (total_return / initial_capital) * 100
    
    print(f"Portfolio Value: ${portfolio_value:,.2f}")
    print(f"Total Return: ${total_return:+,.2f} ({return_pct:+.2f}%)")
    print(f"Available Buying Power: ${buying_power:,.2f}")
    print(f"Active Positions: {len(positions)}")
    
    # 2. POSITION ANALYSIS
    print(f"\n📍 POSITION BREAKDOWN")
    print("-" * 50)
    
    if positions:
        total_market_value = 0
        total_unrealized_pl = 0
        profitable_positions = 0
        
        print("Symbol    | Quantity     | Market Value  | Unrealized P&L | % Return")
        print("-" * 75)
        
        for pos in positions:
            symbol = pos.symbol
            qty = float(pos.qty)
            market_value = float(pos.market_value)
            unrealized_pl = float(pos.unrealized_pl)
            
            # Calculate position return %
            if hasattr(pos, 'avg_entry_price') and pos.avg_entry_price:
                entry_price = float(pos.avg_entry_price)
                current_price = market_value / qty if qty != 0 else 0
                position_return = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
            else:
                position_return = 0
            
            total_market_value += abs(market_value)
            total_unrealized_pl += unrealized_pl
            
            if unrealized_pl > 0:
                profitable_positions += 1
            
            print(f"{symbol:8} | {qty:>12,.4f} | ${market_value:>12,.2f} | ${unrealized_pl:>+10,.2f} | {position_return:>+6.2f}%")
        
        print("-" * 75)
        print(f"{'TOTAL':8} | {'':>12} | ${total_market_value:>12,.2f} | ${total_unrealized_pl:>+10,.2f} | {(total_unrealized_pl/total_market_value*100) if total_market_value > 0 else 0:>+6.2f}%")
        
        win_rate = (profitable_positions / len(positions)) * 100 if positions else 0
        print(f"\nPosition Win Rate: {profitable_positions}/{len(positions)} ({win_rate:.1f}%)")
    
    # 3. FIREBASE TRADE HISTORY ANALYSIS
    print(f"\n🔥 TRADE HISTORY ANALYSIS")
    print("-" * 50)
    
    # Get recent trades from Firebase
    recent_trades = firebase_db.db.collection('trade_history_details').order_by('timestamp', direction='DESCENDING').limit(20).get()
    
    if recent_trades:
        print(f"Recent Trades (last 20):")
        print("Time        | Symbol   | Side | Quantity    | Price    | Value")
        print("-" * 65)
        
        total_trade_value = 0
        buy_value = 0
        sell_value = 0
        
        for trade_doc in recent_trades:
            trade_data = trade_doc.to_dict()
            timestamp = trade_data.get('timestamp', 'unknown')[:16]  # Show date and time
            symbol = trade_data.get('symbol', 'unknown')
            side = trade_data.get('side', 'unknown').upper()
            quantity = trade_data.get('quantity', 0)
            price = trade_data.get('price', 0)
            value = trade_data.get('value', 0)
            
            total_trade_value += abs(value)
            if side == 'BUY':
                buy_value += value
            else:
                sell_value += value
            
            print(f"{timestamp} | {symbol:8} | {side:4} | {quantity:>11,.4f} | ${price:>8.2f} | ${value:>10,.2f}")
        
        print(f"\nTrading Activity Summary:")
        print(f"Total Buy Value: ${buy_value:,.2f}")
        print(f"Total Sell Value: ${sell_value:,.2f}")
        print(f"Net Trading: ${buy_value - sell_value:+,.2f}")
    
    # 4. PERFORMANCE METRICS & PROJECTIONS
    print(f"\n📊 PERFORMANCE METRICS")
    print("-" * 50)
    
    # Calculate time-based metrics
    # Assume system has been running for analysis period
    days_running = 1.0  # Adjust based on actual running time
    
    daily_return_rate = return_pct / days_running if days_running > 0 else return_pct
    monthly_projection = daily_return_rate * 30
    annual_projection = daily_return_rate * 365
    
    print(f"Current ROI: {return_pct:+.2f}%")
    print(f"Daily Return Rate: {daily_return_rate:+.3f}%")
    print(f"Monthly Projection: {monthly_projection:+.2f}%")
    print(f"Annual Projection: {annual_projection:+.1f}%")
    
    # Target analysis
    print(f"\n🎯 TARGET ANALYSIS")
    print("-" * 30)
    print(f"Monthly Target: 5-10%")
    print(f"Current Projection: {monthly_projection:+.2f}%")
    
    if monthly_projection >= 10:
        status = "🚀 EXCEEDING TARGET"
    elif monthly_projection >= 5:
        status = "✅ MEETING TARGET"
    elif monthly_projection >= 0:
        status = "⚠️ BELOW TARGET (Positive)"
    else:
        status = "❌ NEGATIVE PERFORMANCE"
    
    print(f"Status: {status}")
    
    # 5. RISK ANALYSIS
    print(f"\n🛡️ RISK ANALYSIS")
    print("-" * 30)
    
    if positions:
        portfolio_utilization = (total_market_value / portfolio_value) * 100
        largest_position = max(abs(float(pos.market_value)) for pos in positions)
        largest_position_pct = (largest_position / portfolio_value) * 100
        
        print(f"Portfolio Utilization: {portfolio_utilization:.1f}%")
        print(f"Largest Position: ${largest_position:,.2f} ({largest_position_pct:.1f}%)")
        print(f"Position Diversification: {len(positions)} symbols")
        
        # Check if limits are working
        if largest_position_pct > 20:
            print("⚠️ WARNING: Large position concentration")
        elif portfolio_utilization > 80:
            print("⚠️ WARNING: High portfolio utilization")
        else:
            print("✅ Risk levels appear reasonable")
    
    # 6. SYSTEM HEALTH CHECK
    print(f"\n🔧 SYSTEM HEALTH")
    print("-" * 30)
    
    # Check Firebase data freshness
    doc_ref = firebase_db.db.collection('trade_history_tracker').document('current_status')
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        last_updated = data.get('last_updated', 'unknown')
        
        if last_updated != 'unknown':
            try:
                last_update_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                time_since_update = datetime.now() - last_update_time.replace(tzinfo=None)
                minutes_since = time_since_update.total_seconds() / 60
                
                print(f"Last Firebase Update: {minutes_since:.1f} minutes ago")
                
                if minutes_since < 5:
                    print("✅ Firebase data is fresh")
                elif minutes_since < 30:
                    print("⚠️ Firebase data slightly stale")
                else:
                    print("❌ Firebase data is stale")
            except:
                print(f"Last Update: {last_updated}")
        
        # Check safety controls
        safety_limits = data.get('safety_limits', {})
        cooldown_minutes = safety_limits.get('cooldown_minutes', 'unknown')
        max_hourly_trades = safety_limits.get('max_hourly_trades', 'unknown')
        
        print(f"Safety Controls:")
        print(f"  - Cooldown: {cooldown_minutes} minutes")
        print(f"  - Hourly limit: {max_hourly_trades} trades")
        print(f"  - Position limits: REMOVED (unlimited)")
        print(f"  - Daily limits: REMOVED (unlimited)")
    
    # 7. RECOMMENDATIONS
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 30)
    
    if return_pct < -5:
        print("🚨 HIGH PRIORITY: Portfolio down >5%, review strategy")
    elif return_pct < 0:
        print("⚠️ MEDIUM PRIORITY: Negative returns, monitor closely")
    elif monthly_projection < 5:
        print("📈 OPTIMIZATION: Consider increasing position sizes or frequency")
    else:
        print("✅ PERFORMING WELL: Continue current strategy")
    
    if len(positions) < 5:
        print("📊 DIVERSIFICATION: Consider more positions for risk distribution")
    
    print(f"\n📋 Analysis complete at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    analyze_current_performance()