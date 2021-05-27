from django.db import models
from django.utils.translation import ugettext_lazy as _

NAME_MAX_LENGTH = 24


class ContentSlot:
  """
    A slot is a position in the page at which to insert content.
    Enumerate the set of slot types supported by the system.  The set is static.
  """
  HEADER = "header"
  META1 = "meta1"
  META2 = "meta2"
  BODY = "body"
  FOOTER = "footer"

  class Descriptor:
    def __init__(self, name, **kwargs):
      self.name = name
      self.tip = kwargs.get("tip")
      self.is_meta = kwargs.get("is_meta", False)
      self.css_classes = kwargs.get("css_classes", "")

  ALL = (
      Descriptor(
          name=HEADER,
          tip="These sections appear at the top of the page.",
          is_meta=True,  # Even though it's not meta, we don't want wrapper div.
      ),
      Descriptor(
          name=META1,
          tip="Meta tags add SEO information to the page but are not visible.",
          is_meta=True,
      ),
      Descriptor(
          name=META2,
          tip="Meta tags add SEO information to the page but are not visible.",
          is_meta=True,
      ),
      Descriptor(
          name=BODY,
          tip="These sections appear in the main section of the page.",
          css_classes="oem-ymm-body",
      ),
      Descriptor(
          name=FOOTER,
          tip="These sections appear at the bottom of the page.",
          css_classes="oem-ymm-footer",
      ),
  )

  SLOT_BY_NAME = {(s.name, s) for s in ALL}

  NAMES = (s.name for s in ALL)
  CHOICES = ((n, n) for n in NAMES)


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
