
from importlib import import_module

from django.conf import settings
from django.core.exceptions import *
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.urls import reverse
from django.utils import translation
from django.views import generic
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from .models import *
from .tokens import account_activation_token
from .translations import filter_translations


SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
s = SessionStore()


"""
Base Context, providing navigation and footer links for all pages.
"""


class BaseContext(ContextMixin):
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        lang = translation.get_language()

        navlinks = NavLink.objects.select_related('page').order_by(
            'position'
        )
        pages = Page.objects.all().select_related('common')
        pages = filter_translations(
            pages, lang).order_by('common__footer_position')

        context['sociallinks'] = SocialLink.objects.all()
        context['pages'] = pages
        context['navlinks'] = navlinks
        context['footerlinks'] = FooterLink.objects.order_by('position')

        return context


"""
Generic Views for Page, Collection, and Detail pages.
#####################################################

Page View consists of Sections defined in the database.
(model: Page, PageCommon)

Collection View consists of list view of Collection Items, also defined in the
database (model: CollectionItem, CollectionItemCommon)

Detail View consists of a single Collection Item

"""

"""TODO: access args from url conf instead of parsing path"""


class PageView(BaseContext, generic.ListView):
    model = Section
    context_object_name = 'sections'

    template_name = 'portfolio/page.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        lang = translation.get_language()

        sections = self.get_queryset().values_list('common__id')

        queryset = CollectionItem.objects.select_related('common').filter(
            common__isnull=False,
            common__parent_section__id__in=sections
        )

        queryset = filter_translations(queryset, lang)

        context['collectionitems'] = queryset

        # print(context['pages'].values())

        spotlights = CollectionItem.objects.filter(
            common__spotlight=True).select_related(
                'common__parent_section').prefetch_related(
                    'common__parent_section__sections').filter(
                        common__parent_section__id__in=sections)

        context['spotlights'] = filter_translations(spotlights, lang)

        return context

    def get_queryset(self):

        lang = translation.get_language()

        page_slug = self.request.path.replace('/', '')

        if page_slug == '':

            page_slug = 'home'

        page = Page.objects.filter(lang=lang, slug=page_slug)
        if len(page) == 0:
            page = Page.objects.filter(
                lang=settings.LANGUAGE_CODE, slug=page_slug)
        page = page.first()
        queryset = Section.objects.select_related(
            'common').filter(common__page__id=page.common.id)

        queryset = filter_translations(
            queryset, lang).order_by('common__position')

        return queryset


class CollectionView(BaseContext, generic.ListView):
    model = CollectionItem
    context_object_name = 'collectionitems'

    template_name = 'portfolio/page_collection.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        lang = translation.get_language()

        path = self.request.path.split('/')
        section_slug = path[1]

        section = Section.objects.filter(lang=lang, slug=section_slug)
        if len(section) == 0:
            section = Section.objects.filter(
                lang=settings.LANGUAGE_CODE, slug=section_slug)

        context['section'] = section.first()

        return context

    def get_queryset(self):

        lang = translation.get_language()

        # Instead of parsing url, can we access slug directly?
        page_slug = self.request.path.replace('/', '')

        section = Section.objects.filter(
            lang=lang, slug=page_slug)
        if len(section) == 0:
            section = Section.objects.filter(
                lang=settings.LANGUAGE_CODE, slug=page_slug)

        section = section.first()

        queryset = CollectionItem.objects.select_related(
            'common').filter(common__parent_section__id=section.common.id)

        queryset = filter_translations(queryset, lang)

        return queryset


class DetailView(BaseContext, generic.ListView):
    model = CollectionItem
    template_name = 'portfolio/page_detail.html'
    context_object_name = 'collectionitem'

    def get_queryset(self):
        lang = translation.get_language()

        path = self.request.path.split('/')
        item_slug = path[2]

        queryset = CollectionItem.objects.filter(
            slug=item_slug)

        queryset = filter_translations(queryset, lang)
        queryset = queryset.first()
        return queryset


"""
A few extra views with individual templates that don't fit the current
Page > Section Setup (can be refactored to work as such)

The names are fairly self-explanatory.

"""


class BaseTemplateView(BaseContext, generic.TemplateView):
    pass


"""
class ImprintView(BaseTemplateView):
    template_name = 'portfolio/imprint.html'


class PrivacyView(BaseTemplateView):
    template_name = 'portfolio/privacy.html'
 """

"""
Contact views, for contact form actions and email confirmation.

Needs refactoring into single UserResponse view, then based on path
actions get taken

Needed paths:
contact/confirm-email
contact/email-confirmed
contact/thanks
contact/delete
contact/messages
"""


