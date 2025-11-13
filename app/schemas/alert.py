from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional, Literal


class AlertCreate(BaseModel):
    """Schema for creating a price alert"""
    user_id: int = Field(..., gt=0)
    symbol: str = Field(..., min_length=1, description="Market symbol like BTC/USDT")
    direction: Literal["above", "below"] = Field(..., description="Alert direction: above or below")
    target_price: Decimal = Field(..., gt=0, description="Target price for alert")


class AlertResponse(BaseModel):
    """Schema for alert response"""
    id: int
    user_id: int
    market_id: int
    target_price: Decimal
    direction: str
    triggered: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None

    class Config:
        from_attributes = True
