#!/usr/bin/env python3
"""
Production Configuration Management

Handles environment variable loading, validation, and configuration
management for the modular trading system in production.
"""

import os
import logging
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


class ProductionConfig:
    """
    Production configuration manager with validation and defaults.
    
    Handles all environment variable loading with proper validation,
    type conversion, and sensible defaults for production deployment.
    """
    
    def __init__(self):
        """Initialize production configuration."""
        self.config = {}
        self._load_configuration()
        self._validate_critical_config()
    
    def _load_configuration(self):
        """Load all configuration from environment variables."""
        
        # Trading API Configuration
        self.config.update({
            'ALPACA_PAPER_API_KEY': os.getenv('ALPACA_PAPER_API_KEY'),
            'ALPACA_PAPER_SECRET_KEY': os.getenv('ALPACA_PAPER_SECRET_KEY'),
            'ALPACA_BASE_URL': os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets'),
        })
        
        # System Configuration
        self.config.update({
            'EXECUTION_ENABLED': self._get_bool_env('EXECUTION_ENABLED', True),
            'MODULAR_SYSTEM': self._get_bool_env('MODULAR_SYSTEM', True),
            'ML_OPTIMIZATION': self._get_bool_env('ML_OPTIMIZATION', True),
            'RISK_MANAGEMENT': self._get_bool_env('RISK_MANAGEMENT', True),
        })
        
        # Module Configuration
        self.config.update({
            'OPTIONS_TRADING': self._get_bool_env('OPTIONS_TRADING', True),
            'CRYPTO_TRADING': self._get_bool_env('CRYPTO_TRADING', True),
            'STOCKS_TRADING': self._get_bool_env('STOCKS_TRADING', True),
        })
        
        # Performance Configuration
        self.config.update({
            'ORCHESTRATOR_CYCLE_DELAY': self._get_int_env('ORCHESTRATOR_CYCLE_DELAY', 120),
            'ML_OPTIMIZATION_INTERVAL': self._get_int_env('ML_OPTIMIZATION_INTERVAL', 600),
            'DASHBOARD_UPDATE_INTERVAL': self._get_int_env('DASHBOARD_UPDATE_INTERVAL', 30),
            'MAX_CONCURRENT_MODULES': self._get_int_env('MAX_CONCURRENT_MODULES', 3),
        })
        
        # Risk Management Configuration
        self.config.update({
            'MAX_PORTFOLIO_RISK': self._get_float_env('MAX_PORTFOLIO_RISK', 0.20),
            'MAX_POSITION_SIZE': self._get_float_env('MAX_POSITION_SIZE', 0.10),
            'OPTIONS_MAX_ALLOCATION': self._get_float_env('OPTIONS_MAX_ALLOCATION', 0.30),
            'CRYPTO_MAX_ALLOCATION': self._get_float_env('CRYPTO_MAX_ALLOCATION', 0.20),
        })
        
        # Market Intelligence Configuration (NEW)
        self.config.update({
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'OPENAI_MODEL': os.getenv('OPENAI_MODEL', 'o4-mini'),
            'INTELLIGENCE_CYCLE_HOURS': self._get_int_env('INTELLIGENCE_CYCLE_HOURS', 6),
            'MARKET_INTELLIGENCE': self._get_bool_env('MARKET_INTELLIGENCE', True),
        })
        
        # Firebase Configuration
        self.config.update({
            'FIREBASE_PRIVATE_KEY_ID': os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            'FIREBASE_PRIVATE_KEY': os.getenv('FIREBASE_PRIVATE_KEY'),
            'FIREBASE_CLIENT_EMAIL': os.getenv('FIREBASE_CLIENT_EMAIL'),
            'FIREBASE_CLIENT_ID': os.getenv('FIREBASE_CLIENT_ID'),
            'FIREBASE_CLIENT_CERT_URL': os.getenv('FIREBASE_CLIENT_CERT_URL'),
        })
        
        # Railway/Deployment Configuration
        self.config.update({
            'PORT': self._get_int_env('PORT', 8080),
            'RAILWAY_ENVIRONMENT': os.getenv('RAILWAY_ENVIRONMENT', 'local'),
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        })
        
        logger.info("✅ Configuration loaded from environment")
    
    def _validate_critical_config(self):
        """Validate critical configuration values."""
        
        # Critical API keys
        if not self.config.get('ALPACA_PAPER_API_KEY'):
            logger.warning("⚠️ ALPACA_PAPER_API_KEY not set - trading will be disabled")
        
        if not self.config.get('ALPACA_PAPER_SECRET_KEY'):
            logger.warning("⚠️ ALPACA_PAPER_SECRET_KEY not set - trading will be disabled")
        
        # Market Intelligence API key
        if not self.config.get('OPENAI_API_KEY'):
            logger.warning("⚠️ OPENAI_API_KEY not set - Market Intelligence will be disabled")
        elif self.config.get('OPENAI_API_KEY'):
            logger.info(f"✅ OpenAI API key configured for Market Intelligence (model: {self.config.get('OPENAI_MODEL', 'o4-mini')})")
        
        # Firebase configuration
        firebase_keys = [
            'FIREBASE_PRIVATE_KEY_ID', 'FIREBASE_PRIVATE_KEY', 
            'FIREBASE_CLIENT_EMAIL', 'FIREBASE_CLIENT_ID'
        ]
        
        missing_firebase = [key for key in firebase_keys if not self.config.get(key)]
        if missing_firebase:
            logger.warning(f"⚠️ Firebase keys missing: {missing_firebase} - Firebase will be disabled")
        
        # Risk management validation
        if self.config.get('MAX_PORTFOLIO_RISK', 0) > 0.5:
            logger.warning("⚠️ MAX_PORTFOLIO_RISK > 50% - very high risk configuration")
        
        if self.config.get('MAX_POSITION_SIZE', 0) > 0.2:
            logger.warning("⚠️ MAX_POSITION_SIZE > 20% - high concentration risk")
        
        # Performance validation
        if self.config.get('ORCHESTRATOR_CYCLE_DELAY', 0) < 60:
            logger.warning("⚠️ ORCHESTRATOR_CYCLE_DELAY < 60s - may cause high API usage")
        
        logger.info("✅ Configuration validation complete")
    
    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable with default."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on', 'enabled')
    
    def _get_int_env(self, key: str, default: int = 0) -> int:
        """Get integer environment variable with default."""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            logger.warning(f"⚠️ Invalid integer for {key}, using default: {default}")
            return default
    
    def _get_float_env(self, key: str, default: float = 0.0) -> float:
        """Get float environment variable with default."""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            logger.warning(f"⚠️ Invalid float for {key}, using default: {default}")
            return default
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""
        value = self.config.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', '1', 'yes', 'on', 'enabled')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        value = self.config.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float configuration value."""
        value = self.config.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.config.get('RAILWAY_ENVIRONMENT', '').lower() == 'production'
    
    def is_trading_enabled(self) -> bool:
        """Check if trading is enabled."""
        return (self.get_bool('EXECUTION_ENABLED', False) and 
                self.config.get('ALPACA_PAPER_API_KEY') and 
                self.config.get('ALPACA_PAPER_SECRET_KEY'))
    
    def is_firebase_enabled(self) -> bool:
        """Check if Firebase is properly configured."""
        required_keys = [
            'FIREBASE_PRIVATE_KEY_ID', 'FIREBASE_PRIVATE_KEY',
            'FIREBASE_CLIENT_EMAIL', 'FIREBASE_CLIENT_ID'
        ]
        return all(self.config.get(key) for key in required_keys)
    
    def get_risk_limits(self) -> Dict[str, float]:
        """Get all risk management limits."""
        return {
            'max_portfolio_risk': self.get_float('MAX_PORTFOLIO_RISK', 0.20),
            'max_position_size': self.get_float('MAX_POSITION_SIZE', 0.10),
            'options_max_allocation': self.get_float('OPTIONS_MAX_ALLOCATION', 0.30),
            'crypto_max_allocation': self.get_float('CRYPTO_MAX_ALLOCATION', 0.20),
        }
    
    def get_module_config(self) -> Dict[str, bool]:
        """Get trading module configuration."""
        return {
            'options': self.get_bool('OPTIONS_TRADING', True),
            'crypto': self.get_bool('CRYPTO_TRADING', True),
            'stocks': self.get_bool('STOCKS_TRADING', True),
        }
    
    def get_performance_config(self) -> Dict[str, int]:
        """Get performance configuration."""
        return {
            'orchestrator_cycle_delay': self.get_int('ORCHESTRATOR_CYCLE_DELAY', 120),
            'ml_optimization_interval': self.get_int('ML_OPTIMIZATION_INTERVAL', 600),
            'dashboard_update_interval': self.get_int('DASHBOARD_UPDATE_INTERVAL', 30),
            'max_concurrent_modules': self.get_int('MAX_CONCURRENT_MODULES', 3),
        }
    
    def get_alpaca_config(self) -> Dict[str, Optional[str]]:
        """Get Alpaca API configuration."""
        return {
            'api_key': self.config.get('ALPACA_PAPER_API_KEY'),
            'secret_key': self.config.get('ALPACA_PAPER_SECRET_KEY'),
            'base_url': self.config.get('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets'),
        }
    
    def get_firebase_config(self) -> Dict[str, Optional[str]]:
        """Get Firebase configuration."""
        return {
            'private_key_id': self.config.get('FIREBASE_PRIVATE_KEY_ID'),
            'private_key': self.config.get('FIREBASE_PRIVATE_KEY'),
            'client_email': self.config.get('FIREBASE_CLIENT_EMAIL'),
            'client_id': self.config.get('FIREBASE_CLIENT_ID'),
            'client_cert_url': self.config.get('FIREBASE_CLIENT_CERT_URL'),
        }
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """Get deployment information."""
        return {
            'environment': self.config.get('RAILWAY_ENVIRONMENT', 'local'),
            'port': self.get_int('PORT', 8080),
            'log_level': self.config.get('LOG_LEVEL', 'INFO'),
            'is_production': self.is_production(),
            'trading_enabled': self.is_trading_enabled(),
            'firebase_enabled': self.is_firebase_enabled(),
        }
    
    def log_configuration_summary(self):
        """Log a summary of the current configuration."""
        logger.info("📋 PRODUCTION CONFIGURATION SUMMARY")
        logger.info("=" * 50)
        
        # Deployment info
        deployment = self.get_deployment_info()
        logger.info(f"🌍 Environment: {deployment['environment']}")
        logger.info(f"🚪 Port: {deployment['port']}")
        logger.info(f"📊 Log Level: {deployment['log_level']}")
        
        # Feature flags
        logger.info(f"💰 Trading Enabled: {deployment['trading_enabled']}")
        logger.info(f"🔥 Firebase Enabled: {deployment['firebase_enabled']}")
        logger.info(f"🧠 ML Optimization: {self.get_bool('ML_OPTIMIZATION')}")
        logger.info(f"🛡️ Risk Management: {self.get_bool('RISK_MANAGEMENT')}")
        
        # Module configuration
        modules = self.get_module_config()
        logger.info(f"📈 Modules - Options: {modules['options']}, Crypto: {modules['crypto']}, Stocks: {modules['stocks']}")
        
        # Performance settings
        perf = self.get_performance_config()
        logger.info(f"⏱️ Cycle Delay: {perf['orchestrator_cycle_delay']}s")
        logger.info(f"🔄 ML Interval: {perf['ml_optimization_interval']}s")
        
        # Risk limits
        risk = self.get_risk_limits()
        logger.info(f"⚠️ Max Portfolio Risk: {risk['max_portfolio_risk']:.1%}")
        logger.info(f"📊 Max Position Size: {risk['max_position_size']:.1%}")
        
        logger.info("=" * 50)