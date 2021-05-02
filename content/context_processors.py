from django.conf import settings
from django.utils import timezone

from .models import ContentSlot


def context_settings(request=None):
  return {
      "slots": ContentSlot.ALL,
      "slot_names": ContentSlot.NAMES,
  }
