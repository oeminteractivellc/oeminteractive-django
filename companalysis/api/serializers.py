from rest_framework import serializers

from core import models


class ManufacturerSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Manufacturer
    fields = ("id", "name")


class PartSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Part
    fields = ("id", "part_number", "part_type", "cost_price_range", "manufacturer")


class WebsiteSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Website
    fields = ("id", "domain_name", "is_client", "start_date")
