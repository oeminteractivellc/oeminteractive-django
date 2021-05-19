import csv, logging

from celery import shared_task
from io import StringIO

from .models import UploadProgress
from . import LoaderClassForModelName

logger = logging.getLogger(__name__)


@shared_task
def run_csv_upload(upload_progress_id, csv_string_data):
  up = UploadProgress.objects.get(id=upload_progress_id)
  LoaderClass = LoaderClassForModelName(up.schema)

  def update_progress(*args, **kwargs):
    UploadProgress.objects.filter(id=upload_progress_id).update(**kwargs)

  loader = LoaderClass(csv.reader(StringIO(csv_string_data)))
  loader.process(update_progress)
