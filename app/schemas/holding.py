from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Literal


class TradeRequest(BaseModel):
    """Schema for buy/sell trade request"""
    user_id: int = Field(..., gt=0)
    symbol: str = Field(..., min_length=1, description="Market symbol like BTC/USDT")
    type: Literal["buy", "sell"] = Field(..., description="Trade type: buy or sell")
    price: Decimal = Field(..., gt=0, description="Price per unit")
    quantity: Decimal = Field(..., gt=0, description="Quantity to trade")


class HoldingResponse(BaseModel):
    """Schema for holding response"""
    id: int
    user_id: int
    market_id: int
    quantity: Decimal
    avg_buy_price: Decimal

    class Config:
        from_attributes = True
