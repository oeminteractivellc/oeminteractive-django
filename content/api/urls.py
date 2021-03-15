from django.conf.urls import url

from . import views as api_views

urlpatterns = [
    url(r'^cs$', api_views.ListCreateContentSectionView.as_view()),
    url(r'^cs/(?P<pk>[0-9]+)$', api_views.RetrieveUpdateContentSectionView.as_view()),
    url(r'^cv$', api_views.ListCreateContentVariantView.as_view()),
    url(r'^cv/(?P<pk>[0-9]+)$', api_views.RetrieveUpdateContentVariantView.as_view()),
    url(r'^ccfg/(?P<key>[a-zA-Z0-9-.,]+)$', api_views.RetrieveContentConfigurationView.as_view()),
    url(r'^ccfg$', api_views.CreateContentConfigurationView.as_view()),
]
