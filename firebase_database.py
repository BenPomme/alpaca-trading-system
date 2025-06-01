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
    
    # TRADES COLLECTION (Enhanced for ML Optimization)
    def save_trade_opportunity(self, opportunity_data: Dict[str, Any]) -> str:
        """Save a trading opportunity to Firebase"""
        try:
            if not self.db:
                return ""
            
            # Add timestamp and metadata
            opportunity_doc = {
                **opportunity_data,
                'timestamp': datetime.now(),
                'type': 'trade_opportunity',
                'created_at': datetime.now().isoformat()
            }
            
            # Save to opportunities collection
            doc_ref = self.db.collection('opportunities').add(opportunity_doc)
            doc_id = doc_ref[1].id
            
            logging.info(f"✅ Saved trade opportunity to Firebase: {doc_id}")
            return doc_id
            
        except Exception as e:
            logging.error(f"❌ Error saving trade opportunity to Firebase: {e}")
            return ""

    def save_trade_result(self, result_data: Dict[str, Any]) -> str:
        """Save a trade execution result to Firebase"""
        try:
            if not self.db:
                return ""
            
            # Add timestamp and metadata
            result_doc = {
                **result_data,
                'timestamp': datetime.now(),
                'type': 'trade_result',
                'created_at': datetime.now().isoformat()
            }
            
            # Save to trade_results collection
            doc_ref = self.db.collection('trade_results').add(result_doc)
            doc_id = doc_ref[1].id
            
            logging.info(f"✅ Saved trade result to Firebase: {doc_id}")
            return doc_id
            
        except Exception as e:
            logging.error(f"❌ Error saving trade result to Firebase: {e}")
            return ""

    def save_trade(self, trade_data: Dict[str, Any]) -> str:
        """Save trade execution to Firebase with ML-critical parameter data"""
        try:
            if not self.is_connected():
                return "mock_trade_id"
            
            # Validate and enhance trade data for ML optimization
            enhanced_trade_data = self._enhance_trade_data_for_ml(trade_data)
            
            enhanced_trade_data['timestamp'] = datetime.now()
            enhanced_trade_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.db.collection('trades').add(enhanced_trade_data)
            trade_id = doc_ref[1].id
            
            print(f"✅ Enhanced trade saved to Firebase: {trade_data['symbol']} - {trade_id}")
            return trade_id
            
        except Exception as e:
            print(f"❌ Error saving trade: {e}")
            return "error_trade_id"
    
    def _enhance_trade_data_for_ml(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance trade data with ML-critical fields and validation"""
        enhanced_data = trade_data.copy()
        
        # Ensure required ML fields exist with defaults
        if 'entry_parameters' not in enhanced_data:
            enhanced_data['entry_parameters'] = {}
        
        if 'module_specific_params' not in enhanced_data:
            enhanced_data['module_specific_params'] = {}
            
        if 'exit_analysis' not in enhanced_data:
            enhanced_data['exit_analysis'] = {}
            
        if 'market_context' not in enhanced_data:
            enhanced_data['market_context'] = {}
            
        if 'parameter_performance' not in enhanced_data:
            enhanced_data['parameter_performance'] = {}
        
        # Add ML tracking metadata
        enhanced_data['ml_data_version'] = "1.0"
        enhanced_data['ml_enhanced'] = True
        
        return enhanced_data
    
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
    
    # ORCHESTRATOR CYCLE COLLECTION
    def save_orchestrator_cycle(self, cycle_data: Dict[str, Any]) -> str:
        """Save orchestrator cycle data to Firebase"""
        try:
            if not self.is_connected():
                return "mock_orchestrator_cycle_id"
            
            cycle_data['timestamp'] = datetime.now()
            cycle_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.db.collection('orchestrator_cycles').add(cycle_data)
            cycle_id = doc_ref[1].id
            
            return cycle_id
            
        except Exception as e:
            print(f"❌ Error saving orchestrator cycle: {e}")
            return "error_orchestrator_cycle_id"
    
    def save_orchestrator_shutdown(self, shutdown_data: Dict[str, Any]) -> str:
        """Save orchestrator shutdown data to Firebase"""
        try:
            if not self.is_connected():
                return "mock_shutdown_id"
            
            shutdown_data['timestamp'] = datetime.now()
            shutdown_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.db.collection('orchestrator_shutdowns').add(shutdown_data)
            shutdown_id = doc_ref[1].id
            
            return shutdown_id
            
        except Exception as e:
            print(f"❌ Error saving orchestrator shutdown: {e}")
            return "error_shutdown_id"

    # UTILITY METHODS
    def get_database_stats(self) -> Dict[str, Any]:
        """Get Firebase database statistics"""
        try:
            if not self.is_connected():
                return {"status": "disconnected"}
            
            collections = ['trading_cycles', 'trades', 'market_quotes', 'ml_models', 'performance_metrics', 
                          'parameter_effectiveness', 'ml_learning_events', 'ml_optimization_data']
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
    
    # ML OPTIMIZATION COLLECTIONS
    def save_parameter_effectiveness(self, param_data: Dict[str, Any]) -> str:
        """Save parameter effectiveness data for ML optimization"""
        try:
            if not self.is_connected():
                return "mock_param_id"
            
            param_data['timestamp'] = datetime.now()
            param_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            # Use parameter type and value as document ID for easy retrieval
            doc_id = f"{param_data['module_name']}_{param_data['parameter_type']}_{param_data['parameter_value']}"
            doc_ref = self.db.collection('parameter_effectiveness').document(doc_id)
            doc_ref.set(param_data)
            
            return doc_id
            
        except Exception as e:
            print(f"❌ Error saving parameter effectiveness: {e}")
            return "error_param_id"
    
    def get_parameter_effectiveness(self, module_name: str = None, parameter_type: str = None) -> List[Dict[str, Any]]:
        """Get parameter effectiveness data for analysis"""
        try:
            if not self.is_connected():
                return []
            
            params_ref = self.db.collection('parameter_effectiveness')
            
            # Apply filters if provided
            query = params_ref
            if module_name:
                query = query.where(filter=FieldFilter('module_name', '==', module_name))
            if parameter_type:
                query = query.where(filter=FieldFilter('parameter_type', '==', parameter_type))
            
            query = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(100)
            docs = query.stream()
            
            params = []
            for doc in docs:
                param_data = doc.to_dict()
                param_data['id'] = doc.id
                params.append(param_data)
            
            return params
            
        except Exception as e:
            print(f"❌ Error getting parameter effectiveness: {e}")
            return []
    
    def save_ml_learning_event(self, event_data: Dict[str, Any]) -> str:
        """Save ML learning event for audit trail"""
        try:
            if not self.is_connected():
                return "mock_event_id"
            
            event_data['timestamp'] = datetime.now()
            event_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.db.collection('ml_learning_events').add(event_data)
            event_id = doc_ref[1].id
            
            return event_id
            
        except Exception as e:
            print(f"❌ Error saving ML learning event: {e}")
            return "error_event_id"
    
    def get_ml_learning_events(self, model_name: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get ML learning events for analysis"""
        try:
            if not self.is_connected():
                return []
            
            events_ref = self.db.collection('ml_learning_events')
            
            query = events_ref
            if model_name:
                query = query.where(filter=FieldFilter('model_name', '==', model_name))
            
            query = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            events = []
            for doc in docs:
                event_data = doc.to_dict()
                event_data['id'] = doc.id
                events.append(event_data)
            
            return events
            
        except Exception as e:
            print(f"❌ Error getting ML learning events: {e}")
            return []
    
    def save_ml_optimization_data(self, module_name: str, optimization_data: Dict[str, Any]) -> str:
        """Save ML optimization data for a module"""
        try:
            if not self.is_connected():
                return "mock_optimization_id"
            
            optimization_data['module_name'] = module_name
            optimization_data['timestamp'] = datetime.now()
            optimization_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            # Use module name as document ID
            doc_ref = self.db.collection('ml_optimization_data').document(module_name)
            doc_ref.set(optimization_data)
            
            print(f"✅ ML optimization data saved for {module_name}")
            return module_name
            
        except Exception as e:
            print(f"❌ Error saving ML optimization data: {e}")
            return "error_optimization_id"
    
    def get_ml_optimization_data(self, module_name: str = None) -> List[Dict[str, Any]]:
        """Get ML optimization data"""
        try:
            if not self.is_connected():
                return []
            
            if module_name:
                # Get specific module optimization data
                doc_ref = self.db.collection('ml_optimization_data').document(module_name)
                doc = doc_ref.get()
                
                if doc.exists:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    return [data]
                else:
                    return []
            else:
                # Get all optimization data
                docs = self.db.collection('ml_optimization_data').stream()
                
                optimization_data = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    optimization_data.append(data)
                
                return optimization_data
            
        except Exception as e:
            print(f"❌ Error getting ML optimization data: {e}")
            return []
    
    def get_trades_for_ml_analysis(self, module_name: str = None, days_back: int = 30, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get trades with ML-enhanced data for parameter analysis"""
        try:
            if not self.is_connected():
                return []
            
            # Calculate date filter
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            trades_ref = self.db.collection('trades')
            query = trades_ref.where(filter=FieldFilter('timestamp', '>=', cutoff_date)) \
                             .where(filter=FieldFilter('ml_enhanced', '==', True))
            
            if module_name:
                # Filter by module (inferred from strategy or asset_type)
                if module_name == 'crypto':
                    query = query.where(filter=FieldFilter('asset_type', '==', 'crypto'))
                elif module_name == 'options':
                    query = query.where(filter=FieldFilter('options_trade', '==', True))
                elif module_name == 'stocks':
                    query = query.where(filter=FieldFilter('asset_type', '==', 'stock'))
            
            query = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            trades = []
            for doc in docs:
                trade_data = doc.to_dict()
                trade_data['id'] = doc.id
                trades.append(trade_data)
            
            return trades
            
        except Exception as e:
            print(f"❌ Error getting ML trades: {e}")
            return []

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