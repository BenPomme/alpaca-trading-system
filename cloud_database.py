#!/usr/bin/env python3
"""
Cloud Database Manager for 24/7 Trading System
Stores trading data in GitHub repository for persistence across all environments
"""

import json
import os
import sqlite3
import subprocess
from datetime import datetime
from typing import Dict, List, Any
import base64

class CloudDatabase:
    """Manages trading data storage in GitHub for 24/7 persistence"""
    
    def __init__(self):
        self.local_db_path = "data/trading_system.db"
        self.cloud_data_path = "data/cloud_trading_data.json"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs("data", exist_ok=True)
    
    def export_local_db_to_cloud(self):
        """Export local SQLite database to JSON for cloud storage"""
        try:
            if not os.path.exists(self.local_db_path):
                print("⚠️ No local database found to export")
                return False
            
            print("📤 Exporting local database to cloud format...")
            
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            cloud_data = {
                'exported_at': datetime.now().isoformat(),
                'tables': {},
                'metadata': {
                    'version': '1.0',
                    'source': 'local_db_export'
                }
            }
            
            # Export each table
            for (table_name,) in tables:
                print(f"📊 Exporting table: {table_name}")
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # Get table data
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                cloud_data['tables'][table_name] = {
                    'columns': columns,
                    'rows': [list(row) for row in rows],
                    'count': len(rows)
                }
                
                print(f"✅ Exported {len(rows)} rows from {table_name}")
            
            conn.close()
            
            # Save to JSON file
            with open(self.cloud_data_path, 'w') as f:
                json.dump(cloud_data, f, indent=2, default=str)
            
            print(f"✅ Database exported to {self.cloud_data_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting database: {e}")
            return False
    
    def import_cloud_to_local_db(self):
        """Import cloud JSON data back to local SQLite database"""
        try:
            if not os.path.exists(self.cloud_data_path):
                print("⚠️ No cloud data found to import")
                return False
            
            print("📥 Importing cloud data to local database...")
            
            with open(self.cloud_data_path, 'r') as f:
                cloud_data = json.load(f)
            
            # Create/connect to local database
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            # Import each table
            for table_name, table_data in cloud_data['tables'].items():
                columns = table_data['columns']
                rows = table_data['rows']
                
                print(f"📊 Importing table: {table_name} ({len(rows)} rows)")
                
                # Drop existing table
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                
                # Create table (simple approach - adjust types as needed)
                columns_def = ", ".join([f"{col} TEXT" for col in columns])
                cursor.execute(f"CREATE TABLE {table_name} ({columns_def})")
                
                # Insert data
                if rows:
                    placeholders = ", ".join(["?" for _ in columns])
                    cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", rows)
                
                print(f"✅ Imported {len(rows)} rows to {table_name}")
            
            conn.commit()
            conn.close()
            
            print(f"✅ Cloud data imported to {self.local_db_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error importing cloud data: {e}")
            return False
    
    def sync_to_github(self):
        """Push cloud data to GitHub repository"""
        try:
            print("📤 Syncing data to GitHub...")
            
            # Check if there are changes
            result = subprocess.run(["git", "diff", "--quiet", self.cloud_data_path], 
                                  capture_output=True)
            
            if result.returncode == 0:
                print("ℹ️ No changes to sync")
                return True
            
            # Add, commit, and push
            subprocess.run(["git", "add", self.cloud_data_path], check=True)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
            commit_msg = f"📊 Sync trading data to cloud {timestamp}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            
            print("✅ Trading data synced to GitHub")
            return True
            
        except Exception as e:
            print(f"❌ Error syncing to GitHub: {e}")
            return False
    
    def sync_from_github(self):
        """Pull latest cloud data from GitHub"""
        try:
            print("📥 Syncing data from GitHub...")
            
            # Pull latest changes
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            
            # Import to local database
            if os.path.exists(self.cloud_data_path):
                self.import_cloud_to_local_db()
                print("✅ Data synced from GitHub")
                return True
            else:
                print("⚠️ No cloud data found after pull")
                return False
                
        except Exception as e:
            print(f"❌ Error syncing from GitHub: {e}")
            return False
    
    def get_cloud_data_for_api(self) -> Dict[str, Any]:
        """Get trading data directly from cloud storage for API use"""
        try:
            if not os.path.exists(self.cloud_data_path):
                return {}
            
            with open(self.cloud_data_path, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"❌ Error reading cloud data: {e}")
            return {}
    
    def full_sync_cycle(self):
        """Complete sync cycle: local -> cloud -> GitHub"""
        print("🔄 Starting full sync cycle...")
        
        # Export local data to cloud format
        if self.export_local_db_to_cloud():
            # Sync to GitHub
            if self.sync_to_github():
                print("✅ Full sync cycle completed")
                return True
        
        print("❌ Sync cycle failed")
        return False

def main():
    """Test the cloud database functionality"""
    cloud_db = CloudDatabase()
    
    print("🧪 Testing Cloud Database System")
    print("=" * 50)
    
    # Test export
    if cloud_db.export_local_db_to_cloud():
        print("✅ Export test passed")
    else:
        print("❌ Export test failed")
    
    # Test full sync
    if cloud_db.full_sync_cycle():
        print("✅ Full sync test passed")
    else:
        print("❌ Full sync test failed")

if __name__ == "__main__":
    main()