import re

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

ENUM_MAX_LENGTH = 16
NAME_MAX_LENGTH = 32
SLUG_MAX_LENGTH = 64


class Manufacturer(models.Model):
  """
    A manufacturer of automobiles and/or automobile parts.
  """
  class Meta:
    verbose_name = "Manufacturer"

  # The manufacturer name, e.g. "Subaru"
  name = models.CharField(blank=False,
                          null=False,
                          max_length=NAME_MAX_LENGTH,
                          unique=True,
                          verbose_name=_("name"))

  def __str__(self):
    return self.name


class Website(models.Model):
  """
    A part vendor website.
  """

  # The site domain name, e.g. "subaruautomotiveparts.com"
  domain_name = models.CharField(blank=False,
                                 db_index=True,
                                 null=False,
                                 max_length=NAME_MAX_LENGTH,
                                 unique=True,
                                 verbose_name=_("domain name"))

  # The site name.
  title = models.CharField(blank=True,
                           null=True,
                           max_length=NAME_MAX_LENGTH,
                           unique=False,
                           verbose_name=_("title"))

  # A site can sell parts from multiple manufacturers.
  manufacturers = models.ManyToManyField(to=Manufacturer,
                                         blank=True,
                                         verbose_name=_("manufacturers"))

  # Is this site an OEM client?
  is_client = models.BooleanField(
      blank=False,
      null=False,
      default=False,
      verbose_name=_("is client"),
  )

  # When did entry of data from this site start?
  start_date = models.DateField(
      auto_now_add=True,
      blank=False,
      null=False,
      verbose_name=("start date"),
  )

  # Was this site still reachable, last we checked?
  is_active = models.BooleanField(
      blank=False,
      null=False,
      default=True,
      verbose_name=_("is active"),
  )

  def __str__(self):
    return self.domain_name


class CarMakeModel(models.Model):
  """
    A car make and model.
  """
  class Meta:
    verbose_name = "Car Make/Model"
    verbose_name_plural = "Car Make/Models"

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
    return re.sub(r"[,.;@#?!&$\-_ ]+", "", name)


class Part(models.Model):
  """
    An automotive part or accessory.
  """
  class Meta:
    verbose_name = "Car Part"
    verbose_name_plural = "Car Parts"

  # The commercial ID as it appears in a part catalog.
  part_number = models.CharField(
      blank=False,
      db_index=True,
      null=False,
      max_length=NAME_MAX_LENGTH,
      unique=True,
      verbose_name=_("part number"),
  )

  class PartType(object):
    PART = "Part"
    ACCESSORY = "Accessory"
    DEFAULT = PART
    CHOICES = ((PART, PART), (ACCESSORY, ACCESSORY))

  # "Part" or "Accessory"
  part_type = models.CharField(blank=False,
                               null=False,
                               max_length=ENUM_MAX_LENGTH,
                               default=PartType.DEFAULT,
                               choices=PartType.CHOICES,
                               verbose_name=_("type"))

  # Descriptive text
  title = models.TextField(
      blank=True,
      db_index=False,
      null=True,
      verbose_name=_("title"),
  )

  class CostPriceRange(object):
    # VALUES appear in display order.
    # 500+ applies only to accessories, while 500-1000, 1000-2000 and 2000+ apply to parts.
    VALUES = ("0-50", "50-100", "100-150", "150-200", "200-250", "250-500", "500+", "500-1000",
              "1000-2000", "2000+")
    DEFAULT = VALUES[0]
    CHOICES = ((v, v) for v in VALUES)

  # "0-50", "50-100", etc.
  cost_price_range = models.CharField(blank=False,
                                      null=False,
                                      max_length=ENUM_MAX_LENGTH,
                                      default=CostPriceRange.DEFAULT,
                                      choices=CostPriceRange.CHOICES,
                                      verbose_name=_("cost price range"))

  # The manufacturer of the part.
  manufacturer = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="parts",
      to=Manufacturer,
      verbose_name=_("manufacturer"),
  )

  # Do maintain pricing information for this part.
  is_active = models.BooleanField(
      blank=False,
      null=False,
      default=True,
      verbose_name=_("is active"),
  )

  def __str__(self):
    return self.part_number

  @property
  def manufacturer_name(self):
    return self.manufacturer.name


class PartPrice(models.Model):
  """
    Price of a part by vendor on a particular day.
  """
  class Meta:
    verbose_name = "Car Part Price"
    verbose_name_plural = "Car Part Prices"

  # The date for which this price was obtained.
  date = models.DateField(
      blank=False,
      db_index=True,
      null=False,
      verbose_name=_("date"),
  )

  # The associated part.
  part = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="part_prices",
      to=Part,
      verbose_name=_("part"),
  )

  # The website that the price was obtained from.
  website = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="part_prices",
      to=Website,
      verbose_name=_("website"),
  )

  # The price.
  price = models.DecimalField(
      blank=False,
      decimal_places=2,
      max_digits=9,
      null=False,
      verbose_name=_("price"),
  )

  @property
  def part_number(self):
    return self.part.part_number


class PartCostPoint(models.Model):
  """
    Cost of a part on a particular date.
  """
  class Meta:
    verbose_name = "Car Part Cost"
    verbose_name_plural = "Car Part Costs"

  # The associated part.
  part = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="part_cost_points",
      to=Part,
      verbose_name=_("part"),
  )

  # The first date for which this cost applies.
  start_date = models.DateField(
      blank=False,
      db_index=True,
      null=False,
      verbose_name=_("start date"),
  )
  # The cost.
  cost = models.DecimalField(
      blank=False,
      decimal_places=2,
      max_digits=9,
      null=False,
      verbose_name=_("cost"),
  )

  @property
  def part_number(self):
    return self.part.part_number
