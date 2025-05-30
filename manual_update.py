#!/usr/bin/env python3
"""
Manual Dashboard Update Script
Run this locally to update dashboard data and push to GitHub
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, description):
    """Run a command and handle errors"""
    try:
        print(f"🔄 {description}...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        if result.stdout:
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr.strip()}")
        return False

def main():
    print("🚀 Manual Dashboard Update Starting...")
    
    # Step 1: Generate fresh dashboard data
    if not run_command("python dashboard_api.py", "Generating dashboard data"):
        return False
    
    # Step 2: Check if there are changes
    result = subprocess.run("git diff --quiet docs/api/dashboard-data.json", 
                          shell=True, capture_output=True)
    
    if result.returncode == 0:
        print("ℹ️ No changes to dashboard data")
        return True
    
    print("📊 Changes detected in dashboard data")
    
    # Step 3: Add, commit, and push changes
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    commit_msg = f"📊 Manual dashboard update {timestamp}"
    
    commands = [
        ("git add docs/api/dashboard-data.json", "Staging changes"),
        (f'git commit -m "{commit_msg}"', "Committing changes"),
        ("git push origin main", "Pushing to GitHub")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    print("✅ Dashboard successfully updated!")
    print("🌐 Your dashboard will update in 1-2 minutes at:")
    print("   https://benpomme.github.io/alpaca-trading-system")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Update failed. Check the errors above.")
        sys.exit(1)
    print("\n🎯 Manual update completed successfully!")