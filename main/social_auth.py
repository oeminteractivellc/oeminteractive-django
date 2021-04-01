import logging
from social_django.middleware import SocialAuthExceptionMiddleware
from social_core.exceptions import AuthForbidden

logger = logging.getLogger(__name__)


class MySocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
  def get_message(self, request, exception):
    return "Login failed.  Login restricted to oeminteractive.com domain."

  def process_exception(self, request, exception):
    logger.error(str(exception))
    return super().process_exception(request, exception)


def trace(backend, user, response, *args, **kwargs):
  logger.info(
      f"social auth pipeline backend={backend.name} user={user.get_full_name()} response={response}"
  )
