from django.conf import settings

from .models import Part, PartType


def context_settings(request=None):
  return {
      "CostPriceRange": Part.CostPriceRange,
      "PartType": PartType,
  }
