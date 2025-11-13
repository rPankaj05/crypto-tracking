// API Configuration
const CONFIG = {
    // API Base URL - Can be changed via settings
    API_BASE_URL: localStorage.getItem('apiBaseUrl') || 'http://localhost:8000',

    // WebSocket URL
    get WS_URL() {
        const apiUrl = localStorage.getItem('apiBaseUrl') || 'http://localhost:8000';
        return apiUrl.replace('http://', 'ws://').replace('https://', 'wss://');
    },

    // API Endpoints
    ENDPOINTS: {
        // Auth
        REGISTER: '/api/auth/register',
        LOGIN: '/api/auth/login',
        ME: '/api/auth/me',

        // Markets
        MARKETS: '/api/markets/',
        MARKET_BY_SYMBOL: '/api/markets/symbol',

        // Holdings/Trading
        TRADE: '/api/holdings/trade/',
        USER_HOLDINGS: '/api/holdings/user',

        // Portfolio
        PORTFOLIO: '/api/users',

        // Alerts
        ALERTS: '/api/alerts/',
        USER_ALERTS: '/api/alerts/user',
        ACTIVE_ALERTS: '/api/alerts/user',

        // WebSocket
        MARKET_STREAM: '/ws/market-stream'
    },

    // WebSocket settings
    WS_RECONNECT_ATTEMPTS: 5,
    WS_RECONNECT_DELAY: 3000,

    // Update intervals
    PORTFOLIO_UPDATE_INTERVAL: 10000, // 10 seconds

    // Formats
    CURRENCY_FORMAT: {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    },

    CRYPTO_FORMAT: {
        minimumFractionDigits: 2,
        maximumFractionDigits: 8
    }
};

// Update API base URL
function updateApiBaseUrl(newUrl) {
    localStorage.setItem('apiBaseUrl', newUrl);
    CONFIG.API_BASE_URL = newUrl;
    window.location.reload();
}
