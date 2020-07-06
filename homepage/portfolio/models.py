import uuid
import os

from django.db import models
from django.core.mail import send_mail, EmailMessage, BadHeaderError, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template

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

navlink_positions = []
for j in range(settings.MAX_NAVLINKS):
    navlink_positions.append((j, j))

footerlink_positions = []
for k in range(settings.MAX_FOOTERLINKS):
    footerlink_positions.append((k, k))
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

class Link(models.Model):
    name = models.CharField(max_length=12)
    url = models.CharField(max_length=256)
    view = models.CharField(max_length=64, default='portfolio:project-detail', choices=views)
    def __str__(self):
        return self.url

class FooterLink(Link):
    position = models.IntegerField(null=True, choices=footerlink_positions, unique=True)
    icon = models.ForeignKey(Icon, on_delete=models.SET_NULL, null=True)

class NavLink(Link):
    #link_positions = range(1, len(NavLink.objects.all()))
    position = models.IntegerField(null=True, choices=navlink_positions, unique=True)

class TranslationsGroup(models.Model):
     name = models.CharField(max_length=24)

     def __str__(self):
         return self.name

class Translatable(models.Model):
    translations_group = models.ForeignKey(TranslationsGroup, on_delete=models.SET_NULL, null=True)
    lang = models.CharField(max_length=5, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    class Meta:                                                             
        abstract = True
    
class Page(models.Model):
    name = models.CharField(max_length=24)
    template_name = models.CharField(max_length=64)
    nav_bar_link = models.BooleanField(default=True)
    nav_link = models.ForeignKey(NavLink, on_delete=models.SET_NULL, null=True)

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
    nav_bar_link = models.BooleanField(default=True)
    nav_link = models.ForeignKey(NavLink, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.friendly_name
class Section(Translatable):
    #section_positions = range(1, len(Section.objects.all()))
    name = models.CharField(max_length=64)
    slug = models.SlugField(editable=False)
    description = models.TextField(null=True, blank=True)
    common = models.ForeignKey(SectionCommon, related_name='sections', on_delete=models.CASCADE, null=True)
    

    def __str__(self):
        return self.name

    def save(self):
        """ TODO: Add support for default position
        sections = Section.objects.order_by(position)
        if self.position == None:
            self.position = self.section_type.default_position """

        self.slug = generate_slug(self.name)
        if self.common.nav_bar_link:
            try:
                NavLink.objects.get(name=self.slug)
            except models.ObjectDoesNotExist:
                position = len(NavLink.objects.all())
                navlink = NavLink(name=self.slug, url=f'/#{self.slug}', position=position)
                navlink.save()
                self.common.nav_link = navlink
        super().save()
    
class BaseEntry(Translatable):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, editable=False)
    description = models.TextField()
    image = models.ImageField(upload_to='images')
    created = models.DateTimeField()
    spotlight = models.BooleanField()
    parent_section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    detail_view = models.CharField(max_length=64, default='portfolio.views.BaseEntryView', choices=views)

    def __str__(self):
        return self.name

    def save(self):
        self.slug = generate_slug(self.name)
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
        self.slug = generate_slug(self.name)
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
        self.slug = generate_slug(self.name)
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
        self.slug = generate_slug(self.name)
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


def generate_slug(name):
    REPLACE_CHARS = [' ', ',', '.', "'", '"', ':', ';', '/', '|', '\\']

    for char in REPLACE_CHARS:
        name = name.replace(char, "-")

    return name.lower()