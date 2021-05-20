default_app_config = "upload.apps.UploadAppConfig"

_lookup = dict()


def LoaderClassForModelName(model_name):
  print('lookup', model_name)
  return _lookup.get(model_name)


def register(loader_class):
  def register_decorator():
    model_class = loader_class.MODEL_CLASS
    _lookup[model_class.__name__] = loader_class
    print('register', model_class, model_class.__name__)

  return register_decorator
