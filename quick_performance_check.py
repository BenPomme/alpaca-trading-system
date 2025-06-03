#!/usr/bin/env python3
"""
Quick Performance Check

Load environment variables and provide current system performance status.
"""

import os
import sys
from datetime import datetime

def load_env_vars():
    """Load environment variables from .env.local"""
    env_file = '.env.local'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"').strip("'")
                    os.environ[key] = value
        print("✅ Environment variables loaded")
        return True
    else:
        print("❌ .env.local file not found")
        return False

def quick_analysis():
    """Quick performance analysis"""
    
    if not load_env_vars():
        return
    
    print("\n🚀 QUICK PERFORMANCE CHECK")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect to Alpaca
        import alpaca_trade_api as tradeapi
        api = tradeapi.REST(
            os.getenv('ALPACA_PAPER_API_KEY'),
            os.getenv('ALPACA_PAPER_SECRET_KEY'),
            base_url='https://paper-api.alpaca.markets'
        )
        
        # Get account info
        account = api.get_account()
        positions = api.list_positions()
        
        portfolio_value = float(account.portfolio_value)
        initial_capital = 1000000
        total_return = portfolio_value - initial_capital
        return_pct = (total_return / initial_capital) * 100
        
        print(f"\n💰 ACCOUNT STATUS")
        print(f"Portfolio Value: ${portfolio_value:,.2f}")
        print(f"Total Return: ${total_return:+,.2f} ({return_pct:+.2f}%)")
        print(f"Positions: {len(positions)}")
        print(f"Buying Power: ${float(account.buying_power):,.2f}")
        
        # Quick position summary
        if positions:
            print(f"\n📊 TOP POSITIONS")
            total_unrealized = 0
            for pos in positions[:5]:
                unrealized_pl = float(pos.unrealized_pl)
                total_unrealized += unrealized_pl
                print(f"{pos.symbol:8}: ${float(pos.market_value):>12,.2f} (P&L: ${unrealized_pl:+,.2f})")
            print(f"{'Total P&L':8}: ${total_unrealized:+,.2f}")
        
        # Performance assessment
        print(f"\n🎯 PERFORMANCE ASSESSMENT")
        monthly_projection = return_pct * 30  # Rough monthly projection
        
        if return_pct > 0:
            print(f"✅ POSITIVE: {return_pct:+.2f}% current return")
        else:
            print(f"❌ NEGATIVE: {return_pct:+.2f}% current return")
        
        print(f"📈 Monthly Projection: {monthly_projection:+.2f}%")
        
        if monthly_projection >= 5:
            print("🎯 ON TRACK for 5-10% monthly target")
        else:
            print("⚠️ BELOW TARGET performance")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Check Firebase connectivity
    try:
        from firebase_database import FirebaseDatabase
        db = FirebaseDatabase()
        
        # Get recent trade count
        recent_trades = db.db.collection('trade_history_details').limit(5).get()
        print(f"\n🔥 FIREBASE STATUS")
        print(f"Recent trades in database: {len(recent_trades)}")
        print("✅ Firebase connected")
        
    except Exception as e:
        print(f"\n❌ Firebase error: {e}")

if __name__ == "__main__":
    quick_analysis()