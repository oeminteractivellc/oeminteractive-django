from django.contrib import admin

from . import models


@admin.register(models.ContentConfiguration)
class ContentConfigurationAdmin(admin.ModelAdmin):
  list_display = ("id", "key")


@admin.register(models.ContentSection)
class ContentSectionAdmin(admin.ModelAdmin):
  list_display = ("id", "name")


@admin.register(models.ContentVariant)
class ContentVariantAdmin(admin.ModelAdmin):
  list_display = ("id", "section")


@admin.register(models.Website)
class WebsiteAdmin(admin.ModelAdmin):
  list_display = ("id", "domain")
