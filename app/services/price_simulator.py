import random
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Market, Alert
from app.config import settings


def get_db_session():
    """Get database session for Celery tasks"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, will close after use


@celery_app.task(name="app.services.price_simulator.update_market_prices")
def update_market_prices():
    """
    Celery task to simulate price changes for all markets
    Updates prices with random variations between configured min/max percentages
    """
    db = get_db_session()

    try:
        markets = db.query(Market).all()

        if not markets:
            print("⚠️  No markets found to update")
            return

        updated_count = 0

        for market in markets:
            # Generate random price change percentage
            variation_percent = random.uniform(
                settings.PRICE_VARIATION_MIN,
                settings.PRICE_VARIATION_MAX
            )

            # Randomly decide if price goes up or down
            direction = random.choice([1, -1])

            # Calculate new price
            current_price = Decimal(str(market.current_price))
            price_change = current_price * Decimal(str(variation_percent / 100)) * direction
            new_price = current_price + price_change

            # Ensure price doesn't go negative
            if new_price < Decimal("0.00000001"):
                new_price = current_price * Decimal("0.99")

            # Update market price
            market.current_price = new_price
            updated_count += 1

            print(f"📊 {market.symbol}: {float(current_price):.8f} → {float(new_price):.8f} ({direction * variation_percent:+.2f}%)")

        db.commit()
        print(f"✅ Updated {updated_count} market prices at {datetime.now()}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error updating market prices: {str(e)}")
    finally:
        db.close()


@celery_app.task(name="app.services.price_simulator.check_and_trigger_alerts")
def check_and_trigger_alerts():
    """
    Celery task to check all active alerts and trigger them if conditions are met
    Runs after each price update
    """
    db = get_db_session()

    try:
        # Get all non-triggered alerts
        active_alerts = db.query(Alert).filter(Alert.triggered == False).all()

        if not active_alerts:
            return

        triggered_count = 0

        for alert in active_alerts:
            market = alert.market
            current_price = Decimal(str(market.current_price))
            target_price = Decimal(str(alert.target_price))

            should_trigger = False

            # Check if alert conditions are met
            if alert.direction == "above" and current_price >= target_price:
                should_trigger = True
            elif alert.direction == "below" and current_price <= target_price:
                should_trigger = True

            if should_trigger:
                # Mark alert as triggered
                alert.triggered = True
                alert.triggered_at = datetime.utcnow()
                triggered_count += 1

                # Log to console (simulated notification)
                print(f"\n🚨 ALERT TRIGGERED!")
                print(f"   User ID: {alert.user_id}")
                print(f"   Market: {market.symbol}")
                print(f"   Condition: Price {alert.direction} {float(target_price):.8f}")
                print(f"   Current Price: {float(current_price):.8f}")
                print(f"   Triggered At: {alert.triggered_at}")
                print(f"=" * 50)

        if triggered_count > 0:
            db.commit()
            print(f"✅ Triggered {triggered_count} alerts at {datetime.now()}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error checking alerts: {str(e)}")
    finally:
        db.close()
