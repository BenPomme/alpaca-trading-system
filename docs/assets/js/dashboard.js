// Alpaca Trading Dashboard JavaScript
class TradingDashboard {
    constructor() {
        this.data = {
            portfolio: null,
            positions: [],
            trades: [],
            performance: null,
            strategies: []
        };
        this.chart = null;
        this.refreshInterval = null;
        this.init();
    }

    async init() {
        console.log('🚀 Initializing Trading Dashboard...');
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

        // Manual refresh (could add a button)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.loadDashboardData();
            }
        });
    }

    async loadDashboardData() {
        try {
            console.log('📊 Loading dashboard data...');
            document.body.classList.add('loading');

            // Since we can't directly access the SQLite database from the browser,
            // we'll use a combination of approaches:
            // 1. Try to fetch from a local API endpoint (if available)
            // 2. Use mock data for demo purposes
            // 3. Later, we'll create a simple API endpoint

            const data = await this.fetchTradingData();
            this.data = data;

            this.updateHeaderStats();
            this.updatePerformanceMetrics();
            this.updatePositionsTable();
            this.updateTradesTable();
            this.updateStrategyPerformance();
            this.updateIntradayStatus();
            this.updatePortfolioChart();

            this.updateLastSync();
            console.log('✅ Dashboard data loaded successfully');

        } catch (error) {
            console.error('❌ Error loading dashboard data:', error);
            this.showError('Failed to load trading data. Using demo data.');
            await this.loadMockData();
        } finally {
            document.body.classList.remove('loading');
        }
    }

    async fetchTradingData() {
        // Try to fetch from local API endpoint first
        try {
            const response = await fetch('/api/dashboard-data.json');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.log('Local API not available, using mock data');
        }

        // If no API available, generate realistic mock data based on current system
        return this.generateMockData();
    }

    generateMockData() {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        
        return {
            portfolio: {
                value: 99071.57,
                cash: 24532.57,
                dayTradingPower: 222926.24,
                dailyPL: -428.43,
                dailyPLPercent: -0.43
            },
            positions: [
                {
                    symbol: 'AAPL',
                    quantity: 14,
                    entryPrice: 198.5,
                    currentPrice: 200.11,
                    marketValue: 2801.54,
                    unrealizedPL: 22.54,
                    unrealizedPLPercent: 0.81,
                    holdTime: '2.3h',
                    strategy: 'momentum',
                    type: 'stock'
                },
                {
                    symbol: 'BTCUSD',
                    quantity: 0.0665,
                    entryPrice: 46000,
                    currentPrice: 45000,
                    marketValue: 7011.76,
                    unrealizedPL: -110.42,
                    unrealizedPLPercent: -1.55,
                    holdTime: '1.2d',
                    strategy: 'crypto_momentum',
                    type: 'crypto'
                },
                {
                    symbol: 'MSFT',
                    quantity: 6,
                    entryPrice: 459.5,
                    currentPrice: 458.24,
                    marketValue: 2749.44,
                    unrealizedPL: -7.56,
                    unrealizedPLPercent: -0.27,
                    holdTime: '4.1h',
                    strategy: 'aggressive_momentum',
                    type: 'stock'
                }
            ],
            trades: [
                {
                    date: '2025-05-30 14:23:15',
                    symbol: 'NVDA',
                    side: 'SELL',
                    quantity: 7,
                    price: 138.16,
                    pl: 18.51,
                    plPercent: 1.35,
                    strategy: 'momentum',
                    exitReason: 'profit_protection'
                },
                {
                    date: '2025-05-30 13:45:22',
                    symbol: 'SPY',
                    side: 'BUY',
                    quantity: 1,
                    price: 589.01,
                    pl: 0,
                    plPercent: 0,
                    strategy: 'conservative',
                    exitReason: null
                }
            ],
            performance: {
                totalTrades: 156,
                winningTrades: 89,
                losingTrades: 67,
                winRate: 57.05,
                avgHoldTime: 6.2,
                bestTrade: 245.67,
                worstTrade: -89.23,
                totalROI: 12.34,
                dailyROI: 0.43,
                weeklyROI: 2.87,
                monthlyROI: 8.91
            },
            strategies: [
                {
                    name: 'aggressive_momentum',
                    trades: 45,
                    winRate: 62.2,
                    avgReturn: 2.8,
                    totalReturn: 126.4
                },
                {
                    name: 'momentum',
                    trades: 67,
                    winRate: 55.2,
                    avgReturn: 1.9,
                    totalReturn: 127.3
                },
                {
                    name: 'crypto_momentum',
                    trades: 23,
                    winRate: 65.2,
                    avgReturn: 3.4,
                    totalReturn: 78.2
                },
                {
                    name: 'conservative',
                    trades: 21,
                    winRate: 47.6,
                    avgReturn: 1.2,
                    totalReturn: 25.2
                }
            ],
            marketStatus: {
                isOpen: false,
                nextOpen: '2025-05-30 09:30:00 ET',
                nextClose: '2025-05-30 16:00:00 ET'
            }
        };
    }

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
            
            row.innerHTML = `
                <td><strong>${position.symbol}</strong></td>
                <td>${position.quantity}</td>
                <td>$${position.entryPrice.toFixed(2)}</td>
                <td>$${position.currentPrice.toFixed(2)}</td>
                <td class="${plClass}">$${position.unrealizedPL.toFixed(2)}</td>
                <td class="${plClass}">${plPercent}${position.unrealizedPLPercent.toFixed(2)}%</td>
                <td>${position.holdTime}</td>
                <td><span class="strategy-tag">${position.strategy}</span></td>
            `;
            
            tbody.appendChild(row);
        });
    }

    updateTradesTable() {
        const tbody = document.getElementById('trades-tbody');
        tbody.innerHTML = '';

        // Show recent trades (last 20)
        const recentTrades = this.data.trades.slice(-20).reverse();
        
        recentTrades.forEach(trade => {
            const row = document.createElement('tr');
            const plClass = trade.pl >= 0 ? 'positive' : 'negative';
            const plSign = trade.pl >= 0 ? '+' : '';
            
            row.innerHTML = `
                <td>${new Date(trade.date).toLocaleString()}</td>
                <td><strong>${trade.symbol}</strong></td>
                <td><span class="side-${trade.side.toLowerCase()}">${trade.side}</span></td>
                <td>${trade.quantity}</td>
                <td>$${trade.price.toFixed(2)}</td>
                <td class="${plClass}">${plSign}$${trade.pl.toFixed(2)}</td>
                <td><span class="strategy-tag">${trade.strategy}</span></td>
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
            
            strategyDiv.innerHTML = `
                <div class="strategy-name">${strategy.name.replace('_', ' ').toUpperCase()}</div>
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
        
        // Generate mock chart data for the last 30 days
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
        
        for (let i = days; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString());
            
            // Generate realistic portfolio growth with some volatility
            const dayProgress = (days - i) / days;
            const baseGrowth = currentValue * (0.95 + dayProgress * 0.15); // 5% to 10% growth
            const volatility = (Math.random() - 0.5) * 0.02 * currentValue; // ±2% daily volatility
            values.push(Math.round(baseGrowth + volatility));
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
        // Refresh every 5 minutes
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
        // Could add a toast notification here
    }

    async loadMockData() {
        this.data = this.generateMockData();
        this.updateHeaderStats();
        this.updatePerformanceMetrics();
        this.updatePositionsTable();
        this.updateTradesTable();
        this.updateStrategyPerformance();
        this.updateIntradayStatus();
        this.updatePortfolioChart();
        this.updateLastSync();
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new TradingDashboard();
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TradingDashboard;
}