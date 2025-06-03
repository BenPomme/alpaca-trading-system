#!/usr/bin/env python3
"""
Enhanced ML Models - PyTorch Integration
Advanced machine learning models for algorithmic trading
Maintains compatibility with existing scikit-learn models
Preserves Firebase + Railway deployment compatibility
"""

import numpy as np
import pandas as pd
import logging
import pickle
import json
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timezone
import warnings

# Core ML libraries
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error

# Advanced ML with PyTorch
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    PYTORCH_AVAILABLE = True
except ImportError:
    print("⚠️ PyTorch not available - install with: pip install torch")
    PYTORCH_AVAILABLE = False
    # Create dummy classes for import compatibility
    class nn:
        class Module:
            def __init__(self): pass
        class LSTM:
            def __init__(self, *args, **kwargs): pass
        class MultiheadAttention:
            def __init__(self, *args, **kwargs): pass
        class Sequential:
            def __init__(self, *args): pass
        class Linear:
            def __init__(self, *args, **kwargs): pass
        class ReLU:
            def __init__(self): pass
        class Dropout:
            def __init__(self, *args): pass
        class Softmax:
            def __init__(self, *args, **kwargs): pass
        class TransformerEncoderLayer:
            def __init__(self, *args, **kwargs): pass
        class TransformerEncoder:
            def __init__(self, *args, **kwargs): pass
        class CrossEntropyLoss:
            def __init__(self): pass
    
    class optim:
        class Adam:
            def __init__(self, *args, **kwargs): pass
        class AdamW:
            def __init__(self, *args, **kwargs): pass
    
    class torch:
        @staticmethod
        def FloatTensor(*args): return None
        @staticmethod
        def LongTensor(*args): return None
        @staticmethod
        def device(*args): return None
        @staticmethod
        def cuda(): 
            class cuda:
                @staticmethod
                def is_available(): return False
            return cuda()
        @staticmethod
        def backends():
            class backends:
                class mps:
                    @staticmethod
                    def is_available(): return False
            return backends()
        @staticmethod
        def max(*args): return None, None
        @staticmethod
        def mean(*args): return None
        @staticmethod
        def save(*args): pass

# Performance optimization
try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class TradingLSTM(nn.Module):
    """
    LSTM Neural Network for time series prediction in trading
    Designed for price movement and volatility prediction
    """
    
    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 2, 
                 output_size: int = 3, dropout: float = 0.2):
        super(TradingLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=8,
            dropout=dropout,
            batch_first=True
        )
        
        # Classification layers
        self.fc_layers = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 4, output_size)
        )
        
        # Softmax for classification (Buy/Hold/Sell)
        self.softmax = nn.Softmax(dim=1)
    
    def forward(self, x):
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Apply attention to the last sequence output
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Use the last time step
        final_output = attn_out[:, -1, :]
        
        # Classification
        output = self.fc_layers(final_output)
        return self.softmax(output)


