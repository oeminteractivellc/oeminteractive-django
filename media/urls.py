from django.conf.urls import url

from . import views

urlpatterns = [
    url('^upload/(?P<schema>[a-zA-Z_]+)/?$', views.MediaMultiUploadView.as_view()),
    url('^(?P<slug>[a-zA-Z0-9-.,]+)$', views.MediaRedirectView.as_view()),
]
