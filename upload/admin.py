from django.contrib import admin

from . import models


@admin.register(models.UploadProgress)
class ProgressAdmin(admin.ModelAdmin):
  list_display = ("id", "created_at", "schema", "user", "status")
