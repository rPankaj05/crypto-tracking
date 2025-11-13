from sqlalchemy import Column, Integer, String, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Market(Base):
    """Market model for storing cryptocurrency market information"""

    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, index=True, nullable=False)  # e.g., BTC/USDT, ETH/USDT
    current_price = Column(DECIMAL(20, 8), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    holdings = relationship("Holding", back_populates="market", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="market", cascade="all, delete-orphan")
    transactions = relationship("TransactionLog", back_populates="market", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Market(id={self.id}, symbol={self.symbol}, price={self.current_price})>"
