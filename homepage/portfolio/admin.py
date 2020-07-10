from django.contrib import admin
from django.conf import settings

from .models import *
# Message, Contact, CollectionItem, Section, SectionType, Setting, Icon, Page, SectionCommon, NavLink, FooterLink, CollectionItem, LinkEdit # TranslationsGroup

# Register your models here.


""" 
TODO: 
- TranslationGroups Admin view with children

"""


class SlugAdmin(admin.ModelAdmin):
    prepopulated_fiels = {
        "slug": ("name",)
    }


class NavLinkInline(admin.TabularInline):
    model = NavLink
    readonly_fields = ('url',)


class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    readonly_fields = ('url',)


class LinkAdmin(admin.ModelAdmin):
    inlines = [
        NavLinkInline,
        FooterLinkInline
    ]


class TranslationInline(admin.StackedInline):
    max_num = len(settings.LANGUAGES)

    """ def get_prepopulated_fields(self, request, obj=None):
        translated = self.model.objects.filter(translations_group__id=obj.id)
        langs = settings.LANGUAGES
        for lang in translated:
            idx = [y[0] for y in langs].index(lang.lang)
            del langs[idx]
        
        return {"lang": next(iter(langs))} """


class SectionCommonInline(admin.TabularInline):
    model = SectionCommon


class SectionInline(TranslationInline):
    model = Section


class SectionCommonAdmin(SlugAdmin):
    inlines = [
        SectionInline
    ]


class CollectionItemAdmin(admin.ModelAdmin):
    model = CollectionItem

    list_display = ('name', 'lang')


class CollectionItemInline(TranslationInline):
    model = CollectionItem


class CollectionItemCommonAdmin(SlugAdmin):
    model = CollectionItemCommon
    #readonly_fields = ('detail_view',)
    inlines = [
        CollectionItemInline
    ]


class TranslationAdmin(admin.ModelAdmin):

    inlines = [
        SectionInline,
        CollectionItemInline
    ]

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if obj != None and inline.model.objects.filter(translations_group__id=obj.id, translations_group__isnull=False).count() > 0:
                yield inline.get_formset(request, obj), inline
            elif obj == None:
                yield inline.get_formset(request, obj), inline


class PageAdmin(SlugAdmin):
    pass


""" admin.site.register(Project)
admin.site.register(Collection)
admin.site.register(Photo) """
admin.site.register(Message)
admin.site.register(Contact)
admin.site.register(CollectionItem, CollectionItemAdmin)
admin.site.register(Section, SlugAdmin)
admin.site.register(SectionType)
admin.site.register(NavLink)
admin.site.register(Setting)
admin.site.register(FooterLink)
admin.site.register(LinkEdit, LinkAdmin)
admin.site.register(Icon)
admin.site.register(PageType)
admin.site.register(Page, PageAdmin)
admin.site.register(PageCommon)
#admin.site.register(TranslationsGroup, TranslationAdmin)
admin.site.register(SectionCommon, SectionCommonAdmin)
admin.site.register(CollectionItemCommon, CollectionItemCommonAdmin)
