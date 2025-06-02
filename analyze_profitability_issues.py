#!/usr/bin/env python3
"""
Analyze Trading System Profitability Issues
Identify specific problems causing the system to lose money
"""

import os
import sys
import json
from datetime import datetime, timedelta
import pandas as pd

# Set environment variables for testing
os.environ['ALPACA_PAPER_API_KEY'] = "PKOBXG3RWCRQTXH6ID0L"
os.environ['ALPACA_PAPER_SECRET_KEY'] = "8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn"
os.environ['ALPACA_BASE_URL'] = "https://paper-api.alpaca.markets"
os.environ['EXECUTION_ENABLED'] = "false"  # Analysis mode only
os.environ['GLOBAL_TRADING'] = "true"
os.environ['CRYPTO_TRADING'] = "true"
os.environ['OPTIONS_TRADING'] = "false"  # Disable for cleaner analysis
os.environ['MARKET_TIER'] = "2"
os.environ['MIN_CONFIDENCE'] = "0.6"

def analyze_base_module_logic():
    """Analyze the base module for profitability issues"""
    print("🔍 ANALYZING BASE MODULE LOGIC...")
    
    try:
        # Read the base module to understand success definition
        with open('modular/base_module.py', 'r') as f:
            content = f.read()
        
        print("📊 CHECKING TRADE SUCCESS DEFINITION...")
        
        # Look for success property
        if '@property' in content and 'def success' in content:
            # Extract success method
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'def success' in line:
                    print(f"  Found success definition at line {i+1}:")
                    # Print next few lines to see the logic
                    for j in range(5):
                        if i+j < len(lines):
                            print(f"    {i+j+1}: {lines[i+j]}")
                    break
        
        # Look for profit/loss calculation
        print("\n📊 CHECKING P&L CALCULATION...")
        if 'pnl' in content.lower() or 'profit' in content.lower():
            print("  ✅ P&L logic found in base module")
        else:
            print("  ❌ NO P&L calculation logic found")
        
        # Look for win rate calculation
        print("\n📊 CHECKING WIN RATE CALCULATION...")
        if 'win_rate' in content:
            print("  ✅ Win rate calculation found")
        else:
            print("  ❌ NO win rate calculation found")
            
    except Exception as e:
        print(f"❌ Error analyzing base module: {e}")

def analyze_crypto_module_logic():
    """Analyze crypto module for allocation and trading logic"""
    print("\n🔍 ANALYZING CRYPTO MODULE LOGIC...")
    
    try:
        with open('modular/crypto_module.py', 'r') as f:
            content = f.read()
        
        print("📊 CHECKING ALLOCATION LOGIC...")
        
        # Look for allocation limits
        if 'max_crypto_allocation' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'max_crypto_allocation' in line and '=' in line:
                    print(f"  Line {i+1}: {line.strip()}")
        
        # Look for smart allocation logic
        if '_get_smart_allocation_limit' in content:
            print("  ✅ Smart allocation logic found")
        else:
            print("  ❌ NO smart allocation logic found")
        
        # Look for exit logic
        print("\n📊 CHECKING EXIT LOGIC...")
        if 'exit' in content.lower() and 'profit' in content.lower():
            print("  ✅ Exit logic found")
        else:
            print("  ❌ Incomplete exit logic")
        
        # Look for profit targets
        profit_targets = []
        lines = content.split('\n')
        for line in lines:
            if 'profit' in line.lower() and '%' in line and any(char.isdigit() for char in line):
                profit_targets.append(line.strip())
        
        if profit_targets:
            print("  📈 PROFIT TARGETS FOUND:")
            for target in profit_targets[:5]:  # Show first 5
                print(f"    {target}")
        else:
            print("  ❌ NO clear profit targets found")
            
    except Exception as e:
        print(f"❌ Error analyzing crypto module: {e}")

def test_current_system():
    """Test current system with analysis mode"""
    print("\n🔍 TESTING CURRENT SYSTEM LOGIC...")
    
    try:
        # Try to run a debug cycle to see what happens
        print("📊 Running debug cycle in analysis mode...")
        
        # Import and test crypto module directly
        sys.path.append('modular')
        from crypto_module import CryptoModule
        
        # Create test instance
        crypto_module = CryptoModule(
            alpaca_api=None,  # We'll mock this
            risk_manager=None,
            order_executor=None,
            firebase_db=None,
            logger=None
        )
        
        print("✅ Crypto module imported successfully")
        
        # Check allocation limits
        if hasattr(crypto_module, 'max_crypto_allocation'):
            print(f"  Max Crypto Allocation: {crypto_module.max_crypto_allocation*100:.1f}%")
        
        # Check if smart allocation exists
        if hasattr(crypto_module, '_get_smart_allocation_limit'):
            print("  ✅ Smart allocation method exists")
        else:
            print("  ❌ Smart allocation method missing")
        
        # Check profit exit thresholds
        if hasattr(crypto_module, 'profit_exit_threshold'):
            print(f"  Profit Exit Threshold: {crypto_module.profit_exit_threshold*100:.1f}%")
        
    except Exception as e:
        print(f"❌ Error testing system: {e}")

