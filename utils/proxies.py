import requests

from django.conf import settings

TIMEOUT_SECONDS = 4


class ProxyManager:
  class HttpsError(Exception):
    pass

  class SiteNotFoundError(Exception):
    pass

  class NetworkError(Exception):
    pass

  class ContentError(Exception):
    pass

  proxy = settings.PROXY_URL
  proxies = {
      "http": proxy,
      "https": proxy,
  } if proxy else None

  @classmethod
  def get(cls, url, headers={}):
    try:
      r = requests.get(url, timeout=TIMEOUT_SECONDS, headers=headers, proxies=cls.proxies)
      if r.status_code != 200:
        raise cls.ContentError(r.status_code)
      return r
    except requests.exceptions.ProxyError:
      raise cls.SiteNotFoundError()
