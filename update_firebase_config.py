#!/usr/bin/env python3
"""
Firebase Dashboard Configuration Updater

This script helps you easily update the Firebase configuration in your dashboard
with your actual Firebase project credentials.
"""

import os
import re

def update_firebase_config(api_key, sender_id, app_id):
    """
    Update the Firebase configuration in the dashboard HTML file.
    
    Args:
        api_key: Your Firebase API key (starts with AIzaSy...)
        sender_id: Your Firebase sender ID (usually a 12-digit number)
        app_id: Your Firebase app ID (format: 1:number:web:alphanumeric)
    """
    
    dashboard_file = 'docs/modular-dashboard.html'
    
    if not os.path.exists(dashboard_file):
        print(f"❌ Dashboard file not found: {dashboard_file}")
        return False
    
    print("🔥 Updating Firebase configuration in dashboard...")
    
    # Read the current file
    with open(dashboard_file, 'r') as f:
        content = f.read()
    
    # Replace the placeholder values
    content = content.replace('YOUR_ACTUAL_API_KEY_HERE', api_key)
    content = content.replace('YOUR_ACTUAL_SENDER_ID', sender_id)  
    content = content.replace('YOUR_ACTUAL_APP_ID', app_id)
    
    # Write the updated content
    with open(dashboard_file, 'w') as f:
        f.write(content)
    
    print("✅ Firebase configuration updated successfully!")
    print(f"📝 Updated file: {dashboard_file}")
    print("\n🚀 Next steps:")
    print("1. Deploy the updated dashboard: python deploy_firebase_dashboard.py hosting-only")
    print("2. Visit your dashboard: https://alpaca-12fab.web.app")
    print("3. Check browser console for Firebase connection status")
    
    return True

def get_firebase_config_from_user():
    """Get Firebase configuration from user input."""
    
    print("🔥 Firebase Dashboard Configuration Setup")
    print("=" * 50)
    print("You need to get these values from:")
    print("https://console.firebase.google.com/project/alpaca-12fab/settings/general")
    print("\nLook for the 'Your apps' section and select your web app.\n")
    
    # Get API Key
    api_key = input("Enter your Firebase API Key (starts with 'AIzaSy'): ").strip()
    if not api_key.startswith('AIzaSy'):
        print("⚠️  Warning: API key should start with 'AIzaSy'")
    
    # Get Sender ID  
    sender_id = input("Enter your Firebase Messaging Sender ID (12-digit number): ").strip()
    if not sender_id.isdigit() or len(sender_id) != 12:
        print("⚠️  Warning: Sender ID should be a 12-digit number")
    
    # Get App ID
    app_id = input("Enter your Firebase App ID (format 1:number:web:alphanumeric): ").strip()
    if not app_id.startswith('1:') or ':web:' not in app_id:
        print("⚠️  Warning: App ID should have format '1:number:web:alphanumeric'")
    
    print(f"\n📋 Configuration Summary:")
    print(f"API Key: {api_key}")
    print(f"Sender ID: {sender_id}")
    print(f"App ID: {app_id}")
    
    confirm = input("\nProceed with this configuration? (y/n): ").strip().lower()
    
    if confirm == 'y':
        return update_firebase_config(api_key, sender_id, app_id)
    else:
        print("❌ Configuration update cancelled")
        return False

def main():
    """Main function"""
    
    # Check if we're in the right directory
    if not os.path.exists('docs/modular-dashboard.html'):
        print("❌ Please run this script from the Alpaca directory")
        print("Current directory should contain: docs/modular-dashboard.html")
        return
    
    print("🎯 Firebase Dashboard Configuration Updater")
    print("\nThis script will help you connect your dashboard to real Firebase data.")
    print("You need your Firebase project configuration from the Firebase Console.\n")
    
    get_firebase_config_from_user()

if __name__ == "__main__":
    main()