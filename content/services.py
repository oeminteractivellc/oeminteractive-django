import logging

from django.conf import settings
from django.template import Template, Context

from . import models

logger = logging.getLogger(__name__)


def server_context_params():
  return {"server_host": settings.SITE_URL, "media_host": settings.MEDIA_URL or settings.SITE_URL}


def website_context_params(website):
  return {
      "website": website,
      "Website": website.capitalize(),  # TODO: lookup display name from Website model.
  }


def appdomain_context_params(slug):  # Awareness of application domain.
  year, make, model = slug.split("-")
  Make = make.capitalize()  # TODO: lookup name from Make model.
  Model = model.capitalize()
  return {
      "Make": Make,
      "Model": Model,
      "make": make,
      "model": model,
      "year": year,
  }


class PageBuilder:
  def __init__(self, ccfg, **kwargs):
    self.ccfg = ccfg
    self.context_params = {}
    self.context_params.update(server_context_params())
    if kwargs.get("website", None):
      self.context_params.update(website_context_params(kwargs.get("website")))
    if kwargs.get("slug", None):
      self.context_params.update(appdomain_context_params(kwargs.get("slug")))
    self._preload_sections()
    self._preload_variants()

  def _preload_sections(self):
    sids = (int(section["sid"]) for section in self.ccfg["sections"])
    all_sections = models.ContentSection.objects.filter(id__in=sids)
    self.sections = dict((str(s.id), s) for s in all_sections)

  def _preload_variants(self):
    vids = (int(section["vid"]) for section in self.ccfg["sections"]
            if "vid" in section and section["vid"])
    all_variants = models.ContentVariant.objects.filter(id__in=vids)
    self.variant_text = dict((str(v.id), v.text) for v in all_variants)

  def build(self):
    slot_text = {}
    for slot in models.ContentSlot.ALL:
      slot_text[slot.name] = ""
      if not slot.is_meta:
        if slot.css_classes:
          slot_text[slot.name] += f'<div class="{slot.css_classes}">'
        else:
          slot_text[slot.name] += f'<div>'
    for s in self.ccfg["sections"]:
      if "vid" in s:
        slot_name = self.sections[str(s["sid"])].slot
        section_text = self._expand_template(str(s["vid"]))
        slot_text[slot_name] += section_text
    for slot in models.ContentSlot.ALL:
      if not slot.is_meta:
        slot_text[slot.name] += f'</div>'
    return slot_text

  def _expand_template(self, variant_id):
    text = self.variant_text.get(variant_id, None)
    if not text:
      logger.error(f"Missing variant {variant_id} referenced in {self.ccfg}")
      return ""
    template = Template(text)
    context = Context(self.context_params)
    return template.render(context)