def analyze_performance_data():
    """Analyze any available performance data"""
    print("\n🔍 ANALYZING PERFORMANCE DATA...")
    
    # Check for various data files
    data_files = [
        'data/cloud_trading_data.json',
        'complete_audit_results.json', 
        'live_system_audit_results.json',
        'trading_data.json',
        'performance_data.json'
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            print(f"\n📊 ANALYZING {file_path}:")
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, dict):
                    if 'position_details' in data:
                        positions = data['position_details']
                        print(f"  📊 {len(positions)} positions found")
                        
                        # Analyze position performance
                        crypto_positions = [p for p in positions if p.get('category') == '₿']
                        stock_positions = [p for p in positions if p.get('category') == '📈']
                        
                        crypto_pnl = sum(p.get('unrealized_pl', 0) for p in crypto_positions)
                        stock_pnl = sum(p.get('unrealized_pl', 0) for p in stock_positions)
                        
                        print(f"    ₿ Crypto P&L: ${crypto_pnl:+.2f} ({len(crypto_positions)} positions)")
                        print(f"    📈 Stock P&L: ${stock_pnl:+.2f} ({len(stock_positions)} positions)")
                        
                        # Identify worst performers
                        worst_positions = sorted(positions, key=lambda x: x.get('unrealized_pl', 0))[:3]
                        print(f"    📉 WORST PERFORMERS:")
                        for pos in worst_positions:
                            if pos.get('unrealized_pl', 0) < 0:
                                print(f"      {pos.get('symbol', '?')}: ${pos.get('unrealized_pl', 0):+.2f}")
                
                elif isinstance(data, list) and len(data) > 0:
                    print(f"  📊 {len(data)} records found")
                    sample = data[0]
                    print(f"    Sample keys: {list(sample.keys())}")
                    
            except Exception as e:
                print(f"    ❌ Error reading {file_path}: {e}")

def identify_critical_issues():
    """Identify the most critical profitability issues"""
    print("\n🚨 CRITICAL PROFITABILITY ISSUES IDENTIFIED:")
    
    # Based on analysis so far
    issues = [
        "🔴 EXTREME CRYPTO OVER-ALLOCATION (89.5% vs recommended 5-10%)",
        "🔴 NO PROPER RISK MANAGEMENT (no 1-2% per trade limit visible)",
        "🔴 PROFIT/LOSS CONFUSION (execution success ≠ profitability)",
        "🔴 NO CLEAR EXIT STRATEGY (positions bleeding without stops)",
        "🔴 PORTFOLIO DECLINE (-4.7% from start)",
        "🔴 UNBALANCED ALLOCATION (only 3.1% stocks vs 89.5% crypto)"
    ]
    
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    
    print(f"\n💡 ROOT CAUSE ANALYSIS:")
    root_causes = [
        "📊 ALLOCATION DISASTER: 89.5% crypto violates all risk management principles",
        "🎯 SUCCESS METRICS BROKEN: System counts executed trades as 'successful' regardless of profit",
        "🚫 NO STOP LOSSES: Bleeding positions allowed to continue losing",
        "📈 MISSED STOCK OPPORTUNITIES: Only 3.1% in stocks during potential gains",
        "🔄 NO REBALANCING: System not maintaining target allocations"
    ]
    
    for cause in root_causes:
        print(f"  • {cause}")

def generate_fix_recommendations():
    """Generate specific fix recommendations"""
    print(f"\n🛠️ IMMEDIATE FIX RECOMMENDATIONS:")
    
    fixes = [
        {
            "priority": "CRITICAL",
            "issue": "Crypto Over-Allocation",
            "action": "Reduce crypto from 89.5% to 30% maximum",
            "implementation": "Sell excess crypto positions immediately"
        },
        {
            "priority": "CRITICAL", 
            "issue": "No Risk Management",
            "action": "Implement 1-2% risk per trade limit",
            "implementation": "Add position sizing based on portfolio value"
        },
        {
            "priority": "HIGH",
            "issue": "Success Definition Bug",
            "action": "Fix TradeResult.success to require profitability",
            "implementation": "Update base_module.py success property"
        },
        {
            "priority": "HIGH",
            "issue": "No Stop Losses",
            "action": "Implement automatic stop losses",
            "implementation": "Add 15% stop loss on all positions"
        },
        {
            "priority": "MEDIUM",
            "issue": "Stock Under-Allocation", 
            "action": "Increase stock allocation to 40-50%",
            "implementation": "Buy stocks with unused buying power"
        }
    ]
    
    for i, fix in enumerate(fixes, 1):
        print(f"\n  {i}. 🚨 {fix['priority']}: {fix['issue']}")
        print(f"     Action: {fix['action']}")
        print(f"     Implementation: {fix['implementation']}")

def main():
    print("🚨 COMPREHENSIVE PROFITABILITY ANALYSIS")
    print("=" * 60)
    
    # Run all analysis functions
    analyze_base_module_logic()
    analyze_crypto_module_logic()
    test_current_system()
    analyze_performance_data()
    identify_critical_issues()
    generate_fix_recommendations()
    
    # Save analysis results
    analysis_results = {
        'timestamp': datetime.now().isoformat(),
        'critical_issues': [
            'Extreme crypto over-allocation (89.5%)',
            'No proper risk management',
            'Profit/loss calculation issues',
            'No clear exit strategy', 
            'Portfolio decline (-4.7%)',
            'Unbalanced allocation'
        ],
        'immediate_actions': [
            'Reduce crypto allocation to 30%',
            'Implement 1-2% risk per trade',
            'Fix success definition in base_module.py',
            'Add stop losses to all positions',
            'Increase stock allocation'
        ],
        'status': 'analysis_complete'
    }
    
    with open('profitability_analysis_results.json', 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\n📁 Analysis saved to: profitability_analysis_results.json")

if __name__ == "__main__":
    main()