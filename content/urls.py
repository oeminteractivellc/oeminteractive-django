from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^builder/?$', views.ContentBuilderView.as_view()),
    url(r'^builder/(?P<domain>[a-z0-9.\-_]+)/?$', views.ContentBuilderView.as_view()),
    url(r'^builder/(?P<domain>[a-z0-9.\-_]+)/(?P<slug>[a-z0-9\-]+)/?$',
        views.ContentBuilderView.as_view()),
    url(r'^preview$', views.PreviewView.as_view()),
    url(r'^raw$', views.RawView.as_view()),
]
