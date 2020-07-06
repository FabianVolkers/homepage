from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic
from django.conf import settings
from django.utils import translation
from django.db.models import Q
#from django.contrib.auth.tokens import default_token_generator

from .models import Message, Contact, Section, BaseEntry, NavLink, FooterLink, SectionCommon
from .tokens import account_activation_token


# Base Views

class BaseDetailView(generic.DetailView):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['sections'] = Section.objects.order_by('position')
        context['navlinks'] = NavLink.objects.all()
        context['footerlinks'] = FooterLink.objects.order_by('position')
        return context

class BaseListView(generic.ListView):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['sections'] = Section.objects.order_by('position')
        context['navlinks'] = NavLink.objects.order_by('position')
        context['footerlinks'] = FooterLink.objects.order_by('position')
        return context

class BaseTemplateView(generic.TemplateView):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        
        if translation.get_language() == settings.LANGUAGE_CODE:
            context['sections'] = Section.objects.filter(
                lang=translation.get_language()
                ).select_related('common').exclude(
                    common__isnull=True,
                    translations_group__isnull=True
                    )
        else:
            sections = Section.objects.filter(
                lang=translation.get_language()
                ).select_related('common').exclude(
                    common__isnull=True,
                    translations_group__isnull=True
                    )

            fallback = Section.objects.exclude(
                common__id__in=sections.values('common')
                ).filter(
                    lang=settings.LANGUAGE_CODE
                    ).select_related('common').exclude(
                        common__isnull=True, translations_group__isnull=True
                        )
            
            context['sections'] = fallback.union(sections).order_by('common__position')

        context['navlinks'] = NavLink.objects.order_by('position')
        context['footerlinks'] = FooterLink.objects.order_by('position')

        return context  


""" Detail Views """ 

class CollectionView(BaseDetailView):
    model = BaseEntry
    template_name = 'portfolio/collection.html'

class PhotoView(BaseDetailView):
    model = BaseEntry
    template_name = 'portfolio/photo.html'

class ProjectDetailView(BaseDetailView):
    model = BaseEntry
    template_name = 'portfolio/project.html'


""" List Views """
class MessageView(generic.ListView):
    model = Message
    template_name = 'portfolio/'

class PhotoListView(BaseListView):
    queryset = BaseEntry.objects.filter(parent_section='3')
    context_object_name = 'photos'
    template_name = 'portfolio/photos.html'

class ProjectListView(BaseListView):
    queryset = BaseEntry.objects.filter(parent_section='2')
    context_object_name = 'projects'
    template_name = 'portfolio/projects.html'

  
""" Template Views """

class ImprintView(BaseTemplateView):
    template_name = 'portfolio/imprint.html'

class IndexView(BaseTemplateView):
    template_name = 'portfolio/index.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['spotlights'] = BaseEntry.objects.filter(spotlight=True)
        return context 

class PrivacyView(BaseTemplateView):
    template_name = 'portfolio/privacy.html'





def contact(request):
    email = request.POST['email']
    subject = request.POST['subject']
    content = request.POST['message']
    try:
        contact = Contact.objects.get(email_address=email)
    except Contact.DoesNotExist:
        contact = Contact(email_address=email)
        contact.save()
        token = account_activation_token.make_token(contact)
        contact.send_confirmation_email(token)
        
        
    
    #try:
    
    message = Message(contact=contact, subject=subject, content=content)
    message.save()

    if message.contact.email_confirmed:
        message.send()
        return HttpResponseRedirect(reverse('portfolio:contact-thanks', args=[message.id]))
    else:
        return HttpResponseRedirect(reverse('portfolio:unconfirmed-email', args=[contact.id]))
        
    #except:
    #    return HttpResponseRedirect(reverse('portfolio:index'))

        

def contacted(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    context = {'message': message}
    return render(request, 'portfolio/contact.html', context)

def confirm_email(request, contact_id, token):
    contact = get_object_or_404(Contact, id=contact_id)
    if account_activation_token.check_token(contact, token):
        contact.email_confirmed = True
        contact.save()
        messages = Message.objects.filter(contact=contact, sent=False)
        for message in messages:
            message.send()
        return render(request, 'portfolio/confirmed_email.html')
    else:
        raise Http404('Invalid user/token combination')

def unconfirmed_email(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    context = {'contact': contact}
    return render(request, 'portfolio/unconfirmed_email.html', context)

def send_confirmation_email(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    token = account_activation_token.make_token(contact)
    contact.send_confirmation_email(token)
    return HttpResponseRedirect(reverse(f'portfolio:index'))

def set_language(request):
    next = request.GET.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)
    if request.method == 'GET':
        lang_code = request.GET.get('lang', None)

        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)

    print(request.session[settings.LANGUAGE_COOKIE_NAME])
    for key in response.__dict__:
        print(f"{key} = {response.__dict__[key]}")
    translation.activate(lang_code)
    return response

def check_for_language(lang_code):
    supported_lang = False
    for language in settings.LANGUAGES:
        if language[0] == lang_code:
            supported_lang = True
    return supported_lang
    