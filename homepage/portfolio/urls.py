from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'portfolio'

urlpatterns = [
    path('lang', views.set_language, name='set-lang'),
    re_path(r'^contact(?:/(?P<slug>[\w|-]{0,}))?',
            views.ContactView.as_view(), name="contact"),
    re_path(r'^(?!(admin|media|static))(?P<section_slug>[\w|-]+)/(?P<collectionitem_slug>[\w|-]+)',
            views.DetailView.as_view(), name='detail'),
    re_path(r'^(?!(admin|media|privacy|imprint]))(?P<section_slug>[\w|-]+$)',
            views.CollectionView.as_view(), name='collection'),
    re_path(r'^(?!(admin|media|static|projects|photography))(?P<page_name>[\w|-]{0,}$)',
            views.PageView.as_view(), name='page'),
]


if settings.ENVIRONMENT == 'development':

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    print(settings.STATIC_URL, settings.MEDIA_URL)
    print(settings.STATIC_ROOT, settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
