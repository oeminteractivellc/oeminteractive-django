from upload.csvbase import GenericLoader

from . import models


class CarMakeModelLoader(GenericLoader):

  FIELDS = ["make", "model"]
  MODEL_CLASS = models.CarMakeModel

  def _map_data(self, data):
    keys = {}
    fields = {}
    make = data["make"]
    model = data["model"]
    keys["make_slug"] = models.CarMakeModel.slugify(make)
    keys["model_slug"] = models.CarMakeModel.slugify(model)
    fields["make"] = data["make"]
    fields["model"] = data["model"]
    return keys, fields


class PartLoader(GenericLoader):

  KEY_FIELDS = ["partnumber"]
  FIELDS = ["parttype", "costpricerange", "title", "manufacturer"]
  MODEL_CLASS = models.Part

  def _map_data(self, data):
    keys = {}
    fields = {}
    keys["part_number"] = data["partnumber"]
    fields["part_type"] = data["parttype"]
    fields["cost_price_range"] = data["costpricerange"]
    fields["title"] = data["title"]
    try:
      fields["manufacturer"] = models.Manufacturer.objects.get(name=data["manufacturer"])
    except models.Manufacturer.DoesNotExist:
      raise ValueError(f"Unrecognized manufacturer: {data['manufacturer']}")
    return keys, fields


class PartPriceLoader(GenericLoader):

  KEY_FIELDS = ["date", "website", "partnumber"]
  FIELDS = ["partprice"]
  MODEL_CLASS = models.PartPrice

  def _map_data(self, data):
    keys = {}
    fields = {}
    keys["date"] = data["date"]
    try:
      keys["website"] = models.Website.objects.get(domain_name=data["website"])
    except models.Website.DoesNotExist:
      raise ValueError(f"Unrecognized domain name: {data['website']}")
    try:
      keys["part"] = models.Part.objects.get(part_number=data["partnumber"])
    except models.Part.DoesNotExist:
      raise ValueError(f"Bad part number: {data['partnumber']}")
    fields["price"] = data["partprice"]
    return keys, fields


class PartCostPointLoader(GenericLoader):

  KEY_FIELDS = ["date", "partnumber"]
  FIELDS = ["cost"]
  MODEL_CLASS = models.PartCostPoint

  def _map_data(self, data):
    keys = {}
    fields = {}
    keys["start_date"] = data["date"]
    try:
      keys["part"] = models.Part.objects.get(part_number=data["partnumber"])
    except models.Part.DoesNotExist:
      raise ValueError(f"Bad part number: {data['partnumber']}")
    fields["cost"] = data["cost"]
    return keys, fields


class WebsiteLoader(GenericLoader):

  KEY_FIELDS = ["domainname"]
  FIELDS = ["title", "isclient"]
  MODEL_CLASS = models.Website

  def _map_data(self, data):
    keys = {}
    fields = {}
    keys["domain_name"] = data["domainname"].lower()
    fields["title"] = data["title"]
    fields["is_client"] = data["isclient"].lower() in ("yes", "y", "true", "x")
    return keys, fields
