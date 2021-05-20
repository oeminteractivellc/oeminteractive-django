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


class PartsLoader(GenericLoader):

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
    fields["manufacturer"] = Manufacturer.objects.get(name=data["manufacturer"])
    return keys, fields


class PricesLoader(GenericLoader):

  KEY_FIELDS = ["date", "website", "partnumber"]
  FIELDS = ["partprice"]
  MODEL_CLASS = models.PartPrice

  def _map_data(self, data):
    keys = {}
    fields = {}
    keys["date"] = data["date"]
    keys["website"] = Website.objects.get(domain_name=data["website"])
    keys["part"] = Part.objects.get(part_number=data["partnumber"])
    fields["price"] = data["partprice"]
    return keys, fields


class CostsLoader(GenericLoader):

  KEY_FIELDS = ["date", "partnumber"]
  FIELDS = ["cost"]
  MODEL_CLASS = models.PartCostPoint

  def _map_data(self, data):
    keys = {}
    fields = {}
    keys["start_date"] = data["date"]
    keys["part"] = Part.objects.get(part_number=data["partnumber"])
    fields["cost"] = data["cost"]
    return keys, fields
