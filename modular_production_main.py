#!/usr/bin/env python3
"""
Modular Trading System - Production Entry Point

This is the main entry point for the production modular trading system.
It initializes all components, handles environment configuration, and provides
health monitoring endpoints for Railway deployment.
"""

import os
import sys
import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import signal
from flask import Flask, jsonify

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modular components
from modular.orchestrator import ModularOrchestrator
from modular.firebase_interface import ModularFirebaseInterface
from firebase_database import FirebaseDatabase
from production_config import ProductionConfig
from production_health_check import HealthMonitor
from data_mode_manager import DataModeManager

# Legacy fallback imports
import alpaca_trade_api as tradeapi

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('production.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)


class ProductionTradingSystem:
    """
    Production wrapper for the modular trading system.
    
    Handles initialization, health monitoring, graceful shutdown,
    and integration with Railway deployment infrastructure.
    """
    
    def __init__(self):
        """Initialize the production trading system."""
        self.config = ProductionConfig()
        self.health_monitor = HealthMonitor()
        self.orchestrator = None
        self.firebase_db = None
        self.running = False
        self.flask_app = None
        
        # System state tracking
        self.start_time = datetime.now()
        self.last_health_check = None
        self.error_count = 0
        self.cycle_count = 0
        
        logger.info("🚀 Production Trading System initializing...")
        
        # Initialize data mode manager for subscription-aware optimization
        self.data_mode_manager = DataModeManager(logger=logger)
        logger.info("🔧 DELAYED DATA OPTIMIZATION: System configured for your subscription level")
        logger.info(self.data_mode_manager.format_data_mode_status())
        
    def initialize_components(self) -> bool:
        """
        Initialize all system components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("🔧 Initializing system components...")
            
            # Initialize Firebase
            if not self._initialize_firebase():
                return False
            
            # Initialize Trading API
            if not self._initialize_alpaca():
                return False
                
            # Initialize Modular Components
            if not self._initialize_modular_system():
                return False
                
            # Initialize Health Monitoring
            self._initialize_health_monitoring()
            
            # Initialize Flask health endpoints
            self._initialize_flask_app()
            
            logger.info("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            return False
    
    def _initialize_firebase(self) -> bool:
        """Initialize Firebase database connection."""
        try:
            logger.info("🔥 Initializing Firebase database...")
            
            self.firebase_db = FirebaseDatabase()
            
            if self.firebase_db.is_connected():
                logger.info("✅ Firebase database connected")
                return True
            else:
                logger.warning("⚠️ Firebase database not connected - using fallback mode")
                return True  # Continue without Firebase
                
        except Exception as e:
            logger.error(f"❌ Firebase initialization failed: {e}")
            return False
    
    def _initialize_alpaca(self) -> bool:
        """Initialize Alpaca trading API."""
        try:
            logger.info("📈 Initializing Alpaca trading API...")
            
            api_key = self.config.get('ALPACA_PAPER_API_KEY')
            secret_key = self.config.get('ALPACA_PAPER_SECRET_KEY')
            base_url = self.config.get('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
            
            # COMPREHENSIVE CREDENTIAL DEBUGGING
            logger.info("🔍 ALPACA API CREDENTIAL DEBUGGING:")
            logger.info(f"   API Key present: {bool(api_key)}")
            logger.info(f"   Secret Key present: {bool(secret_key)}")
            logger.info(f"   Base URL: {base_url}")
            
            if api_key:
                logger.info(f"   API Key starts with: {api_key[:8]}..." if len(api_key) > 8 else f"   API Key: {api_key}")
                logger.info(f"   API Key length: {len(api_key)}")
            
            if secret_key:
                logger.info(f"   Secret Key starts with: {secret_key[:8]}..." if len(secret_key) > 8 else f"   Secret Key: {secret_key}")
                logger.info(f"   Secret Key length: {len(secret_key)}")
            
            if not api_key or not secret_key:
                logger.error("❌ Alpaca API credentials not found")
                logger.error("🔍 Available environment variables:")
                import os
                env_vars = [k for k in os.environ.keys() if 'ALPACA' in k.upper()]
                for var in env_vars:
                    logger.error(f"   {var}: {'SET' if os.environ.get(var) else 'NOT SET'}")
                return False
            
            # VALIDATE API KEY FORMATS
            logger.info("🔍 VALIDATING API KEY FORMATS:")
            
            # Alpaca paper keys should start with specific prefixes
            if api_key and not (api_key.startswith('PK') or api_key.startswith('AK')):
                logger.warning(f"⚠️ API Key format unusual - should start with 'PK' or 'AK', got: {api_key[:4]}...")
            
            if secret_key and not secret_key.replace('-', '').replace('_', '').isalnum():
                logger.warning(f"⚠️ Secret Key format unusual - contains unexpected characters")
            
            # Check for common environment variable issues
            if api_key and (api_key.startswith('"') or api_key.endswith('"')):
                logger.warning("⚠️ API Key has quotes - removing them")
                api_key = api_key.strip('"')
                
            if secret_key and (secret_key.startswith('"') or secret_key.endswith('"')):
                logger.warning("⚠️ Secret Key has quotes - removing them")
                secret_key = secret_key.strip('"')
            
            # Initialize Alpaca API for algorithmic trading
            logger.info("📡 Connecting to Alpaca API...")
            self.alpaca_api = tradeapi.REST(
                api_key,
                secret_key,
                base_url,
                api_version='v2'
            )
            
            # Data quality depends on Alpaca subscription tier:
            # - Basic Plan (Free): IEX real-time data, 15-min delayed historical
            # - Algo Trader Plus ($99/month): Full market real-time data, unlimited historical
            logger.info("📊 Alpaca API initialized - data quality depends on account subscription tier")
            
            # Test connection with detailed error handling
            try:
                account = self.alpaca_api.get_account()
                logger.info(f"✅ Alpaca API connected - Account: {account.id}")
                logger.info(f"💰 Portfolio Value: ${float(account.portfolio_value):,.2f}")
                logger.info(f"🔓 Buying Power: ${float(account.buying_power):,.2f}")
            except Exception as api_error:
                logger.error(f"❌ Alpaca API test failed: {api_error}")
                if "unauthorized" in str(api_error).lower():
                    logger.error("🔑 AUTHENTICATION ERROR: Check these environment variables:")
                    logger.error("   - ALPACA_PAPER_API_KEY")
                    logger.error("   - ALPACA_PAPER_SECRET_KEY") 
                    logger.error("   - ALPACA_BASE_URL")
                raise api_error
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Alpaca API initialization failed: {e}")
            return False
    
    def _initialize_modular_system(self) -> bool:
        """Initialize the modular trading orchestrator."""
        try:
            logger.info("🎼 Initializing modular orchestrator...")
            
            # Initialize risk manager
            from risk_manager import RiskManager
            risk_mgr = RiskManager(api_client=self.alpaca_api, db=None, logger=logger)
            
            # Initialize order executor
            from modular.order_executor import ModularOrderExecutor
            order_executor = ModularOrderExecutor(api_client=self.alpaca_api, logger=logger)
            
            # Configure execution mode based on environment
            execution_enabled = self.config.get_bool('EXECUTION_ENABLED', True)
            dry_run_mode = self.config.get_bool('DRY_RUN_MODE', False)
            order_executor.set_execution_mode(execution_enabled, dry_run_mode)
            
            # Initialize orchestrator
            self.orchestrator = ModularOrchestrator(
                firebase_db=self.firebase_db,
                risk_manager=risk_mgr,
                order_executor=order_executor,  # Now properly initialized
                ml_optimizer=None,  # Will be initialized by orchestrator
                logger=logger
            )
            
            # Register trading modules
            self._register_trading_modules()
            
            logger.info("✅ Modular orchestrator initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Modular system initialization failed: {e}")
            return False
    
    def _register_trading_modules(self):
        """Register trading modules with the orchestrator."""
        try:
            logger.info("📋 Registering trading modules...")
            
            # Import module classes
            from modular.options_module import OptionsModule
            from modular.crypto_module import CryptoModule  
            from modular.stocks_module import StocksModule
            from modular.market_intelligence_module import MarketIntelligenceModule
            
            # Module configuration from environment
            modules_config = self.config.get_module_config()
            
            # Import module configuration
            from modular.base_module import ModuleConfig
            
            # Register Options Module
            if modules_config.get('options', True):
                try:
                    logger.info("🎯 Initializing Options module...")
                    
                    options_config = ModuleConfig(
                        module_name="options",
                        enabled=True,
                        max_allocation_pct=70.0,  # Higher allocation for 100% buying power
                        min_confidence=0.55,     # Lower for more opportunities
                        max_positions=15,        # More positions
                        default_stop_loss_pct=0.08,
                        default_profit_target_pct=0.15,
                        custom_params={
                            'leverage_target': 2.5,
                            'hedge_threshold': 15.0
                        }
                    )
                    
                    options_module = OptionsModule(
                        config=options_config,
                        firebase_db=self.firebase_db,
                        risk_manager=self.orchestrator.risk_manager,  # Use orchestrator's risk manager
                        order_executor=self.orchestrator.order_executor,  # Use orchestrator's order executor
                        api_client=self.alpaca_api,
                        logger=logger
                    )
                    self.orchestrator.register_module(options_module)
                    logger.info("✅ Options module registered")
                except Exception as e:
                    logger.error(f"❌ Failed to register options module: {e}")
                    import traceback
                    logger.error(f"Options module error details: {traceback.format_exc()}")
            
            # Register Crypto Module
            if modules_config.get('crypto', True):
                try:
                    logger.info("₿ Initializing Crypto module...")
                    
                    crypto_config = ModuleConfig(
                        module_name="crypto",
                        enabled=True,
                        max_allocation_pct=30.0,  # Market hours: conservative 30%
                        min_confidence=0.6,
                        max_positions=15,  # Increased for aggressive after-hours trading
                        default_stop_loss_pct=0.10,
                        default_profit_target_pct=0.20,
                        custom_params={
                            'session_thresholds': {
                                'asia': 0.45,
                                'europe': 0.50,
                                'us': 0.40
                            },
                            # AGGRESSIVE AFTER-HOURS PARAMETERS
                            'after_hours_max_allocation_pct': 90.0,  # Use 90% of buying power after hours
                            'leverage_multiplier': 1.5,  # Standard leverage during market hours
                            'after_hours_leverage': 3.5,  # MAXIMUM leverage after hours
                            'max_allocation_pct': 30.0,  # Conservative during market hours
                            'volatility_threshold': 3.0  # Lower threshold for more opportunities
                        }
                    )
                    
                    crypto_module = CryptoModule(
                        config=crypto_config,
                        firebase_db=self.firebase_db,
                        risk_manager=self.orchestrator.risk_manager,  # Use orchestrator's risk manager
                        order_executor=self.orchestrator.order_executor,  # Use orchestrator's order executor
                        api_client=self.alpaca_api,
                        logger=logger
                    )
                    self.orchestrator.register_module(crypto_module)
                    logger.info("✅ Crypto module registered")
                except Exception as e:
                    logger.error(f"❌ Failed to register crypto module: {e}")
                    import traceback
                    logger.error(f"Crypto module error details: {traceback.format_exc()}")
            
            # Register Stocks Module  
            if modules_config.get('stocks', True):
                try:
                    logger.info("📈 DEBUGGING: Starting Stocks module initialization...")
                    logger.info(f"📈 DEBUGGING: modules_config stocks = {modules_config.get('stocks', True)}")
                    
                    stocks_config = ModuleConfig(
                        module_name="stocks",
                        enabled=True,
                        max_allocation_pct=40.0,  # REDUCED: Prevent insufficient balance
                        min_confidence=0.35,     # LOWERED: More opportunities
                        max_positions=30,        # Maximum diversification
                        default_stop_loss_pct=0.08,
                        default_profit_target_pct=0.15,
                        custom_params={
                            'sector_limits': {
                                'technology': 40.0,
                                'healthcare': 30.0,
                                'financials': 25.0
                            }
                        }
                    )
                    
                    logger.info("📈 DEBUGGING: Creating StocksModule instance...")
                    stocks_module = StocksModule(
                        config=stocks_config,
                        firebase_db=self.firebase_db,
                        risk_manager=self.orchestrator.risk_manager,  # Use orchestrator's risk manager
                        order_executor=self.orchestrator.order_executor,  # Use orchestrator's order executor
                        api_client=self.alpaca_api,
                        logger=logger
                    )
                    logger.info("📈 DEBUGGING: StocksModule created, registering with orchestrator...")
                    self.orchestrator.register_module(stocks_module)
                    logger.info("✅ DEBUGGING: Stocks module registration COMPLETED")
                    
                    # VERIFY REGISTRATION
                    active_modules = self.orchestrator.registry.get_active_modules()
                    stocks_found = any(m.module_name == 'stocks' for m in active_modules)
                    logger.info(f"📈 DEBUGGING: Stocks module in active list: {stocks_found}")
                    logger.info(f"📈 DEBUGGING: All active modules: {[m.module_name for m in active_modules]}")
                except Exception as e:
                    logger.error(f"❌ Failed to register stocks module: {e}")
                    import traceback
                    logger.error(f"Stocks module error details: {traceback.format_exc()}")
            
            # Register Market Intelligence Module (NEW)
            if modules_config.get('market_intelligence', True) and self.config.get('OPENAI_API_KEY'):
                try:
                    logger.info("🧠 Initializing Market Intelligence module...")
                    
                    intelligence_config = ModuleConfig(
                        module_name="market_intelligence",
                        enabled=True,
                        max_allocation_pct=0.0,  # Intelligence module doesn't trade directly
                        min_confidence=0.6,
                        max_positions=0,  # No position limits for intelligence
                        custom_params={
                            'intelligence_cycle_hours': int(self.config.get('INTELLIGENCE_CYCLE_HOURS', '6')),
                            'openai_model': self.config.get('OPENAI_MODEL', 'o4-mini'),
                            'enable_pre_market': True,
                            'enable_post_market': True
                        }
                    )
                    
                    intelligence_module = MarketIntelligenceModule(
                        config=intelligence_config,
                        firebase_db=self.firebase_db,
                        risk_manager=self.orchestrator.risk_manager,
                        order_executor=self.orchestrator.order_executor,
                        openai_api_key=self.config.get('OPENAI_API_KEY'),
                        openai_model=self.config.get('OPENAI_MODEL', 'o4-mini'),
                        logger=logger
                    )
                    self.orchestrator.register_module(intelligence_module)
                    logger.info("✅ Market Intelligence module registered")
                except Exception as e:
                    logger.error(f"❌ Failed to register market intelligence module: {e}")
                    import traceback
                    logger.error(f"Market Intelligence module error details: {traceback.format_exc()}")
            elif not self.config.get('OPENAI_API_KEY'):
                logger.warning("⚠️ Market Intelligence module disabled - OPENAI_API_KEY not found")
            
            logger.info("📋 Module registration complete")
            
            # Log registered modules for verification
            active_modules = self.orchestrator.registry.get_active_modules()
            if active_modules:
                logger.info(f"✅ Active modules: {[m.module_name for m in active_modules]}")
            else:
                logger.warning("⚠️ No active modules found after registration")
            
        except Exception as e:
            logger.error(f"❌ Module registration failed: {e}")
            import traceback
            logger.error(f"Module registration error details: {traceback.format_exc()}")
    
    def _initialize_health_monitoring(self):
        """Initialize health monitoring system."""
        try:
            logger.info("🏥 Initializing health monitoring...")
            
            self.health_monitor.register_component('firebase', self.firebase_db)
            self.health_monitor.register_component('alpaca', self.alpaca_api)
            self.health_monitor.register_component('orchestrator', self.orchestrator)
            
            logger.info("✅ Health monitoring initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Health monitoring initialization failed: {e}")
    
    def _initialize_flask_app(self):
        """Initialize Flask app for health endpoints."""
        try:
            self.flask_app = Flask(__name__)
            
            @self.flask_app.route('/health')
            def health_check():
                """Health check endpoint for Railway."""
                health_status = self.get_system_health()
                # Return 200 for healthy and degraded (system running)
                # Return 503 only for stopped, error, or critical (system down)
                running_statuses = {'healthy', 'degraded'}
                status_code = 200 if health_status['status'] in running_statuses else 503
                return jsonify(health_status), status_code
            
            @self.flask_app.route('/status')
            def system_status():
                """Detailed system status endpoint."""
                return jsonify(self.get_detailed_status())
            
            @self.flask_app.route('/metrics')
            def system_metrics():
                """System metrics endpoint."""
                return jsonify(self.get_system_metrics())
            
            @self.flask_app.route('/intelligence')
            def intelligence_status():
                """Market Intelligence module status endpoint."""
                try:
                    if self.orchestrator:
                        intelligence_module = self.orchestrator.registry.get_module('market_intelligence')
                        if intelligence_module:
                            return jsonify(intelligence_module.get_performance_summary())
                        else:
                            return jsonify({'error': 'Market Intelligence module not found'}), 404
                    else:
                        return jsonify({'error': 'Orchestrator not initialized'}), 503
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            @self.flask_app.route('/intelligence/debug')
            def intelligence_debug():
                """Market Intelligence module debug endpoint."""
                try:
                    if self.orchestrator:
                        intelligence_module = self.orchestrator.registry.get_module('market_intelligence')
                        if intelligence_module:
                            return jsonify(intelligence_module.get_debug_info())
                        else:
                            return jsonify({'error': 'Market Intelligence module not found'}), 404
                    else:
                        return jsonify({'error': 'Orchestrator not initialized'}), 503
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            @self.flask_app.route('/intelligence/signals')
            def intelligence_signals():
                """Market Intelligence signals endpoint."""
                try:
                    if self.orchestrator:
                        intelligence_module = self.orchestrator.registry.get_module('market_intelligence')
                        if intelligence_module:
                            signals = intelligence_module.get_market_intelligence_signals()
                            return jsonify({
                                'signals_count': len(signals),
                                'signals': [
                                    {
                                        'type': s.signal_type,
                                        'symbol': s.symbol,
                                        'value': s.value,
                                        'confidence': s.confidence,
                                        'reasoning': s.reasoning[:100] + '...' if len(s.reasoning) > 100 else s.reasoning,
                                        'timestamp': s.timestamp.isoformat(),
                                        'metadata': s.metadata
                                    } for s in signals
                                ]
                            })
                        else:
                            return jsonify({'error': 'Market Intelligence module not found'}), 404
                    else:
                        return jsonify({'error': 'Orchestrator not initialized'}), 503
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            @self.flask_app.route('/safety')
            def safety_status():
                """CRITICAL SAFETY: Safety controls status endpoint."""
                try:
                    safety_data = {}
                    
                    # Orchestrator safety status
                    if self.orchestrator and hasattr(self.orchestrator, 'get_safety_status'):
                        safety_data['orchestrator'] = self.orchestrator.get_safety_status()
                    
                    # Order executor safety status
                    if (self.orchestrator and hasattr(self.orchestrator, 'order_executor') and 
                        hasattr(self.orchestrator.order_executor, 'get_safety_status')):
                        safety_data['order_executor'] = self.orchestrator.order_executor.get_safety_status()
                    
                    # Add timestamp
                    safety_data['timestamp'] = datetime.now().isoformat()
                    safety_data['status'] = 'emergency' if safety_data.get('orchestrator', {}).get('emergency_stop') else 'operational'
                    
                    return jsonify(safety_data)
                    
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            @self.flask_app.route('/safety/reset', methods=['POST'])
            def reset_safety():
                """CRITICAL SAFETY: Reset circuit breaker (use with extreme caution)."""
                try:
                    if self.orchestrator and hasattr(self.orchestrator, 'reset_circuit_breaker'):
                        self.orchestrator.reset_circuit_breaker()
                        return jsonify({'message': 'Circuit breaker reset', 'timestamp': datetime.now().isoformat()})
                    else:
                        return jsonify({'error': 'Orchestrator not available'}), 503
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            logger.info("✅ Flask health endpoints initialized (including Market Intelligence)")
            
        except Exception as e:
            logger.warning(f"⚠️ Flask app initialization failed: {e}")
    
    def start_system(self):
        """Start the production trading system."""
        try:
            logger.info("🚀 Starting production trading system...")
            
            if not self.initialize_components():
                logger.error("❌ System initialization failed")
                return False
            
            # EMERGENCY CHECK: Verify account allocation 
            self._emergency_allocation_check()
            
            self.running = True
            
            # Start Flask health server in background
            if self.flask_app:
                import threading
                port = int(os.environ.get('PORT', 8080))
                flask_thread = threading.Thread(
                    target=lambda: self.flask_app.run(
                        host='0.0.0.0', 
                        port=port, 
                        debug=False,
                        use_reloader=False,
                        threaded=True
                    )
                )
                flask_thread.daemon = True
                flask_thread.start()
                logger.info(f"🌐 Health endpoints running on port {port}")
            
            # Start main trading loop
            self._run_trading_loop()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ System start failed: {e}")
            return False
    
    def _run_trading_loop(self):
        """Main trading loop with error handling and recovery."""
        logger.info("🔄 Starting main trading loop...")
        
        while self.running:
            try:
                cycle_start = time.time()
                
                # Run orchestrator cycle
                if self.orchestrator:
                    cycle_results = self.orchestrator.run_single_cycle()
                    self.cycle_count += 1
                    
                    # Update health status
                    self.last_health_check = datetime.now()
                    
                    # Log cycle results
                    if cycle_results:
                        logger.info(f"🎯 Cycle {self.cycle_count} completed: {cycle_results.get('summary', 'No summary')}")
                
                # Calculate cycle delay - OPTIMIZED FOR SUBSCRIPTION LEVEL
                cycle_duration = time.time() - cycle_start
                # Use data mode manager to get optimized cycle delay
                optimized_cycle_delay = self.data_mode_manager.get_cycle_delay()
                cycle_delay = max(0, optimized_cycle_delay - cycle_duration)
                
                if cycle_delay != optimized_cycle_delay:
                    logger.debug(f"⏱️ Cycle took {cycle_duration:.1f}s, next cycle in {cycle_delay:.1f}s")
                
                if cycle_delay > 0:
                    time.sleep(cycle_delay)
                
            except KeyboardInterrupt:
                logger.info("🛑 Shutdown signal received")
                break
            except Exception as e:
                self.error_count += 1
                logger.error(f"❌ Trading loop error #{self.error_count}: {e}")
                
                # Emergency handling
                if self.error_count > 10:
                    logger.critical("🚨 Too many errors, shutting down system")
                    break
                
                # Brief pause before retry
                time.sleep(30)
        
        logger.info("🛑 Trading loop stopped")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get basic system health status."""
        try:
            uptime = datetime.now() - self.start_time
            
            health_status = {
                'status': 'healthy' if self.running else 'stopped',
                'uptime_seconds': int(uptime.total_seconds()),
                'cycle_count': self.cycle_count,
                'error_count': self.error_count,
                'last_check': self.last_health_check.isoformat() if self.last_health_check else None,
                'timestamp': datetime.now().isoformat()
            }
            
            # Check component health
            if self.health_monitor:
                component_health = self.health_monitor.check_all_components()
                health_status['components'] = component_health
                
                # Overall status based on critical components
                if not component_health.get('alpaca', {}).get('healthy', False):
                    health_status['status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed system status."""
        basic_health = self.get_system_health()
        
        detailed_status = {
            **basic_health,
            'config': {
                'modular_system': self.config.get_bool('MODULAR_SYSTEM', True),
                'ml_optimization': self.config.get_bool('ML_OPTIMIZATION', True),
                'execution_enabled': self.config.get_bool('EXECUTION_ENABLED', False),
                'modules': {
                    'options': self.config.get_bool('OPTIONS_TRADING', True),
                    'crypto': self.config.get_bool('CRYPTO_TRADING', True),
                    'stocks': self.config.get_bool('STOCKS_TRADING', True)
                }
            },
            'performance': self.get_system_metrics()
        }
        
        return detailed_status
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        try:
            uptime = datetime.now() - self.start_time
            
            metrics = {
                'uptime_hours': round(uptime.total_seconds() / 3600, 2),
                'cycles_per_hour': round(self.cycle_count / max(uptime.total_seconds() / 3600, 0.01), 2),
                'error_rate': round(self.error_count / max(self.cycle_count, 1), 4),
                'memory_usage': self._get_memory_usage(),
            }
            
            # Add trading metrics if available
            if self.orchestrator:
                trading_metrics = self.orchestrator.get_performance_metrics()
                if trading_metrics:
                    metrics['trading'] = trading_metrics
            
            return metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': round(memory_info.rss / 1024 / 1024, 2),
                'vms_mb': round(memory_info.vms / 1024 / 1024, 2),
                'percent': round(process.memory_percent(), 2)
            }
        except ImportError:
            return {'error': 'psutil not available'}
        except Exception as e:
            return {'error': str(e)}
    
    def shutdown(self):
        """Graceful system shutdown."""
        logger.info("🛑 Initiating graceful shutdown...")
        
        self.running = False
        
        # Shutdown orchestrator
        if self.orchestrator:
            try:
                self.orchestrator.shutdown()
                logger.info("✅ Orchestrator shutdown complete")
            except Exception as e:
                logger.error(f"❌ Orchestrator shutdown error: {e}")
        
        # Close Firebase connection
        if self.firebase_db:
            try:
                # Firebase connections close automatically
                logger.info("✅ Firebase connection closed")
            except Exception as e:
                logger.error(f"❌ Firebase shutdown error: {e}")
        
        logger.info("✅ Graceful shutdown complete")
    
    def _emergency_allocation_check(self):
        """Emergency check for catastrophic allocation failures"""
        try:
            logger.info("🚨 EMERGENCY ALLOCATION CHECK")
            
            # Get account and positions
            account = self.alpaca_api.get_account()
            positions = self.alpaca_api.list_positions()
            
            buying_power = float(account.buying_power)
            portfolio_value = float(account.portfolio_value)
            
            # Calculate current allocation
            crypto_value = 0
            stock_value = 0
            
            for pos in positions:
                value = abs(float(pos.market_value))
                if any(crypto in pos.symbol for crypto in ['BTC', 'ETH', 'SOL', 'AVAX', 'LINK', 'UNI', 'AAVE', 'DOT', 'MATIC']):
                    crypto_value += value
                else:
                    stock_value += value
            
            total_invested = crypto_value + stock_value
            crypto_pct = (crypto_value / portfolio_value * 100) if portfolio_value > 0 else 0
            unused_pct = (buying_power / portfolio_value * 100) if portfolio_value > 0 else 0
            
            logger.info(f"💰 Portfolio: ${portfolio_value:,.0f}")
            logger.info(f"🔓 Buying Power: ${buying_power:,.0f} ({unused_pct:.1f}%)")
            logger.info(f"₿ Crypto: ${crypto_value:,.0f} ({crypto_pct:.1f}%)")
            logger.info(f"📈 Stocks: ${stock_value:,.0f}")
            
            # Check for allocation disasters
            if crypto_pct > 50:
                logger.error(f"🚨 ALLOCATION DISASTER: {crypto_pct:.1f}% in crypto during bullish stock market!")
            
            if unused_pct > 70:
                logger.error(f"🚨 UNUSED CAPITAL DISASTER: {unused_pct:.1f}% buying power unused!")
            
            if stock_value < 10000 and buying_power > 100000:
                logger.error(f"🚨 BULLISH MARKET MISS: Only ${stock_value:,.0f} in stocks with ${buying_power:,.0f} available!")
                logger.error("💡 SPY/QQQ showing 68-72% bullish confidence - should be trading aggressively!")
            
        except Exception as e:
            logger.error(f"❌ Emergency allocation check failed: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"🛑 Received signal {signum}")
    if hasattr(signal_handler, 'system'):
        signal_handler.system.shutdown()
    sys.exit(0)


def main():
    """Main production entry point."""
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🚀 MODULAR TRADING SYSTEM - PRODUCTION STARTUP") 
    logger.info("🔧 CRITICAL FIX: Order Executor Implementation - v1.5")
    logger.info("🎯 ORDER EXECUTION SHOULD NOW WORK")
    logger.info("🎯 SUCCESSFUL TRADES EXPECTED")
    logger.info("=" * 60)
    logger.info(f"⏰ Start Time: {datetime.now()}")
    logger.info(f"🐍 Python Version: {sys.version}")
    logger.info(f"📁 Working Directory: {os.getcwd()}")
    logger.info(f"🌍 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    logger.info("")
    
    # Initialize and start the system
    system = ProductionTradingSystem()
    signal_handler.system = system  # Store reference for signal handler
    
    try:
        success = system.start_system()
        
        if success:
            logger.info("✅ Production system started successfully")
        else:
            logger.error("❌ Production system failed to start")
            sys.exit(1)
            
    except Exception as e:
        logger.critical(f"🚨 Critical system error: {e}")
        sys.exit(1)
    finally:
        system.shutdown()


if __name__ == "__main__":
    main()