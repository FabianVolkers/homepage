from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'portfolio'
urlpatterns = [
    re_path(r'^(?!(admin|media|projects|photography|lang))(?P<page_name>[\w|-]{0,}$)',
            views.PageView.as_view(), name='page'),
    path('contact', views.contact, name='contact'),
    path('contact/thanks/<int:message_id>',
         views.contacted, name='contact-thanks'),
    path('contact/confirm-email/<str:contact_id>/<str:token>',
         views.confirm_email, name='confirm-email'),
    path('contact/unconfirmed-email/<str:contact_id>',
         views.unconfirmed_email, name='unconfirmed-email'),
    path('contact/send-confirmation-email/<str:contact_id>',
         views.send_confirmation_email, name='send-confirmation-email'),
    #path('projects', views.CollectionView.as_view(), name='projects-collection'),
    # path('project/<slug:slug>', views.DetailView.as_view(),
    #     name='project-detail'),
    # path('photography', views.CollectionView.as_view(),
    #     name='photography-collection'),
    #path('photo/<slug:slug>', views.DetailView.as_view(), name='photo-detail'),
    #path('imprint', views.ImprintView.as_view(), name='imprint'),
    #path('privacy', views.PrivacyView.as_view(), name='privacy'),
    path('lang', views.set_language, name='set-lang'),
    re_path(r'^(?!(admin|media|privacy|imprint|lang]))(?P<section_slug>[\w|-]+$)',
            views.CollectionView.as_view(), name='collection'),
    re_path(r'^(?![admin|media|lang])(?P<section_slug>[\w|-]+)/(?P<collectionitem_slug>[\w|-]+)',
            views.DetailView.as_view(), name='detail'),

]

if settings.DEV_MODE:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
