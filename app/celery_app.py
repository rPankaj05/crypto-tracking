from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "crypto_tracker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.services.price_simulator"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "update-market-prices": {
            "task": "app.services.price_simulator.update_market_prices",
            "schedule": settings.PRICE_UPDATE_INTERVAL,  # Run every X seconds
        },
        "check-price-alerts": {
            "task": "app.services.price_simulator.check_and_trigger_alerts",
            "schedule": settings.PRICE_UPDATE_INTERVAL,  # Run every X seconds
        },
    },
)
