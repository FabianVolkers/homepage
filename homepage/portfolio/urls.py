from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views 

app_name = 'portfolio'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('contact', views.contact, name='contact'),
    path('contact/thanks/<int:message_id>', views.contacted, name='contact-thanks'),
    path('contact/confirm-email/<int:contact_id>/<str:token>', views.confirm_email, name='confirm-email'),
    path('contact/unconfirmed-email/<int:contact_id>', views.unconfirmed_email, name='unconfirmed-email'),
    path('contact/send-confirmation-email/<int:contact_id>', views.send_confirmation_email, name='send-confirmation-email'),
    path('project/<slug:slug>', views.ProjectView.as_view(), name='project-detail'),
    path('collection/<slug:slug>', views.CollectionView.as_view(), name='collection-detail'),
    path('photo/<slug:slug>', views.PhotoView.as_view(), name='photo-detail'),
    path('imprint', views.ImprintView.as_view(), name='imprint'),
    path('privacy', views.PrivacyView.as_view(), name='privacy')
]

if settings.DEV_MODE:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)