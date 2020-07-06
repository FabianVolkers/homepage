from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views 

app_name = 'portfolio'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('contact', views.contact, name='contact'),
    path('contact/thanks/<int:message_id>', views.contacted, name='contact-thanks'),
    path('contact/confirm-email/<str:contact_id>/<str:token>', views.confirm_email, name='confirm-email'),
    path('contact/unconfirmed-email/<str:contact_id>', views.unconfirmed_email, name='unconfirmed-email'),
    path('contact/send-confirmation-email/<str:contact_id>', views.send_confirmation_email, name='send-confirmation-email'),
    path('projects', views.ProjectListView.as_view(), name='projects-collection'),
    path('project/<slug:slug>', views.ProjectDetailView.as_view(), name='project-detail'),
    path('photography', views.PhotoListView.as_view(), name='photo-list'),
    path('collection/<slug:slug>', views.CollectionView.as_view(), name='collection-detail'),
    path('photo/<slug:slug>', views.PhotoView.as_view(), name='photo-detail'),
    path('imprint', views.ImprintView.as_view(), name='imprint'),
    path('privacy', views.PrivacyView.as_view(), name='privacy'),
    path('lang', views.set_language, name='set-lang')
]

if settings.DEV_MODE:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)