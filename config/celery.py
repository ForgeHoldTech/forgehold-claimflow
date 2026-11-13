import os
from pathlib import Path

from celery import Celery
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.conf.broker_url = os.environ.get("REDIS_URL", "redis://127.0.0.1:6380/0")
app.conf.result_backend = os.environ.get("REDIS_URL", "redis://127.0.0.1:6380/0")
app.autodiscover_tasks()