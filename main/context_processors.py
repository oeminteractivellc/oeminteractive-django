from django.conf import settings
from django.utils import timezone


def context_settings(request=None):
  return {
      "DEBUG":
      settings.DEBUG,
      "DEMO":
      settings.DEMO,
      "STAGING":
      settings.STAGING,
      "admin_apps": (
          {
              "title":
              "Image Overlay",
              "url":
              "/imageoverlay",
              "icon":
              "img/ford.jpeg",
              "description":
              "Manage automatic generation of generic product images for Google Marketplace."
          },
          {
              "title": "SEO Landing Page Builder",
              "url": "/content/builder",
              "icon": "img/manufacture.svg",
              "description": "Assemble content for SEO landing pages."
          },
          {
              "title": "SEO Landing Page Content Catalog",
              "url": "/seolp-catalog",
              "icon": "img/blocks.png",
              "description": "Define the content sections that make up SEO landing pages."
          },
          {
              "title":
              "Media Manager",
              "url":
              "/seolp-media",
              "icon":
              "img/media.png",
              "description":
              "Upload and tag images to cloud storage to appear in SEO landing pages (and other web pages)."
          },
          {
              "title": "Competitive Analysis",
              "url": "https://oemcompanalysis.herokuapp.com",
              "icon": "img/competition.svg",
              "description": "Run competitive pricing analysis reports."
          },
          {
              "title":
              "Data Admin",
              "url":
              "/admin123",
              "icon":
              "img/chest.png",
              "description":
              "Manage users, makes, models, parts, and other data entities used in the admin apps."
          },
          {
              "title": "VIN Decoder",
              "url": "/proxyadmin/decoder.php",
              "icon": "img/vindecoder.png",
              "description": "Manage VIN Decoder pages and settings.  Retrieve insert code."
          },
          {
              "title": "Dealer Pass",
              "url": "/proxyadmin/dealerpass.php",
              "icon": "img/dealerpass.png",
              "description": "Manage Dealer Pass pages and settings.  Retrieve insert code."
          },
          {
              "title": "cPanel",
              "url": "https://oeminteractive.com:2083",
              "icon": "img/cpanel.png",
              "description": "Link to cPanel Login."
          },
          {
              "title": "Client Portal",
              "url": "https://oeminteractive.com/client-portal-login/",
              "icon": "img/ClientPortal.png",
              "description": "Link to our Client Portal Login."
          },
      ),
      "slots": (
          {
              "name": "header",
              "tip": "These sections appear at the top of the page."
          },
          {
              "name": "meta1",
              "tip": "Meta tags add SEO information to the page but are not visible."
          },
          {
              "name": "meta2",
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
      "year_range": [(timezone.now().year - off) for off in range(10)],
  }
