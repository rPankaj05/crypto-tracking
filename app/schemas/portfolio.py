from pydantic import BaseModel
from decimal import Decimal
from typing import List


class HoldingDetail(BaseModel):
    """Schema for detailed holding information in portfolio"""
    symbol: str
    quantity: Decimal
    avg_buy_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal  # Profit/Loss

    class Config:
        from_attributes = True


class PortfolioResponse(BaseModel):
    """Schema for portfolio summary response"""
    balance: Decimal
    holdings: List[HoldingDetail]
    total_value: Decimal  # balance + value of all holdings

    class Config:
        from_attributes = True
