// UI Helper Functions

// Show loading overlay
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = {
        success: '✓',
        error: '✗',
        warning: '⚠',
        info: 'ℹ'
    }[type] || 'ℹ';

    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Remove after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 5000);
}

// Format currency
function formatCurrency(value) {
    return `$${parseFloat(value).toLocaleString('en-US', CONFIG.CURRENCY_FORMAT)}`;
}

// Format crypto amount
function formatCrypto(value) {
    return parseFloat(value).toLocaleString('en-US', CONFIG.CRYPTO_FORMAT);
}

// Format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

// Page Navigation
class PageNavigator {
    constructor() {
        this.currentPage = 'dashboard';
        this.init();
    }

    init() {
        // Setup navigation links
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                this.navigateTo(page);
            });
        });

        // Show initial page
        this.navigateTo(this.currentPage);
    }

    navigateTo(pageName) {
        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page === pageName) {
                link.classList.add('active');
            }
        });

        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });

        // Show selected page
        const pageElement = document.getElementById(`${pageName}Page`);
        if (pageElement) {
            pageElement.classList.add('active');
            this.currentPage = pageName;

            // Load page data
            this.loadPageData(pageName);
        }
    }

    loadPageData(pageName) {
        // Markets can be viewed without login
        if (pageName === 'markets') {
            loadMarkets();
            return;
        }

        // Other pages require authentication
        if (!authManager.isAuthenticated()) {
            if (pageName !== 'dashboard') {
                showToast('Please login to access this page', 'warning');
            }
            return;
        }

        switch (pageName) {
            case 'portfolio':
                loadPortfolio();
                break;
            case 'trade':
                loadTradePageData();
                break;
            case 'alerts':
                loadAlerts();
                break;
            case 'dashboard':
                loadDashboard();
                break;
        }
    }
}

