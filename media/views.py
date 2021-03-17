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
    return {"name": filename, "message": "Uploaded", "url": str(media_file)}


class MediaRedirectView(View):
  def get(self, request, *args, **kwargs):
    slug = kwargs.get("slug")
    _v, year, make, model = slug.split("-")
    q = models.MediaFile.objects.exclude(deleted=True)
    for key, value in (("year", year), ("make", make), ("model", model)):
      q = q.filter(tags__key=key, tags__value=value)
    media_file = q.first()
    if not media_file:
      raise Http404()
    return redirect(str(media_file.file))
