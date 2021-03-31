import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class PageView(LoginRequiredMixin, TemplateView):
  def get(self, request, *args, **kwargs):
    if not request.user.is_authenticated:
      return redirect("login")
    return super().get(request, *args, **kwargs)


class HomeView(PageView):
  template_name = "home.html"
