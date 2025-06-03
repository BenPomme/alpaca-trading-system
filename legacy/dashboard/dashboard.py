#!/usr/bin/env python3
"""
Simple Web Dashboard for Trading System
Minimal Flask app to monitor trading activity
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
import threading
import time

# Trading system import
from start_ultra_simple import UltraSimpleTrader

app = Flask(__name__)

class TradingDashboard:
    """Dashboard data provider"""
    
    def __init__(self):
        self.trader = None
        self.status = "Initializing..."
        self.last_cycle = None
        self.init_trader()
    
    def init_trader(self):
        """Initialize trading system"""
        try:
            self.trader = UltraSimpleTrader()
            self.status = "Connected"
        except Exception as e:
            self.status = f"Error: {e}"
    
    def get_status(self):
        """Get current system status"""
        return {
            'status': self.status,
            'timestamp': datetime.now().isoformat(),
            'last_cycle': self.last_cycle
        }
    
    def get_account_info(self):
        """Get account information"""
        if not self.trader:
            return {'error': 'Trader not initialized'}
        
        try:
            account = self.trader.api.get_account()
            return {
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'market_value': float(account.long_market_value or 0)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_recent_logs(self, limit=10):
        """Get recent trading logs"""
        try:
            if os.path.exists('data/trading_log.json'):
                with open('data/trading_log.json', 'r') as f:
                    logs = json.load(f)
                return logs[-limit:]
            return []
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_market_data(self):
        """Get current market data"""
        if not self.trader:
            return {'error': 'Trader not initialized'}
        
        try:
            symbols = ['SPY', 'QQQ', 'IWM']
            market_data = []
            
            for symbol in symbols:
                quote = self.trader.get_quote(symbol)
                if quote:
                    market_data.append({
                        'symbol': symbol,
                        'price': quote['ask'],
                        'timestamp': quote['timestamp']
                    })
            
            return market_data
        except Exception as e:
            return {'error': str(e)}

# Global dashboard instance
dashboard = TradingDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify(dashboard.get_status())

@app.route('/api/account')
def api_account():
    """API endpoint for account info"""
    return jsonify(dashboard.get_account_info())

@app.route('/api/logs')
def api_logs():
    """API endpoint for recent logs"""
    return jsonify(dashboard.get_recent_logs())

@app.route('/api/market')
def api_market():
    """API endpoint for market data"""
    return jsonify(dashboard.get_market_data())

@app.route('/api/cycle')
def api_cycle():
    """Run one trading cycle manually"""
    if not dashboard.trader:
        return jsonify({'error': 'Trader not initialized'})
    
    try:
        cycle_data = dashboard.trader.run_cycle()
        dashboard.last_cycle = cycle_data
        return jsonify({'success': True, 'cycle': cycle_data})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Create templates directory and HTML
    os.makedirs('templates', exist_ok=True)
    
    # Development server
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)