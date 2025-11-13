from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.database import get_db
from app.models import User, Market, Holding, TransactionLog
from app.schemas.holding import TradeRequest, HoldingResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/holdings", tags=["Holdings"])


@router.post("/trade/", status_code=status.HTTP_201_CREATED)
def execute_trade(
    trade: TradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute a buy or sell trade
    - Buy: Decrease user balance, add/update holdings
    - Sell: Increase user balance, reduce holdings
    - Record transaction in TransactionLog
    """

    # Get user
    user = db.query(User).filter(User.id == trade.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get market
    market = db.query(Market).filter(Market.symbol == trade.symbol).first()
    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market {trade.symbol} not found"
        )

    # Calculate total amount
    total_amount = trade.price * trade.quantity

    if trade.type == "buy":
        # Check if user has sufficient balance
        if user.balance < total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )

        # Deduct balance
        user.balance -= total_amount

        # Check if holding exists
        holding = db.query(Holding).filter(
            Holding.user_id == user.id,
            Holding.market_id == market.id
        ).first()

        if holding:
            # Update existing holding - calculate new average buy price
            total_value = (holding.avg_buy_price * holding.quantity) + (trade.price * trade.quantity)
            new_quantity = holding.quantity + trade.quantity
            holding.avg_buy_price = total_value / new_quantity
            holding.quantity = new_quantity
        else:
            # Create new holding
            holding = Holding(
                user_id=user.id,
                market_id=market.id,
                quantity=trade.quantity,
                avg_buy_price=trade.price
            )
            db.add(holding)

    elif trade.type == "sell":
        # Check if holding exists
        holding = db.query(Holding).filter(
            Holding.user_id == user.id,
            Holding.market_id == market.id
        ).first()

        if not holding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No holdings found for this market"
            )

        # Check if user has sufficient quantity
        if holding.quantity < trade.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient quantity. Available: {holding.quantity}"
            )

        # Increase balance
        user.balance += total_amount

        # Reduce holding quantity
        holding.quantity -= trade.quantity

        # If quantity becomes zero, delete the holding
        if holding.quantity == 0:
            db.delete(holding)

    # Record transaction
    transaction = TransactionLog(
        user_id=user.id,
        market_id=market.id,
        type=trade.type,
        price=trade.price,
        quantity=trade.quantity,
        total_amount=total_amount
    )
    db.add(transaction)

    # Commit all changes
    db.commit()

    return {
        "message": f"{trade.type.capitalize()} order executed successfully",
        "trade_type": trade.type,
        "symbol": trade.symbol,
        "quantity": float(trade.quantity),
        "price": float(trade.price),
        "total_amount": float(total_amount),
        "new_balance": float(user.balance)
    }


@router.get("/user/{user_id}", response_model=list[HoldingResponse])
def get_user_holdings(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all holdings for a specific user"""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    holdings = db.query(Holding).filter(Holding.user_id == user_id).all()
    return holdings
