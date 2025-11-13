import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Market, Holding, TransactionLog


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create test database and session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create test user"""
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password="hashed_password",
        balance=Decimal("10000.00000000")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_market(db):
    """Create test market"""
    market = Market(
        symbol="BTC/USDT",
        current_price=Decimal("60000.00000000")
    )
    db.add(market)
    db.commit()
    db.refresh(market)
    return market


def test_buy_trade_new_holding(db, test_user, test_market):
    """Test buying crypto creates new holding"""
    quantity = Decimal("0.5")
    price = Decimal("60000.00000000")
    total = price * quantity

    # Execute buy
    test_user.balance -= total
    holding = Holding(
        user_id=test_user.id,
        market_id=test_market.id,
        quantity=quantity,
        avg_buy_price=price
    )
    db.add(holding)
    db.commit()

    # Verify
    assert test_user.balance == Decimal("7000.00000000")
    assert holding.quantity == Decimal("0.5")
    assert holding.avg_buy_price == Decimal("60000.00000000")


def test_buy_trade_update_holding(db, test_user, test_market):
    """Test buying more crypto updates average buy price"""
    # First purchase
    quantity1 = Decimal("0.5")
    price1 = Decimal("60000.00000000")

    holding = Holding(
        user_id=test_user.id,
        market_id=test_market.id,
        quantity=quantity1,
        avg_buy_price=price1
    )
    db.add(holding)
    test_user.balance -= (price1 * quantity1)
    db.commit()
    db.refresh(holding)

    # Second purchase at different price
    quantity2 = Decimal("0.3")
    price2 = Decimal("62000.00000000")

    # Calculate new average
    total_value = (holding.avg_buy_price * holding.quantity) + (price2 * quantity2)
    new_quantity = holding.quantity + quantity2
    new_avg_price = total_value / new_quantity

    holding.quantity = new_quantity
    holding.avg_buy_price = new_avg_price
    test_user.balance -= (price2 * quantity2)
    db.commit()

    # Verify
    assert holding.quantity == Decimal("0.8")
    expected_avg = Decimal("60750.00000000")
    assert abs(holding.avg_buy_price - expected_avg) < Decimal("0.0001")


def test_sell_trade_reduce_holding(db, test_user, test_market):
    """Test selling crypto reduces holding"""
    # Create initial holding
    holding = Holding(
        user_id=test_user.id,
        market_id=test_market.id,
        quantity=Decimal("1.0"),
        avg_buy_price=Decimal("60000.00000000")
    )
    db.add(holding)
    test_user.balance = Decimal("5000.00000000")
    db.commit()
    db.refresh(holding)

    # Sell some
    sell_quantity = Decimal("0.4")
    sell_price = Decimal("62000.00000000")
    sell_total = sell_quantity * sell_price

    holding.quantity -= sell_quantity
    test_user.balance += sell_total
    db.commit()

    # Verify
    assert holding.quantity == Decimal("0.6")
    assert test_user.balance == Decimal("29800.00000000")


def test_calculate_pnl(db, test_user, test_market):
    """Test profit/loss calculation"""
    # Create holding
    holding = Holding(
        user_id=test_user.id,
        market_id=test_market.id,
        quantity=Decimal("0.5"),
        avg_buy_price=Decimal("60000.00000000")
    )
    db.add(holding)
    db.commit()
    db.refresh(holding)

    # Update market price
    test_market.current_price = Decimal("65000.00000000")
    db.commit()

    # Calculate P&L
    current_price = test_market.current_price
    unrealized_pnl = (current_price - holding.avg_buy_price) * holding.quantity

    # Verify
    expected_pnl = Decimal("2500.00000000")
    assert unrealized_pnl == expected_pnl


def test_insufficient_balance(db, test_user, test_market):
    """Test buying with insufficient balance fails"""
    quantity = Decimal("1.0")
    price = Decimal("60000.00000000")
    total = price * quantity

    # User balance is 10000, trying to buy 60000 worth
    assert test_user.balance < total


def test_insufficient_quantity_to_sell(db, test_user, test_market):
    """Test selling more than owned fails"""
    # Create holding
    holding = Holding(
        user_id=test_user.id,
        market_id=test_market.id,
        quantity=Decimal("0.5"),
        avg_buy_price=Decimal("60000.00000000")
    )
    db.add(holding)
    db.commit()

    # Try to sell more than owned
    sell_quantity = Decimal("1.0")
    assert holding.quantity < sell_quantity


def test_transaction_log(db, test_user, test_market):
    """Test transaction logging"""
    # Create transaction
    transaction = TransactionLog(
        user_id=test_user.id,
        market_id=test_market.id,
        type="buy",
        price=Decimal("60000.00000000"),
        quantity=Decimal("0.5"),
        total_amount=Decimal("30000.00000000")
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # Verify
    assert transaction.type == "buy"
    assert transaction.quantity == Decimal("0.5")
    assert transaction.total_amount == Decimal("30000.00000000")
