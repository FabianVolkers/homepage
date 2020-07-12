from django.conf import settings

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
