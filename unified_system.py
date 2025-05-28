#!/usr/bin/env python3
"""
Unified Trading System with Real-Time Dashboard
Both trading bot and dashboard running simultaneously
"""

import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, jsonify

# Global shared state between trading system and dashboard
shared_state = {
    'trader': None,
    'last_cycle': None,
    'status': 'Initializing...',
    'cycle_count': 0,
    'start_time': datetime.now().isoformat(),
    'errors': []
}

class RealTimeTrader:
    """Enhanced trader that updates shared state"""
    
    def __init__(self):
        from start_ultra_simple import UltraSimpleTrader
        shared_state['status'] = 'Connecting to Alpaca...'
        self.trader = UltraSimpleTrader()
        shared_state['trader'] = self.trader
        shared_state['status'] = 'Connected - Ready to Trade'
        print("✅ Real-time trader initialized")
    
    def run_cycle_with_updates(self):
        """Run cycle and update shared state"""
        try:
            shared_state['status'] = 'Running Trading Cycle...'
            cycle_data = self.trader.run_cycle()
            
            # Update shared state
            shared_state['last_cycle'] = {
                **cycle_data,
                'timestamp': datetime.now().isoformat(),
                'cycle_number': shared_state['cycle_count'] + 1
            }
            shared_state['cycle_count'] += 1
            shared_state['status'] = 'Active - Monitoring Markets'
            
            return cycle_data
        except Exception as e:
            error_msg = f"Cycle error: {e}"
            shared_state['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': error_msg
            })
            shared_state['status'] = f'Error: {str(e)[:50]}...'
            print(f"❌ {error_msg}")
            return None
    
    def run_continuous_with_updates(self):
        """Main trading loop with real-time updates"""
        print("🔄 Starting continuous trading with real-time updates...")
        
        try:
            while True:
                # Run trading cycle
                self.run_cycle_with_updates()
                
                # Wait between cycles
                wait_time = 120  # 2 minutes
                shared_state['status'] = f'Waiting {wait_time}s for next cycle...'
                time.sleep(wait_time)
                
        except Exception as e:
            shared_state['status'] = f'System Error: {e}'
            shared_state['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': f"System error: {e}"
            })
            print(f"❌ System error: {e}")
            time.sleep(60)  # Wait before restart

# Flask Dashboard
app = Flask(__name__)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """Real-time system status"""
    return jsonify({
        'status': shared_state['status'],
        'timestamp': datetime.now().isoformat(),
        'cycle_count': shared_state['cycle_count'],
        'start_time': shared_state['start_time'],
        'last_cycle': shared_state['last_cycle'],
        'has_trader': shared_state['trader'] is not None
    })

@app.route('/api/account')
def api_account():
    """Real-time account information"""
    if not shared_state['trader']:
        return jsonify({'error': 'Trading system not connected'})
    
    try:
        account = shared_state['trader'].api.get_account()
        return jsonify({
            'portfolio_value': float(account.portfolio_value),
            'buying_power': float(account.buying_power),
            'cash': float(account.cash),
            'market_value': float(account.long_market_value or 0),
            'updated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/market')
def api_market():
    """Real-time market data"""
    if not shared_state['trader']:
        return jsonify({'error': 'Trading system not connected'})
    
    try:
        symbols = ['SPY', 'QQQ', 'IWM']
        market_data = []
        
        for symbol in symbols:
            quote = shared_state['trader'].get_quote(symbol)
            if quote:
                market_data.append({
                    'symbol': symbol,
                    'price': quote['ask'],
                    'timestamp': quote['timestamp']
                })
        
        return jsonify(market_data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/logs')
def api_logs():
    """Recent trading logs and errors"""
    logs = []
    
    # Add recent cycle if available
    if shared_state['last_cycle']:
        logs.append({
            'type': 'cycle',
            'data': shared_state['last_cycle']
        })
    
    # Add recent errors
    for error in shared_state['errors'][-5:]:
        logs.append({
            'type': 'error',
            'data': error
        })
    
    # Try to get file logs too
    try:
        if os.path.exists('data/trading_log.json'):
            with open('data/trading_log.json', 'r') as f:
                file_logs = json.load(f)
            for log in file_logs[-5:]:
                logs.append({
                    'type': 'file_log',
                    'data': log
                })
    except Exception:
        pass
    
    return jsonify(logs)

@app.route('/api/cycle')
def api_manual_cycle():
    """Manually trigger a trading cycle"""
    if not shared_state['trader']:
        return jsonify({'error': 'Trading system not connected'})
    
    try:
        trader_instance = RealTimeTrader()
        trader_instance.trader = shared_state['trader']  # Use existing connection
        cycle_data = trader_instance.run_cycle_with_updates()
        
        if cycle_data:
            return jsonify({'success': True, 'cycle': shared_state['last_cycle']})
        else:
            return jsonify({'error': 'Cycle failed - check logs'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/health')
def health():
    """Health check for Railway"""
    return jsonify({
        'status': 'healthy',
        'trading_system': shared_state['trader'] is not None,
        'timestamp': datetime.now().isoformat()
    })

def run_trading_system():
    """Background thread for trading system"""
    print("🤖 Starting real-time trading system...")
    try:
        trader = RealTimeTrader()
        trader.run_continuous_with_updates()
    except Exception as e:
        shared_state['status'] = f'Trading system crashed: {e}'
        shared_state['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': f"Trading system crashed: {e}"
        })
        print(f"❌ Trading system crashed: {e}")

def run_dashboard():
    """Main thread for web dashboard"""
    print("🌐 Starting real-time dashboard...")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("🚀 UNIFIED REAL-TIME TRADING SYSTEM")
    print("=" * 50)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("☁️ Platform: Railway Cloud")
    print("💰 Mode: Paper Trading")
    print("🌐 Dashboard: Real-time monitoring")
    print("🔄 Trading: Continuous background execution")
    print()
    
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    # Start trading system in background thread (daemon so it dies with main process)
    trading_thread = threading.Thread(target=run_trading_system, daemon=True)
    trading_thread.start()
    
    # Give trading system time to initialize
    time.sleep(3)
    
    # Start dashboard (main thread)
    run_dashboard()