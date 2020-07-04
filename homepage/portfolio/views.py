from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic
#from django.contrib.auth.tokens import default_token_generator

from .models import Message, Contact, Section, BaseEntry, NavLink, FooterLink
from .tokens import account_activation_token


# Create your views here.
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
class ProjectDetailView(BaseDetailView):
    model = BaseEntry
    template_name = 'portfolio/project.html'

class ProjectListView(BaseListView):
    model = BaseEntry
    context_object_name = 'projects'
    template_name = 'portfolio/projects.html'
class PhotoView(BaseDetailView):
    model = BaseEntry
    template_name = 'portfolio/photo.html'

class CollectionView(BaseDetailView):
    model = BaseEntry
    template_name = 'portfolio/collection.html'

class MessageView(generic.ListView):
    model = Message
    template_name = 'portfolio/'

class BaseTemplateView(generic.TemplateView):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['sections'] = Section.objects.order_by('position')
        context['navlinks'] = NavLink.objects.order_by('position')
        context['footerlinks'] = FooterLink.objects.order_by('position')
        return context    

class ImprintView(BaseTemplateView):
    template_name = 'portfolio/imprint.html'

class PrivacyView(BaseTemplateView):
    template_name = 'portfolio/privacy.html'

class IndexView(BaseTemplateView):
    template_name = 'portfolio/index.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books

        
        context['spotlights'] = BaseEntry.objects.filter(spotlight=True)
        return context 



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