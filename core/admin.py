import csv
import logging

from django import forms
from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path
from io import TextIOWrapper

from . import models
from upload.csvbase import GenericLoader

logger = logging.getLogger(__name__)


@admin.register(models.CarMakeModel)
class CarMakeModelAdmin(admin.ModelAdmin):
  list_display = ("slug", "make", "model")
  readonly_fields = ("slug", "make_slug", "model_slug")
  change_list_template = "admin/carmakemodel_changelist.html"

  def get_urls(self):
    return [
        path("import-csv/", self.import_csv),
    ] + super().get_urls()

  def import_csv(self, request):
    message = ""

    def track_import(*args, **kwargs):
      message = f"Added {kwargs['objects_added']} make/models.  Errors: {len(kwargs['errors'])}"
      logger.info(str(kwargs))

    if request.method == "POST":
      csv_file = request.FILES["csv_file"]
      csv_reader = csv.reader(TextIOWrapper(csv_file.file, encoding="UTF-8"))
      loader = CarMakeModelLoader(csv_reader)
      loader.process(track_import)
      self.message_user(request, message)
      return redirect("..")
    return render(request, "admin/carmakemodel_import_form.html", {"form": CsvImportForm()})


class CsvImportForm(forms.Form):
  csv_file = forms.FileField()


class CarMakeModelLoader(GenericLoader):

  FIELDS = ["make", "model"]
  MODEL_CLASS = models.CarMakeModel

  def _map_data(self, data):
    keys = {}
    fields = {}
    make = data["make"]
    model = data["model"]
    keys["make_slug"] = models.CarMakeModel.slugify(make)
    keys["model_slug"] = models.CarMakeModel.slugify(model)
    fields["make"] = data["make"]
    fields["model"] = data["model"]
    return keys, fields
