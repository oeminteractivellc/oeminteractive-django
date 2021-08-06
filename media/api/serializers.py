from django.conf import settings
from rest_framework import serializers

from media.models import MediaFile


class MediaFileSerializer(serializers.ModelSerializer):
  url = serializers.SerializerMethodField()
  tags = serializers.SerializerMethodField()

  class Meta:
    model = MediaFile
    fields = ("id", "url", "created_at", "tags")

  def get_url(self, obj):
    return f"{settings.MEDIA_SITE_URL}/media/m/{obj.id}"

  def get_tags(self, obj):
    return {tag.key: tag.value for tag in obj.tags.all()}
