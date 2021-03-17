import re

from django.db import models
from django.utils.translation import ugettext_lazy as _

NAME_MAX_LENGTH = 32
SLUG_MAX_LENGTH = 64


class CarMakeModel(models.Model):

  # The display name of the make.
  make = models.CharField(
      blank=False,
      db_index=True,
      null=False,
      max_length=NAME_MAX_LENGTH,
      verbose_name=_("make"),
  )

  # The display name of the model.
  model = models.CharField(
      blank=False,
      db_index=True,
      null=False,
      max_length=NAME_MAX_LENGTH,
      verbose_name=_("model"),
  )

  # Slug format: make-model (no spaces, all lower case)
  slug = models.CharField(
      blank=False,
      db_index=True,
      null=False,
      max_length=SLUG_MAX_LENGTH,
      unique=True,
      verbose_name=_("slug"),
  )

  # The part of the slug that corresponds to the make.
  make_slug = models.CharField(
      blank=False,
      db_index=True,
      null=False,
      max_length=NAME_MAX_LENGTH,
      verbose_name=_("make slug"),
  )

  # The part of the slug that corresponds to the model.
  model_slug = models.CharField(
      blank=False,
      db_index=True,
      null=False,
      max_length=NAME_MAX_LENGTH,
      verbose_name=_("model slug"),
  )

  def slugify_make(self):
    return self.slugify(self.make)

  def slugify_model(self):
    return self.slugify(self.model)

  @staticmethod
  def slugify(name):
    name = name.lower()
    return re.sub(r"[,.;@#?!&$-_ ]+", "", name)
