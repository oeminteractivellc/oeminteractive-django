import csv
import logging

from django import forms
from django.shortcuts import render
from django.urls import path

from . import models
from . import tasks

logger = logging.getLogger(__name__)


class CsvEnabledModelAdminMixin:
  change_list_template = "upload/admin/changelist_with_csv.html"

  def get_urls(self):
    return [
        path("import-csv/", self.import_csv),
    ] + super().get_urls()

  def import_csv(self, request):
    model = self.Meta.Model
    template_path = "upload/admin/import-csv.html"
    context_data = {
        "form": CsvImportForm(),
        "model": model,
        "model_name": model._meta.verbose_name,
        "model_class_name": model.__name__,
    }
    if request.method == "POST":
      try:
        logger.info("posted csv upload")
        csv_file = request.FILES["csv_file"]
        csv_string = csv_file.read().decode("utf-8")
        up = models.UploadProgress.objects.create(user=request.user, schema=model.__name__)
        context_data.update({"upload_progress_id": up.id})
        tasks.run_csv_upload.delay(up.id, csv_string)
        template_path = "upload/admin/track-import-csv.html"
      except ValueError as e:
        context_data.update({"error": str(e)})
    return render(request, template_path, context_data)


class CsvImportForm(forms.Form):
  csv_file = forms.FileField()
