import logging

from django.conf import settings
from django.template import Template, Context

from core import models as core_models
from . import models

logger = logging.getLogger(__name__)


def server_context_params():
  return {"server_host": settings.SITE_URL, "media_host": settings.MEDIA_SITE_URL}


def config_context_params(ccfg):
  image_url = None
  if ccfg.get("selectedImage", None):
    image_url = ccfg.get("selectedImage")
  return {"image_url": image_url}


def website_context_params(domain_name):
  website = core_models.Website.objects.filter(domain_name=domain_name).first()
  title = website.title if website and website.title else domain_name
  return {
      "website": domain_name,
      "Website": title,
  }


def appdomain_context_params(slug):  # Awareness of application domain.
  slugparts = slug.split("-")
  if len(slugparts) == 2:
    year = None
    (make, model) = slugparts
  elif len(slugparts) == 3:
    (year, make, model) = slugparts
  else:
    raise ValueError(slug)
  Make = make.capitalize()  # TODO: lookup name from Make model.
  Model = model.capitalize()
  params = {
      "Make": Make,
      "Model": Model,
      "make": make,
      "model": model,
  }
  if year is not None:
    params.update({
        "year": year,
    })
  return params


class PageBuilder:
  def __init__(self, ccfg, **kwargs):
    self.ccfg = ccfg
    self.context_params = {}
    self.context_params.update(server_context_params())
    self.context_params.update(config_context_params(ccfg))
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
      if "vid" in s and s["vid"] is not None:
        slot_name = self.sections[str(s["sid"])].slot
        section_text = self._expand_template(str(s["vid"]))
        slot_text[slot_name] += section_text
        slot_text[slot_name] += " "
    for slot in models.ContentSlot.ALL:
      slot_text[slot.name] = slot_text[slot.name].strip()
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
