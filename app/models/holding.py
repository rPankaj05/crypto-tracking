from sqlalchemy import Column, Integer, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.database import Base


class Holding(Base):
    """Holding model for storing user's cryptocurrency holdings"""

    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    market_id = Column(Integer, ForeignKey("markets.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(DECIMAL(20, 8), nullable=False, default=0.00000000)
    avg_buy_price = Column(DECIMAL(20, 8), nullable=False)

    # Relationships
    user = relationship("User", back_populates="holdings")
    market = relationship("Market", back_populates="holdings")

    def __repr__(self):
        return f"<Holding(id={self.id}, user_id={self.user_id}, market_id={self.market_id}, quantity={self.quantity})>"
