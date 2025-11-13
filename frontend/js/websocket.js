// WebSocket Manager
class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = CONFIG.WS_RECONNECT_ATTEMPTS;
        this.reconnectDelay = CONFIG.WS_RECONNECT_DELAY;
        this.listeners = [];
        this.isConnecting = false;
    }

    connect() {
        if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
            return;
        }

        this.isConnecting = true;

        try {
            const wsUrl = `${CONFIG.WS_URL}${CONFIG.ENDPOINTS.MARKET_STREAM}`;
            console.log('Connecting to WebSocket:', wsUrl);

            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('✅ WebSocket connected');
                this.isConnecting = false;
                this.reconnectAttempts = 0;
                this.updateStatus('connected', 'Connected');
                this.notifyListeners('connected', null);
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.notifyListeners('message', data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnecting = false;
                this.updateStatus('disconnected', 'Connection Error');
            };

            this.ws.onclose = () => {
                console.log('❌ WebSocket disconnected');
                this.isConnecting = false;
                this.updateStatus('disconnected', 'Disconnected');
                this.notifyListeners('disconnected', null);

                // Attempt to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`Reconnecting... (Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                    setTimeout(() => this.connect(), this.reconnectDelay);
                } else {
                    this.updateStatus('disconnected', 'Connection Failed');
                    showToast('WebSocket connection failed. Please refresh the page.', 'error');
                }
            };
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            this.isConnecting = false;
            this.updateStatus('disconnected', 'Connection Failed');
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }

    addListener(callback) {
        this.listeners.push(callback);
    }

    removeListener(callback) {
        this.listeners = this.listeners.filter(listener => listener !== callback);
    }

    notifyListeners(event, data) {
        this.listeners.forEach(callback => {
            try {
                callback(event, data);
            } catch (error) {
                console.error('Error in WebSocket listener:', error);
            }
        });
    }

    updateStatus(status, text) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');

        if (statusDot) {
            statusDot.className = `status-dot ${status}`;
        }

        if (statusText) {
            statusText.textContent = text;
        }
    }
}

// Create global WebSocket manager
const wsManager = new WebSocketManager();

// Market data handler
let previousPrices = {};

function handleMarketUpdate(data) {
    if (!data.markets || data.markets.length === 0) {
        return;
    }

    // Update last update time
    const lastUpdate = document.getElementById('lastUpdate');
    if (lastUpdate) {
        lastUpdate.textContent = new Date().toLocaleTimeString();
    }

    // Update market cards
    data.markets.forEach(market => {
        updateMarketCard(market);
    });
}

function updateMarketCard(market) {
    // Update dashboard markets
    updateMarketCardInContainer('dashboardMarkets', market);

    // Update markets page
    updateMarketCardInContainer('marketsGrid', market);
}

function updateMarketCardInContainer(containerId, market) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Remove "no data" message
    const noData = container.querySelector('.no-data');
    if (noData) {
        noData.remove();
    }

    const cardId = `market-${market.id}-${containerId}`;
    let card = document.getElementById(cardId);

    const currentPrice = parseFloat(market.price);
    const previousPrice = previousPrices[market.symbol] || currentPrice;
    const priceChange = currentPrice - previousPrice;
    const priceChangePercent = previousPrice !== 0
        ? ((priceChange / previousPrice) * 100).toFixed(2)
        : 0;

    if (!card) {
        // Create new card
        card = document.createElement('div');
        card.id = cardId;
        card.className = 'market-card';
        container.appendChild(card);
    } else {
        // Add animation class
        card.className = 'market-card';
        if (priceChange > 0) {
            card.classList.add('price-up');
        } else if (priceChange < 0) {
            card.classList.add('price-down');
        }
    }

    // Update card content
    card.innerHTML = `
        <div class="market-header">
            <div class="symbol">${market.symbol}</div>
            <div class="price-badge ${priceChange >= 0 ? 'up' : 'down'}">
                ${priceChange >= 0 ? '▲' : '▼'} ${Math.abs(priceChangePercent)}%
            </div>
        </div>
        <div class="price">$${currentPrice.toLocaleString('en-US', CONFIG.CURRENCY_FORMAT)}</div>
        <div class="price-change ${priceChange >= 0 ? 'positive' : 'negative'}">
            <span class="arrow">${priceChange >= 0 ? '↑' : '↓'}</span>
            <span>$${Math.abs(priceChange).toLocaleString('en-US', CONFIG.CURRENCY_FORMAT)}</span>
        </div>
        <div class="market-info">
            <span>ID: ${market.id}</span>
            <span>Live Updates</span>
        </div>
    `;

    // Log significant price changes (only if price actually changed)
    if (previousPrice !== currentPrice && previousPrices[market.symbol] !== undefined) {
        const direction = priceChange > 0 ? 'increased' : 'decreased';
        const changeAmount = Math.abs(priceChange).toFixed(2);
        addLogEntry(`${market.symbol} ${direction} by $${changeAmount} (${priceChangePercent}%)`, priceChange > 0);
    }

    // Store current price for next comparison
    previousPrices[market.symbol] = currentPrice;
}

// Add log entry function
function addLogEntry(message, isPositive = null) {
    const updateLog = document.getElementById('updateLog');
    if (!updateLog) return;

    // Remove "no data" message
    const noData = updateLog.querySelector('.no-data');
    if (noData) {
        noData.remove();
    }

    const now = new Date();
    const timeString = now.toLocaleTimeString();

    const entry = document.createElement('div');
    entry.className = 'log-entry';

    const messageClass = isPositive === null ? '' : (isPositive ? 'positive' : 'negative');

    entry.innerHTML = `
        <div class="log-time">${timeString}</div>
        <div class="log-message ${messageClass}">${message}</div>
    `;

    // Insert at the top
    updateLog.insertBefore(entry, updateLog.firstChild);

    // Keep only last 50 entries
    while (updateLog.children.length > 50) {
        updateLog.removeChild(updateLog.lastChild);
    }
}

// Listen to WebSocket events
wsManager.addListener((event, data) => {
    if (event === 'message') {
        handleMarketUpdate(data);
    } else if (event === 'connected') {
        addLogEntry('✅ Connected to market stream - Price updates starting...', null);
    } else if (event === 'disconnected') {
        addLogEntry('❌ Disconnected from market stream', null);
    }
});

// Add initial log entry when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing logs...');
    const updateLog = document.getElementById('updateLog');
    if (updateLog) {
        console.log('updateLog element found');
        addLogEntry('🔄 Initializing market stream connection...', null);
    } else {
        console.log('updateLog element NOT found');
    }
});
