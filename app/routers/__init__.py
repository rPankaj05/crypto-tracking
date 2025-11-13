from .auth import router as auth_router
from .markets import router as markets_router
from .holdings import router as holdings_router
from .alerts import router as alerts_router
from .portfolio import router as portfolio_router

__all__ = [
    "auth_router",
    "markets_router",
    "holdings_router",
    "alerts_router",
    "portfolio_router"
]
