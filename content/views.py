import logging
import requests

from bs4 import BeautifulSoup
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View, TemplateView

from . import models
from .services import PageBuilder
from core import models as core_models

logger = logging.getLogger(__name__)


class ContentBuilderView(LoginRequiredMixin, TemplateView):
  template_name = "builder.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    if kwargs.get("domain", None):
      domain = kwargs.get("domain")
      website = get_object_or_404(core_models.Website.objects.all(), domain_name=domain)
      context.update({"website": website})
    else:
      websites = core_models.Website.objects.all().order_by("domain_name")
      context.update({"websites": websites})
    if kwargs.get("slug", None):
      slug = kwargs.get("slug")
      if len(slug.split("-")) == 3:
        year, make_slug, model_slug = slug.split("-")
      else:
        year = "*"
        make_slug, model_slug = slug.split("-")
      make_model = get_object_or_404(core_models.CarMakeModel.objects.all(),
                                     make_slug=make_slug,
                                     model_slug=model_slug)
      context.update({"year": year, "make_model": make_model})
    else:
      makes = self.assemble_makes_and_models()
      context.update({"makes": makes})
    return context

  @staticmethod
  def assemble_makes_and_models():
    makes = []
    make_slug = None
    for mm in core_models.CarMakeModel.objects.all().order_by("make", "model"):
      if mm.make_slug != make_slug:
        makes.append({"make": mm.make, "make_slug": mm.make_slug, "models": []})
        make_slug = mm.make_slug
      makes[-1]["models"].append(mm)
    return makes


class ProxyManager:
  proxy = "http://spa7cc30b3:Gnu8s-word@gate.dc.smartproxy.com:20000"
  proxies = {
      "http": proxy,
      "https": proxy,
  } if proxy else None


def get_url(url):
  resp = requests.get(url, timeout=5, proxies=ProxyManager.proxies)
  return resp.text


class PreviewView(View):
  def get(self, request, *args, **kwargs):
    logger.info(f"PreviewView {self.website} {self.slug}")
    ccfg = self.get_content_config()
    logger.info(f"PreviewView {str(ccfg.config)}")
    slot_texts = PageBuilder(ccfg.config, slug=self.slug, website=self.website).build()
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
    return context_params

  def load_rep_page_and_insert_content(self, rep_page_url, slot_texts):
    rep_page_text = get_url(rep_page_url)
    rep_page_soup = BeautifulSoup(rep_page_text, "html.parser")
    slot_containers = self.preprocess_page(rep_page_soup)
    if slot_containers:
      for slot in models.ContentSlot.ALL:
        slot_text = slot_texts[slot.name]
        slot_soup = BeautifulSoup(slot_text, "html.parser")
        slot_containers[slot.name].append(slot_soup)
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
        "meta1": meta,
        "meta2": meta,
    }


class RawView(LoginRequiredMixin, TemplateView):
  template_name = "raw.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    ccfg = self.get_content_config()
    slot_texts = PageBuilder(ccfg.config, slug=self.slug, website=self.website).build()
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
