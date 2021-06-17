import logging

from celery import shared_task

from core import models as core_models
from companalysis.services import WebsiteScanner


@shared_task
def speak():
  print("speaking")


@shared_task
def run_full_manufacturer_scrape():
  """ Refresh the manufacturer list for all websites. """
  print("run_full_manufacturer_scrape: START")
  for website in core_models.Website.objects.all():
    print(f"delay run_manufacturer_scrape({website})")
    run_manufacturer_scrape.delay(website.id)
  print("run_full_manufacturer_scrape: DONE")


@shared_task
def run_manufacturer_scrape(website_id):
  """ Refresh the manufacturer list for one website. """
  print(f"run_manufacturer_scrape({website_id}): START")
  website = core_models.Website.objects.get(id=website_id)
  website_scanner = WebsiteScanner(website)
  website_scanner.clear_state()
  try:
    manufacturers = website_scanner.scan_manufacturers()
    print(f"run_manufacturer_scrape({website_id}): RESULTS: {str(manufacturers)}")
  except Exception as e:
    print(f"run_manufacturer_scrape ERROR {e}")


@shared_task
def run_full_price_scrape():
  """ Find all available prices for all parts. """
  print("run_full_price_scrape: START")
  for part in core_models.Part.objects.filter(is_active=True):
    print(f"delay run_price_scrape({part})")
    run_price_scrape.delay(part.id)
  print("run_full_price_scrape: DONE")


@shared_task
def run_price_scrape(part_id):
  """ Find all available prices for one part. """
  print(f"run_price_scrape({part_id}): START")
  part = core_models.Part.objects.get(id=part_id)
  for website in core_models.Website.objects.filter(manufacturers__id=part.manufacturer_id,
                                                    is_active=True):
    website_price_scrape(part, website)  # No delay here.  Avoid stressing redis.
  print(f"run_price_scrape({part_id}): DONE")


def website_price_scrape(part, website):
  """ Find the price of a part on a specific website. """
  print(f"website_price_scrape(part={part}, website={website}): START")
  website_scanner = WebsiteScanner(website)
  try:
    price = website_scanner.scan_for_part_price(part)
    if price is None:
      print(f"run_price_scrape({part}), {website}: RESULT -- none --")
    else:
      print(f"run_price_scrape({part}), {website}: RESULT ${price}")
    print(f"run_website_price_scrape(part={part}, website={website}): START")
  except Exception as e:
    print(f"run_price_scrape({part}), {website}: ERROR {e}")