// Dashboard loader
async function loadDashboard() {
    if (!authManager.isAuthenticated()) return;

    const userId = authManager.getUserId();

    try {
        // Load portfolio for quick stats
        const portfolio = await api.getPortfolio(userId);

        // Update quick stats
        document.getElementById('statBalance').textContent = formatCurrency(portfolio.balance);
        document.getElementById('statPortfolio').textContent = formatCurrency(portfolio.total_value);

        // Calculate total P&L
        let totalPnL = 0;
        portfolio.holdings.forEach(holding => {
            totalPnL += parseFloat(holding.unrealized_pnl);
        });

        const pnlElement = document.getElementById('statPnL');
        pnlElement.textContent = formatCurrency(totalPnL);
        pnlElement.className = `stat-value ${totalPnL >= 0 ? 'positive' : 'negative'}`;

        // Load active alerts count
        const alerts = await api.getActiveAlerts(userId);
        document.getElementById('statAlerts').textContent = alerts.length;
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Markets loader
async function loadMarkets() {
    const container = document.getElementById('marketsGrid');

    // Markets are updated via WebSocket, so just wait for data
    // If user is logged in, we can also fetch from API
    if (authManager.isAuthenticated()) {
        try {
            showLoading();
            const markets = await api.getAllMarkets();

            // Remove "no data" message if it exists
            const noData = container.querySelector('.no-data');
            if (noData) {
                noData.remove();
            }

            if (markets.length === 0) {
                container.innerHTML = '<div class="no-data">No markets available. Waiting for WebSocket data...</div>';
            } else {
                // Just ensure cards exist - let WebSocket populate the content
                markets.forEach(market => {
                    const cardId = `market-${market.id}-marketsGrid`;
                    let card = document.getElementById(cardId);

                    if (!card) {
                        // Create new empty card shell only if it doesn't exist
                        card = document.createElement('div');
                        card.id = cardId;
                        card.className = 'market-card';
                        card.innerHTML = '<div class="no-data">Loading market data...</div>';
                        container.appendChild(card);

                        // WebSocket will populate it soon, but trigger a manual update with current data
                        setTimeout(() => {
                            updateMarketCardInContainer('marketsGrid', {
                                id: market.id,
                                symbol: market.symbol,
                                price: market.current_price
                            });
                        }, 100);
                    }
                });
            }
        } catch (error) {
            console.error('Error loading markets:', error);
            if (container.children.length === 0) {
                container.innerHTML = '<div class="no-data">Loading markets via WebSocket...</div>';
            }
        } finally {
            hideLoading();
        }
    } else {
        // Not logged in - markets will be populated by WebSocket
        container.innerHTML = '<div class="no-data">Connecting to market stream...</div>';
    }
}

// Portfolio loader
async function loadPortfolio() {
    const userId = authManager.getUserId();
    if (!userId) return;

    try {
        showLoading();
        const portfolio = await api.getPortfolio(userId);

        // Update summary
        document.getElementById('portfolioBalance').textContent = formatCurrency(portfolio.balance);
        document.getElementById('portfolioTotal').textContent = formatCurrency(portfolio.total_value);

        // Update holdings table
        const tbody = document.getElementById('holdingsTableBody');

        if (portfolio.holdings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="no-data">No holdings yet</td></tr>';
            return;
        }

        tbody.innerHTML = portfolio.holdings.map(holding => {
            const value = parseFloat(holding.current_price) * parseFloat(holding.quantity);
            const pnl = parseFloat(holding.unrealized_pnl);
            const pnlClass = pnl >= 0 ? 'positive' : 'negative';

            return `
                <tr>
                    <td><strong>${holding.symbol}</strong></td>
                    <td>${formatCrypto(holding.quantity)}</td>
                    <td>${formatCurrency(holding.avg_buy_price)}</td>
                    <td>${formatCurrency(holding.current_price)}</td>
                    <td>${formatCurrency(value)}</td>
                    <td class="${pnlClass}">${formatCurrency(pnl)}</td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading portfolio:', error);
        showToast('Failed to load portfolio', 'error');
    } finally {
        hideLoading();
    }
}

// Trade page data loader
async function loadTradePageData() {
    try {
        const markets = await api.getAllMarkets();

        // Populate market selector
        const select = document.getElementById('tradeSymbol');
        select.innerHTML = '<option value="">Select a market</option>' +
            markets.map(market => `
                <option value="${market.symbol}" data-price="${market.current_price}">
                    ${market.symbol} - $${parseFloat(market.current_price).toLocaleString('en-US', CONFIG.CURRENCY_FORMAT)}
                </option>
            `).join('');
    } catch (error) {
        console.error('Error loading trade page data:', error);
        showToast('Failed to load markets', 'error');
    }
}

// Alerts loader
async function loadAlerts(activeOnly = true) {
    const userId = authManager.getUserId();
    if (!userId) return;

    try {
        showLoading();
        const alerts = activeOnly
            ? await api.getActiveAlerts(userId)
            : await api.getUserAlerts(userId);

        const tbody = document.getElementById('alertsTableBody');

        if (alerts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="no-data">No alerts yet</td></tr>';
            return;
        }

        tbody.innerHTML = alerts.map(alert => `
            <tr>
                <td><strong>${alert.market_id}</strong></td>
                <td>${alert.direction.toUpperCase()}</td>
                <td>${formatCurrency(alert.target_price)}</td>
                <td>
                    <span class="badge ${alert.triggered ? 'badge-success' : 'badge-warning'}">
                        ${alert.triggered ? 'Triggered' : 'Active'}
                    </span>
                </td>
                <td>${formatDate(alert.created_at)}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteAlert(${alert.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading alerts:', error);
        showToast('Failed to load alerts', 'error');
    } finally {
        hideLoading();
    }
}

// Delete alert function
async function deleteAlert(alertId) {
    if (!confirm('Are you sure you want to delete this alert?')) {
        return;
    }

    try {
        showLoading();
        await api.deleteAlert(alertId);
        showToast('Alert deleted successfully', 'success');

        // Reload alerts
        const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
        loadAlerts(activeTab === 'active');
    } catch (error) {
        console.error('Error deleting alert:', error);
        showToast('Failed to delete alert', 'error');
    } finally {
        hideLoading();
    }
}

// Initialize page navigator
const pageNavigator = new PageNavigator();
