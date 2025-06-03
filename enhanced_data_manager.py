#!/usr/bin/env python3
"""
Enhanced Data Manager - Multi-Source Data Integration
Provides robust data fetching with fallbacks while preserving Alpaca as primary source
Maintains Firebase + Railway compatibility
"""

import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Union, Any
import numpy as np
import pandas as pd

# Primary data source (PRESERVE - Required for trading)
try:
    from alpaca.trading.client import TradingClient
    from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
    from alpaca.data.live import StockDataStream, CryptoDataStream
    from alpaca.data.requests import StockLatestQuoteRequest, CryptoLatestQuoteRequest
    ALPACA_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Alpaca API not available: {e}")
    ALPACA_AVAILABLE = False

# Enhanced data sources (NEW - Phase 2)
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    print("⚠️ yfinance not available - install with: pip install yfinance")
    YFINANCE_AVAILABLE = False

try:
    from alpha_vantage.timeseries import TimeSeries
    from alpha_vantage.techindicators import TechIndicators
    ALPHA_VANTAGE_AVAILABLE = True
except ImportError:
    print("⚠️ alpha-vantage not available - install with: pip install alpha-vantage")
    ALPHA_VANTAGE_AVAILABLE = False

try:
    import finnhub
    FINNHUB_AVAILABLE = True
except ImportError:
    print("⚠️ finnhub not available - install with: pip install finnhub-python")
    FINNHUB_AVAILABLE = False


