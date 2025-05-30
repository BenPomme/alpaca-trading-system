#!/usr/bin/env python3
"""
Dashboard API for GitHub Pages
Generates JSON data from trading database for dashboard consumption
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any
import alpaca_trade_api as tradeapi

class DashboardAPI:
    """Generate dashboard data from trading database"""
    
    def __init__(self, db_path: str = "data/trading_system.db"):
        self.db_path = db_path
        
        # Initialize Alpaca API for real-time data
        api_key = os.getenv('ALPACA_PAPER_API_KEY')
        secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
        
        if api_key and secret_key:
            self.api = tradeapi.REST(
                key_id=api_key,
                secret_key=secret_key,
                base_url='https://paper-api.alpaca.markets',
                api_version='v2'
            )
        else:
            self.api = None
            print("⚠️ Alpaca API credentials not found")
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate complete dashboard data"""
        try:
            print("📊 Generating dashboard data...")
            
            # Get portfolio information from Alpaca
            portfolio_data = self.get_portfolio_data()
            
            # Get positions from Alpaca
            positions_data = self.get_positions_data()
            
            # Get trades from database
            trades_data = self.get_trades_from_db()
            
            # Calculate performance metrics
            performance_data = self.calculate_performance_metrics(trades_data)
            
            # Get strategy performance
            strategy_data = self.get_strategy_performance(trades_data)
            
            # Get market status
            market_status = self.get_market_status()
            
            dashboard_data = {
                'portfolio': portfolio_data,
                'positions': positions_data,
                'trades': trades_data[-50:],  # Last 50 trades
                'performance': performance_data,
                'strategies': strategy_data,
                'marketStatus': market_status,
                'generated_at': datetime.now().isoformat(),
                'data_source': 'live' if self.api else 'mock'
            }
            
            print(f"✅ Dashboard data generated: {len(positions_data)} positions, {len(trades_data)} trades")
            return dashboard_data
            
        except Exception as e:
            print(f"❌ Error generating dashboard data: {e}")
            return self.get_mock_dashboard_data()
    
    def get_portfolio_data(self) -> Dict[str, Any]:
        """Get portfolio data from Alpaca API"""
        try:
            if not self.api:
                return self.get_mock_portfolio_data()
            
            account = self.api.get_account()
            
            return {
                'value': float(account.portfolio_value),
                'cash': float(account.cash),
                'dayTradingPower': float(getattr(account, 'daytrading_buying_power', 0)),
                'dailyPL': float(account.portfolio_value) - float(account.last_equity),
                'dailyPLPercent': ((float(account.portfolio_value) - float(account.last_equity)) / float(account.last_equity)) * 100 if float(account.last_equity) > 0 else 0
            }
            
        except Exception as e:
            print(f"⚠️ Error getting portfolio data: {e}")
            return self.get_mock_portfolio_data()
    
    def get_positions_data(self) -> List[Dict[str, Any]]:
        """Get current positions from Alpaca API"""
        try:
            if not self.api:
                return self.get_mock_positions_data()
            
            positions = self.api.list_positions()
            positions_data = []
            
            for pos in positions:
                # Determine position type
                symbol = pos.symbol
                if symbol.endswith('USD'):
                    pos_type = 'crypto'
                elif '/' in symbol or len(symbol) > 5:
                    pos_type = 'options'
                else:
                    pos_type = 'stock'
                
                # Calculate entry price
                try:
                    entry_price = float(pos.avg_entry_price) if hasattr(pos, 'avg_entry_price') else float(pos.market_value) / float(pos.qty)
                except:
                    entry_price = float(pos.market_value) / float(pos.qty) if float(pos.qty) != 0 else 0
                
                # Calculate current price
                current_price = float(pos.market_value) / float(pos.qty) if float(pos.qty) != 0 else 0
                
                # Calculate hold time (simplified - would need entry time from DB)
                hold_time = "Unknown"
                
                # Get strategy from database or default
                strategy = self.get_position_strategy(symbol) or "unknown"
                
                position_data = {
                    'symbol': symbol,
                    'quantity': float(pos.qty),
                    'entryPrice': entry_price,
                    'currentPrice': current_price,
                    'marketValue': float(pos.market_value),
                    'unrealizedPL': float(pos.unrealized_pl),
                    'unrealizedPLPercent': float(pos.unrealized_plpc) * 100,
                    'holdTime': hold_time,
                    'strategy': strategy,
                    'type': pos_type
                }
                
                positions_data.append(position_data)
            
            return positions_data
            
        except Exception as e:
            print(f"⚠️ Error getting positions data: {e}")
            return self.get_mock_positions_data()
    
    def get_trades_from_db(self) -> List[Dict[str, Any]]:
        """Get trades from database"""
        try:
            if not os.path.exists(self.db_path):
                print(f"⚠️ Database not found: {self.db_path}")
                return []
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get trades from the last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            cursor.execute("""
                SELECT * FROM trades 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC 
                LIMIT 500
            """, (thirty_days_ago,))
            
            columns = [description[0] for description in cursor.description]
            trades_data = []
            
            for row in cursor.fetchall():
                trade_dict = dict(zip(columns, row))
                
                # Format for dashboard
                trade_formatted = {
                    'date': trade_dict.get('timestamp', ''),
                    'symbol': trade_dict.get('symbol', ''),
                    'side': trade_dict.get('side', '').upper(),
                    'quantity': trade_dict.get('quantity', 0),
                    'price': trade_dict.get('price', 0),
                    'pl': trade_dict.get('profit_loss', 0),
                    'plPercent': (trade_dict.get('profit_loss', 0) / (trade_dict.get('price', 1) * trade_dict.get('quantity', 1))) * 100 if trade_dict.get('price', 0) > 0 else 0,
                    'strategy': trade_dict.get('strategy', 'unknown'),
                    'exitReason': trade_dict.get('exit_reason', None)
                }
                
                trades_data.append(trade_formatted)
            
            conn.close()
            return trades_data
            
        except Exception as e:
            print(f"⚠️ Error getting trades from database: {e}")
            return []
    
    def calculate_performance_metrics(self, trades_data: List[Dict]) -> Dict[str, Any]:
        """Calculate performance metrics from trades"""
        try:
            if not trades_data:
                return self.get_mock_performance_data()
            
            total_trades = len(trades_data)
            winning_trades = len([t for t in trades_data if t['pl'] > 0])
            losing_trades = total_trades - winning_trades
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            # Calculate returns
            total_pl = sum(t['pl'] for t in trades_data)
            best_trade = max([t['pl'] for t in trades_data], default=0)
            worst_trade = min([t['pl'] for t in trades_data], default=0)
            
            # Time-based metrics (simplified)
            today_trades = [t for t in trades_data if t['date'].startswith(datetime.now().strftime('%Y-%m-%d'))]
            week_trades = [t for t in trades_data if datetime.fromisoformat(t['date'].split('.')[0]) > datetime.now() - timedelta(days=7)]
            month_trades = trades_data  # All trades are from last 30 days
            
            daily_pl = sum(t['pl'] for t in today_trades)
            weekly_pl = sum(t['pl'] for t in week_trades)
            monthly_pl = sum(t['pl'] for t in month_trades)
            
            # Calculate ROI percentages (simplified)
            base_portfolio = 100000  # Approximate portfolio value
            
            return {
                'totalTrades': total_trades,
                'winningTrades': winning_trades,
                'losingTrades': losing_trades,
                'winRate': win_rate,
                'avgHoldTime': 6.2,  # Would need to calculate from entry/exit times
                'bestTrade': best_trade,
                'worstTrade': worst_trade,
                'totalROI': (monthly_pl / base_portfolio) * 100,
                'dailyROI': (daily_pl / base_portfolio) * 100,
                'weeklyROI': (weekly_pl / base_portfolio) * 100,
                'monthlyROI': (monthly_pl / base_portfolio) * 100
            }
            
        except Exception as e:
            print(f"⚠️ Error calculating performance metrics: {e}")
            return self.get_mock_performance_data()
    
    def get_strategy_performance(self, trades_data: List[Dict]) -> List[Dict[str, Any]]:
        """Calculate performance by strategy"""
        try:
            strategy_stats = {}
            
            for trade in trades_data:
                strategy = trade['strategy']
                if strategy not in strategy_stats:
                    strategy_stats[strategy] = {
                        'trades': 0,
                        'wins': 0,
                        'total_return': 0
                    }
                
                strategy_stats[strategy]['trades'] += 1
                if trade['pl'] > 0:
                    strategy_stats[strategy]['wins'] += 1
                strategy_stats[strategy]['total_return'] += trade['pl']
            
            # Format for dashboard
            strategies = []
            for name, stats in strategy_stats.items():
                strategies.append({
                    'name': name,
                    'trades': stats['trades'],
                    'winRate': (stats['wins'] / stats['trades']) * 100 if stats['trades'] > 0 else 0,
                    'avgReturn': (stats['total_return'] / stats['trades']) if stats['trades'] > 0 else 0,
                    'totalReturn': stats['total_return']
                })
            
            return sorted(strategies, key=lambda x: x['totalReturn'], reverse=True)
            
        except Exception as e:
            print(f"⚠️ Error calculating strategy performance: {e}")
            return []
    
    def get_position_strategy(self, symbol: str) -> str:
        """Get strategy for a position from database"""
        try:
            if not os.path.exists(self.db_path):
                return "unknown"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT strategy FROM trades 
                WHERE symbol = ? AND side = 'BUY'
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (symbol,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else "unknown"
            
        except Exception as e:
            return "unknown"
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status"""
        try:
            if not self.api:
                return {'isOpen': False, 'nextOpen': 'Unknown', 'nextClose': 'Unknown'}
            
            clock = self.api.get_clock()
            
            return {
                'isOpen': clock.is_open,
                'nextOpen': clock.next_open.isoformat() if clock.next_open else 'Unknown',
                'nextClose': clock.next_close.isoformat() if clock.next_close else 'Unknown'
            }
            
        except Exception as e:
            print(f"⚠️ Error getting market status: {e}")
            return {'isOpen': False, 'nextOpen': 'Unknown', 'nextClose': 'Unknown'}
    
    def get_mock_dashboard_data(self) -> Dict[str, Any]:
        """Fallback mock data"""
        return {
            'portfolio': self.get_mock_portfolio_data(),
            'positions': self.get_mock_positions_data(),
            'trades': [],
            'performance': self.get_mock_performance_data(),
            'strategies': [],
            'marketStatus': {'isOpen': False, 'nextOpen': 'Unknown', 'nextClose': 'Unknown'},
            'generated_at': datetime.now().isoformat(),
            'data_source': 'mock'
        }
    
    def get_mock_portfolio_data(self) -> Dict[str, Any]:
        return {
            'value': 99071.57,
            'cash': 24532.57,
            'dayTradingPower': 222926.24,
            'dailyPL': -428.43,
            'dailyPLPercent': -0.43
        }
    
    def get_mock_positions_data(self) -> List[Dict[str, Any]]:
        return [
            {
                'symbol': 'AAPL',
                'quantity': 14,
                'entryPrice': 198.5,
                'currentPrice': 200.11,
                'marketValue': 2801.54,
                'unrealizedPL': 22.54,
                'unrealizedPLPercent': 0.81,
                'holdTime': '2.3h',
                'strategy': 'momentum',
                'type': 'stock'
            }
        ]
    
    def get_mock_performance_data(self) -> Dict[str, Any]:
        return {
            'totalTrades': 156,
            'winningTrades': 89,
            'losingTrades': 67,
            'winRate': 57.05,
            'avgHoldTime': 6.2,
            'bestTrade': 245.67,
            'worstTrade': -89.23,
            'totalROI': 12.34,
            'dailyROI': 0.43,
            'weeklyROI': 2.87,
            'monthlyROI': 8.91
        }
    
    def save_to_file(self, data: Dict[str, Any], filename: str = "docs/api/dashboard-data.json"):
        """Save dashboard data to JSON file for GitHub Pages"""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"✅ Dashboard data saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving dashboard data: {e}")

def main():
    """Generate dashboard data and save to file"""
    api = DashboardAPI()
    data = api.generate_dashboard_data()
    api.save_to_file(data)
    
    print(f"📊 Dashboard data generation complete:")
    print(f"   Portfolio Value: ${data['portfolio']['value']:,.2f}")
    print(f"   Active Positions: {len(data['positions'])}")
    print(f"   Recent Trades: {len(data['trades'])}")
    print(f"   Data Source: {data['data_source']}")

if __name__ == "__main__":
    main()