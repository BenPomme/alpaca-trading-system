#!/usr/bin/env python3
"""
Dashboard Update Script
Run this to update your GitHub Pages dashboard with latest trading data
"""

import subprocess
import sys
from dashboard_api import DashboardAPI

def update_dashboard():
    """Update dashboard data and push to GitHub"""
    print("📊 UPDATING TRADING DASHBOARD")
    print("=" * 50)
    
    try:
        # 1. Generate fresh dashboard data
        print("🔄 Generating fresh dashboard data...")
        api = DashboardAPI()
        data = api.generate_dashboard_data()
        api.save_to_file(data)
        
        print(f"✅ Dashboard data updated:")
        print(f"   Portfolio Value: ${data['portfolio']['value']:,.2f}")
        print(f"   Daily P&L: ${data['portfolio']['dailyPL']:+.2f} ({data['portfolio']['dailyPLPercent']:+.2f}%)")
        print(f"   Active Positions: {len(data['positions'])}")
        print(f"   Data Source: {data['data_source'].upper()}")
        
        # 2. Git operations
        print("\n🔄 Pushing updates to GitHub...")
        
        # Add the updated JSON file
        result = subprocess.run(['git', 'add', 'docs/api/dashboard-data.json'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Check if there are changes to commit
        result = subprocess.run(['git', 'diff', '--staged', '--quiet'], 
                              capture_output=True)
        if result.returncode == 0:
            print("ℹ️ No changes to dashboard data")
            return True
        
        # Commit the changes
        from datetime import datetime
        commit_msg = f"📊 Update dashboard data - {datetime.now().strftime('%Y-%m-%d %H:%M')} - Portfolio: ${data['portfolio']['value']:,.0f}"
        
        result = subprocess.run(['git', 'commit', '-m', commit_msg], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git commit failed: {result.stderr}")
            return False
        
        # Push to GitHub
        result = subprocess.run(['git', 'push'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git push failed: {result.stderr}")
            return False
        
        print("✅ Dashboard successfully updated on GitHub!")
        print("🔗 View at: https://benpomme.github.io/alpaca-trading-system")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating dashboard: {e}")
        return False

def main():
    """Main execution"""
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        print("🧪 DRY RUN MODE - No git operations")
        api = DashboardAPI()
        data = api.generate_dashboard_data()
        api.save_to_file(data)
        print("✅ Dashboard data generated locally only")
    else:
        success = update_dashboard()
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()