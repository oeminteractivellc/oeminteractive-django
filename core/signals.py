from django.db.models.signals import pre_save
from django.dispatch import receiver

from . import models


@receiver(pre_save, sender=models.CarMakeModel)
def set_carmakemodel_slug_fields(sender, instance, **kwargs):
  instance.make_slug = instance.slugify_make()
  instance.model_slug = instance.slugify_model()
  instance.slug = f"{instance.make_slug}-{instance.model_slug}"
