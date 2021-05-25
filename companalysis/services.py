import requests

from .revolution import RevolutionPartsScanner

from core import models
from utils.proxies import ProxyManager


class WebsiteScanException(Exception):
  """ Exception type that indicates persistent failure to scan the website. """
  pass


DEFAULT_HEADERS = {
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://www.oeminteractive.com",
    "user-agent": "oeminteractive.com",
}

# TODO: set website to inactive when it goes south.


class WebsiteScanner:
  platform_scanner = None

  def __init__(self, website):
    self.website = website

  @property
  def base_url(self):
    return f"https://{self.website.domain_name}"

  def get(self, path, local_headers={}):
    url = f"{self.base_url}/{path}"
    headers = {}
    headers.update(DEFAULT_HEADERS)
    headers.update(local_headers)
    return ProxyManager.get(url, headers=headers)

  def _prescan(self):
    try:
      if self.website.is_active is None:
        is_active = self.check_active()
        self.website.is_active = is_active
      if not self.website.is_active:
        raise WebsiteScanException(
            f"{self.base_url} was found not to be active. Clear_state to retry.")
      if not self.website.platform:
        platform = self.detect_platform()
        self.website.platform = platform
      if not self.website.platform:
        raise WebsiteScanException(f"{self.base_url}: cannot determine platform.")
      self.platform_scanner = self.scanner_for_platform()
      if not self.platform_scanner:
        raise WebsiteScanException(f"Unrecognized platform {self.website.platform}.")
    finally:
      self.website.save()

  def check_active(self):
    try:
      self.get("")
      return True
    except (ProxyManager.SiteNotFoundError, ProxyManager.HttpsError):
      return False

  def detect_platform(self):
    if RevolutionPartsScanner(self).test():
      return "revolution"

  def scanner_for_platform(self):
    if self.website.platform == "revolution":
      return RevolutionPartsScanner(self)  # TODO: support other platforms

  def clear_state(self):
    self.website.is_active = None
    self.website.platform = ""
    self.website.save()

  def scan_manufacturers(self):
    self._prescan()
    manufacturers = self.platform_scanner.scan_manufacturers()
    print('ack')
    print(str(manufacturers))
    self.website.manufacturers.set(
        (models.Manufacturer.objects.get_or_create(name=m)[0] for m in manufacturers))
    return manufacturers
