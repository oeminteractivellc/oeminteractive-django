default_app_config = "upload.apps.UploadAppConfig"

_lookup = dict()


def LoaderClassForModelName(model_name):
  return _lookup.get(model_name)


def register():
  def register_decorator(loader_class):
    model_class = loader_class.MODEL_CLASS
    _lookup[model_class.__name__] = loader_class

  return register_decorator
