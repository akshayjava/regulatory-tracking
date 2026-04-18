"""
APScheduler-based daily sync scheduler for LATTICE ingestion pipeline.
"""
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


def start_scheduler(pipeline) -> BackgroundScheduler:
    """Start the background scheduler running pipeline.run() daily at 06:00 UTC."""
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        func=pipeline.run,
        trigger=CronTrigger(hour=6, minute=0),
        id="daily_ingestion",
        name="Daily Regulatory Ingestion",
        replace_existing=True,
    )
    scheduler.start()
    next_run = scheduler.get_job("daily_ingestion").next_run_time
    logger.info(f"Scheduler started. Next ingestion run: {next_run}")
    return scheduler


def run_once(pipeline) -> dict:
    """Run the pipeline immediately (blocking) and return stats."""
    logger.info(f"Running ingestion pipeline at {datetime.utcnow().isoformat()}")
    stats = pipeline.run()
    logger.info(f"Ingestion complete: {stats}")
    return stats
