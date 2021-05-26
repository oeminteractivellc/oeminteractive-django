import logging

from celery import shared_task

from core import models as core_models
from companalysis.services import WebsiteScanner

logger = logging.getLogger(__name__)


@shared_task
def run_full_manufacturer_scrape():
  """ Refresh the manufacturer list for all websites. """
  logger.info("run_full_manufacturer_scrape: START")
  for website in core_models.Website.objects.all():
    logger.info(f"delay run_manufacturer_scrape({website})")
    run_manufacturer_scrape.delay(website.id)
  logger.info("run_full_manufacturer_scrape: DONE")


@shared_task
def run_manufacturer_scrape(website_id):
  """ Refresh the manufacturer list for one website. """
  logger.info(f"run_manufacturer_scrape({website_id}): START")
  website = core_models.Website.objects.get(id=website_id)
  website_scanner = WebsiteScanner(website)
  website_scanner.clear_state()
  try:
    manufacturers = website_scanner.scan_manufacturers()
    logger.info(f"run_manufacturer_scrape({website_id}): RESULTS: {str(manufacturers)}")
  except Exception as e:
    logger.warn(f"run_manufacturer_scrape ERROR {e}")


@shared_task
def run_full_price_scrape():
  """ Find all available prices for all parts. """
  logger.info("run_full_price_scrape: START")
  for part in core_models.Part.objects.filter(is_active=True):
    logger.info(f"delay run_price_scrape({part})")
    run_price_scrape.delay(part.id)
  logger.info("run_full_price_scrape: DONE")


@shared_task
def run_price_scrape(part_id):
  """ Find all available prices for one part. """
  logger.info(f"run_manufacturer_scrape({website_id}): START")
  part = core_models.Part.objects.get(id=part_id)
  for website in core_models.Website.objects.filter(manufacturers__id=part.manufacturer_id,
                                                    is_active=True):
    website_price_scrape(part, website)  # No delay here.  Avoid stressing redis.
  logger.info(f"run_manufacturer_scrape({website_id}): DONE")


def website_price_scrape(part, website):
  """ Find the price of a part on a specific website. """
  logger.info(f"website_price_scrape(part={part}, website={website}): START")
  website_scanner = WebsiteScanner(website)
  try:
    price = website_scanner.scan_price(part)
    logger.info(f"run_price_scrape({part}), {website}: RESULT ${price}")
    logger.info(f"run_website_price_scrape(part_id={part_id}, website_id={website_id}): START")
  except Exception as e:
    logger.warn(f"run_price_scrape({part}), {website}: ERROR {e}")
