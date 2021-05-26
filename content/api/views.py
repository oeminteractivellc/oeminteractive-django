import logging

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from content import models
from content.services import PageBuilder
from content.api import serializers

logger = logging.getLogger(__name__)


class ListCreateContentSectionView(generics.ListCreateAPIView):
  queryset = models.ContentSection.objects.all().order_by("order", "id")
  serializer_class = serializers.ContentSectionSerializer


class RetrieveUpdateContentSectionView(generics.RetrieveUpdateAPIView):
  queryset = models.ContentSection.objects.all()
  serializer_class = serializers.ContentSectionSerializer


class ListCreateContentVariantView(generics.ListCreateAPIView):
  queryset = models.ContentVariant.objects.exclude(deleted=True).order_by("id")

  def get_serializer_class(self, *args, **kwargs):
    if self.request.method == "GET":
      return serializers.ListContentVariantSerializer
    else:
      return serializers.ContentVariantSerializer


class RetrieveUpdateContentVariantView(generics.RetrieveUpdateDestroyAPIView):
  queryset = models.ContentVariant.objects.exclude(deleted=True)
  serializer_class = serializers.ContentVariantSerializer


class RetrieveContentConfigurationView(generics.RetrieveAPIView):
  def get(self, request, *args, **kwargs):
    key = kwargs.get("key")
    obj = get_object_or_404(models.ContentConfiguration.objects.all(), key=key)
    data = serializers.ContentConfigurationSerializer(obj).data
    return Response(data)


class CreateContentConfigurationView(generics.CreateAPIView):
  def create(self, request, *args, **kwargs):
    key = request.data.get("key")
    config = request.data.get("config")
    obj, _created = models.ContentConfiguration.objects.update_or_create(
        key=key, defaults={"config": config})
    data = serializers.ContentConfigurationSerializer(obj).data
    return Response(data)


class GetContentView(generics.RetrieveAPIView):
  def post(self, request, *args, **kwargs):
    key = request.data.get("key")
    config = request.data.get("config")
    logger.info(f"{key} {config}")

    keyparts = key.split("-")
    if len(keyparts) == 3:
      (_website, make, model) = keyparts
      slug = f"{make}-{model}"
    elif len(keyparts) == 4:
      (_website, year, make, model) = keyparts
      slug = f"{year}-{make}-{model}"
    else:
      raise ValidationError("invalid content key")

    data = PageBuilder(config, slug=slug).build()
    return Response(data)
