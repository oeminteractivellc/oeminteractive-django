import requests

from django.core.management.base import BaseCommand

from utils.proxies import ProxyManager


class Command(BaseCommand):
  help = "Run a web request through the proxy and dump the results to the console."

  def add_arguments(self, parser):
    parser.add_argument("url", nargs=1, type=str)

  def handle(self, *args, **options):
    url = options["url"][0]
    r = ProxyManager.get(url)
    r.raise_for_status()
    self.stdout.write(r.text)
