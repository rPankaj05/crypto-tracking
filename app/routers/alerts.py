from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Market, Alert
from app.schemas.alert import AlertCreate, AlertResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new price alert"""

    # Check if user exists
    user = db.query(User).filter(User.id == alert_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if market exists
    market = db.query(Market).filter(Market.symbol == alert_data.symbol).first()
    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market {alert_data.symbol} not found"
        )

    # Validate alert direction
    if alert_data.direction not in ["above", "below"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Direction must be 'above' or 'below'"
        )

    # Create alert
    new_alert = Alert(
        user_id=user.id,
        market_id=market.id,
        target_price=alert_data.target_price,
        direction=alert_data.direction,
        triggered=False
    )

    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    return new_alert


@router.get("/user/{user_id}", response_model=List[AlertResponse])
def get_user_alerts(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all alerts for a specific user"""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    alerts = db.query(Alert).filter(Alert.user_id == user_id).all()
    return alerts


@router.get("/user/{user_id}/active", response_model=List[AlertResponse])
def get_active_alerts(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get only active (non-triggered) alerts for a user"""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    alerts = db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.triggered == False
    ).all()

    return alerts


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific alert"""

    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    db.delete(alert)
    db.commit()

    return None
