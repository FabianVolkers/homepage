import uuid
import os

from django.db import models
from django.core.mail import send_mail, EmailMessage, BadHeaderError, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template

#from .mail import send_mail

# Create your models here.
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

class Contact(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email_address = models.EmailField()
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.email_address

    
    def send_confirmation_email(self, token):
        print(token)
        url = f'http://127.0.0.1:8000/contact/confirm-email/{self.id}/{token}'
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

        email_template = get_template('portfolio/contact_email.html.jinja2')
        context = {
            'from': self.contact.email_address,
            'subject': self.subject,
            'message': self.content
        }
        html_message = email_template.render(context=context)

        email.attach_alternative(html_message, 'text/html')
        email.send(fail_silently=False)


def generate_slug(name):
    REPLACE_CHARS = [' ', ',', '.', "'", '"', ':', ';', '/', '|', '\\']

    for char in REPLACE_CHARS:
        name = name.replace(char, "-")

    return name.lower()