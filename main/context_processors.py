from django.conf import settings


def context_settings(request=None):
  return {
      "DEBUG":
      settings.DEBUG,
      "DEMO":
      settings.DEMO,
      "STAGING":
      settings.STAGING,
      "slots": (
          {
              "name": "header",
              "tip": "These sections appear at the top of the page."
          },
          {
              "name": "meta",
              "tip": "Meta tags add SEO information to the page but are not visible."
          },
          {
              "name": "body",
              "tip": "These sections appear in the main section of the page."
          },
          {
              "name": "footer",
              "tip": "These sections appear at the bottom of the page."
          },
      ),  # TODO: find a new home for this.
  }
