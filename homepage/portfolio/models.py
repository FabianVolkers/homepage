import uuid
import os
import datetime

from django.db import models
from django.core.mail import send_mail, EmailMessage, BadHeaderError, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template, render_to_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
""" 
TODO: 
- Link abstract base class
- AbstractTranslatable BaseEntry with commonEntry and TranslationGroup

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

sociallink_positions = []
# for l in range()
link_types = [
    ('page', 'Page'),
    ('section', 'Section'),
    ('external', 'External')
]
# Create your models here.


class Setting(models.Model):
    key = models.CharField(max_length=256)
    value = models.CharField(max_length=1024)

    def __str__(self):
        return f'{self.key}={self.value}'


class Icon(models.Model):
    name = models.CharField(max_length=64)
    icon_class = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class AbstractTranslatable(models.Model):

    lang = models.CharField(
        max_length=5, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    class Meta:
        abstract = True
        unique_together = ['lang', 'slug']

    def __str__(self):
        return self.lang


class PageType(models.Model):
    name = models.CharField(max_length=24)
    template_name = models.CharField(max_length=64)
    view_name = models.CharField(max_length=64, editable=False)
    overwrite_view_name = models.CharField(
        max_length=64, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        if self.overwrite_view_name != None:
            self.view_name = self.overwrite_view_name
        else:
            self.view_name = f"portfolio:{self.name}"

        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


class PageCommon(models.Model):
    friendly_name = models.CharField(max_length=64)
    template_name = models.CharField(max_length=64)
    page_type = models.ForeignKey(
        PageType, on_delete=models.SET_NULL, null=True, blank=True)
    footer_link = models.BooleanField(default=True)
    footer_position = models.IntegerField(
        unique=True, null=True, blank=True, choices=[(i, i) for i in range(10)])

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __str__(self):
        return self.friendly_name


class Page(AbstractTranslatable):
    name = models.CharField(max_length=24)

    slug = models.SlugField(null=True, blank=True)
    common = models.ForeignKey(PageCommon, on_delete=models.CASCADE, null=True)

    #nav_link = models.ForeignKey(NavLink, on_delete=models.SET_NULL, default=1, null=True)

    class Meta:
        verbose_name = _('Single Page')
        verbose_name_plural = _('Single Pages')

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        self.slug = slugify(self.name)


class SectionType(models.Model):
    name = models.CharField(max_length=64)
    template_name = models.CharField(max_length=64)
    default_position = models.IntegerField()

    def __str__(self):
        return self.name


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
    #nav_link = models.ForeignKey(NavLink, on_delete=models.SET_NULL, default=1, null=True)

    class Meta:
        verbose_name = _('Page Section')
        verbose_name_plural = _('Page Sections')
        unique_together = ['page', 'position']

    def __str__(self):
        return self.friendly_name


class Section(AbstractTranslatable):
    #section_positions = range(1, len(Section.objects.all()))
    name = models.CharField(max_length=64)
    slug = models.SlugField()
    detail_slug = models.SlugField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    common = models.ForeignKey(
        SectionCommon, related_name='sections', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('Section Translation')
        verbose_name_plural = _('Sections Translations')

    def __str__(self):
        return self.name

    def save(self):
        """ TODO: Add support for default position
        sections = Section.objects.order_by(position)
        if self.position == None:
            self.position = self.section_type.default_position """

        self.slug = slugify(self.name)
        """ if self.common.nav_bar_link:
            try:
                NavLink.objects.get(name=self.slug)
            except models.ObjectDoesNotExist:
                position = len(NavLink.objects.all())
                navlink = NavLink(name=self.slug, url=f'/#{self.slug}', position=position)
                navlink.save()
                self.common.nav_link = navlink """
        return super().save()


class AbstractLink(models.Model):
    name = models.CharField(max_length=12)
    url = models.CharField(max_length=256, editable=False,
                           blank=True, default='/')
    view = models.CharField(
        max_length=64, default='portfolio:detail', choices=views)
    position = models.CharField(
        max_length=8, null=True, choices=link_positions, unique=True)
    link_for = models.CharField(max_length=24, choices=link_types, null=True)
    section = models.ForeignKey(
        Section, null=True, blank=True, on_delete=models.SET_NULL)
    page = models.ForeignKey(PageCommon, null=True,
                             blank=True, on_delete=models.SET_NULL)
    external = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.url

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """ if self.link_for == 'section':
            self.url = f"{self.page.slug}/#{self.section.slug}"
        elif self.link_for == 'page':
            self.url = f"/{self.page.objects.select_related('common').get()slug}"
        elif self.link_for == 'external':
            self.url = self.external """

        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    class Meta:
        abstract = True
        #verbose_name = 'ModelName'
        #verbose_name_plural = 'ModelNames'


class LinkEdit(models.Model):

    class Meta:
        verbose_name = _('Page Link')
        verbose_name_plural = _('Page Links')


class SocialLink(AbstractLink):
    icon = models.ForeignKey(Icon, on_delete=models.SET_NULL, null=True)
    link_edit = models.ForeignKey(
        LinkEdit, on_delete=models.SET_NULL, null=True, related_name='social_links')

    class Meta:
        verbose_name = _('Social Link')
        verbose_name_plural = _('Social Links')


class FooterLink(AbstractLink):
    icon = models.ForeignKey(Icon, on_delete=models.SET_NULL, null=True)
    link_edit = models.ForeignKey(
        LinkEdit, on_delete=models.SET_NULL, null=True, related_name='footer_links')

    class Meta:
        verbose_name = _('Footer Link')
        verbose_name_plural = _('Footer Links')


class NavLink(AbstractLink):
    link_edit = models.ForeignKey(
        LinkEdit, on_delete=models.SET_NULL, null=True, related_name='navbar_links')

    class Meta:
        verbose_name = _('Navigation Link')
        verbose_name_plural = _('Navigation Links')


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


class CollectionItem(AbstractTranslatable):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, editable=False)
    description = models.TextField()
    common = models.ForeignKey(
        CollectionItemCommon, related_name='collection_items', on_delete=models.CASCADE, null=True)
    image_alttext = models.TextField(default="")

    class Meta:
        verbose_name = _('Item Translation')
        verbose_name_plural = _('Item Translations')

    def save(self):
        self.slug = slugify(self.name)
        super().save()


class Contact(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email_address = models.EmailField()
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.email_address

    def send_confirmation_email(self, token):
        if settings.DEV_MODE:
            url = f'{settings.PROTO}://{settings.HOST}:{settings.PORT}/contact-view/confirm?id={self.id}&token={token}'
        else:
            url = f'{settings.PROTO}://{settings.HOST}/contact/confirm-email/{self.id}/{token}'
        print(url)

        email = render_to_string(
            'portfolio/email_confirmation.html', context={'user': {'confirmation_url': url}})
        print(email)
        send_mail(
            subject='Please Confirm your email address',
            from_email='noreply@fabianvolkers.com',
            recipient_list=[self.email_address],
            message='Click here to confirm your email address',
            html_message=f"""<p>Click <a href='{url}'>here</a> to confirm your email address</p>""",
            fail_silently=False
        )


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
        email = EmailMultiAlternatives(
            subject=self.subject,
            from_email='noreply@fabianvolkers.com',
            reply_to=[self.contact.email_address],
            to=[settings.EMAIL_CONTACT_ADDRESS],
            body=self.content
        )

        email_template = get_template('portfolio/contact_email.html')
        context = {
            'from': self.contact.email_address,
            'subject': self.subject,
            'message': self.content
        }
        html_message = email_template.render(context=context)

        email.attach_alternative(html_message, 'text/html')
        email.send(fail_silently=False)

        self.date_sent = datetime.datetime.now()
        self.sent = True


class ContactResponseAction(models.Model):
    name = models.CharField(max_length=24)
    page = models.ForeignKey(
        PageCommon, on_delete=models.SET_NULL, null=True, blank=True)
    method = models.CharField(max_length=7, choices=[(
        'GET', 'GET'), ('POST', 'POST'), ('DELETE', 'DELETE')])
    argument = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.name


class ContactResponseCommon(models.Model):
    friendly_name = models.CharField(max_length=32)
    action = models.ForeignKey(
        ContactResponseAction, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.friendly_name}"


class ContactResponse(AbstractTranslatable):
    name = models.CharField(max_length=32)
    slug = models.SlugField(blank=True, null=True)
    message = models.TextField()
    common = models.ForeignKey(
        ContactResponseCommon, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.lang}"
