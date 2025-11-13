from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.config import settings
from app.database import init_db
from app.routers import (
    auth_router,
    markets_router,
    holdings_router,
    alerts_router,
    portfolio_router
)
from app.websockets.market_stream import manager, market_data_streamer

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A backend service for tracking crypto prices, managing portfolios, and setting price alerts",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and start background tasks"""
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📊 Initializing database...")

    # Create database tables
    init_db()

    print(f"✅ Database initialized successfully")
    print(f"📡 WebSocket endpoint available at: ws://localhost:8000/ws/market-stream")
    print(f"📚 API Documentation available at: http://localhost:8000/docs")

    # Start WebSocket market data streaming task
    asyncio.create_task(market_data_streamer())


# Include routers
app.include_router(auth_router)
app.include_router(markets_router)
app.include_router(holdings_router)
app.include_router(alerts_router)
app.include_router(portfolio_router)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "websocket": "/ws/market-stream"
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }


# WebSocket endpoint for real-time market streaming
@app.websocket("/ws/market-stream")
async def websocket_market_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming real-time market price updates
    Connect to ws://localhost:8000/ws/market-stream to receive live price data
    """
    await manager.connect(websocket)

    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()

            # Echo back client message (optional)
            if data:
                await manager.send_personal_message(f"Received: {data}", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
