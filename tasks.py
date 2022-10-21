import os
import time

from celery import Celery
from django.core.mail import send_mail

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
app = Celery("tasks", broker="redis://localhost")


@app.task
def send_email(subject, message, from_email, to_email):
    """Send email to user. Simulate 5 seconds of delay"""
    time.sleep(5)
    send_mail(subject, message, from_email, [to_email])
    print("Email sent to user")
