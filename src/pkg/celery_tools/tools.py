from celery import Celery

from configuration.config import settings
from internal.database import storage
from pkg.email_tools.tools import EmailTools

celery_app = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    broker_connection_retry_on_startup=True,
)
celery_app.conf.task_always_eager = settings.CELERY_EAGER


@celery_app.task(name="send_email")
def send_email_task(recipient: str, subject: str, body: str) -> dict:
    EmailTools().send_email(recipient, subject, body)
    return {"status": "success"}


@celery_app.task(name="upload_file")
def upload_file_task(
    content: str, path: str, content_type: str = None, metadata: dict = None
):
    storage.upload_file_to_storage(content, path, content_type, metadata)
    return {"storage": storage.bucket.name}


@celery_app.task(name="delete_file")
def delete_file_task(name: str):
    blob = storage.get_blob(name)
    blob.delete()
    return {"delete": "success"}
