"""A gunicorn config file, used to define tasks done at certain hooks.

- `on_starting`: Sets the job scheduler to run on the app.
                 Runs on startup so that only one worker (the main arbiter) runs the scheduled task.
"""

from gunicorn.arbiter import Arbiter

from apps.football_pool.job_scheduling import schedule_result_computation


# https://docs.gunicorn.org/en/stable/settings.html#on-starting
def on_starting(main_worker: Arbiter):
    """Sets up the job scheduler to schedule the computation of results for the database.

    Args:
        main_worker (Arbiter): The central main worker process from gunicorn.
    """
    schedule_result_computation()
