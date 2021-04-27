from django.contrib import admin

from . import models


@admin.register(models.ContentConfiguration)
class ContentConfigurationAdmin(admin.ModelAdmin):
  list_display = ("id", "key")


@admin.register(models.ContentSection)
class ContentSectionAdmin(admin.ModelAdmin):
  list_display = ("name", "slot", "order")


@admin.register(models.ContentVariant)
class ContentVariantAdmin(admin.ModelAdmin):
  list_display = ("section", "id")


@admin.register(models.Website)
class WebsiteAdmin(admin.ModelAdmin):
  list_display = ("id", "domain")
