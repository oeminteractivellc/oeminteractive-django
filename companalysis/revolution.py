import logging

from lxml import html

from utils.proxies import ProxyManager

logger = logging.getLogger(__name__)


class RevolutionPartsScanner:
  """ Revolution Parts platform scanning logic. """
  def __init__(self, website_scanner):
    self.website_scanner = website_scanner

  def test(self):
    try:
      self.scan_manufacturers()
      return True
    except ProxyManager.ContentError:
      return False

  def scan_manufacturers(self):
    path = "/ajax/vehicle-picker/makes/all"
    local_headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "referer": self.website_scanner.base_url,
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }
    r = self.website_scanner.get(path, local_headers=local_headers)
    rj = r.json()
    return [obj["ui"] for obj in rj]

  def scan_part_price(self, part_number):
    path = "/search?search_str={part_number}"
    local_headers = {
        "referer": self.website_scanner.base_url,
    }
    r = self.website_scanner.get(path, local_headers=local_headers)
    r.raise_for_status()
    htmldoc = html.fromstring(r.content)
    prices = htmldoc.xpath('//span[contains(@class,"sale-price-amount")]/text()')
    if prices:
      price = prices[0].replace("$", "").replace(",", "")
      return price
