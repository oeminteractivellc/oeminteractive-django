from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

ENUM_MAX_LENGTH = 12
CLASS_NAME_MAX_LENGTH = 40


class UploadProgress(models.Model):
  class Meta:
    verbose_name = "Upload tracker"

  # The associated user.
  user = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="uploads",
      to=get_user_model(),
      verbose_name=_("user"),
  )

  # Identify the schema to upload.
  schema = models.CharField(
      blank=True,
      db_index=False,
      null=True,
      max_length=CLASS_NAME_MAX_LENGTH,
      verbose_name=_("type"),
  )

  # Status: "running", "done", "error".
  status = models.CharField(
      blank=False,
      max_length=ENUM_MAX_LENGTH,
      null=False,
      default="running",
      verbose_name=_("status"),
  )

  rows_processed = models.PositiveIntegerField(default=0)
  objects_added = models.PositiveIntegerField(default=0)
  objects_updated = models.PositiveIntegerField(default=0)
  errors = models.JSONField(blank=True, null=True)

  created_at = models.DateTimeField(
      auto_now_add=True,
      editable=False,
      verbose_name=_("created at"),
  )

  updated_at = models.DateTimeField(
      auto_now=True,
      editable=False,
      verbose_name=_("updated at"),
  )
