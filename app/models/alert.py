from sqlalchemy import Column, Integer, ForeignKey, String, DECIMAL, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Alert(Base):
    """Alert model for storing price alert configurations"""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    market_id = Column(Integer, ForeignKey("markets.id", ondelete="CASCADE"), nullable=False, index=True)
    target_price = Column(DECIMAL(20, 8), nullable=False)
    direction = Column(String(10), nullable=False)  # 'above' or 'below'
    triggered = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    triggered_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="alerts")
    market = relationship("Market", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, market_id={self.market_id}, direction={self.direction}, target={self.target_price}, triggered={self.triggered})>"
