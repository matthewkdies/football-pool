"""Contains scheduled jobs run with 'apscheduler'."""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from apps.football_pool import create_app
from apps.football_pool.get_scores import EST, write_to_db


def schedule_result_computation() -> None:
    """Schedules the computation of results into the database for Tuesday at 1AM EST."""
    app = create_app()
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=write_to_db,
        args=[app],
        trigger=CronTrigger(day_of_week="tue", hour=1, minute=0, timezone=EST),
        misfire_grace_time=None,
        max_instances=1,
        coalesce=True,
    )
