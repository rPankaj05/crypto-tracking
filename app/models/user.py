from sqlalchemy import Column, Integer, String, DECIMAL
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """User model for storing user account information"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    balance = Column(DECIMAL(20, 8), default=10000.00000000, nullable=False)  # Virtual USD balance

    # Relationships
    holdings = relationship("Holding", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("TransactionLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, balance={self.balance})>"
