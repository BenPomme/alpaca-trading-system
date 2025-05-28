#!/usr/bin/env python3
"""
Simple Dashboard Only - For Railway Deployment
Minimal web interface to monitor trading system
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Simple status tracking
status_data = {
    'status': 'Dashboard Running',
    'started_at': datetime.now().isoformat(),
    'version': '1.0.0'
}

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify({
        'status': status_data['status'],
        'timestamp': datetime.now().isoformat(),
        'uptime': 'Dashboard active',
        'version': status_data['version']
    })

@app.route('/api/account')
def api_account():
    """API endpoint for account info - mock data for now"""
    try:
        # Try to get real data if possible
        from start_ultra_simple import UltraSimpleTrader
        trader = UltraSimpleTrader()
        account = trader.api.get_account()
        return jsonify({
            'portfolio_value': float(account.portfolio_value),
            'buying_power': float(account.buying_power),
            'cash': float(account.cash),
            'market_value': float(account.long_market_value or 0)
        })
    except Exception as e:
        # Return mock data if trading system fails
        return jsonify({
            'portfolio_value': 100000.78,
            'buying_power': 100000.00,
            'cash': 100000.00,
            'market_value': 0.78,
            'note': 'Mock data - trading system connecting...'
        })

@app.route('/api/logs')
def api_logs():
    """API endpoint for recent logs"""
    try:
        if os.path.exists('data/trading_log.json'):
            with open('data/trading_log.json', 'r') as f:
                logs = json.load(f)
            return jsonify(logs[-10:])
    except Exception:
        pass
    
    # Return mock logs
    return jsonify([
        {
            'timestamp': datetime.now().isoformat(),
            'cycle': {
                'regime': 'active',
                'strategy': 'momentum',
                'confidence': 0.8,
                'quotes_count': 3
            }
        }
    ])

@app.route('/api/market')
def api_market():
    """API endpoint for market data"""
    try:
        # Try to get real market data
        from start_ultra_simple import UltraSimpleTrader
        trader = UltraSimpleTrader()
        symbols = ['SPY', 'QQQ', 'IWM']
        market_data = []
        
        for symbol in symbols:
            quote = trader.get_quote(symbol)
            if quote:
                market_data.append({
                    'symbol': symbol,
                    'price': quote['ask'],
                    'timestamp': quote['timestamp']
                })
        
        return jsonify(market_data)
    except Exception:
        # Return mock market data
        return jsonify([
            {'symbol': 'SPY', 'price': 591.60, 'timestamp': datetime.now().isoformat()},
            {'symbol': 'QQQ', 'price': 522.34, 'timestamp': datetime.now().isoformat()},
            {'symbol': 'IWM', 'price': 207.92, 'timestamp': datetime.now().isoformat()}
        ])

@app.route('/api/cycle')
def api_cycle():
    """Run one trading cycle manually"""
    try:
        from start_ultra_simple import UltraSimpleTrader
        trader = UltraSimpleTrader()
        cycle_data = trader.run_cycle()
        return jsonify({'success': True, 'cycle': cycle_data})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🌐 Starting Trading Dashboard...")
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("☁️ Platform: Railway Cloud")
    print("📊 Dashboard: Ready")
    
    # Create templates directory if not exists
    os.makedirs('templates', exist_ok=True)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)