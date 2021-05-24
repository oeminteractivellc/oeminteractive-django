from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _


class WebsiteExclusion(models.Model):

  # The owner of this filter.
  user = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="website_exclusions",
      to=get_user_model(),
      verbose_name=_("user"),
  )

  # The website to exclude.
  website = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="exclusions",
      to="core.Website",
      verbose_name=_("website"),
  )
