import datetime
import os
import uuid

from django.conf import settings
from django.core.mail import (BadHeaderError, EmailMessage,
                              EmailMultiAlternatives, send_mail)
from django.db import models
from django.http import QueryDict
from django.shortcuts import render
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .translations import filter_translations
from .validators import *

"""
A couple of hard coded choices for the database models.
"""
views = [
    ('portfolio:detail', 'Detail View'),
    ('portfolio:collection', 'Collection View'),
    ('portfolio:page', 'Page View'),
]

page_positions = []
for h in range(settings.MAX_PAGES):
    page_positions.append((h, h))

section_postitions = []
for i in range(settings.MAX_SECTIONS):
    section_postitions.append((i, i))

link_positions = []
for j in range(settings.MAX_NAVLINKS):
    link_positions.append((f"navbar-{j}", f"navbar {j}"))
for k in range(settings.MAX_FOOTERLINKS):
    link_positions.append((f"footer-{k}", f"footer {k}"))

sociallink_positions = [
    ('deg270', '12:00'),
    ('deg315', '01:30'),
    ('deg0', '03:00'),
    ('deg45', '04:30'),
    ('deg90', '06:00'),
    ('deg135', '07:30'),
    ('deg180', '09:00'),
    ('deg225', '10:30')
]

link_types = [
    ('page', 'Page'),
    ('section', 'Section'),
    ('external', 'External')
]


class Setting(models.Model):
    key = models.CharField(max_length=256)
    value = models.CharField(max_length=1024)

    def __str__(self):
        return f'{self.key}={self.value}'


"""
Icon model for external links
"""


class Icon(models.Model):
    name = models.CharField(max_length=64)
    icon_class = models.CharField(max_length=64)

    colour = models.CharField(max_length=7, null=True,
                              blank=True, validators=[validate_colour_code])
    colour_value = models.CharField(max_length=7, null=True,
                                    blank=True, validators=[validate_colour_code])

    slug = models.SlugField(null=True)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        self.slug = slugify(self.name)
        self.colour = self.colour_value


"""
Abstract Translatable model from which all models with translatable fields inherit
"""


