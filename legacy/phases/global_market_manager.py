#!/usr/bin/env python3
"""
Global Market Manager - Phase 4.1
Multi-timezone trading coordination and Asian market integration
"""

import datetime
import pytz
from typing import Dict, List, Tuple, Optional
import json
import os

class GlobalMarketManager:
    """Manages global market sessions and timezone-aware trading"""
    
    def __init__(self):
        self.market_sessions = self._initialize_market_sessions()
        self.asian_adrs = self._initialize_asian_adrs()
        self.global_symbols = self._build_global_symbol_universe()
        
    def _initialize_market_sessions(self) -> Dict:
        """Initialize trading sessions for major global markets"""
        return {
            'us_regular': {
                'timezone': 'America/New_York',
                'start_time': '09:30',
                'end_time': '16:00',
                'days': [0, 1, 2, 3, 4],  # Monday-Friday
                'symbol_prefix': '',
                'description': 'US Regular Market Hours'
            },
            'us_extended': {
                'timezone': 'America/New_York', 
                'start_time': '04:00',
                'end_time': '20:00',
                'days': [0, 1, 2, 3, 4],
                'symbol_prefix': '',
                'description': 'US Extended Hours'
            },
            'asia_japan': {
                'timezone': 'Asia/Tokyo',
                'start_time': '09:00',
                'end_time': '15:30',
                'days': [0, 1, 2, 3, 4],
                'symbol_prefix': 'ADR_',
                'description': 'Asian Market (Japan ADRs)'
            },
            'asia_hong_kong': {
                'timezone': 'Asia/Hong_Kong',
                'start_time': '09:30',
                'end_time': '16:00',
                'days': [0, 1, 2, 3, 4],
                'symbol_prefix': 'ADR_',
                'description': 'Asian Market (Hong Kong ADRs)'
            },
            'europe': {
                'timezone': 'Europe/London',
                'start_time': '08:00',
                'end_time': '16:30',
                'days': [0, 1, 2, 3, 4],
                'symbol_prefix': 'EUR_',
                'description': 'European Market Hours'
            }
        }
    
    def _initialize_asian_adrs(self) -> Dict:
        """Initialize Asian ADR symbols available on US exchanges"""
        return {
            # Japanese Companies (ADRs trading on NYSE/NASDAQ)
            'japan': {
                'TM': {'name': 'Toyota Motor Corp', 'sector': 'automotive', 'exchange': 'NYSE'},
                'SONY': {'name': 'Sony Group Corp', 'sector': 'technology', 'exchange': 'NYSE'},
                'NTDOY': {'name': 'Nintendo Co Ltd', 'sector': 'gaming', 'exchange': 'OTC'},
                'MUFG': {'name': 'Mitsubishi UFJ Financial', 'sector': 'financial', 'exchange': 'NYSE'},
                'SMFG': {'name': 'Sumitomo Mitsui Financial', 'sector': 'financial', 'exchange': 'NYSE'},
                'NMR': {'name': 'Nomura Holdings', 'sector': 'financial', 'exchange': 'NYSE'},
                'HMC': {'name': 'Honda Motor Co', 'sector': 'automotive', 'exchange': 'NYSE'},
                'NTT': {'name': 'Nippon Telegraph & Telephone', 'sector': 'telecom', 'exchange': 'NYSE'}
            },
            # South Korean Companies
            'korea': {
                'LPL': {'name': 'LG Display Co', 'sector': 'technology', 'exchange': 'NYSE'},
                'SKM': {'name': 'SK Telecom Co', 'sector': 'telecom', 'exchange': 'NYSE'},
                'KB': {'name': 'KB Financial Group', 'sector': 'financial', 'exchange': 'NYSE'}
            },
            # Chinese Companies (Hong Kong listed, US ADRs)
            'china': {
                'BABA': {'name': 'Alibaba Group', 'sector': 'ecommerce', 'exchange': 'NYSE'},
                'JD': {'name': 'JD.com Inc', 'sector': 'ecommerce', 'exchange': 'NASDAQ'},
                'BIDU': {'name': 'Baidu Inc', 'sector': 'technology', 'exchange': 'NASDAQ'},
                'NTES': {'name': 'NetEase Inc', 'sector': 'gaming', 'exchange': 'NASDAQ'},
                'TCEHY': {'name': 'Tencent Holdings', 'sector': 'technology', 'exchange': 'OTC'},
                'NIO': {'name': 'NIO Inc', 'sector': 'automotive', 'exchange': 'NYSE'},
                'XPEV': {'name': 'XPeng Inc', 'sector': 'automotive', 'exchange': 'NYSE'},
                'LI': {'name': 'Li Auto Inc', 'sector': 'automotive', 'exchange': 'NASDAQ'}
            },
            # Taiwan
            'taiwan': {
                'TSM': {'name': 'Taiwan Semiconductor', 'sector': 'semiconductor', 'exchange': 'NYSE'},
                'UMC': {'name': 'United Microelectronics', 'sector': 'semiconductor', 'exchange': 'NYSE'}
            },
            # India
            'india': {
                'INFY': {'name': 'Infosys Limited', 'sector': 'technology', 'exchange': 'NYSE'},
                'WIT': {'name': 'Wipro Limited', 'sector': 'technology', 'exchange': 'NYSE'},
                'HDB': {'name': 'HDFC Bank Limited', 'sector': 'financial', 'exchange': 'NYSE'},
                'IBN': {'name': 'ICICI Bank Limited', 'sector': 'financial', 'exchange': 'NYSE'}
            }
        }
    
    def _build_global_symbol_universe(self) -> Dict:
        """Build comprehensive global symbol universe"""
        global_universe = {}
        
        # Add all Asian ADRs to global universe
        for region, companies in self.asian_adrs.items():
            for symbol, info in companies.items():
                global_universe[symbol] = {
                    'region': region,
                    'sector': info['sector'],
                    'exchange': info['exchange'],
                    'name': info['name'],
                    'trading_session': self._get_primary_trading_session(region)
                }
        
        return global_universe
    
    def _get_primary_trading_session(self, region: str) -> str:
        """Get primary trading session for a region"""
        region_mapping = {
            'japan': 'asia_japan',
            'korea': 'asia_japan',  # Similar timezone
            'china': 'asia_hong_kong',
            'taiwan': 'asia_hong_kong',
            'india': 'asia_hong_kong',  # Close enough timezone
            'us': 'us_regular',
            'europe': 'europe'
        }
        return region_mapping.get(region, 'us_regular')
    
    def get_current_active_sessions(self) -> List[str]:
        """Get currently active trading sessions"""
        active_sessions = []
        current_utc = datetime.datetime.now(pytz.UTC)
        
        for session_name, session_info in self.market_sessions.items():
            if self.is_session_active(session_name, current_utc):
                active_sessions.append(session_name)
        
        return active_sessions
    
    def is_session_active(self, session_name: str, current_time: datetime.datetime = None) -> bool:
        """Check if a trading session is currently active"""
        if current_time is None:
            current_time = datetime.datetime.now(pytz.UTC)
        
        session = self.market_sessions.get(session_name)
        if not session:
            return False
        
        # Convert to session timezone
        session_tz = pytz.timezone(session['timezone'])
        local_time = current_time.astimezone(session_tz)
        
        # Check if it's a trading day
        if local_time.weekday() not in session['days']:
            return False
        
        # Check if within trading hours
        start_time = datetime.time(*map(int, session['start_time'].split(':')))
        end_time = datetime.time(*map(int, session['end_time'].split(':')))
        
        current_time_only = local_time.time()
        
        return start_time <= current_time_only <= end_time
    
    def get_tradeable_symbols_by_session(self, session_name: str) -> List[str]:
        """Get symbols that are most active during a specific session"""
        if session_name.startswith('asia'):
            # Return Asian ADRs for Asian sessions
            asian_symbols = []
            for symbol, info in self.global_symbols.items():
                if info['trading_session'] == session_name:
                    asian_symbols.append(symbol)
            return asian_symbols
        
        elif session_name.startswith('us'):
            # Return all US symbols plus Asian ADRs (they trade during US hours)
            from market_universe import get_symbols_by_tier
            us_symbols = get_symbols_by_tier(2)  # Get tier 2 US symbols
            asian_adrs = list(self.global_symbols.keys())
            return us_symbols + asian_adrs
        
        elif session_name == 'europe':
            # European ADRs and some US symbols
            return ['ASML', 'SAP', 'NVO', 'UL', 'BP', 'SHELL']  # European ADRs
        
        return []
    
    def get_optimal_trading_schedule(self) -> Dict:
        """Get 24/5 trading schedule with symbol priorities"""
        schedule = {}
        
        # Define trading periods throughout the week
        periods = [
            {
                'name': 'Asia Morning',
                'sessions': ['asia_japan', 'asia_hong_kong'],
                'priority_symbols': self.get_asian_momentum_symbols(),
                'strategy_focus': 'asian_breakout'
            },
            {
                'name': 'Europe/Asia Overlap',
                'sessions': ['europe', 'asia_hong_kong'],
                'priority_symbols': self.get_global_etfs() + self.get_currency_sensitive_symbols(),
                'strategy_focus': 'global_momentum'
            },
            {
                'name': 'US Pre-Market',
                'sessions': ['us_extended'],
                'priority_symbols': self.get_earnings_gappers() + self.get_news_reactive_symbols(),
                'strategy_focus': 'gap_trading'
            },
            {
                'name': 'US Regular',
                'sessions': ['us_regular'],
                'priority_symbols': self.get_high_volume_us_symbols(),
                'strategy_focus': 'momentum_breakout'
            },
            {
                'name': 'US After Hours',
                'sessions': ['us_extended'],
                'priority_symbols': self.get_earnings_reactive_symbols(),
                'strategy_focus': 'earnings_momentum'
            }
        ]
        
        return periods
    
    def get_asian_momentum_symbols(self) -> List[str]:
        """Get Asian ADR symbols suitable for momentum trading"""
        momentum_symbols = []
        for symbol, info in self.global_symbols.items():
            if info['region'] in ['japan', 'korea', 'china', 'taiwan']:
                if info['sector'] in ['technology', 'automotive', 'semiconductor']:
                    momentum_symbols.append(symbol)
        return momentum_symbols[:10]  # Top 10 for momentum
    
    def get_global_etfs(self) -> List[str]:
        """Get global/international ETFs"""
        return ['EWJ', 'FXI', 'EWT', 'INDA', 'EWY', 'VEA', 'VWO', 'IEFA']
    
    def get_currency_sensitive_symbols(self) -> List[str]:
        """Get symbols sensitive to currency movements"""
        return ['TM', 'SONY', 'TSM', 'BABA', 'ASML']
    
    def get_earnings_gappers(self) -> List[str]:
        """Get symbols that often gap on earnings"""
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']
    
    def get_news_reactive_symbols(self) -> List[str]:
        """Get symbols that react strongly to news"""
        return ['TSLA', 'GME', 'AMC', 'PLTR', 'SPCE', 'COIN', 'HOOD']
    
    def get_earnings_reactive_symbols(self) -> List[str]:
        """Get symbols that move significantly after earnings"""
        return ['NFLX', 'SPOT', 'UBER', 'LYFT', 'SNAP', 'TWTR', 'PINS']
    
    def get_high_volume_us_symbols(self) -> List[str]:
        """Get high volume US symbols for regular trading"""
        from market_universe import get_symbols_by_tier
        return get_symbols_by_tier(2)
    
    def get_next_trading_opportunity(self) -> Dict:
        """Get the next trading opportunity based on global schedule"""
        current_utc = datetime.datetime.now(pytz.UTC)
        active_sessions = self.get_current_active_sessions()
        
        if active_sessions:
            # Currently active session
            primary_session = active_sessions[0]
            return {
                'status': 'active',
                'session': primary_session,
                'symbols': self.get_tradeable_symbols_by_session(primary_session),
                'description': self.market_sessions[primary_session]['description']
            }
        else:
            # Find next upcoming session
            next_session = self._find_next_session(current_utc)
            return {
                'status': 'waiting',
                'next_session': next_session,
                'wait_time': self._calculate_wait_time(current_utc, next_session),
                'description': f"Waiting for {next_session}"
            }
    
    def _find_next_session(self, current_time: datetime.datetime) -> str:
        """Find the next upcoming trading session"""
        next_sessions = []
        
        for session_name, session_info in self.market_sessions.items():
            session_tz = pytz.timezone(session_info['timezone'])
            local_time = current_time.astimezone(session_tz)
            
            # Calculate next occurrence of this session
            next_occurrence = self._calculate_next_session_time(local_time, session_info)
            if next_occurrence:
                next_sessions.append((session_name, next_occurrence))
        
        if not next_sessions:
            return 'us_regular'  # Default fallback
        
        # Return the session that starts earliest
        next_sessions.sort(key=lambda x: x[1])
        return next_sessions[0][0]
    
    def _calculate_next_session_time(self, local_time: datetime.datetime, session_info: Dict) -> Optional[datetime.datetime]:
        """Calculate when the next session starts"""
        start_time = datetime.time(*map(int, session_info['start_time'].split(':')))
        today = local_time.date()
        
        # Try today first
        if today.weekday() in session_info['days']:
            session_start = datetime.datetime.combine(today, start_time)
            session_start = session_start.replace(tzinfo=local_time.tzinfo)
            if session_start > local_time:
                return session_start
        
        # Try next few days
        for days_ahead in range(1, 8):
            future_date = today + datetime.timedelta(days=days_ahead)
            if future_date.weekday() in session_info['days']:
                session_start = datetime.datetime.combine(future_date, start_time)
                session_start = session_start.replace(tzinfo=local_time.tzinfo)
                return session_start
        
        return None
    
    def _calculate_wait_time(self, current_time: datetime.datetime, next_session: str) -> str:
        """Calculate human-readable wait time until next session"""
        session_info = self.market_sessions.get(next_session)
        if not session_info:
            return "Unknown"
        
        session_tz = pytz.timezone(session_info['timezone'])
        local_time = current_time.astimezone(session_tz)
        next_start = self._calculate_next_session_time(local_time, session_info)
        
        if not next_start:
            return "Unknown"
        
        time_diff = next_start - local_time
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    
    def get_global_market_status(self) -> Dict:
        """Get comprehensive global market status"""
        current_utc = datetime.datetime.now(pytz.UTC)
        status = {
            'timestamp': current_utc.isoformat(),
            'active_sessions': [],
            'upcoming_sessions': [],
            'tradeable_symbols': [],
            'total_global_symbols': len(self.global_symbols)
        }
        
        # Check all sessions
        for session_name, session_info in self.market_sessions.items():
            if self.is_session_active(session_name, current_utc):
                status['active_sessions'].append({
                    'name': session_name,
                    'description': session_info['description'],
                    'symbols': self.get_tradeable_symbols_by_session(session_name)
                })
                status['tradeable_symbols'].extend(self.get_tradeable_symbols_by_session(session_name))
        
        # Remove duplicates from tradeable symbols
        status['tradeable_symbols'] = list(set(status['tradeable_symbols']))
        
        return status

