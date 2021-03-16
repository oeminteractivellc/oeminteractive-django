from django.contrib import admin

from . import models


@admin.register(models.CarMakeModel)
class CarMakeModelAdmin(admin.ModelAdmin):
  list_display = ("slug", "make", "model")
