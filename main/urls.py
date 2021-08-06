from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from proxy.views import proxy_view

from . import forms as main_forms
from . import views as main_views
from companalysis.views import CompAnalysisView


@csrf_exempt
def oem_admin_imageoverlay_proxy_view(request, path):
  remoteurl = "https://oeminteractive.com/imageoverlay/" + path
  headers = {}
  if settings.IMAGE_OVERLAY_AUTH is not None:
    headers.update({"authorization": settings.IMAGE_OVERLAY_AUTH})
  return proxy_view(request, remoteurl, {"headers": headers})


@csrf_exempt
def oem_admin_proxy_view(request, path):
  remoteurl = "https://oeminteractive.com/admin/" + path
  headers = {}
  if settings.IMAGE_OVERLAY_AUTH is not None:
    headers.update({"authorization": settings.IMAGE_OVERLAY_AUTH})
  return proxy_view(request, remoteurl, {"headers": headers})


urlpatterns = [
    path("", include("social_django.urls")),
    path("", main_views.HomeView.as_view(), name="home"),
    path("login/",
         auth_views.LoginView.as_view(template_name="login.html",
                                      authentication_form=main_forms.LoginForm,
                                      redirect_authenticated_user=True),
         name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("login-error/",
         TemplateView.as_view(template_name="login-error.html"),
         name="login-error"),
    path("admin123/", admin.site.urls),
    path("content/", include("content.urls")),
    path("media/", include("media.urls")),
    path("api/1.0/", include("companalysis.api.urls")),
    path("api/1.0/", include("content.api.urls")),
    path("api/1.0/", include("media.api.urls")),
    path("api/1.0/", include("upload.api.urls")),
    path("seolp-catalog", main_views.PageView.as_view(template_name="ccat.html")),
    path("seolp-media", main_views.PageView.as_view(template_name="seolp-media.html")),
    path("companalysis", CompAnalysisView.as_view()),
    url("proxyadmin/(?P<path>.*)", oem_admin_proxy_view),
    url("imageoverlay/(?P<path>.*)", oem_admin_imageoverlay_proxy_view),
]

if settings.SERVE_MEDIA:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
