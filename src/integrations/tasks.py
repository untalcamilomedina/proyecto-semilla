from config.celery import app as celery_app
from celery import shared_task
import time

@shared_task
def debug_task(duration=5):
    """
    Simple task to test Celery/Redis connection.
    """
    time.sleep(duration)
    return "Task completed"

@shared_task
def scan_notion_workspace_task(job_id, user_id, config):
    """
    Placeholder task for Notion Scan.
    In real implementation, this will:
    1. Update Job status to RUNNING
    2. Call NotionService
    3. Update Job status to SUCCEEDED/FAILED
    """
    pass
