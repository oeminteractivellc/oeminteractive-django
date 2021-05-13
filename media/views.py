import datetime
import logging
import os
import requests

from django.core.exceptions import ValidationError
from django.http import JsonResponse, Http404
from django.shortcuts import redirect
from django.views.generic import View

from . import models
from core import models as core_models

logger = logging.getLogger(__name__)


class MediaMultiUploadView(View):
  def post(self, request, *args, **kwargs):
    schema = kwargs.get("schema")
    if schema != "ymm":
      raise ValidationError("invalid schema")
    results = []
    for f in request.FILES.getlist("images"):
      results.append(self.process_file(f))
    return JsonResponse({"results": results})

  def process_file(self, f):
    filename = str(f)

    def error(msg):
      return {"name": filename, "error": msg}

    basename = os.path.basename(filename)
    basename = os.path.splitext(basename)[0]
    parts = basename.split("-")
    if len(parts) < 3:
      return error("Must have year-make-model parts")
    year = parts[0]
    make = parts[1].lower()
    model = parts[2].lower()
    try:
      if int(year) < 1990 or int(year) > datetime.datetime.now().year + 1:
        return error("Invalid year")
    except ValueError:
      return error("Invalid year")
    if not core_models.CarMakeModel.objects.filter(make_slug=make, model_slug=model).exists():
      return error("Unknown make/model")

    media_file = models.MediaFile.objects.create(file=f)
    models.MediaFileTag.objects.create(media_file=media_file, key="year", value=year)
    models.MediaFileTag.objects.create(media_file=media_file, key="make", value=make)
    models.MediaFileTag.objects.create(media_file=media_file, key="model", value=model)
    return {"name": filename, "message": "Uploaded", "url": media_file.file.url}


class MediaRedirectView(View):
  def get(self, request, *args, **kwargs):
    if kwargs.get("slug", None):
      q = self._slug_query()
    else:
      q = self._id_query()
    media_file = q.first()
    if not media_file:
      raise Http404()
    return redirect(media_file.file.url)

  def _slug_query(self):
    slug = self.kwargs.get("slug")
    parts = slug.split("-")
    if parts[0] == "v":
      parts = parts[1:]
    while len(parts) < 3:
      parts.append(None)
    (year, make, model) = parts
    q = models.MediaFile.objects.exclude(deleted=True)
    for key, value in (("year", year), ("make", make), ("model", model)):
      if value is not None:
        q = q.filter(tags__key=key, tags__value=value)
    return q

  def _id_query(self):
    id = self.kwargs.get("id")
    return models.MediaFile.objects.filter(id=id)