class EnhancedDataManager:
    """
    Multi-source data manager with Alpaca as primary source
    Provides fallback data sources for enhanced reliability and enrichment
    """
    
    def __init__(self, api_client=None, alpaca_api_key: str = None, alpaca_secret_key: str = None, 
                 alpha_vantage_key: str = None, finnhub_key: str = None,
                 logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Use injected API client if available (from modules)
        self.api_client = api_client
        
        # Initialize Alpaca (PRIMARY - Required for trading)
        self.alpaca_available = False
        if ALPACA_AVAILABLE and (api_client or (alpaca_api_key and alpaca_secret_key)):
            try:
                if api_client:
                    # Use injected client
                    self.trading_client = api_client
                    self.alpaca_available = True
                    self.logger.info("✅ Alpaca API client injected (PRIMARY)")
                else:
                    # Initialize new client
                    self.trading_client = TradingClient(alpaca_api_key, alpaca_secret_key, paper=True)
                    self.stock_data_client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret_key)
                    self.crypto_data_client = CryptoHistoricalDataClient(alpaca_api_key, alpaca_secret_key)
                    self.alpaca_available = True
                    self.logger.info("✅ Alpaca API initialized (PRIMARY)")
            except Exception as e:
                self.logger.error(f"❌ Alpaca initialization failed: {e}")
        
        # Initialize enhanced data sources (REAL-TIME/ENRICHMENT)
        self.yfinance_available = YFINANCE_AVAILABLE
        if self.yfinance_available:
            self.logger.info("✅ yfinance available (FALLBACK)")
            
        self.alpha_vantage_available = False
        if ALPHA_VANTAGE_AVAILABLE and alpha_vantage_key:
            try:
                self.av_timeseries = TimeSeries(key=alpha_vantage_key, output_format='pandas')
                self.av_tech = TechIndicators(key=alpha_vantage_key, output_format='pandas')
                self.av_key = alpha_vantage_key
                self.alpha_vantage_available = True
                self.logger.info("✅ Alpha Vantage initialized (REAL-TIME ENRICHMENT)")
            except Exception as e:
                self.logger.warning(f"⚠️ Alpha Vantage initialization failed: {e}")
        
        self.finnhub_available = False
        if FINNHUB_AVAILABLE and finnhub_key:
            try:
                self.finnhub_client = finnhub.Client(api_key=finnhub_key)
                self.finnhub_key = finnhub_key
                self.finnhub_available = True
                self.logger.info("✅ Finnhub initialized (REAL-TIME ENRICHMENT)")
            except Exception as e:
                self.logger.warning(f"⚠️ Finnhub initialization failed: {e}")
    
    def get_latest_quote(self, symbol: str, fallback: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get latest quote with fallback chain: Alpaca -> yfinance
        Returns standardized quote format
        """
        quote = None
        source = "unknown"
        
        # PRIMARY: Try Alpaca first (required for trading execution)
        if self.alpaca_available:
            try:
                if '/' in symbol:  # Crypto format
                    request = CryptoLatestQuoteRequest(symbol_or_symbols=[symbol])
                    quotes = self.crypto_data_client.get_crypto_latest_quote(request)
                    if symbol in quotes:
                        alpaca_quote = quotes[symbol]
                        quote = {
                            'symbol': symbol,
                            'bid': float(alpaca_quote.bid_price),
                            'ask': float(alpaca_quote.ask_price),
                            'timestamp': alpaca_quote.timestamp,
                            'source': 'alpaca',
                            'bid_size': alpaca_quote.bid_size,
                            'ask_size': alpaca_quote.ask_size
                        }
                        source = "alpaca"
                else:  # Stock format
                    request = StockLatestQuoteRequest(symbol_or_symbols=[symbol])
                    quotes = self.stock_data_client.get_stock_latest_quote(request)
                    if symbol in quotes:
                        alpaca_quote = quotes[symbol]
                        quote = {
                            'symbol': symbol,
                            'bid': float(alpaca_quote.bid_price),
                            'ask': float(alpaca_quote.ask_price),
                            'timestamp': alpaca_quote.timestamp,
                            'source': 'alpaca',
                            'bid_size': alpaca_quote.bid_size,
                            'ask_size': alpaca_quote.ask_size
                        }
                        source = "alpaca"
            except Exception as e:
                self.logger.warning(f"⚠️ Alpaca quote failed for {symbol}: {e}")
        
        # FALLBACK: Try yfinance if Alpaca failed and fallback enabled
        if quote is None and fallback and self.yfinance_available:
            try:
                # Convert crypto symbols from Alpaca format to yfinance format
                yf_symbol = self._convert_symbol_for_yfinance(symbol)
                ticker = yf.Ticker(yf_symbol)
                info = ticker.fast_info
                
                quote = {
                    'symbol': symbol,
                    'bid': float(info.get('bid', info.get('regularMarketPrice', 0))),
                    'ask': float(info.get('ask', info.get('regularMarketPrice', 0))),
                    'timestamp': datetime.now(timezone.utc),
                    'source': 'yfinance',
                    'last_price': float(info.get('regularMarketPrice', 0)),
                    'volume': int(info.get('regularMarketVolume', 0))
                }
                source = "yfinance"
                self.logger.info(f"📈 yfinance fallback used for {symbol}")
                
            except Exception as e:
                self.logger.warning(f"⚠️ yfinance fallback failed for {symbol}: {e}")
        
        if quote:
            self.logger.debug(f"✅ Quote retrieved for {symbol} from {source}")
            return quote
        else:
            self.logger.error(f"❌ All data sources failed for {symbol}")
            return None
    
    def _convert_symbol_for_yfinance(self, symbol: str) -> str:
        """Convert symbol from Alpaca format to yfinance format"""
        # Handle crypto symbols: BTCUSD -> BTC-USD
        crypto_mappings = {
            'BTCUSD': 'BTC-USD',
            'ETHUSD': 'ETH-USD', 
            'SOLUSD': 'SOL-USD',
            'AVAXUSD': 'AVAX-USD',
            'ADAUSD': 'ADA-USD',
            'DOTUSD': 'DOT-USD',
            'LINKUSD': 'LINK-USD',
            'UNIUSD': 'UNI-USD',
            'AAVEUSD': 'AAVE-USD',
            'MATICUSD': 'MATIC-USD',
            'ALGOUSD': 'ALGO-USD'
        }
        
        # Return mapped symbol if it's a crypto, otherwise return as-is
        return crypto_mappings.get(symbol, symbol)
    
    def get_historical_data(self, symbol: str, period: str = "1mo", 
                          interval: str = "1d", fallback: bool = True) -> Optional[pd.DataFrame]:
        """
        Get historical data with fallback
        Returns pandas DataFrame with OHLCV data
        """
        data = None
        source = "unknown"
        
        # PRIMARY: Try Alpaca first
        if self.alpaca_available:
            try:
                # Convert period to start/end dates for Alpaca
                end_date = datetime.now(timezone.utc)
                if period == "1mo":
                    start_date = end_date - timedelta(days=30)
                elif period == "3mo":
                    start_date = end_date - timedelta(days=90)
                elif period == "1y":
                    start_date = end_date - timedelta(days=365)
                else:
                    start_date = end_date - timedelta(days=30)
                
                # Alpaca historical data implementation would go here
                # This is a placeholder for Alpaca historical data
                pass
                
            except Exception as e:
                self.logger.warning(f"⚠️ Alpaca historical data failed for {symbol}: {e}")
        
        # FALLBACK: Try yfinance
        if data is None and fallback and self.yfinance_available:
            try:
                # Convert crypto symbols for yfinance compatibility
                yf_symbol = self._convert_symbol_for_yfinance(symbol)
                ticker = yf.Ticker(yf_symbol)
                data = ticker.history(period=period, interval=interval)
                
                if not data.empty:
                    # Standardize column names
                    data.columns = [col.lower().replace(' ', '_') for col in data.columns]
                    data['source'] = 'yfinance'
                    source = "yfinance"
                    self.logger.info(f"📈 yfinance historical data used for {symbol}")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ yfinance historical data failed for {symbol}: {e}")
        
        return data
    
    def get_real_time_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time quote using Finnhub (preferred) -> Alpha Vantage -> Alpaca chain
        Returns standardized real-time quote format
        """
        quote = None
        source = "unknown"
        
        # PRIMARY REAL-TIME: Try Finnhub first for most up-to-date data
        if self.finnhub_available:
            try:
                # Convert symbol format for Finnhub (remove USD suffix for crypto)
                fh_symbol = symbol.replace('USD', '') if 'USD' in symbol else symbol
                
                if 'USD' in symbol:  # Crypto symbol
                    quote_data = self.finnhub_client.crypto_candles(fh_symbol + 'USDT', 'D', 
                                                                   int(time.time()) - 86400, 
                                                                   int(time.time()))
                    if quote_data and quote_data.get('c') and len(quote_data['c']) > 0:
                        latest_price = quote_data['c'][-1]  # Latest close price
                        quote = {
                            'symbol': symbol,
                            'price': float(latest_price),
                            'bid': float(latest_price) * 0.999,  # Estimate spread
                            'ask': float(latest_price) * 1.001,
                            'timestamp': datetime.now(timezone.utc),
                            'source': 'finnhub_crypto',
                            'real_time': True
                        }
                        source = "finnhub_crypto"
                else:  # Stock symbol
                    quote_data = self.finnhub_client.quote(symbol)
                    if quote_data and quote_data.get('c'):
                        quote = {
                            'symbol': symbol,
                            'price': float(quote_data['c']),
                            'bid': float(quote_data.get('pc', quote_data['c'])),  # Previous close as bid fallback
                            'ask': float(quote_data['c']),
                            'timestamp': datetime.fromtimestamp(quote_data.get('t', time.time()), timezone.utc),
                            'source': 'finnhub_stock',
                            'real_time': True,
                            'change': float(quote_data.get('d', 0)),
                            'change_percent': float(quote_data.get('dp', 0))
                        }
                        source = "finnhub_stock"
                        
                self.logger.debug(f"✅ Finnhub real-time quote for {symbol}: ${quote['price']:.4f}")
                        
            except Exception as e:
                self.logger.warning(f"⚠️ Finnhub real-time quote failed for {symbol}: {e}")
        
        # SECONDARY REAL-TIME: Try Alpha Vantage if Finnhub failed
        if quote is None and self.alpha_vantage_available:
            try:
                if 'USD' in symbol:  # Crypto
                    crypto_symbol = symbol.replace('USD', '')
                    # Use Alpha Vantage crypto endpoint
                    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={crypto_symbol}&to_currency=USD&apikey={self.av_key}"
                    import requests
                    response = requests.get(url, timeout=10)
                    data = response.json()
                    
                    if 'Realtime Currency Exchange Rate' in data:
                        rate_data = data['Realtime Currency Exchange Rate']
                        price = float(rate_data['5. Exchange Rate'])
                        quote = {
                            'symbol': symbol,
                            'price': price,
                            'bid': price * 0.999,
                            'ask': price * 1.001,
                            'timestamp': datetime.now(timezone.utc),
                            'source': 'alpha_vantage_crypto',
                            'real_time': True
                        }
                        source = "alpha_vantage_crypto"
                else:  # Stock
                    # Use Alpha Vantage GLOBAL_QUOTE for real-time stock data
                    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.av_key}"
                    import requests
                    response = requests.get(url, timeout=10)
                    data = response.json()
                    
                    if 'Global Quote' in data:
                        quote_data = data['Global Quote']
                        price = float(quote_data['05. price'])
                        quote = {
                            'symbol': symbol,
                            'price': price,
                            'bid': price * 0.999,
                            'ask': price * 1.001,
                            'timestamp': datetime.now(timezone.utc),
                            'source': 'alpha_vantage_stock',
                            'real_time': True,
                            'change': float(quote_data.get('09. change', 0)),
                            'change_percent': quote_data.get('10. change percent', '0%').replace('%', '')
                        }
                        source = "alpha_vantage_stock"
                        
                self.logger.debug(f"✅ Alpha Vantage real-time quote for {symbol}: ${quote['price']:.4f}")
                        
            except Exception as e:
                self.logger.warning(f"⚠️ Alpha Vantage real-time quote failed for {symbol}: {e}")
        
        # FALLBACK: Use existing get_latest_quote method
        if quote is None:
            quote = self.get_latest_quote(symbol, fallback=True)
            if quote:
                quote['real_time'] = False
                source = quote.get('source', 'fallback')
        
        if quote:
            self.logger.debug(f"✅ Real-time quote retrieved for {symbol} from {source}")
            return quote
        else:
            self.logger.error(f"❌ All real-time data sources failed for {symbol}")
            return None
    
    def get_enhanced_quote_data(self, symbol: str, include_fundamentals: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive quote data combining real-time price with technical indicators
        """
        try:
            # Get real-time quote
            quote = self.get_real_time_quote(symbol)
            if not quote:
                return None
            
            # Get historical data for technical analysis
            historical_data = self.get_historical_data(symbol, period="1mo", interval="1d")
            
            enhanced_data = {
                'symbol': symbol,
                'current_price': quote['price'],
                'bid': quote.get('bid', quote['price']),
                'ask': quote.get('ask', quote['price']),
                'timestamp': quote['timestamp'],
                'source': quote['source'],
                'real_time': quote.get('real_time', False),
                'change': quote.get('change', 0),
                'change_percent': quote.get('change_percent', 0)
            }
            
            # Add historical price data for technical analysis
            if historical_data is not None and not historical_data.empty:
                enhanced_data['price_history'] = historical_data['close'].tail(50).tolist()
                enhanced_data['volume_history'] = historical_data.get('volume', pd.Series()).tail(50).tolist()
                enhanced_data['high_history'] = historical_data.get('high', pd.Series()).tail(50).tolist()
                enhanced_data['low_history'] = historical_data.get('low', pd.Series()).tail(50).tolist()
            
            # Add fundamental data if requested
            if include_fundamentals and not 'USD' in symbol:  # Stocks only
                fundamentals = self.get_fundamental_data(symbol)
                if fundamentals:
                    enhanced_data['fundamentals'] = fundamentals
            
            return enhanced_data
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced quote data failed for {symbol}: {e}")
            return None
    
    def get_market_context(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get market context using Finnhub market data
        """
        if not self.finnhub_available:
            return None
        
        try:
            # Get market sentiment and context
            context = {}
            
            # Get market news sentiment
            news = self.get_news_sentiment(symbol, limit=5)
            if news:
                sentiment_scores = []
                for item in news:
                    # Simple sentiment analysis based on keywords
                    headline = item.get('headline', '').lower()
                    if any(word in headline for word in ['surge', 'rally', 'gain', 'bull', 'up']):
                        sentiment_scores.append(1)
                    elif any(word in headline for word in ['crash', 'fall', 'bear', 'down', 'decline']):
                        sentiment_scores.append(-1)
                    else:
                        sentiment_scores.append(0)
                
                avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
                context['news_sentiment'] = avg_sentiment
                context['news_count'] = len(news)
            
            # Add market volatility context
            if not 'USD' in symbol:  # For stocks
                try:
                    # Get basic company profile
                    profile = self.finnhub_client.company_profile2(symbol=symbol)
                    if profile:
                        context['sector'] = profile.get('finnhubIndustry', '')
                        context['market_cap'] = profile.get('marketCapitalization', 0)
                except Exception:
                    pass
            
            return context if context else None
            
        except Exception as e:
            self.logger.error(f"❌ Market context failed for {symbol}: {e}")
            return None
    
    def get_sector_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get sector-specific data and rotation signals
        """
        try:
            if not self.finnhub_available or 'USD' in symbol:
                return None
            
            # Get company profile for sector information
            profile = self.finnhub_client.company_profile2(symbol=symbol)
            if not profile:
                return None
            
            sector = profile.get('finnhubIndustry', '')
            if not sector:
                return None
            
            # Simple sector momentum analysis
            sector_data = {
                'sector': sector,
                'rotation_signal': 'neutral',  # Would implement sector rotation logic
                'sector_momentum': 0.5,  # Placeholder for sector momentum
                'relative_strength': 0.5  # Placeholder for relative strength vs sector
            }
            
            return sector_data
            
        except Exception as e:
            self.logger.error(f"❌ Sector data failed for {symbol}: {e}")
            return None
    
    def get_fundamental_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get fundamental data (PE ratio, market cap, etc.)
        Uses yfinance as primary source for fundamentals
        """
        if not self.yfinance_available:
            self.logger.warning("⚠️ yfinance not available for fundamental data")
            return None
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            fundamentals = {
                'symbol': symbol,
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'price_to_book': info.get('priceToBook'),
                'debt_to_equity': info.get('debtToEquity'),
                'dividend_yield': info.get('dividendYield'),
                'earnings_growth': info.get('earningsGrowth'),
                'revenue_growth': info.get('revenueGrowth'),
                'profit_margins': info.get('profitMargins'),
                'operating_margins': info.get('operatingMargins'),
                'return_on_equity': info.get('returnOnEquity'),
                'return_on_assets': info.get('returnOnAssets'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'source': 'yfinance'
            }
            
            self.logger.debug(f"✅ Fundamental data retrieved for {symbol}")
            return fundamentals
            
        except Exception as e:
            self.logger.error(f"❌ Fundamental data failed for {symbol}: {e}")
            return None
    
    def get_news_sentiment(self, symbol: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Get news and sentiment data
        Uses Finnhub as primary source for news
        """
        if not self.finnhub_available:
            self.logger.warning("⚠️ Finnhub not available for news data")
            return None
        
        try:
            # Get news from past 7 days
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            news = self.finnhub_client.company_news(symbol, _from=from_date, to=to_date)
            
            if news:
                # Limit results and add sentiment placeholder
                news_items = []
                for item in news[:limit]:
                    news_items.append({
                        'headline': item.get('headline', ''),
                        'summary': item.get('summary', ''),
                        'url': item.get('url', ''),
                        'datetime': datetime.fromtimestamp(item.get('datetime', 0)),
                        'source': item.get('source', ''),
                        'sentiment': 'neutral',  # Placeholder - could add sentiment analysis
                        'relevance': 1.0
                    })
                
                self.logger.debug(f"✅ News data retrieved for {symbol} ({len(news_items)} items)")
                return news_items
                
        except Exception as e:
            self.logger.error(f"❌ News data failed for {symbol}: {e}")
            return None
    
    def check_data_sources_health(self) -> Dict[str, bool]:
        """
        Check health of all data sources
        """
        health = {
            'alpaca': self.alpaca_available,
            'yfinance': self.yfinance_available,
            'alpha_vantage': self.alpha_vantage_available,
            'finnhub': self.finnhub_available
        }
        
        active_sources = sum(health.values())
        self.logger.info(f"📊 Data sources active: {active_sources}/4")
        
        return health
    
    def get_enhanced_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive market data combining all sources
        Returns enriched dataset for advanced analysis
        """
        enhanced_data = {
            'symbol': symbol,
            'timestamp': datetime.now(timezone.utc),
            'sources_used': []
        }
        
        # Get real-time quote (required for trading)
        quote = self.get_latest_quote(symbol)
        if quote:
            enhanced_data.update(quote)
            enhanced_data['sources_used'].append(quote['source'])
        
        # Get fundamental data (enrichment)
        fundamentals = self.get_fundamental_data(symbol)
        if fundamentals:
            enhanced_data['fundamentals'] = fundamentals
            enhanced_data['sources_used'].append('fundamentals')
        
        # Get news sentiment (enrichment)
        news = self.get_news_sentiment(symbol, limit=5)
        if news:
            enhanced_data['recent_news'] = news
            enhanced_data['sources_used'].append('news')
        
        enhanced_data['data_quality_score'] = len(enhanced_data['sources_used']) / 3.0
        
        return enhanced_data


# Singleton instance for modular system integration
enhanced_data_manager = None

def get_enhanced_data_manager(**kwargs) -> EnhancedDataManager:
    """
    Get singleton instance of enhanced data manager
    Preserves Firebase + Railway compatibility
    """
    global enhanced_data_manager
    if enhanced_data_manager is None:
        enhanced_data_manager = EnhancedDataManager(**kwargs)
    return enhanced_data_manager


if __name__ == "__main__":
    # Test the enhanced data manager
    import os
    
    # Test initialization
    manager = EnhancedDataManager(
        alpaca_api_key=os.getenv('ALPACA_PAPER_API_KEY'),
        alpaca_secret_key=os.getenv('ALPACA_PAPER_SECRET_KEY'),
        alpha_vantage_key=os.getenv('ALPHA_VANTAGE_API_KEY'),
        finnhub_key=os.getenv('FINNHUB_API_KEY')
    )
    
    # Check data source health
    health = manager.check_data_sources_health()
    print(f"📊 Data Sources Health: {health}")
    
    # Test enhanced data retrieval
    test_symbols = ['AAPL', 'BTCUSD', 'SPY']
    for symbol in test_symbols:
        print(f"\n🔍 Testing {symbol}:")
        enhanced_data = manager.get_enhanced_market_data(symbol)
        print(f"  Sources used: {enhanced_data.get('sources_used', [])}")
        print(f"  Data quality: {enhanced_data.get('data_quality_score', 0):.2f}")
        if 'bid' in enhanced_data:
            print(f"  Quote: ${enhanced_data['bid']:.2f} / ${enhanced_data['ask']:.2f}")