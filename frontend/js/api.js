// API Service Layer
class APIService {
    constructor() {
        this.baseUrl = CONFIG.API_BASE_URL;
    }

    // Get auth token from localStorage
    getToken() {
        return localStorage.getItem('access_token');
    }

    // Get current user ID from localStorage
    getUserId() {
        return localStorage.getItem('user_id');
    }

    // Build headers with authentication
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (includeAuth) {
            const token = this.getToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        return headers;
    }

    // Generic fetch wrapper with error handling
    async fetch(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                headers: this.getHeaders(options.auth !== false)
            });

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication APIs
    async register(userData) {
        return this.fetch(CONFIG.ENDPOINTS.REGISTER, {
            method: 'POST',
            body: JSON.stringify(userData),
            auth: false
        });
    }

    async login(credentials) {
        const data = await this.fetch(CONFIG.ENDPOINTS.LOGIN, {
            method: 'POST',
            body: JSON.stringify(credentials),
            auth: false
        });

        // Store tokens
        if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
        }

        return data;
    }

    async getCurrentUser() {
        const user = await this.fetch(CONFIG.ENDPOINTS.ME);
        if (user.id) {
            localStorage.setItem('user_id', user.id);
        }
        return user;
    }

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('current_user');
        window.location.reload();
    }

    // Markets APIs
    async getAllMarkets() {
        return this.fetch(CONFIG.ENDPOINTS.MARKETS);
    }

    async getMarketBySymbol(symbol) {
        return this.fetch(`${CONFIG.ENDPOINTS.MARKET_BY_SYMBOL}?symbol=${encodeURIComponent(symbol)}`);
    }

    async createOrUpdateMarket(marketData) {
        return this.fetch(CONFIG.ENDPOINTS.MARKETS, {
            method: 'POST',
            body: JSON.stringify(marketData)
        });
    }

    async updateMarketPrice(symbol, price) {
        return this.fetch(`${CONFIG.ENDPOINTS.MARKETS}?symbol=${encodeURIComponent(symbol)}`, {
            method: 'PUT',
            body: JSON.stringify({ price })
        });
    }

    // Trading APIs
    async executeTrade(tradeData) {
        return this.fetch(CONFIG.ENDPOINTS.TRADE, {
            method: 'POST',
            body: JSON.stringify(tradeData)
        });
    }

    async getUserHoldings(userId) {
        return this.fetch(`${CONFIG.ENDPOINTS.USER_HOLDINGS}/${userId}`);
    }

    // Portfolio APIs
    async getPortfolio(userId) {
        return this.fetch(`${CONFIG.ENDPOINTS.PORTFOLIO}/${userId}/portfolio`);
    }

    // Alerts APIs
    async createAlert(alertData) {
        return this.fetch(CONFIG.ENDPOINTS.ALERTS, {
            method: 'POST',
            body: JSON.stringify(alertData)
        });
    }

    async getUserAlerts(userId) {
        return this.fetch(`${CONFIG.ENDPOINTS.USER_ALERTS}/${userId}`);
    }

    async getActiveAlerts(userId) {
        return this.fetch(`${CONFIG.ENDPOINTS.ACTIVE_ALERTS}/${userId}/active`);
    }

    async deleteAlert(alertId) {
        return this.fetch(`${CONFIG.ENDPOINTS.ALERTS}${alertId}`, {
            method: 'DELETE'
        });
    }

    // Health check
    async healthCheck() {
        return this.fetch('/health', { auth: false });
    }
}

// Create global API instance
const api = new APIService();
