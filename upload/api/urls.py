from django.conf.urls import url

from . import views as api_views

urlpatterns = [
    url(r'^progress/(?P<progress_id>[0-9]+)/?$', api_views.ProgressView.as_view()),
]
