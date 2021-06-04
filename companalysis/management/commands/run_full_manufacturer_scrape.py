from django.core.management.base import BaseCommand

from companalysis.tasks import run_full_manufacturer_scrape


class Command(BaseCommand):
  help = "Update the list of manufacturers for all domains - ASYNC."

  def handle(self, *args, **options):
    run_full_manufacturer_scrape()
