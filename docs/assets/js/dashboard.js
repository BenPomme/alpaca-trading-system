// Enhanced Alpaca Trading Dashboard JavaScript with ML Audit Trail
class TradingDashboard {
    constructor() {
        this.data = {
            portfolio: null,
            positions: [],
            trades: [],
            performance: null,
            strategies: [],
            mlData: {
                decisions: [],
                learningEvents: [],
                parameters: [],
                modelStatus: {},
                performance: {}
            }
        };
        this.chart = null;
        this.mlParametersChart = null;
        this.mlEffectivenessChart = null;
        this.refreshInterval = null;
        this.init();
    }

    async init() {
        console.log('🚀 Initializing Enhanced Trading Dashboard with ML Audit Trail...');
        this.setupEventListeners();
        await this.loadDashboardData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.filterPositions(e.target.dataset.filter);
            });
        });

        // ML Tab buttons
        document.querySelectorAll('.ml-tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.ml-tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.ml-tab-content').forEach(c => c.classList.remove('active'));
                
                e.target.classList.add('active');
                const tabId = `ml-${e.target.dataset.tab}`;
                document.getElementById(tabId).classList.add('active');
                
                // Load specific ML data for the tab
                this.loadMLTabData(e.target.dataset.tab);
            });
        });

        // Manual refresh
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.loadDashboardData();
            }
        });
    }

    async loadDashboardData() {
        try {
            console.log('📊 Loading enhanced dashboard data with ML audit trail...');
            document.body.classList.add('loading');

            const data = await this.fetchTradingData();
            this.data = { ...this.data, ...data };

            // Load ML audit trail data
            await this.loadMLData();

            // Update all sections
            this.updateHeaderStats();
            this.updatePerformanceMetrics();
            this.updatePositionsTable();
            this.updateTradesTable();
            this.updateStrategyPerformance();
            this.updateIntradayStatus();
            this.updatePortfolioChart();
            
            // Update ML sections
            this.updateMLAuditTrail();
            this.updateMLModelStatus();

            this.updateLastSync();
            console.log('✅ Enhanced dashboard data loaded successfully');

        } catch (error) {
            console.error('❌ Error loading dashboard data:', error);
            this.showError('Failed to load trading data. Using demo data with ML simulation.');
            
            // Load enhanced mock data with ML components
            await this.loadEnhancedMockData();
        } finally {
            document.body.classList.remove('loading');
        }
    }

    async fetchTradingData() {
        const timestamp = Date.now();
        
        // Try to fetch from Firebase/API with ML data
        try {
            console.log('🔄 Attempting to fetch live data with ML audit trail...');
            const response = await fetch(`./api/dashboard-data.json?v=${timestamp}`);
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Loaded live trading data');
                
                // Enhance with ML data if not present
                if (!data.mlData) {
                    data.mlData = this.generateMockMLData();
                }
                
                return data;
            }
        } catch (error) {
            console.log('❌ API error, using enhanced mock data:', error.message);
        }

        // Generate enhanced mock data with ML components
        console.log('📊 Using enhanced mock data with ML simulation');
        return this.generateEnhancedMockData();
    }

    generateEnhancedMockData() {
        const baseData = this.generateMockData();
        baseData.mlData = this.generateMockMLData();
        return baseData;
    }

    generateMockData() {
        const now = new Date();
        
        return {
            portfolio: {
                value: 102157.43,
                cash: 18532.57,
                dayTradingPower: 245926.24,
                dailyPL: 1245.67,
                dailyPLPercent: 1.23
            },
            positions: [
                {
                    symbol: 'AAPL',
                    quantity: 18,
                    entryPrice: 195.25,
                    currentPrice: 198.75,
                    marketValue: 3577.50,
                    unrealizedPL: 63.00,
                    unrealizedPLPercent: 1.79,
                    holdTime: '3.2h',
                    strategy: 'ml_momentum',
                    type: 'stock',
                    mlScore: 0.87
                },
                {
                    symbol: 'NVDA',
                    quantity: 12,
                    entryPrice: 142.50,
                    currentPrice: 145.20,
                    marketValue: 1742.40,
                    unrealizedPL: 32.40,
                    unrealizedPLPercent: 1.89,
                    holdTime: '1.8h',
                    strategy: 'aggressive_momentum',
                    type: 'stock',
                    mlScore: 0.92
                },
                {
                    symbol: 'BTCUSD',
                    quantity: 0.0845,
                    entryPrice: 47200,
                    currentPrice: 48100,
                    marketValue: 4064.45,
                    unrealizedPL: 76.05,
                    unrealizedPLPercent: 1.90,
                    holdTime: '2.1d',
                    strategy: 'crypto_momentum',
                    type: 'crypto',
                    mlScore: 0.78
                },
                {
                    symbol: 'MSFT',
                    quantity: 8,
                    entryPrice: 461.25,
                    currentPrice: 459.80,
                    marketValue: 3678.40,
                    unrealizedPL: -11.60,
                    unrealizedPLPercent: -0.31,
                    holdTime: '5.4h',
                    strategy: 'momentum',
                    type: 'stock',
                    mlScore: 0.65
                }
            ],
            trades: [
                {
                    date: '2025-05-31 13:45:22',
                    symbol: 'TSLA',
                    side: 'SELL',
                    quantity: 15,
                    price: 178.95,
                    pl: 89.25,
                    plPercent: 3.45,
                    strategy: 'ml_momentum',
                    exitReason: 'ml_profit_protection',
                    mlDecision: true,
                    mlConfidence: 0.91
                },
                {
                    date: '2025-05-31 12:30:15',
                    symbol: 'AMD',
                    side: 'BUY',
                    quantity: 25,
                    price: 156.20,
                    pl: 0,
                    plPercent: 0,
                    strategy: 'ml_momentum',
                    exitReason: null,
                    mlDecision: true,
                    mlConfidence: 0.84
                },
                {
                    date: '2025-05-31 11:15:30',
                    symbol: 'GOOGL',
                    side: 'SELL',
                    quantity: 4,
                    price: 185.40,
                    pl: 45.60,
                    plPercent: 2.51,
                    strategy: 'aggressive_momentum',
                    exitReason: 'time_based',
                    mlDecision: false,
                    mlConfidence: 0.45
                }
            ],
            performance: {
                totalTrades: 189,
                winningTrades: 117,
                losingTrades: 72,
                winRate: 61.90,
                avgHoldTime: 5.8,
                bestTrade: 312.45,
                worstTrade: -67.20,
                totalROI: 18.67,
                dailyROI: 1.23,
                weeklyROI: 4.12,
                monthlyROI: 12.34
            },
            strategies: [
                {
                    name: 'ml_momentum',
                    trades: 67,
                    winRate: 71.6,
                    avgReturn: 3.2,
                    totalReturn: 214.4,
                    mlEnhanced: true
                },
                {
                    name: 'aggressive_momentum',
                    trades: 52,
                    winRate: 59.6,
                    avgReturn: 2.4,
                    totalReturn: 124.8,
                    mlEnhanced: false
                },
                {
                    name: 'momentum',
                    trades: 45,
                    winRate: 55.6,
                    avgReturn: 1.8,
                    totalReturn: 81.0,
                    mlEnhanced: false
                },
                {
                    name: 'crypto_momentum',
                    trades: 25,
                    winRate: 68.0,
                    avgReturn: 4.1,
                    totalReturn: 102.5,
                    mlEnhanced: true
                }
            ],
            marketStatus: {
                isOpen: true,
                nextOpen: '2025-06-02 09:30:00 ET',
                nextClose: '2025-05-31 16:00:00 ET'
            }
        };
    }

    generateMockMLData() {
        const now = new Date();
        
        return {
            decisions: [
                {
                    id: 'ml_001',
                    timestamp: new Date(now.getTime() - 15 * 60 * 1000).toISOString(),
                    type: 'Strategy Selection',
                    decision: 'Selected ML_MOMENTUM strategy for AAPL',
                    confidence: 0.87,
                    details: 'High momentum signals (RSI: 72, MACD: bullish, Volume: +45%) with strong market regime confidence (0.91)',
                    parameters: {
                        rsi: 72,
                        macd: 'bullish',
                        volume_change: 45,
                        regime_confidence: 0.91
                    },
                    outcome: 'pending'
                },
                {
                    id: 'ml_002',
                    timestamp: new Date(now.getTime() - 45 * 60 * 1000).toISOString(),
                    type: 'Risk Adjustment',
                    decision: 'Reduced position size for MSFT by 20%',
                    confidence: 0.73,
                    details: 'Elevated sector volatility detected. Risk model suggests reducing exposure in tech sector.',
                    parameters: {
                        sector_volatility: 0.34,
                        correlation_risk: 0.67,
                        position_adjustment: -0.20
                    },
                    outcome: 'applied'
                },
                {
                    id: 'ml_003',
                    timestamp: new Date(now.getTime() - 90 * 60 * 1000).toISOString(),
                    type: 'Exit Signal',
                    decision: 'Triggered profit protection exit for TSLA',
                    confidence: 0.91,
                    details: 'Momentum degradation detected. ML model predicts 78% probability of reversal within 2 hours.',
                    parameters: {
                        momentum_score: 0.23,
                        reversal_probability: 0.78,
                        profit_protection: true
                    },
                    outcome: 'successful'
                }
            ],
            learningEvents: [
                {
                    id: 'learn_001',
                    timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
                    type: 'Parameter Optimization',
                    event: 'Updated momentum threshold for crypto assets',
                    impact: 'Improved crypto strategy win rate by 4.2%',
                    details: 'Learning from recent crypto market volatility patterns. Adjusted momentum sensitivity from 0.65 to 0.72.',
                    before: { momentum_threshold: 0.65 },
                    after: { momentum_threshold: 0.72 },
                    performance_improvement: 4.2
                },
                {
                    id: 'learn_002',
                    timestamp: new Date(now.getTime() - 4 * 60 * 60 * 1000).toISOString(),
                    type: 'Strategy Refinement',
                    event: 'Enhanced exit timing for aggressive momentum',
                    impact: 'Reduced average loss by 15%',
                    details: 'ML detected pattern where holding positions >4h in high volatility regime reduces profitability.',
                    before: { max_hold_time: '6h' },
                    after: { max_hold_time: '4h' },
                    performance_improvement: 15.0
                },
                {
                    id: 'learn_003',
                    timestamp: new Date(now.getTime() - 6 * 60 * 60 * 1000).toISOString(),
                    type: 'Risk Model Update',
                    event: 'Calibrated sector correlation matrix',
                    impact: 'Better portfolio diversification',
                    details: 'Updated correlation assumptions based on recent market data. Tech sector correlation increased to 0.78.',
                    before: { tech_correlation: 0.65 },
                    after: { tech_correlation: 0.78 },
                    performance_improvement: 8.5
                }
            ],
            parameters: {
                current: {
                    momentum_threshold: 0.72,
                    risk_tolerance: 0.15,
                    max_position_size: 0.08,
                    stop_loss_threshold: 0.02,
                    profit_target: 0.03,
                    regime_confidence_min: 0.60
                },
                history: [
                    {
                        timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
                        parameter: 'momentum_threshold',
                        old_value: 0.65,
                        new_value: 0.72,
                        reason: 'Crypto volatility adaptation'
                    },
                    {
                        timestamp: new Date(now.getTime() - 1 * 24 * 60 * 60 * 1000).toISOString(),
                        parameter: 'max_position_size',
                        old_value: 0.10,
                        new_value: 0.08,
                        reason: 'Risk reduction after market stress'
                    }
                ]
            },
            modelStatus: {
                strategySelector: {
                    status: 'online',
                    accuracy: 0.73,
                    confidence: 0.85,
                    lastUpdate: new Date(now.getTime() - 30 * 60 * 1000).toISOString(),
                    trainingData: 1247,
                    version: 'v2.3.1'
                },
                riskPredictor: {
                    status: 'online',
                    accuracy: 0.68,
                    confidence: 0.79,
                    lastUpdate: new Date(now.getTime() - 45 * 60 * 1000).toISOString(),
                    trainingData: 892,
                    version: 'v1.8.2'
                },
                regimeDetector: {
                    status: 'online',
                    currentRegime: 'Bullish Momentum',
                    confidence: 0.91,
                    lastUpdate: new Date(now.getTime() - 10 * 60 * 1000).toISOString(),
                    trainingData: 2156,
                    version: 'v3.1.0'
                }
            },
            performance: {
                mlTrades: {
                    total: 89,
                    wins: 64,
                    winRate: 71.9,
                    avgReturn: 2.8,
                    totalPL: 2847.65
                },
                traditionalTrades: {
                    total: 100,
                    wins: 53,
                    winRate: 53.0,
                    avgReturn: 1.9,
                    totalPL: 1923.40
                },
                effectiveness: {
                    mlAdvantage: 18.9, // percentage points better
                    riskAdjustedReturn: 3.2,
                    sharpeImprovement: 0.45
                }
            }
        };
    }

    async loadMLData() {
        // In a real implementation, this would fetch from Firebase ML collections
        console.log('🧠 Loading ML audit trail data...');
        
        // For now, ensure we have ML data
        if (!this.data.mlData) {
            this.data.mlData = this.generateMockMLData();
        }
    }

    loadMLTabData(tab) {
        console.log(`📊 Loading ML tab data for: ${tab}`);
        
        switch (tab) {
            case 'decisions':
                this.updateMLDecisions();
                break;
            case 'learning':
                this.updateMLLearningEvents();
                break;
            case 'parameters':
                this.updateMLParameters();
                break;
            case 'performance':
                this.updateMLPerformance();
                break;
        }
    }

    updateMLAuditTrail() {
        console.log('🧠 Updating ML audit trail...');
        this.updateMLDecisions();
        this.updateMLModelStatus();
    }

    updateMLDecisions() {
        const container = document.getElementById('ml-decisions-list');
        if (!container) return;
        
        container.innerHTML = '';
        
        const decisions = this.data.mlData.decisions || [];
        
        decisions.slice(0, 10).forEach(decision => {
            const item = document.createElement('div');
            item.className = 'ml-decision-item';
            
            const confidenceClass = decision.confidence >= 0.8 ? 'high' : decision.confidence >= 0.6 ? 'medium' : 'low';
            
            item.innerHTML = `
                <div class="ml-decision-header">
                    <span class="ml-decision-type">${decision.type}</span>
                    <span class="ml-decision-time">${new Date(decision.timestamp).toLocaleString()}</span>
                </div>
                <div class="ml-decision-details">
                    ${decision.decision}
                    <span class="ml-decision-confidence ${confidenceClass}">
                        ${(decision.confidence * 100).toFixed(0)}% confidence
                    </span>
                </div>
                <div class="ml-decision-details" style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--text-secondary);">
                    ${decision.details}
                </div>
            `;
            
            container.appendChild(item);
        });
    }

    updateMLLearningEvents() {
        const container = document.getElementById('ml-learning-list');
        if (!container) return;
        
        container.innerHTML = '';
        
        const events = this.data.mlData.learningEvents || [];
        
        events.slice(0, 10).forEach(event => {
            const item = document.createElement('div');
            item.className = 'ml-learning-item';
            
            item.innerHTML = `
                <div class="ml-learning-header">
                    <span class="ml-learning-type">${event.type}</span>
                    <span class="ml-learning-impact">+${event.performance_improvement}% improvement</span>
                </div>
                <div class="ml-decision-details">
                    <strong>${event.event}</strong><br>
                    ${event.details}
                </div>
                <div class="ml-decision-details" style="margin-top: 0.5rem; font-size: 0.8rem;">
                    Impact: ${event.impact}
                </div>
            `;
            
            container.appendChild(item);
        });
    }

    updateMLParameters() {
        this.updateMLParametersChart();
        this.updateParameterDetails();
    }

    updateMLParametersChart() {
        const canvas = document.getElementById('ml-parameters-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        if (this.mlParametersChart) {
            this.mlParametersChart.destroy();
        }
        
        // Generate parameter evolution data
        const parameterData = this.generateParameterChartData();
        
        this.mlParametersChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: parameterData.labels,
                datasets: parameterData.datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#f8fafc'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Parameter Evolution Over Time',
                        color: '#f8fafc'
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#334155' }
                    },
                    y: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#334155' }
                    }
                }
            }
        });
    }

    generateParameterChartData() {
        const hours = 24;
        const labels = [];
        const momentumData = [];
        const riskData = [];
        
        for (let i = hours; i >= 0; i--) {
            const time = new Date();
            time.setHours(time.getHours() - i);
            labels.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
            
            // Simulate parameter evolution
            momentumData.push(0.65 + (Math.random() * 0.1) + (i < 2 ? 0.07 : 0)); // Recent jump
            riskData.push(0.12 + (Math.random() * 0.06));
        }
        
        return {
            labels,
            datasets: [
                {
                    label: 'Momentum Threshold',
                    data: momentumData,
                    borderColor: '#60a5fa',
                    backgroundColor: 'rgba(96, 165, 250, 0.1)',
                    borderWidth: 2,
                    tension: 0.4
                },
                {
                    label: 'Risk Tolerance',
                    data: riskData,
                    borderColor: '#34d399',
                    backgroundColor: 'rgba(52, 211, 153, 0.1)',
                    borderWidth: 2,
                    tension: 0.4
                }
            ]
        };
    }

    updateParameterDetails() {
        const container = document.getElementById('parameter-details');
        if (!container) return;
        
        container.innerHTML = '';
        
        const params = this.data.mlData.parameters?.current || {};
        
        Object.entries(params).forEach(([key, value]) => {
            const card = document.createElement('div');
            card.className = 'parameter-card';
            
            // Find recent changes for this parameter
            const history = this.data.mlData.parameters?.history || [];
            const recentChange = history.find(h => h.parameter === key);
            
            let changeHtml = '';
            if (recentChange) {
                const change = ((value - recentChange.old_value) / recentChange.old_value * 100).toFixed(1);
                const changeClass = change > 0 ? 'positive' : 'negative';
                changeHtml = `
                    <div class="parameter-change ${changeClass}">
                        ${change > 0 ? '+' : ''}${change}% from ${recentChange.old_value}
                    </div>
                `;
            }
            
            card.innerHTML = `
                <div class="parameter-name">${key.replace(/_/g, ' ').toUpperCase()}</div>
                <div class="parameter-value">${typeof value === 'number' ? value.toFixed(3) : value}</div>
                ${changeHtml}
            `;
            
            container.appendChild(card);
        });
    }

    updateMLPerformance() {
        const mlData = this.data.mlData.performance || {};
        
        // Update ML performance stats
        document.getElementById('ml-total-trades').textContent = mlData.mlTrades?.total || 0;
        document.getElementById('ml-win-rate').textContent = `${(mlData.mlTrades?.winRate || 0).toFixed(1)}%`;
        document.getElementById('ml-avg-return').textContent = `${(mlData.mlTrades?.avgReturn || 0).toFixed(1)}%`;
        document.getElementById('ml-total-pl').textContent = `$${(mlData.mlTrades?.totalPL || 0).toLocaleString()}`;
        
        // Update traditional performance stats
        document.getElementById('traditional-total-trades').textContent = mlData.traditionalTrades?.total || 0;
        document.getElementById('traditional-win-rate').textContent = `${(mlData.traditionalTrades?.winRate || 0).toFixed(1)}%`;
        document.getElementById('traditional-avg-return').textContent = `${(mlData.traditionalTrades?.avgReturn || 0).toFixed(1)}%`;
        document.getElementById('traditional-total-pl').textContent = `$${(mlData.traditionalTrades?.totalPL || 0).toLocaleString()}`;
        
        // Update effectiveness chart
        this.updateMLEffectivenessChart();
    }

    updateMLEffectivenessChart() {
        const canvas = document.getElementById('ml-effectiveness-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        if (this.mlEffectivenessChart) {
            this.mlEffectivenessChart.destroy();
        }
        
        const mlData = this.data.mlData.performance || {};
        
        this.mlEffectivenessChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Win Rate', 'Avg Return', 'Total P&L'],
                datasets: [
                    {
                        label: 'ML-Driven',
                        data: [
                            mlData.mlTrades?.winRate || 0,
                            mlData.mlTrades?.avgReturn || 0,
                            (mlData.mlTrades?.totalPL || 0) / 100
                        ],
                        backgroundColor: 'rgba(96, 165, 250, 0.8)',
                        borderColor: '#60a5fa',
                        borderWidth: 1
                    },
                    {
                        label: 'Traditional',
                        data: [
                            mlData.traditionalTrades?.winRate || 0,
                            mlData.traditionalTrades?.avgReturn || 0,
                            (mlData.traditionalTrades?.totalPL || 0) / 100
                        ],
                        backgroundColor: 'rgba(156, 163, 175, 0.8)',
                        borderColor: '#9ca3af',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#f8fafc' }
                    },
                    title: {
                        display: true,
                        text: 'ML vs Traditional Performance Comparison',
                        color: '#f8fafc'
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#334155' }
                    },
                    y: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#334155' }
                    }
                }
            }
        });
    }

    updateMLModelStatus() {
        const modelStatus = this.data.mlData.modelStatus || {};
        
        // Strategy Selector
        const strategyStatus = modelStatus.strategySelector || {};
        this.updateModelCard('strategy', strategyStatus);
        
        // Risk Predictor
        const riskStatus = modelStatus.riskPredictor || {};
        this.updateModelCard('risk', riskStatus);
        
        // Regime Detector
        const regimeStatus = modelStatus.regimeDetector || {};
        this.updateModelCard('regime', regimeStatus);
    }

    updateModelCard(type, status) {
        const statusElement = document.getElementById(`${type === 'strategy' ? 'strategy-selector' : type === 'risk' ? 'risk-predictor' : 'regime-detector'}-status`);
        if (statusElement) {
            statusElement.className = `model-status ${status.status || 'offline'}`;
        }
        
        if (type === 'strategy') {
            document.getElementById('strategy-accuracy').textContent = `${((status.accuracy || 0) * 100).toFixed(1)}%`;
            document.getElementById('strategy-confidence').textContent = `${((status.confidence || 0) * 100).toFixed(1)}%`;
            document.getElementById('strategy-last-update').textContent = status.lastUpdate ? 
                new Date(status.lastUpdate).toLocaleString() : 'Never';
        } else if (type === 'risk') {
            document.getElementById('risk-accuracy').textContent = `${((status.accuracy || 0) * 100).toFixed(1)}%`;
            document.getElementById('risk-confidence').textContent = `${((status.confidence || 0) * 100).toFixed(1)}%`;
            document.getElementById('risk-last-update').textContent = status.lastUpdate ? 
                new Date(status.lastUpdate).toLocaleString() : 'Never';
        } else if (type === 'regime') {
            document.getElementById('current-regime').textContent = status.currentRegime || 'Unknown';
            document.getElementById('regime-confidence').textContent = `${((status.confidence || 0) * 100).toFixed(1)}%`;
            document.getElementById('regime-last-update').textContent = status.lastUpdate ? 
                new Date(status.lastUpdate).toLocaleString() : 'Never';
        }
    }

    // Enhanced methods with ML data
    updateHeaderStats() {
        const { portfolio } = this.data;
        
        document.getElementById('portfolio-value').textContent = 
            `$${portfolio.value.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
        
        const dailyPLElement = document.getElementById('daily-pl');
        dailyPLElement.textContent = 
            `$${portfolio.dailyPL.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
        dailyPLElement.className = `stat-value ${portfolio.dailyPL >= 0 ? 'positive' : 'negative'}`;
        
        document.getElementById('success-rate').textContent = 
            `${this.data.performance.winRate.toFixed(1)}%`;
        
        document.getElementById('active-positions').textContent = 
            this.data.positions.length.toString();
    }

    updatePerformanceMetrics() {
        const { performance } = this.data;
        
        document.getElementById('roi-today').textContent = `${performance.dailyROI >= 0 ? '+' : ''}${performance.dailyROI.toFixed(2)}%`;
        document.getElementById('roi-week').textContent = `${performance.weeklyROI >= 0 ? '+' : ''}${performance.weeklyROI.toFixed(2)}%`;
        document.getElementById('roi-month').textContent = `${performance.monthlyROI >= 0 ? '+' : ''}${performance.monthlyROI.toFixed(2)}%`;
        document.getElementById('roi-total').textContent = `${performance.totalROI >= 0 ? '+' : ''}${performance.totalROI.toFixed(2)}%`;
        
        document.getElementById('win-rate').textContent = `${performance.winRate.toFixed(1)}%`;
        document.getElementById('avg-hold-time').textContent = `${performance.avgHoldTime.toFixed(1)}h`;
        document.getElementById('total-trades').textContent = performance.totalTrades.toString();
        document.getElementById('best-trade').textContent = `$${performance.bestTrade.toFixed(2)}`;

        // Apply color classes
        ['roi-today', 'roi-week', 'roi-month', 'roi-total'].forEach(id => {
            const element = document.getElementById(id);
            const value = parseFloat(element.textContent);
            element.className = `roi-value ${value >= 0 ? 'positive' : 'negative'}`;
        });
    }

    updatePositionsTable() {
        const tbody = document.getElementById('positions-tbody');
        tbody.innerHTML = '';

        this.data.positions.forEach(position => {
            const row = document.createElement('tr');
            row.className = `position-row ${position.type}`;
            
            const plClass = position.unrealizedPL >= 0 ? 'positive' : 'negative';
            const plPercent = position.unrealizedPLPercent >= 0 ? '+' : '';
            
            // Add ML score indicator
            const mlIndicator = position.mlScore ? 
                `<span class="ml-score" title="ML Score: ${(position.mlScore * 100).toFixed(0)}%">🧠${(position.mlScore * 100).toFixed(0)}%</span>` : '';
            
            row.innerHTML = `
                <td><strong>${position.symbol}</strong> ${mlIndicator}</td>
                <td>${position.quantity}</td>
                <td>$${position.entryPrice.toFixed(2)}</td>
                <td>$${position.currentPrice.toFixed(2)}</td>
                <td class="${plClass}">$${position.unrealizedPL.toFixed(2)}</td>
                <td class="${plClass}">${plPercent}${position.unrealizedPLPercent.toFixed(2)}%</td>
                <td>${position.holdTime}</td>
                <td><span class="strategy-tag ${position.strategy.includes('ml') ? 'ml-strategy' : ''}">${position.strategy}</span></td>
            `;
            
            tbody.appendChild(row);
        });
    }

    updateTradesTable() {
        const tbody = document.getElementById('trades-tbody');
        tbody.innerHTML = '';

        const recentTrades = this.data.trades.slice(-20).reverse();
        
        recentTrades.forEach(trade => {
            const row = document.createElement('tr');
            const plClass = trade.pl >= 0 ? 'positive' : 'negative';
            const plSign = trade.pl >= 0 ? '+' : '';
            
            // Add ML decision indicator
            const mlIndicator = trade.mlDecision ? 
                `<span class="ml-decision-indicator" title="ML Confidence: ${(trade.mlConfidence * 100).toFixed(0)}%">🧠</span>` : '';
            
            row.innerHTML = `
                <td>${new Date(trade.date).toLocaleString()}</td>
                <td><strong>${trade.symbol}</strong> ${mlIndicator}</td>
                <td><span class="side-${trade.side.toLowerCase()}">${trade.side}</span></td>
                <td>${trade.quantity}</td>
                <td>$${trade.price.toFixed(2)}</td>
                <td class="${plClass}">${plSign}$${trade.pl.toFixed(2)}</td>
                <td><span class="strategy-tag ${trade.strategy.includes('ml') ? 'ml-strategy' : ''}">${trade.strategy}</span></td>
                <td>${trade.exitReason || 'Active'}</td>
            `;
            
            tbody.appendChild(row);
        });
    }

    updateStrategyPerformance() {
        const container = document.getElementById('strategy-stats');
        container.innerHTML = '';

        this.data.strategies.forEach(strategy => {
            const strategyDiv = document.createElement('div');
            strategyDiv.className = 'strategy-item';
            
            const returnClass = strategy.totalReturn >= 0 ? 'positive' : 'negative';
            const mlBadge = strategy.mlEnhanced ? '<span class="ml-badge">🧠 ML Enhanced</span>' : '';
            
            strategyDiv.innerHTML = `
                <div class="strategy-name">${strategy.name.replace('_', ' ').toUpperCase()} ${mlBadge}</div>
                <div class="strategy-metrics">
                    <span>Trades: ${strategy.trades}</span>
                    <span>Win Rate: ${strategy.winRate.toFixed(1)}%</span>
                    <span>Avg Return: ${strategy.avgReturn.toFixed(1)}%</span>
                    <span class="${returnClass}">Total: $${strategy.totalReturn.toFixed(2)}</span>
                </div>
            `;
            
            container.appendChild(strategyDiv);
        });
    }

    updateIntradayStatus() {
        document.getElementById('dt-power').textContent = 
            `$${this.data.portfolio.dayTradingPower.toLocaleString()}`;
        
        const intradayCount = this.data.positions.filter(p => p.type === 'stock').length;
        document.getElementById('intraday-count').textContent = intradayCount.toString();
        
        const marketStatusElement = document.getElementById('market-status');
        marketStatusElement.textContent = this.data.marketStatus.isOpen ? 'OPEN' : 'CLOSED';
        marketStatusElement.className = this.data.marketStatus.isOpen ? 'open' : 'closed';
    }

    updatePortfolioChart() {
        const ctx = document.getElementById('portfolio-chart').getContext('2d');
        
        const chartData = this.generateChartData();
        
        if (this.chart) {
            this.chart.destroy();
        }
        
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Portfolio Value',
                    data: chartData.values,
                    borderColor: '#60a5fa',
                    backgroundColor: 'rgba(96, 165, 250, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#f8fafc'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#94a3b8'
                        },
                        grid: {
                            color: '#334155'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        },
                        grid: {
                            color: '#334155'
                        }
                    }
                }
            }
        });
    }

    generateChartData() {
        const days = 30;
        const labels = [];
        const values = [];
        const currentValue = this.data.portfolio.value;
        
        const startingValue = 95000;
        const totalChange = currentValue - startingValue;
        
        for (let i = days; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            
            const dayProgress = (days - i) / days;
            const baseValue = startingValue + (totalChange * dayProgress);
            
            const dailyVolatilityPct = 0.012;
            const volatility = (Math.random() - 0.5) * 2 * dailyVolatilityPct * baseValue;
            
            if (i === 0) {
                values.push(Math.round(currentValue));
            } else {
                values.push(Math.round(baseValue + volatility));
            }
        }
        
        return { labels, values };
    }

    filterPositions(filter) {
        const rows = document.querySelectorAll('.position-row');
        
        rows.forEach(row => {
            const shouldShow = filter === 'all' || row.classList.contains(filter);
            row.style.display = shouldShow ? '' : 'none';
        });
    }

    updateLastSync() {
        const now = new Date().toLocaleString();
        document.getElementById('last-updated').textContent = `Last updated: ${now}`;
        document.getElementById('footer-sync-time').textContent = now;
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 5 * 60 * 1000);
        
        console.log('🔄 Auto-refresh started (5 minutes)');
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            console.log('⏹️ Auto-refresh stopped');
        }
    }

    showError(message) {
        console.error(message);
    }

    async loadEnhancedMockData() {
        this.data = this.generateEnhancedMockData();
        this.updateHeaderStats();
        this.updatePerformanceMetrics();
        this.updatePositionsTable();
        this.updateTradesTable();
        this.updateStrategyPerformance();
        this.updateIntradayStatus();
        this.updatePortfolioChart();
        this.updateMLAuditTrail();
        this.updateMLModelStatus();
        this.updateLastSync();
    }
}

// Add custom styles for ML indicators
const style = document.createElement('style');
style.textContent = `
    .ml-score {
        display: inline-block;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        color: white;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    
    .ml-decision-indicator {
        display: inline-block;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.7rem;
        margin-left: 0.5rem;
    }
    
    .strategy-tag.ml-strategy {
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .ml-badge {
        display: inline-block;
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    
    .ml-decision-confidence.high {
        background-color: var(--success-color);
    }
    
    .ml-decision-confidence.medium {
        background-color: var(--warning-color);
    }
    
    .ml-decision-confidence.low {
        background-color: var(--danger-color);
    }
`;
document.head.appendChild(style);

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new TradingDashboard();
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TradingDashboard;
}