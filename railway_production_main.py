#!/usr/bin/env python3
"""
Railway Production Entry Point

Railway-specific version that ensures Flask server starts even if trading
components fail to initialize. This allows for debugging and health monitoring.
"""

import os
import sys
import time
import logging
from datetime import datetime
from flask import Flask, jsonify
import threading

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

class RailwayProductionSystem:
    """
    Railway-specific production system that prioritizes web server availability
    over trading functionality for debugging purposes.
    """
    
    def __init__(self):
        self.flask_app = Flask(__name__)
        self.system_status = "initializing"
        self.trading_system = None
        self.start_time = datetime.now()
        self.error_messages = []
        
        # Initialize Flask endpoints immediately
        self._setup_flask_endpoints()
        
    def _setup_flask_endpoints(self):
        """Setup Flask endpoints for Railway health checking and debugging."""
        
        @self.flask_app.route('/')
        def root():
            return jsonify({
                "status": "Railway deployment running",
                "application": "Alpaca Trading System",
                "start_time": self.start_time.isoformat(),
                "system_status": self.system_status,
                "errors": len(self.error_messages)
            })
        
        @self.flask_app.route('/health')
        def health():
            """Health check for Railway."""
            return "OK", 200
            
        @self.flask_app.route('/status')
        def status():
            """Detailed status for debugging."""
            return jsonify({
                "system_status": self.system_status,
                "start_time": self.start_time.isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "trading_system_initialized": self.trading_system is not None,
                "error_count": len(self.error_messages),
                "recent_errors": self.error_messages[-5:] if self.error_messages else []
            })
            
        @self.flask_app.route('/debug')
        def debug():
            """Debug information for troubleshooting."""
            env_vars = {}
            for key in ['ALPACA_PAPER_API_KEY', 'ALPACA_PAPER_SECRET_KEY', 'OPENAI_API_KEY']:
                env_vars[key] = "SET" if os.environ.get(key) else "NOT SET"
                
            return jsonify({
                "environment_variables": env_vars,
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "railway_environment": os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
                "port": os.environ.get('PORT', 'not set'),
                "system_errors": self.error_messages
            })
            
        @self.flask_app.route('/modules')
        def modules_status():
            """Module status information."""
            if self.trading_system and hasattr(self.trading_system, 'orchestrator'):
                try:
                    active_modules = self.trading_system.orchestrator.registry.get_active_modules()
                    return jsonify({
                        "modules_registered": len(active_modules),
                        "active_modules": [m.module_name for m in active_modules],
                        "status": "trading_system_running"
                    })
                except Exception as e:
                    return jsonify({
                        "error": str(e),
                        "status": "trading_system_error"
                    })
            else:
                return jsonify({
                    "modules_registered": 0,
                    "active_modules": [],
                    "status": "trading_system_not_initialized"
                })
                
        @self.flask_app.route('/trading')
        def trading_status():
            """Trading system status."""
            if self.trading_system:
                return jsonify({
                    "status": "initialized",
                    "running": getattr(self.trading_system, 'running', False),
                    "cycle_count": getattr(self.trading_system, 'cycle_count', 0)
                })
            else:
                return jsonify({
                    "status": "not_initialized",
                    "reason": "System failed to start",
                    "errors": self.error_messages
                })
    
    def start_system(self):
        """Start the Railway production system."""
        logger.info("🚀 Railway Production System Starting...")
        logger.info(f"📡 Port: {os.environ.get('PORT', 'not set')}")
        logger.info(f"🌍 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')}")
        
        # Start Flask server first (critical for Railway health checks)
        self._start_flask_server()
        
        # Try to initialize trading system (but don't fail if it doesn't work)
        self._try_initialize_trading_system()
        
        # Keep the main thread alive
        self._run_main_loop()
    
    def _start_flask_server(self):
        """Start Flask server in background thread."""
        try:
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
            
            logger.info(f"✅ Flask server started on port {port}")
            logger.info(f"🌐 Health endpoint: http://0.0.0.0:{port}/health")
            logger.info(f"🔍 Debug endpoint: http://0.0.0.0:{port}/debug")
            
            # Give Flask time to start
            time.sleep(2)
            self.system_status = "flask_running"
            
        except Exception as e:
            logger.error(f"❌ Flask server failed to start: {e}")
            self.error_messages.append(f"Flask startup error: {str(e)}")
            self.system_status = "flask_failed"
    
    def _try_initialize_trading_system(self):
        """Try to initialize the trading system, but don't fail if it doesn't work."""
        try:
            logger.info("🔄 Attempting to initialize trading system...")
            
            # Import and initialize the full trading system
            from modular_production_main import ProductionTradingSystem
            
            self.trading_system = ProductionTradingSystem()
            
            # Try to initialize components
            if self.trading_system.initialize_components():
                logger.info("✅ Trading system initialized successfully")
                self.system_status = "trading_system_ready"
                
                # Start trading loop in background
                self._start_trading_loop()
            else:
                logger.warning("⚠️ Trading system initialization failed")
                self.system_status = "trading_system_failed"
                self.error_messages.append("Trading system initialization failed")
                
        except Exception as e:
            logger.error(f"❌ Trading system error: {e}")
            self.error_messages.append(f"Trading system error: {str(e)}")
            self.system_status = "trading_system_error"
            
    def _start_trading_loop(self):
        """Start trading loop in background thread."""
        try:
            if self.trading_system:
                trading_thread = threading.Thread(
                    target=self.trading_system._run_trading_loop
                )
                trading_thread.daemon = True
                trading_thread.start()
                logger.info("✅ Trading loop started in background")
                self.system_status = "fully_operational"
        except Exception as e:
            logger.error(f"❌ Trading loop failed to start: {e}")
            self.error_messages.append(f"Trading loop error: {str(e)}")
    
    def _run_main_loop(self):
        """Keep the main thread alive for Railway."""
        logger.info("🔄 Main loop started - system will stay alive for Railway")
        
        try:
            while True:
                time.sleep(30)  # Health check every 30 seconds
                
                # Update system status
                current_time = datetime.now()
                uptime = (current_time - self.start_time).total_seconds()
                
                if uptime % 300 == 0:  # Log every 5 minutes
                    logger.info(f"💓 System alive - uptime: {uptime:.0f}s, status: {self.system_status}")
                    
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown signal received")
        except Exception as e:
            logger.error(f"❌ Main loop error: {e}")
            self.error_messages.append(f"Main loop error: {str(e)}")

def main():
    """Railway entry point."""
    logger.info("🚀 RAILWAY PRODUCTION SYSTEM - STARTUP")
    logger.info("🔧 Ensures Flask server starts even if trading fails")
    logger.info("=" * 60)
    logger.info(f"⏰ Start Time: {datetime.now()}")
    logger.info(f"🐍 Python Version: {sys.version}")
    logger.info(f"📁 Working Directory: {os.getcwd()}")
    logger.info(f"🌍 Railway Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')}")
    logger.info("")
    
    # Create and start Railway system
    system = RailwayProductionSystem()
    system.start_system()

if __name__ == "__main__":
    main()