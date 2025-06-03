#!/usr/bin/env python3
"""
Live Performance Monitor

Real-time monitoring of trading system performance using:
1. Railway health endpoints for system status
2. Firebase database for trade history and P&L
3. Alpaca API for current account status
4. Performance analytics and ROI calculations

This provides comprehensive live monitoring without needing Railway CLI access.
"""

import os
import time
import json
import requests
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
import logging

# Set precision for financial calculations
getcontext().prec = 28

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LivePerformanceMonitor:
    """Monitor live trading system performance across all platforms"""
    
    def __init__(self):
        self.load_environment()
        self.railway_base_url = None  # Will be set when we find the Railway URL
        self.firebase_db = None
        self.alpaca_api = None
        
        # Performance tracking
        self.initial_portfolio_value = 1000000  # $1M baseline
        self.monitoring_start_time = datetime.now()
        
        if self.check_environment():
            self.initialize_connections()
    
    def check_environment(self):
        """Check required environment variables are available"""
        required_vars = [
            'ALPACA_PAPER_API_KEY',
            'ALPACA_PAPER_SECRET_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        logger.info("✅ Environment variables verified")
        return True
    
    def initialize_connections(self):
        """Initialize Firebase and Alpaca connections"""
        
        # Initialize Firebase
        try:
            from firebase_database import FirebaseDatabase
            self.firebase_db = FirebaseDatabase()
            logger.info("🔥 Firebase connection established")
        except Exception as e:
            logger.error(f"❌ Firebase connection failed: {e}")
        
        # Initialize Alpaca API
        try:
            import alpaca_trade_api as tradeapi
            self.alpaca_api = tradeapi.REST(
                os.getenv('ALPACA_PAPER_API_KEY'),
                os.getenv('ALPACA_PAPER_SECRET_KEY'),
                base_url='https://paper-api.alpaca.markets'
            )
            logger.info("📈 Alpaca API connection established")
        except Exception as e:
            logger.error(f"❌ Alpaca API connection failed: {e}")
    
    def check_railway_system_health(self):
        """Check Railway system health via public endpoints"""
        
        # Try common Railway app URLs (you'll need to replace with your actual URL)
        possible_urls = [
            "https://your-app.railway.app",  # Replace with actual Railway URL
            "https://alpaca-trading-system.railway.app",  # Common pattern
        ]
        
        for base_url in possible_urls:
            try:
                # Health check
                response = requests.get(f"{base_url}/health", timeout=10)
                if response.status_code == 200:
                    self.railway_base_url = base_url
                    health_data = response.json()
                    
                    print("🚀 RAILWAY SYSTEM STATUS")
                    print("-" * 40)
                    print(f"✅ System: {health_data.get('status', 'unknown')}")
                    print(f"📊 Uptime: {health_data.get('uptime', 'unknown')}")
                    print(f"🔄 Cycle: {health_data.get('cycle_count', 'unknown')}")
                    print(f"⏰ Last check: {health_data.get('last_health_check', 'unknown')}")
                    
                    return health_data
                    
            except Exception as e:
                logger.debug(f"URL {base_url} not accessible: {e}")
                continue
        
        print("❌ RAILWAY SYSTEM: Not accessible via health endpoints")
        print("   Note: You may need to update the Railway URL in the script")
        return None
    
    def check_safety_controls(self):
        """Check current safety control status"""
        
        if not self.railway_base_url:
            return None
        
        try:
            response = requests.get(f"{self.railway_base_url}/safety", timeout=10)
            if response.status_code == 200:
                safety_data = response.json()
                
                print("\n🛡️ SAFETY CONTROLS STATUS")
                print("-" * 40)
                
                # Order executor status
                if 'order_executor' in safety_data:
                    executor_data = safety_data['order_executor']
                    tracker_status = executor_data.get('trade_tracker_status', {})
                    
                    print(f"📊 Execution enabled: {executor_data.get('execution_enabled', 'unknown')}")
                    print(f"🔄 Emergency stop: {executor_data.get('emergency_stop', 'unknown')}")
                    print(f"📝 Pending orders: {executor_data.get('pending_orders', 'unknown')}")
                    
                    if tracker_status:
                        print(f"🎯 Symbols tracked: {tracker_status.get('total_symbols', 0)}")
                        print(f"📊 Trades today: {tracker_status.get('total_trades_today', 0)}")
                        print(f"🕐 Symbols on cooldown: {tracker_status.get('symbols_on_cooldown', 0)}")
                
                return safety_data
                
        except Exception as e:
            logger.warning(f"⚠️ Safety endpoint not accessible: {e}")
        
        return None
    
    def analyze_firebase_performance(self):
        """Analyze trading performance from Firebase database"""
        
        if not self.firebase_db:
            return None
        
        try:
            print("\n🔥 FIREBASE PERFORMANCE ANALYSIS")
            print("-" * 40)
            
            # Get trade history summary
            doc_ref = self.firebase_db.db.collection('trade_history_tracker').document('current_status')
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                
                # Position values
                position_values = data.get('position_values', {})
                total_position_value = sum(Decimal(v) for v in position_values.values())
                
                print(f"💰 Total position value: ${float(total_position_value):,.2f}")
                print(f"📊 Active symbols: {len(position_values)}")
                
                # Show top positions
                sorted_positions = sorted(
                    [(k, float(Decimal(v))) for k, v in position_values.items()],
                    key=lambda x: abs(x[1]),
                    reverse=True
                )
                
                print("\n🎯 Top 5 Positions:")
                for symbol, value in sorted_positions[:5]:
                    print(f"   {symbol:8}: ${value:>12,.2f}")
                
                # Last update
                last_updated = data.get('last_updated', 'unknown')
                print(f"\n⏰ Last updated: {last_updated}")
                
            else:
                print("❌ No trade history found in Firebase")
            
            # Get recent detailed trades
            recent_trades = self.firebase_db.db.collection('trade_history_details').order_by('timestamp', direction='DESCENDING').limit(10).get()
            
            if recent_trades:
                print(f"\n📝 Recent Trades ({len(recent_trades)} shown):")
                print("-" * 50)
                
                for trade_doc in recent_trades:
                    trade_data = trade_doc.to_dict()
                    symbol = trade_data.get('symbol', 'unknown')
                    side = trade_data.get('side', 'unknown')
                    quantity = trade_data.get('quantity', 0)
                    price = trade_data.get('price', 0)
                    value = trade_data.get('value', 0)
                    timestamp = trade_data.get('timestamp', 'unknown')
                    
                    print(f"   {timestamp[:19]} | {symbol:8} {side.upper():4} {quantity:>8,.4f} @ ${price:>8.2f} = ${value:>10,.2f}")
            
            return {
                'total_position_value': float(total_position_value),
                'active_symbols': len(position_values),
                'positions': sorted_positions,
                'recent_trades_count': len(recent_trades)
            }
            
        except Exception as e:
            logger.error(f"❌ Firebase analysis failed: {e}")
            return None
    
    def analyze_alpaca_account(self):
        """Analyze current Alpaca account status and performance"""
        
        if not self.alpaca_api:
            return None
        
        try:
            print("\n📈 ALPACA ACCOUNT ANALYSIS")
            print("-" * 40)
            
            # Get account info
            account = self.alpaca_api.get_account()
            positions = self.alpaca_api.list_positions()
            
            # Current values
            portfolio_value = float(account.portfolio_value)
            buying_power = float(account.buying_power)
            day_trading_power = float(getattr(account, 'daytrading_buying_power', 0))
            equity = float(account.equity)
            
            # Calculate performance
            total_return = portfolio_value - self.initial_portfolio_value
            return_pct = (total_return / self.initial_portfolio_value) * 100
            
            print(f"💰 Portfolio Value: ${portfolio_value:,.2f}")
            print(f"💰 Equity: ${equity:,.2f}")
            print(f"💰 Buying Power: ${buying_power:,.2f}")
            print(f"💰 Day Trading Power: ${day_trading_power:,.2f}")
            print(f"📊 Total Return: ${total_return:+,.2f} ({return_pct:+.2f}%)")
            
            # Position analysis
            print(f"\n📍 Current Positions: {len(positions)}")
            if positions:
                total_market_value = 0
                total_unrealized_pl = 0
                
                print("Symbol    | Qty      | Market Value | Unrealized P&L")
                print("-" * 55)
                
                for pos in positions[:10]:  # Show top 10
                    symbol = pos.symbol
                    qty = float(pos.qty)
                    market_value = float(pos.market_value)
                    unrealized_pl = float(pos.unrealized_pl)
                    
                    total_market_value += abs(market_value)
                    total_unrealized_pl += unrealized_pl
                    
                    print(f"{symbol:8} | {qty:>8,.4f} | ${market_value:>11,.2f} | ${unrealized_pl:>+10,.2f}")
                
                print("-" * 55)
                print(f"{'TOTAL':8} | {'':>8} | ${total_market_value:>11,.2f} | ${total_unrealized_pl:>+10,.2f}")
            
            return {
                'portfolio_value': portfolio_value,
                'total_return': total_return,
                'return_pct': return_pct,
                'positions_count': len(positions),
                'equity': equity,
                'buying_power': buying_power
            }
            
        except Exception as e:
            logger.error(f"❌ Alpaca analysis failed: {e}")
            return None
    
    def calculate_performance_metrics(self, alpaca_data, firebase_data):
        """Calculate comprehensive performance metrics"""
        
        if not alpaca_data:
            return None
        
        print("\n📊 PERFORMANCE METRICS")
        print("-" * 40)
        
        # Time-based metrics
        monitoring_duration = datetime.now() - self.monitoring_start_time
        days_running = monitoring_duration.days + (monitoring_duration.seconds / 86400)
        
        # ROI calculations
        portfolio_value = alpaca_data['portfolio_value']
        total_return = alpaca_data['total_return']
        return_pct = alpaca_data['return_pct']
        
        # Annualized metrics (if running more than 1 day)
        if days_running > 1:
            daily_return_rate = (portfolio_value / self.initial_portfolio_value) ** (1/days_running) - 1
            annualized_return = ((1 + daily_return_rate) ** 365 - 1) * 100
        else:
            daily_return_rate = return_pct / 100
            annualized_return = daily_return_rate * 365 * 100
        
        print(f"🎯 Target Monthly ROI: 5-10%")
        print(f"📈 Current Total ROI: {return_pct:+.2f}%")
        print(f"📅 Days Running: {days_running:.1f}")
        print(f"📊 Daily Return Rate: {daily_return_rate*100:+.3f}%")
        print(f"📈 Annualized Return: {annualized_return:+.1f}%")
        
        # Monthly projection
        if days_running > 0:
            monthly_projection = (daily_return_rate * 30) * 100
            print(f"🔮 Monthly Projection: {monthly_projection:+.2f}%")
            
            # Performance vs target
            if monthly_projection >= 5:
                print("✅ ON TRACK: Meeting 5-10% monthly target")
            elif monthly_projection >= 0:
                print("⚠️ BELOW TARGET: Positive but under 5% monthly")
            else:
                print("❌ NEGATIVE: Below target performance")
        
        # Risk metrics
        if firebase_data:
            active_symbols = firebase_data['active_symbols']
            total_position_value = firebase_data['total_position_value']
            portfolio_utilization = (abs(total_position_value) / portfolio_value) * 100
            
            print(f"\n🛡️ RISK METRICS")
            print(f"📊 Active Positions: {active_symbols}")
            print(f"📊 Portfolio Utilization: {portfolio_utilization:.1f}%")
            print(f"💰 Position Value: ${abs(total_position_value):,.2f}")
        
        return {
            'current_roi': return_pct,
            'daily_return_rate': daily_return_rate * 100,
            'annualized_return': annualized_return,
            'monthly_projection': monthly_projection if days_running > 0 else None,
            'days_running': days_running
        }
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        
        print("🔍 LIVE TRADING SYSTEM PERFORMANCE MONITOR")
        print("=" * 70)
        print(f"📅 Monitor Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check all systems
        railway_health = self.check_railway_system_health()
        safety_status = self.check_safety_controls()
        firebase_data = self.analyze_firebase_performance()
        alpaca_data = self.analyze_alpaca_account()
        
        # Calculate performance metrics
        performance_metrics = self.calculate_performance_metrics(alpaca_data, firebase_data)
        
        # Summary
        print("\n🎯 MONITORING SUMMARY")
        print("=" * 40)
        
        if railway_health:
            print("✅ Railway System: Online and accessible")
        else:
            print("❌ Railway System: Not accessible (may need URL update)")
        
        if firebase_data:
            print(f"✅ Firebase: {firebase_data['active_symbols']} symbols, ${firebase_data['total_position_value']:,.2f} positions")
        else:
            print("❌ Firebase: Not accessible")
        
        if alpaca_data:
            print(f"✅ Alpaca: ${alpaca_data['portfolio_value']:,.2f} portfolio, {alpaca_data['return_pct']:+.2f}% ROI")
        else:
            print("❌ Alpaca: Not accessible")
        
        if performance_metrics:
            monthly_proj = performance_metrics.get('monthly_projection', 0)
            if monthly_proj and monthly_proj >= 5:
                print("🎯 Performance: ON TRACK for 5-10% monthly target")
            elif monthly_proj and monthly_proj >= 0:
                print("⚠️ Performance: BELOW TARGET but positive")
            else:
                print("❌ Performance: NEGATIVE returns")
        
        return {
            'railway_health': railway_health,
            'safety_status': safety_status,
            'firebase_data': firebase_data,
            'alpaca_data': alpaca_data,
            'performance_metrics': performance_metrics
        }

def continuous_monitoring(interval_minutes=5):
    """Run continuous monitoring with specified interval"""
    
    monitor = LivePerformanceMonitor()
    
    print(f"🔄 Starting continuous monitoring (every {interval_minutes} minutes)")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    try:
        while True:
            monitor.run_monitoring_cycle()
            
            print(f"\n⏰ Next check in {interval_minutes} minutes...")
            print("=" * 70)
            
            time.sleep(interval_minutes * 60)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        continuous_monitoring(interval)
    else:
        monitor = LivePerformanceMonitor()
        results = monitor.run_monitoring_cycle()
        
        print(f"\n📋 Single monitoring cycle complete")
        print("For continuous monitoring, run: python monitor_live_performance.py continuous [interval_minutes]")