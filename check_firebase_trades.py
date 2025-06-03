#!/usr/bin/env python3
"""
Firebase Trade Results Checker

Verify that all trades are being tracked properly in Firebase and
analyze trading performance across all modules.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_firebase_connection():
    """Check Firebase connection and available data"""
    try:
        from firebase_database import FirebaseDatabase
        
        logger.info("🔥 Connecting to Firebase...")
        firebase_db = FirebaseDatabase()
        
        if firebase_db.is_connected():
            logger.info("✅ Firebase connected successfully")
            return firebase_db
        else:
            logger.warning("⚠️ Firebase not connected - using mock mode")
            return None
            
    except Exception as e:
        logger.error(f"❌ Firebase connection failed: {e}")
        return None

def analyze_trade_history(firebase_db):
    """Analyze complete trade history from Firebase"""
    if not firebase_db:
        logger.warning("⚠️ No Firebase connection - cannot analyze trades")
        return
    
    try:
        logger.info("📊 Analyzing Firebase trade history...")
        
        # Check trade_history_tracker collection
        trade_tracker_data = firebase_db.get_collection('trade_history_tracker')
        logger.info(f"📋 Trade history tracker entries: {len(trade_tracker_data) if trade_tracker_data else 0}")
        
        # Check trade_history_details collection  
        trade_details_data = firebase_db.get_collection('trade_history_details')
        logger.info(f"📋 Trade detail entries: {len(trade_details_data) if trade_details_data else 0}")
        
        # Check ml_enhanced_trades collection
        ml_trades_data = firebase_db.get_collection('ml_enhanced_trades')
        logger.info(f"📋 ML enhanced trades: {len(ml_trades_data) if ml_trades_data else 0}")
        
        if trade_details_data:
            analyze_trade_performance(trade_details_data)
            
        if ml_trades_data:
            analyze_ml_trade_performance(ml_trades_data)
            
    except Exception as e:
        logger.error(f"❌ Trade history analysis failed: {e}")

def analyze_trade_performance(trade_details: List[Dict]):
    """Analyze trade performance by module and strategy"""
    logger.info("🎯 TRADE PERFORMANCE ANALYSIS")
    logger.info("=" * 50)
    
    # Group trades by module
    module_stats = {}
    strategy_stats = {}
    daily_stats = {}
    
    total_trades = len(trade_details)
    profitable_trades = 0
    total_pnl = 0
    
    for trade in trade_details:
        try:
            # Extract trade info
            symbol = trade.get('symbol', 'UNKNOWN')
            strategy = trade.get('strategy', 'unknown')
            pnl = trade.get('profit_loss', 0)
            timestamp = trade.get('timestamp', datetime.now().isoformat())
            side = trade.get('side', 'unknown')
            
            # Module classification
            if 'USD' in symbol and len(symbol) > 6:
                module = 'crypto'
            elif len(symbol) > 10:  # Options have long symbols
                module = 'options'
            else:
                module = 'stocks'
                
            # Update module stats
            if module not in module_stats:
                module_stats[module] = {'trades': 0, 'profitable': 0, 'total_pnl': 0}
            module_stats[module]['trades'] += 1
            if pnl > 0:
                module_stats[module]['profitable'] += 1
                profitable_trades += 1
            module_stats[module]['total_pnl'] += pnl
            total_pnl += pnl
            
            # Update strategy stats
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {'trades': 0, 'profitable': 0, 'total_pnl': 0}
            strategy_stats[strategy]['trades'] += 1
            if pnl > 0:
                strategy_stats[strategy]['profitable'] += 1
            strategy_stats[strategy]['total_pnl'] += pnl
            
            # Daily stats
            trade_date = timestamp[:10]  # YYYY-MM-DD
            if trade_date not in daily_stats:
                daily_stats[trade_date] = {'trades': 0, 'pnl': 0}
            daily_stats[trade_date]['trades'] += 1
            daily_stats[trade_date]['pnl'] += pnl
            
        except Exception as e:
            logger.warning(f"⚠️ Error processing trade: {e}")
    
    # Print overall stats
    win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
    logger.info(f"📈 OVERALL PERFORMANCE:")
    logger.info(f"   Total Trades: {total_trades}")
    logger.info(f"   Profitable Trades: {profitable_trades}")
    logger.info(f"   Win Rate: {win_rate:.1f}%")
    logger.info(f"   Total P&L: ${total_pnl:.2f}")
    logger.info(f"   Avg P&L per trade: ${total_pnl/total_trades:.2f}" if total_trades > 0 else "   Avg P&L: N/A")
    
    # Print module performance
    logger.info(f"\n📊 MODULE PERFORMANCE:")
    for module, stats in module_stats.items():
        win_rate = (stats['profitable'] / stats['trades'] * 100) if stats['trades'] > 0 else 0
        avg_pnl = stats['total_pnl'] / stats['trades'] if stats['trades'] > 0 else 0
        logger.info(f"   {module.upper()}:")
        logger.info(f"     Trades: {stats['trades']}")
        logger.info(f"     Win Rate: {win_rate:.1f}%")
        logger.info(f"     Total P&L: ${stats['total_pnl']:.2f}")
        logger.info(f"     Avg P&L: ${avg_pnl:.2f}")
    
    # Print strategy performance
    logger.info(f"\n🎯 STRATEGY PERFORMANCE:")
    for strategy, stats in sorted(strategy_stats.items(), key=lambda x: x[1]['total_pnl'], reverse=True):
        if stats['trades'] > 0:
            win_rate = (stats['profitable'] / stats['trades'] * 100)
            avg_pnl = stats['total_pnl'] / stats['trades']
            logger.info(f"   {strategy}:")
            logger.info(f"     Trades: {stats['trades']}, Win Rate: {win_rate:.1f}%, P&L: ${stats['total_pnl']:.2f}")
    
    # Print recent daily performance
    logger.info(f"\n📅 RECENT DAILY PERFORMANCE:")
    sorted_days = sorted(daily_stats.items(), reverse=True)[:7]  # Last 7 days
    for date, stats in sorted_days:
        logger.info(f"   {date}: {stats['trades']} trades, ${stats['pnl']:.2f} P&L")

def analyze_ml_trade_performance(ml_trades: List[Dict]):
    """Analyze ML-enhanced trade performance"""
    logger.info(f"\n🧠 ML TRADE ANALYSIS:")
    logger.info("=" * 30)
    
    if not ml_trades:
        logger.info("   No ML trades found")
        return
    
    # Analyze ML trade outcomes
    ml_profitable = sum(1 for trade in ml_trades if trade.get('profit_loss', 0) > 0)
    ml_total = len(ml_trades)
    ml_win_rate = (ml_profitable / ml_total * 100) if ml_total > 0 else 0
    ml_total_pnl = sum(trade.get('profit_loss', 0) for trade in ml_trades)
    
    logger.info(f"   ML Enhanced Trades: {ml_total}")
    logger.info(f"   ML Win Rate: {ml_win_rate:.1f}%")
    logger.info(f"   ML Total P&L: ${ml_total_pnl:.2f}")
    
    # Analyze ML parameters effectiveness
    confidence_ranges = {'high': 0, 'medium': 0, 'low': 0}
    for trade in ml_trades:
        confidence = trade.get('confidence', 0.5)
        if confidence >= 0.7:
            confidence_ranges['high'] += 1
        elif confidence >= 0.5:
            confidence_ranges['medium'] += 1
        else:
            confidence_ranges['low'] += 1
    
    logger.info(f"   Confidence Distribution:")
    logger.info(f"     High (≥70%): {confidence_ranges['high']} trades")
    logger.info(f"     Medium (50-70%): {confidence_ranges['medium']} trades")
    logger.info(f"     Low (<50%): {confidence_ranges['low']} trades")

def check_current_positions():
    """Check current positions and verify they're being tracked"""
    logger.info("\n💼 CURRENT POSITIONS CHECK:")
    logger.info("=" * 30)
    
    try:
        # This would require Alpaca API credentials
        logger.info("   (Requires Alpaca API connection for position data)")
        
        # For now, indicate what we would check:
        checks_needed = [
            "Active stock positions",
            "Active crypto positions", 
            "Active options positions",
            "Position entry tracking in Firebase",
            "Position exit tracking in Firebase",
            "P&L calculation accuracy"
        ]
        
        for check in checks_needed:
            logger.info(f"   📋 TODO: {check}")
            
    except Exception as e:
        logger.error(f"❌ Position check failed: {e}")

