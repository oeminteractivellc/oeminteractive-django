from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core import models
from companalysis.services import WebsiteScanner


class Command(BaseCommand):
  help = "Search a website or websites for the price of a part."

  def add_arguments(self, parser):
    parser.add_argument("part_number", nargs=1, type=str)
    parser.add_argument("domain", nargs="?", type=str)

  def handle(self, *args, **options):
    part_number = options["part_number"][0]
    domain = options["domain"]

    try:
      part = models.Part.objects.filter(part_number=part_number).get()
    except models.Part.DoesNotExist:
      raise CommandError(f"{part_number}: no such part")

    if domain:
      website, _created = models.Website.objects.get_or_create(domain_name=domain)
      self._scan_website(website, part)
    else:
      for w in models.Website.objects.filter(manufacturers__id=part.manufacturer_id):
        self._scan_website(w, part)

  def _scan_website(self, website, part):
    self.stdout.write(self.style.SUCCESS(f"Scanning {website.domain_name}..."))
    price = WebsiteScanner(website).scan_for_part_price(part)
    self.stdout.write(self.style.SUCCESS(f"... price of {part} is ${price}"))
