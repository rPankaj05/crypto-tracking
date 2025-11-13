from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.database import get_db
from app.models import User, Holding
from app.schemas.portfolio import PortfolioResponse, HoldingDetail
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["Portfolio"])


@router.get("/{user_id}/portfolio", response_model=PortfolioResponse)
def get_portfolio_summary(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get portfolio summary for a user including:
    - Current balance
    - All holdings with unrealized P&L
    - Total portfolio value
    """

    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get all holdings
    holdings = db.query(Holding).filter(Holding.user_id == user_id).all()

    # Calculate holding details
    holding_details = []
    total_holdings_value = Decimal("0")

    for holding in holdings:
        # Get current market price
        current_price = holding.market.current_price

        # Calculate unrealized P&L
        # P&L = (current_price - avg_buy_price) * quantity
        unrealized_pnl = (current_price - holding.avg_buy_price) * holding.quantity

        # Calculate value of this holding
        holding_value = current_price * holding.quantity
        total_holdings_value += holding_value

        holding_detail = HoldingDetail(
            symbol=holding.market.symbol,
            quantity=holding.quantity,
            avg_buy_price=holding.avg_buy_price,
            current_price=current_price,
            unrealized_pnl=unrealized_pnl
        )
        holding_details.append(holding_detail)

    # Calculate total portfolio value (balance + holdings value)
    total_value = user.balance + total_holdings_value

    portfolio = PortfolioResponse(
        balance=user.balance,
        holdings=holding_details,
        total_value=total_value
    )

    return portfolio
