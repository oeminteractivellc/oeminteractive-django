import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core import models
from companalysis.services import WebsiteScanner, WebsiteScanException


class Command(BaseCommand):
  help = "Update the list of manufacturers for a domain."

  def add_arguments(self, parser):
    parser.add_argument("domain", nargs="+", type=str)

  def handle(self, *args, **options):
    for domain in options["domain"]:
      self.stdout.write(self.style.SUCCESS(f"{domain} : scanning"))
      website, _created = models.Website.objects.get_or_create(domain_name=domain)
      try:
        scanner = WebsiteScanner(website)
        manufacturers = scanner.scan_manufacturers()
      except WebsiteScanException as e:
        raise CommandError(str(e))
      for m in manufacturers:
        self.stdout.write(m)