class ContactView(BaseContext, generic.View):
    model = ContactResponse
    context_object_name = 'contactresponses'
    template_name = 'portfolio/contact.html'

    def get(self, request, *args, **kwargs):

        context = self.get_context_data(kwargs=kwargs)

        lang = translation.get_language()

        response_slug = kwargs['slug']
        contact_id = self.request.GET.get('id')
        token = self.request.GET.get('token')
        if len(response_slug) > 0:
            queryset = ContactResponse.objects.filter(
                slug=response_slug)

            context['contactresponse'] = filter_translations(
                queryset, lang).first()

            if response_slug == 'confirmed' or response_slug == 'thanks':
                context['messages'] = Message.objects.filter(
                    contact__id=contact_id, sent=False)

        if contact_id:
            contact = get_object_or_404(Contact, id=contact_id)

        """
        Redirects for email confirmation and resend confirmation email
        """
        # Confirm email address and redirect to contact/confirmed
        if response_slug == 'confirm' and contact_id and token:
            if account_activation_token.check_token(contact, token):
                contact.email_confirmed = True
                contact.save()
                messages = Message.objects.filter(contact=contact, sent=False)
                for message in messages:
                    message.send()
                url = reverse('portfolio:contact', args=['confirmed'])
                return HttpResponseRedirect(f"{url}?{QueryDict(f'id={contact.id}').urlencode()}")
            else:
                raise Http404('Invalid user/token combination')

        # Catch missing contact or token params
        elif response_slug == 'confirm' and (not contact_id or not token):
            raise Http404('Missing user or token parameters')

        # raise 404 on other urls
        elif response_slug not in [
                'confirmed',
                'thanks',
                'messages',
                'unconfirmed',
                'send-confirmation-email',
                'sent-confirmation-email']:
            raise Http404('Contact view not found')

        # Finally, render template with context
        return render(request, 'portfolio/contact.html', context=context)

    def post(self, request, *args, **kwargs):

        try:
            response_slug = kwargs['slug']
        except KeyError:
            response_slug = ''

        if response_slug == '':
            name = request.POST['name']
            email = request.POST['email']
            subject = request.POST['subject']
            content = request.POST['message']
            try:
                contact = Contact.objects.get(email_address=email)
            except Contact.DoesNotExist:
                contact = Contact(email_address=email, name=name)
                contact.save()
                token = account_activation_token.make_token(contact)
                contact.send_confirmation_email(token)

            # try:

            message = Message(
                contact=contact,
                subject=subject,
                content=content)

            message.save()

            if message.contact.email_confirmed:
                message.send()
                url = reverse('portfolio:contact', args=['thanks'])
                return HttpResponseRedirect(f"{url}?{QueryDict(f'id={contact.id}').urlencode()}")

            else:
                url = reverse('portfolio:contact', args=['unconfirmed'])
                return HttpResponseRedirect(f"{url}?{QueryDict(f'id={contact.id}').urlencode()}")

        elif response_slug == 'send-confirmation-email':
            email = request.POST['email']

            contact = Contact.objects.get(email_address=email)
            token = account_activation_token.make_token(contact)
            contact.send_confirmation_email(token)

            return HttpResponseRedirect(reverse('portfolio:contact', args=['sent-confirmation-email']))

    def delete(self, request, *args, **kwargs):
        """Delete all contact's information"""
        pass

    def get_context_data(self, **kwargs):
        print(kwargs)
        context = super().get_context_data(**kwargs)

        contact_id = self.request.GET.get('id')
        token = self.request.GET.get('token')

        try:
            response_slug = kwargs['kwargs']['slug']
        except KeyError:
            response_slug = ''

        if contact_id:
            try:
                contact = Contact.objects.get(id=contact_id)
                context['contact'] = contact
                print(contact)
                if response_slug in ['confirmed', 'thanks', 'messages']:
                    context['messages'] = Message.objects.filter(
                        contact=contact, sent=True)
            except ValidationError:
                print('invalid contact id, skipping contact')

        return context


"""Email not being displayed correctly? View in browser"""


class EmailView(BaseContext, generic.DetailView):
    model = Message
    template_name = 'portfolio/email_confirmation'


""" 
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

    # try:

    message = Message(
        contact=contact,
        subject=subject,
        content=content)

    message.save()

    if message.contact.email_confirmed:
        message.send()
        return HttpResponseRedirect(
            reverse(
                'portfolio:contact-thanks',
                args=[message.id]))
    else:
        return HttpResponseRedirect(
            reverse(
                'portfolio:unconfirmed-email',
                args=[contact.id])) """

# except:
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
    return HttpResponseRedirect(reverse(f'portfolio:page'))


"""
Views for changing language
"""


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

    translation.activate(lang_code)
    return response


def check_for_language(lang_code):
    supported_lang = False
    for language in settings.LANGUAGES:
        if language[0] == lang_code:
            supported_lang = True
    return supported_lang
