class CarMakeModelSchema:
  headers = ("Make", "Model")
  fields = (lambda obj: obj.make, lambda obj: obj.model)


class PartSchema:
  headers = ("PartNumber", "PartType", "CostPriceRange", "Title", "Manufacturer")
  fields = (lambda obj: obj.part_number, lambda obj: obj.cost_price_range, lambda obj: obj.title,
            lambda obj: obj.manufacturer)


class PartPriceSchema:
  headers = ("Date", "Website", "PartNumber", "PartPrice")
  fields = (lambda obj: obj.date, lambda obj: obj.website, lambda obj: obj.part_number,
            lambda obj: obj.part_price)


class PartCostPointSchema:
  headers = ("Date", "PartNumber", "Cost")
  fields = (lambda obj: obj.date, lambda obj: obj.part_number, lambda obj: obj.cost)


class WebsiteSchema:
  headers = ("DomainName", "Title", "IsClient")
  fields = (lambda obj: obj.domain_name, lambda obj: obj.title, lambda obj: obj.is_client)
