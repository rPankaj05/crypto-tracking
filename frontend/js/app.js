// Main Application Controller

class CryptoTrackerApp {
    constructor() {
        this.markets = [];
        this.updateInterval = null;
        this.init();
    }

    async init() {
        console.log('🚀 Initializing Crypto Tracker App...');

        // Initialize WebSocket connection
        wsManager.connect();

        // Setup event listeners
        this.setupEventListeners();

        // Load initial data if authenticated
        if (authManager.isAuthenticated()) {
            await this.loadInitialData();
            this.startPeriodicUpdates();
        }

        console.log('✅ App initialized');
    }

    setupEventListeners() {
        // Refresh buttons
        document.getElementById('refreshMarketsBtn')?.addEventListener('click', () => {
            loadMarkets();
        });

        document.getElementById('refreshPortfolioBtn')?.addEventListener('click', () => {
            loadPortfolio();
        });

        // Market management buttons
        document.getElementById('addMarketBtn')?.addEventListener('click', () => {
            this.showMarketForm();
        });

        document.getElementById('cancelMarketBtn')?.addEventListener('click', () => {
            this.hideMarketForm();
        });

        document.getElementById('marketForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleAddMarket();
        });

        // Trade form
        const tradeForm = document.getElementById('tradeForm');
        if (tradeForm) {
            tradeForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleTrade();
            });

            // Update total when price or quantity changes
            document.getElementById('tradePrice')?.addEventListener('input', () => this.updateTradeTotal());
            document.getElementById('tradeQuantity')?.addEventListener('input', () => this.updateTradeTotal());

            // Auto-fill price when market is selected
            document.getElementById('tradeSymbol')?.addEventListener('change', (e) => {
                const selectedOption = e.target.options[e.target.selectedIndex];
                const price = selectedOption.dataset.price;
                if (price) {
                    document.getElementById('tradePrice').value = price;
                    this.updateTradeTotal();
                    this.updateMarketInfo(e.target.value);
                }
            });
        }

        // Alert form
        document.getElementById('createAlertBtn')?.addEventListener('click', () => {
            this.showAlertForm();
        });

        document.getElementById('cancelAlertBtn')?.addEventListener('click', () => {
            this.hideAlertForm();
        });

        document.getElementById('alertForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCreateAlert();
        });

        // Alert tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                loadAlerts(btn.dataset.tab === 'active');
            });
        });
    }

    async loadInitialData() {
        try {
            // Load markets for trade page
            this.markets = await api.getAllMarkets();

            // Load dashboard data
            loadDashboard();
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    startPeriodicUpdates() {
        // Update portfolio and dashboard data periodically
        this.updateInterval = setInterval(() => {
            if (authManager.isAuthenticated()) {
                const currentPage = pageNavigator.currentPage;
                if (currentPage === 'dashboard') {
                    loadDashboard();
                } else if (currentPage === 'portfolio') {
                    loadPortfolio();
                }
            }
        }, CONFIG.PORTFOLIO_UPDATE_INTERVAL);
    }

    stopPeriodicUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    updateTradeTotal() {
        const price = parseFloat(document.getElementById('tradePrice')?.value || 0);
        const quantity = parseFloat(document.getElementById('tradeQuantity')?.value || 0);
        const total = price * quantity;

        const totalElement = document.getElementById('tradeTotal');
        if (totalElement) {
            totalElement.textContent = formatCurrency(total);
        }
    }

    async updateMarketInfo(symbol) {
        const infoContainer = document.getElementById('selectedMarketInfo');
        if (!symbol || !infoContainer) return;

        try {
            const market = await api.getMarketBySymbol(symbol);
            infoContainer.innerHTML = `
                <div class="info-item">
                    <span class="info-label">Symbol:</span>
                    <span class="info-value">${market.symbol}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Current Price:</span>
                    <span class="info-value">${formatCurrency(market.current_price)}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Market ID:</span>
                    <span class="info-value">${market.id}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Last Updated:</span>
                    <span class="info-value">${formatDate(market.updated_at)}</span>
                </div>
            `;
        } catch (error) {
            console.error('Error loading market info:', error);
            infoContainer.innerHTML = '<p class="no-data">Failed to load market info</p>';
        }
    }

    async handleTrade() {
        const userId = authManager.getUserId();
        if (!userId) {
            showToast('Please login to trade', 'warning');
            return;
        }

        const symbol = document.getElementById('tradeSymbol').value;
        const type = document.getElementById('tradeType').value;
        const price = parseFloat(document.getElementById('tradePrice').value);
        const quantity = parseFloat(document.getElementById('tradeQuantity').value);
        const errorElement = document.getElementById('tradeError');

        if (!symbol || !type || !price || !quantity) {
            errorElement.textContent = 'Please fill in all fields';
            return;
        }

        try {
            showLoading();
            errorElement.textContent = '';

            const result = await api.executeTrade({
                user_id: parseInt(userId),
                symbol,
                type,
                price,
                quantity
            });

            showToast(result.message, 'success');

            // Reset form
            document.getElementById('tradeForm').reset();
            document.getElementById('tradeTotal').textContent = '$0.00';
            document.getElementById('selectedMarketInfo').innerHTML = '<p class="no-data">Select a market to see details</p>';

            // Refresh portfolio and dashboard
            await loadPortfolio();
            await loadDashboard();

            // Update current user balance
            await authManager.loadCurrentUser();
        } catch (error) {
            console.error('Error executing trade:', error);
            errorElement.textContent = error.message || 'Trade execution failed';
            showToast('Trade failed: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    showAlertForm() {
        const formContainer = document.getElementById('alertFormContainer');
        formContainer.style.display = 'block';

        // Load markets for alert selector
        this.loadAlertMarkets();
    }

    hideAlertForm() {
        const formContainer = document.getElementById('alertFormContainer');
        formContainer.style.display = 'none';
        document.getElementById('alertForm').reset();
        document.getElementById('alertError').textContent = '';
    }

    async loadAlertMarkets() {
        try {
            const markets = await api.getAllMarkets();
            const select = document.getElementById('alertSymbol');
            select.innerHTML = '<option value="">Select a market</option>' +
                markets.map(market => `
                    <option value="${market.symbol}">
                        ${market.symbol} - $${parseFloat(market.current_price).toLocaleString('en-US', CONFIG.CURRENCY_FORMAT)}
                    </option>
                `).join('');
        } catch (error) {
            console.error('Error loading markets for alerts:', error);
        }
    }

    async handleCreateAlert() {
        const userId = authManager.getUserId();
        if (!userId) {
            showToast('Please login to create alerts', 'warning');
            return;
        }

        const symbol = document.getElementById('alertSymbol').value;
        const direction = document.getElementById('alertDirection').value;
        const targetPrice = parseFloat(document.getElementById('alertPrice').value);
        const errorElement = document.getElementById('alertError');

        if (!symbol || !direction || !targetPrice) {
            errorElement.textContent = 'Please fill in all fields';
            return;
        }

        try {
            showLoading();
            errorElement.textContent = '';

            await api.createAlert({
                user_id: parseInt(userId),
                symbol,
                direction,
                target_price: targetPrice
            });

            showToast('Alert created successfully', 'success');

            // Hide form and reload alerts
            this.hideAlertForm();
            loadAlerts(true);
            loadDashboard(); // Update alert count
        } catch (error) {
            console.error('Error creating alert:', error);
            errorElement.textContent = error.message || 'Failed to create alert';
            showToast('Failed to create alert: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    showMarketForm() {
        const formContainer = document.getElementById('marketFormContainer');
        formContainer.style.display = 'block';
    }

    hideMarketForm() {
        const formContainer = document.getElementById('marketFormContainer');
        formContainer.style.display = 'none';
        document.getElementById('marketForm').reset();
        document.getElementById('marketError').textContent = '';
    }

    async handleAddMarket() {
        if (!authManager.isAuthenticated()) {
            showToast('Please login to add markets', 'warning');
            return;
        }

        const symbol = document.getElementById('marketSymbol').value.trim().toUpperCase();
        const price = parseFloat(document.getElementById('marketPrice').value);
        const errorElement = document.getElementById('marketError');

        if (!symbol || !price) {
            errorElement.textContent = 'Please fill in all fields';
            return;
        }

        try {
            showLoading();
            errorElement.textContent = '';

            await api.createOrUpdateMarket({
                symbol,
                price
            });

            showToast('Market added successfully', 'success');

            // Hide form and reload markets
            this.hideMarketForm();
            loadMarkets();
        } catch (error) {
            console.error('Error adding market:', error);
            errorElement.textContent = error.message || 'Failed to add market';
            showToast('Failed to add market: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    cleanup() {
        this.stopPeriodicUpdates();
        wsManager.disconnect();
    }
}

// Initialize app when DOM is ready
let app = null;

document.addEventListener('DOMContentLoaded', () => {
    app = new CryptoTrackerApp();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (app) {
        app.cleanup();
    }
});

// Handle visibility change to pause/resume updates
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        if (app) {
            app.stopPeriodicUpdates();
        }
    } else {
        if (app && authManager.isAuthenticated()) {
            app.startPeriodicUpdates();
        }
    }
});
