from django.conf import settings
from rest_framework import serializers

from media.models import MediaFile


class MediaFileSerializer(serializers.ModelSerializer):
  url = serializers.SerializerMethodField()

  class Meta:
    model = MediaFile
    fields = ("id", "url", "created_at")

  def get_url(self, obj):
    return f"{settings.MEDIA_SITE_URL}/media/m/{obj.id}"
