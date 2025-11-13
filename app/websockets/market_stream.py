import asyncio
import json
from typing import List
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Market


class ConnectionManager:
    """Manages WebSocket connections for real-time market data streaming"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.remove(websocket)
        print(f"❌ WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific client"""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")


# Create global connection manager
manager = ConnectionManager()


async def get_market_data(db: Session) -> dict:
    """Fetch current market data from database"""
    markets = db.query(Market).all()

    market_data = {
        "timestamp": asyncio.get_event_loop().time(),
        "markets": [
            {
                "id": market.id,
                "symbol": market.symbol,
                "price": float(market.current_price),
            }
            for market in markets
        ]
    }

    return market_data


async def market_data_streamer():
    """Background task to continuously stream market data to all connected clients"""
    while True:
        if manager.active_connections:
            db = SessionLocal()
            try:
                market_data = await get_market_data(db)
                message = json.dumps(market_data)
                await manager.broadcast(message)
            except Exception as e:
                print(f"Error streaming market data: {e}")
            finally:
                db.close()

        # Wait before next update (1 second)
        await asyncio.sleep(1)
