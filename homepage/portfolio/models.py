import uuid
import os

from django.db import models
from django.core.mail import send_mail, EmailMessage, BadHeaderError, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

""" 
TODO: 
- Link abstract base class
- AbstractTranslatable BaseEntry with commonEntry and TranslationGroup

"""

views = [
    ('portfolio:project-detail', 'Project Detail View'),
    ('portfolio:project-list', 'Project List View'),
    ('portfolio:photo-detail', 'Photo View'),
    ('portfolio:entry-detail', 'Base View')
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
#for l in range()
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

    lang = models.CharField(max_length=5, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    class Meta:                                                             
        abstract = True
        unique_together = ['common', 'lang']
    
    def __str__(self):
        return self.lang

class PageType(models.Model):
    name = models.CharField(max_length=24)

    def __str__(self):
        return self.name

class PageCommon(models.Model):
    template_name = models.CharField(max_length=64)
    page_type = models.ForeignKey(PageType, on_delete=models.SET_NULL, null=True, blank=True)
    view_name = models.CharField(max_length=64, editable=False)
    overwrite_view_name = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __str__(self):
        return self.name
class Page(models.Model):
    name = models.CharField(max_length=24)
    template_name = models.CharField(max_length=64)
    slug = models.SlugField(null=True, blank=True)
    page_type = models.ForeignKey(PageType, on_delete=models.SET_NULL, null=True, blank=True)
    view_name = models.CharField(max_length=64, editable=False)
    overwrite_view_name = models.CharField(max_length=64, null=True, blank=True)
    #nav_link = models.ForeignKey(NavLink, on_delete=models.SET_NULL, default=1, null=True)

    class Meta:
        verbose_name = _('Single Page')
        verbose_name_plural = _('Single Pages')

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.name != 'Home':
            self.slug = slugify(self.name)
        else:
            self.slug = ""

        if self.overwrite_view_name != None:
            self.view_name = self.overwrite_view_name
        else:
            self.view_name = f"portfolio:{self.slug}-{self.page_type.name}"
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
 

class SectionType(models.Model):
    name = models.CharField(max_length=64)
    template_name = models.CharField(max_length=64)
    default_position = models.IntegerField()
    

    def __str__(self):
        return self.name

class SectionCommon(models.Model):
    friendly_name = models.CharField(max_length=64)
    section_type = models.ForeignKey(SectionType, on_delete=models.SET_NULL, null=True)
    position = models.IntegerField(null=True, choices=section_postitions, unique=True)
    page = models.ForeignKey(Page, on_delete=models.SET_NULL, null=True, blank=True, related_name='sections')
    #nav_link = models.ForeignKey(NavLink, on_delete=models.SET_NULL, default=1, null=True)

    class Meta:
        verbose_name = _('Page Section')
        verbose_name_plural = _('Page Sections')

    def __str__(self):
        return self.friendly_name
class Section(AbstractTranslatable):
    #section_positions = range(1, len(Section.objects.all()))
    name = models.CharField(max_length=64)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    common = models.ForeignKey(SectionCommon, related_name='sections', on_delete=models.CASCADE, null=True)
    
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
    url = models.CharField(max_length=256, editable=False, blank=True, default='/')
    view = models.CharField(max_length=64, default='portfolio:project-detail', choices=views)
    position = models.CharField(max_length=8, null=True, choices=link_positions, unique=True)
    link_for = models.CharField(max_length=24, choices=link_types, null=True)
    section = models.ForeignKey(Section, null=True, blank=True, on_delete=models.SET_NULL)
    page = models.ForeignKey(Page, null=True, blank=True, on_delete=models.SET_NULL)
    external = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.url

    def save(self):
        if self.link_for == 'section':
            self.url = f"{self.section.page.slug}/#{self.section.slug}"
        elif self.link_for == 'page':
            self.url = f"/{self.page.slug}"
        elif self.link_for == 'external':
            self.url = self.external
        return super.save()

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
    link_edit = models.ForeignKey(LinkEdit, on_delete=models.SET_NULL, null=True, related_name='social_links')

    class Meta:
        verbose_name = _('Social Link')
        verbose_name_plural = _('Social Links')

class FooterLink(AbstractLink):
    icon = models.ForeignKey(Icon, on_delete=models.SET_NULL, null=True)
    link_edit = models.ForeignKey(LinkEdit, on_delete=models.SET_NULL, null=True, related_name='footer_links')

    class Meta:
        verbose_name = _('Footer Link')
        verbose_name_plural = _('Footer Links')

class NavLink(AbstractLink):
    link_edit = models.ForeignKey(LinkEdit, on_delete=models.SET_NULL, null=True, related_name='navbar_links')
    
    class Meta:
        verbose_name = _('Navigation Link')
        verbose_name_plural = _('Navigation Links')


class CollectionItemCommon(models.Model):
    friendly_name = models.CharField(max_length=64)
    image = models.ImageField(upload_to='images')
    created = models.DateTimeField()
    spotlight = models.BooleanField()
    parent_section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    detail_view = models.CharField(max_length=64, default='portfolio.views.BaseEntryView', choices=views)

    class Meta:
        verbose_name = _('Collection Item')
        verbose_name_plural = _('Collection Items')

    def __str__(self):
        return self.friendly_name

class CollectionItem(AbstractTranslatable):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, editable=False)
    description = models.TextField()
    common = models.ForeignKey(CollectionItemCommon, related_name='collection_items', on_delete=models.CASCADE, null=True)
    image_alttext = models.TextField(default="")
    class Meta:
        verbose_name = _('Item Translation')
        verbose_name_plural = _('Item Translations')


    def save(self):
        self.slug = slugify(self.name)
        super().save()
""" 
class Project(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, editable=False)
    description = models.TextField()
    image = models.CharField(max_length=100)
    created = models.DateTimeField()
    spotlight = models.BooleanField()

    def __str__(self):
        return self.name

    def save(self):
        self.slug = slugify(self.name)
        super().save()

class Collection(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, editable=False)
    description = models.TextField()
    cover_photo = models.CharField(max_length=100)   
    spotlight = models.BooleanField()

    def __str__(self):
        return self.name

    def save(self):
        self.slug = slugify(self.name)
        super().save()

class Photo(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, editable=False)
    description = models.TextField()
    image = models.CharField(max_length=100)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def save(self):
        self.slug = slugify(self.name)
        super().save()
 """



class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email_address = models.EmailField()
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.email_address

    
    def send_confirmation_email(self, token):
        if settings.DEV_MODE:
            url = f'{settings.PROTO}://{settings.HOST}:{settings.PORT}/contact/confirm-email/{self.id}/{token}'
        else:
            url = f'{settings.PROTO}://{settings.HOST}/contact/confirm-email/{self.id}/{token}'
        print(url)
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
        # TODO: Check if email was sent successfi;;y
        self.sent = True

