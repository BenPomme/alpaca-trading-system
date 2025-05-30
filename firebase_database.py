#!/usr/bin/env python3
"""
Firebase Database Integration for Alpaca Trading System
Provides persistent cloud database storage replacing ephemeral SQLite
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

class FirebaseDatabase:
    """Firebase Firestore integration for persistent trading data storage"""
    
    def __init__(self):
        self.db = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            print("🔥 FIREBASE INIT: Starting Firebase initialization...")
            
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                self.db = firestore.client()
                print("✅ FIREBASE INIT: Firebase already initialized")
                return
            
            # Initialize with service account key
            service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
            
            if os.path.exists(service_account_path):
                # Use service account file
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                print(f"✅ Firebase initialized with service account: {service_account_path}")
            else:
                # Use environment variables for Railway deployment
                print("🔥 FIREBASE INIT: Attempting environment variable initialization...")
                firebase_config = {
                    "type": "service_account",
                    "project_id": "alpaca-12fab",
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                    "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
                }
                
                # Debug: Check which variables are present
                env_vars = ['FIREBASE_PRIVATE_KEY_ID', 'FIREBASE_PRIVATE_KEY', 'FIREBASE_CLIENT_EMAIL', 'FIREBASE_CLIENT_ID', 'FIREBASE_CLIENT_CERT_URL']
                missing_vars = [var for var in env_vars if not os.getenv(var)]
                if missing_vars:
                    print(f"❌ FIREBASE INIT: Missing environment variables: {missing_vars}")
                else:
                    print("✅ FIREBASE INIT: All environment variables present")
                
                if all(firebase_config.values()):
                    cred = credentials.Certificate(firebase_config)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase initialized with environment variables")
                else:
                    print("⚠️ Firebase credentials not found - using mock mode")
                    return
            
            self.db = firestore.client()
            
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            self.db = None
    
    def is_connected(self) -> bool:
        """Check if Firebase connection is active"""
        return self.db is not None
    
    # TRADING CYCLES COLLECTION
    def save_trading_cycle(self, cycle_data: Dict[str, Any]) -> str:
        """Save trading cycle analysis to Firebase"""
        try:
            if not self.is_connected():
                return "mock_id"
            
            cycle_data['timestamp'] = datetime.now()
            cycle_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.db.collection('trading_cycles').add(cycle_data)
            cycle_id = doc_ref[1].id
            
            print(f"✅ Trading cycle saved to Firebase: {cycle_id}")
            return cycle_id
            
        except Exception as e:
            print(f"❌ Error saving trading cycle: {e}")
            return "error_id"
    
    def get_recent_trading_cycles(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trading cycles from Firebase"""
        try:
            if not self.is_connected():
                return []
            
            cycles_ref = self.db.collection('trading_cycles')
            query = cycles_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            cycles = []
            for doc in docs:
                cycle_data = doc.to_dict()
                cycle_data['id'] = doc.id
                cycles.append(cycle_data)
            
            return cycles
            
        except Exception as e:
            print(f"❌ Error getting trading cycles: {e}")
            return []
    
    # TRADES COLLECTION
    def save_trade(self, trade_data: Dict[str, Any]) -> str:
        """Save trade execution to Firebase"""
        try:
            if not self.is_connected():
                return "mock_trade_id"
            
            trade_data['timestamp'] = datetime.now()
            trade_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.db.collection('trades').add(trade_data)
            trade_id = doc_ref[1].id
            
            print(f"✅ Trade saved to Firebase: {trade_data['symbol']} - {trade_id}")
            return trade_id
            
        except Exception as e:
            print(f"❌ Error saving trade: {e}")
            return "error_trade_id"
    
    def get_trades(self, limit: int = 500, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get recent trades from Firebase"""
        try:
            if not self.is_connected():
                return []
            
            # Calculate date filter
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            trades_ref = self.db.collection('trades')
            query = trades_ref.where(filter=FieldFilter('timestamp', '>=', cutoff_date)) \
                             .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                             .limit(limit)
            docs = query.stream()
            
            trades = []
            for doc in docs:
                trade_data = doc.to_dict()
                trade_data['id'] = doc.id
                trades.append(trade_data)
            
            return trades
            
        except Exception as e:
            print(f"❌ Error getting trades: {e}")
            return []
    
    def get_trades_by_symbol(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get trades for a specific symbol"""
        try:
            if not self.is_connected():
                return []
            
            trades_ref = self.db.collection('trades')
            query = trades_ref.where(filter=FieldFilter('symbol', '==', symbol)) \
                             .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                             .limit(limit)
            docs = query.stream()
            
            trades = []
            for doc in docs:
                trade_data = doc.to_dict()
                trade_data['id'] = doc.id
                trades.append(trade_data)
            
            return trades
            
        except Exception as e:
            print(f"❌ Error getting trades for {symbol}: {e}")
            return []
    
    # MARKET QUOTES COLLECTION
    def save_market_quote(self, quote_data: Dict[str, Any]) -> str:
        """Save market quote data to Firebase"""
        try:
            if not self.is_connected():
                return "mock_quote_id"
            
            quote_data['timestamp'] = datetime.now()
            quote_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.db.collection('market_quotes').add(quote_data)
            quote_id = doc_ref[1].id
            
            return quote_id
            
        except Exception as e:
            print(f"❌ Error saving market quote: {e}")
            return "error_quote_id"
    
    def get_latest_quotes(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """Get latest market quotes from Firebase"""
        try:
            if not self.is_connected():
                return []
            
            quotes_ref = self.db.collection('market_quotes')
            
            if symbols:
                # Get quotes for specific symbols
                quotes = []
                for symbol in symbols:
                    query = quotes_ref.where(filter=FieldFilter('symbol', '==', symbol)) \
                                     .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                                     .limit(1)
                    docs = query.stream()
                    for doc in docs:
                        quote_data = doc.to_dict()
                        quote_data['id'] = doc.id
                        quotes.append(quote_data)
                return quotes
            else:
                # Get recent quotes for all symbols
                query = quotes_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(100)
                docs = query.stream()
                
                quotes = []
                for doc in docs:
                    quote_data = doc.to_dict()
                    quote_data['id'] = doc.id
                    quotes.append(quote_data)
                
                return quotes
            
        except Exception as e:
            print(f"❌ Error getting market quotes: {e}")
            return []
    
    # ML MODELS COLLECTION
    def save_ml_model_state(self, model_name: str, model_data: Dict[str, Any]) -> str:
        """Save ML model state for persistence across deployments"""
        try:
            if not self.is_connected():
                return "mock_model_id"
            
            model_data['model_name'] = model_name
            model_data['timestamp'] = datetime.now()
            model_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            # Use model name as document ID for easy retrieval
            doc_ref = self.db.collection('ml_models').document(model_name)
            doc_ref.set(model_data)
            
            print(f"✅ ML model state saved: {model_name}")
            return model_name
            
        except Exception as e:
            print(f"❌ Error saving ML model state: {e}")
            return "error_model_id"
    
    def get_ml_model_state(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get ML model state from Firebase"""
        try:
            if not self.is_connected():
                return None
            
            doc_ref = self.db.collection('ml_models').document(model_name)
            doc = doc_ref.get()
            
            if doc.exists:
                model_data = doc.to_dict()
                return model_data
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error getting ML model state for {model_name}: {e}")
            return None
    
    def get_all_ml_models(self) -> List[Dict[str, Any]]:
        """Get all ML model states"""
        try:
            if not self.is_connected():
                return []
            
            models_ref = self.db.collection('ml_models')
            docs = models_ref.stream()
            
            models = []
            for doc in docs:
                model_data = doc.to_dict()
                model_data['id'] = doc.id
                models.append(model_data)
            
            return models
            
        except Exception as e:
            print(f"❌ Error getting ML models: {e}")
            return []
    
    # POSITIONS COLLECTION
    def save_positions(self, positions_data: List[Dict[str, Any]]) -> str:
        """Save current positions to Firebase for real-time dashboard updates"""
        try:
            if not self.is_connected():
                return "mock_positions_id"
            
            # Clear existing positions and save new ones
            positions_ref = self.db.collection('positions')
            
            # Delete old positions
            old_positions = positions_ref.stream()
            for doc in old_positions:
                doc.reference.delete()
            
            # Save new positions
            batch = self.db.batch()
            position_ids = []
            
            for i, position in enumerate(positions_data):
                position['timestamp'] = datetime.now()
                position['created_at'] = firestore.SERVER_TIMESTAMP
                position['id'] = f"pos_{i}_{int(datetime.now().timestamp())}"
                
                doc_ref = positions_ref.document(position['id'])
                batch.set(doc_ref, position)
                position_ids.append(position['id'])
            
            batch.commit()
            
            print(f"🔥 {len(positions_data)} positions saved to Firebase")
            return f"batch_{len(positions_data)}_positions"
            
        except Exception as e:
            print(f"❌ Error saving positions: {e}")
            return "error_positions_id"
    
    def get_current_positions(self) -> List[Dict[str, Any]]:
        """Get current positions from Firebase"""
        try:
            if not self.is_connected():
                return []
            
            positions_ref = self.db.collection('positions')
            query = positions_ref.order_by('timestamp', direction=firestore.Query.DESCENDING)
            docs = query.stream()
            
            positions = []
            for doc in docs:
                position_data = doc.to_dict()
                position_data['id'] = doc.id
                positions.append(position_data)
            
            return positions
            
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return []

    # PERFORMANCE METRICS COLLECTION
    def save_performance_metrics(self, metrics_data: Dict[str, Any]) -> str:
        """Save performance metrics to Firebase"""
        try:
            if not self.is_connected():
                return "mock_metrics_id"
            
            metrics_data['timestamp'] = datetime.now()
            metrics_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.db.collection('performance_metrics').add(metrics_data)
            metrics_id = doc_ref[1].id
            
            return metrics_id
            
        except Exception as e:
            print(f"❌ Error saving performance metrics: {e}")
            return "error_metrics_id"
    
    def get_performance_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get performance metrics history"""
        try:
            if not self.is_connected():
                return []
            
            metrics_ref = self.db.collection('performance_metrics')
            query = metrics_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            metrics = []
            for doc in docs:
                metric_data = doc.to_dict()
                metric_data['id'] = doc.id
                metrics.append(metric_data)
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error getting performance history: {e}")
            return []
    
    # UTILITY METHODS
    def get_database_stats(self) -> Dict[str, Any]:
        """Get Firebase database statistics"""
        try:
            if not self.is_connected():
                return {"status": "disconnected"}
            
            collections = ['trading_cycles', 'trades', 'market_quotes', 'ml_models', 'performance_metrics']
            stats = {"status": "connected", "collections": {}}
            
            for collection_name in collections:
                try:
                    collection_ref = self.db.collection(collection_name)
                    # Count documents (limited to 1000 for performance)
                    docs = collection_ref.limit(1000).stream()
                    count = len(list(docs))
                    stats["collections"][collection_name] = count
                except Exception as e:
                    stats["collections"][collection_name] = f"Error: {e}"
            
            return stats
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def clear_old_data(self, days_to_keep: int = 90):
        """Clear old data from Firebase (for maintenance)"""
        try:
            if not self.is_connected():
                print("⚠️ Firebase not connected - cannot clear old data")
                return
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            collections_to_clean = ['trading_cycles', 'market_quotes', 'performance_metrics']
            
            for collection_name in collections_to_clean:
                collection_ref = self.db.collection(collection_name)
                query = collection_ref.where(filter=FieldFilter('timestamp', '<', cutoff_date))
                docs = query.stream()
                
                deleted_count = 0
                for doc in docs:
                    doc.reference.delete()
                    deleted_count += 1
                
                print(f"🗑️ Deleted {deleted_count} old documents from {collection_name}")
            
        except Exception as e:
            print(f"❌ Error clearing old data: {e}")

def main():
    """Test Firebase database connection and basic operations"""
    print("🔥 Testing Firebase Database Integration")
    print("=" * 50)
    
    db = FirebaseDatabase()
    
    # Test connection
    if db.is_connected():
        print("✅ Firebase connection successful")
        
        # Test database stats
        stats = db.get_database_stats()
        print(f"📊 Database stats: {stats}")
        
        # Test saving a sample trading cycle
        sample_cycle = {
            "analysis_type": "test",
            "confidence": 0.75,
            "strategy": "momentum",
            "symbols_analyzed": ["AAPL", "MSFT"],
            "market_regime": "bull"
        }
        
        cycle_id = db.save_trading_cycle(sample_cycle)
        print(f"✅ Test trading cycle saved: {cycle_id}")
        
        # Test retrieving recent cycles
        recent_cycles = db.get_recent_trading_cycles(limit=5)
        print(f"📊 Recent cycles retrieved: {len(recent_cycles)}")
        
    else:
        print("❌ Firebase connection failed")

if __name__ == "__main__":
    main()