class AbstractTranslatable(models.Model):

    lang = models.CharField(
        max_length=5, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    class Meta:
        abstract = True
        unique_together = ['lang', 'slug']

    def __str__(self):
        return self.lang


"""
Models for website pages
########################
"""


"""
PageType model for the different types of pages supported
"""


class PageType(models.Model):
    name = models.CharField(max_length=24)
    template_name = models.CharField(max_length=64)
    view_name = models.CharField(max_length=64, editable=False)
    overwrite_view_name = models.CharField(
        max_length=64, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, force_insert=False,
             force_update=False, using=None, update_fields=None):

        if self.overwrite_view_name != None:
            self.view_name = self.overwrite_view_name
        else:
            self.view_name = f"portfolio:{self.name}"

        return super().save(force_insert=force_insert,
                            force_update=force_update,
                            using=using,
                            update_fields=update_fields)


"""
PageCommon model for shared attributes between translations
"""


class PageCommon(models.Model):
    friendly_name = models.CharField(max_length=64)

    page_type = models.ForeignKey(
        PageType, on_delete=models.SET_NULL, null=True, blank=True)
    footer_link = models.BooleanField(default=True)
    footer_position = models.IntegerField(unique=True, null=True, blank=True,
                                          choices=[(i, i) for i in range(10)])

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __str__(self):
        return self.friendly_name


"""
Translatable Page model holding the page text translations
"""


class Page(AbstractTranslatable):
    name = models.CharField(max_length=24)

    slug = models.SlugField(null=True, blank=True)
    common = models.ForeignKey(
        PageCommon, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('Single Page')
        verbose_name_plural = _('Single Pages')

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False,
             using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        self.slug = slugify(self.name)


"""
Models for page sections
########################
"""

"""
Section Type model for defining different section types
e.g.: Collection, Spotlight, Contact
"""


class SectionType(models.Model):
    name = models.CharField(max_length=64)
    template_name = models.CharField(max_length=64)
    default_position = models.IntegerField()

    def __str__(self):
        return self.name


"""
Section Common model for shared attributes between translated sections
"""


class SectionCommon(models.Model):
    friendly_name = models.CharField(max_length=64)
    section_type = models.ForeignKey(
        SectionType, on_delete=models.SET_NULL, null=True)
    position = models.IntegerField(null=True, choices=section_postitions)
    page = models.ForeignKey(
        PageCommon,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sections'
    )

    class Meta:
        verbose_name = _('Page Section')
        verbose_name_plural = _('Page Sections')
        unique_together = ['page', 'position']

    def __str__(self):
        return self.friendly_name


"""
Translatable section model holding section translations
"""


class Section(AbstractTranslatable):

    name = models.CharField(max_length=64)
    slug = models.SlugField()
    detail_slug = models.SlugField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    common = models.ForeignKey(SectionCommon, related_name='sections',
                               on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('Section Translation')
        verbose_name_plural = _('Sections Translations')

    def __str__(self):
        return self.name

    def save(self):
        self.slug = slugify(self.name)
        return super().save()


"""
Models for Navigation, Contact and Footer links
###############################################
"""

"""
Abstract Link model from which all other link models inherit
"""


class AbstractLink(models.Model):
    name = models.CharField(max_length=12)
    url = models.CharField(max_length=256, editable=False,
                           blank=True, default='/')
    view = models.CharField(
        max_length=64, default='portfolio:detail', choices=views)
    position = models.CharField(
        max_length=8, null=True, choices=link_positions, unique=True)
    link_for = models.CharField(
        max_length=24, choices=link_types, null=True)
    section = models.ForeignKey(
        Section, null=True, blank=True, on_delete=models.SET_NULL)
    page = models.ForeignKey(PageCommon, null=True,
                             blank=True, on_delete=models.SET_NULL)
    external = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.url

    class Meta:
        abstract = True


"""
Helper model for editing all page links in bulk
"""


class LinkEdit(models.Model):

    class Meta:
        verbose_name = _('Page Link')
        verbose_name_plural = _('Page Links')


"""
Social Link model for the contact circle
"""


class SocialLink(AbstractLink):
    icon = models.ForeignKey(Icon, on_delete=models.SET_NULL,
                             null=True)
    link_edit = models.ForeignKey(
        LinkEdit, on_delete=models.SET_NULL, null=True,
        related_name='social_links')
    position = models.CharField(
        max_length=6, null=True, blank=True, unique=True,
        choices=sociallink_positions)

    class Meta:
        verbose_name = _('Social Link')
        verbose_name_plural = _('Social Links')


"""
Footer link model
"""


class FooterLink(AbstractLink):
    icon = models.ForeignKey(Icon, on_delete=models.SET_NULL, null=True)
    link_edit = models.ForeignKey(
        LinkEdit, on_delete=models.SET_NULL,
        null=True, related_name='footer_links')

    class Meta:
        verbose_name = _('Footer Link')
        verbose_name_plural = _('Footer Links')


"""
Navigation Link model
"""


class NavLink(AbstractLink):
    link_edit = models.ForeignKey(
        LinkEdit, on_delete=models.SET_NULL,
        null=True, related_name='navbar_links')

    class Meta:
        verbose_name = _('Navigation Link')
        verbose_name_plural = _('Navigation Links')


"""
Models for Collection Items
e.g.: Projects, Photos
##################
"""

"""
Collection Item Common model for shared attributes between translated items
"""


class CollectionItemCommon(models.Model):
    friendly_name = models.CharField(max_length=64)
    image = models.ImageField(upload_to='images')
    created = models.DateTimeField()
    spotlight = models.BooleanField()
    parent_section = models.ForeignKey(
        SectionCommon, on_delete=models.SET_NULL, null=True)
    detail_view = models.CharField(
        max_length=64, default='portfolio:detail', choices=views)

    class Meta:
        verbose_name = _('Collection Item')
        verbose_name_plural = _('Collection Items')

    def __str__(self):
        return self.friendly_name


"""
Collection Item model for translatable items
"""


class CollectionItem(AbstractTranslatable):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, editable=False)
    description = models.TextField()
    common = models.ForeignKey(
        CollectionItemCommon, related_name='collection_items',
        on_delete=models.CASCADE, null=True)
    image_alttext = models.TextField(default="")

    class Meta:
        verbose_name = _('Item Translation')
        verbose_name_plural = _('Item Translations')

    def save(self):
        self.slug = slugify(self.name)
        super().save()


"""
Models for the contact form
###########################
"""

"""
Contact model to enable email address confirmation
"""


class Contact(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email_address = models.EmailField()
    email_confirmed = models.BooleanField(default=False)
    name = models.CharField(max_length=64, null=True)

    def __str__(self):
        return self.email_address

    def send_confirmation_email(self, token):
        url = reverse('portfolio:contact', args=['confirm'])
        url = f"{url}?{QueryDict(f'id={self.id}&token={token}').urlencode()}"
        if settings.DEV_MODE:
            url = f'{settings.PROTO}://{settings.HOST}:{settings.PORT}/{url}'
        else:
            url = f'{settings.PROTO}://{settings.HOST}/{url}'

        pages = Page.objects.all().select_related('common')
        pages = filter_translations(
            pages, 'en').order_by('common__footer_position')

        context = {
            'pages': pages,
            'footerlinks': FooterLink.objects.order_by('position'),
            'user': {'confirmation_url': url}
        }

        html_email = render_to_string(
            'portfolio/email_confirmation.html', context=context)
        print(html_email)
        send_mail(
            subject='Please Confirm your email address',
            from_email="Fabian Volkers <noreply@fabianvolkers.com>",
            recipient_list=[self.email_address],
            message=f'Use this link to confirm your email address {url}',
            html_message=html_email,
            fail_silently=False
        )


"""
Message model for storing messages until email confirmation
"""


class Message(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    content = models.TextField()
    sent = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now=True)
    date_sent = models.DateTimeField(blank=True, null=True, editable=False)

    def __str__(self):
        return f"{self.contact.email_address} - {self.subject}"

    def send(self):

        email_template = get_template('portfolio/email_contact.html')

        context = {
            'from': self.contact.email_address,
            'name': self.contact.name,
            'subject': self.subject,
            'message': self.content
        }

        html_message = email_template.render(context=context)

        headers = {
            'Sender': 'noreply@fabianvolkers.com',
            'From': f'{self.contact.name} via fabianvolkers.com <{self.contact.email_address}>',
            'Reply-To': f'{self.contact.name} <{self.contact.email_address}>',
            'To': f'Fabian Volkers <{settings.EMAIL_CONTACT_ADDRESS}>'
        }
        email = EmailMultiAlternatives(
            subject=self.subject,
            from_email="Fabian Volkers <noreply@fabianvolkers.com>",
            to=[settings.EMAIL_CONTACT_ADDRESS],
            body=self.content,
            headers=headers
        )
        email.attach_alternative(html_message, 'text/html')
        email.send(fail_silently=False)

        self.date_sent = datetime.datetime.now()
        self.sent = True


"""
Contact Response Action model for storing actions for response to user
e.g.: resend confirmation email, delete personal information
"""


class ContactResponseAction(models.Model):
    name = models.CharField(max_length=24)
    page = models.ForeignKey(
        PageCommon, on_delete=models.SET_NULL, null=True, blank=True)
    method = models.CharField(max_length=7, choices=[(
        'GET', 'GET'), ('POST', 'POST'), ('DELETE', 'DELETE')])
    argument = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.name


"""
Contact response common for shared attributes between translatable contact
responses
"""


class ContactResponseCommon(models.Model):
    friendly_name = models.CharField(max_length=32)
    action = models.ForeignKey(
        ContactResponseAction, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.friendly_name}"


"""
Contact response model for translatable contact responses
"""


class ContactResponse(AbstractTranslatable):
    name = models.CharField(max_length=32)
    slug = models.SlugField(blank=True, null=True)
    message = models.TextField()
    common = models.ForeignKey(
        ContactResponseCommon, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.lang}"
