import csv, logging

from celery import shared_task
from io import StringIO

from .models import UploadProgress

logger = logging.getLogger(__name__)


# HACK for until we figure out how to get loader classes registered at startup in celery.
def get_loader_class(model_name):
  import sys
  return getattr(sys.modules["core"].loaders, model_name + "Loader")


@shared_task
def run_csv_upload(upload_progress_id, csv_string_data):
  logger.info(f"run csv upload, upload_progress_id={upload_progress_id}")
  up = UploadProgress.objects.get(id=upload_progress_id)
  logger.info(f"run csv upload, up.schema={up.schema}")
  LoaderClass = get_loader_class(up.schema)

  def update_progress(*args, **kwargs):
    UploadProgress.objects.filter(id=upload_progress_id).update(**kwargs)

  loader = LoaderClass(csv.reader(StringIO(csv_string_data)))
  loader.process(update_progress)
