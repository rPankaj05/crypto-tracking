from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Market, User
from app.schemas.market import MarketCreate, MarketResponse, MarketUpdate
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/markets", tags=["Markets"])


@router.post("/", response_model=MarketResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_market(
    market_data: MarketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new market or update existing market price
    This simulates manual price updates for testing
    """

    # Check if market already exists
    existing_market = db.query(Market).filter(Market.symbol == market_data.symbol).first()

    if existing_market:
        # Update existing market
        existing_market.current_price = market_data.price
        db.commit()
        db.refresh(existing_market)
        return existing_market
    else:
        # Create new market
        new_market = Market(
            symbol=market_data.symbol,
            current_price=market_data.price
        )
        db.add(new_market)
        db.commit()
        db.refresh(new_market)
        return new_market


@router.get("/", response_model=List[MarketResponse])
def get_all_markets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all markets"""
    markets = db.query(Market).all()
    print(markets)
    return markets


@router.get("/symbol", response_model=MarketResponse)
def get_market_by_symbol(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific market by symbol (use query parameter: ?symbol=BTC/USDT)"""
    market = db.query(Market).filter(Market.symbol == symbol).first()

    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market {symbol} not found"
        )

    return market


@router.put("/", response_model=MarketResponse)
def update_market_price(
    symbol: str,
    price_update: MarketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update market price (use query parameter: ?symbol=BTC/USDT)"""
    market = db.query(Market).filter(Market.symbol == symbol).first()

    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market {symbol} not found"
        )

    market.current_price = price_update.price
    db.commit()
    db.refresh(market)

    return market


@router.delete("/{market_id}", status_code=status.HTTP_200_OK)
def delete_market(
    market_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a market by ID"""
    market = db.query(Market).filter(Market.id == market_id).first()

    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market with ID {market_id} not found"
        )

    # Delete the market (cascade will handle related records)
    db.delete(market)
    db.commit()

    return {"message": f"Market {market.symbol} deleted successfully"}
