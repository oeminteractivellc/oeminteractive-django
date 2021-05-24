from django.conf import settings

from .models import Part


def context_settings(request=None):
  return {
      "CostPriceRange": Part.CostPriceRange,
      "PartType": Part.PartType,
  }
