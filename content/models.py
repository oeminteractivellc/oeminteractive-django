from django.db import models
from django.utils.translation import ugettext_lazy as _

NAME_MAX_LENGTH = 24


class ContentSlot:
  """
    A slot is a position in the page at which to insert content.
    Enumerate the set of slot types supported by the system.  The set is static.
  """
  NAMES = ("body", "meta1", "meta2", "header", "footer")
  CHOICES = ((x, x) for x in NAMES)


class ContentSection(models.Model):
  """
    A logical section of the output document.  A slot is populated with a list of sections.  The contents of
      each section depend on random selection from among its variants.  """

  # Each content section has a name.
  name = models.CharField(
      blank=False,
      db_index=True,
      null=False,
      max_length=NAME_MAX_LENGTH,
      unique=True,
      verbose_name=_("section id"),
  )

  # The slot in which to place this section. (see ContentSlot above)
  slot = models.CharField(
      blank=False,
      choices=ContentSlot.CHOICES,
      default="body",
      db_index=True,
      null=False,
      max_length=NAME_MAX_LENGTH,
      verbose_name=_("slot"),
  )

  # The order relative to other sections in the same slot (lower appears higher).
  order = models.IntegerField(blank=True, default=0, null=False, verbose_name=_("order"))

  # Optional name of a special group of sections to which this section belongs.
  # Groups may be added/removed from the selected list in bulk.
  group = models.CharField(blank=True,
                           null=True,
                           max_length=NAME_MAX_LENGTH,
                           verbose_name=_("group"))

  def __str__(self):
    return self.name


class ContentVariant(models.Model):
  """
    There may be many variants for a single section.
  """

  # The section that this text is intended for.
  section = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="variants",
      to=ContentSection,
      verbose_name=_("section"),
  )

  # The HTML text.
  text = models.TextField(
      blank=False,
      null=False,
      verbose_name=_("text"),
  )

  # For soft deletion.
  deleted = models.BooleanField(
      blank=True,
      default=False,
      null=True,
      verbose_name=("deleted"),
  )


class ContentConfiguration(models.Model):
  """
    Key-value storage for content configurations. 
  """

  # In practice, the key is a serialized website-year-make-model tuple.
  key = models.TextField(
      blank=False,
      db_index=True,
      null=False,
      unique=True,
      verbose_name=_("key"),
  )

  # Structured configuration:
  # .sections[]
  #   .sid       # section id
  #   .vid       # bound variant id
  config = models.JSONField()


class Website(models.Model):
  """
    Content goes into websites, after all.
  """

  # All lower case. Also serves as a key
  domain = models.CharField(
      blank=False,
      db_index=True,
      null=False,
      max_length=NAME_MAX_LENGTH,
      unique=True,
      verbose_name=_("domain name"),
  )

  display_name = models.CharField(
      blank=False,
      null=False,
      max_length=NAME_MAX_LENGTH,
      verbose_name=_("display name"),
  )
