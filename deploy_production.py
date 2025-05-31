#!/usr/bin/env python3
"""
Production Deployment Script

Handles the complete deployment of the modular trading system to production,
including environment validation, Railway configuration, and health monitoring setup.
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionDeployer:
    """
    Handles complete production deployment of the modular trading system.
    
    Manages Railway deployment, environment variable configuration,
    health monitoring setup, and deployment validation.
    """
    
    def __init__(self):
        """Initialize the production deployer."""
        self.project_name = "modular-trading-system"
        self.railway_services = ["main", "dashboard-updater"]
        self.required_env_vars = self._get_required_env_vars()
        
        logger.info("🚀 Production Deployer initialized")
    
    def _get_required_env_vars(self) -> Dict[str, Dict[str, Any]]:
        """Get list of required environment variables by category."""
        return {
            'alpaca': {
                'ALPACA_PAPER_API_KEY': {'required': True, 'description': 'Alpaca Paper Trading API Key'},
                'ALPACA_PAPER_SECRET_KEY': {'required': True, 'description': 'Alpaca Paper Trading Secret Key'},
                'ALPACA_BASE_URL': {'required': False, 'default': 'https://paper-api.alpaca.markets'}
            },
            'firebase': {
                'FIREBASE_PRIVATE_KEY_ID': {'required': True, 'description': 'Firebase Private Key ID'},
                'FIREBASE_PRIVATE_KEY': {'required': True, 'description': 'Firebase Private Key (with newlines as \\n)'},
                'FIREBASE_CLIENT_EMAIL': {'required': True, 'description': 'Firebase Client Email'},
                'FIREBASE_CLIENT_ID': {'required': True, 'description': 'Firebase Client ID'},
                'FIREBASE_CLIENT_CERT_URL': {'required': True, 'description': 'Firebase Client Certificate URL'}
            },
            'trading': {
                'EXECUTION_ENABLED': {'required': False, 'default': 'true'},
                'MODULAR_SYSTEM': {'required': False, 'default': 'true'},
                'ML_OPTIMIZATION': {'required': False, 'default': 'true'},
                'OPTIONS_TRADING': {'required': False, 'default': 'true'},
                'CRYPTO_TRADING': {'required': False, 'default': 'true'},
                'STOCKS_TRADING': {'required': False, 'default': 'true'}
            },
            'performance': {
                'ORCHESTRATOR_CYCLE_DELAY': {'required': False, 'default': '120'},
                'ML_OPTIMIZATION_INTERVAL': {'required': False, 'default': '600'},
                'DASHBOARD_UPDATE_INTERVAL': {'required': False, 'default': '30'},
                'MAX_CONCURRENT_MODULES': {'required': False, 'default': '3'}
            },
            'risk': {
                'MAX_PORTFOLIO_RISK': {'required': False, 'default': '0.20'},
                'MAX_POSITION_SIZE': {'required': False, 'default': '0.10'},
                'OPTIONS_MAX_ALLOCATION': {'required': False, 'default': '0.30'},
                'CRYPTO_MAX_ALLOCATION': {'required': False, 'default': '0.20'}
            }
        }
    
    def validate_local_environment(self) -> bool:
        """Validate local environment before deployment."""
        logger.info("🔍 Validating local environment...")
        
        # Check if Railway CLI is installed
        if not self._check_railway_cli():
            return False
        
        # Check if git repository is clean
        if not self._check_git_status():
            return False
        
        # Check required files exist
        if not self._check_required_files():
            return False
        
        # Validate configuration files
        if not self._validate_config_files():
            return False
        
        logger.info("✅ Local environment validation passed")
        return True
    
    def _check_railway_cli(self) -> bool:
        """Check if Railway CLI is installed and authenticated."""
        try:
            result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Railway CLI not found. Install: npm install -g @railway/cli")
                return False
            
            logger.info(f"✅ Railway CLI version: {result.stdout.strip()}")
            
            # Check if logged in
            result = subprocess.run(['railway', 'whoami'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Not logged into Railway. Run: railway login")
                return False
            
            logger.info("✅ Railway authentication verified")
            return True
            
        except Exception as e:
            logger.error(f"❌ Railway CLI check failed: {e}")
            return False
    
    def _check_git_status(self) -> bool:
        """Check git repository status."""
        try:
            # Check if we're in a git repository
            result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Not in a git repository")
                return False
            
            # Check for uncommitted changes
            if result.stdout.strip():
                logger.warning("⚠️ Uncommitted changes detected")
                uncommitted = result.stdout.strip().split('\n')
                for change in uncommitted[:5]:  # Show first 5 changes
                    logger.warning(f"   {change}")
                if len(uncommitted) > 5:
                    logger.warning(f"   ... and {len(uncommitted) - 5} more changes")
                
                confirm = input("Continue with uncommitted changes? (y/n): ").strip().lower()
                if confirm != 'y':
                    logger.info("Deployment cancelled. Commit changes and try again.")
                    return False
            
            logger.info("✅ Git repository status OK")
            return True
            
        except Exception as e:
            logger.error(f"❌ Git status check failed: {e}")
            return False
    
    def _check_required_files(self) -> bool:
        """Check if all required files exist."""
        required_files = [
            'modular_production_main.py',
            'production_config.py',
            'production_health_check.py',
            'firebase_dashboard_updater.py',
            'requirements.txt',
            'modular/orchestrator.py',
            'modular/firebase_interface.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error("❌ Missing required files:")
            for file_path in missing_files:
                logger.error(f"   {file_path}")
            return False
        
        logger.info("✅ All required files present")
        return True
    
    def _validate_config_files(self) -> bool:
        """Validate configuration files."""
        try:
            # Test import of production config
            sys.path.insert(0, os.getcwd())
            from production_config import ProductionConfig
            
            config = ProductionConfig()
            config.log_configuration_summary()
            
            logger.info("✅ Production configuration validated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration validation failed: {e}")
            return False
    
    def setup_railway_project(self) -> bool:
        """Set up Railway project and services."""
        logger.info("🚄 Setting up Railway project...")
        
        try:
            # Check if already in a Railway project
            result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ Already connected to Railway project")
            else:
                # Link or create project
                logger.info("🔗 Linking to Railway project...")
                result = subprocess.run(['railway', 'link'], capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"❌ Failed to link Railway project: {result.stderr}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Railway project setup failed: {e}")
            return False
    
    def configure_environment_variables(self) -> bool:
        """Configure environment variables in Railway."""
        logger.info("🔧 Configuring environment variables...")
        
        # Get current environment variables
        current_env = self._get_railway_env_vars()
        
        # Check which variables are missing
        missing_vars = []
        
        for category, vars_dict in self.required_env_vars.items():
            for var_name, var_config in vars_dict.items():
                if var_config.get('required', False) and var_name not in current_env:
                    missing_vars.append((var_name, var_config['description']))
        
        if missing_vars:
            logger.warning("⚠️ Missing required environment variables:")
            for var_name, description in missing_vars:
                logger.warning(f"   {var_name}: {description}")
            
            logger.info("\n📋 Set these variables in Railway dashboard:")
            logger.info("   https://railway.app/dashboard")
            logger.info("   Go to your project → Variables tab")
            
            return False
        
        # Set default values for optional variables
        self._set_default_env_vars(current_env)
        
        logger.info("✅ Environment variables configured")
        return True
    
    def _get_railway_env_vars(self) -> Dict[str, str]:
        """Get current Railway environment variables."""
        try:
            result = subprocess.run(['railway', 'env'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning("⚠️ Could not fetch Railway environment variables")
                return {}
            
            # Parse environment variables
            env_vars = {}
            for line in result.stdout.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
            
            return env_vars
            
        except Exception as e:
            logger.warning(f"⚠️ Error fetching environment variables: {e}")
            return {}
    
    def _set_default_env_vars(self, current_env: Dict[str, str]):
        """Set default values for missing optional environment variables."""
        for category, vars_dict in self.required_env_vars.items():
            for var_name, var_config in vars_dict.items():
                if not var_config.get('required', False) and var_name not in current_env:
                    default_value = var_config.get('default')
                    if default_value:
                        try:
                            subprocess.run([
                                'railway', 'env', 'set', f'{var_name}={default_value}'
                            ], capture_output=True, text=True, check=True)
                            logger.info(f"✅ Set default value for {var_name}")
                        except:
                            logger.warning(f"⚠️ Could not set default for {var_name}")
    
    def deploy_to_railway(self) -> bool:
        """Deploy the application to Railway."""
        logger.info("🚀 Deploying to Railway...")
        
        try:
            # Update Procfile for production
            self._update_procfile()
            
            # Commit changes if needed
            self._commit_deployment_changes()
            
            # Deploy to Railway
            logger.info("📤 Pushing to Railway...")
            result = subprocess.run(['railway', 'up'], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Railway deployment failed: {result.stderr}")
                return False
            
            logger.info("✅ Railway deployment successful")
            
            # Get deployment URL
            deployment_url = self._get_deployment_url()
            if deployment_url:
                logger.info(f"🌐 Deployment URL: {deployment_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Railway deployment failed: {e}")
            return False
    
    def _update_procfile(self):
        """Update Procfile for production deployment."""
        try:
            # Copy production Procfile
            if os.path.exists('Procfile.production'):
                import shutil
                shutil.copy('Procfile.production', 'Procfile')
                logger.info("✅ Updated Procfile for production")
        except Exception as e:
            logger.warning(f"⚠️ Could not update Procfile: {e}")
    
    def _commit_deployment_changes(self):
        """Commit any deployment-related changes."""
        try:
            # Add deployment files
            subprocess.run(['git', 'add', 'Procfile'], capture_output=True)
            
            # Check if there are changes to commit
            result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            if result.stdout.strip():
                subprocess.run([
                    'git', 'commit', '-m', f'🚀 Production deployment {datetime.now().strftime("%Y-%m-%d %H:%M")}'
                ], capture_output=True, text=True)
                logger.info("✅ Committed deployment changes")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not commit changes: {e}")
    
    def _get_deployment_url(self) -> Optional[str]:
        """Get Railway deployment URL."""
        try:
            result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
            if result.returncode == 0:
                # Parse status output to find URL
                for line in result.stdout.split('\n'):
                    if 'https://' in line and 'railway.app' in line:
                        return line.strip().split()[-1]
            return None
        except:
            return None
    
    def validate_deployment(self) -> bool:
        """Validate the deployed application."""
        logger.info("🔍 Validating deployment...")
        
        try:
            deployment_url = self._get_deployment_url()
            if not deployment_url:
                logger.warning("⚠️ Could not get deployment URL")
                return False
            
            # Test health endpoint
            import requests
            import time
            
            logger.info("⏳ Waiting for deployment to start...")
            time.sleep(30)  # Give deployment time to start
            
            health_url = f"{deployment_url}/health"
            logger.info(f"🏥 Testing health endpoint: {health_url}")
            
            response = requests.get(health_url, timeout=30)
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Health check passed: {health_data.get('status', 'unknown')}")
                return True
            else:
                logger.error(f"❌ Health check failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Deployment validation failed: {e}")
            return False
    
    def deploy_complete_system(self) -> bool:
        """Deploy the complete modular trading system to production."""
        logger.info("🚀 MODULAR TRADING SYSTEM - PRODUCTION DEPLOYMENT")
        logger.info("=" * 60)
        
        # Step 1: Validate local environment
        if not self.validate_local_environment():
            logger.error("❌ Local environment validation failed")
            return False
        
        # Step 2: Setup Railway project
        if not self.setup_railway_project():
            logger.error("❌ Railway project setup failed")
            return False
        
        # Step 3: Configure environment variables
        if not self.configure_environment_variables():
            logger.error("❌ Environment configuration incomplete")
            logger.info("\n📋 Please set the missing environment variables and run again")
            return False
        
        # Step 4: Deploy to Railway
        if not self.deploy_to_railway():
            logger.error("❌ Railway deployment failed")
            return False
        
        # Step 5: Validate deployment
        if not self.validate_deployment():
            logger.warning("⚠️ Deployment validation failed, but deployment may still be successful")
        
        self._log_deployment_summary()
        
        logger.info("🎉 PRODUCTION DEPLOYMENT COMPLETE!")
        return True
    
    def _log_deployment_summary(self):
        """Log deployment summary and next steps."""
        deployment_url = self._get_deployment_url()
        
        logger.info("\n" + "=" * 60)
        logger.info("📋 DEPLOYMENT SUMMARY")
        logger.info("=" * 60)
        logger.info(f"🌐 Application URL: {deployment_url or 'Check Railway dashboard'}")
        logger.info(f"🏥 Health Check: {deployment_url}/health" if deployment_url else "Available at /health endpoint")
        logger.info(f"📊 Status Endpoint: {deployment_url}/status" if deployment_url else "Available at /status endpoint")
        logger.info(f"📈 Dashboard: https://alpaca-12fab.web.app")
        logger.info("")
        logger.info("📋 Next Steps:")
        logger.info("1. Monitor health endpoints for system status")
        logger.info("2. Check Firebase dashboard for real-time data")
        logger.info("3. Monitor Railway logs for any issues")
        logger.info("4. Verify trading functionality if EXECUTION_ENABLED=true")
        logger.info("")
        logger.info("🔧 Monitoring Commands:")
        logger.info("  railway logs          # View application logs")
        logger.info("  railway status        # Check service status")
        logger.info("  railway env           # View environment variables")


def main():
    """Main deployment function."""
    deployer = ProductionDeployer()
    
    try:
        success = deployer.deploy_complete_system()
        
        if success:
            logger.info("✅ Production deployment successful!")
            sys.exit(0)
        else:
            logger.error("❌ Production deployment failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"🚨 Deployment error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()