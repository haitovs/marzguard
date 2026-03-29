import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import get_settings
from src.core.enforcer import Enforcer
from src.core.tracker import IPTracker

logger = logging.getLogger(__name__)


def create_scheduler(tracker: IPTracker, enforcer: Enforcer) -> AsyncIOScheduler:
    """Create and configure the APScheduler with enforcement jobs."""
    settings = get_settings()
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        enforcer.enforce,
        "interval",
        seconds=settings.enforcement_interval,
        id="enforce",
        name="IP Limit Enforcement",
        max_instances=1,
    )

    scheduler.add_job(
        enforcer.check_reenable,
        "interval",
        seconds=settings.reenable_check_interval,
        id="reenable",
        name="Re-enable Check",
        max_instances=1,
    )

    scheduler.add_job(
        tracker.cleanup,
        "interval",
        seconds=60,
        id="cleanup",
        name="IP Tracker Cleanup",
        max_instances=1,
    )

    logger.info(
        "Scheduler configured: enforce every %ds, reenable every %ds",
        settings.enforcement_interval,
        settings.reenable_check_interval,
    )
    return scheduler
