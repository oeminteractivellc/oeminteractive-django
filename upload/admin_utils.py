import logging

from django import forms
from django.db import transaction
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
        path("export-csv/", self.export_csv),
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
      csv_string = None
      try:
        csv_file = request.FILES["csv_file"]
        csv_string = csv_file.read().decode("utf-8")
      except ValueError as e:
        context_data.update({"error": str(e)})
      if csv_string is not None:
        up = models.UploadProgress.objects.create(user=request.user, schema=model.__name__)
        transaction.on_commit(lambda: tasks.run_csv_upload.delay(up.id, csv_string))
        template_path = "upload/admin/track-import-csv.html"
        context_data.update({"upload_progress_id": up.id})
    return render(request, template_path, context_data)

  def export_csv(self, request):
    import sys
    import unicodecsv as csv
    from django.http import HttpResponse
    Model = self.Meta.Model
    model_name = Model.__name__
    filename = f"{model_name}.csv"
    schema = getattr(sys.modules["core"].schemas, model_name + "Schema")
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    writer.writerow(schema.headers)
    for record in Model.objects.all():
      writer.writerow([str(f(record)) for f in schema.fields])
    response["Content-Disposition"] = ("attachment;" "filename={0}".format(filename))
    return response


class CsvImportForm(forms.Form):
  csv_file = forms.FileField()
