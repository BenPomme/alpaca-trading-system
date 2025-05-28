# 🚀 DUAL SERVICE RAILWAY DEPLOYMENT

## 📋 Overview
Deploy your trading system as **2 separate Railway services**:
1. **Trading Worker** - Continuous background trading bot
2. **Dashboard Web** - Real-time web interface

## 🏗️ Architecture

```
┌─────────────────────┐    ┌─────────────────────┐
│   TRADING WORKER    │    │   DASHBOARD WEB     │
│                     │    │                     │
│ • Runs trading bot  │◄──►│ • Web interface     │
│ • Every 2 minutes   │    │ • Shows live data   │
│ • Writes JSON files │    │ • Reads JSON files  │
│ • Background service│    │ • HTTP endpoints    │
└─────────────────────┘    └─────────────────────┘
         SERVICE 1                 SERVICE 2
```

## 🎯 Benefits
- **Separation of concerns** - trading logic separate from web interface
- **Better reliability** - if one service fails, the other continues
- **Easier debugging** - independent logs and monitoring
- **Scalability** - services can be scaled independently

## 🚀 Railway Deployment Steps

### Step 1: Deploy Dashboard Web Service (Current)
**Already done!** Your current service will become the dashboard.

### Step 2: Create Trading Worker Service
1. Go to Railway dashboard
2. Click **"New Service"** in your project
3. Select **"Deploy from GitHub repo"**
4. Choose the same repo: `BenPomme/alpaca-trading-system`
5. **Important:** In service settings, change the **Start Command** to:
   ```
   python trading_worker.py
   ```
6. Add the same environment variables:
   ```
   ALPACA_PAPER_API_KEY=PKOBXG3RWCRQTXH6ID0L
   ALPACA_PAPER_SECRET_KEY=8A6pGtEB4HOD38SfLDWLibdA2ve9SOssepXEVFMn
   ```

### Step 3: Configure Services

**Dashboard Web Service:**
- **Type:** Web Service (has public URL)
- **Command:** `python dashboard_web.py`
- **Port:** 5000 (automatic)
- **Purpose:** User interface

**Trading Worker Service:**
- **Type:** Worker Service (no public URL needed)
- **Command:** `python trading_worker.py`
- **Purpose:** Background trading

## 📊 Data Communication

Services communicate via shared JSON files in `data/` directory:

**Files:**
- `data/worker_status.json` - Worker status and last cycle
- `data/trading_log.json` - Detailed trading history
- `data/manual_cycle_request.json` - Dashboard→Worker requests

**Data Flow:**
1. Worker runs trading cycles every 2 minutes
2. Worker writes status to JSON files
3. Dashboard reads JSON files and displays data
4. Dashboard can request manual cycles

## 🌐 Access Points

**Dashboard URL:** `https://your-project.up.railway.app`
**Worker Service:** Background only (no URL)

## 🔧 Service Commands

If you want to use Railway CLI:

```bash
# Deploy web dashboard
railway up --service web

# Deploy trading worker  
railway up --service worker
```

## ✅ Expected Behavior

**Dashboard Web Service:**
```
🌐 DASHBOARD WEB SERVICE
🕐 Started: 2025-05-28 16:30:00
☁️ Platform: Railway Cloud (Web Service)
📊 Type: Data presentation and monitoring
🔗 Communication: Reads worker JSON files
🌐 Dashboard starting on port 5000
```

**Trading Worker Service:**
```
🤖 TRADING WORKER SERVICE
🕐 Started: 2025-05-28 16:30:00
☁️ Platform: Railway Cloud (Worker Service)
💰 Mode: Paper Trading
🔄 Type: Continuous Background Trading
📊 Communication: JSON status files
🔄 Starting continuous worker monitoring...
```

## 📱 Dashboard Features

Once both services are running:
- **Live Status:** See worker status in real-time
- **Trading Activity:** View each cycle as it happens
- **Account Info:** Real-time portfolio updates
- **Market Data:** Live SPY/QQQ/IWM quotes
- **Manual Control:** Force trading cycles from dashboard

## 🎯 Next Step
Create the **Trading Worker** service in Railway dashboard and you'll have a professional dual-service architecture!