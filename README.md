# 🚀 Crypto Market Alert & Portfolio Tracker Backend

A backend service for tracking cryptocurrency prices, managing virtual portfolios, and setting price alerts with real-time updates.


## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (for Docker method)
- Python 3.11+ and Redis (for local development)

### Option 1: Docker Compose (Recommended)

#### 1. Clone and navigate to project
```bash
git clone <repository-url>
cd crypto-tracker
```

#### 2. Create `.env` file
```bash
cp .env.example .env
```

#### 3. Start all services
```bash
docker-compose up --build
```

This will start:
- **API Server** on `http://localhost:8000`
- **Dashboard Server** on `http://localhost:3000`
- **Redis** on `localhost:6379`
- **Celery Worker** for background tasks
- **Celery Beat** for scheduled tasks

#### 4. Seed the database (in another terminal)
```bash
docker-compose exec api python seed_data.py
```

### Option 2: Local Development

#### 1. Clone the repository
```bash
git clone <repository-url>
cd crypto-tracker
```

#### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Create `.env` file
```bash
cp .env.example .env
# Edit .env with your configuration
```

#### 5. Initialize database with seed data
```bash
python seed_data.py
```

#### 6. Start Redis server
```bash
redis-server
```

#### 7. Start FastAPI server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 8. Start Celery worker (in new terminal)
```bash
celery -A app.celery_app worker --loglevel=info
```

#### 9. Start Celery beat scheduler (in new terminal)
```bash
celery -A app.celery_app beat --loglevel=info
```

---

## 📋 Features

### ✅ Core Features
- **User Authentication** - JWT-based authentication with access and refresh tokens
- **Market Management** - Create and track multiple crypto markets with real-time price updates
- **Portfolio Management** - Buy/sell crypto assets with automatic average price calculation
- **Price Alerts** - Set alerts for price thresholds (above/below) with automatic triggering
- **Real-time Streaming** - WebSocket endpoint for live market price updates
- **Background Processing** - Celery workers for continuous price simulation and alert checking

### 🎯 Technical Highlights
- **FastAPI** framework with async support
- **SQLite** database with SQLAlchemy ORM
- **Celery + Redis** for background task processing
- **WebSocket** support for real-time data streaming
- **JWT Authentication** for secure API access
- **Docker** containerization for easy deployment
- **Unit Tests** for critical business logic
- **DECIMAL precision** to avoid floating-point errors

---

## 🏗️ Architecture

```
crypto-tracker/
├── app/
│   ├── models/          # SQLAlchemy database models
│   ├── schemas/         # Pydantic validation schemas
│   ├── routers/         # API endpoint routes
│   ├── services/        # Business logic & background tasks
│   ├── websockets/      # WebSocket handlers
│   ├── utils/           # Helper functions (auth, etc.)
│   ├── config.py        # Application configuration
│   ├── database.py      # Database connection
│   ├── celery_app.py    # Celery configuration
│   └── main.py          # FastAPI application
├── tests/               # Unit tests
├── docker-compose.yml   # Docker orchestration
├── Dockerfile           # Container definition
├── requirements.txt     # Python dependencies
└── seed_data.py         # Database seeding script
```

---

## 📡 API Documentation

### Interactive API Docs
Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword",
  "balance": 10000.0
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

### Market Endpoints

#### Create/Update Market
```http
POST /api/markets/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "symbol": "BTC/USDT",
  "price": 62000.0
}
```

#### Get All Markets
```http
GET /api/markets/
Authorization: Bearer <access_token>
```

#### Get Market by Symbol
```http
GET /api/markets/BTC/USDT
Authorization: Bearer <access_token>
```

### Trading Endpoints

#### Execute Trade (Buy/Sell)
```http
POST /api/holdings/trade/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_id": 1,
  "symbol": "BTC/USDT",
  "type": "buy",
  "price": 62000.0,
  "quantity": 0.05
}
```

#### Get User Holdings
```http
GET /api/holdings/user/1
Authorization: Bearer <access_token>
```

### Alert Endpoints

#### Create Price Alert
```http
POST /api/alerts/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_id": 1,
  "symbol": "BTC/USDT",
  "direction": "below",
  "target_price": 60000.0
}
```

#### Get User Alerts
```http
GET /api/alerts/user/1
Authorization: Bearer <access_token>
```

#### Get Active Alerts Only
```http
GET /api/alerts/user/1/active
Authorization: Bearer <access_token>
```

### Portfolio Endpoints

#### Get Portfolio Summary
```http
GET /api/users/1/portfolio
Authorization: Bearer <access_token>

Response:
{
  "balance": 4800.0,
  "holdings": [
    {
      "symbol": "BTC/USDT",
      "quantity": 0.05,
      "avg_buy_price": 61000.0,
      "current_price": 62300.0,
      "unrealized_pnl": 65.0
    }
  ],
  "total_value": 4865.0
}
```

### WebSocket Endpoint

#### Connect to Real-time Market Stream
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/market-stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Market Update:', data);
};

// Data format:
// {
//   "timestamp": 1234567890.123,
//   "markets": [
//     {"id": 1, "symbol": "BTC/USDT", "price": 62150.50},
//     {"id": 2, "symbol": "ETH/USDT", "price": 3205.75}
//   ]
// }
```

---

## 🧪 Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app tests/
```

### Run specific test file
```bash
pytest tests/test_trades.py -v
```

---


### Average Buy Price Calculation
```
New Average = ((Old Avg × Old Qty) + (New Price × New Qty)) / (Old Qty + New Qty)
```

---

## 🐛 Troubleshooting

### Redis Connection Error
Make sure Redis is running:
```bash
redis-server
```

### Celery Not Processing Tasks
Check Celery worker logs:
```bash
celery -A app.celery_app worker --loglevel=debug
```

### Database Locked Error (SQLite)
SQLite has limited concurrent access. Consider:
- Increasing timeout in database URL
- Using PostgreSQL for production

### WebSocket Connection Fails
Ensure the API server is running and accessible at the correct port.

---

## 📝 Test Credentials

After running `seed_data.py`, you can use these credentials:

```
Email: alice@example.com
Password: password123

Email: bob@example.com
Password: password123

Email: charlie@example.com
Password: password123
```

---

## 🚦 System Requirements

- **Python**: 3.11+
- **Redis**: 6.0+
- **Memory**: 512MB minimum
- **Storage**: 100MB for application + database

---

## 📦 Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start services in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart api

# Run seed script in container
docker-compose exec api python seed_data.py
```

---
