from django.apps import AppConfig


class CoreAppConfig(AppConfig):
  name = "core"
  verbose_name = "Core"

  def ready(self):
    import core.signals
    import core.loaders
