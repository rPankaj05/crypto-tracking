"""
Seed script to populate the database with initial test data
Run this script to create sample users and markets
"""
from decimal import Decimal
from app.database import SessionLocal, init_db
from app.models import User, Market
from app.utils.auth import get_password_hash


def seed_database():
    """Seed the database with initial data"""
    print("🌱 Starting database seeding...")

    # Initialize database
    init_db()

    # Create session
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("⚠️  Database already contains data. Skipping seed.")
            return

        # Create sample users
        users_data = [
            {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "password": "password123",
                "balance": Decimal("10000.00000000")
            },
            {
                "name": "Bob Smith",
                "email": "bob@example.com",
                "password": "password123",
                "balance": Decimal("15000.00000000")
            },
            {
                "name": "Charlie Brown",
                "email": "charlie@example.com",
                "password": "password123",
                "balance": Decimal("20000.00000000")
            }
        ]

        print("\n👥 Creating users...")
        for user_data in users_data:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                balance=user_data["balance"]
            )
            db.add(user)
            print(f"  ✓ {user_data['name']} ({user_data['email']})")

        # Create sample markets
        markets_data = [
            {"symbol": "BTC/USDT", "price": Decimal("62000.00000000")},
            {"symbol": "ETH/USDT", "price": Decimal("3200.00000000")},
            {"symbol": "SOL/USDT", "price": Decimal("145.50000000")},
            {"symbol": "BNB/USDT", "price": Decimal("420.75000000")},
            {"symbol": "XRP/USDT", "price": Decimal("0.55000000")},
            {"symbol": "ADA/USDT", "price": Decimal("0.48000000")},
            {"symbol": "DOGE/USDT", "price": Decimal("0.12000000")},
            {"symbol": "MATIC/USDT", "price": Decimal("0.85000000")},
        ]

        print("\n📊 Creating markets...")
        for market_data in markets_data:
            market = Market(
                symbol=market_data["symbol"],
                current_price=market_data["price"]
            )
            db.add(market)
            print(f"  ✓ {market_data['symbol']}: ${float(market_data['price']):.2f}")

        # Commit all changes
        db.commit()

        print("\n✅ Database seeding completed successfully!")
        print("\n📝 Test credentials:")
        print("  Email: alice@example.com")
        print("  Password: password123")
        print("\n  Email: bob@example.com")
        print("  Password: password123")
        print("\n  Email: charlie@example.com")
        print("  Password: password123")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding database: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