def verify_trade_linking():
    """Verify that entry and exit trades are properly linked"""
    logger.info("\n🔗 TRADE LINKING VERIFICATION:")
    logger.info("=" * 35)
    
    # This would check that:
    # 1. Entry trades have unique trade_ids
    # 2. Exit trades reference the correct entry trade_ids  
    # 3. P&L is calculated correctly from entry to exit
    # 4. No orphaned trades (exits without entries)
    
    logger.info("   📋 TODO: Verify entry-exit trade linking")
    logger.info("   📋 TODO: Check for orphaned exit trades") 
    logger.info("   📋 TODO: Validate P&L calculations")
    logger.info("   📋 TODO: Ensure ML data collection on both entry and exit")

def main():
    """Main execution function"""
    logger.info("🔍 FIREBASE TRADE TRACKING VERIFICATION")
    logger.info("=" * 60)
    logger.info(f"⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check Firebase connection
    firebase_db = check_firebase_connection()
    
    # Analyze trade history
    analyze_trade_history(firebase_db)
    
    # Check current positions  
    check_current_positions()
    
    # Verify trade linking
    verify_trade_linking()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Firebase trade tracking verification complete")
    
    if not firebase_db:
        logger.warning("⚠️ IMPORTANT: Firebase not connected - trade tracking may not be working")
        logger.info("🔧 SOLUTION: Configure Firebase credentials to enable trade tracking")

if __name__ == "__main__":
    main()