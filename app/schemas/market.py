from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional


class MarketCreate(BaseModel):
    """Schema for creating/updating a market"""
    symbol: str = Field(..., min_length=1, max_length=50, description="Market symbol like BTC/USDT")
    price: Decimal = Field(..., gt=0, description="Current market price")


class MarketUpdate(BaseModel):
    """Schema for updating market price"""
    price: Decimal = Field(..., gt=0)


class MarketResponse(BaseModel):
    """Schema for market response"""
    id: int
    symbol: str
    current_price: Decimal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
