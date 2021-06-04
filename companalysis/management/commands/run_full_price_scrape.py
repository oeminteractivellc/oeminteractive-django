from django.core.management.base import BaseCommand

from companalysis.tasks import run_full_price_scrape


class Command(BaseCommand):
  help = "Scrape prices for all parts - ASYNC."

  def handle(self, *args, **options):
    run_full_price_scrape()
