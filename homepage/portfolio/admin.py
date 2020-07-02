from django.contrib import admin

from .models import Project, Collection, Photo, Message, Contact, BaseEntry, Category

# Register your models here.




admin.site.register(Project)
admin.site.register(Collection)
admin.site.register(Photo)
admin.site.register(Message)
admin.site.register(Contact)
admin.site.register(BaseEntry)
admin.site.register(Category)