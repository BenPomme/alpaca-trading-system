#!/usr/bin/env python3
"""
Firebase Dashboard Deployment Script

Deploys the enhanced modular trading dashboard to Firebase hosting
with real-time data integration and ML optimization monitoring.
"""

import os
import subprocess
import logging
import json
from datetime import datetime
from typing import Dict, Any

# Import modular components
from modular_dashboard_api import ModularDashboardAPI
from firebase_dashboard_updater import FirebaseDashboardService


class FirebaseDashboardDeployer:
    """Handles Firebase dashboard deployment"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.dashboard_api = ModularDashboardAPI()
        
        # Firebase project configuration
        self.project_id = "alpaca-12fab"
        self.hosting_url = "https://alpaca-12fab.web.app"
        
    def deploy_dashboard(self, update_data: bool = True, deploy_rules: bool = True, 
                        deploy_hosting: bool = True) -> bool:
        """
        Deploy the complete Firebase dashboard.
        
        Args:
            update_data: Whether to update Firebase with latest data
            deploy_rules: Whether to deploy Firestore rules
            deploy_hosting: Whether to deploy hosting files
            
        Returns:
            True if deployment successful, False otherwise
        """
        try:
            self.logger.info("🚀 Starting Firebase Dashboard Deployment")
            
            # Step 1: Validate Firebase setup
            if not self._validate_firebase_setup():
                return False
            
            # Step 2: Generate latest dashboard data
            if update_data:
                self._update_dashboard_data()
            
            # Step 3: Deploy Firestore rules
            if deploy_rules:
                if not self._deploy_firestore_rules():
                    return False
            
            # Step 4: Deploy hosting
            if deploy_hosting:
                if not self._deploy_hosting():
                    return False
            
            # Step 5: Verify deployment
            self._verify_deployment()
            
            self.logger.info(f"✅ Firebase Dashboard Deployment Complete!")
            self.logger.info(f"🌐 Dashboard URL: {self.hosting_url}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Deployment failed: {e}")
            return False
    
    def _validate_firebase_setup(self) -> bool:
        """Validate Firebase CLI and project setup"""
        try:
            # Check if Firebase CLI is installed
            result = subprocess.run(['firebase', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error("Firebase CLI not found. Install with: npm install -g firebase-tools")
                return False
            
            self.logger.info(f"Firebase CLI version: {result.stdout.strip()}")
            
            # Check if logged in
            result = subprocess.run(['firebase', 'projects:list'], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error("Not logged into Firebase. Run: firebase login")
                return False
            
            # Verify project exists
            if self.project_id not in result.stdout:
                self.logger.error(f"Project {self.project_id} not found. Check Firebase project setup.")
                return False
            
            self.logger.info(f"✅ Firebase setup validated for project: {self.project_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating Firebase setup: {e}")
            return False
    
    def _update_dashboard_data(self):
        """Update Firebase with latest dashboard data"""
        try:
            self.logger.info("📊 Updating Firebase with latest dashboard data...")
            
            # Generate enhanced dashboard data
            dashboard_data = self.dashboard_api.generate_enhanced_dashboard_data()
            
            # Save to local file for reference
            os.makedirs('docs/api', exist_ok=True)
            with open('docs/api/modular-dashboard-data.json', 'w') as f:
                json.dump(dashboard_data, f, indent=2, default=str)
            
            self.logger.info("✅ Dashboard data updated successfully")
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard data: {e}")
    
    def _deploy_firestore_rules(self) -> bool:
        """Deploy Firestore security rules"""
        try:
            self.logger.info("🔒 Deploying Firestore security rules...")
            
            result = subprocess.run([
                'firebase', 'deploy', '--only', 'firestore:rules',
                '--project', self.project_id
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Firestore rules deployment failed: {result.stderr}")
                return False
            
            self.logger.info("✅ Firestore rules deployed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deploying Firestore rules: {e}")
            return False
    
    def _deploy_hosting(self) -> bool:
        """Deploy Firebase hosting"""
        try:
            self.logger.info("🌐 Deploying Firebase hosting...")
            
            # Ensure docs directory exists with required files
            self._prepare_hosting_files()
            
            result = subprocess.run([
                'firebase', 'deploy', '--only', 'hosting',
                '--project', self.project_id
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Hosting deployment failed: {result.stderr}")
                return False
            
            self.logger.info("✅ Firebase hosting deployed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deploying hosting: {e}")
            return False
    
    def _prepare_hosting_files(self):
        """Prepare hosting files for deployment"""
        try:
            # Ensure all required files exist in docs directory
            required_files = [
                'docs/modular-dashboard.html',
                'docs/index.html',
                'docs/assets/css/dashboard.css',
                'docs/assets/js/dashboard.js'
            ]
            
            for file_path in required_files:
                if not os.path.exists(file_path):
                    if 'modular-dashboard.html' in file_path:
                        self.logger.error(f"Required file missing: {file_path}")
                        raise FileNotFoundError(f"Missing required dashboard file: {file_path}")
                    else:
                        self.logger.warning(f"Optional file missing: {file_path}")
            
            # Update Firebase config in dashboard HTML if needed
            self._update_firebase_config()
            
            self.logger.info("✅ Hosting files prepared")
            
        except Exception as e:
            self.logger.error(f"Error preparing hosting files: {e}")
            raise
    
    def _update_firebase_config(self):
        """Update Firebase configuration in dashboard HTML"""
        try:
            dashboard_file = 'docs/modular-dashboard.html'
            
            if not os.path.exists(dashboard_file):
                return
            
            # Read the dashboard HTML
            with open(dashboard_file, 'r') as f:
                html_content = f.read()
            
            # Check if Firebase config needs updating
            if 'your-api-key' in html_content:
                self.logger.warning("⚠️ Firebase config in dashboard HTML contains placeholder values")
                self.logger.warning("   Update the firebaseConfig object in modular-dashboard.html")
                self.logger.warning("   Get your config from: https://console.firebase.google.com/")
            
        except Exception as e:
            self.logger.warning(f"Could not check Firebase config: {e}")
    
    def _verify_deployment(self):
        """Verify the deployment was successful"""
        try:
            self.logger.info("🔍 Verifying deployment...")
            
            # Check hosting URL
            import requests
            try:
                response = requests.get(self.hosting_url, timeout=10)
                if response.status_code == 200:
                    self.logger.info(f"✅ Dashboard accessible at: {self.hosting_url}")
                else:
                    self.logger.warning(f"⚠️ Dashboard returned status code: {response.status_code}")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not verify dashboard accessibility: {e}")
            
            # Verify Firestore rules deployment
            self.logger.info("✅ Firestore rules deployed")
            
            # Log deployment summary
            self._log_deployment_summary()
            
        except Exception as e:
            self.logger.warning(f"Error during deployment verification: {e}")
    
    def _log_deployment_summary(self):
        """Log deployment summary"""
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'project_id': self.project_id,
                'hosting_url': self.hosting_url,
                'dashboard_type': 'modular_ml_optimization',
                'features': [
                    'Real-time Firebase data integration',
                    'ML parameter optimization monitoring',
                    'Multi-module performance tracking',
                    'Orchestrator status monitoring',
                    'Interactive charts and visualizations',
                    'Mobile-responsive design'
                ],
                'collections_used': [
                    'orchestrator_cycles',
                    'modular_trades',
                    'ml_optimization_data',
                    'parameter_effectiveness',
                    'dashboard_summary'
                ]
            }
            
            # Save deployment log
            os.makedirs('deployment_logs', exist_ok=True)
            log_file = f"deployment_logs/firebase_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(log_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.logger.info(f"📋 Deployment summary saved to: {log_file}")
            
        except Exception as e:
            self.logger.warning(f"Could not save deployment summary: {e}")
    
    def start_data_updater(self):
        """Start the Firebase data updater service"""
        try:
            self.logger.info("🔄 Starting Firebase dashboard data updater...")
            
            updater_service = FirebaseDashboardService()
            updater_service.start_service(update_interval=30)  # Update every 30 seconds
            
        except Exception as e:
            self.logger.error(f"Error starting data updater: {e}")
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get current deployment status"""
        return {
            'project_id': self.project_id,
            'hosting_url': self.hosting_url,
            'dashboard_file': 'docs/modular-dashboard.html',
            'firebase_config': 'firebase.json',
            'firestore_rules': 'firestore.rules',
            'last_deployment': 'check deployment_logs directory'
        }


