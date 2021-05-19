from upload.csvbase import GenericLoader
from upload import register


@register
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
