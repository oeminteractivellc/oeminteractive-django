import logging
import requests

from bs4 import BeautifulSoup
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import Template, Context
from django.views.generic import View, TemplateView

from . import models

logger = logging.getLogger(__name__)


class ProxyManager:
  proxy = "http://spa7cc30b3:Gnu8s-word@gate.dc.smartproxy.com:20000"
  proxies = {
      "http": proxy,
      "https": proxy,
  } if proxy else None


def get_url(url):
  resp = requests.get(url, timeout=5, proxies=ProxyManager.proxies)
  return resp.text


def server_context_params():
  return {
      "server_host": settings.SITE_URL,
  }


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
  def __init__(self, ccfg, context_params):
    self.ccfg = ccfg
    self.context_params = context_params
    self._preload_sections()
    self._preload_variants()

  def _preload_sections(self):
    sids = (int(section["sid"]) for section in self.ccfg.config["sections"])
    all_sections = models.ContentSection.objects.filter(id__in=sids)
    self.sections = dict((str(s.id), s) for s in all_sections)

  def _preload_variants(self):
    vids = (int(section["vid"]) for section in self.ccfg.config["sections"] if "vid" in section)
    all_variants = models.ContentVariant.objects.filter(id__in=vids)
    self.variant_text = dict((str(v.id), v.text) for v in all_variants)

  def build(self):
    slot_text = {}
    for slot_name in models.ContentSlot.NAMES:
      slot_text[slot_name] = ""
    for s in self.ccfg.config["sections"]:
      if "vid" in s:
        slot_name = self.sections[str(s["sid"])].slot
        section_text = self.expand_template(str(s["vid"]))
        slot_text[slot_name] += section_text
    return slot_text

  def expand_template(self, variant_id):
    template = Template(self.variant_text[variant_id])
    context = Context(self.context_params)
    return template.render(context)


class PreviewView(View):
  def get(self, request, *args, **kwargs):
    logger.info(f"PreviewView {self.website} {self.slug}")
    ccfg = self.get_content_config()
    logger.info(f"PreviewView {str(ccfg.config)}")
    slot_texts = PageBuilder(ccfg, self.get_context_params()).build()
    logger.info(f"PreviewView {slot_texts}")
    page_text = self.load_rep_page_and_insert_content(self.get_rep_page_url(), slot_texts)
    return HttpResponse(page_text)

  @property
  def website(self):
    return self.request.GET.get("website")

  @property
  def slug(self):
    return self.request.GET.get("slug")

  def get_content_config(self):
    return get_object_or_404(models.ContentConfiguration.objects.all(),
                             key=f"{self.website}-{self.slug}")  # App domain knowledge

  def get_rep_page_url(self):
    return f"https://www.{self.website}/v-{self.slug}"

  def get_context_params(self):
    context_params = {}
    context_params.update(website_context_params(self.website))
    context_params.update(appdomain_context_params(self.slug))
    context_params.update(server_context_params())
    return context_params

  def load_rep_page_and_insert_content(self, rep_page_url, slot_texts):
    rep_page_text = get_url(rep_page_url)
    rep_page_soup = BeautifulSoup(rep_page_text, "html.parser")
    slot_containers = self.preprocess_page(rep_page_soup)
    if slot_containers:
      for slot_name in models.ContentSlot.NAMES:
        slot_text = slot_texts[slot_name]
        slot_soup = BeautifulSoup(slot_text, "html.parser")
        slot_containers[slot_name].append(slot_soup)
    return str(rep_page_soup)

  def preprocess_page(self, rep_page_soup):
    # Awareness of site's page layout.
    picker = rep_page_soup.find("div", class_="oem-vehicle-picker-module")
    if not picker:
      return None
    body = picker.parent.parent
    picker.extract()
    left_content = rep_page_soup.find("div", class_="left-content")
    left_content.find("h1").extract()
    left_content.find("h3").extract()
    footer = rep_page_soup.find("footer")
    meta = rep_page_soup.find("head")
    return {
        "body": body,
        "header": left_content,
        "footer": footer,
        "meta": meta,
    }


class RawView(TemplateView):
  template_name = "raw.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    ccfg = self.get_content_config()
    slot_texts = PageBuilder(ccfg, self.get_context_params()).build()
    context.update(self.get_context_params())
    context.update({"slot_texts": slot_texts})
    return context

  @property
  def website(self):
    return self.request.GET.get("website")

  @property
  def slug(self):
    return self.request.GET.get("slug")

  def get_content_config(self):
    return get_object_or_404(models.ContentConfiguration.objects.all(),
                             key=f"{self.website}-{self.slug}")  # App domain knowledge

  def get_rep_page_url(self):
    return f"https://www.{self.website}/v-{self.slug}"

  def get_context_params(self):
    context_params = {}
    context_params.update(website_context_params(self.website))
    context_params.update(appdomain_context_params(self.slug))
    context_params.update(server_context_params())
    return context_params