def test_global_market_manager():
    """Test the global market manager functionality"""
    print("🌍 Testing Global Market Manager...")
    
    gmm = GlobalMarketManager()
    
    # Test market sessions
    print(f"✅ Market Sessions: {len(gmm.market_sessions)} sessions configured")
    for session_name, session_info in gmm.market_sessions.items():
        print(f"   📅 {session_name}: {session_info['description']}")
    
    # Test Asian ADRs
    print(f"✅ Asian ADRs: {len(gmm.global_symbols)} symbols across regions")
    for region, companies in gmm.asian_adrs.items():
        print(f"   🏢 {region.title()}: {len(companies)} companies")
    
    # Test current status
    active_sessions = gmm.get_current_active_sessions()
    print(f"✅ Currently Active Sessions: {active_sessions}")
    
    # Test next opportunity
    next_opportunity = gmm.get_next_trading_opportunity()
    print(f"✅ Next Trading Opportunity: {next_opportunity}")
    
    # Test global status
    global_status = gmm.get_global_market_status()
    print(f"✅ Global Market Status: {len(global_status['active_sessions'])} active, {len(global_status['tradeable_symbols'])} symbols")
    
    print("🎉 Global Market Manager tests completed!")
    
    return gmm

if __name__ == "__main__":
    test_global_market_manager()