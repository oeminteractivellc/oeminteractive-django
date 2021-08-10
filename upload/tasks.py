import csv, logging, requests

from celery import shared_task
from io import StringIO

from .models import UploadProgress

logger = logging.getLogger(__name__)


# HACK for until we figure out how to get loader classes registered at startup in celery.
def get_loader_class(model_name):
  import sys
  return getattr(sys.modules["core"].loaders, model_name + "Loader")


@shared_task
def run_csv_upload(upload_progress_id, csv_url):
  logger.info(f"run csv upload, upload_progress_id={upload_progress_id} csv_url={csv_url}")
  up = UploadProgress.objects.get(id=upload_progress_id)
  logger.info(f"run csv upload, up.schema={up.schema}")
  LoaderClass = get_loader_class(up.schema)

  def update_progress(*args, **kwargs):
    logger.info("update progress")
    UploadProgress.objects.filter(id=upload_progress_id).update(**kwargs)
    logger.info("updated progress")

  res = requests.get(csv_url)
  res.raise_for_status()
  csv_string_data = res.text
  loader = LoaderClass(csv.reader(StringIO(csv_string_data)))
  loader.process_import(update_progress)
