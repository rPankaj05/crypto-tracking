# API Usage Examples

This document provides curl examples for all API endpoints.

## Setup

First, start the services:
```bash
# Option 1: Local
python seed_data.py
uvicorn app.main:app --reload

# Option 2: Docker
docker-compose up -d
docker-compose exec api python seed_data.py
```

---

## 1. Authentication

### Register New User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "balance": 10000.0
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "password123"
  }'
```

**Save the access_token from response for subsequent requests!**

### Get Current User Info
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 2. Markets

### Create or Update Market
```bash
curl -X POST http://localhost:8000/api/markets/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC/USDT",
    "price": 62000.0
  }'
```

### Get All Markets
```bash
curl -X GET http://localhost:8000/api/markets/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Specific Market
```bash
curl -X GET http://localhost:8000/api/markets/BTC/USDT \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Update Market Price
```bash
curl -X PUT http://localhost:8000/api/markets/BTC/USDT \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 63500.0
  }'
```

---

## 3. Trading (Buy/Sell)

### Buy Crypto
```bash
curl -X POST http://localhost:8000/api/holdings/trade/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "symbol": "BTC/USDT",
    "type": "buy",
    "price": 62000.0,
    "quantity": 0.05
  }'
```

### Sell Crypto
```bash
curl -X POST http://localhost:8000/api/holdings/trade/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "symbol": "BTC/USDT",
    "type": "sell",
    "price": 63000.0,
    "quantity": 0.02
  }'
```

### Get User Holdings
```bash
curl -X GET http://localhost:8000/api/holdings/user/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 4. Price Alerts

### Create Alert (Price Below)
```bash
curl -X POST http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "symbol": "BTC/USDT",
    "direction": "below",
    "target_price": 60000.0
  }'
```

### Create Alert (Price Above)
```bash
curl -X POST http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "symbol": "ETH/USDT",
    "direction": "above",
    "target_price": 3500.0
  }'
```

### Get All User Alerts
```bash
curl -X GET http://localhost:8000/api/alerts/user/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Only Active Alerts
```bash
curl -X GET http://localhost:8000/api/alerts/user/1/active \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Delete Alert
```bash
curl -X DELETE http://localhost:8000/api/alerts/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 5. Portfolio

### Get Portfolio Summary
```bash
curl -X GET http://localhost:8000/api/users/1/portfolio \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response includes:**
- Current balance
- All holdings with unrealized P&L
- Total portfolio value

---

## 6. WebSocket (Real-time Streaming)

### JavaScript Example
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/market-stream');

ws.onopen = () => {
  console.log('Connected to market stream');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Market Update:', data);

  // Data format:
  // {
  //   "timestamp": 1234567890.123,
  //   "markets": [
  //     {"id": 1, "symbol": "BTC/USDT", "price": 62150.50},
  //     {"id": 2, "symbol": "ETH/USDT", "price": 3205.75}
  //   ]
  // }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from market stream');
};
```

### Python Example
```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"Market Update: {data}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connected to market stream")

ws = websocket.WebSocketApp(
    "ws://localhost:8000/ws/market-stream",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open
)

ws.run_forever()
```

---

## 7. Complete Workflow Example

### Step 1: Register and Login
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Trader",
    "email": "john@trader.com",
    "password": "securepass123",
    "balance": 50000.0
  }'

# Login and save token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@trader.com",
    "password": "securepass123"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"
```

### Step 2: Check Available Markets
```bash
curl -X GET http://localhost:8000/api/markets/ \
  -H "Authorization: Bearer $TOKEN"
```

### Step 3: Buy Some Crypto
```bash
# Buy 0.1 BTC
curl -X POST http://localhost:8000/api/holdings/trade/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "symbol": "BTC/USDT",
    "type": "buy",
    "price": 62000.0,
    "quantity": 0.1
  }'

# Buy 1 ETH
curl -X POST http://localhost:8000/api/holdings/trade/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "symbol": "ETH/USDT",
    "type": "buy",
    "price": 3200.0,
    "quantity": 1.0
  }'
```

### Step 4: Set Price Alerts
```bash
# Alert when BTC goes below $60,000
curl -X POST http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "symbol": "BTC/USDT",
    "direction": "below",
    "target_price": 60000.0
  }'

# Alert when ETH goes above $3,500
curl -X POST http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "symbol": "ETH/USDT",
    "direction": "above",
    "target_price": 3500.0
  }'
```

### Step 5: Check Portfolio
```bash
curl -X GET http://localhost:8000/api/users/1/portfolio \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Step 6: Monitor Alerts
```bash
# Check active alerts
curl -X GET http://localhost:8000/api/alerts/user/1/active \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## Testing Tips

1. **Use jq for pretty JSON**: Install jq and pipe responses through it
   ```bash
   curl ... | jq
   ```

2. **Save token as variable**: Makes subsequent requests easier
   ```bash
   TOKEN="your_access_token_here"
   curl -H "Authorization: Bearer $TOKEN" ...
   ```

3. **Watch Celery logs**: See price updates and alert triggers in real-time
   ```bash
   # Docker
   docker-compose logs -f celery_worker

   # Local
   # Check terminal running Celery worker
   ```

4. **Monitor Redis**: Check task queue
   ```bash
   redis-cli
   KEYS *
   ```

---

## Postman Collection

Import this collection into Postman for easier testing:

1. Create new collection: "Crypto Tracker API"
2. Add environment variable: `base_url` = `http://localhost:8000`
3. Add environment variable: `token` = (set after login)
4. Import all the curl commands above

---

## Common Issues

### 401 Unauthorized
- Token expired or invalid
- Get a new token by logging in again

### 404 Not Found
- Market doesn't exist
- Create market first using POST /api/markets/

### 400 Insufficient Balance
- User doesn't have enough balance to buy
- Check portfolio and reduce quantity

### 400 Insufficient Quantity
- Trying to sell more than owned
- Check holdings first
