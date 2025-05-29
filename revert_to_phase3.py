#!/usr/bin/env python3
"""
Emergency Revert Script - Phase 4.1 to Phase 3
Quickly rollback global trading changes if deployment fails
"""

import os
import shutil
from datetime import datetime

def create_backup():
    """Create backup of current Phase 4.1 files"""
    backup_dir = f"backup_phase4_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'start_phase3.py',
        'risk_manager.py', 
        'market_universe.py',
        'phase3_trader.py',
        'requirements.txt',
        'CLAUDE.md'
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
    
    print(f"✅ Phase 4.1 backup created: {backup_dir}")
    return backup_dir

def revert_start_phase3():
    """Revert start_phase3.py to Phase 3 configuration"""
    print("🔄 Reverting start_phase3.py...")
    
    revert_changes = [
        ('global_trading = os.getenv(\'GLOBAL_TRADING\', \'true\')', 
         'global_trading = os.getenv(\'GLOBAL_TRADING\', \'false\')'),
        ('trader = Phase3Trader(use_database=True, market_tier=market_tier, global_trading=global_trading)',
         'trader = Phase3Trader(use_database=True, market_tier=market_tier)'),
        ('print(f"🌍 Global Trading: {\'ENABLED\' if global_trading else \'DISABLED\'}")',
         '# Global trading disabled in Phase 3')
    ]
    
    try:
        with open('start_phase3.py', 'r') as f:
            content = f.read()
        
        for old_text, new_text in revert_changes:
            content = content.replace(old_text, new_text)
        
        with open('start_phase3.py', 'w') as f:
            f.write(content)
        
        print("✅ start_phase3.py reverted to Phase 3")
    except Exception as e:
        print(f"❌ Failed to revert start_phase3.py: {e}")

def revert_risk_manager():
    """Revert risk manager to 5-position limit"""
    print("🔄 Reverting risk_manager.py...")
    
    revert_changes = [
        ('self.max_positions = None                 # No limit on concurrent positions',
         'self.max_positions = 5                    # Maximum concurrent positions'),
        ('# Risk Parameters (Phase 4.1: Unlimited positions for aggressive strategy)',
         '# Risk Parameters (Conservative for paper trading)'),
        ('if self.max_positions is not None and len(positions) >= self.max_positions:',
         'if len(positions) >= self.max_positions:'),
        ('f"{len(positions)}/{\'Unlimited\' if self.max_positions is None else self.max_positions}"',
         'f"{len(positions)}/{self.max_positions}"'),
        ('print(f"   Max Positions: {\'Unlimited\' if self.max_positions is None else self.max_positions}")',
         'print(f"   Max Positions: {self.max_positions}")')
    ]
    
    try:
        with open('risk_manager.py', 'r') as f:
            content = f.read()
        
        for old_text, new_text in revert_changes:
            content = content.replace(old_text, new_text)
        
        with open('risk_manager.py', 'w') as f:
            f.write(content)
        
        print("✅ risk_manager.py reverted to 5-position limit")
    except Exception as e:
        print(f"❌ Failed to revert risk_manager.py: {e}")

def revert_requirements():
    """Revert requirements.txt to Phase 3"""
    print("🔄 Reverting requirements.txt...")
    
    try:
        content = """alpaca-trade-api
flask==2.3.3"""
        
        with open('requirements.txt', 'w') as f:
            f.write(content)
        
        print("✅ requirements.txt reverted (removed pytz)")
    except Exception as e:
        print(f"❌ Failed to revert requirements.txt: {e}")

def revert_phase3_trader():
    """Revert phase3_trader.py to remove global trading"""
    print("🔄 Reverting phase3_trader.py...")
    
    revert_changes = [
        ('def __init__(self, use_database=True, market_tier=2, global_trading=False):',
         'def __init__(self, use_database=True, market_tier=2):'),
        ('from global_market_manager import GlobalMarketManager', ''),
        ('# Phase 4.1: Initialize global market manager', ''),
        ('self.global_trading = global_trading', ''),
        ('if self.global_trading:', 'if False:'),  # Disable global trading blocks
    ]
    
    try:
        with open('phase3_trader.py', 'r') as f:
            content = f.read()
        
        for old_text, new_text in revert_changes:
            if old_text:
                content = content.replace(old_text, new_text)
        
        with open('phase3_trader.py', 'w') as f:
            f.write(content)
        
        print("✅ phase3_trader.py reverted to Phase 3")
    except Exception as e:
        print(f"❌ Failed to revert phase3_trader.py: {e}")

def main():
    """Execute emergency revert to Phase 3"""
    print("🚨 EMERGENCY REVERT: Phase 4.1 → Phase 3")
    print("=" * 50)
    print(f"⏰ Revert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create backup first
    backup_dir = create_backup()
    
    # Revert core files
    revert_start_phase3()
    revert_risk_manager()
    revert_requirements()
    revert_phase3_trader()
    
    print("\n✅ REVERT COMPLETE")
    print("=" * 50)
    print("📊 Reverted to Phase 3 Configuration:")
    print("   • Global trading: DISABLED")
    print("   • Max positions: 5 (limited)")
    print("   • Market tier: 2 (default)")
    print("   • Requirements: No pytz dependency")
    print(f"   • Backup saved: {backup_dir}")
    
    print("\n🚀 To restart Phase 3:")
    print("   python3 start_phase3.py")
    
    print("\n⚠️ Railway Environment Variables to Update:")
    print("   GLOBAL_TRADING=false")
    print("   MARKET_TIER=2")

if __name__ == "__main__":
    main()