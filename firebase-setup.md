# Firebase Setup Guide for Alpaca Trading System

## Firebase Configuration

Your Firebase project details:
- **Project ID**: `alpaca-12fab`
- **Auth Domain**: `alpaca-12fab.firebaseapp.com`
- **Storage Bucket**: `alpaca-12fab.firebasestorage.app`

## Required Service Account Setup

### 1. Generate Service Account Key

1. Go to [Firebase Console](https://console.firebase.google.com/project/alpaca-12fab)
2. Click **Project Settings** → **Service Accounts**
3. Click **Generate New Private Key**
4. Download the JSON file and rename it to `firebase-service-account.json`

### 2. Railway Environment Variables Setup

For Railway deployment, set these environment variables in your Railway dashboard:

#### Firebase Service Account (from the JSON file you downloaded):

```bash
FIREBASE_PRIVATE_KEY_ID="your_private_key_id_here"
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour_private_key_here\n-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL="firebase-adminsdk-xxxxx@alpaca-12fab.iam.gserviceaccount.com"
FIREBASE_CLIENT_ID="your_client_id_here"
FIREBASE_CLIENT_CERT_URL="https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40alpaca-12fab.iam.gserviceaccount.com"
```

#### Existing Trading Variables:
```bash
ALPACA_PAPER_API_KEY="your_alpaca_key"
ALPACA_PAPER_SECRET_KEY="your_alpaca_secret"
EXECUTION_ENABLED="true"
GLOBAL_TRADING="true"
OPTIONS_TRADING="true"
CRYPTO_TRADING="true"
MARKET_TIER="2"
MIN_CONFIDENCE="0.6"
```

### 3. Local Development Setup

For local development, place the `firebase-service-account.json` file in your project root directory.

### 4. Firestore Database Rules

Set up Firestore security rules in Firebase Console → Firestore Database → Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write access to trading data collections
    match /trading_cycles/{document} {
      allow read, write: if true; // Adjust security as needed
    }
    match /trades/{document} {
      allow read, write: if true;
    }
    match /market_quotes/{document} {
      allow read, write: if true;
    }
    match /ml_models/{document} {
      allow read, write: if true;
    }
    match /performance_metrics/{document} {
      allow read, write: if true;
    }
  }
}
```

## Firebase Collections Structure

The system will automatically create these collections:

### `trading_cycles`
- Stores intelligence analysis cycles
- Contains confidence scores, strategies, market regime data
- Used for ML training and performance tracking

### `trades`
- Stores all trade executions (stocks, options, crypto)
- Contains entry/exit data, P&L, strategies
- Used for performance analysis and dashboard

### `market_quotes`
- Real-time market data storage
- Price, volume, timestamp data
- Used for technical analysis

### `ml_models`
- ML model states for persistence across deployments
- Strategy selector, risk predictor model states
- Performance metrics and learning progress

### `performance_metrics`
- Portfolio performance over time
- Win rates, ROI, drawdown metrics
- Used for dashboard charts and analysis

## Testing Firebase Connection

Run this command to test Firebase connectivity:

```bash
python firebase_database.py
```

This will verify:
- ✅ Firebase connection successful
- 📊 Database stats and collection counts
- 🔥 Sample data save/retrieve operations

## Architecture Benefits

### Before Firebase (Ephemeral):
```
Railway Restart → SQLite Wiped → ML Learning Lost → Start from Zero
```

### After Firebase (Persistent):
```
Railway Restart → Connect to Firebase → ML Learning Persists → Continuous Improvement
```

### Key Advantages:
1. **True Persistence**: ML models keep learning across Railway restarts
2. **Real-time Sync**: Dashboard gets live updates from Firebase
3. **Scalability**: Multiple instances can share the same database
4. **Backup**: Data is automatically backed up by Google Cloud
5. **Analytics**: Rich querying capabilities for performance analysis

## Monitoring & Maintenance

### Database Statistics
The system provides real-time database stats:
```python
stats = firebase_db.get_database_stats()
# Returns collection counts and connection status
```

### Data Cleanup
Automatic cleanup of old data (configurable):
```python
firebase_db.clear_old_data(days_to_keep=90)
```

### Performance Monitoring
Track Firebase usage in Railway logs:
- 🔥 Trading cycle saved to Firebase
- 🔥 Trade saved to Firebase 
- ✅ ML states saved to Firebase
- 📊 Using X trades from Firebase

## Troubleshooting

### Common Issues:

1. **Firebase Not Connected**:
   - Check environment variables are set correctly
   - Verify service account JSON format
   - Ensure Firestore is enabled in Firebase Console

2. **Permission Denied**:
   - Update Firestore security rules
   - Verify service account has correct permissions

3. **Import Errors**:
   - Ensure `firebase-admin` and `google-cloud-firestore` are in requirements.txt
   - Run `pip install firebase-admin google-cloud-firestore`

### Debug Commands:
```bash
# Test Firebase connectivity
python firebase_database.py

# Test trading system with Firebase
python phase3_trader.py

# Check dashboard with Firebase data
python dashboard_api.py
```