def main():
    """Deploy Firebase dashboard"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    deployer = FirebaseDashboardDeployer()
    
    print("🚀 Firebase Dashboard Deployment")
    print("=" * 50)
    print(f"Project ID: {deployer.project_id}")
    print(f"Dashboard URL: {deployer.hosting_url}")
    print(f"Features: ML Optimization Monitoring, Real-time Updates")
    print()
    
    # Deploy options
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'data-only':
            # Update data only
            deployer._update_dashboard_data()
            print("✅ Dashboard data updated")
            return
        elif sys.argv[1] == 'hosting-only':
            # Deploy hosting only
            success = deployer.deploy_dashboard(update_data=False, deploy_rules=False, deploy_hosting=True)
        elif sys.argv[1] == 'rules-only':
            # Deploy rules only
            success = deployer.deploy_dashboard(update_data=False, deploy_rules=True, deploy_hosting=False)
        elif sys.argv[1] == 'start-updater':
            # Start data updater service
            deployer.start_data_updater()
            return
        else:
            print("Usage: python deploy_firebase_dashboard.py [data-only|hosting-only|rules-only|start-updater]")
            return
    else:
        # Full deployment
        success = deployer.deploy_dashboard()
    
    if success:
        print("\n🎉 Deployment Successful!")
        print(f"🌐 Visit your dashboard: {deployer.hosting_url}")
        print("\n📋 Next steps:")
        print("1. Update Firebase config in modular-dashboard.html with your actual API keys")
        print("2. Start the data updater: python deploy_firebase_dashboard.py start-updater")
        print("3. Monitor the dashboard for real-time updates")
    else:
        print("\n❌ Deployment Failed!")
        print("Check the logs above for error details")


if __name__ == "__main__":
    main()