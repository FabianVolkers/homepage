from .tokens import account_activation_token
from .models import *
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic
from django.conf import settings
from django.utils import translation
from django.db.models import Q
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from django.core.exceptions import *
from importlib import import_module

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
s = SessionStore()
# from django.contrib.auth.tokens import default_token_generator


"""
TODO:
- replace contact views with User Notification view with message and action

"""


"""
Base Context, providing navigation and footer links for all pages.
"""


class BaseContext(ContextMixin):
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        navlinks = NavLink.objects.select_related('page').order_by(
            'position'
        )
        pages = filter_translations(
            Page.objects.all(), translation.get_language())

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

        print(context['pages'].values())

        spotlights = CollectionItem.objects.filter(
            common__spotlight=True).select_related(
                'common__parent_section').prefetch_related(
                    'common__parent_section__sections').filter(
                        common__parent_section__id__in=sections)

        context['spotlights'] = filter_translations(spotlights, lang)
        print(context['spotlights'].values())
        print(CollectionItem.objects.prefetch_related(
            'common__parent_section__sections'))

        return context

    def get_queryset(self):

        lang = self.request.COOKIES[settings.LANGUAGE_COOKIE_NAME]

        page_slug = self.request.path.replace('/', '')

        if page_slug == '':

            page_slug = 'home'

        try:
            page = Page.objects.get(lang=lang, slug=page_slug)
        except Page.DoesNotExist:
            page = Page.objects.get(
                lang=settings.LANGUAGE_CODE, slug=page_slug)

        queryset = Section.objects.select_related(
            'common').filter(common__page__id=page.id)

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

        lang = self.request.COOKIES[settings.LANGUAGE_COOKIE_NAME]

        # Instead of parsing url, can we access slug directly?
        page_slug = self.request.path.replace('/', '')
        print(page_slug)
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
        lang = self.request.COOKIES[settings.LANGUAGE_COOKIE_NAME]

        path = self.request.path.split('/')
        item_slug = path[2]
        print(item_slug)
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


class ImprintView(BaseTemplateView):
    template_name = 'portfolio/imprint.html'


class PrivacyView(BaseTemplateView):
    template_name = 'portfolio/privacy.html'


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
                args=[contact.id]))

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
    return HttpResponseRedirect(reverse(f'portfolio:index'))


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


"""
Helper function for filtering querysets for current language,
falling back to default language if translations does not exist

"""


def filter_translations(queryset, lang):

    if lang == settings.LANGUAGE_CODE:

        queryset = queryset.filter(lang=lang)

    else:
        translations = queryset.filter(lang=lang)

        # Fallback to default language
        fallback = queryset.exclude(
            common__id__in=translations.values('common')
        ).filter(
            lang=settings.LANGUAGE_CODE
        )

        queryset = fallback.union(translations)

    return queryset