class TradingTransformer(nn.Module):
    """
    Transformer model for trading signals
    State-of-the-art architecture for sequence modeling
    """
    
    def __init__(self, input_size: int, d_model: int = 128, nhead: int = 8, 
                 num_layers: int = 3, output_size: int = 3, dropout: float = 0.1):
        super(TradingTransformer, self).__init__()
        
        # Input projection
        self.input_projection = nn.Linear(input_size, d_model)
        
        # Positional encoding
        self.positional_encoding = PositionalEncoding(d_model, dropout)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Output layers
        self.output_layers = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, output_size)
        )
        
        self.softmax = nn.Softmax(dim=1)
    
    def forward(self, x):
        # Project input to model dimension
        x = self.input_projection(x)
        
        # Add positional encoding
        x = self.positional_encoding(x)
        
        # Transformer encoding
        encoded = self.transformer(x)
        
        # Global average pooling
        pooled = torch.mean(encoded, dim=1)
        
        # Output prediction
        output = self.output_layers(pooled)
        return self.softmax(output)


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer models"""
    
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)


class EnhancedMLFramework:
    """
    Enhanced ML framework combining traditional ML with deep learning
    Maintains backward compatibility with existing scikit-learn models
    """
    
    def __init__(self, logger: logging.Logger = None, device: str = None):
        self.logger = logger or logging.getLogger(__name__)
        self.pytorch_available = PYTORCH_AVAILABLE
        
        # Device selection for PyTorch
        if self.pytorch_available:
            if device is None:
                self.device = torch.device('cuda' if torch.cuda.is_available() else 
                                         'mps' if torch.backends.mps.is_available() else 'cpu')
            else:
                self.device = torch.device(device)
            self.logger.info(f"🔥 PyTorch device: {self.device}")
        
        # Model storage
        self.models = {}
        self.scalers = {}
        self.model_metadata = {}
        
        # Training history
        self.training_history = {}
        
        self.logger.info("✅ Enhanced ML Framework initialized")
    
    def create_lstm_model(self, input_size: int, sequence_length: int = 20, 
                         hidden_size: int = 128, num_layers: int = 2) -> str:
        """
        Create and register an LSTM model for trading predictions
        Returns model_id for future reference
        """
        if not self.pytorch_available:
            self.logger.error("❌ PyTorch not available for LSTM model")
            return None
        
        model_id = f"lstm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            model = TradingLSTM(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                output_size=3  # Buy/Hold/Sell
            ).to(self.device)
            
            self.models[model_id] = {
                'model': model,
                'type': 'lstm',
                'optimizer': optim.Adam(model.parameters(), lr=0.001),
                'criterion': nn.CrossEntropyLoss(),
                'sequence_length': sequence_length
            }
            
            self.model_metadata[model_id] = {
                'created': datetime.now(timezone.utc),
                'input_size': input_size,
                'hidden_size': hidden_size,
                'num_layers': num_layers,
                'type': 'lstm'
            }
            
            self.logger.info(f"✅ LSTM model created: {model_id}")
            return model_id
            
        except Exception as e:
            self.logger.error(f"❌ LSTM model creation failed: {e}")
            return None
    
    def create_transformer_model(self, input_size: int, sequence_length: int = 20,
                               d_model: int = 128, nhead: int = 8) -> str:
        """
        Create and register a Transformer model for trading predictions
        """
        if not self.pytorch_available:
            self.logger.error("❌ PyTorch not available for Transformer model")
            return None
        
        model_id = f"transformer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            model = TradingTransformer(
                input_size=input_size,
                d_model=d_model,
                nhead=nhead,
                num_layers=3,
                output_size=3
            ).to(self.device)
            
            self.models[model_id] = {
                'model': model,
                'type': 'transformer',
                'optimizer': optim.AdamW(model.parameters(), lr=0.0001, weight_decay=0.01),
                'criterion': nn.CrossEntropyLoss(),
                'sequence_length': sequence_length
            }
            
            self.model_metadata[model_id] = {
                'created': datetime.now(timezone.utc),
                'input_size': input_size,
                'd_model': d_model,
                'nhead': nhead,
                'type': 'transformer'
            }
            
            self.logger.info(f"✅ Transformer model created: {model_id}")
            return model_id
            
        except Exception as e:
            self.logger.error(f"❌ Transformer model creation failed: {e}")
            return None
    
    def create_traditional_model(self, model_type: str = 'random_forest') -> str:
        """
        Create traditional ML model (scikit-learn) for backward compatibility
        """
        model_id = f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            if model_type == 'random_forest':
                model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42
                )
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            self.models[model_id] = {
                'model': model,
                'type': model_type,
                'scaler': StandardScaler()
            }
            
            self.model_metadata[model_id] = {
                'created': datetime.now(timezone.utc),
                'type': model_type,
                'framework': 'sklearn'
            }
            
            self.logger.info(f"✅ Traditional model created: {model_id}")
            return model_id
            
        except Exception as e:
            self.logger.error(f"❌ Traditional model creation failed: {e}")
            return None
    
    def prepare_data_for_pytorch(self, features: np.ndarray, labels: np.ndarray, 
                               sequence_length: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Prepare data for PyTorch models (LSTM/Transformer)
        Creates sequences from time series data
        """
        if len(features) < sequence_length:
            raise ValueError(f"Not enough data for sequence length {sequence_length}")
        
        # Create sequences
        X_sequences = []
        y_sequences = []
        
        for i in range(len(features) - sequence_length + 1):
            X_sequences.append(features[i:i + sequence_length])
            y_sequences.append(labels[i + sequence_length - 1])
        
        X_tensor = torch.FloatTensor(np.array(X_sequences)).to(self.device)
        y_tensor = torch.LongTensor(np.array(y_sequences)).to(self.device)
        
        return X_tensor, y_tensor
    
    def train_model(self, model_id: str, features: np.ndarray, labels: np.ndarray,
                   epochs: int = 100, batch_size: int = 32, validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Train a model (PyTorch or traditional)
        """
        if model_id not in self.models:
            self.logger.error(f"❌ Model {model_id} not found")
            return None
        
        model_info = self.models[model_id]
        model_type = model_info['type']
        
        try:
            if model_type in ['lstm', 'transformer']:
                return self._train_pytorch_model(model_id, features, labels, epochs, batch_size, validation_split)
            else:
                return self._train_traditional_model(model_id, features, labels, validation_split)
                
        except Exception as e:
            self.logger.error(f"❌ Training failed for {model_id}: {e}")
            return None
    
    def _train_pytorch_model(self, model_id: str, features: np.ndarray, labels: np.ndarray,
                           epochs: int, batch_size: int, validation_split: float) -> Dict[str, Any]:
        """Train PyTorch model (LSTM or Transformer)"""
        model_info = self.models[model_id]
        model = model_info['model']
        optimizer = model_info['optimizer']
        criterion = model_info['criterion']
        sequence_length = model_info['sequence_length']
        
        # Prepare data
        X_tensor, y_tensor = self.prepare_data_for_pytorch(features, labels, sequence_length)
        
        # Train/validation split
        split_idx = int(len(X_tensor) * (1 - validation_split))
        X_train, X_val = X_tensor[:split_idx], X_tensor[split_idx:]
        y_train, y_val = y_tensor[:split_idx], y_tensor[split_idx:]
        
        # Create data loaders
        train_dataset = TensorDataset(X_train, y_train)
        val_dataset = TensorDataset(X_val, y_val)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        # Training loop
        training_history = {'train_loss': [], 'val_loss': [], 'val_accuracy': []}
        
        model.train()
        for epoch in range(epochs):
            # Training
            train_loss = 0.0
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            
            # Validation
            model.eval()
            val_loss = 0.0
            correct = 0
            total = 0
            
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    outputs = model(batch_X)
                    loss = criterion(outputs, batch_y)
                    val_loss += loss.item()
                    
                    _, predicted = torch.max(outputs.data, 1)
                    total += batch_y.size(0)
                    correct += (predicted == batch_y).sum().item()
            
            train_loss /= len(train_loader)
            val_loss /= len(val_loader)
            val_accuracy = 100 * correct / total
            
            training_history['train_loss'].append(train_loss)
            training_history['val_loss'].append(val_loss)
            training_history['val_accuracy'].append(val_accuracy)
            
            if epoch % 10 == 0:
                self.logger.info(f"Epoch {epoch}: Train Loss: {train_loss:.4f}, "
                               f"Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy:.2f}%")
            
            model.train()
        
        self.training_history[model_id] = training_history
        self.logger.info(f"✅ PyTorch model {model_id} trained successfully")
        
        return {
            'model_id': model_id,
            'final_val_accuracy': training_history['val_accuracy'][-1],
            'final_val_loss': training_history['val_loss'][-1],
            'epochs_trained': epochs
        }
    
    def _train_traditional_model(self, model_id: str, features: np.ndarray, labels: np.ndarray,
                               validation_split: float) -> Dict[str, Any]:
        """Train traditional ML model"""
        model_info = self.models[model_id]
        model = model_info['model']
        scaler = model_info['scaler']
        
        # Scale features
        X_scaled = scaler.fit_transform(features)
        
        # Train/validation split
        X_train, X_val, y_train, y_val = train_test_split(
            X_scaled, labels, test_size=validation_split, random_state=42
        )
        
        # Train model
        model.fit(X_train, y_train)
        
        # Evaluate
        train_accuracy = model.score(X_train, y_train)
        val_accuracy = model.score(X_val, y_val)
        
        self.logger.info(f"✅ Traditional model {model_id} trained - "
                        f"Train Acc: {train_accuracy:.3f}, Val Acc: {val_accuracy:.3f}")
        
        return {
            'model_id': model_id,
            'train_accuracy': train_accuracy,
            'val_accuracy': val_accuracy
        }
    
    def predict(self, model_id: str, features: np.ndarray) -> Optional[np.ndarray]:
        """
        Make predictions using specified model
        """
        if model_id not in self.models:
            self.logger.error(f"❌ Model {model_id} not found")
            return None
        
        model_info = self.models[model_id]
        model_type = model_info['type']
        
        try:
            if model_type in ['lstm', 'transformer']:
                return self._predict_pytorch_model(model_id, features)
            else:
                return self._predict_traditional_model(model_id, features)
                
        except Exception as e:
            self.logger.error(f"❌ Prediction failed for {model_id}: {e}")
            return None
    
    def _predict_pytorch_model(self, model_id: str, features: np.ndarray) -> np.ndarray:
        """Make predictions with PyTorch model"""
        model_info = self.models[model_id]
        model = model_info['model']
        sequence_length = model_info['sequence_length']
        
        if len(features) < sequence_length:
            # If not enough data, use the available data and pad
            padded_features = np.zeros((sequence_length, features.shape[1]))
            padded_features[-len(features):] = features
            features = padded_features
        
        # Use the last sequence for prediction
        last_sequence = features[-sequence_length:]
        X_tensor = torch.FloatTensor(last_sequence).unsqueeze(0).to(self.device)
        
        model.eval()
        with torch.no_grad():
            output = model(X_tensor)
            probabilities = output.cpu().numpy()[0]
            prediction = np.argmax(probabilities)
        
        return prediction, probabilities
    
    def _predict_traditional_model(self, model_id: str, features: np.ndarray) -> np.ndarray:
        """Make predictions with traditional model"""
        model_info = self.models[model_id]
        model = model_info['model']
        scaler = model_info['scaler']
        
        # Use the last feature vector for prediction
        last_features = features[-1:] if len(features.shape) > 1 else features.reshape(1, -1)
        X_scaled = scaler.transform(last_features)
        
        prediction = model.predict(X_scaled)[0]
        probabilities = model.predict_proba(X_scaled)[0] if hasattr(model, 'predict_proba') else None
        
        return prediction, probabilities
    
    def save_model(self, model_id: str, filepath: str) -> bool:
        """
        Save model to disk (compatible with Firebase storage)
        """
        if model_id not in self.models:
            self.logger.error(f"❌ Model {model_id} not found")
            return False
        
        try:
            model_info = self.models[model_id]
            model_type = model_info['type']
            
            save_data = {
                'model_id': model_id,
                'metadata': self.model_metadata[model_id],
                'type': model_type
            }
            
            if model_type in ['lstm', 'transformer']:
                # Save PyTorch model state dict
                save_data['model_state_dict'] = model_info['model'].state_dict()
                save_data['optimizer_state_dict'] = model_info['optimizer'].state_dict()
                torch.save(save_data, filepath)
            else:
                # Save traditional model with pickle
                save_data['model'] = model_info['model']
                save_data['scaler'] = model_info['scaler']
                with open(filepath, 'wb') as f:
                    pickle.dump(save_data, f)
            
            self.logger.info(f"✅ Model {model_id} saved to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save model {model_id}: {e}")
            return False
    
    def get_model_summary(self) -> Dict[str, Any]:
        """
        Get summary of all models
        """
        summary = {
            'total_models': len(self.models),
            'pytorch_available': self.pytorch_available,
            'device': str(self.device) if self.pytorch_available else None,
            'models': {}
        }
        
        for model_id, metadata in self.model_metadata.items():
            summary['models'][model_id] = {
                'type': metadata['type'],
                'created': metadata['created'].isoformat(),
                'framework': metadata.get('framework', 'pytorch')
            }
        
        return summary
    
    def predict_stock_movement(self, symbol: str, market_data: Dict[str, Any], 
                              technical_indicators: Dict[str, Any], market_regime: str,
                              sector_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Predict stock movement direction and confidence using ML models
        Compatible interface for stocks module integration
        """
        try:
            # Extract features from market data and technical indicators
            features = self._extract_stock_features(
                market_data, technical_indicators, market_regime, sector_context
            )
            
            if features is None or len(features) == 0:
                # Return neutral prediction if no features available
                return {
                    'confidence': 0.5,
                    'direction': 'neutral',
                    'price_target': market_data.get('current_price', 100.0),
                    'time_horizon_hours': 1,
                    'regime_alignment': 0.5,
                    'model_used': 'fallback',
                    'feature_quality': 'insufficient'
                }
            
            # Try to make prediction with best available model
            best_prediction = None
            model_used = 'none'
            
            # Use the most recent model if available
            if self.models:
                recent_model_id = max(self.models.keys(), 
                                    key=lambda x: self.model_metadata[x]['created'])
                
                try:
                    prediction, probabilities = self.predict(recent_model_id, features)
                    if prediction is not None:
                        best_prediction = prediction
                        model_used = recent_model_id
                        
                        # Convert model output to trading signals
                        if probabilities is not None and len(probabilities) >= 3:
                            # Assuming 3-class output: [Sell, Hold, Buy]
                            sell_prob = probabilities[0]
                            hold_prob = probabilities[1] 
                            buy_prob = probabilities[2]
                            
                            if buy_prob > max(sell_prob, hold_prob):
                                direction = 'bullish'
                                confidence = float(buy_prob)
                            elif sell_prob > max(buy_prob, hold_prob):
                                direction = 'bearish'
                                confidence = float(sell_prob)
                            else:
                                direction = 'neutral'
                                confidence = float(hold_prob)
                        else:
                            direction = 'neutral'
                            confidence = 0.5
                            
                except Exception as e:
                    self.logger.warning(f"⚠️ ML prediction failed for {symbol}: {e}")
            
            # Fallback to technical analysis if ML prediction failed
            if best_prediction is None:
                confidence, direction = self._fallback_technical_prediction(technical_indicators)
                model_used = 'technical_fallback'
            
            # Calculate price target based on direction and current price
            current_price = market_data.get('current_price', 100.0)
            if direction == 'bullish':
                price_target = current_price * 1.02  # 2% upside target
            elif direction == 'bearish':
                price_target = current_price * 0.98  # 2% downside target
            else:
                price_target = current_price  # Neutral
            
            # Calculate regime alignment
            regime_alignment = self._calculate_regime_alignment(market_regime, direction)
            
            return {
                'confidence': max(0.0, min(1.0, confidence)),
                'direction': direction,
                'price_target': price_target,
                'time_horizon_hours': 1,  # 1-hour horizon for intraday
                'regime_alignment': regime_alignment,
                'model_used': model_used,
                'feature_quality': 'good' if len(features) > 5 else 'limited',
                'raw_features_count': len(features)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Stock movement prediction failed for {symbol}: {e}")
            # Return safe neutral prediction
            return {
                'confidence': 0.5,
                'direction': 'neutral',
                'price_target': market_data.get('current_price', 100.0),
                'time_horizon_hours': 1,
                'regime_alignment': 0.5,
                'model_used': 'error_fallback',
                'error': str(e)
            }
    
    def _extract_stock_features(self, market_data: Dict[str, Any], 
                               technical_indicators: Dict[str, Any], 
                               market_regime: str, sector_context: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract numerical features for ML model from market data"""
        try:
            features = []
            
            # Market data features
            if market_data:
                features.extend([
                    market_data.get('current_price', 100.0),
                    market_data.get('volume', 1000000),
                    market_data.get('volatility', 0.02),
                    market_data.get('spread', 0.01)
                ])
            
            # Technical indicator features
            if technical_indicators:
                indicators = technical_indicators.get('raw_indicators', {})
                
                # RSI
                features.append(indicators.get('rsi', 50.0))
                
                # MACD
                macd_data = indicators.get('macd', {})
                features.extend([
                    macd_data.get('macd', 0.0),
                    macd_data.get('signal', 0.0),
                    macd_data.get('histogram', 0.0)
                ])
                
                # Bollinger Bands
                bb_data = indicators.get('bollinger_bands', {})
                features.extend([
                    bb_data.get('position', 50.0),  # Position within bands
                    bb_data.get('bandwidth', 10.0)  # Band width
                ])
                
                # Moving averages
                mas = indicators.get('moving_averages', {})
                current_price = market_data.get('current_price', 100.0)
                features.extend([
                    current_price / mas.get(20, current_price) - 1,  # Price vs MA20
                    current_price / mas.get(50, current_price) - 1,  # Price vs MA50
                    mas.get(20, current_price) / mas.get(50, current_price) - 1  # MA20 vs MA50
                ])
            
            # Market regime features
            regime_mapping = {'bull': 1.0, 'bear': -1.0, 'sideways': 0.0, 'uncertain': 0.0}
            features.append(regime_mapping.get(market_regime, 0.0))
            
            # Sector context features
            if sector_context:
                features.extend([
                    sector_context.get('sector_momentum', 0.0),
                    sector_context.get('sector_volatility', 0.02),
                    1.0 if sector_context.get('rotation_signal') == 'positive' else 0.0
                ])
            
            # Ensure we have enough features
            while len(features) < 10:
                features.append(0.0)  # Pad with zeros
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            self.logger.error(f"❌ Feature extraction failed: {e}")
            return None
    
    def _fallback_technical_prediction(self, technical_indicators: Dict[str, Any]) -> Tuple[float, str]:
        """Fallback prediction based on technical indicators only"""
        try:
            signals = technical_indicators.get('raw_signals', {})
            
            bullish_count = sum(1 for signal in signals.values() if signal == 'bullish')
            bearish_count = sum(1 for signal in signals.values() if signal == 'bearish')
            total_signals = len(signals)
            
            if total_signals == 0:
                return 0.5, 'neutral'
            
            if bullish_count > bearish_count:
                confidence = 0.5 + (bullish_count - bearish_count) / total_signals * 0.3
                return confidence, 'bullish'
            elif bearish_count > bullish_count:
                confidence = 0.5 + (bearish_count - bullish_count) / total_signals * 0.3
                return confidence, 'bearish'
            else:
                return 0.5, 'neutral'
                
        except Exception:
            return 0.5, 'neutral'
    
    def _calculate_regime_alignment(self, market_regime: str, predicted_direction: str) -> float:
        """Calculate how well the prediction aligns with market regime"""
        regime_bias = {
            'bull': {'bullish': 0.8, 'neutral': 0.6, 'bearish': 0.2},
            'bear': {'bullish': 0.2, 'neutral': 0.4, 'bearish': 0.8},
            'sideways': {'bullish': 0.5, 'neutral': 0.7, 'bearish': 0.5},
            'uncertain': {'bullish': 0.5, 'neutral': 0.5, 'bearish': 0.5}
        }
        
        return regime_bias.get(market_regime, {}).get(predicted_direction, 0.5)


# Singleton instance for modular system integration
enhanced_ml_framework = None

def get_enhanced_ml_framework(**kwargs) -> EnhancedMLFramework:
    """
    Get singleton instance of enhanced ML framework
    Preserves Firebase + Railway compatibility
    """
    global enhanced_ml_framework
    if enhanced_ml_framework is None:
        enhanced_ml_framework = EnhancedMLFramework(**kwargs)
    return enhanced_ml_framework


if __name__ == "__main__":
    # Test the enhanced ML framework
    print("🧠 Testing Enhanced ML Framework")
    print("=" * 50)
    
    # Initialize framework
    ml_framework = EnhancedMLFramework()
    
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    # Create sample features (price indicators, volume, etc.)
    features = np.random.randn(n_samples, n_features)
    
    # Create sample labels (0: Sell, 1: Hold, 2: Buy)
    labels = np.random.choice([0, 1, 2], n_samples, p=[0.3, 0.4, 0.3])
    
    print(f"📊 Sample data: {n_samples} samples, {n_features} features")
    
    # Test traditional model
    rf_model_id = ml_framework.create_traditional_model('random_forest')
    if rf_model_id:
        rf_results = ml_framework.train_model(rf_model_id, features, labels)
        print(f"🌲 Random Forest trained: {rf_results}")
    
    # Test PyTorch models (if available)
    if PYTORCH_AVAILABLE:
        # Test LSTM
        lstm_model_id = ml_framework.create_lstm_model(input_size=n_features, sequence_length=20)
        if lstm_model_id:
            lstm_results = ml_framework.train_model(lstm_model_id, features, labels, epochs=50)
            print(f"🔄 LSTM trained: {lstm_results}")
        
        # Test Transformer
        transformer_model_id = ml_framework.create_transformer_model(input_size=n_features, sequence_length=20)
        if transformer_model_id:
            transformer_results = ml_framework.train_model(transformer_model_id, features, labels, epochs=30)
            print(f"🤖 Transformer trained: {transformer_results}")
    
    # Get summary
    summary = ml_framework.get_model_summary()
    print(f"\n📋 Model Summary: {summary}")