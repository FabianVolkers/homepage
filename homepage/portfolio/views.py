from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic
#from django.contrib.auth.tokens import default_token_generator

from .models import Project, Collection, Photo, Message, Contact
from .tokens import account_activation_token

# Create your views here.
class ProjectView(generic.DetailView):
    model = Project
    template_name = 'portfolio/project.html.jinja2'

class PhotoView(generic.DetailView):
    model = Photo
    template_name = 'portfolio/photo.html.jinja2'

class CollectionView(generic.DetailView):
    model = Collection
    template_name = 'portfolio/collection.html.jinja2'

class MessageView(generic.ListView):
    model = Message
    template_name = 'portfolio/'
def index(request):
    projects = get_list_or_404(Project, spotlight=True)
    collections = get_list_or_404(Collection, spotlight=True)
    context = {
        'projects': projects,
        'collections': collections
    }
    return render(request, 'portfolio/index.html.jinja2', context)



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
        return HttpResponseRedirect(reverse('portfolio:contacted', args=[message.id]))
    else:
        return HttpResponseRedirect(reverse('portfolio:unconfirmed-email', args=[contact.id]))
        
    #except:
    #    return HttpResponseRedirect(reverse('portfolio:index'))

        

def contacted(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    context = {'message': message}
    return render(request, 'portfolio/contact.html.jinja2', context)

def confirm_email(request, contact_id, token):
    contact = get_object_or_404(Contact, id=contact_id)
    if account_activation_token.check_token(contact, token):
        contact.email_confirmed = True
        contact.save()
        messages = get_list_or_404(Message, contact=contact)
        for message in messages:
            message.send()
        return render(request, 'portfolio/confirmed_email.html.jinja2')
    else:
        raise Http404('Invalid token for user')

def unconfirmed_email(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    context = {'contact': contact}
    return render(request, 'portfolio/unconfirmed_email.html.jinja2', context)

def send_confirmation_email(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    token = account_activation_token.make_token(contact)
    contact.send_confirmation_email(token)
    return HttpResponseRedirect(reverse(f'portfolio:index'))