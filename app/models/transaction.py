from sqlalchemy import Column, Integer, ForeignKey, String, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class TransactionLog(Base):
    """Transaction log model for storing all buy/sell transactions"""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    market_id = Column(Integer, ForeignKey("markets.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(10), nullable=False)  # 'buy' or 'sell'
    price = Column(DECIMAL(20, 8), nullable=False)
    quantity = Column(DECIMAL(20, 8), nullable=False)
    total_amount = Column(DECIMAL(20, 8), nullable=False)  # price * quantity
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
    market = relationship("Market", back_populates="transactions")

    def __repr__(self):
        return f"<TransactionLog(id={self.id}, type={self.type}, market_id={self.market_id}, quantity={self.quantity}, price={self.price})>"
