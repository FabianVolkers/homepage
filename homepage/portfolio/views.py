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


class BaseContext(ContextMixin):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
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
# Base Views


"""
TODO:
 - Refactor Translatable mixins to avoid duplication
"""
""" 

class TranslatableDetailMixin(SingleObjectMixin):
    def get_queryset(self):

        lang = self.request.COOKIES[settings.LANGUAGE_COOKIE_NAME]
        print(self.request.path_info)
        # Fallback to default language
        if len(self.model.objects.filter(lang=lang)) == 0:
            lang = settings.LANGUAGE_CODE

        return super().get_queryset().filter(
            lang=lang
        )


class TranslatableListMixin(MultipleObjectMixin):
    def get_queryset(self):

        lang = self.request.COOKIES[settings.LANGUAGE_COOKIE_NAME]

        # Fallback to default language
        print(self.request.path_info)
         for key in self.request.__dict__:
    print(f"{key} = {self.request.__dict__[key]}")
    try:
        for key_ in self.__dict__[key].__dict__:
            print(f"\t{key_} = {self.__dict__[key_]}")
    except:
        continue 

        if len(self.model.objects.filter(lang=lang)) == 0:
            lang = settings.LANGUAGE_CODE

        return super().get_queryset().filter(
            lang=lang
        )
 """
# class CollectionItemTypeMixin()


"""
Base Views for each type combining Mixins and Django's generic class based views.
"""

""" 
class BaseDetailView(BaseContext, TranslatableDetailMixin, generic.DetailView):
    pass


class BaseListView(BaseContext, TranslatableListMixin, generic.ListView):
    pass
 """


class BaseTemplateView(BaseContext, generic.TemplateView):
    pass


""" 
class BasePageMixin(MultipleObjectMixin):

    pass
 """

""" Detail Views """


""" class CollectionView(BaseDetailView):
    model = CollectionItem
    template_name = 'portfolio/collection.html'



class PhotoView(BaseDetailView):
    model = CollectionItem
    template_name = 'portfolio/photo.html'


class ProjectDetailView(BaseDetailView):
    model = CollectionItem
    template_name = 'portfolio/detail_view.html'
 """

""" List Views """

""" 
class MessageView(generic.ListView):
    model = Message
    template_name = 'portfolio/'


class PhotoListView(BaseListView):
    queryset = CollectionItem.objects.filter(common__parent_section='3')
    context_object_name = 'photos'
    template_name = 'portfolio/photos.html'


class ProjectListView(BaseListView):
    queryset = CollectionItem.objects.filter(common__parent_section='2')
    context_object_name = 'projects'
    template_name = 'portfolio/projects.html' """


""" Template Views """


class ImprintView(BaseTemplateView):
    template_name = 'portfolio/imprint.html'


class PageView(BaseContext, generic.ListView):
    model = Section
    context_object_name = 'sections'

    template_name = 'portfolio/index.html'

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
            common__spotlight=True).select_related('common__parent_section').prefetch_related('common__parent_section__sections').filter(common__parent_section__id__in=sections)

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

    template_name = 'portfolio/collection.html'

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
    template_name = 'portfolio/detail.html'
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

    # try:

    message = Message(contact=contact, subject=subject, content=content)
    message.save()

    if message.contact.email_confirmed:
        message.send()
        return HttpResponseRedirect(reverse('portfolio:contact-thanks', args=[message.id]))
    else:
        return HttpResponseRedirect(reverse('portfolio:unconfirmed-email', args=[contact.id]))

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


""" class IndexView(BaseListView):
    model = Section
    context_object_name = 'sections'

    template_name = 'portfolio/index.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['spotlights'] = CollectionItem.objects.filter(
            common__spotlight=True)
        return context


    def get_queryset(self):

        lang = self.request.COOKIES[settings.LANGUAGE_COOKIE_NAME]
        page = self.request.path.replace('/', '')
        if page == '':
            page = 'home'
        print(lang, page)
        if lang == settings.LANGUAGE_CODE:
            queryset = Section.objects.filter(
                lang=lang,
                ).select_related('common').filter(
                    common__isnull=False,
                    common__page__pages__slug=page
                    )
        else:
            sections = Section.objects.filter(
                lang=lang
                ).select_related('common').filter(
                    common__isnull=False,
                    # common__page__slug=page
                    )

            fallback = Section.objects.exclude(
                common__id__in=sections.values('common')
                ).filter(
                    lang=settings.LANGUAGE_CODE
                    ).select_related('common').filter(
                    common__isnull=False,
                    # common__page__slug=page
                    )
            queryset = fallback.union(sections).order_by('common__position')

        # Fallback to default language
        print(self.request.path_info)


        if len(self.model.objects.filter(lang=lang)) == 0:
            lang = settings.LANGUAGE_CODE

        return queryset
 """
