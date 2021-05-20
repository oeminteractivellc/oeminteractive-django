import csv
import logging

from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path
from io import TextIOWrapper

from . import models
from upload.admin_utils import CsvEnabledModelAdminMixin

logger = logging.getLogger(__name__)


@admin.register(models.Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "name",
  )
  search_fields = ("name", )


@admin.register(models.Website)
class WebsiteAdmin(CsvEnabledModelAdminMixin, admin.ModelAdmin):
  list_display = (
      "domain_name",
      "title",
  )
  list_filter = ("is_active", )
  search_fields = ("domain_name", "title")

  class Meta:
    Model = models.Website


@admin.register(models.CarMakeModel)
class CarMakeModelAdmin(CsvEnabledModelAdminMixin, admin.ModelAdmin):
  class Meta:
    Model = models.CarMakeModel

  list_display = ("slug", "make", "model")
  readonly_fields = ("slug", "make_slug", "model_slug")


@admin.register(models.Part)
class PartAdmin(CsvEnabledModelAdminMixin, admin.ModelAdmin):
  list_display = ("id", "part_number", "manufacturer")
  search_fields = ("part_number", "title")
  list_filter = (
      AutocompleteFilterFactory("Manufacturer", "manufacturer"),
      "part_type",
      "cost_price_range",
  )

  class Meta:
    Model = models.Part

  class Media:  # See django-admin-autocomplete-filter docs
    pass


@admin.register(models.PartPrice)
class PartPriceAdmin(CsvEnabledModelAdminMixin, admin.ModelAdmin):
  list_display = (
      "id",
      "date",
      "part",
  )
  list_filter = (
      AutocompleteFilterFactory("Part", "part"),
      AutocompleteFilterFactory("Website", "website"),
      "date",
  )

  class Meta:
    Model = models.PartPrice


@admin.register(models.PartCostPoint)
class PartCostPointAdmin(CsvEnabledModelAdminMixin, admin.ModelAdmin):
  list_display = (
      "id",
      "start_date",
      "part",
  )
  list_filter = (AutocompleteFilterFactory("Part", "part"), "start_date")

  class Meta:
    Model = models.PartCostPoint
