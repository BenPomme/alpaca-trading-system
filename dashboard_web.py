#!/usr/bin/env python3
"""
Dashboard Web Service
Dedicated web interface that reads data from trading worker
Lightweight service focused only on data presentation
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify

app = Flask(__name__)

class DashboardService:
    """Dashboard service that reads worker data"""
    
    def __init__(self):
        self.worker_status_file = 'data/worker_status.json'
        self.trading_log_file = 'data/trading_log.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        print("✅ Dashboard service initialized")
    
    def get_worker_status(self):
        """Read worker status from shared file"""
        try:
            if os.path.exists(self.worker_status_file):
                with open(self.worker_status_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'status': 'Worker not found - may be starting up',
                    'timestamp': datetime.now().isoformat(),
                    'worker_type': 'unknown',
                    'cycle_count': 0
                }
        except Exception as e:
            return {
                'status': f'Error reading worker status: {e}',
                'timestamp': datetime.now().isoformat(),
                'error': True
            }
    
    def get_account_info(self):
        """Get account info by connecting directly to Alpaca"""
        try:
            from start_ultra_simple import UltraSimpleTrader
            trader = UltraSimpleTrader()
            account = trader.api.get_account()
            return {
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'market_value': float(account.long_market_value or 0),
                'updated_at': datetime.now().isoformat(),
                'source': 'direct_api'
            }
        except Exception as e:
            return {
                'error': f'Account connection failed: {e}',
                'source': 'error'
            }
    
    def get_market_data(self):
        """Get live market data"""
        try:
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
            
            return market_data
        except Exception as e:
            return {'error': f'Market data failed: {e}'}
    
    def get_trading_logs(self, limit=10):
        """Get trading logs from worker and file"""
        logs = []
        
        # Get worker's last cycle
        worker_status = self.get_worker_status()
        if worker_status.get('last_cycle'):
            logs.append({
                'type': 'worker_cycle',
                'timestamp': worker_status['timestamp'],
                'data': worker_status['last_cycle']
            })
        
        # Get file logs
        try:
            if os.path.exists(self.trading_log_file):
                with open(self.trading_log_file, 'r') as f:
                    file_logs = json.load(f)
                for log in file_logs[-limit:]:
                    logs.append({
                        'type': 'file_log',
                        'timestamp': log.get('timestamp', 'N/A'),
                        'data': log.get('cycle', log)
                    })
        except Exception as e:
            logs.append({
                'type': 'error',
                'timestamp': datetime.now().isoformat(),
                'data': {'error': f'Log read error: {e}'}
            })
        
        return logs[-limit:]

# Global dashboard instance
dashboard = DashboardService()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """System status from worker"""
    worker_status = dashboard.get_worker_status()
    
    # Add dashboard info
    dashboard_status = {
        'dashboard_service': 'running',
        'dashboard_timestamp': datetime.now().isoformat(),
        'worker_status': worker_status.get('status', 'Unknown'),
        'worker_cycle_count': worker_status.get('cycle_count', 0),
        'worker_uptime': worker_status.get('uptime_seconds', 0),
        'last_worker_update': worker_status.get('timestamp', 'Never'),
        'architecture': 'dual_service'
    }
    
    return jsonify(dashboard_status)

@app.route('/api/account')
def api_account():
    """Account information"""
    return jsonify(dashboard.get_account_info())

@app.route('/api/market')
def api_market():
    """Live market data"""
    return jsonify(dashboard.get_market_data())

@app.route('/api/logs')
def api_logs():
    """Trading activity logs"""
    return jsonify(dashboard.get_trading_logs())

@app.route('/api/worker')
def api_worker():
    """Worker service status"""
    return jsonify(dashboard.get_worker_status())

@app.route('/api/cycle')
def api_manual_cycle():
    """Manual cycle execution (creates request for worker)"""
    try:
        # Create a request file for the worker to pick up
        request_file = 'data/manual_cycle_request.json'
        request_data = {
            'requested_at': datetime.now().isoformat(),
            'requested_by': 'dashboard',
            'type': 'manual_cycle'
        }
        
        with open(request_file, 'w') as f:
            json.dump(request_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Manual cycle requested - worker will process on next iteration',
            'request_file': request_file
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/health')
def health():
    """Health check for Railway"""
    worker_status = dashboard.get_worker_status()
    
    return jsonify({
        'dashboard_status': 'healthy',
        'worker_connected': not worker_status.get('error', False),
        'timestamp': datetime.now().isoformat(),
        'service_type': 'dashboard_web'
    })

if __name__ == '__main__':
    print("🌐 DASHBOARD WEB SERVICE")
    print("=" * 40)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("☁️ Platform: Railway Cloud (Web Service)")
    print("📊 Type: Data presentation and monitoring")
    print("🔗 Communication: Reads worker JSON files")
    print("🎯 Purpose: Real-time trading system dashboard")
    print()
    
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Dashboard starting on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)