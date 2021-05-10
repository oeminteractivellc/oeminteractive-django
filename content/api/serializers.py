from rest_framework import serializers

from content.models import ContentConfiguration, ContentSection, ContentVariant


class ContentSectionSerializer(serializers.ModelSerializer):
  class Meta:
    model = ContentSection
    fields = ("id", "name", "slot", "order", "group")


class ContentVariantSerializer(serializers.ModelSerializer):
  class Meta:
    model = ContentVariant
    fields = ("id", "section", "text")


class ListContentVariantSerializer(serializers.ModelSerializer):
  class Meta:
    model = ContentVariant
    fields = ("id", "section", "text")


class ContentConfigurationSerializer(serializers.ModelSerializer):
  class Meta:
    model = ContentConfiguration
    fields = ("id", "key", "config")
